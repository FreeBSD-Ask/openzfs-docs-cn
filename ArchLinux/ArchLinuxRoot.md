# 构建以 ZFS 为根文件系统的 Arch Linux

**ZFSBootMenu**

[ZFSBootMenu](https://zfsbootmenu.org/) 是一种不受此类限制的替代引导加载器，还支持启动环境。如果你计划使用 ZBM，请不要参照本文，因为与其布局不兼容。请参考其网站获取安装细节。

**自定义**

除非另有说明，否则不建议在重启之前自定义系统配置。

**仅使用经过充分测试的存储池特性**

你应且只应使用经过充分测试的存储池特性。如果数据完整性至关重要，请避免使用新特性。例如，可参见 [此评论](https://github.com/openzfs/openzfs-docs/pull/464#issuecomment-1776918481)。

**仅支持 UEFI**

本指南仅支持 UEFI。

## 准备

1. 禁用安全启动。如果启用了安全启动，将无法加载 ZFS 模块。
2. 由于最新 Live CD 的内核可能与 ZFS 不兼容，我们将使用默认自带 ZFS 的 Alpine Linux Extended。
   下载最新版扩展变体的 [Alpine Linux Live 镜像](https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-extended-3.19.0-x86_64.iso)，校验 [校验和](https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-extended-3.19.0-x86_64.iso.asc)，再从该镜像启动。

   ```sh
   gpg --auto-key-retrieve --keyserver hkps://keyserver.ubuntu.com --verify alpine-extended-*.asc

   dd if=input-file of=output-file bs=1M
   ```

3. 以 root 用户登录。密码为空。
4. 配置网络

   ```sh
   setup-interfaces -r
   # 必须使用选项 "-r" 才能正确启动网络服务
   # 示例：
   network interface: wlan0
   WiFi name:         <ssid>
   ip address:        dhcp
   <按回车键以完成网络设置>
   manual netconfig:  n
   ```

5. 如果使用无线网络但网络未显示在列表中，请参阅 [Alpine Linux wiki](https://wiki.alpinelinux.org/wiki/Wi-Fi#wpa_supplicant) 获取更多细节。可在无网络情况下通过命令 `apk add wpa_supplicant` 安装 `wpa_supplicant`。
6. 配置 SSH 服务器

   ```sh
   setup-sshd
   # 示例：
   ssh server:        openssh
   allow root:        "prohibit-password" 或 "yes"
   ssh key:           "none" 或 "<公钥>"
   ```

7. 设置 root 密码或 `/root/.ssh/authorized_keys`。
8. 从另一台计算机连接

   ```sh
   ssh root@192.168.1.91
   ```

9. 配置 NTP 客户端进行时间同步

   ```sh
   setup-ntp busybox
   ```

10. 设置 apk-repo。将显示可用镜像列表，按空格键继续。

    ```sh
    setup-apkrepos
    ```

11. 本指南中使用由 udev 生成的可预测磁盘名称。

    ```sh
    apk update
    apk add eudev
    setup-devd udev
    ```

12. 目标磁盘
    列出可用磁盘：

    ```sh
    find /dev/disk/by-id/
    ```

    如果使用 virtio 作为磁盘总线，请关闭虚拟机并为磁盘设置序列号。对于 QEMU，使用 `-drive format=raw,file=disk2.img,serial=AaBb`；对于 libvirt，请编辑域 XML。示例可参见 [此页面](https://bugzilla.redhat.com/show_bug.cgi?id=1245013)。
    声明磁盘编号：

    ```sh
    DISK='/dev/disk/by-id/ata-FOO /dev/disk/by-id/nvme-BAR'
    ```

    单块磁盘安装使用：

    ```sh
    DISK='/dev/disk/by-id/disk1'
    ```

13. 设置挂载点

    ```sh
    MNT=$(mktemp -d)
    ```

14. 设置分区大小：
    设置 swap 大小（GB），若不希望 swap 占用过多空间，可设为 1。

    ```sh
    SWAPSIZE=4
    ```

    设置磁盘末尾保留空间，最少 1GB。

    ```sh
    RESERVE=1
    ```

15. 从 Live 安装介质安装 ZFS 支持：

    ```sh
    apk add zfs
    ```

16. 安装分区工具

    ```sh
    apk add parted e2fsprogs cryptsetup util-linux
    ```

## 系统安装

1. 对磁盘进行分区。
   >**注意**
   >
   >必须清除目标磁盘上所有现有的分区表和数据结构。
   对于基于闪存的存储，可使用以下 blkdiscard 命令：

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

2. 仅为本次安装设置临时加密 swap，当可用内存较小时非常有用：

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

   创建系统数据集，使用 `mountpoint=legacy` 管理挂载点：

   ```sh
   zfs create -o mountpoint=legacy rpool/home
   mount -o X-mount.mkdir -t zfs rpool/root "${MNT}"
   mount -o X-mount.mkdir -t zfs rpool/home "${MNT}"/home
   ```

6. 格式化并挂载 ESP。仅使用其中一个作为 `/boot`，之后需设置镜像：

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

1. 下载解压最小 Arch Linux 根文件系统：

   ```sh
   apk add curl

   curl --fail-early --fail -L \
   https://america.archive.pkgbuild.com/iso/2024.01.01/archlinux-bootstrap-x86_64.tar.gz \
   -o rootfs.tar.gz
   curl --fail-early --fail -L \
   https://america.archive.pkgbuild.com/iso/2024.01.01/archlinux-bootstrap-x86_64.tar.gz.sig \
   -o rootfs.tar.gz.sig

   apk add gnupg
   gpg --auto-key-retrieve --keyserver hkps://keyserver.ubuntu.com --verify rootfs.tar.gz.sig

   ln -s "${MNT}" "${MNT}"/root.x86_64
   tar x  -C "${MNT}" -af rootfs.tar.gz root.x86_64
   ```

2. 启用社区仓库：

   ```sh
   sed -i '/edge/d' /etc/apk/repositories
   sed -i -E 's/#(.*)community/\1community/' /etc/apk/repositories
   ```

3. 生成 fstab：

   ```sh
   apk add arch-install-scripts
   genfstab -t PARTUUID "${MNT}" \
   | grep -v swap \
   | sed "s|vfat.*rw|vfat rw,x-systemd.idle-timeout=1min,x-systemd.automount,noauto,nofail|" \
   > "${MNT}"/etc/fstab
   ```

4. chroot：

   ```sh
   cp /etc/resolv.conf "${MNT}"/etc/resolv.conf
   for i in /dev /proc /sys; do mkdir -p "${MNT}"/"${i}"; mount --rbind "${i}" "${MNT}"/"${i}"; done
   chroot "${MNT}" /usr/bin/env DISK="${DISK}" bash
   ```

5. 在 pacman 配置中添加 archzfs 仓库：

   ```sh
   pacman-key --init
   pacman-key --refresh-keys
   pacman-key --populate

   curl --fail-early --fail -L https://archzfs.com/archzfs.gpg \
   |  pacman-key -a - --gpgdir /etc/pacman.d/gnupg

   pacman-key \
   --lsign-key \
   --gpgdir /etc/pacman.d/gnupg \
   DDF7DB817396A49B2A2723F7403BD972F75D9D76

   tee -a /etc/pacman.d/mirrorlist-archzfs <<- 'EOF'
   ## See https://github.com/archzfs/archzfs/wiki
   ## 法国
   #,Server = https://archzfs.com/$repo/$arch

   ## 德国
   #,Server = https://mirror.sum7.eu/archlinux/archzfs/$repo/$arch
   #,Server = https://mirror.biocrafting.net/archlinux/archzfs/$repo/$arch

   ## 印度
   #,Server = https://mirror.in.themindsmaze.com/archzfs/$repo/$arch

   ## 美国
   #,Server = https://zxcvfdsa.com/archzfs/$repo/$arch
   EOF

   tee -a /etc/pacman.conf <<- 'EOF'

   #[archzfs-testing]
   #Include = /etc/pacman.d/mirrorlist-archzfs

   #,[archzfs]
   #,Include = /etc/pacman.d/mirrorlist-archzfs
   EOF

   # 这个 #, 前缀是 CI/CD 测试的解决方法
   # 移除它们
   sed -i 's|#,||' /etc/pacman.d/mirrorlist-archzfs
   sed -i 's|#,||' /etc/pacman.conf
   sed -i 's|^#||' /etc/pacman.d/mirrorlist
   ```

6. 安装基础软件包：

   ```sh
   pacman -Sy
   pacman -S --noconfirm mg mandoc efibootmgr mkinitcpio

   kernel_compatible_with_zfs="$(pacman -Si zfs-linux \
   | grep 'Depends On' \
   | sed "s|.*linux=||" \
   | awk '{ print $1 }')"
   pacman -U --noconfirm https://america.archive.pkgbuild.com/packages/l/linux/linux-"${kernel_compatible_with_zfs}"-x86_64.pkg.tar.zst
   ```

7. 安装 ZFS 软件包：

   ```sh
   pacman -S --noconfirm zfs-linux zfs-utils
   ```

8. 配置 mkinitcpio：

   ```sh
   sed -i 's|filesystems|zfs filesystems|' /etc/mkinitcpio.conf
   mkinitcpio -P
   ```

9. 物理机还需安装固件：

   ```sh
   pacman -S linux-firmware intel-ucode amd-ucode
   ```

10. 启用网络时间同步：

    ```sh
    systemctl enable systemd-timesyncd
    ```

11. 生成 host id：

    ```sh
    zgenhostid -f -o /etc/hostid
    ```

12. 进行本地化：

    ```sh
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
    locale-gen
    ```

13. 设置语言、键盘布局、时区、主机名：

    ```sh
    rm -f /etc/localtime
    systemd-firstboot \
    --force \
    --locale=en_US.UTF-8 \
    --timezone=Etc/UTC \
    --hostname=testhost \
    --keymap=us
    ```

14. 设置 root 密码：

    ```sh
    printf 'root:yourpassword' | chpasswd
    ```

## 引导加载器

1. 安装 rEFInd 引导加载器：

   ```sh
   # 来源：http://www.rodsbooks.com/refind/getting.html
   # 使用二进制 Zip 文件方案
   pacman -S --noconfirm unzip
   curl -L http://sourceforge.net/projects/refind/files/0.14.0.2/refind-bin-0.14.0.2.zip/download --output refind.zip

   unzip refind.zip
   mkdir -p /boot/EFI/BOOT
   find ./refind-bin-0.14.0.2/ -name 'refind_x64.efi' -print0 \
   | xargs -0I{} mv {} /boot/EFI/BOOT/BOOTX64.EFI
   rm -rf refind.zip refind-bin-0.14.0.2
   ```

2. 添加引导条目：

   ```sh
   tee -a /boot/refind-linux.conf <<EOF
   "Arch Linux" "root=ZFS=rpool/root rw zfs_import_dir=/dev/"
   EOF
   ```

3. 退出 chroot：

   ```sh
   exit
   ```

4. 卸载文件系统并创建初始系统快照：

   ```sh
   umount -Rl "${MNT}"
   zfs snapshot -r rpool@initial-installation
   ```

5. 导出所有存储池：

   ```sh
   zpool export -a
   ```

6. 重启：

   ```sh
   reboot
   ```

7. 挂载其他 EFI 系统分区，然后设置服务来同步其内容。
