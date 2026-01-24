# 根文件系统使用 ZFS 的 Debian9 Stretch

## 概述

### 提供了更新的版本

* 新安装请参阅《[根文件系统使用 ZFS 的 Debian 10 Buster](Debian-Buster-10.md)》。

### 注意事项

* 本教程将使用整块物理磁盘。
* 本教程不适用于双系统环境。
* 请先备份数据。现有数据都将被清除。

### 系统要求

* [64 位 Debian GNU/Linux Stretch Live CD](https://cdimage.debian.org/mirror/cdimage/release/current-live/amd64/iso-hybrid/)
* 强烈建议使用 [64-bit 内核](https://github.com/zfsonlinux/zfs/wiki/FAQ#32-bit-vs-64-bit-systems)。
* 在逻辑扇区为 4 KiB（“4Kn” 磁盘）的磁盘上安装，仅在 UEFI 启动模式下可行。这并非 ZFS 特有。[GRUB 在 legacy（BIOS）启动模式下无法也不会支持 4K 扇区。](http://savannah.gnu.org/bugs/?46700)

内存小于 2 GiB 的计算机运行 ZFS 时会非常缓慢。在基础工作负载下，建议至少 4 GiB 内存，才能获得正常性能。如果你希望使用去重（deduplication），则需要[大量内存](http://wiki.freebsd.org/ZFSTuningGuide#Deduplication)。启用去重是不可逆的永久性更改，无法轻易恢复。

### 支持

如果你需要帮助，可以通过 [邮件列表](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/Mailing%20Lists.html#mailing-lists) 或在 [Libera Chat](https://libera.chat/) 上的 IRC 频道 [#zfsonlinux](ircs://irc.libera.chat/#zfsonlinux) 联系社区。如果你有与本教程相关的 Bug 报告或功能请求，请[提交新的 issue 并 @rlaager](https://github.com/openzfs/openzfs-docs/issues/new?body=@rlaager,%20I%20have%20the%20following%20issue%20with%20the%20Debian%20Bullseye%20Root%20on%20ZFS%20教程:)。

### 贡献

1. 复刻并克隆：[https://github.com/openzfs/openzfs-docs](https://github.com/openzfs/openzfs-docs)
2. 安装工具：

   ```sh
   sudo apt install python3-pip

   pip3 install -r docs/requirements.txt

   # 将 ~/.local/bin 添加到你的 $PATH，例如把下面这行加入 ~/.bashrc：
   PATH=$HOME/.local/bin:$PATH
   ```
3. 进行你的修改。
4. 测试：

   ```sh
   cd docs
   make html
   sensible-browser _build/html/index.html
   ```
5. 使用 `git commit --signoff` 提交到分支，`git push`，并创建 pull request。提及 @rlaager。

### 加密

本指南支持两种加密方案：未加密和 LUKS（全盘加密）。ZFS 原生加密尚未发布。无论选择何种方式，所有 ZFS 功能均可完全使用。

未加密当然不会对任何数据进行加密。在没有加密开销的情况下，该方案自然具有最佳性能。

LUKS 会对几乎所有内容进行加密：操作系统、交换分区、用户主目录以及其他数据。唯一未加密的数据是引导加载程序、内核和 initrd。系统启动时必须在控制台输入密码，否则无法启动。性能表现良好，但 LUKS 位于 ZFS 下层，因此如果使用多块磁盘（镜像或 raidz 拓扑），每个磁盘上的数据都需要单独加密一次。


## 第一步：准备安装环境

1.1 启动 Debian GNU/Linux Live CD。如果出现提示，请使用用户名 `user` 和密码 `live` 进行登录。根据需要将系统连接到互联网（例如接入你的 WiFi 网络）。

1.2 可选：在 Live CD 环境中安装并启动 OpenSSH 服务器：

如果你有第二台设备，通过 SSH 访问目标系统会很方便。

```sh
$ sudo apt update
$ sudo apt install --yes openssh-server
$ sudo systemctl restart ssh
```

**提示：** 可以使用 `ip addr show scope global | grep inet` 查找你的 IP 地址。然后，从主机通过 `ssh user@IP` 连接。

1.3 切换为 root 用户：

```sh
$ sudo -i
```

1.4 设置，更新软件源：

```sh
# echo deb http://deb.debian.org/debian stretch contrib >> /etc/apt/sources.list
# echo deb http://deb.debian.org/debian stretch-backports main contrib >> /etc/apt/sources.list
# apt update
```

1.5 在 Live CD 环境中安装 ZFS：

```sh
# apt install --yes debootstrap gdisk dkms dpkg-dev linux-headers-amd64
# apt install --yes -t stretch-backports zfs-dkms
# modprobe zfs
```

* dkms 依赖项是手动安装的，以确保来自 stretch 而不是 stretch-backports。这并非关键步骤。

## 第二步：磁盘格式化

2.1 如果重复使用磁盘，根据需要清理：

```sh
如果磁盘之前用于 MD 阵列，请清除超级块：
# apt install --yes mdadm
# mdadm --zero-superblock --force /dev/disk/by-id/scsi-SATA_disk1

清除分区表：
# sgdisk --zap-all /dev/disk/by-id/scsi-SATA_disk1
```

2.2 对磁盘进行分区：

```sh
如果需要传统（BIOS）启动，运行：
# sgdisk -a1 -n1:24K:+1000K -t1:EF02 /dev/disk/by-id/scsi-SATA_disk1

如果使用 UEFI 启动（现在或未来使用），运行：
# sgdisk     -n2:1M:+512M   -t2:EF00 /dev/disk/by-id/scsi-SATA_disk1

为引导 pool 分区，运行：
# sgdisk     -n3:0:+1G      -t3:BF01 /dev/disk/by-id/scsi-SATA_disk1
```

选择以下其中任一方案：

2.2a 不加密：

```sh
# sgdisk     -n4:0:0        -t4:BF01 /dev/disk/by-id/scsi-SATA_disk1
```

2.2b LUKS 加密：

```sh
# sgdisk     -n4:0:0        -t4:8300 /dev/disk/by-id/scsi-SATA_disk1
```

在 ZFS 中始终使用长的别名 `/dev/disk/by-id/*`。直接使用设备节点 `/dev/sd*` 可能导致间歇性导入失败，尤其是在系统中存在多个存储池的情况下。

**提示：**

* 使用命令 `ls -la /dev/disk/by-id` 可以列出别名。
* 你是在虚拟机中操作吗？如果虚拟磁盘在 `/dev/disk/by-id` 中缺失，使用 KVM + virtio 时可用 `/dev/vda`；否则请参考[故障排查](https://openzfs.github.io/openzfs-docs/Getting%20Started/Debian/Debian%20Stretch%20Root%20on%20ZFS.html#troubleshooting)部分。
* 如果你要创建镜像或 raidz 拓扑，请对 pool 中的所有磁盘重复分区命令。

2.3 创建引导存储池：

```sh
# zpool create -o ashift=12 -d \
      -o feature@async_destroy=enabled \
      -o feature@bookmarks=enabled \
      -o feature@embedded_data=enabled \
      -o feature@empty_bpobj=enabled \
      -o feature@enabled_txg=enabled \
      -o feature@extensible_dataset=enabled \
      -o feature@filesystem_limits=enabled \
      -o feature@hole_birth=enabled \
      -o feature@large_blocks=enabled \
      -o feature@lz4_compress=enabled \
      -o feature@spacemap_histogram=enabled \
      -o feature@userobj_accounting=enabled \
      -O acltype=posixacl -O canmount=off -O compression=lz4 -O devices=off \
      -O normalization=formD -O relatime=on -O xattr=sa \
      -O mountpoint=/ -R /mnt \
      bpool /dev/disk/by-id/scsi-SATA_disk1-part3
```

通常无需为引导存储池自定义任何选项。

GRUB 并不支持所有 ZFS 存储池特性。参见 [grub-core/fs/zfs/zfs.c](http://git.savannah.gnu.org/cgit/grub.git/tree/grub-core/fs/zfs/zfs.c#n276) 中的 `spa_feature_names`。此步骤为 `/boot` 创建一个单独的引导存储池，仅启用 GRUB 支持的特性，从而让根存储池用任意特性。注意 GRUB 以只读方式打开存储池，因此所有兼容只读的特性都被 GRUB 支持。

**提示：**

* 如果创建镜像或 raidz 拓扑，可使用 `zpool create ... bpool mirror /dev/disk/by-id/scsi-SATA_disk1-part3 /dev/disk/by-id/scsi-SATA_disk2-part3`（或将 `mirror` 替换为 `raidz`、`raidz2` 或 `raidz3`，并列出额外磁盘的分区）。
* 可自定义存储池名称。如果更改，需在整个操作中保持一致。`bpool` 命名约定源自本教程。

2.4 创建根存储池：

选择以下其中任一方案：

2.4a 不加密：

```sh
# zpool create -o ashift=12 \
      -O acltype=posixacl -O canmount=off -O compression=lz4 \
      -O dnodesize=auto -O normalization=formD -O relatime=on -O xattr=sa \
      -O mountpoint=/ -R /mnt \
      rpool /dev/disk/by-id/scsi-SATA_disk1-part4
```

2.4b LUKS 加密：

```sh
# apt install --yes cryptsetup
# cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 \
      /dev/disk/by-id/scsi-SATA_disk1-part4
# cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part4 luks1
# zpool create -o ashift=12 \
      -O acltype=posixacl -O canmount=off -O compression=lz4 \
      -O dnodesize=auto -O normalization=formD -O relatime=on -O xattr=sa \
      -O mountpoint=/ -R /mnt \
      rpool /dev/mapper/luks1
```

* 建议在此使用 `ashift=12`，因为如今许多硬盘的物理扇区为 4KiB（或更大），即使它们呈现为 512B 的逻辑扇区。未来更换的硬盘可能具有 4KiB 物理扇区（此时 `ashift=12` 是可选的）或 4KiB 逻辑扇区（此时 `ashift=12` 是必需的）。
* 设置 `-O acltype=posixacl` 可全局启用 POSIX ACL。如果不需要，可移除此选项，但之后在创建 `/var/log` 的 `zfs create` 时需添加 `-o acltype=posixacl`（注意小写“o”），因为 [journald 需要 ACL](https://askubuntu.com/questions/970886/journalctl-says-failed-to-search-journal-acl-operation-not-supported)。
* 设置 `normalization=formD` 可消除一些与 UTF-8 文件名规范化相关的极端情况，同时隐含 `utf8only=on`，意味着只允许 UTF-8 文件名。如果希望支持非 UTF-8 文件名，请勿使用此选项。关于强制 UTF-8 文件名可能带来的问题，请参见 [The problems with enforced UTF-8 only filenames](http://utcc.utoronto.ca/~cks/space/blog/linux/ForcedUTF8Filenames)。
* 设置 `relatime=on` 是经典 POSIX `atime` 行为（性能影响较大）和 `atime=off`（完全禁用 atime 更新来获得最佳性能）之间的折中。自 Linux 2.6.30 起，其他文件系统默认启用 `relatime`。详情请参见 [RedHat 文档](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/power_management_guide/relatime)。
* 设置 `xattr=sa` 可显著提升扩展属性性能 [performance of extended attributes](https://github.com/zfsonlinux/zfs/commit/82a37189aac955c81a59a5ecc3400475adb56355)。在 ZFS 内部，扩展属性用于实现 POSIX ACL，也可被用户空间应用使用。[部分桌面 GUI 应用使用扩展属性](https://en.wikipedia.org/wiki/Extended_file_attributes#Linux)。[Samba 可利用扩展属性存储 Windows ACL 和 DOS 属性；Samba Active Directory 域控制器也需要它们](https://wiki.samba.org/index.php/Setting_up_a_Share_Using_Windows_ACLs)。请注意，`xattr=sa` 是 Linux 特有的。如果将 `xattr=sa` 过是存储池移动到除 ZFS-on-Linux 之外的 OpenZFS 实现，扩展属性将不可读（数据本身仍可读）。若扩展属性的可移植性对你很重要，请省略上述 `-O xattr=sa`。即便不为整个存储池使用 `xattr=sa`，在 `/var/log` 使用通常没有问题。
* 确保包含驱动路径的 `-part4` 部分。如果忘记，将指定整个磁盘，ZFS 会重新分区，从而丢失引导加载器分区。
* 对于 LUKS，选择的密钥大小为 512 位。但 XTS 模式需要两个密钥，因此 LUKS 密钥会被拆分为两半，`-s 512` 即表示 AES-256。
* 密码可能是安全链中最薄弱的环节，请谨慎选择。参考 [cryptsetup FAQ 第 5 节](https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions#5-security-aspects) 获取指导。

**提示：**

* 如果创建镜像或 raidz 拓扑，可使用 `zpool create ... rpool mirror /dev/disk/by-id/scsi-SATA_disk1-part4 /dev/disk/by-id/scsi-SATA_disk2-part4`（或将 `mirror` 替换为 `raidz`、`raidz2` 或 `raidz3`，并列出额外磁盘的分区）。对于 LUKS，使用 `/dev/mapper/luks1`、`/dev/mapper/luks2` 等，需要通过 `cryptsetup` 创建。
* 存储池名称可自定义。如果要更改，需在所有操作中保持一致。在可自动安装到 ZFS 的系统上，根存储池默认命名为 `rpool`。

## 第三步：系统安装

3.1 创建作为容器的文件系统数据集：

```sh
# zfs create -o canmount=off -o mountpoint=none rpool/ROOT
# zfs create -o canmount=off -o mountpoint=none bpool/BOOT
```

在 Solaris 系统上，根文件系统会被克隆，并在通过 `pkg image-update` 或 `beadm` 进行重大系统变更时增加后缀。APT 虽可实现类似功能，但目前尚未实现。即使没有此类工具，仍可用于手动创建的克隆。

3.2 为根文件系统和引导文件系统创建文件系统数据集：

```sh
# zfs create -o canmount=noauto -o mountpoint=/ rpool/ROOT/debian
# zfs mount rpool/ROOT/debian

# zfs create -o canmount=noauto -o mountpoint=/boot bpool/BOOT/debian
# zfs mount bpool/BOOT/debian
```

在 ZFS 中通常不需要使用挂载命令（`mount` 或 `zfs mount`），此处之所以需要，是因为设置了 `canmount=noauto`。

3.3 创建数据集：

```sh
# zfs create                                 rpool/home
# zfs create -o mountpoint=/root             rpool/home/root
# zfs create -o canmount=off                 rpool/var
# zfs create -o canmount=off                 rpool/var/lib
# zfs create                                 rpool/var/log
# zfs create                                 rpool/var/spool
```

以下数据集可选，取决于你的偏好，软件选择：

如果希望排除在快照之外：

```sh
# zfs create -o com.sun:auto-snapshot=false  rpool/var/cache
# zfs create -o com.sun:auto-snapshot=false  rpool/var/tmp
# chmod 1777 /mnt/var/tmp
```

如果系统使用 `/opt`：

```sh
# zfs create                                 rpool/opt
```

如果系统使用 `/srv`：

```sh
# zfs create                                 rpool/srv
```

如果系统使用 `/usr/local`：

```sh
# zfs create -o canmount=off                 rpool/usr
# zfs create                                 rpool/usr/local
```

如果系统将安装游戏：

```sh
# zfs create                                 rpool/var/games
```

如果系统将在 `/var/mail` 存储本地邮件：

```sh
# zfs create                                 rpool/var/mail
```

如果系统将使用 Snap 软件包：

```sh
# zfs create                                 rpool/var/snap
```

如果系统使用 `/var/www`：

```sh
# zfs create                                 rpool/var/www
```

如果系统将使用 GNOME：

```sh
# zfs create                                 rpool/var/lib/AccountsService
```

如果系统将使用 Docker（管理自己的数据集和快照）：

```sh
# zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/docker
```

如果系统将使用 NFS（锁定）：

```sh
# zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/nfs
```

建议之后使用 tmpfs，但如果希望为 `/tmp` 创建单独的数据集：

```sh
# zfs create -o com.sun:auto-snapshot=false  rpool/tmp
# chmod 1777 /mnt/tmp
```

此数据集布局的主要目标是将操作系统与用户数据分离。这样可以在回滚根文件系统时，不影响用户数据，如 `/var/log` 中的日志。这在将来集成 `beadm` 或类似工具时尤为重要。`com.sun.auto-snapshot` 设置被一些 ZFS 快照工具用来排除临时数据。

如果不做额外操作，`/tmp` 将作为根文件系统的一部分存储。或者，你可以像上文示例那样为 `/tmp` 创建单独的数据集，这样 `/tmp` 数据不会包含在根文件系统的快照中。还可以对 `rpool/tmp` 设置配额，以限制最大使用空间。后续还可以使用 tmpfs（RAM 文件系统）。

3.4 安装最小系统：

```sh
# debootstrap stretch /mnt
# zfs set devices=off rpool
```

`debootstrap` 命令会将新系统保持在未配置状态。替代方法是将既有可用系统的全部内容复制到新的 ZFS 根中。

## 第四步：系统配置

4.1 配置主机名（将 `HOSTNAME` 替换为所需主机名）。

```sh
# echo HOSTNAME > /mnt/etc/hostname

# vi /mnt/etc/hosts
添加一行：
127.0.1.1       HOSTNAME
或者如果系统在 DNS 中有真实名称：
127.0.1.1       FQDN HOSTNAME
```

**提示：** 如果觉得 `vi` 使用困难，可使用 `nano`。

4.2 配置网络接口：

```sh
查找接口名称：
# ip addr show

# vi /mnt/etc/network/interfaces.d/NAME
auto NAME
iface NAME inet dhcp
```

如果系统不是 DHCP 客户端，请自定义此文件。

4.3 配置软件源：

```ini
# vi /mnt/etc/apt/sources.list
deb http://deb.debian.org/debian stretch main contrib
deb-src http://deb.debian.org/debian stretch main contrib
deb http://security.debian.org/debian-security stretch/updates main contrib
deb-src http://security.debian.org/debian-security stretch/updates main contrib
deb http://deb.debian.org/debian stretch-updates main contrib
deb-src http://deb.debian.org/debian stretch-updates main contrib

# vi /mnt/etc/apt/sources.list.d/stretch-backports.list
deb http://deb.debian.org/debian stretch-backports main contrib
deb-src http://deb.debian.org/debian stretch-backports main contrib

# vi /mnt/etc/apt/preferences.d/90_zfs
Package: src:zfs-linux
Pin: release n=stretch-backports
Pin-Priority: 990
```

4.4 将 LiveCD 环境的虚拟文件系统绑定到新系统并 `chroot` 进入：

```sh
# mount --rbind /dev  /mnt/dev
# mount --rbind /proc /mnt/proc
# mount --rbind /sys  /mnt/sys
# chroot /mnt /bin/bash --login
```

>**注意：** 使
>
>用的是 `--rbind`，而不是 `--bind`。

4.5 配置基本系统环境：

```sh
# ln -s /proc/self/mounts /etc/mtab
# apt update

# apt install --yes locales
# dpkg-reconfigure locales
```

即使你需要非英语系统语言，也需确保 `en_US.UTF-8` 可用。

```sh
# dpkg-reconfigure tzdata
```

4.6 在新系统的 chroot 环境中安装 ZFS：

```sh
# apt install --yes dpkg-dev linux-headers-amd64 linux-image-amd64
# apt install --yes zfs-initramfs
```

4.7 仅针对 LUKS 安装，配置 crypttab：

```sh
# apt install --yes cryptsetup

# echo luks1 UUID=$(blkid -s UUID -o value \
      /dev/disk/by-id/scsi-SATA_disk1-part4) none \
      luks,discard,initramfs > /etc/crypttab
```

* 使用 `initramfs` 是为了绕过 [cryptsetup 不支持 ZFS](https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906) 的问题。

>**提示：**
>
>如果创建镜像或 raidz 拓扑，请为 `luks2` 等磁盘重复 `/etc/crypttab` 条目。

4.8 安装 GRUB

选择以下其中任一方案：

4.8a 安装 GRUB 用于传统（BIOS）启动

```sh
# apt install --yes grub-pc
```

将 GRUB 安装到磁盘，而非分区。

4.8b 安装 GRUB 用于 UEFI 启动

```sh
# apt install dosfstools
# mkdosfs -F 32 -s 1 -n EFI /dev/disk/by-id/scsi-SATA_disk1-part2
# mkdir /boot/efi
# echo PARTUUID=$(blkid -s PARTUUID -o value \
      /dev/disk/by-id/scsi-SATA_disk1-part2) \
      /boot/efi vfat nofail,x-systemd.device-timeout=1 0 1 >> /etc/fstab
# mount /boot/efi
# apt install --yes grub-efi-amd64 shim
```

* `mkdosfs` 中的 `-s 1` 仅对呈现 4 KiB 逻辑扇区（“4Kn” 硬盘）的驱动器必要，以满足 FAT32 的最小簇大小（针对 512 MiB 分区），对呈现 512 B 扇区的驱动器也适用。

>**注意：**
>
>如果创建镜像或 raidz 拓扑，此步骤仅在第一块磁盘上安装 GRUB，其他磁盘稍后处理。

4.9 设置 root 密码

```sh
# passwd
```

4.10 启用 bpool 导入

这可确保 `bpool` 始终被导入，无论在 `/etc/zfs/zpool.cache` 中是否存在、是否在缓存文件中，是否启用 `zfs-import-scan.service`。

```ini
# vi /etc/systemd/system/zfs-import-bpool.service
[Unit]
DefaultDependencies=no
Before=zfs-import-scan.service
Before=zfs-import-cache.service

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/sbin/zpool import -N -o cachefile=none bpool

[Install]
WantedBy=zfs-import.target

# systemctl enable zfs-import-bpool.service
```

4.11 可选（但推荐）：将 tmpfs 挂载到 /tmp

如果之前创建了数据集 `/tmp`，则请跳过此步骤，因为两者冲突。否则，可以通过启用 `tmp.mount` 单元，将 `/tmp` 放在 tmpfs（RAM 文件系统）上。

```sh
# cp /usr/share/systemd/tmp.mount /etc/systemd/system/
# systemctl enable tmp.mount
```

4.12 可选（但推荐）：安装 popcon

软件包 `popularity-contest` 会报告系统上安装的软件列表。显示 ZFS 的受欢迎程度有助于让 ZFS 获得发行版长期关注。

```sh
# apt install --yes popularity-contest
```

在出现提示时选择 `Yes`。

## 第五步：安装 GRUB 

5.1 验证 ZFS 引导文件系统是否被识别：

```sh
# grub-probe /boot
zfs
```

5.2 更新 initrd 文件：

```sh
# update-initramfs -u -k all
update-initramfs: Generating /boot/initrd.img-4.9.0-8-amd64
```

>**注意：**
>
>在使用 LUKS 时，可能会显示 “WARNING could not determine root device from /etc/fstab”。这是因为 [cryptsetup 不支持 ZFS](https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906)。

5.3 解决 GRUB 对 ZFS 存储池特性支持缺失的问题：

```sh
# vi /etc/default/grub
设置：GRUB_CMDLINE_LINUX="root=ZFS=rpool/ROOT/debian"
```

5.4 可选（但强烈建议）：便于调试 GRUB：

```ini
# vi /etc/default/grub
从 GRUB_CMDLINE_LINUX_DEFAULT 中移除 quiet
取消注释：GRUB_TERMINAL=console
保存并退出。
```

系统重启两次并确认一切正常后，可根据需要撤销这些更改。

5.5 更新引导配置：

```sh
# update-grub
Generating grub configuration file ...
Found linux image: /boot/vmlinuz-4.9.0-8-amd64
Found initrd image: /boot/initrd.img-4.9.0-8-amd64
done
```

>**注意：**
>
>如果出现报错 `osprober`，则可忽略。

5.6 安装引导加载器

5.6a 对于传统（BIOS）启动，将 GRUB 安装到 MBR：

```sh
# grub-install /dev/disk/by-id/scsi-SATA_disk1
Installing for i386-pc platform.
Installation finished. No error reported.
```

在得到完全相同的结果信息前，请勿重启计算机。注意，此操作是将 GRUB 安装到整个磁盘，而非分区。

如果创建镜像或 raidz 拓扑，请对 pool 中的每块磁盘重复执行 `grub-install` 命令。

5.6b 对于 UEFI 启动，安装 GRUB：

```sh
# grub-install --target=x86_64-efi --efi-directory=/boot/efi \
      --bootloader-id=debian --recheck --no-floppy
```

5.7 验证 ZFS 模块安装情况：

```sh
# ls /boot/grub/*/zfs.mod
```

5.8 修复文件系统挂载顺序

[在 ZFS 支持 systemd 挂载生成器之前](https://github.com/zfsonlinux/zfs/issues/4898)，文件系统挂载与某些守护进程启动之间存在竞争问题。实际上，问题（如 [#5754](https://github.com/zfsonlinux/zfs/issues/5754)）似乎出现在 `/var` 中的某些文件系统，特别是 `/var/log` 和 `/var/tmp`。将它们设置为使用 `legacy` 挂载，并在 `/etc/fstab` 中列出，使 systemd 知道它们是独立的挂载点。这样，`rsyslog.service` 通过 `local-fs.target` 依赖于 `var-log.mount`，使用 systemd `PrivateTmp` 特性的服务会自动依赖 `After=var-tmp.mount`。

现在，initramfs 尚未支持挂载 `/boot`，我们仍然需要手动挂载 `/boot`，因为它被标记为 `canmount=noauto`。此外，对于 UEFI，需要确保在其子文件系统 `/boot/efi` 挂载之前先挂载 `/boot`。

`rpool` 已由 initramfs 保证导入，因此不需要在这些文件系统上添加 `x-systemd.requires=zfs-import.target`。

```sh
对于 UEFI 启动，先卸载 /boot/efi：
# umount /boot/efi

其他操作适用于 BIOS 和 UEFI 启动：

# zfs set mountpoint=legacy bpool/BOOT/debian
# echo bpool/BOOT/debian /boot zfs \
      nodev,relatime,x-systemd.requires=zfs-import-bpool.service 0 0 >> /etc/fstab

# zfs set mountpoint=legacy rpool/var/log
# echo rpool/var/log /var/log zfs nodev,relatime 0 0 >> /etc/fstab

# zfs set mountpoint=legacy rpool/var/spool
# echo rpool/var/spool /var/spool zfs nodev,relatime 0 0 >> /etc/fstab

如果创建了 /var/tmp dataset：
# zfs set mountpoint=legacy rpool/var/tmp
# echo rpool/var/tmp /var/tmp zfs nodev,relatime 0 0 >> /etc/fstab

如果创建了 /tmp dataset：
# zfs set mountpoint=legacy rpool/tmp
# echo rpool/tmp /tmp zfs nodev,relatime 0 0 >> /etc/fstab
```

## 第六步：首次启动

6.1 对初始安装进行快照：

```sh
# zfs snapshot bpool/BOOT/debian@install
# zfs snapshot rpool/ROOT/debian@install
```

将来，你可能希望在每次升级前创建快照，并在适当时候删除旧快照（包括此快照）以节省空间。

6.2 退出 `chroot` 环境回到 LiveCD 环境：

```sh
# exit
```

6.3 在 LiveCD 环境中运行以下命令卸载所有文件系统：

```sh
# mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | xargs -i{} umount -lf {}
# zpool export -a
```

6.4 重启：

```
# reboot
```

6.5 等待新安装的系统正常启动，使用 root 登录。

6.6 创建用户账户：

```sh
# zfs create rpool/home/你的用户名
# adduser 你的用户名
# cp -a /etc/skel/.[!.]* /home/你的用户名
# chown -R 你的用户名:你的用户名 /home/你的用户名
```

6.7 将用户账户添加到默认管理员组：

```sh
# usermod -a -G audio,cdrom,dip,floppy,netdev,plugdev,sudo,video 你的用户名
```

6.8 镜像 GRUB

如果安装到多块磁盘，请在其他磁盘上安装 GRUB：

6.8a 对于传统（BIOS）启动：

```sh
# dpkg-reconfigure grub-pc
按回车直到设备选择界面。
使用空格选择 pool 中的所有磁盘（非分区）。
```

6.8b UEFI

```sh
# umount /boot/efi

对于第二块及之后的磁盘（将 debian-2 递增到 -3 等）：
# dd if=/dev/disk/by-id/scsi-SATA_disk1-part2 \
     of=/dev/disk/by-id/scsi-SATA_disk2-part2
# efibootmgr -c -g -d /dev/disk/by-id/scsi-SATA_disk2 \
      -p 2 -L "debian-2" -l '\EFI\debian\grubx64.efi'

# mount /boot/efi
```

## 第七步：（可选）配置交换空间

>**注意**：
>
>在内存压力极高的系统上，使用 zvol 作为交换设备可能导致系统锁死，无论交换空间还有多少可用。目前该问题正在调查中：[https://github.com/zfsonlinux/zfs/issues/7734](https://github.com/zfsonlinux/zfs/issues/7734)

7.1 创建用于交换的卷数据集（zvol）：

```sh
# zfs create -V 4G -b $(getconf PAGESIZE) -o compression=zle \
      -o logbias=throughput -o sync=always \
      -o primarycache=metadata -o secondarycache=none \
      -o com.sun:auto-snapshot=false rpool/swap
```

可以根据需要调整大小（`4G` 部分）。

压缩算法设置为 `zle`，因为这是开销最小的算法。由于本指南推荐使用 `ashift=12`（磁盘上 4 KiB 块），对于常见的 4 KiB 页大小，没有压缩算法能降低 I/O。例外情况是全零页，ZFS 会丢弃它们；但必须启用某种压缩才能实现此行为。

7.2 配置交换设备：

>**注意**：
>
>在配置文件中始终使用长别名 `/dev/zvol`，绝不要使用短 `/dev/zdX` 设备名。

```sh
# mkswap -f /dev/zvol/rpool/swap
# echo /dev/zvol/rpool/swap none swap discard 0 0 >> /etc/fstab
# echo RESUME=none > /etc/initramfs-tools/conf.d/resume
```

`RESUME=none` 用于禁用从休眠恢复。因为在恢复脚本运行时 zvol 尚未导入（未导入存储池），所以如果不禁用，启动过程会等待交换 zvol 出现而停滞 30 秒。

7.3 启用交换设备：

```sh
# swapon -av
```

## 第八步：安装完整软件

8.1 升级最小系统：

```sh
# apt dist-upgrade --yes
```

8.2 安装常用软件集：

```sh
# tasksel
```

>**注意**：
>
>默认会勾选“Debian 桌面环境”和“打印服务器”。如果希望安装服务器版本，请取消勾选这些选项。

8.3 可选：禁用日志压缩：

由于 `/var/log` 已由 ZFS 压缩，logrotate 的压缩会消耗 CPU 和磁盘 I/O，但通常收益甚微。此外，如果你对 `/var/log` 进行快照，logrotate 的压缩反而会浪费空间，因为未压缩的数据仍然保留在快照中。你可以手动编辑 `/etc/logrotate.d` 中的文件注释掉 `compress`，或者使用以下循环（强烈建议复制粘贴）：

```sh
# for file in /etc/logrotate.d/* ; do
    if grep -Eq "(^|[^#y])compress" "$file" ; then
        sed -i -r "s/(^|[^#y])(compress)/\1#\2/" "$file"
    fi
done
```

8.4 重启：

```sh
# reboot
```

### 第九步：最终清理

9.1 等待系统正常启动，使用你创建的账户登录。确保系统（包括网络）正常工作。

9.2 可选：删除初始安装快照：

```sh
$ sudo zfs destroy bpool/BOOT/debian@install
$ sudo zfs destroy rpool/ROOT/debian@install
```

9.3 可选：禁用 root 密码：

```sh
$ sudo usermod -p '*' root
```

9.4 可选：重新启用图形化启动过程：

如果你希望使用图形化启动，现在可以重新启用。如果使用 LUKS，这会让提示界面更美观。

```sh
$ sudo vi /etc/default/grub
在 GRUB_CMDLINE_LINUX_DEFAULT 中添加 quiet
注释掉 GRUB_TERMINAL=console
保存并退出

$ sudo update-grub
```

>**注意**：
>
>如果出现 osprober 错误，可忽略。

9.5 可选：仅针对 LUKS 安装，备份 LUKS 头：

```sh
$ sudo cryptsetup luksHeaderBackup /dev/disk/by-id/scsi-SATA_disk1-part4 \
    --header-backup-file luks1-header.dat
```

将备份妥善保存（例如云存储）。备份受 LUKS 密码保护，但你也可以选择额外加密。

**提示**：如果你创建了镜像或 raidz 拓扑，请对每个 LUKS 卷重复此操作（`luks2` 等）。

## 故障排除

### 使用 Live CD 进行救援

请参考[第一步：准备安装环境](https://openzfs.github.io/openzfs-docs/Getting%20Started/Debian/Debian%20Stretch%20Root%20on%20ZFS.html#step-1-prepare-the-install-environment)。

这将自动导入你的存储池。导出并重新导入以修正挂载：

```sh
对于 LUKS，先解锁磁盘：
# apt install --yes cryptsetup
# cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part4 luks1
如果是镜像或 raidz 拓扑，请对其他磁盘重复操作。

# zpool export -a
# zpool import -N -R /mnt rpool
# zpool import -N -R /mnt bpool
# zfs mount rpool/ROOT/debian
# zfs mount -a
```

如有需要，可以 chroot 进入已安装系统：

```sh
# mount --rbind /dev  /mnt/dev
# mount --rbind /proc /mnt/proc
# mount --rbind /sys  /mnt/sys
# chroot /mnt /bin/bash --login
# mount /boot/efi
# mount -a
```

执行所需操作修复系统。

完成后，进行清理：

```sh
# exit
# mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | xargs -i{} umount -lf {}
# zpool export -a
# reboot
```

### MPT2SAS

本教程的大多数问题报告都与硬件 `mpt2sas` 相关，这类硬件会进行缓慢的异步磁盘初始化，例如一些 IBM M1015 或刷成参考 LSI 固件的 OEM 卡。

基本问题是，这些控制器上的磁盘在 Linux 内核启动常规系统之前不可见，而 ZoL 不支持热插拔存储池成员。详见 [https://github.com/zfsonlinux/zfs/issues/330](https://github.com/zfsonlinux/zfs/issues/330)。

大多数 LSI 卡与 ZoL 完全兼容。如果你的卡存在此问题，尝试在 `/etc/default/zfs` 中设置 `ZFS_INITRD_PRE_MOUNTROOT_SLEEP=X`。系统将在导入存储池前等待 X 秒以确保所有磁盘被识别。

### Areca

需要 `arcsas` 驱动的系统，应将 `arcsas` 添加到文件 `/etc/initramfs-tools/modules` 中，并运行 `update-initramfs -u -k all`。

如果内核日志中出现类似 `RIP: 0010:[<ffffffff8101b316>]  [<ffffffff8101b316>] native_read_tsc+0x6/0x20` 的信息，请升级或降级 Areca 驱动。在出现此错误信息的设备上使用 ZoL 并不稳定。

### VMware

* 在 vmx 文件或 vsphere 配置中设置 `disk.EnableUUID = "TRUE"`。此操作确保在虚拟机中创建 `/dev/disk` 别名。

### QEMU/KVM/XEN

使用 libvirt 或 qemu 为每个虚拟磁盘设置唯一序列号（例如 `-drive if=none,id=disk1,file=disk1.qcow2,serial=1234567890`）。

要在虚拟机中使用 UEFI（而不仅仅是 BIOS 启动），在宿主机上执行：

```sh
$ sudo apt install ovmf
$ sudo vi /etc/libvirt/qemu.conf
取消对下面这些行的注释：
nvram = [
   "/usr/share/OVMF/OVMF_CODE.fd:/usr/share/OVMF/OVMF_VARS.fd",
   "/usr/share/AAVMF/AAVMF_CODE.fd:/usr/share/AAVMF/AAVMF_VARS.fd"
]
$ sudo service libvirt-bin restart
```
