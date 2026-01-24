# 根文件系统使用 ZFS 的 Debian 12 Bookworm

## 概述

### 提供了更新的版本

* 新安装请参阅《[Debian Trixie Root on ZFS](https://openzfs.github.io/openzfs-docs/Getting%20Started/Debian/Debian%20Trixie%20Root%20on%20ZFS.html)》。本指南继续保留，仅作为遵循本指南完成的现有安装的参考。

### 注意事项

* 本 HOWTO 使用整块物理磁盘。
* 不要将这些说明用于双系统启动。
* 请先备份数据。任何现有数据都会被清除。

### 系统要求

* [64-bit Debian GNU/Linux Bookworm Live CD（带 GUI，例如 gnome ISO）](https://cdimage.debian.org/mirror/cdimage/release/current-live/amd64/iso-hybrid/)
* 强烈建议使用 [64-bit 内核](https://github.com/zfsonlinux/zfs/wiki/FAQ#32-bit-vs-64-bit-systems)。
* 在逻辑扇区为 4 KiB（“4Kn” 磁盘）的驱动器上安装，仅在 UEFI 启动模式下可行。这并非 ZFS 特有。[GRUB 在 legacy（BIOS）启动模式下无法也不会支持 4Kn。](http://savannah.gnu.org/bugs/?46700)

内存小于 2 GiB 的计算机运行 ZFS 会非常缓慢。基础工作负载下，建议至少 4 GiB 内存以获得正常性能。如果你希望使用去重（deduplication），则需要[大量内存](http://wiki.freebsd.org/ZFSTuningGuide#Deduplication)。启用去重是不可逆的永久性更改，无法轻易恢复。

### 支持

如果你需要帮助，可以通过 [邮件列表](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/Mailing%20Lists.html#mailing-lists) 或在 [Libera Chat](https://libera.chat/) 上的 IRC 频道 [#zfsonlinux](ircs://irc.libera.chat/#zfsonlinux) 联系社区。如果你有与本 HOWTO 相关的 Bug 报告或功能请求，请[提交新的 issue 并提及 @rlaager](https://github.com/openzfs/openzfs-docs/issues/new?body=@rlaager,%20I%20have%20the%20following%20issue%20with%20the%20Debian%20Bookworm%20Root%20on%20ZFS%20HOWTO:)。

### 贡献

1. Fork 并 clone：[https://github.com/openzfs/openzfs-docs](https://github.com/openzfs/openzfs-docs)
2. 安装工具：

   ```
   sudo apt install python3-pip

   pip3 install -r docs/requirements.txt

   # 将 ~/.local/bin 添加到你的 $PATH，例如把下面这行加入 ~/.bashrc：
   PATH=$HOME/.local/bin:$PATH
   ```
3. 进行你的修改。
4. 测试：

   ```
   cd docs
   make html
   sensible-browser _build/html/index.html
   ```
5. 使用 `git commit --signoff` 提交到分支，`git push`，并创建 pull request。提及 @rlaager。

### 加密

本指南支持三种不同的加密选项：不加密、ZFS 原生加密、以及 LUKS。无论选择哪一种，所有 ZFS 特性都可以完整使用。

不加密当然不会对任何内容进行加密。在没有加密的情况下，该选项自然具有最佳性能。

ZFS 原生加密会对根池中的数据以及大多数元数据进行加密。它不会加密 dataset 或 snapshot 的名称或属性。启动池完全不加密，但其中只包含引导加载器、内核和 initrd。（除非你在 `/etc/fstab` 中放置了密码，否则 initrd 中通常不会包含敏感数据。）系统在控制台输入口令之前无法启动。性能表现良好。由于加密发生在 ZFS 内部，即使使用多块磁盘（mirror 或 raidz 拓扑），数据也只需要加密一次。

LUKS 会对几乎所有内容进行加密。唯一未加密的数据是引导加载器、内核和 initrd。系统在控制台输入口令之前无法启动。性能表现良好，但 LUKS 位于 ZFS 之下，因此如果使用多块磁盘（mirror 或 raidz 拓扑），数据需要在每块磁盘上分别加密一次。

## 步骤 1：准备安装环境

1. 启动 Debian GNU/Linux Live CD。如果提示登录，请使用用户名 `user` 和密码 `live`。根据需要将系统连接到互联网（例如加入你的 WiFi 网络）。打开终端。
2. 配置并更新软件源：

   ```
   sudo vi /etc/apt/sources.list
   ```

   ```
   deb http://deb.debian.org/debian bookworm main contrib non-free-firmware
   ```

   ```
   sudo apt update
   ```
3. 可选：在 Live CD 环境中安装并启动 OpenSSH 服务器：
   如果你有第二台系统，通过 SSH 访问目标系统会更方便：

   ```
   sudo apt install --yes openssh-server

   sudo systemctl restart ssh
   ```

   **提示：** 你可以使用 `ip addr show scope global | grep inet` 查找你的 IP 地址。然后在主机上使用 `ssh user@IP` 进行连接。
4. 禁用自动挂载：
   如果磁盘之前被使用过（在相同偏移处存在分区），在未禁用的情况下，之前的文件系统（例如 ESP）可能会被自动挂载：

   ```
   gsettings set org.gnome.desktop.media-handling automount false
   ```
5. 切换为 root：

   ```
   sudo -i
   ```
6. 在 Live CD 环境中安装 ZFS：

   ```
   apt install --yes debootstrap gdisk zfsutils-linux
   ```

## 步骤 2：磁盘格式化

1. 使用磁盘名称设置变量：

   ```
   DISK=/dev/disk/by-id/scsi-SATA_disk1
   ```

   使用 ZFS 时始终应使用完整的 `/dev/disk/by-id/*` 别名。直接使用 `/dev/sd*` 设备节点可能会导致偶发的导入失败，尤其是在存在多个存储池的系统上。
   **提示：**

   * `ls -la /dev/disk/by-id` 将列出这些别名。
   * 你是在虚拟机中进行操作吗？如果你的虚拟磁盘在 `/dev/disk/by-id` 中缺失，且你在使用 KVM + virtio，可以使用 `/dev/vda`。同时，使用 `/dev/vda` 时，后续使用的分区名称也会有所不同。否则，请阅读“故障排除”章节。
   * 对于 mirror 或 raidz 拓扑，请使用 `DISK1`、`DISK2` 等。
   * 在选择 boot pool 大小时，请考虑你将如何使用这些空间。一个内核和 initrd 可能会占用大约 100M。如果你有多个内核并且会创建快照，boot pool 空间可能会变得紧张，尤其是在需要重新生成 initramfs 镜像时，每个镜像可能约为 85M。请根据你的需求合理规划 boot pool 的大小。
2. 如果你正在重复使用磁盘，请按需进行清理：
   确保 swap 分区未在使用中：

   ```
   swapoff --all
   ```

   如果该磁盘之前用于 MD 阵列：

   ```
   apt install --yes mdadm

   # 查看是否有一个或多个 MD 阵列处于活动状态：
   cat /proc/mdstat
   # 如果有，则停止它们（根据需要替换 ``md0``）：
   mdadm --stop /dev/md0

   # 对于使用整个磁盘的阵列：
   mdadm --zero-superblock --force $DISK
   # 对于使用分区的阵列：
   mdadm --zero-superblock --force ${DISK}-part2
   ```

   如果该磁盘之前用于 zfs：

   ```
   wipefs -a $DISK
   ```

   对于基于闪存的存储设备，如果磁盘之前被使用过，你可能希望执行一次全盘 discard（TRIM/UNMAP），这有助于提升性能：

   ```
   blkdiscard -f $DISK
   ```

   清除分区表：

   ```
   sgdisk --zap-all $DISK
   ```

   如果出现内核仍在使用旧分区表的提示，可以请求内核重新加载分区信息：

   ```
   partprobe $DISK
   ```

   如果新分区仍未显示，可以重启并重新开始（不过可以跳过本步骤）。
3. 对磁盘进行分区：
   如果需要传统（BIOS）启动，请运行：

   ```
   sgdisk -a1 -n1:24K:+1000K -t1:EF02 $DISK
   ```

   如果使用 UEFI 启动（当前或将来），请运行：

   ```
   sgdisk     -n2:1M:+512M   -t2:EF00 $DISK
   ```

   创建 boot pool 分区：

   ```
   sgdisk     -n3:0:+1G      -t3:BF01 $DISK
   ```

   在以下选项中选择其一：

   * 未加密或 ZFS 原生加密：

     ```
     sgdisk     -n4:0:0        -t4:BF00 $DISK
     ```
   * LUKS：

     ```
     sgdisk     -n4:0:0        -t4:8309 $DISK
     ```

   如果你要创建 mirror 或 raidz 拓扑，请对将要加入存储池的所有磁盘重复上述分区命令。
4. 创建 boot pool：

   ```
   zpool create \
       -o ashift=12 \
       -o autotrim=on \
       -o compatibility=grub2 \
       -o cachefile=/etc/zfs/zpool.cache \
       -O devices=off \
       -O acltype=posixacl -O xattr=sa \
       -O compression=lz4 \
       -O normalization=formD \
       -O relatime=on \
       -O canmount=off -O mountpoint=/boot -R /mnt \
       bpool ${DISK}-part3
   ```

   *注意：* GRUB 不支持所有的 zpool 特性（参见 `spa_feature_names`，位于 `grub-core/fs/zfs/zfs.c`）。这里为 `/boot` 单独创建一个 zpool，并指定 `-o compatibility=grub2` 属性，将该池限制为仅使用 GRUB 支持的特性，从而允许 root pool 使用任意或全部特性。
   更多信息请参阅 `zpool-features` 手册页中关于“Compatibility feature sets”的章节。
   **提示：**

   * 如果你要创建 mirror 拓扑，可以使用：

     ```
     zpool create \
         ... \
         bpool mirror \
         /dev/disk/by-id/scsi-SATA_disk1-part3 \
         /dev/disk/by-id/scsi-SATA_disk2-part3
     ```
   * 对于 raidz 拓扑，请将上述命令中的 `mirror` 替换为 `raidz`、`raidz2` 或 `raidz3`，并列出来自其他磁盘的分区。
   * 存储池名称是任意的。如果更改了名称，必须在后续步骤中保持一致。`bpool` 这一约定源自本 HOWTO。
5. 创建 root pool：
   在以下选项中选择其一：

   * 未加密：

     ```
     zpool create \
         -o ashift=12 \
         -o autotrim=on \
         -O acltype=posixacl -O xattr=sa -O dnodesize=auto \
         -O compression=lz4 \
         -O normalization=formD \
         -O relatime=on \
         -O canmount=off -O mountpoint=/ -R /mnt \
         rpool ${DISK}-part4
     ```
   * ZFS 原生加密：

     ```
     zpool create \
         -o ashift=12 \
         -o autotrim=on \
         -O encryption=on -O keylocation=prompt -O keyformat=passphrase \
         -O acltype=posixacl -O xattr=sa -O dnodesize=auto \
         -O compression=lz4 \
         -O normalization=formD \
         -O relatime=on \
         -O canmount=off -O mountpoint=/ -R /mnt \
         rpool ${DISK}-part4
     ```
   * LUKS：

     ```
     apt install --yes cryptsetup

     cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 ${DISK}-part4
     cryptsetup luksOpen ${DISK}-part4 luks1
     zpool create \
         -o ashift=12 \
         -o autotrim=on \
         -O acltype=posixacl -O xattr=sa -O dnodesize=auto \
         -O compression=lz4 \
         -O normalization=formD \
         -O relatime=on \
         -O canmount=off -O mountpoint=/ -R /mnt \
         rpool /dev/mapper/luks1
     ```

**注意事项：**

* 这里推荐使用 `ashift=12`，因为如今许多磁盘即使对外呈现为 512 B 逻辑扇区，实际上也具有 4 KiB（或更大）的物理扇区。此外，将来更换的磁盘也可能具有 4 KiB 物理扇区（此时 `ashift=12` 是理想选择），或者具有 4 KiB 逻辑扇区（此时 `ashift=12` 是必需的）。
* 设置 `-O acltype=posixacl` 会在全局启用 POSIX ACL。如果你不希望如此，可以移除此选项，但需要在之后为 `/var/log` 的 `zfs create` 命令添加 `-o acltype=posixacl`（注意：小写的 “o”），因为 journald 需要 ACL。
* 设置 `xattr=sa` 可以极大地提升扩展属性的性能。在 ZFS 内部，扩展属性用于实现 POSIX ACL。扩展属性也可被用户空间应用程序使用，一些桌面 GUI 应用会用到它们。Samba 也可以使用扩展属性来存储 Windows ACL 和 DOS 属性；它们对于 Samba Active Directory 域控制器是必需的。需要注意的是，`xattr=sa` 是 Linux 特有的。如果你将启用了 `xattr=sa` 的存储池移动到除 ZFS-on-Linux 之外的其他 OpenZFS 实现上，扩展属性将无法读取（但数据本身仍然可以）。如果扩展属性的可移植性对你很重要，请省略上面的 `-O xattr=sa`。即使你不希望整个存储池使用 `xattr=sa`，对 `/var/log` 使用它通常也是合适的。
* 设置 `normalization=formD` 可以消除与 UTF-8 文件名规范化相关的一些边缘情况。它还隐含启用了 `utf8only=on`，这意味着只允许 UTF-8 文件名。如果你希望支持非 UTF-8 文件名，请不要使用此选项。关于为何强制要求 UTF-8 文件名可能不是一个好主意的讨论，请参见相关链接。
* `recordsize` 未设置（保持默认的 128 KiB）。如果你希望进行调优（例如 `-O recordsize=1M`），请参阅相关博客文章。
* 设置 `relatime=on` 在传统 POSIX `atime` 行为（具有显著性能开销）与 `atime=off`（完全禁用 atime 更新以获得最佳性能）之间取得了折中。自 Linux 2.6.30 起，`relatime` 已成为其他文件系统的默认选项。更多信息请参见 RedHat 的文档。
* 请务必包含驱动器路径中的 `-part4` 部分。如果忘记这一点，就会指定整个磁盘，ZFS 将重新对其分区，从而导致你丢失 bootloader 分区。
* ZFS 原生加密现在默认使用 `aes-256-gcm`。
* 对于 LUKS，这里选择的密钥长度是 512 位。但 XTS 模式需要两个密钥，因此 LUKS 密钥会被一分为二。也就是说，`-s 512` 实际表示 AES-256。
* 你的口令短语很可能是最薄弱的一环。请慎重选择。相关指导请参见 cryptsetup FAQ 的第 5 节。

**提示：**

* 如果你要创建 mirror 拓扑，可以使用：

  ```
  zpool create \
      ... \
      rpool mirror \
      /dev/disk/by-id/scsi-SATA_disk1-part4 \
      /dev/disk/by-id/scsi-SATA_disk2-part4
  ```
* 对于 raidz 拓扑，请将上述命令中的 `mirror` 替换为 `raidz`、`raidz2` 或 `raidz3`，并列出来自其他磁盘的分区。
* 在使用 LUKS 的 mirror 或 raidz 拓扑时，请使用 `/dev/mapper/luks1`、`/dev/mapper/luks2` 等，这些需要通过 `cryptsetup` 创建。
* 存储池名称是任意的。如果更改了名称，必须在各处保持一致。在能够自动安装到 ZFS 的系统上，root pool 默认命名为 `rpool`。

## 步骤 3：系统安装

1. 创建作为容器的文件系统数据集：

   ```
   zfs create -o canmount=off -o mountpoint=none rpool/ROOT
   zfs create -o canmount=off -o mountpoint=none bpool/BOOT
   ```

   在 Solaris 系统中，root 文件系统会被克隆，并在通过 `pkg image-update` 或 `beadm` 进行重大系统变更时递增后缀。Ubuntu 中通过 `zsys` 工具实现了类似功能，不过其数据集布局更为复杂，而且 `zsys` 已处于维护边缘状态。即便没有此类工具，rpool/ROOT 和 bpool/BOOT 容器仍可用于手动创建的克隆。尽管如此，为了简化起见，本 HOWTO 假定 `/boot` 仅使用单一文件系统。
2. 为 root 和 boot 文件系统创建文件系统数据集：

   ```
   zfs create -o canmount=noauto -o mountpoint=/ rpool/ROOT/debian
   zfs mount rpool/ROOT/debian

   zfs create -o mountpoint=/boot bpool/BOOT/debian
   ```

   在 ZFS 中，通常不需要使用挂载命令（无论是 `mount` 还是 `zfs mount`）。这里是一个例外，因为使用了 `canmount=noauto`。
3. 创建数据集：

   ```
   zfs create                     rpool/home
   zfs create -o mountpoint=/root rpool/home/root
   chmod 700 /mnt/root
   zfs create -o canmount=off     rpool/var
   zfs create -o canmount=off     rpool/var/lib
   zfs create                     rpool/var/log
   zfs create                     rpool/var/spool
   ```

   以下数据集是可选的，取决于你的偏好和／或所使用的软件。
   如果你希望将它们分离以排除在快照之外：

   ```
   zfs create -o com.sun:auto-snapshot=false rpool/var/cache
   zfs create -o com.sun:auto-snapshot=false rpool/var/lib/nfs
   zfs create -o com.sun:auto-snapshot=false rpool/var/tmp
   chmod 1777 /mnt/var/tmp
   ```

   如果该系统使用 /srv：

   ```
   zfs create rpool/srv
   ```

   如果该系统使用 /usr/local：

   ```
   zfs create -o canmount=off rpool/usr
   zfs create                 rpool/usr/local
   ```

   如果该系统将安装游戏：

   ```
   zfs create rpool/var/games
   ```

   如果该系统将使用 GUI：

   ```
   zfs create rpool/var/lib/AccountsService
   zfs create rpool/var/lib/NetworkManager
   ```

   如果该系统将使用 Docker（其会管理自身的数据集和快照）：

   ```
   zfs create -o com.sun:auto-snapshot=false rpool/var/lib/docker
   ```

   如果该系统将在 /var/mail 中存储本地邮件：

   ```
   zfs create rpool/var/mail
   ```

   如果该系统将使用 Snap 软件包：

   ```
   zfs create rpool/var/snap
   ```

   如果该系统使用 /var/www：

   ```
   zfs create rpool/var/www
   ```

   后续推荐使用 tmpfs，但如果你希望为 `/tmp` 创建单独的数据集：

   ```
   zfs create -o com.sun:auto-snapshot=false  rpool/tmp
   chmod 1777 /mnt/tmp
   ```

   这种数据集布局的主要目标是将操作系统与用户数据分离。这样可以在回滚 root 文件系统时不回滚用户数据。
   如果你不做额外配置，`/tmp` 将作为 root 文件系统的一部分进行存储。或者，你也可以像上面那样为 `/tmp` 创建一个单独的数据集，从而将 `/tmp` 数据排除在 root 文件系统快照之外。这还允许你为 `rpool/tmp` 设置配额，以限制其最大使用空间。否则，你也可以在后续使用 tmpfs（内存文件系统）。
   **注意：** 如果你将启动所需的目录（例如 `/etc`）分离为单独的数据集，必须将其添加到 `/etc/default/zfs` 中的 `ZFS_INITRD_ADDITIONAL_DATASETS`。设置了 `canmount=off` 的数据集（如上面的 `rpool/usr`）不受此影响。
4. 在 /run 挂载 tmpfs：

   ```
   mkdir /mnt/run
   mount -t tmpfs tmpfs /mnt/run
   mkdir /mnt/run/lock
   ```
5. 安装最小系统：

   ```
   debootstrap bookworm /mnt
   ```

   `debootstrap` 命令会使新系统处于未配置状态。作为替代方案，你也可以将一个可用系统的全部内容复制到新的 ZFS root 中。
6. 复制 zpool.cache：

   ```
   mkdir /mnt/etc/zfs
   cp /etc/zfs/zpool.cache /mnt/etc/zfs/
   ```

## 步骤 4：系统配置

1. 配置主机名：
   将 `HOSTNAME` 替换为所需的主机名：

   ```
   hostname HOSTNAME
   hostname > /mnt/etc/hostname
   vi /mnt/etc/hosts
   ```

   ```
   添加一行：
   127.0.1.1       HOSTNAME
   或者如果系统在 DNS 中有正式名称：
   127.0.1.1       FQDN HOSTNAME
   ```

   **提示：** 如果你觉得 `vi` 难以使用，可以使用 `nano`。
2. 配置网络接口：
   查找接口名称：

   ```
   ip addr show
   ```

   将下面的 `NAME` 调整为与你的接口名称一致：

   ```
   vi /mnt/etc/network/interfaces.d/NAME
   ```

   ```
   auto NAME
   iface NAME inet dhcp
   ```

   如果系统不是 DHCP 客户端，请根据需要自定义此文件。
3. 可选：安装驱动固件和 WiFi 支持
   如果你是在笔记本电脑或无线网络是主要网络方式的设备上安装，上述步骤可能还不够，因为可能缺少合适的设备固件以及配置无线电的工具。可以安装一些额外的软件包来覆盖这一需求：

   ```
   apt install --yes firmware-linux wireless-tools
   ```
4. 配置软件包源：

   ```
   vi /mnt/etc/apt/sources.list
   ```

   ```
   deb http://deb.debian.org/debian bookworm main contrib non-free-firmware
   deb-src http://deb.debian.org/debian bookworm main contrib non-free-firmware

   deb http://deb.debian.org/debian-security bookworm-security main contrib non-free-firmware
   deb-src http://deb.debian.org/debian-security bookworm-security main contrib non-free-firmware

   deb http://deb.debian.org/debian bookworm-updates main contrib non-free-firmware
   deb-src http://deb.debian.org/debian bookworm-updates main contrib non-free-firmware
   ```
5. 将 LiveCD 环境中的虚拟文件系统绑定到新系统并 `chroot` 进入：

   ```
   mount --make-private --rbind /dev  /mnt/dev
   mount --make-private --rbind /proc /mnt/proc
   mount --make-private --rbind /sys  /mnt/sys
   chroot /mnt /usr/bin/env DISK=$DISK bash --login
   ```

   **注意：** 这里使用的是 `--rbind`，而不是 `--bind`。
6. 配置基础系统环境：

   ```
   apt update

   apt install --yes console-setup locales
   ```

   即使你偏好非英文的系统语言，也务必确保 `en_US.UTF-8` 可用：

   ```
   dpkg-reconfigure locales tzdata keyboard-configuration console-setup
   ```
7. 在 chroot 环境中为新系统安装 ZFS：

   ```
   apt install --yes dpkg-dev linux-headers-generic linux-image-generic

   apt install --yes zfs-initramfs

   echo REMAKE_INITRD=yes > /etc/dkms/zfs.conf
   ```

   **注意：** 请忽略任何提示 `ERROR: Couldn't resolve device` 和 `WARNING: Couldn't determine root device` 的错误信息。[cryptsetup 不支持 ZFS](https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906)。
8. 仅针对 LUKS 安装，配置 `/etc/crypttab`：

   ```
   apt install --yes cryptsetup cryptsetup-initramfs

   echo luks1 /dev/disk/by-uuid/$(blkid -s UUID -o value ${DISK}-part4) \
       none luks,discard,initramfs > /etc/crypttab
   ```

   使用 `initramfs` 是针对 [cryptsetup 不支持 ZFS](https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906) 的一种变通方案。
   **提示：** 如果你创建的是 mirror 或 raidz 拓扑，请为 `luks2` 等重复添加 `/etc/crypttab` 条目，并根据每块磁盘进行相应调整。
9. 安装 NTP 服务以同步时间。此步骤针对 Bookworm，因为在 bootstrap 过程中不会自动安装该软件包。虽然这一步对 ZFS 不是必须的，但在进行互联网访问时非常有用，因为本地时钟漂移可能导致登录失败：

   ```
   apt install systemd-timesyncd
   ```
10. 安装 GRUB
    从以下选项中选择其一：

    * 为传统（BIOS）启动安装 GRUB：

      ```
      apt install --yes grub-pc
      ```
    * 为 UEFI 启动安装 GRUB：

      ```
      apt install dosfstools

      mkdosfs -F 32 -s 1 -n EFI ${DISK}-part2
      mkdir /boot/efi
      echo /dev/disk/by-uuid/$(blkid -s UUID -o value ${DISK}-part2) \
         /boot/efi vfat defaults 0 0 >> /etc/fstab
      mount /boot/efi
      apt install --yes grub-efi-amd64 shim-signed
      ```

      **注意：**

      * `mkdosfs` 中的 `-s 1` 仅在磁盘提供 4 KiB 逻辑扇区（“4Kn” 磁盘）时才需要，用于满足 FAT32 的最小簇大小要求（在分区大小为 512 MiB 的情况下）。在提供 512 B 扇区的磁盘上同样可以正常工作。
      * 对于 mirror 或 raidz 拓扑，此步骤只会在第一块磁盘上安装 GRUB，其他磁盘将在后续步骤中处理。
11. 可选：移除 os-prober：

    ```
    apt purge --yes os-prober
    ```

    这样可以避免 update-grub 输出错误信息。os-prober 仅在双启动配置中才需要。
12. 设置 root 密码：

    ```
    passwd
    ```
13. 启用导入 bpool
    这可以确保无论 `/etc/zfs/zpool.cache` 是否存在、是否在 cachefile 中、或者 `zfs-import-scan.service` 是否启用，`bpool` 都会被导入。

    ```
    vi /etc/systemd/system/zfs-import-bpool.service
    ```

    ```
    [Unit]
    DefaultDependencies=no
    Before=zfs-import-scan.service
    Before=zfs-import-cache.service

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/sbin/zpool import -N -o cachefile=none bpool
    # 用于保留 zpool cache 的变通方案：
    ExecStartPre=-/bin/mv /etc/zfs/zpool.cache /etc/zfs/preboot_zpool.cache
    ExecStartPost=-/bin/mv /etc/zfs/preboot_zpool.cache /etc/zfs/zpool.cache

    [Install]
    WantedBy=zfs-import.target
    ```

    ```
    systemctl enable zfs-import-bpool.service
    ```

    **注意：** 在某些磁盘配置（例如 NVMe？）下，此服务[可能会失败](https://github.com/openzfs/openzfs-docs/issues/349)，并提示无法找到 `bpool`。如果发生这种情况，请在 `zpool import` 命令中添加 `-d DISK-part3`（将 `DISK` 替换为正确的设备路径）。
14. 可选（但推荐）：将 tmpfs 挂载到 `/tmp`
    如果你在前面选择创建了 `/tmp` 数据集，请跳过此步骤，因为两者是互斥的。否则，可以通过启用 `tmp.mount` 单元将 `/tmp` 放在 tmpfs（内存文件系统）上。

    ```
    cp /usr/share/systemd/tmp.mount /etc/systemd/system/
    systemctl enable tmp.mount
    ```
15. 可选：安装 SSH：

    ```
    apt install --yes openssh-server

    vi /etc/ssh/sshd_config
    # 设置：PermitRootLogin yes
    ```
16. 可选：针对 ZFS 原生加密或 LUKS，配置 Dropbear 以实现远程解锁：

    ```
    apt install --yes --no-install-recommends dropbear-initramfs
    mkdir -p /etc/dropbear/initramfs

    # 可选：将 OpenSSH 服务器密钥转换供 Dropbear 使用
    for type in ecdsa ed25519 rsa ; do
        cp /etc/ssh/ssh_host_${type}_key /tmp/openssh.key
        ssh-keygen -p -N "" -m PEM -f /tmp/openssh.key
        dropbearconvert openssh dropbear \
            /tmp/openssh.key \
            /etc/dropbear/initramfs/dropbear_${type}_host_key
    done
    rm /tmp/openssh.key

    # 以与 ~/.ssh/authorized_keys 相同的格式添加用户密钥
    vi /etc/dropbear/initramfs/authorized_keys

    # 如果使用静态 IP，为 initramfs 环境设置它：
    vi /etc/initramfs-tools/initramfs.conf
    # 语法为：IP=ADDRESS::GATEWAY:MASK:HOSTNAME:NIC
    # 例如：
    # IP=192.168.1.100::192.168.1.1:255.255.255.0:myhostname:ens3
    # HOSTNAME 和 NIC 为可选项。

    # 重建 initramfs（当更改上述任何内容时都需要）：
    update-initramfs -u -k all
    ```

    **注意：**

    * 转换服务器密钥可以让 Dropbear 使用与 OpenSSH 相同的密钥，从而避免主机密钥不匹配警告。目前，[dropbearconvert 无法识别新的 OpenSSH 私钥格式](https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=955384)，因此需要先使用 `ssh-keygen` 将密钥转换为旧的 PEM 格式。使用相同密钥的缺点是 OpenSSH 的密钥会以未加密形式存在于 initramfs 中。
    * 之后使用该功能时，在系统启动过程中提示输入口令时，以 root 身份通过 SSH 连接到系统。对于 ZFS 原生加密，运行 `zfsunlock`；对于 LUKS，运行 `cryptroot-unlock`。
    * 你也可以在 `authorized_keys` 行前添加 `command="/usr/bin/zfsunlock"` 或 `command="/bin/cryptroot-unlock"` 来强制执行解锁命令。这样解锁命令会自动运行，且只能运行该命令。
17. 可选（但非常希望）：安装 popcon
    `popularity-contest` 软件包会报告系统中已安装的软件包列表。显示 ZFS 的使用率可能有助于其在发行版中获得长期关注。

    ```
    apt install --yes popularity-contest
    ```

    在出现提示时选择 Yes。

## 步骤 5：GRUB 安装

1. 验证是否识别了 ZFS 启动文件系统：

   ```
   grub-probe /boot
   ```
2. 刷新 initrd 文件：

   ```
   update-initramfs -c -k all
   ```

   **注意：** 请忽略任何提示 `ERROR: Couldn't resolve device` 和 `WARNING: Couldn't determine root device` 的错误信息。[cryptsetup 不支持 ZFS](https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906)。
3. 解决 GRUB 缺少 zpool-features 支持的问题：

   ```
   vi /etc/default/grub
   # 设置：GRUB_CMDLINE_LINUX="root=ZFS=rpool/ROOT/debian"
   ```
4. 可选（但强烈推荐）：让 GRUB 调试更容易：

   ```
   vi /etc/default/grub
   # 从 GRUB_CMDLINE_LINUX_DEFAULT 中移除 quiet
   # 取消注释：GRUB_TERMINAL=console
   # 保存并退出。
   ```

   稍后，在系统已经成功重启两次并且你确认一切工作正常之后，如有需要，可以撤销这些更改。
5. 更新启动配置：

   ```
   update-grub
   ```

   **注意：** 如果存在，请忽略来自 `osprober` 的错误。
6. 安装引导加载器：
   从以下选项中选择其一：

   * 对于传统（BIOS）启动，将 GRUB 安装到 MBR：

     ```
     grub-install $DISK
     ```

     请注意，你是将 GRUB 安装到整个磁盘，而不是某个分区。
     如果你正在创建 mirror 或 raidz 拓扑，请对池中的每一块磁盘重复执行 `grub-install` 命令。
   * 对于 UEFI 启动，将 GRUB 安装到 ESP：

     ```
     grub-install --target=x86_64-efi --efi-directory=/boot/efi \
          --bootloader-id=debian --recheck --no-floppy

     不需要在这里指定磁盘。如果你正在创建 mirror
     或 raidz 拓扑，额外的磁盘将在后续步骤中处理。
     ```
7. 修复文件系统挂载顺序：
   我们需要启用 `zfs-mount-generator`。这会让 systemd 感知到各个独立的挂载点，这对于诸如 `/var/log` 和 `/var/tmp` 之类的路径非常重要。相应地，`rsyslog.service` 通过 `local-fs.target` 依赖于 `var-log.mount`，而使用 systemd 的 `PrivateTmp` 特性的服务会自动使用 `After=var-tmp.mount`。

   ```
   mkdir /etc/zfs/zfs-list.cache
   touch /etc/zfs/zfs-list.cache/bpool
   touch /etc/zfs/zfs-list.cache/rpool
   zed -F &
   ```

   通过确认以下文件不为空，来验证 `zed` 是否更新了缓存：

   ```
   cat /etc/zfs/zfs-list.cache/bpool
   cat /etc/zfs/zfs-list.cache/rpool
   ```

   如果其中任意一个为空，强制更新缓存并再次检查：

   ```
   zfs set canmount=on     bpool/BOOT/debian
   zfs set canmount=noauto rpool/ROOT/debian
   ```

   如果它们仍然为空，请停止 zed（如下所示），然后重新启动 zed（如上所示）并再次尝试。
   一旦这些文件中有了数据，就停止 `zed`：

   ```
   fg
   按 Ctrl-C。
   ```

   修正路径以消除 `/mnt`：

   ```
   sed -Ei "s|/mnt/?|/|" /etc/zfs/zfs-list.cache/*
   ```

## 步骤 6：首次启动

1. 可选：对初始安装创建快照：

   ```
   zfs snapshot bpool/BOOT/debian@install
   zfs snapshot rpool/ROOT/debian@install
   ```

   将来，你很可能会在每次升级之前创建快照，并在某个时间点删除旧的快照（包括这个），以节省空间。
2. 从 `chroot` 环境退出，返回到 LiveCD 环境：

   ```
   exit
   ```
3. 在 LiveCD 环境中运行以下命令以卸载所有文件系统：

   ```
   mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | \
       xargs -i{} umount -lf {}
   zpool export -a
   ```
4. 如果由于 busy 错误导致 export 失败，尝试杀掉所有可能正在使用它的进程：

   ```
   grep [p]ool /proc/*/mounts | cut -d/ -f3 | uniq | xargs kill
   zpool export -a
   ```
5. 如果即便如此池仍然处于 busy 状态，那么在启动时挂载它将会失败，你需要在 initramfs 提示符下执行 `zpool import -f rpool`，然后再执行 `exit`。
6. 重启：

   ```
   reboot
   ```

   等待新安装的系统正常启动。以 root 身份登录。
7. 创建一个用户账户：
   将 `YOUR_USERNAME` 替换为你希望使用的用户名：

   ```
   username=YOUR_USERNAME

   zfs create rpool/home/$username
   adduser $username

   cp -a /etc/skel/. /home/$username
   chown -R $username:$username /home/$username
   usermod -a -G audio,cdrom,dip,floppy,netdev,plugdev,sudo,video $username
   ```
8. 镜像 GRUB
   如果你安装到了多块磁盘上，请在额外的磁盘上安装 GRUB。

   * 对于传统（BIOS）启动：

     ```
     dpkg-reconfigure grub-pc
     ```

     一直按回车，直到进入设备选择界面。使用空格键选择池中所有的磁盘（而不是分区）。
   * 对于 UEFI 启动：

     ```
     umount /boot/efi
     ```

     对于第二块及之后的磁盘（将 debian-2 递增为 -3，依此类推）：

     ```
     dd if=/dev/disk/by-id/scsi-SATA_disk1-part2 \
        of=/dev/disk/by-id/scsi-SATA_disk2-part2
     efibootmgr -c -g -d /dev/disk/by-id/scsi-SATA_disk2 \
         -p 2 -L "debian-2" -l '\EFI\debian\grubx64.efi'

     mount /boot/efi
     ```

## 步骤 7：可选：配置 Swap

**注意**：在内存压力极高的系统上，使用 zvol 作为 swap 可能导致系统锁死，无论 swap 空间有多少。[上游有相关 bug 报告](https://github.com/zfsonlinux/zfs/issues/7734)。

1. 创建一个用于 swap 的 zvol：

   ```
   zfs create -V 4G -b $(getconf PAGESIZE) -o compression=zle \
       -o logbias=throughput -o sync=always \
       -o primarycache=metadata -o secondarycache=none \
       -o com.sun:auto-snapshot=false rpool/swap
   ```

   你可以根据需要调整大小（即 `4G` 部分）。
   压缩算法选择 `zle`，因为它是开销最低的算法。由于本指南推荐 `ashift=12`（磁盘上 4 KiB 块），常见的 4 KiB 页面大小情况下，没有压缩算法可以减少 I/O。唯一例外是全零页面，ZFS 会自动丢弃；但必须启用某种压缩才能达到这一效果。
2. 配置 swap 设备：
   **注意**：在配置文件中始终使用 `/dev/zvol` 的长别名，绝不可使用短别名 `/dev/zdX`。

   ```
   mkswap -f /dev/zvol/rpool/swap
   echo /dev/zvol/rpool/swap none swap discard 0 0 >> /etc/fstab
   echo RESUME=none > /etc/initramfs-tools/conf.d/resume
   ```

   `RESUME=none` 用于禁用休眠恢复。因为 zvol 在恢复脚本运行时尚未被导入，如果不禁用，启动过程会因为等待 swap zvol 出现而挂起约 30 秒。
3. 启用 swap 设备：

   ```
   swapon -av
   ```

## 步骤 8：完整软件安装

1. 升级最小系统：

   ```
   apt dist-upgrade --yes
   ```
2. 安装常规软件集：

   ```
   tasksel --new-install
   ```

   **注意**：默认会勾选“Debian 桌面环境”和“打印服务器”。如果你需要安装服务器，请取消选择这些选项。
3. 可选：禁用日志压缩：
   由于 `/var/log` 已由 ZFS 压缩，logrotate 的压缩会消耗 CPU 和磁盘 I/O，而收益通常很小。如果你对 `/var/log` 进行快照，logrotate 的压缩实际上会浪费空间，因为未压缩的数据仍存在快照中。可以手动编辑 `/etc/logrotate.d` 下的文件注释掉 `compress`，或者使用以下循环（推荐复制粘贴执行）：

   ```
   for file in /etc/logrotate.d/* ; do
       if grep -Eq "(^|[^#y])compress" "$file" ; then
           sed -i -r "s/(^|[^#y])(compress)/\1#\2/" "$file"
       fi
   done
   ```
4. 重启系统：

   ```
   reboot
   ```

## 步骤 9：最终清理

1. 等待系统正常启动。使用你创建的账户登录，确保系统（包括网络）正常运行。
2. 可选：删除初始安装的快照：

   ```
   sudo zfs destroy bpool/BOOT/debian@install
   sudo zfs destroy rpool/ROOT/debian@install
   ```
3. 可选：禁用 root 密码：

   ```
   sudo usermod -p '*' root
   ```
4. 可选（强烈推荐）：禁用 root SSH 登录：
   如果之前安装了 SSH，请撤销临时修改：

   ```
   sudo vi /etc/ssh/sshd_config
   # 删除: PermitRootLogin yes

   sudo systemctl restart ssh
   ```
5. 可选：重新启用图形化启动过程：
   如果你喜欢图形化启动界面，现在可以重新启用。使用 LUKS 时，界面看起来会更美观。

   ```
   sudo vi /etc/default/grub
   # 在 GRUB_CMDLINE_LINUX_DEFAULT 中添加 quiet
   # 注释掉 GRUB_TERMINAL=console
   # 保存并退出

   sudo update-grub
   ```

   **注意**：如果出现 `osprober` 错误，可忽略。
6. 可选：仅针对 LUKS 安装，备份 LUKS 头：

   ```
   sudo cryptsetup luksHeaderBackup /dev/disk/by-id/scsi-SATA_disk1-part4 \
       --header-backup-file luks1-header.dat
   ```

   将备份妥善保存（例如存储在云端）。它受你的 LUKS 密码保护，但你可能希望使用额外的加密。
   **提示**：如果创建了镜像或 raidz 拓扑，请对每个 LUKS 卷（如 `luks2` 等）重复此操作。

## 故障排除

### 使用 Live CD 进行救援

按照 [步骤 1：准备安装环境](https://openzfs.github.io/openzfs-docs/Getting%20Started/Debian/Debian%20Bookworm%20Root%20on%20ZFS.html#step-1-prepare-the-install-environment) 操作。

对于 LUKS，首先解锁磁盘：

```
apt install --yes cryptsetup

cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part4 luks1
# 如果是镜像或 raidz 拓扑，请对额外的磁盘重复此操作。
```

正确挂载所有文件系统：

```
zpool export -a
zpool import -N -R /mnt rpool
zpool import -N -R /mnt bpool
zfs load-key -a
zfs mount rpool/ROOT/debian
zfs mount -a
```

如有需要，可 `chroot` 进入已安装系统环境：

```
mount --make-private --rbind /dev  /mnt/dev
mount --make-private --rbind /proc /mnt/proc
mount --make-private --rbind /sys  /mnt/sys
mount -t tmpfs tmpfs /mnt/run
mkdir /mnt/run/lock
chroot /mnt /bin/bash --login
mount /boot/efi
mount -a
```

完成所需修复后，清理挂载：

```
exit
mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | \
    xargs -i{} umount -lf {}
zpool export -a
reboot
```

### Areca 控制器

需要 `arcsas` 驱动的系统，应将其添加到 `/etc/initramfs-tools/modules` 文件中，并运行：

```
update-initramfs -c -k all
```

如果内核日志中出现类似如下错误：

```
RIP: 0010:[<ffffffff8101b316>]  [<ffffffff8101b316>] native_read_tsc+0x6/0x20
```

请升级或降级 Areca 驱动。ZoL 在出现此错误的系统上可能不稳定。

### MPT2SAS 控制器

本教程的大多数问题报告涉及 `mpt2sas` 硬件，这类硬件会进行缓慢的异步驱动初始化，例如某些 IBM M1015 或刷成参考 LSI 固件的 OEM 卡。

基本问题是，这类控制器上的磁盘在 Linux 内核启动后才可见，而 ZoL 不会热插入池成员。详细说明见 [https://github.com/zfsonlinux/zfs/issues/330](https://github.com/zfsonlinux/zfs/issues/330)。

大多数 LSI 卡与 ZoL 完全兼容。如果你的卡出现此问题，可在 `/etc/default/zfs` 中设置：

```
ZFS_INITRD_PRE_MOUNTROOT_SLEEP=X
```

系统将在导入 ZFS 池之前等待 `X` 秒，以确保所有磁盘都出现。

### QEMU/KVM/XEN

为每个虚拟磁盘设置唯一的序列号（通过 libvirt 或 qemu），例如：

```
-drive if=none,id=disk1,file=disk1.qcow2,serial=1234567890
```

如果希望在虚拟机中使用 UEFI（而不仅仅是 BIOS 引导），在宿主机上执行：

```
sudo apt install ovmf
sudo vi /etc/libvirt/qemu.conf
```

取消注释以下行：

```
nvram = [
   "/usr/share/OVMF/OVMF_CODE.fd:/usr/share/OVMF/OVMF_VARS.fd",
   "/usr/share/OVMF/OVMF_CODE.secboot.fd:/usr/share/OVMF/OVMF_VARS.fd",
   "/usr/share/AAVMF/AAVMF_CODE.fd:/usr/share/AAVMF/AAVMF_VARS.fd",
   "/usr/share/AAVMF/AAVMF32_CODE.fd:/usr/share/AAVMF/AAVMF32_VARS.fd"
]
```

然后重启 libvirt 服务：

```
sudo systemctl restart libvirtd.service
```

### VMware

* 在 vmx 文件或 vSphere 配置中设置：

```
disk.EnableUUID = "TRUE"
```

这样可以确保在虚拟机中创建 `/dev/disk` 别名。
