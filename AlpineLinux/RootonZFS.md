# 以 ZFS 为根文件系统的 Alpine Linux

**ZFSBootMenu**

[ZFSBootMenu](https://zfsbootmenu.org/) 是一种不受此类限制的替代引导加载器，还支持启动环境。如果你计划使用 ZFSBootMenu，请勿参照本页面上的说明，因为与其布局并不兼容。请参考其网站获取安装细节。

**自定义**

除非另有说明，否则不建议在重启之前自定义系统配置。

**仅使用经过充分测试的存储池特性**

你应且只应使用经过充分测试的存储池特性。若数据完整性至关重要，请避免使用新特性。例如，可参见 [此评论](https://github.com/openzfs/openzfs-docs/pull/464#issuecomment-1776918481)。

**仅支持 UEFI**

本指南仅支持 UEFI。

## 准备

1. 禁用安全启动。如果启用了安全启动，将无法加载 ZFS 模块。
2. 下载最新 extended（衍生版本）的 [Alpine Linux Live 镜像](https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-extended-3.19.0-x86_64.iso)，校验 [校验和](https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-extended-3.19.0-x86_64.iso.asc)，然后从该镜像启动。

   ```sh
   gpg --auto-key-retrieve --keyserver hkps://keyserver.ubuntu.com --verify alpine-extended-*.asc

   dd if=input-file of=output-file bs=1M
   ```

3. 以 root 用户登录。密码为空。
4. 配置网络

   ```sh
   setup-interfaces -r
   # 你必须使用选项“-r”才能正确启动网络服务
   # 示例：
   network interface: wlan0
   WiFi name:         <ssid>
   ip address:        dhcp
   <此处按回车完成网络配置>
   manual netconfig:  n
   ```

5. 如果你使用的是无线网络但无线网卡未出现在列表中，请参阅 [Alpine Linux wiki](https://wiki.alpinelinux.org/wiki/Wi-Fi#wpa_supplicant) 获取更多细节。`wpa_supplicant` 可以在没有互联网连接的情况下通过命令 `apk add wpa_supplicant` 进行安装。
6. 配置 SSH 服务器

   ```sh
   setup-sshd
   # 示例：
   ssh server:        openssh
   allow root:        "prohibit-password" 或 "yes"
   ssh key:           "none" 或 "<公钥>"
   ```

   此处设置的配置将被原样复制到已安装的系统中。
7. 设置 root 密码或 `/root/.ssh/authorized_keys`。
   请设置足够复杂的 root 密码，因为它将用于新安装的系统。不过，`authorized_keys` 文件本身不会被复制到新系统中。
8. 通过另一台计算机进行连接

   ```sh
   ssh root@192.168.1.91
   ```

9. 配置 NTP 客户端，用于同步时间

   ```sh
   setup-ntp busybox
   ```

10. 设置 apk-repo。将显示可用镜像列表。按空格键继续。

    ```sh
    setup-apkrepos
    ```

11. 在本指南中，我们使用由 udev 生成的可预测磁盘名称

    ```sh
    apk update
    apk add eudev
    setup-devd udev
    ```

    重启后可通过命令 `setup-devd mdev && apk del eudev` 将其移除。
12. 目标磁盘
    使用以下命令列出可用磁盘：

    ```sh
    find /dev/disk/by-id/
    ```

    如果使用 virtio 作为磁盘总线，请关闭虚拟机并为磁盘设置序列号。对于 QEMU，可使用 `-drive format=raw,file=disk2.img,serial=AaBb`。对于 libvirt，请编辑域 XML。示例可参见 [此页面](https://bugzilla.redhat.com/show_bug.cgi?id=1245013)。

    声明磁盘编号：

    ```sh
    DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'
    ```

    对于单块磁盘安装，使用：

    ```sh
    DISK='/dev/disk/by-id/disk1'
    ```

13. 设置挂载点

    ```ini
    MNT=$(mktemp -d)
    ```

14. 设置分区大小：
    设置 swap 大小（单位为 GB），如果不希望 swap 占用过多空间，可设置为 1。

    ```ini
    SWAPSIZE=4
    ```

    设置磁盘末尾需要保留的空间大小，最少 1 GB。

    ```ini
    RESERVE=1
    ```

15. 通过安装介质安装 ZFS 支持：

    ```sh
    apk add zfs
    ```

16. 安装引导加载程序和分区工具

    ```sh
    apk add parted e2fsprogs cryptsetup util-linux
    ```

## 系统安装

1. 对磁盘进行分区。
   >**注意**
   >
   >你必须清除目标磁盘上所有现有的分区表和数据结构。
   对于基于闪存的存储，可以使用下面的 blkdiscard 命令完成此操作：

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

2. 仅为本次安装设置临时加密 swap。当可用内存较小时，这很有用：

   ```sh
   for i in ${DISK}; do
      cryptsetup open --type plain --key-file /dev/random "${i}"-part3 "${i##*/}"-part3
      mkswap /dev/mapper/"${i##*/}"-part3
      swapon /dev/mapper/"${i##*/}"-part3
   done
   ```

3. 加载 ZFS 内核模块

   ```sh
   modprobe zfs
   ```

4. 创建根存储池

   * 未加密：

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

5. 创建根系统容器：

   > ```sh
   > zfs create -o canmount=noauto -o mountpoint=legacy rpool/root
   > ```

   创建系统数据集，使用 `mountpoint=legacy` 管理挂载点。

   ```sh
   zfs create -o mountpoint=legacy rpool/home
   mount -o X-mount.mkdir -t zfs rpool/root "${MNT}"
   mount -o X-mount.mkdir -t zfs rpool/home "${MNT}"/home
   ```

6. 格式化并挂载 ESP。只有其中一个会被用作 `/boot`，之后你需要再设置镜像。

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

1. 将系统安装到磁盘

   ```sh
   BOOTLOADER=none setup-disk -k lts -v "${MNT}"
   ```

   关于 ZFS 内核模块的错误信息可以忽略。
2. 安装 rEFInd 引导加载器：

   ```sh
   # 来自 http://www.rodsbooks.com/refind/getting.html
   # 使用 Binary Zip File 选项
   apk add curl
   curl -L http://sourceforge.net/projects/refind/files/0.14.0.2/refind-bin-0.14.0.2.zip/download --output refind.zip
   unzip refind

   mkdir -p "${MNT}"/boot/EFI/BOOT
   find ./refind-bin-0.14.0.2/ -name 'refind_x64.efi' -print0 \
   | xargs -0I{} mv {} "${MNT}"/boot/EFI/BOOT/BOOTX64.EFI
   rm -rf refind.zip refind-bin-0.14.0.2
   ```

3. 添加启动项：

   ```sh
   tee -a "${MNT}"/boot/refind-linux.conf <<EOF
   "Alpine Linux" "root=ZFS=rpool/root"
   EOF
   ```

4. 卸载文件系统，创建初始系统快照：

   ```sh
   umount -Rl "${MNT}"
   zfs snapshot -r rpool@initial-installation
   zpool export -a
   ```

5. 重启

   ```sh
   reboot
   ```

6. 挂载其他 EFI 系统分区，然后设置服务来同步其内容。
