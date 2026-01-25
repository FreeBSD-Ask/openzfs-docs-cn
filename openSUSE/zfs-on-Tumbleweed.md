# 构建以 ZFS 为根文件系统的 openSUSE Tumbleweed

## 概览

### 注意事项

* 本教程使用整块物理磁盘。
* 本教程不适用于双系统。
* 备份你的数据。一切既有数据都将丢失。
* 这不是 openSUSE 官方教程。如果后续 openSUSE 新增了 Root on ZFS 的支持，本文档将会更新。此外，[openSUSE 的默认系统安装器 Yast2 不支持 zfs](https://forums.opensuse.org/showthread.php/510071-教程-Install-ZFSonLinux-on-OpenSuse)。本教程在不使用 Yast2 的情况下通过 zypper 设置系统的方法，基于社区中人员经验所撰写的 openSUSE 安装方法。有关更多信息，请查看外部链接。

### 系统要求

* [64 位 openSUSE Tumbleweed Live CD，带 GUI（例如 gnome iso）](https://software.opensuse.org/distributions/leap)
* [强烈建议使用 64 位内核](https://github.com/zfsonlinux/zfs/wiki/FAQ#32-bit-vs-64-bit-systems)
* 在提供 4 KiB 逻辑扇区（“4Kn”）的驱动器上进行的安装仅在使用 UEFI 启动时可行。这并非 ZFS 独有的问题。[在 4Kn 磁盘上使用传统（BIOS）启动时，GRUB 不能也不会工作。](http://savannah.gnu.org/bugs/?46700)

在内存少于 2 GiB 的计算机运行 ZFS 时，将存在严重的性能瓶颈。对于基础工作负载，建议至少使用 4 GiB 内存以获得正常性能。如果你希望使用去重功能，将需要[大量的内存](http://wiki.freebsd.org/ZFSTuningGuide#Deduplication)。启用去重是一项永久性更改，无法轻易还原。

### 支持

如果你需要帮助，可以通过 [邮件列表](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/Mailing%20Lists.html#mailing-lists) 或在 [Libera Chat](https://libera.chat/) 上的 IRC 频道 [#zfsonlinux](ircs://irc.libera.chat/#zfsonlinux) 联系社区。如果你有与本教程相关的 Bug 报告或功能请求，请提交新的 issue，并 [@Zaryob](https://github.com/Zaryob)。

### 贡献

1. 复刻然后克隆：[https://github.com/openzfs/openzfs-docs](https://github.com/openzfs/openzfs-docs)
2. 安装工具：

   ```sh
   sudo zypper install python3-pip
   pip3 install -r docs/requirements.txt
   # 将 ~/.local/bin 添加到你的 $PATH，例如通过将以下内容添加到 ~/.bashrc：
   PATH=$HOME/.local/bin:$PATH
   ```

3. 进行你的修改。
4. 测试：

   ```sh
   cd docs
   make html
   sensible-browser _build/html/index.html
   ```

5. 在分支上执行 `git commit --signoff`，然后 `git push`，并创建 pull request。

### 加密

本指南支持三种不同的加密方案：未加密、ZFS 原生加密、以及 LUKS。无论选择哪一种，都能完全使用一切 ZFS 特性。

未加密当然不会加密任何内容。在没有进行任何加密的情况下，该方案自然具有最佳性能。

ZFS 原生加密会对根池中的数据和大多数元数据进行加密。它不会加密 dataset 或 snapshot 的名称或属性。启动池完全不加密，但其中只包含 bootloader、kernel 和 initrd。（除非你在 `/etc/fstab` 中放置了密码，否则 initrd 不太可能包含敏感数据。）系统在未在控制台输入口令的情况下无法启动。性能良好。由于加密是在 ZFS 内部完成的，即使使用了多个磁盘（mirror 或 raidz 拓扑），数据也只需要加密一次。

LUKS 会加密几乎所有内容。唯一未加密的数据是 bootloader、kernel 和 initrd。系统在未在控制台输入口令的情况下无法启动。性能良好，但 LUKS 位于 ZFS 底层，因此如果使用了多个磁盘（mirror 或 raidz 拓扑），数据需要在每个磁盘上各加密一次。

## 第 1 步：准备安装环境

1. 启动 openSUSE Live CD。如果出现提示提示，请使用用户名 `live` 登录，密码 `live`。根据需要将系统连接到互联网（例如加入你的 WiFi 网络）。打开终端。
2. 设置更新软件仓库：

   ```sh
   sudo zypper addrepo https://download.opensuse.org/repositories/filesystems/openSUSE_Tumbleweed/filesystems.repo
   sudo zypper refresh   # 刷新所有软件仓库
   ```

3. 可选：在 Live CD 环境中安装并启动 OpenSSH 服务器：
   如果你有第二台系统，使用 SSH 访问目标系统会更加方便：

   ```sh
   sudo zypper install openssh-server
   sudo systemctl restart sshd.service
   ```

   >**提示：**
   >
   >你可以使用 `ip addr show scope global | grep inet` 查找你的 IP 地址。然后，在你的主机上，通过 `ssh user@IP` 进行连接。

4. 禁用自动挂载：
   如果磁盘之前被使用过（在相同偏移位置存在分区），在未禁用的情况下，先前的文件系统（例如 ESP）会被自动挂载：

   ```sh
   gsettings set org.gnome.desktop.media-handling automount false
   ```

5. 切换为 root：

   ```sh
   sudo -i
   ```

6. 在 Live CD 环境中安装 ZFS：

   ```sh
   zypper install zfs zfs-kmp-default
   zypper install gdisk
   modprobe zfs
   ```

## 第 2 步：格式化磁盘

1. 设置磁盘变量：

   ```ini
   DISK=/dev/disk/by-id/scsi-SATA_disk1
   ```

   在 ZFS 中始终使用长别名 `/dev/disk/by-id/*`。直接使用设备节点 `/dev/sd*` 可能导致偶发的导入失败，尤其是在系统中存在多个存储池时。

   **提示：**

   * `ls -la /dev/disk/by-id` 会列出别名。
   * 你是在虚拟机中操作吗？如果虚拟磁盘在 `/dev/disk/by-id` 中缺失，使用 KVM virtio 时可用 `/dev/vda`；否则，请参考[故障排查](https://openzfs.github.io/openzfs-docs/Getting%20Started/openSUSE/openSUSE%20Leap%20Root%20on%20ZFS.html#troubleshooting)部分。

3. 如果重复使用磁盘，根据需要清理：
   如果磁盘之前用于 MD 阵列：

   ```sh
   zypper install mdadm

   # 查看是否有一到多个 MD 阵列处于激活状态：
   cat /proc/mdstat
   # 如果有，停止它们（根据需要替换 ``md0``）：
   mdadm --stop /dev/md0

   # 对使用整个磁盘的阵列：
   mdadm --zero-superblock --force $DISK
   # 对使用分区的阵列：
   mdadm --zero-superblock --force ${DISK}-part2
   ```

   清除分区表：

   ```sh
   sgdisk --zap-all $DISK
   ```

   如果收到内核仍在使用旧分区表的提示，可以请求内核重新加载分区信息：

   ```sh
   partprobe $DISK
   ```

   如果新分区仍未显示，可重启并重新开始（此步骤可跳过）。

4. 分区你的磁盘：
   如果需要传统（BIOS）启动，运行：

   ```sh
   sgdisk -a1 -n1:24K:+1000K -t1:EF02 $DISK
   ```

   如果需要 UEFI 启动（现在或将来使用），运行：

   ```sh
   sgdisk     -n2:1M:+512M   -t2:EF00 $DISK
   ```

   为启动池创建分区：

   ```sh
   sgdisk     -n3:0:+1G      -t3:BF01 $DISK
   ```

   选择以下之一：

   * 未加密或 ZFS 原生加密：

     ```sh
     sgdisk     -n4:0:0        -t4:BF00 $DISK
     ```

   * LUKS：

     ```sh
     sgdisk     -n4:0:0        -t4:8309 $DISK
     ```

   * 如果创建镜像或 raidz 拓扑，请对将加入池的所有磁盘重复分区命令。

5. 创建启动池：

   ```sh
   zpool create \
       -o cachefile=/etc/zfs/zpool.cache \
       -o ashift=12 -d \
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
       -o feature@zpool_checkpoint=enabled \
       -O acltype=posixacl -O canmount=off -O compression=lz4 \
       -O devices=off -O normalization=formD -O relatime=on -O xattr=sa \
       -O mountpoint=/boot -R /mnt \
       bpool ${DISK}-part3
   ```

   对启动池无需自定义选项。

   GRUB 不支持全部的 zpool 功能。请参见 [grub-core/fs/zfs/zfs.c](http://git.savannah.gnu.org/cgit/grub.git/tree/grub-core/fs/zfs/zfs.c#n276) 中的 `spa_feature_names`。
   此步骤为 `/boot` 创建单独的启动池，其功能仅限于 GRUB 支持的功能，从而能够让根池使用任意功能。注意 GRUB 以只读方式打开池，因此所有只读兼容功能均被 GRUB “支持”。

   **提示：**

   * 如果创建镜像拓扑，请使用：

     ```sh
     zpool create \
         ... \
         bpool mirror \
         /dev/disk/by-id/scsi-SATA_disk1-part3 \
         /dev/disk/by-id/scsi-SATA_disk2-part3
     ```

   * 对于 raidz 拓扑，将上面命令中的 `mirror` 替换为 `raidz`、`raidz2` 或 `raidz3`，并列出其他磁盘的分区。
   * 池名称可自定义。若更改，新名称必须保持一致使用。`bpool` 命名约定来源于本教程。

   **功能说明：**

   * `allocation_classes` 功能安全可用。但除非使用它（如 `special` vdev），否则启用它无意义。几乎不会有人在启动池使用该功能。如果关注启动池速度，将整个池放在更快的磁盘上比使用 `special` vdev 更合理。
   * `project_quota` 功能经过测试，安全可用。对启动池而言几乎无实际意义。
   * `resilver_defer` 功能安全，但启动池较小，通常无需使用。
   * `spacemap_v2` 功能经过测试，安全可用。启动池较小，实际影响不大。
   * 作为只读兼容功能，`userobj_accounting` 理论上兼容，但在实践中 GRUB 可能报错“invalid dnode type”。此功能对 `/boot` 无关紧要。

7. 创建根池：
   选择以下方案之一：

   * 未加密：

     ```sh
     zpool create \
         -o cachefile=/etc/zfs/zpool.cache \
         -o ashift=12 \
         -O acltype=posixacl -O canmount=off -O compression=lz4 \
         -O dnodesize=auto -O normalization=formD -O relatime=on \
         -O xattr=sa -O mountpoint=/ -R /mnt \
         rpool ${DISK}-part4
     ```

   * ZFS 原生加密：

     ```sh
     zpool create \
         -o cachefile=/etc/zfs/zpool.cache \
         -o ashift=12 \
         -O encryption=on \
         -O keylocation=prompt -O keyformat=passphrase \
         -O acltype=posixacl -O canmount=off -O compression=lz4 \
         -O dnodesize=auto -O normalization=formD -O relatime=on \
         -O xattr=sa -O mountpoint=/ -R /mnt \
         rpool ${DISK}-part4
     ```

   * LUKS：

     ```sh
     zypper install cryptsetup
     cryptsetup luksFormat -c aes-xts-plain64 -s 512 -h sha256 ${DISK}-part4
     cryptsetup luksOpen ${DISK}-part4 luks1
     zpool create \
         -o cachefile=/etc/zfs/zpool.cache \
         -o ashift=12 \
         -O acltype=posixacl -O canmount=off -O compression=lz4 \
         -O dnodesize=auto -O normalization=formD -O relatime=on \
         -O xattr=sa -O mountpoint=/ -R /mnt \
         rpool /dev/mapper/luks1
     ```

**备注：**

* 这里推荐使用 `ashift=12`，因为如今许多硬盘的物理扇区为 4 KiB（或更大），即使它们显示为 512 B 的逻辑扇区。此外，未来更换的硬盘可能是 4 KiB 物理扇区（此时 `ashift=12` 是可取的）或 4 KiB 逻辑扇区（此时 `ashift=12` 是必须的）。
* 设置 `-O acltype=posixacl` 可全局启用 POSIX ACL。如果不想启用此选项，可删除它，但随后需要在 `/var/log` 的 `zfs create` 中添加 `-o acltype=posixacl`（注意小写“o”），因为 [journald 需要 ACL](https://askubuntu.com/questions/970886/journalctl-says-failed-to-search-journal-acl-operation-not-supported)。
* 设置 `normalization=formD` 可消除一些与 UTF-8 文件名规范化相关的极端情况。它还隐含 `utf8only=on`，意味着只允许 UTF-8 文件名。如果你希望支持非 UTF-8 文件名，请不要使用此选项。关于强制仅使用 UTF-8 文件名可能存在的问题，请参见 [The problems with enforced UTF-8 only filenames](http://utcc.utoronto.ca/~cks/space/blog/linux/ForcedUTF8Filenames)。
* `recordsize` 未设置（保持默认 128 KiB）。如果想调整（例如 `-O recordsize=1M`），请参见[这些](https://jrs-s.net/2019/04/03/on-zfs-recordsize/) [博客](http://blog.programster.org/zfs-record-size) [文章](https://utcc.utoronto.ca/~cks/space/blog/solaris/ZFSFileRecordsizeGrowth) [帖子](https://utcc.utoronto.ca/~cks/space/blog/solaris/ZFSRecordsizeAndCompression)。
* 设置 `relatime=on` 在经典 POSIX `atime` 行为（性能影响显著）与 `atime=off`（完全禁用 atime 更新来获得最佳性能）之间提供折中。自 Linux 2.6.30 起，`relatime` 成为其他文件系统的默认设置。更多信息请参见 [RedHat 文档](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/6/html/power_management_guide/relatime)。
* 设置 `xattr=sa` [大幅提高扩展属性的性能](https://github.com/zfsonlinux/zfs/commit/82a37189aac955c81a59a5ecc3400475adb56355)。在 ZFS 内部，扩展属性用于实现 POSIX ACL。扩展属性也可被用户空间应用使用，[一些桌面 GUI 应用会使用它们](https://en.wikipedia.org/wiki/Extended_file_attributes#Linux)；[Samba 可使用它们存储 Windows ACL 和 DOS 属性；Samba Active Directory 域控制器需要它们](https://wiki.samba.org/index.php/Setting_up_a_Share_Using_Windows_ACLs)。注意 `xattr=sa` 是 [Linux 特定](https://openzfs.org/wiki/Platform_code_differences) 的。如果将 `xattr=sa` 池迁移到 ZFS-on-Linux 以外的 OpenZFS 实现，扩展属性将无法读取（数据仍可用）。如果扩展属性的可移植性对你重要，请省略上面的 `-O xattr=sa`。即便不希望整个池使用 `xattr=sa`，在 `/var/log` 上使用通常是安全的。
* 确保包括驱动路径的 `-part4` 部分。如果忘记，将指定整个磁盘，ZFS 会重新分区，你将丢失启动器分区。
* ZFS 原生加密 [现](https://github.com/openzfs/zfs/commit/31b160f0a6c673c8f926233af2ed6d5354808393) 默认使用 `aes-256-gcm`。
* 对于 LUKS，选择的密钥大小为 512 位。但 XTS 模式需要两个密钥，因此 LUKS 密钥被一分为二。因此 `-s 512` 即表示 AES-256。
* 你的口令很可能是最薄弱环节。请谨慎选择。参考 [cryptsetup FAQ 第 5 节](https://gitlab.com/cryptsetup/cryptsetup/wikis/FrequentlyAskedQuestions#5-security-aspects) 获取指导。

**提示：**

* 如果你创建镜像拓扑，请使用以下命令创建池：

  ```sh
  zpool create \
      ... \
      rpool mirror \
      /dev/disk/by-id/scsi-SATA_disk1-part4 \
      /dev/disk/by-id/scsi-SATA_disk2-part4
  ```

* 对于 raidz 拓扑，将上面命令中的 `mirror` 替换为 `raidz`、`raidz2` 或 `raidz3`，并列出其他磁盘的分区。
* 使用 LUKS 配合镜像或 raidz 拓扑时，请使用 `/dev/mapper/luks1`、`/dev/mapper/luks2` 等，这些需要通过 `cryptsetup` 创建。
* 可自定义存储池名称。如果更改，新名称必须保持一致。在可以自动安装到 ZFS 的系统中，根池默认命名为 `rpool`。

## 第 3 步：系统安装

1. 创建用于容器的文件系统数据集：

   ```sh
   zfs create -o canmount=off -o mountpoint=none rpool/ROOT
   zfs create -o canmount=off -o mountpoint=none bpool/BOOT
   ```

   在 Solaris 系统中，根文件系统会被克隆，并通过 `pkg image-update` 或 `beadm` 对后缀进行递增以应对重大系统更改。类似功能已在 Ubuntu 20.04 中通过 `zsys` 工具实现，尽管其数据集布局更复杂。即使没有此类工具，仍可手动创建 rpool/ROOT 和 bpool/BOOT 容器的克隆。不过，为简化操作，本教程假设 `/boot` 使用单一文件系统。

2. 为根文件系统和启动文件系统创建数据集：

   ```sh
   zfs create -o canmount=noauto -o mountpoint=/ rpool/ROOT/suse
   zfs mount rpool/ROOT/suse

   zfs create -o mountpoint=/boot bpool/BOOT/suse
   ```

   对于 ZFS，通常不需要使用挂载命令（`mount` 或 `zfs mount`）。此处因 `canmount=noauto` 属于例外情况。

3. 创建其他数据集：

   ```sh
   zfs create                                 rpool/home
   zfs create -o mountpoint=/root             rpool/home/root
   chmod 700 /mnt/root
   zfs create -o canmount=off                 rpool/var
   zfs create -o canmount=off                 rpool/var/lib
   zfs create                                 rpool/var/log
   zfs create                                 rpool/var/spool
   ```

   以下数据集为可选，取决于你的偏好和/或软件选择。
   如果希望这些数据集不被快照：

   ```sh
   zfs create -o com.sun:auto-snapshot=false  rpool/var/cache
   zfs create -o com.sun:auto-snapshot=false  rpool/var/tmp
   chmod 1777 /mnt/var/tmp
   ```

   如果系统使用 `/opt`：

   ```sh
   zfs create                                 rpool/opt
   ```

   如果系统使用 `/srv`：

   ```sh
   zfs create                                 rpool/srv
   ```

   如果系统使用 `/usr/local`：

   ```sh
   zfs create -o canmount=off                 rpool/usr
   zfs create                                 rpool/usr/local
   ```

   如果系统将安装游戏：

   ```sh
   zfs create                                 rpool/var/games
   ```

   如果系统将存储本地邮件在 `/var/mail`：

   ```sh
   zfs create                                 rpool/var/spool/mail
   ```

   如果系统将使用 Snap 包：

   ```sh
   zfs create                                 rpool/var/snap
   ```

   如果系统将使用 Flatpak 包：

   ```sh
   zfs create                                 rpool/var/lib/flatpak
   ```

   如果系统使用 `/var/www`：

   ```sh
   zfs create                                 rpool/var/www
   ```

   如果系统使用 GNOME：

   ```sh
   zfs create                                 rpool/var/lib/AccountsService
   ```

   如果系统使用 Docker（自行管理数据集和快照）：

   ```sh
   zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/docker
   ```

   如果系统使用 NFS（锁定）：

   ```sh
   zfs create -o com.sun:auto-snapshot=false  rpool/var/lib/nfs
   ```

   在 `/run` 挂载 tmpfs：

   ```sh
   mkdir /mnt/run
   mount -t tmpfs tmpfs /mnt/run
   mkdir /mnt/run/lock
   ```

   后续推荐使用 tmpfs，但如果希望为 `/tmp` 创建独立数据集：

   ```sh
   zfs create -o com.sun:auto-snapshot=false  rpool/tmp
   chmod 1777 /mnt/tmp
   ```

   此数据集布局的主要目标是将操作系统与用户数据分离，从而可回滚根文件系统而不影响用户数据。

   如果不做额外操作，`/tmp` 将作为根文件系统的一部分存储。或者，可以如上创建独立的 `/tmp` 数据集，将 `/tmp` 数据排除在根文件系统快照之外。同时，可对 `rpool/tmp` 设置配额以限制最大使用空间。否则，可在后续使用 tmpfs（内存文件系统）。

5. 复制 `zpool.cache`：

   ```sh
   mkdir /mnt/etc/zfs -p
   cp /etc/zfs/zpool.cache /mnt/etc/zfs/
   ```

## 第 4 步：安装系统

1. 将软件源添加到 chroot 目录：

   ```sh
   zypper --root /mnt ar http://download.opensuse.org/tumbleweed/repo/non-oss/ non-oss
   zypper --root /mnt ar http://download.opensuse.org/tumbleweed/repo/oss/ oss
   ```

2. 生成软件源索引：

   ```sh
   zypper --root /mnt refresh
   ```

   你会收到指纹异常提示，输入 `a` 表示始终信任并继续：

   ```sh
   New repository or package signing key received:

   Repository:       oss
   Key Name:         openSUSE Project Signing Key <opensuse@opensuse.org>
   Key Fingerprint:  22C07BA5 34178CD0 2EFE22AA B88B2FD4 3DBDC284
   Key Created:      Mon May  5 11:37:40 2014
   Key Expires:      Thu May  2 11:37:40 2024
   Rpm Name:         gpg-pubkey-3dbdc284-53674dd4

   Do you want to reject the key, trust temporarily, or trust always? [r/t/a/?] (r):
   ```

3. 使用 zypper 安装 openSUSE Tumbleweed：
   如果只安装 base pattern，zypper 会安装 busybox-grep，从而屏蔽默认内核包。因此建议新手安装 enhanced_base pattern。但 enhanced_base 包含的冗余包可能会在服务器环境中带来困扰。你需要根据用途选择：

   1. 使用 zypper 安装 openSUSE Tumbleweed 的基础包（推荐服务器环境）：

      ```sh
      zypper --root /mnt install -t pattern base
      ```

   2. 使用 zypper 安装 openSUSE Tumbleweed 的增强基础包（推荐桌面环境）：

      ```sh
      zypper --root /mnt install -t pattern enhanced_base
      ```

4. 在 chroot 中安装 openSUSE zypper 包管理系统：

   ```sh
   zypper --root /mnt install zypper
   ```

5. 推荐：在 chroot 中安装 openSUSE yast2 系统：

   ```sh
   zypper --root /mnt install yast2
   ```

   >**注意**
   >
   >如果你的 `/etc/resolv.conf` 文件为空，请执行以下命令：
   >
   >```sh
   >echo "nameserver 8.8.4.4" | tee -a /mnt/etc/resolv.conf
   >```

   这将方便初学者配置网络及其他系统设置。

如需安装桌面环境，请参见 [openSUSE wiki](https://en.opensuse.org/openSUSE:Desktop_FAQ#How_to_choose_a_desktop_environment.3F)。

## 第 5 步：系统配置

1. 配置主机名：
   将 `HOSTNAME` 替换为你希望使用的主机名：

   ```sh
   echo HOSTNAME > /mnt/etc/hostname
   vi /mnt/etc/hosts
   ```

   添加一行：

   ```ini
   127.0.1.1       HOSTNAME
   ```

   或者，如果系统在 DNS 中有完整域名：

   ```ini
   127.0.1.1       FQDN HOSTNAME
   ```

   >**提示：**
   >
   >如果觉得 `vi` 难用，可以使用 `nano`。

2. 复制网络信息：

   ```sh
   cp /etc/resolv.conf /mnt/etc
   ```

   将使用 yast2 重新配置网络。

   >**注意**
   >
   >如果你的 `/etc/resolv.conf` 文件为空，请执行以下命令：
   >
   >```sh
   >echo "nameserver 8.8.4.4" | tee -a /mnt/etc/resolv.conf
   >```

3. 将 LiveCD 环境的虚拟文件系统绑定到新系统并进入 chroot：

   ```sh
   mount --make-private --rbind /dev  /mnt/dev
   mount --make-private --rbind /proc /mnt/proc
   mount --make-private --rbind /sys  /mnt/sys
   mount -t tmpfs tmpfs /mnt/run
   mkdir /mnt/run/lock

   chroot /mnt /usr/bin/env DISK=$DISK bash --login
   ```

   >**注意：**
   >
   >这里使用的是 `--rbind` 而非 `--bind`。

4. 配置基本系统环境：

   ```sh
   ln -s /proc/self/mounts /etc/mtab
   zypper refresh
   ```

   即使你偏好非英语系统语言，也要确保 `en_US.UTF-8` 可用：

   ```sh
   locale -a
   ```

   输出中必须包含以下语言：

   * C
   * C.UTF-8
   * en_US.utf8
   * POSIX

   从 `locale -a` 输出中找到所需语言，然后执行：

   ```sh
   localectl set-locale LANG=en_US.UTF-8
   ```

5. 可选：重新安装以增强稳定性：
   安装后可能需要重新安装某些软件包以修复小问题。openSUSE 没有类似 `dpkg-reconfigure` 的命令，可用 `zypper install -f` 作为替代：

   ```sh
   zypper install -f permissions-config iputils ca-certificates ca-certificates-mozilla pam shadow dbus-1 libutempter0 suse-module-tools util-linux
   ```

6. 安装内核：

   ```sh
   zypper install kernel-default kernel-firmware
   ```

   >**注意：**
   >
   >如果安装了 base pattern，需要卸载 busybox-grep 才能安装 kernel-default 包。

7. 在 chroot 环境中为新系统安装 ZFS：

   ```sh
   zypper addrepo https://download.opensuse.org/repositories/filesystems/openSUSE_Tumbleweed/filesystems.repo
   zypper refresh
   zypper install zfs
   ```

   如果系统使用 UEFI 和安全启动，自 Linux 5.4 起，内核要求所有内核模块必须签名。`filesystems` 项目中的 ZFS 内核模块已签名，但不是系统首次启动时自动注册的官方 openSUSE 密钥。为了确保系统信任该签名密钥，请安装：

   ```sh
   zypper install zfs-ueficert
   ```

   下次启动时，MOK 会提示你注册新密钥。

8. 仅对 LUKS 安装：配置 `/etc/crypttab`：

   ```sh
   zypper install cryptsetup

   echo luks1 /dev/disk/by-uuid/$(blkid -s UUID -o value ${DISK}-part4) none \
       luks,discard,initramfs > /etc/crypttab
   ```

   使用 `initramfs` 是为了解决 [cryptsetup 不支持 ZFS](https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1612906) 的问题。

   >**提示：**
   >
   >如果创建 mirror 或 raidz 拓扑，为 `luks2` 等磁盘重复添加 `/etc/crypttab` 条目。

9. 仅对 LUKS 安装：修正 ZFS 的 cryptsetup 命名：

   ```sh
   echo 'ENV{DM_NAME}!="", SYMLINK+="$env{DM_NAME}"
   ENV{DM_NAME}!="", SYMLINK+="dm-name-$env{DM_NAME}"' >> /etc/udev/rules.d/99-local-crypt.rules
   ```

10. 安装 GRUB：
    选择一种启动方式：

    * 安装 GRUB 用于 legacy（BIOS）启动：

      ```sh
      zypper install grub2-i386-pc
      ```

    * 安装 GRUB 用于 UEFI 启动：

      ```sh
      zypper install grub2-x86_64-efi dosfstools os-prober
      mkdosfs -F 32 -s 1 -n EFI ${DISK}-part2
      mkdir /boot/efi
      echo /dev/disk/by-uuid/$(blkid -s PARTUUID -o value ${DISK}-part2) \
          /boot/efi vfat defaults 0 0 >> /etc/fstab
      mount /boot/efi
      ```

      **注意：**

      * 对于 4Kn 驱动器，`-s 1` 是为满足 FAT32 最小簇大小（512 MiB 分区）要求。512 B 扇区的驱动器也可正常使用。
      * 对于 mirror 或 raidz 拓扑，这一步只在第一块磁盘上安装 GRUB，其他磁盘稍后处理。

11. 可选：移除 os-prober：

    ```sh
    zypper remove os-prober
    ```

    仅在双系统环境中需要 os-prober，否则可避免 update-bootloader 报错。

12. 设置 root 密码：

    ```sh
    passwd
    ```

13. 启用 bpool 导入：

    确保 `bpool` 始终被导入，无论 `/etc/zfs/zpool.cache` 是否存在，或 `zfs-import-scan.service` 是否启用。

    ```sh
    vi /etc/systemd/system/zfs-import-bpool.service
    ```

    内容如下：

    ```ini
    [Unit]
    DefaultDependencies=no
    Before=zfs-import-scan.service
    Before=zfs-import-cache.service

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/usr/zpool import -N -o cachefile=none bpool
    # 保持 zpool 缓存的变通方法
    ExecStartPre=-/bin/mv /etc/zfs/zpool.cache /etc/zfs/preboot_zpool.cache
    ExecStartPost=-/bin/mv /etc/zfs/preboot_zpool.cache /etc/zfs/zpool.cache

    [Install]
    WantedBy=zfs-import.target
    ```

    ```sh
    systemctl enable zfs-import-bpool.service
    ```

15. 可选（但推荐）：将 `/tmp` 挂载为 tmpfs

    如果之前创建了 `/tmp` 数据集，则跳过此步，否则可以通过启用 `tmp.mount` 单元将 `/tmp` 放在 tmpfs（内存文件系统）上：

    ```sh
    cp /usr/share/systemd/tmp.mount /etc/systemd/system/
    systemctl enable tmp.mount
    ```

---

## 第 6 步：内核安装

1. 将 zfs 模块添加到 dracut：

   ```sh
   echo 'zfs'>> /etc/modules-load.d/zfs.conf
   ```

2. 刷新内核文件：

   ```sh
   kernel-install $(uname -r) /boot/vmlinuz-$(uname -r)
   ```

3. 刷新 initrd 文件：

   ```sh
   mkinitrd
   ```

   >**注意：**
   >
   >在某些安装中，LUKS 分区可能无法被 dracut 识别，会出现报错 “Failure occurred during following action: configuring encrypted DM device X VOLUME_CRYPTSETUP_FAILED” 。
   解决方法：检查 cryptsetup 安装情况。[详细信息](https://forums.opensuse.org/showthread.php/528938-installation-with-LUKS-cryptsetup-installer-gives-error-code-3034?p=2850404#post2850404)

   >**注意：**
   >
   >即使已将 zfs 配置添加到系统模块 `/etc/modules.d`，若 dracut 未识别，仍需强制添加：

   ```sh
   dracut --kver $(uname -r) --force --add-drivers "zfs"
   ```

## 第 7 步：安装 Grub2

1. 验证 ZFS 启动文件系统是否被识别：

   ```sh
   grub2-probe /boot
   ```

   输出必须为 `zfs`。

2. 如果 `grub2-probe` 命令出现问题，可执行：

   ```sh
   echo 'export ZPOOL_VDEV_NAME_PATH=YES' >> /etc/profile
   export ZPOOL_VDEV_NAME_PATH=YES
   ```

   然后返回执行 `grub2-probe` 步骤。


3. 解决 GRUB 缺少 zpool-features 支持的方法：

   ```sh
   vi /etc/default/grub
   # 设置：GRUB_CMDLINE_LINUX="root=ZFS=rpool/ROOT/suse"
   ```

5. 可选（但强烈建议）：便于调试 GRUB：

   ```sh
   vi /etc/default/grub
   ```

   * 删除 `GRUB_CMDLINE_LINUX_DEFAULT` 中的 `quiet`
   * 取消注释：`GRUB_TERMINAL=console`
   * 保存并退出

   系统重启两次并确认一切正常后，可根据需要恢复这些更改。

6. 更新启动配置：

   ```sh
   update-bootloader
   ```

   >**注意：**
   >
   >如果出现 `os-prober` 错误可忽略。

   >**注意：**
   >
   >如果安装 grub2 时出现问题，可考虑使用 systemd-boot。

   >**注意：**
   >
   >如果命令无输出，可使用经典的 `grub.cfg` 生成：
   >
   >```sh
   >grub2-mkconfig -o /boot/grub2/grub.cfg
   >```

7. 安装启动加载器：

   1. 对于 legacy（BIOS）启动，将 GRUB 安装到 MBR：

      ```sh
      grub2-install $DISK
      ```

      >**注意**
      >
      >这里是将 GRUB 安装到整个磁盘，而非单个分区。

      如果创建了 mirror 或 raidz 拓扑，需要对池中每块磁盘重复执行该命令。

8. 对于 UEFI 启动，将 GRUB 安装到 ESP 分区：

      ```sh
      grub2-install --target=x86_64-efi --efi-directory=/boot/efi \
          --bootloader-id=opensuse --recheck --no-floppy
      ```

      不需要指定磁盘。如果创建了 mirror 或 raidz 拓扑，额外磁盘稍后处理。

## 第 8 步：Systemd-Boot 安装

>**警告：**
>
>这将破坏你的 Yast2 启动加载器配置。仅在无法通过 grub2 修复问题时才使用此方法。本步骤是为某些情况下 grub2 无法识别 rpool 池而提供的替代方案。

1. 安装 systemd-boot：

   ```sh
   bootctl install
   ```

2. 配置启动加载器：

   ```sh
   tee -a /boot/efi/loader/loader.conf << EOF
   default openSUSE_Tumbleweed.conf
   timeout 5
   console-mode auto
   EOF
   ```

3. 创建启动项：

   ```sh
   tee -a /boot/efi/loader/entries/openSUSE_Tumbleweed.conf << EOF
   title   openSUSE Tumbleweed
   linux   /EFI/openSUSE/vmlinuz
   initrd  /EFI/openSUSE/initrd
   options root=zfs=rpool/ROOT/suse boot=zfs
   EOF
   ```

4. 复制内核和 initrd 文件到 EFI 分区：

   ```sh
   mkdir /boot/efi/EFI/openSUSE
   cp /boot/{vmlinuz,initrd} /boot/efi/EFI/openSUSE
   ```

5. 更新 systemd-boot 变量：

   ```sh
   bootctl update
   ```


## 第 9 步：文件系统配置

1. 修复文件系统挂载顺序：

   激活 `zfs-mount-generator`，让 systemd 识别各个挂载点，这对 `/var/log`、`/var/tmp` 等目录至关重要。`rsyslog.service` 会依赖 `var-log.mount`，使用 systemd `PrivateTmp` 特性的服务会自动依赖 `var-tmp.mount`。

   ```sh
   mkdir /etc/zfs/zfs-list.cache
   touch /etc/zfs/zfs-list.cache/bpool
   touch /etc/zfs/zfs-list.cache/rpool
   ln -s /usr/lib/zfs/zed.d/history_event-zfs-list-cacher.sh /etc/zfs/zed.d
   zed -F &
   ```

3. 验证 `zed` 是否更新了缓存，确保以下文件非空：

   ```sh
   cat /etc/zfs/zfs-list.cache/bpool
   cat /etc/zfs/zfs-list.cache/rpool
   ```

4. 如果文件为空，强制更新缓存并重新检查：

   ```sh
   zfs set canmount=on     bpool/BOOT/suse
   zfs set canmount=noauto rpool/ROOT/suse
   ```

   如果仍为空，先停止 `zed`：

   ```sh
   fg
   Ctrl-C
   ```

   然后重新启动 `zed` 并重试。

5. 修正缓存路径，去掉前缀 `/mnt`：

   ```sh
   sed -Ei "s|/mnt/?|/|" /etc/zfs/zfs-list.cache/*
   ```

## 第 10 步：首次启动

1. 可选：安装 SSH 服务：

   ```sh
   zypper install --yes openssh-server

   vi /etc/ssh/sshd_config
   # 设置：PermitRootLogin yes
   ```

2. 可选：对初始安装创建快照：

   ```sh
   zfs snapshot bpool/BOOT/suse@install
   zfs snapshot rpool/ROOT/suse@install
   ```

   以后在每次升级前，你可能希望先创建快照，并在适当的时候删除旧快照（包括这个初始快照）以节省空间。

3. 退出 `chroot` 环境，返回 LiveCD 环境：

   ```sh
   exit
   ```

4. 在 LiveCD 环境中执行以下命令卸载所有文件系统：

   ```sh
   mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | \
       xargs -i{} umount -lf {}
   zpool export -a
   ```

5. 重启系统：

   ```sh
   reboot
   ```

   等待新安装的系统正常启动，并以 root 登录。

6. 创建用户账户：
   将 `用户名` 替换为你希望的用户名：

   ```sh
   zfs create rpool/home/用户名
   adduser 用户名

   cp -a /etc/skel/. /home/用户名
   chown -R 用户名:用户名 /home/用户名
   usermod -a -G audio,cdrom,dip,floppy,netdev,plugdev,sudo,video 用户名
   ```

7. 镜像安装 GRUB（多磁盘安装时）：

   如果系统安装在多个磁盘上，需要在其他磁盘上重复安装 GRUB。

   * 对于 legacy（BIOS）启动：先确认当前是否为 EFI 模式：

     ```sh
     efibootmgr -v
     ```

     输出必须包含 `legacy_boot`。然后重新配置 GRUB：

     ```sh
     grub-install $DISK
     ```

     按回车直到出现设备选择界面，使用空格键选择池中的所有磁盘（不是分区）。

   * 对于 UEFI 启动：

     ```sh
     umount /boot/efi
     ```

     对第二块及后续磁盘（将 debian-2 改为 -3 等）：

     ```sh
     dd if=/dev/disk/by-id/scsi-SATA_disk1-part2 \
        of=/dev/disk/by-id/scsi-SATA_disk2-part2
     efibootmgr -c -g -d /dev/disk/by-id/scsi-SATA_disk2 \
         -p 2 -L "opensuse-2" -l '\EFI\opensuse\grubx64.efi'

     mount /boot/efi
     ```

## 第 11 步（可选）：配置 Swap

>**注意**：
>
>在内存压力极高的系统上，使用 zvol 作为 swap 设备可能导致系统锁死，无论 swap 空间剩余多少。[上游已有相关 bug 报告](https://github.com/zfsonlinux/zfs/issues/7734)。

1. 创建用于 swap 的 zvol（卷数据集）：

   ```sh
   zfs create -V 4G -b $(getconf PAGESIZE) -o compression=zle \
       -o logbias=throughput -o sync=always \
       -o primarycache=metadata -o secondarycache=none \
       -o com.sun:auto-snapshot=false rpool/swap
   ```

   你可以根据需求调整大小（这里为 `4G`）。

   压缩算法使用 `zle`，因为这是开销最小的算法。由于本指南推荐 `ashift=12`（磁盘上 4 KiB 块），4 KiB 页面大小情况下，没有压缩算法能减少 I/O。唯一例外是全零页面，会被 ZFS 丢弃，但必须启用某种压缩才能实现这一行为。

3. 配置 swap 设备：

   >**注意**：
   >
   >在配置文件中始终使用完整 `/dev/zvol` 别名，切勿使用短设备名 `/dev/zdX`。

   ```sh
   mkswap -f /dev/zvol/rpool/swap
   echo /dev/zvol/rpool/swap none swap discard 0 0 >> /etc/fstab
   echo RESUME=none > /etc/initramfs-tools/conf.d/resume
   ```

   `RESUME=none` 用于禁用休眠恢复。由于 zvol 在启动时尚未导入（池未导入），恢复脚本无法找到 swap，如果不禁用，启动过程会停滞约 30 秒等待 swap zvol 出现。

5. 启用 swap 设备：

   ```sh
   swapon -av
   ```

## 第 12 步：最终清理

1. 等待系统正常启动，使用你创建的用户账号登录。确保系统（包括网络）工作正常。

2. 可选：删除初始安装的快照：

   ```sh
   sudo zfs destroy bpool/BOOT/suse@install
   sudo zfs destroy rpool/ROOT/suse@install
   ```

3. 可选：禁用 root 密码：

   ```sh
   sudo usermod -p '*' root
   ```

4. 可选（强烈建议）：禁用 root SSH 登录：

   如果之前安装过 SSH，请撤销临时修改：

   ```sh
   vi /etc/ssh/sshd_config
   # 删除：PermitRootLogin yes

   systemctl restart sshd
   ```

6. 可选：重新启用图形启动过程：

   如果你希望使用图形启动，并且使用了 LUKS，这可以让提示界面更美观。

   ```sh
   sudo vi /etc/default/grub
   # 在 GRUB_CMDLINE_LINUX_DEFAULT 中添加 quiet
   # 注释掉 GRUB_TERMINAL=console
   # 保存并退出

   sudo update-bootloader
   ```

   >**注意**：
   >
   >如果出现 `osprober` 错误，可忽略。

8. 可选：仅针对 LUKS 安装，备份 LUKS 头：

   ```sh
   sudo cryptsetup luksHeaderBackup /dev/disk/by-id/scsi-SATA_disk1-part4 \
       --header-backup-file luks1-header.dat
   ```

   将备份妥善保存（如云端存储）。该备份受 LUKS 密码保护，但你也可选择额外加密。
  
   >**提示**：
   >
   >如果创建了镜像或 raidz 拓扑，请对每个 LUKS 卷重复此操作（如 `luks2` 等）。

## 故障排除

### 使用 Live CD 进行救援

请参考 [第 1 步：准备安装环境](https://openzfs.github.io/openzfs-docs/Getting%20Started/openSUSE/openSUSE%20Leap%20Root%20on%20ZFS.html#step-1-prepare-the-install-environment)。

对于 LUKS 安装，首先解锁磁盘：

```sh
zypper install cryptsetup
cryptsetup luksOpen /dev/disk/by-id/scsi-SATA_disk1-part4 luks1
# 如果是镜像或 raidz 拓扑，请对其他磁盘重复操作。
```

正确挂载所有文件系统：

```sh
zpool export -a
zpool import -N -R /mnt rpool
zpool import -N -R /mnt bpool
zfs load-key -a
zfs mount rpool/ROOT/suse
zfs mount -a
```

如有需要，可以进入已安装的系统环境进行 chroot：

```sh
mount --make-private --rbind /dev  /mnt/dev
mount --make-private --rbind /proc /mnt/proc
mount --make-private --rbind /sys  /mnt/sys
chroot /mnt /bin/bash --login
mount /boot/efi
mount -a
```

进行必要的修复操作。

完成后，进行清理：

```sh
exit
mount | grep -v zfs | tac | awk '/\/mnt/ {print $3}' | \
    xargs -i{} umount -lf {}
zpool export -a
reboot
```

### Areca

需要 `arcsas` blob 驱动的系统应将其添加到 `/etc/initramfs-tools/modules` 文件中，然后运行：

```sh
update-initramfs -c -k all
```

如果内核日志中出现类似以下信息：

```sh
RIP: 0010:[<ffffffff8101b316>]  [<ffffffff8101b316>] native_read_tsc+0x6/0x20
```

请升级或降级 Areca 驱动。在出现此错误的系统上 ZoL 将不稳定。

### MPT2SAS

本教程中大多数问题报告都涉及 `mpt2sas` 硬件，这类硬件会延迟异步初始化驱动器，例如某些 IBM M1015 或已刷回参考 LSI 固件的 OEM 卡。

基本问题是，这些控制器上的磁盘在 Linux 内核启动时不可见，而 ZoL 不支持热插拔池成员。详见：[https://github.com/zfsonlinux/zfs/issues/330](https://github.com/zfsonlinux/zfs/issues/330)。

大多数 LSI 卡完全兼容 ZoL。如果你的卡存在此问题，可在 `/etc/default/zfs` 中设置：

```ini
ZFS_INITRD_PRE_MOUNTROOT_SLEEP=X
```

系统将在导入池之前等待 X 秒，确保所有磁盘都已出现。


### QEMU/KVM/XEN

为每个虚拟磁盘设置唯一序列号（使用 libvirt 或 qemu，例如：`-drive if=none,id=disk1,file=disk1.qcow2,serial=1234567890`）。

要在虚拟机中使用 UEFI（而不仅仅是 BIOS 启动），请在宿主机上执行：

```sh
sudo zypper install ovmf
sudo vi /etc/libvirt/qemu.conf
```

取消注释以下行：

```ini
nvram = [
   "/usr/share/OVMF/OVMF_CODE.fd:/usr/share/OVMF/OVMF_VARS.fd",
   "/usr/share/OVMF/OVMF_CODE.secboot.fd:/usr/share/OVMF/OVMF_VARS.fd",
   "/usr/share/AAVMF/AAVMF_CODE.fd:/usr/share/AAVMF/AAVMF_VARS.fd",
   "/usr/share/AAVMF/AAVMF32_CODE.fd:/usr/share/AAVMF/AAVMF32_VARS.fd"
]
```

重启 libvirt 服务：

```sh
sudo systemctl restart libvirtd.service
```

### VMware

* 在虚拟机的 `.vmx` 文件或 vSphere 配置中设置：

```ini
disk.EnableUUID = "TRUE"
```

这样可以确保在客机中创建别名 `/dev/disk`。


### 外部链接

* [OpenZFS 在 openSUSE 上](https://en.opensuse.org/OpenZFS)
* [ZenLinux 博客 - 如何设置 openSUSE chroot](https://blog.zenlinux.com/2011/02/how-to-setup-an-opensuse-chroot/comment-page-1/)
