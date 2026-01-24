# 使用 ZFS 作为根文件系统的 Fedora


## 注意事项

* 作为在 ZFS 根文件系统上安装 Fedora Linux 的替代方法，你可以使用非官方脚本 [fedora-on-zfs](https://github.com/gregory-lee-bartholomew/fedora-on-zfs)，该脚本更加自动化，可以生成更接近官方 Fedora 配置的安装。fedora-on-zfs 脚本与下文方法的区别在于，它使用 Fedora 官方的 kickstart 文件之一（如 `fedora-disk-minimal.ks`、`fedora-disk-workstation.ks`、`fedora-disk-kde.ks` 等）指导安装，同时进行少量修改以添加 ZFS 功能。如有 bug，请提交至 Greg 的 fedora-on-zfs GitHub 仓库。

**ZFSBootMenu**

[ZFSBootMenu](https://zfsbootmenu.org/) 是一种替代引导加载程序，不受上述限制，并支持启动环境。如果计划使用 ZBM，请不要按照本页面的指示操作，因为布局不兼容。安装详情请参考其官方网站。

**自定义配置**

除非另有说明，否则不建议在重启前自定义系统配置。

**仅使用经过充分测试的池功能**

应仅使用经过充分测试的池功能。如果数据完整性至关重要，请避免使用新功能。参考示例：[此评论](https://github.com/openzfs/openzfs-docs/pull/464#issuecomment-1776918481)。

**仅支持 UEFI**

本指南仅支持 UEFI。

### 准备工作

1. 禁用 Secure Boot。启用 Secure Boot 时无法加载 ZFS 模块。
2. 由于最新 Live CD 的内核可能与 ZFS 不兼容，我们将使用默认自带 ZFS 的 Alpine Linux Extended。
   下载最新的 [Alpine Linux Extended live 镜像](https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-extended-3.19.0-x86_64.iso)，并验证 [校验和](https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-extended-3.19.0-x86_64.iso.asc)，然后从该镜像启动。

   ```
   gpg --auto-key-retrieve --keyserver hkps://keyserver.ubuntu.com --verify alpine-extended-*.asc

   dd if=input-file of=output-file bs=1M
   ```
3. 使用 root 用户登录，初始无密码。
4. 配置网络：

   ```
   setup-interfaces -r
   # 必须使用 "-r" 选项以正确启动网络服务
   # 示例：
   network interface: wlan0
   WiFi name:         <ssid>
   ip address:        dhcp
   <enter done to finish network config>
   manual netconfig:  n
   ```
5. 如果使用无线网络且未显示，请参阅 [Alpine Linux wiki](https://wiki.alpinelinux.org/wiki/Wi-Fi#wpa_supplicant) 获取详细信息。
   可使用 `apk add wpa_supplicant` 安装 `wpa_supplicant`，无需网络连接。
6. 配置 SSH 服务器：

   ```
   setup-sshd
   # 示例：
   ssh server:        openssh
   allow root:        "prohibit-password" 或 "yes"
   ssh key:           "none" 或 "<public key>"
   ```
7. 设置 root 密码或 `/root/.ssh/authorized_keys`。
8. 从另一台计算机连接：

   ```
   ssh root@192.168.1.91
   ```
9. 配置 NTP 客户端进行时间同步：

   ```
   setup-ntp busybox
   ```
10. 设置 apk 仓库。会显示可用镜像列表，按空格键继续：

    ```
    setup-apkrepos
    ```
11. 本指南中，我们使用由 udev 生成的可预测磁盘名称：

    ```
    apk update
    apk add eudev
    setup-devd udev
    ```
12. 目标磁盘
    列出可用磁盘：

    ```
    find /dev/disk/by-id/
    ```

    如果使用 virtio 作为磁盘总线，请关闭虚拟机并为磁盘设置序列号。
    对于 QEMU，使用：

    ```
    -drive format=raw,file=disk2.img,serial=AaBb
    ```

    对于 libvirt，编辑 domain XML。示例请参见 [此页面](https://bugzilla.redhat.com/show_bug.cgi?id=1245013)。
    声明磁盘数组：

    ```
    DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'
    ```

    单磁盘安装使用：

    ```
    DISK='/dev/disk/by-id/disk1'
    ```
13. 设置挂载点：

    ```
    MNT=$(mktemp -d)
    ```
14. 设置分区大小：
    设置交换分区大小（GB），如果不希望占用过多空间，可设为 1：

    ```
    SWAPSIZE=4
    ```

    设置磁盘末尾保留空间，最小 1GB：

    ```
    RESERVE=1
    ```
15. 从 live 镜像安装 ZFS 支持：

    ```
    apk add zfs
    ```
16. 安装分区工具：

    ```
    apk add parted e2fsprogs cryptsetup util-linux
    ```

### 系统安装

1. 分区磁盘
   注意：必须清除目标磁盘上所有现有的分区表和数据结构。
   对于基于闪存的存储，可以使用如下 `blkdiscard` 命令：

   ```bash
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
2. 为本次安装设置临时加密交换分区（仅本次使用）。如果可用内存较小，此操作非常有用：

   ```bash
   for i in ${DISK}; do
      cryptsetup open --type plain --key-file /dev/random "${i}"-part3 "${i##*/}"-part3
      mkswap /dev/mapper/"${i##*/}"-part3
      swapon /dev/mapper/"${i##*/}"-part3
   done
   ```
3. 加载 ZFS 内核模块：

   ```bash
   modprobe zfs
   ```
4. 创建根池

   * 不加密示例：

     ```bash
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

   > ```bash
   > # dracut 要求系统根数据集必须使用非 legacy 挂载点
   > zfs create -o canmount=noauto -o mountpoint=/ rpool/root
   > ```

   创建系统数据集，并使用 `mountpoint=legacy` 管理挂载点：

   ```bash
   zfs create -o mountpoint=legacy rpool/home
   zfs mount rpool/root
   mount -o X-mount.mkdir -t zfs rpool/home "${MNT}"/home
   ```
6. 格式化并挂载 ESP（EFI 系统分区）。只有其中一个会作为 `/boot` 使用，之后需要设置镜像：

   ```bash
   for i in ${DISK}; do
    mkfs.vfat -n EFI "${i}"-part1
   done

   for i in ${DISK}; do
    mount -t vfat -o fmask=0077,dmask=0077,iocharset=iso8859-1,X-mount.mkdir "${i}"-part1 "${MNT}"/boot
    break
   done
   ```

### 系统配置

1. 下载并解压最小 Fedora 根文件系统：

   ```bash
   apk add curl
   curl --fail-early --fail -L \
   https://dl.fedoraproject.org/pub/fedora/linux/releases/39/Container/x86_64/images/Fedora-Container-Base-39-1.5.x86_64.tar.xz \
   -o rootfs.tar.gz
   curl --fail-early --fail -L \
   https://dl.fedoraproject.org/pub/fedora/linux/releases/39/Container/x86_64/images/Fedora-Container-39-1.5-x86_64-CHECKSUM \
   -o checksum

   # BusyBox sha256sum 会将校验文件中的每一行视为 checksum
   # 并要求文件名和校验值之间有两个空格 "  "

   grep 'Container-Base' checksum \
   | grep '^SHA256' \
   | sed -E 's|.*= ([a-z0-9]*)$|\1  rootfs.tar.gz|' > ./sha256checksum

   sha256sum -c ./sha256checksum

   rootfs_tar=$(tar t -af rootfs.tar.gz | grep layer.tar)
   rootfs_tar_dir=$(dirname "${rootfs_tar}")
   tar x -af rootfs.tar.gz "${rootfs_tar}"
   ln -s "${MNT}" "${MNT}"/"${rootfs_tar_dir}"
   tar x  -C "${MNT}" -af "${rootfs_tar}"
   unlink "${MNT}"/"${rootfs_tar_dir}"
   ```
2. 启用社区仓库：

   ```bash
   sed -i '/edge/d' /etc/apk/repositories
   sed -i -E 's/#(.*)community/\1community/' /etc/apk/repositories
   ```
3. 生成 fstab：

   ```bash
   apk add arch-install-scripts
   genfstab -t PARTUUID "${MNT}" \
   | grep -v swap \
   | sed "s|vfat.*rw|vfat rw,x-systemd.idle-timeout=1min,x-systemd.automount,noauto,nofail|" \
   > "${MNT}"/etc/fstab
   ```
4. 切换根环境（chroot）：

   ```bash
   cp /etc/resolv.conf "${MNT}"/etc/resolv.conf
   for i in /dev /proc /sys; do mkdir -p "${MNT}"/"${i}"; mount --rbind "${i}" "${MNT}"/"${i}"; done
   chroot "${MNT}" /usr/bin/env DISK="${DISK}" bash
   ```
5. 取消所有 shell 别名（防止干扰安装）：

   ```bash
   unalias -a
   ```
6. 安装基础软件包：

   ```bash
   dnf -y install @core kernel kernel-devel
   ```
7. 安装 ZFS 软件包：

   ```bash
   dnf -y install \
   https://zfsonlinux.org/fedora/zfs-release-2-4"$(rpm --eval "%{dist}"||true)".noarch.rpm

   dnf -y install zfs zfs-dracut
   ```
8. 检查 ZFS 模块是否成功构建：

   ```bash
   tail -n10 /var/lib/dkms/zfs/**/build/make.log
   ```

   如果构建失败，需要安装 LTS 内核及其头文件，然后重新构建 ZFS 模块：

   ```bash
   # 第三方仓库！
   # 已提醒注意
   #
   # 从以下地址选择内核：
   # https://copr.fedorainfracloud.org/coprs/kwizart/

   dnf copr enable -y kwizart/kernel-longterm-VERSION
   dnf install -y kernel-longterm kernel-longterm-devel
   dnf remove -y kernel-core
   ```

   ZFS 模块将在内核安装过程中构建。可再次使用 `tail` 查看构建日志。
9. 将 ZFS 模块添加到 dracut：

   ```bash
   echo 'add_dracutmodules+=" zfs "' >> /etc/dracut.conf.d/zfs.conf
   echo 'force_drivers+=" zfs "' >> /etc/dracut.conf.d/zfs.conf
   ```
10. 将其他驱动添加到 dracut：

    ```bash
    if grep mpt3sas /proc/modules; then
      echo 'force_drivers+=" mpt3sas "'  >> /etc/dracut.conf.d/zfs.conf
    fi
    if grep virtio_blk /proc/modules; then
      echo 'filesystems+=" virtio_blk "' >> /etc/dracut.conf.d/fs.conf
    fi
    ```
11. 构建 initrd：

    ```bash
    find -D exec /lib/modules -maxdepth 1 \
    -mindepth 1 -type d \
    -exec sh -vxc \
    'if test -e "$1"/modules.dep;
       then kernel=$(basename "$1");
       dracut --verbose --force --kver "${kernel}";
     fi' sh {} \;
    ```
12. 对于 SELinux，在重启时重新标记文件系统：

    ```bash
    fixfiles -F onboot
    ```
13. 启用网络时间同步：

    ```bash
    systemctl enable systemd-timesyncd
    ```
14. 生成主机 ID：

    ```bash
    zgenhostid -f -o /etc/hostid
    ```
15. 安装本地化语言包，例如英文：

    ```bash
    dnf install -y glibc-minimal-langpack glibc-langpack-en
    ```
16. 设置语言、键盘布局、时区和主机名：

    ```bash
    rm -f /etc/localtime
    rm -f /etc/hostname
    systemd-firstboot \
    --force \
    --locale=en_US.UTF-8 \
    --timezone=Etc/UTC \
    --hostname=testhost \
    --keymap=us || true
    ```
17. 设置 root 密码：

    ```bash
    printf 'root:yourpassword' | chpasswd
    ```

### 引导加载程序

1. 安装 rEFInd 引导加载程序：

   ```bash
   # 来源：http://www.rodsbooks.com/refind/getting.html
   # 使用 Binary Zip File 选项
   curl -L http://sourceforge.net/projects/refind/files/0.14.0.2/refind-bin-0.14.0.2.zip/download --output refind.zip

   dnf install -y unzip
   unzip refind.zip
   mkdir -p /boot/EFI/BOOT
   find ./refind-bin-0.14.0.2/ -name 'refind_x64.efi' -print0 \
   | xargs -0I{} mv {} /boot/EFI/BOOT/BOOTX64.EFI
   rm -rf refind.zip refind-bin-0.14.0.2
   ```
2. 添加启动项：

   ```bash
   tee -a /boot/refind-linux.conf <<EOF
   "Fedora" "root=ZFS=rpool/root"
   EOF
   ```
3. 退出 chroot 环境：

   ```bash
   exit
   ```
4. 卸载文件系统并创建初始系统快照。之后可以基于此快照创建启动环境。参见 [ZFS 根文件系统维护页面](https://openzfs.github.io/openzfs-docs/Getting%20Started/zfs_root_maintenance.html)：

   ```bash
   umount -Rl "${MNT}"
   zfs snapshot -r rpool@initial-installation
   ```
5. 导出所有池：

   ```bash
   zpool export -a
   ```
6. 重启系统：

   ```bash
   reboot
   ```

### 安装后操作

1. 安装软件包组：

   ```bash
   dnf group list --hidden -v       # 查询软件包组
   dnf group install gnome-desktop
   ```
2. 添加新用户并配置交换分区。
3. 挂载其他 EFI 系统分区，并设置服务以同步其内容。
