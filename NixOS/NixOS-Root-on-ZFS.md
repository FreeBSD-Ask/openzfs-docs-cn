# 构建以 ZFS 为根文件系统的 NixOS


**自定义**

除非另有说明，否则不建议在重启之前自定义系统配置。

**仅支持 UEFI**

本指南仅支持 UEFI。请确保你的计算机以 UEFI 模式启动。

## 准备工作

1. 下载 [NixOS Live 镜像](https://nixos.org/download.html#nixos-iso) ，然后从其启动。

   ```sh
   sha256sum -c ./nixos-*.sha256

   dd if=input-file of=output-file bs=1M
   ```

2. 连接到互联网。

3. 设置 root 密码或 `/root/.ssh/authorized_keys`。

4. 启动 SSH 服务。

   ```sh
   systemctl restart sshd
   ```

5. 从另一台计算机连接。

   ```sh
   ssh root@192.168.1.91
   ```

6. 目标磁盘
   使用以下命令列出可用磁盘：

   ```sh
   find /dev/disk/by-id/
   ```

   如果使用 virtio 作为磁盘总线，请关闭虚拟机并为磁盘设置序列号。对于 QEMU，使用 `-drive format=raw,file=disk2.img,serial=AaBb`。对于 libvirt，编辑域 XML。示例参见 [此页面](https://bugzilla.redhat.com/show_bug.cgi?id=1245013)。

   声明磁盘数组：

   ```sh
   DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'
   ```

   对于单块磁盘安装，使用：

   ```ini
   DISK='/dev/disk/by-id/disk1'
   ```

7. 设置挂载点：

   ```ini
   MNT=$(mktemp -d)
   ```

8. 设置分区大小：
  设置 swap 大小（单位 GB），如果不希望 swap 占用过多空间则设为 1。

   ```ini
   SWAPSIZE=4
   ```

   设置磁盘末尾保留空间大小，最少 1GB。

   ```ini
   RESERVE=1
   ```

## 系统安装

1. 对磁盘进行分区。
   注意：必须清除目标磁盘上一切既有的分区表和数据结构。
   对于基于闪存的存储，可使用下面的 blkdiscard 命令完成：

   ```sh
   partition_disk () {
    local disk="${1}"
    blkdiscard -f "${disk}" || true

    parted --script --align=optimal  "${disk}" -- \
    mklabel gpt \
    mkpart EFI 1MiB 4GiB \
    mkpart rpool 4GiB -$((SWAPSIZE + RESERVE))GiB \
    mkpart swap  -$((SWAPSIZE + RESERVE))GiB -"${RESERVE}"GiB \
    set 1 esp on \

    partprobe "${disk}"
   }

   for i in ${DISK}; do
      partition_disk "${i}"
   done
   ```

2. 仅为本次安装设置临时加密 swap。这在可用内存较小时非常有用：

   ```sh
   for i in ${DISK}; do
      cryptsetup open --type plain --key-file /dev/random "${i}"-part3 "${i##*/}"-part3
      mkswap /dev/mapper/"${i##*/}"-part3
      swapon /dev/mapper/"${i##*/}"-part3
   done
   ```

3. **仅 LUKS**：为根池设置加密的 LUKS 容器：

   ```sh
   for i in ${DISK}; do
      # 参见 cryptsetup(8) 中的 PASSPHRASE PROCESSING 部分
      printf "YOUR_PASSWD" | cryptsetup luksFormat --type luks2 "${i}"-part2 -
      printf "YOUR_PASSWD" | cryptsetup luksOpen "${i}"-part2 luks-rpool-"${i##*/}"-part2 -
   done
   ```

4. 创建根池

   * 未加密

     ```sh
     # shellcheck disable=SC2046
     zpool create \
         -o ashift=12 \
         -o autotrim=on \
         -R "${MNT}" \
         -O acltype=posixacl \
         -O canmount=off \
         -O dnodesize=auto \
         -O normalization=formD \
         -O relatime=on \
         -O xattr=sa \
         -O mountpoint=none \
         rpool \
         mirror \
        $(for i in ${DISK}; do
           printf '%s ' "${i}-part2";
          done)
     ```

   * LUKS 加密

     ```sh
     # shellcheck disable=SC2046
     zpool create \
         -o ashift=12 \
         -o autotrim=on \
         -R "${MNT}" \
         -O acltype=posixacl \
         -O canmount=off \
         -O dnodesize=auto \
         -O normalization=formD \
         -O relatime=on \
         -O xattr=sa \
         -O mountpoint=none \
         rpool \
         mirror \
        $(for i in ${DISK}; do
           printf '/dev/mapper/luks-rpool-%s ' "${i##*/}-part2";
          done)
     ```

   如果不是多磁盘配置，请移除 `mirror`。

5. 创建根系统容器：

   > ```sh
   > zfs create -o canmount=noauto -o mountpoint=legacy rpool/root
   > ```

   创建系统数据集，使用 `mountpoint=legacy` 管理挂载点：

   ```sh
   zfs create -o mountpoint=legacy rpool/home
   mount -o X-mount.mkdir -t zfs rpool/root "${MNT}"
   mount -o X-mount.mkdir -t zfs rpool/home "${MNT}"/home
   ```

6. 格式化并挂载 ESP。仅使用其中一个作为 `/boot`，之后需要设置镜像：

   ```sh
   for i in ${DISK}; do
    mkfs.vfat -n EFI "${i}"-part1
   done

   for i in ${DISK}; do
    mount -t vfat -o fmask=0077,dmask=0077,iocharset=iso8859-1,X-mount.mkdir "${i}"-part1 "${MNT}"/boot
    break
   done
   ```

## 系统配置

1. 生成系统配置：

   ```sh
   nixos-generate-config --root "${MNT}"
   ```

2. 编辑系统配置：

   ```sh
   nano "${MNT}"/etc/nixos/hardware-configuration.nix
   ```

3. 设置 networking.hostId：

   ```sh
   networking.hostId = "abcd1234";
   ```

4. 如果使用 LUKS，将以下命令的输出添加到系统配置中：

   ```sh
   tee <<EOF
     boot.initrd.luks.devices = {
   EOF

   for i in ${DISK}; do echo \"luks-rpool-"${i##*/}-part2"\".device = \"${i}-part2\"\; ; done

   tee <<EOF
   };
   EOF
   ```

5. 安装系统并应用配置：

   ```sh
   nixos-install  --root "${MNT}"
   ```

   等待出现重置 root 密码的提示。

6. 卸载文件系统：

   ```sh
   cd /
   umount -Rl "${MNT}"
   zpool export -a
   ```

7. 重启：

   ```sh
   reboot
   ```

8. 设置网络、桌面环境和 swap。

9. 挂载其他 EFI 系统分区，然后设置服务同步其内容。
