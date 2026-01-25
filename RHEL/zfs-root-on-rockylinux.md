# 构建以 ZFS 为根文件系统的 Rocky Linux

**ZFSBootMenu**

[ZFSBootMenu](https://zfsbootmenu.org/) 是一种替代的引导加载器，不存在上述限制，并且支持启动环境。如果计划使用 ZBM，请不要参照本文，因为磁盘布局不兼容。有关安装详情，请参考其官方网站。

**自定义**

除非另有说明，否则不建议在重启前自定义系统配置。

**仅使用经过充分测试的 ZFS 存储池功能**

应仅使用经过充分测试的 ZFS 存储池功能。如果数据完整性至关重要，应避免使用新功能。参见，例如 [此评论](https://github.com/openzfs/openzfs-docs/pull/464#issuecomment-1776918481)。

**仅支持 UEFI**

本指南仅支持 UEFI 启动。

## 准备

1. 禁用安全启动。在启用安全启动时无法加载 ZFS 模块。

2. 由于最新 Live CD 的内核可能与 ZFS 不兼容，我们使用 Alpine Linux Extended，它默认自带 ZFS。
   下载最新的 [Alpine Linux live 镜像 extended 版本](https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-extended-3.18.4-x86_64.iso)，并验证 [校验和](https://dl-cdn.alpinelinux.org/alpine/v3.18/releases/x86_64/alpine-extended-3.18.4-x86_64.iso.asc)，然后从其启动。

   ```sh
   gpg --auto-key-retrieve --keyserver hkps://keyserver.ubuntu.com --verify alpine-extended-*.asc

   dd if=input-file of=output-file bs=1M
   ```

3. 以 root 用户登录，初始无密码。

4. 配置网络

   ```sh
   setup-interfaces -r
   # 参数 "-r" 以正确启动网络服务
   # 示例：
   network interface: wlan0
   WiFi name:         <ssid>
   ip address:        dhcp
   <此处按回车完成安装>
   manual netconfig:  n
   ```

5. 如果使用无线网络但未显示，请参考 [Alpine Linux wiki](https://wiki.alpinelinux.org/wiki/Wi-Fi#wpa_supplicant) 获取更多信息。`wpa_supplicant` 可通过 `apk add wpa_supplicant` 安装，无需网络连接。

6. 配置 SSH 服务器

   ```sh
   setup-sshd
   # 示例：
   ssh server:        openssh
   allow root:        "prohibit-password" 或 "yes"
   ssh key:           "none" 或 "<公钥>"
   ```

7. 设置 root 密码或配置 `/root/.ssh/authorized_keys`。

8. 从其他计算机连接

   ```sh
   ssh root@192.168.1.91
   ```

9. 配置 NTP 客户端以同步时间

   ```sh
   setup-ntp busybox
   ```

10. 设置 apk 镜像源，系统会显示可用镜像列表，按空格键继续

    ```sh
    setup-apkrepos
    ```

11. 本指南中使用 udev 生成的可预测磁盘名称

    ```sh
    apk update
    apk add eudev
    setup-devd udev
    ```

12. 目标磁盘
    列出可用磁盘

    ```sh
    find /dev/disk/by-id/
    ```

    如果使用 virtio 作为磁盘总线，请关闭虚拟机并为磁盘设置序列号。

    * 对于 QEMU：使用 `-drive format=raw,file=disk2.img,serial=AaBb`
    * 对于 libvirt：编辑 domain XML
      参见 [示例页面](https://bugzilla.redhat.com/show_bug.cgi?id=1245013)。
      声明磁盘数组

    ```sh
    DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'
    ```

    单盘安装使用

    ```sh
    DISK='/dev/disk/by-id/disk1'
    ```

13. 设置挂载点

    ```sh
    MNT=$(mktemp -d)
    ```

14. 设置分区大小：

    设置 swap 大小（GB），如果不希望 swap 占用过多空间，可设为 1

    ```sh
    SWAPSIZE=4
    ```

    设置磁盘末端保留空间（最少 1GB）

    ```sh
    RESERVE=1
    ```

16. 从 live 系统安装 ZFS 支持

    ```sh
    apk add zfs
    ```

17. 安装分区工具

    ```sh
    apk add parted e2fsprogs cryptsetup util-linux
    ```

## 安装系统

1. 分区磁盘

   注意：必须清除目标磁盘上所有已有的分区表和数据结构。
   对于闪存存储，可使用以下 `blkdiscard` 命令：

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

3. 为本次安装设置临时加密 swap（仅用于安装）。当可用内存较小时非常有用：

   ```sh
   for i in ${DISK}; do
      cryptsetup open --type plain --key-file /dev/random "${i}"-part3 "${i##*/}"-part3
      mkswap /dev/mapper/"${i##*/}"-part3
      swapon /dev/mapper/"${i##*/}"-part3
   done
   ```

4. 加载 ZFS 内核模块

   ```sh
   modprobe zfs
   ```

5. 创建根池

   * 未加密示例：

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

6. 创建根系统容器

   ```sh
   # dracut 要求系统根数据集具有非 legacy mountpoint
   zfs create -o canmount=noauto -o mountpoint=/ rpool/root
   ```

   创建系统数据集，并使用 `mountpoint=legacy` 管理挂载点：

   ```sh
   zfs create -o mountpoint=legacy rpool/home
   zfs mount rpool/root
   mount -o X-mount.mkdir -t zfs rpool/home "${MNT}"/home
   ```

7. 格式化并挂载 ESP。只使用其中一个作为 /boot，其余可稍后设置镜像：

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

1. 下载并解压 RHEL 最小根文件系统：

   ```sh
   apk add curl
   curl --fail-early --fail -L \
   https://dl.rockylinux.org/vault/rocky/9.2/images/x86_64/Rocky-9-Container-Base-9.2-20230513.0.x86_64.tar.xz \
   -o rootfs.tar.gz
   curl --fail-early --fail -L \
   https://dl.rockylinux.org/vault/rocky/9.2/images/x86_64/Rocky-9-Container-Base-9.2-20230513.0.x86_64.tar.xz.CHECKSUM \
   -o checksum

   # BusyBox sha256sum 处理 checksum 文件时要求文件名与校验值之间有两个空格
   grep 'Container-Base' checksum \
   | grep '^SHA256' \
   | sed -E 's|.*= ([a-z0-9]*)$|\1  rootfs.tar.gz|' > ./sha256checksum

   sha256sum -c ./sha256checksum

   tar x  -C "${MNT}" -af rootfs.tar.gz
   ```

2. 启用社区仓库

   ```sh
   sed -i '/edge/d' /etc/apk/repositories
   sed -i -E 's/#(.*)community/\1community/' /etc/apk/repositories
   ```

3. 生成 fstab

   ```sh
   apk add arch-install-scripts
   genfstab -t PARTUUID "${MNT}" \
   | grep -v swap \
   | sed "s|vfat.*rw|vfat rw,x-systemd.idle-timeout=1min,x-systemd.automount,noauto,nofail|" \
   > "${MNT}"/etc/fstab
   ```

4. chroot 进入安装环境

   ```sh
   cp /etc/resolv.conf "${MNT}"/etc/resolv.conf
   for i in /dev /proc /sys; do mkdir -p "${MNT}"/"${i}"; mount --rbind "${i}" "${MNT}"/"${i}"; done
   chroot "${MNT}" /usr/bin/env DISK="${DISK}" bash
   ```

5. 取消所有 shell 别名，以免干扰安装

   ```sh
   unalias -a
   ```

6. 安装基础软件包

   ```sh
   dnf -y install --allowerasing @core kernel-core kernel-modules
   ```

7. 安装 ZFS 软件包

   ```sh
   dnf install -y https://zfsonlinux.org/epel/zfs-release-2-3"$(rpm --eval "%{dist}"|| true)".noarch.rpm
   dnf config-manager --disable zfs
   dnf config-manager --enable zfs-kmod
   dnf install -y zfs zfs-dracut
   ```

8. 将 ZFS 模块添加到 dracut

   ```sh
   echo 'add_dracutmodules+=" zfs "' >> /etc/dracut.conf.d/zfs.conf
   echo 'force_drivers+=" zfs "' >> /etc/dracut.conf.d/zfs.conf
   ```

9. 将其他驱动添加到 dracut

   ```sh
   if grep mpt3sas /proc/modules; then
     echo 'force_drivers+=" mpt3sas "'  >> /etc/dracut.conf.d/zfs.conf
   fi
   if grep virtio_blk /proc/modules; then
     echo 'filesystems+=" virtio_blk "' >> /etc/dracut.conf.d/zfs.conf
   fi
   ```

10. 生成 hostid

    ```sh
    zgenhostid -f -o /etc/hostid
    ```

11. 构建 initrd

    ```sh
    find -D exec /lib/modules -maxdepth 1 \
    -mindepth 1 -type d \
    -exec sh -vxc \
    'if test -e "$1"/modules.dep;
       then kernel=$(basename "$1");
       dracut --verbose --force --kver "${kernel}";
     fi' sh {} \;
    ```

12. 对 SELinux，在重启时重新标记文件系统

    ```sh
    fixfiles -F onboot
    ```

13. 安装语言包（例如英文）

    ```sh
    dnf install -y glibc-minimal-langpack glibc-langpack-en
    ```

14. 设置语言、键盘布局、时区和主机名

    ```sh
    rm -f /etc/localtime
    systemd-firstboot \
    --force \
    --locale=en_US.UTF-8 \
    --timezone=Etc/UTC \
    --hostname=testhost \
    --keymap=us
    ```

15. 设置 root 密码

    ```sh
    printf 'root:yourpassword' | chpasswd
    ```

## 引导加载器

1. 安装 rEFInd 引导加载器：

   ```sh
   # 参考 http://www.rodsbooks.com/refind/getting.html
   # 使用 Binary Zip File 选项
   curl -L https://sourceforge.net/projects/refind/files/0.14.0.2/refind-bin-0.14.0.2.zip/download --output refind.zip

   dnf install -y unzip
   unzip refind.zip
   mkdir -p /boot/EFI/BOOT
   find ./refind-bin-0.14.0.2/ -name 'refind_x64.efi' -print0 \
   | xargs -0I{} mv {} /boot/EFI/BOOT/BOOTX64.EFI
   rm -rf refind.zip refind-bin-0.14.0.2
   ```

2. 添加启动项：

   ```sh
   tee -a /boot/refind-linux.conf <<EOF
   "Rocky Linux" "root=ZFS=rpool/root"
   EOF
   ```

3. 退出 chroot：

   ```sh
   exit
   ```

4. 卸载文件系统并创建初始系统快照（稍后可从此快照创建启动环境，参考 [Root on ZFS 维护页面](https://openzfs.github.io/openzfs-docs/Getting%20Started/zfs_root_maintenance.html)）：

   ```sh
   umount -Rl "${MNT}"
   zfs snapshot -r rpool@initial-installation
   ```

5. 导出所有 ZFS 存储池：

   ```sh
   zpool export -a
   ```

6. 重启系统：

   ```sh
   reboot
   ```

## 安装后配置

1. 安装软件包组：

   ```sh
   dnf group list --hidden -v       # 查询可用软件包组
   dnf group install gnome-desktop
   ```

2. 添加新用户并配置 swap。
3. 挂载其他 EFI 系统分区，然后设置服务以同步其内容。
