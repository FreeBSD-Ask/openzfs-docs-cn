# 在 Gentoo 中启用 ZFS 支持

- 原文地址：[ZFS](https://wiki.gentoo.org/wiki/ZFS)，此页面最后编辑于 2025 年 11 月 6 日 (星期四) 20:52。


**ZFS** 是一种由 Matthew Ahrens 和 Jeff Bonwick 创建的下一代 [文件系统](https://wiki.gentoo.org/wiki/Filesystem)。它围绕着几个核心理念进行设计：

- 存储管理应当是简单的。
- 冗余应当由文件系统处理。
- 在文件系统进行修复时不应被下线。
- 在代码发布之前，对最坏情况进行自动化模拟是重要的。
- 数据完整性至关重要。

ZFS 的开发始于 2001 年的 Sun Microsystems。2005 年，作为 OpenSolaris 的一部分，ZFS 在 [CDDL](https://opensource.org/licenses/CDDL-1.0) 许可下发布。2007 年，Pawel Jakub Dawidek 将 ZFS 移植到了 FreeBSD。2008 年，LLNL 的 Brian Behlendorf 启动了 ZFSOnLinux 项目，将 ZFS 移植到 Linux，用于高性能计算。2010 年，Oracle 收购了 Sun Microsystems，并在当年晚些时候终止了 OpenSolaris。

Illumos 项目启动了，旨在取代 OpenSolaris。大约三分之二的 ZFS 核心团队成员辞职了，其中就有 Matthew Ahrens 和 Jeff Bonwick。许多人加入了后续开发 OpenZFS 的团队，最初是作为 Illumos 项目的一部分。Oracle 内部未辞职的 1/3 ZFS 核心团队则继续在 Oracle Solaris 中开发不兼容的专有 ZFS 分支。

Solaris 的首个版本包含了一些在大规模辞职之前就已在开发中的创新改动。Solaris 的后续版本所包含的改动则更少，且英雄迟暮。如今，一个不断壮大的社区在多个平台上持续开发 OpenZFS，如 FreeBSD、Illumos、Linux 和 Mac OS X。

>**注意**
>
>
>Gentoo 的 ZFS 维护者不建议用户在 PORTAGE_TMPDIR 上使用 ZFS（或任何其他较为特殊的文件系统），因为 Portage 通常会出现 Bug。但截至 2022 年 5 月，在 ZFS 上的使用应当是没有问题的。

## 特性

可以在这篇 [单独的文章](https://wiki.gentoo.org/wiki/ZFS/Features) 中找到详细的特性列表。

## 安装

### 模块

有来自 [ZFSOnLinux Project](https://zfsonlinux.org/) 的 Linux 树外内核模块可用。

自 0.6.1 版本起，OpenZFS 项目认为 ZFS 已经“准备好在从桌面到超级计算机的一切环境中进行大规模部署”，并且在大规模部署场景下是稳定的。

>**注意**
>
>所有对 git 仓库进行的更改都会由 [LLNL](https://www.llnl.gov/) 进行回归测试。

### USE 标志

ZFS 的 Linux 内核模块与用户态工具

Linux 内核模块及 ZFS 用户空间工具的可选功能：

|USE 标志 | 说明|
| --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| [`+dist-kernel-cap`](https://packages.gentoo.org/useflags/+dist-kernel-cap) | 在与 USE=dist-kernel 结合时，可防止升级到未受支持的内核版本                                                                                               |
| [`+initramfs`](https://packages.gentoo.org/useflags/+initramfs)             | 在 initramfs 中内置内核模块，并重新安装内核（仅对发行版内核有效）                                                                                             |
| [`+modules`](https://packages.gentoo.org/useflags/+modules)                 | 编译内核模块                                                                                                                             |
| [`+rootfs`](https://packages.gentoo.org/useflags/+rootfs)                   | 启用从包含根文件系统的 zpool 启动所需的依赖                                                                                                          |
| [`+strip`](https://packages.gentoo.org/useflags/+strip)                     | 允许 ebuild 对特定文件执行符号剥离                                                                                                              |
| [`custom-cflags`](https://packages.gentoo.org/useflags/custom-cflags)       | 使用用户指定的 CFLAGS 编译（不受支持）                                                                                                            |
| [`debug`](https://packages.gentoo.org/useflags/debug)                       | 启用额外的调试代码路径，如断言和额外输出。如需获得有意义的回溯信息，请参见 [Gentoo Wiki: Backtraces](https://wiki.gentoo.org/wiki/Project:Quality_Assurance/Backtraces) |
| [`dist-kernel`](https://packages.gentoo.org/useflags/dist-kernel)           | 启用发行版内核升级时的子槽重建                                                                                                                    |
| [`kernel-builtin`](https://packages.gentoo.org/useflags/kernel-builtin)     | 禁用对 sys-fs/zfs-kmod 的依赖，假设 ZFS 已包含在内核源码树中                                                                                          |
| [`minimal`](https://packages.gentoo.org/useflags/minimal)                   | 不安装 Python 脚本（如 arcstat、dbufstat 等）并避免依赖 dev-lang/python                                                                           |
| [`modules-compress`](https://packages.gentoo.org/useflags/modules-compress) | 安装压缩的内核模块（如果内核配置启用模块压缩）                                                                                                            |
| [`modules-sign`](https://packages.gentoo.org/useflags/modules-sign)         | 对已安装的内核模块进行加密签名（要求内核中 CONFIG_MODULE_SIG=y）                                                                                         |
| [`nls`](https://packages.gentoo.org/useflags/nls)                           | 添加本地语言支持（使用 gettext - GNU locale 工具）                                                                                               |
| [`pam`](https://packages.gentoo.org/useflags/pam)                           | 安装 zfs_key PAM 模块，用于自动加载 `home` 数据集的 ZFS 加密密钥                                                                                            |
| [`python`](https://packages.gentoo.org/useflags/python)                     | 添加对 Python 语言的可选支持/绑定                                                                                                              |
| [`selinux`](https://packages.gentoo.org/useflags/selinux)                   | **仅内部使用**，支持 Security Enhanced Linux，必须由 selinux 配置文件设置，否则会导致破坏                                                                   |
| [`split-usr`](https://packages.gentoo.org/useflags/split-usr)               | 启用支持将 `/bin`、`/lib*`、`/sbin` 和 `/usr/sbin` 与 `/usr/bin` 和 `/usr/lib*` 分开维护的行为                                                                  |
| [`test-suite`](https://packages.gentoo.org/useflags/test-suite)             | 安装回归测试套件                                                                                                                           |
| [`unwind`](https://packages.gentoo.org/useflags/unwind)                     | 添加调用栈展开和函数名解析支持                                                                                                                    |
| [`verify-sig`](https://packages.gentoo.org/useflags/verify-sig)             | 对 distfiles 验证上游签名                                                                                                                  |


### Emerge

要安装 ZFS，运行：

```sh
emerge --ask sys-fs/zfs
```

>**重要**
>
>每次重新编译内核后，都需要重新编译 sys-fs/zfs-kmod，即使内核的改动非常小，亦如此。在合并内核模块之后重新编译内核时，用户可能会遇到 ZFS 存储池进入不可中断睡眠状态（无法杀死的进程）或在执行时崩溃的问题。还可以配合 [Distribution Kernel](https://wiki.gentoo.org/wiki/Project:Distribution_Kernel#Trying_it_out "Project:Distribution Kernel") 设置 `USE=dist-kernel`。
>
>```sh
>emerge -va @module-rebuild
>```

### ZFS 事件守护进程通知

ZED（ZFS Event Daemon）用于监控由 ZFS 内核模块生成的事件。当一个 zevent（ZFS Event）被触发时，ZED 会运行为对应 zevent 类别启用的 ZEDLETs（ZFS Event Daemon Linkage for Executable Tasks, ZFS 事件守护进程可执行任务关联）。

文件 **/etc/zfs/zed.d/zed.rc**

```ini
##
# 用于接收通知的 zpool 管理员电子邮件地址；
#   多个地址以空白字符分隔。
# 只有在定义了 ZED_EMAIL_ADDR 时才会发送邮件。
# 默认启用；如需禁用请注释。
#
ZED_EMAIL_ADDR="admin@example.com"

##
# 通知详细级别。
#   如果设置为 0，在池状态健康时禁用通知。
#   如果设置为 1，无论池状态是否健康都发送通知。
#
ZED_NOTIFY_VERBOSE=1
```

### OpenRC

将 zfs 脚本加入运行级别，以便在启动时初始化：

```sh
rc-update add zfs-import boot
rc-update add zfs-mount boot
rc-update add zfs-load-key boot
rc-update add zfs-share default
rc-update add zfs-zed default
```


>**注意**
>
>对大多数配置来说，只需要前两行命令。zfs-load-key 用于 ZFS 加密。zfs-share 适用于使用 NFS 共享的用户，而 zfs-zed 用于 ZFS 事件守护进程，负责通过热备盘处理磁盘更换以及通过电子邮件发送故障通知。

>**注意**
>
>
>若要将 ZFS 用作根文件系统，以及使用 ZFS swap，请将 zfs-import 和 zfs-mount 添加到 sysinit 运行级别，以便在启动或关机过程中访问 文件系统。

### systemd

启用服务，使其在启动时自动运行：

```sh
systemctl enable zfs.target
```

手动启动守护进程：

```sh
systemctl start zfs.target
```

为了在启动时自动挂载 ZFS 存储池，需要启用以下服务和目标：

```sh
systemctl enable zfs-import-cache
systemctl enable zfs-mount
systemctl enable zfs-import.target
```

## 内核

sys-fs/zfs 需要内核支持 Zlib（模块或内建）。

### 内置

```sh
Cryptographic API --->
  Compression --->
    <*> Deflate
```

### 模块

>**注意**
>
>
>每当内核发生变化时，都必须重新构建内核模块。

>**注意**
>
>
>在安装内核模块时，必须始终选择稳定版本。你可以在 [这里](https://github.com/openzfs/zfs/releases) 查看最新的稳定版本及其对应的内核版本，同时也应确认 Portage 是否提供了该特定的 [内核版本](https://packages.gentoo.org/packages/sys-kernel/gentoo-sources)。

你还应当在 package.mask 目录中添加一些文件，用于屏蔽特定版本的 zfs-kmod 和 zfs。这可以避免拉取这两个包的不同版本。此外，sys-fs/zfs 的版本也必须与 zfs-kmod 的版本保持一致。

如果使用的是由 dracut 或 genkernel 生成的 initramfs，请在（重新）编译模块后重新生成 initramfs。如果你使用的是自定义 initramfs，请参见下一节。

#### 自定义 INITRAMFS

>**注意**
>
>
>本节不适用于 dracut、ugrd 或 genkernel 用户。

>**注意**
>
>每次升级到新内核时，都必须在 initramfs 目录中为其创建一个对应的文件夹。

```sh
mkdir -vp /usr/src/initramfs/lib/modules/$(uname -r)
```

复制二进制文件，以便在 init 中可以使用 modprobe：

```
cp -Prv /lib/modules/$(uname -r)/extra/* /usr/src/initramfs/lib/modules/$(uname -r)/extra/
```

你还需要以下这些库文件，系统才能正确启动：

```sh
lddtree --copy-to-tree /usr/src/initramfs /sbin/zfs
lddtree --copy-to-tree /usr/src/initramfs /sbin/zpool
lddtree --copy-to-tree /usr/src/initramfs /sbin/zed
lddtree --copy-to-tree /usr/src/initramfs /sbin/zgenhostid
lddtree --copy-to-tree /usr/src/initramfs /sbin/zvol_wait
```

>**注意**
>
>如果 modules 目录中存在多个内核文件夹，可以在 find 命令中使用 `-not -path` 来排除特定文件夹。

以下示例，演示为 6.6.2 创建 initramfs，并排除 6.1.118：

```sh
cd /usr/src/initramfs
find . -not -path "./lib/modules/6.1.118/*" -not -path "./lib/modules/6.1.118" -print0 | cpio --null --create --verbose --format=newc | gzip --best > gzip -9 > /boot/initramfs-custom.img
```

现在 initramfs 已创建完成，接下来请更新你的引导加载程序。

## 高级

关于改进 ZFS 在一些边缘场景下需求的高级技巧合集，请参阅以下子文章：

[ZFS/Advanced](https://wiki.gentoo.org/wiki/ZFS/Advanced)

## 使用

ZFS 已经内置了管理硬件和文件系统所需的一切程序，无需任何其他工具。

### 准备

ZFS 支持使用块设备或文件。两种情况下的管理方式是相同的，但在生产环境中，ZFS 开发者建议使用块设备（最好是整块磁盘）。在试验本文所述的各种命令时，用户可以选择最方便的方式。

>**重要**
>
>为了充分利用高级格式化磁盘上的块设备（即具有 4K 扇区的驱动器），强烈建议用户在创建池之前阅读 [ZFS on Linux FAQ](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ.html#advanced-format-disks)。

ZFS 存储池（或 zpool）是由一到多个虚拟设备（vdev）聚合而成的，而每个 vdev 又由一个或多个底层物理设备按特定几何结构组合而成。以下是三条非常重要的规则：

1. ZFS 存储池会跨 vdev 进行条带化，只要其中某个 vdev 不可用，整个 ZFS 存储池也将不可用
2. 只要创建了 vdev，其几何结构就被固定，无法修改。重新配置 vdev 的唯一方式是销毁并重新创建
3. 要修复受损的 ZFS 存储池，每个底层 vdev 都必须具备某种程度的冗余

#### 硬件考量

- ZFS 需要 **直接** 看到并控制支撑 zpool 的物理设备（它有自己的 I/O 调度器）。强烈不建议使用硬 RAID，即使是多个单盘 RAID-0 虚拟磁盘，因为这种方式会削弱 ZFS 带来的优势。应始终使用 JBOD。有些控制器提供相关功能，而另一些（如较老的 LSI HBA）则需要刷入特定固件（在 LSI 的情况下称为“IT 模式固件”）才能实现 JBOD。不幸的是，有些 RAID 控制器只提供 RAID 级别而没有其他选择，这类控制器并不适合 ZFS。
- ZFS 可能具有极高的 I/O 强度：
  - 在 NAS 设备中，非常流行的方案是使用二手 SAS HBA 连接多块 SATA 机械硬盘（在更大规模下，推荐使用近线 SATA 硬盘）
  - 如果 ZFS 存储池使用 NVMe 模块创建，**请确保这些模块不是无 DRAM 的**（请查看数据手册）。原因有二：既可以避免明显的瓶颈，也可以避免硬件崩溃，因为某些无 DRAM 模块在 I/O 请求过载时容易卡死 <https://wiki.gentoo.org/wiki/ZFS#cite_note-1>
  - 不要在 ZFS 存储池中使用所谓的 SMR（Shingled Magnetic Drives, 叠瓦式磁记录）磁盘，这类磁盘写入速度极慢，并且在 ZFS 存储池 resilver 过程中可能发生超时，从而妨碍恢复。**应始终在 ZFS 中使用 CMR（传统磁记录）磁盘。**
- 除非存储由不间断电源（UPS）保护或电力来源极其可靠，否则应考虑使用具备掉电保护的 NVMe/SSD（即带有板载电容）
- 应避免使用 SATA 端口倍增器，除非没有其他选择，因为它会在已连接的磁盘之间复用流量，造成严重瓶颈，实际上会分割可用带宽，同时也会增加 I/O 延迟
- ZFS 能够利用 X86/64 处理器中的 SSE/AVX 向量化指令来加速校验和计算，并会自动选择最快的实现。在 Linux 下，可以在 `/proc/spl/kstat/zfs/fletcher_4_bench` 和 `vdev_raidz_bench` 中查看微基准测试结果。例如：

```sh
cat /proc/spl/kstat/zfs/fletcher_4_bench
```

#### 冗余方面的考量

>**重要**
>
>虽然一个 ZFS 存储池可以包含多个几何结构和容量各不相同的 vdev，但在同一个 vdev 内，所有驱动器必须是同一类型并且具有相同的特性，尤其是相同的容量和相同的扇区大小。不建议在同一个 vdev 中混合使用 SSD 和“老旧”机械硬盘，因为性能差异会带来问题。

与 RAID 类似，ZFS 提供了多种方式来创建具有（或不具有）冗余的 vdev，具体包括：

- striped 条带化（“RAID-0”）：速度最快的方案，但未提供任何磁盘损坏保护。如果一块磁盘损坏，不仅该 vdev 会失效，整个 zpool 也会失效（请记住：zpool 本质上始终是条带化的）。
- mirror 镜像（“RAID-1”）：一块磁盘是另一块的镜像。通常使用两块磁盘，但也可以使用三重（或更多）镜像，不过会牺牲空间利用效率。可容忍一块磁盘损坏（三重镜像则可容忍两块）。
- raidz1，或称 raidz（“RAID-5”）：使用单一校验并在 vdev 内分布，因此只能容忍一块磁盘损坏。vdev 的总容量等于所有单块磁盘容量之和（减去一块磁盘的容量）。
- raidz2（“RAID-6”）：与 raidz1 相同的概念，但使用两个校验。vdev 的总容量等于所有单块磁盘容量之和（减去两块磁盘的容量）。可容忍两块磁盘损坏。
- raidz3：与 raidz1 相同的概念，但使用三个校验。vdev 的总容量等于所有单块磁盘容量之和（减去三块磁盘的容量）。可容忍三块磁盘损坏，适用于对数据安全性要求极高的场景。

#### 准备存储池

>**提示**
>
>推荐使用物理设备来使用 ZFS。对于“空白”设备，并不需要进行分区，ZFS 会自动进行处理。

>**警告**
>
>
>作为后续说明的一种替代方案，如果没有可用的物理设备，也可以使用位于现有文件系统之上的文件。这种方式仅适合用于实验，**绝不能在生产系统中使用**。

以下命令会在 `/var/lib/zfs_img` 中创建四个 2GB 的稀疏镜像文件，用作硬盘。它们最多会占用 8GB 的磁盘空间，但在实际使用中，由于只有写入的区域才会被分配，因此占用空间会很小：

```sh
mkdir /var/lib/zfs_img
truncate -s 2G /var/lib/zfs_img/zfs0.img
truncate -s 2G /var/lib/zfs_img/zfs1.img
truncate -s 2G /var/lib/zfs_img/zfs2.img
truncate -s 2G /var/lib/zfs_img/zfs3.img
```

>**注意**
>
>在导出池之后，所有这些文件都会被释放，并且 `/var/lib/zfs_img` 目录可以被删除。

如果使用 ramdisk 更为方便，上述操作的等效方式如下：

```sh
modprobe brd rd_nr=4 rd_size=1953125
ls -l /dev/ram*
```

这种方案需要在 Linux 内核配置中启用 `CONFIG_BLK_DEV_RAM=m`。作为最后的手段，可以使用回环设备并结合存放在 tmpfs 文件系统中的文件。第一步是创建用于存放原始镜像文件的 tmpfs：

```sh
mkdir /var/lib/zfs_img
```

然后创建原始镜像文件：

```sh
dd if=/dev/null of=/var/lib/zfs0.img bs=1024 count=2097153 seek=2097152
dd if=/dev/null of=/var/lib/zfs1.img bs=1024 count=2097153 seek=2097152
dd if=/dev/null of=/var/lib/zfs2.img bs=1024 count=2097153 seek=2097152
dd if=/dev/null of=/var/lib/zfs3.img bs=1024 count=2097153 seek=2097152
```

接着为上面创建的每个文件都分配一个回环设备：

```sh
losetup /dev/loop0 /var/lib/zfs_img/zfs0.img
losetup /dev/loop1 /var/lib/zfs_img/zfs1.img
losetup /dev/loop2 /var/lib/zfs_img/zfs2.img
losetup /dev/loop3 /var/lib/zfs_img/zfs3.img
losetup -a
```

### ZFS 存储池

每个 ZFS 的使用场景都始于程序 `/usr/sbin/zpool`，它用于创建和调整 ZFS 存储池（zpool）。zpool 是一种逻辑存储空间，用于将一到多个 vdev 组合在一起。该逻辑存储空间可以同时拥有以下两种内容：

- 数据集：一组文件和目录，可挂载到 VFS 中，就像 xfs 或 ext4 这样的传统文件系统一样
- zvolumes（或 zvols）：虚拟卷，可以作为虚拟块设备访问，像机器上的任何物理硬盘一样使用，位于 `/dev` 下

在创建了 zpool 后，就可以对其中不同的 zvolumes 和数据集创建时间点快照（snapshots）。这些快照可以被浏览，甚至可以回滚，用于将内容恢复到过去的某个时间点。ZFS 的另一个重要理念是：可以通过一系列属性来管理 zpool、数据集和 zvolume，例如加密、数据压缩、使用配额等，这些都只是属性可调内容的示例。

切记：zpool 是在其 vdev 之间进行条带化的，因此哪怕只丢失一个 vdev，也意味着整个 ZFS 存储池的丢失。冗余发生在 vdev 层面，而不是 zpool 层面。万一 zpool 丢失，唯一的选择就是从头重建，并从备份中恢复其内容。仅仅创建快照并不足以保证在崩溃后的恢复，还必须将这些快照发送到其他地方。后续章节将对此进行进一步说明。

>**注意**
>
>ZFS 不只是一个简单的文件系统（按通常被接受的定义），它更像是文件系统与卷管理器的混合体。关于这一点的讨论超出了本文范围，只需记住这一事实，并在本文其余部分中继续使用这一常见术语即可。

#### 创建 zpool

通用语法如下：

```sh
zpool create <池名> [{striped,mirror,raidz,raidz2,raidz3}] /dev/blockdevice1 /dev/blockdevice2 ... [{striped,mirror,raidz,raidz2,raidz3}] /dev/blockdeviceA /dev/blockdeviceB ... [{striped,mirror,raidz,raidz2,raidz3}] /dev/blockdeviceX /dev/blockdeviceY ...
```

>**提示**
>
>
>如果未指定 `striped、mirror、raidz、raidz2、raidz3` 中的任何一种，则默认使用 `striped`。

一些示例：

- `zpool create zfs_test /dev/sda`：创建一个仅由单个物理设备组成的 zpool，包含一个 vdev（完全没有冗余）
- `zpool create zfs_test /dev/sda /dev/sdb`：创建一个由两个物理设备条带化组成的单一 vdev 的 zpool（完全没有冗余）
- `zpool create zfs_test mirror /dev/sda /dev/sdb`：创建一个包含一个镜像 vdev 的 zpool
- `zpool create zfs_test mirror /dev/sda /dev/sdb mirror /dev/sdc /dev/sdd`：创建一个由两个 vdev 组成的“条带化镜像”zpool，每个 vdev 都是由两个物理设备构成的镜像（每个 vdev 中可以损坏一块磁盘而不丢失整个 zpool）
- `zpool create zfs_test raidz /dev/sda /dev/sdb /dev/sdc`：创建一个包含三个物理设备、采用 RAID-Z1 的单一 vdev 的 zpool（可容忍一块磁盘损坏）

>**提示**
>
>还有一些其他用于 vdev 类型的关键字，例如 `spare`、`cache`、`slog`、`metadata` 或 `draid`（分布式 RAID）。

如果使用的是文件而不是块设备，只需将块设备路径替换为所使用文件的完整路径即可。例如：

- `zpool create zfs_test /dev/sda` 变为 `zpool create zfs_test /var/lib/zfs_img/zfs0.img`
- `zpool create zfs_test /dev/sda /dev/sdb` 变为 `zpool create zfs_test /var/lib/zfs_img/zfs0.img /var/lib/zfs_img/zfs1.img`

以此类推。

在 zpool 创建完成后，无论其架构如何，都会自动创建一个与 zpool 同名的数据集，并直接挂载到 VFS 根目录下：

```sh
mount | grep zpool_test
zpool_test on /zpool_test type zfs (rw,xattr,noacl)
```

此时，该数据集只是一个“空壳”，尚未包含任何数据。

#### 显示 zpool 的统计信息和状态

可以通过以下命令查看当前已知的 zpool 列表以及一些使用情况统计信息：

```sh
zpool list
NAME         SIZE  ALLOC   FREE  CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP    HEALTH  ALTROOT
rpool       5.45T   991G  4.49T        -         -     1%    17%  1.00x    ONLINE  -
zpool_test  99.5G   456K  99.5G        -         -     0%     0%  1.00x    ONLINE  -
```

下面是对显示内容的一些简要说明：

- NAME：存储池的名称
- SIZE：存储池的总大小。在 RAID-Z{1,3} vdev 的情况下，该大小已计入奇偶校验。由于 `zpool_test` 是一个镜像 vdev，这里显示的大小是单块磁盘的大小。
- ALLOC：当前已存储数据的大小（对于 RAID-Z{1,3} vdev 同样适用上述说明）
- FREE：可用的空闲空间（FREE = SIZE - ALLOC）
- CKPOINT：可能存在的 checkpoint（即全局 zpool 快照）所占用的空间
- EXPANDSZ：可用于扩展 zpool 的空间。通常这里不会显示任何内容，只有在特定场景下才会出现
- FRAG：空闲空间碎片率，以百分比表示。碎片化对于 ZFS 来说并不是问题，因为它在设计时就考虑了这一点。目前也没有对 zpool 进行碎片整理的方法，除非从头重新创建并从备份中恢复数据
- CAP：已使用空间的百分比
- DEDUP：数据去重因子。除非某个 zpool 启用了数据去重，否则始终为 `1.00x`
- HEALTH：当前 pool 的状态，“ONLINE”表示 pool 处于最佳状态（即未降级，或更糟的是不可用）
- ALTROOT：备用根路径（重启后不会持久保留）。当需要在 live media 环境中处理 zpool 时非常有用：所有数据集都会相对于该路径挂载，该路径可以通过 `zpool import` 命令的 `-R` 选项来设置

也可以使用 `-v` 选项查看更多细节：

```sh
zpool list -v
```

另一个非常有用的命令是 `zpool status`，它可以提供有关各个 zpool 当前状况的详细报告，以及是否存在需要修复的问题：

```sh
zpool status
```

#### ZFS 存储池导入、导出

>**技巧**
>
>有关所有可用选项的详细说明，请参阅 `zfs-import(8)` 手册页。

zpool 并不会自动出现，它必须被 **导入** 后，系统才能识别并使用它。在 zpool 被导入后，将会发生以下事情：

1. 所有数据集（包括根数据集）都会挂载到 VFS 中，除非 `mountpoint` 属性另有指定（例如 `mountpoint=none`）。如果数据集之间存在嵌套关系并且需要按层级方式挂载，ZFS 会自动处理这种情况。
2. 将在 `/dev/zvol/<存储池名称>` 下创建 zvolume 的块设备条目。

要搜索并列出系统中所有可用（且尚未导入）的 zpool，可以执行以下命令：

```sh
zpool import
```

要实际导入某个 zpool，只需指定其名称，ZFS 会自动在所有已连接的磁盘上进行探测：

```sh
zpool import zfs_test
```

或者使用选项 `-a` 一次性导入所有可用的 ZFS 存储池：

```sh
zpool import -a
```

如果组成某个 ZFS 存储池的所有 vdev 都可用，无论是处于干净状态还是已降级但仍可接受的状态，导入操作都应当能够成功。如果哪怕只缺失了一个 vdev，也无法导入该 ZFS 存储池，此时只能通过备份来恢复。

现在来演示前面提到过的 ALTROOT：假设需要导入 *zfs_test*，但希望其所有可挂载的数据集都相对于 `/mnt/gentoo`，而不是 VFS 根目录。这可以通过如下方式实现：

```sh
zpool import -R /mnt/gentoo zpool_test
zpool list
```


可以通过以下方式确认：

```sh
mount | grep zpool_test
zpool_test on /mnt/gentoo/zpool_test type zfs (rw,xattr,noacl)
```

与导入 zpool 相反的操作称为存储池 **导出**。如果没有任何对象正在使用该存储池（即数据集上没有打开的文件，且没有 zvolume 正在使用），则可以通过以下命令简单地导出 zpool：

```sh
zpool export zpool_test
```

此时，会从 VFS 中卸载所有已挂载的数据集，与 zvolume 对应的所有块设备条目也会从 `/dev` 中被清除。

#### 编辑 Zpool 属性

zpool 具有若干属性（也称为 properties）。其中一部分是可以修改的，用来作为“旋钮”控制诸如数据压缩、加密等方面；而另一些属性则是内在属性，只能读取，不能修改。可以通过 `zpool` 命令的两个选项来与这些属性交互：

- `zpool get 属性名称 zpoolname` 用于查看指定的属性名称（特殊的属性名称 *all* 可用于查看全部属性）
- `zpool set 属性名称=属性值 zpoolname` 用于将属性名称设置为 `属性值`

```sh
zpool get all zpool_test
```

输出采用表格格式，其中最后两列含义如下：

- `VALUE`：该属性的当前值。对于布尔属性，值可以是 `on` / `off`；对于 zpool feature，值可以是 `active`（已启用且**当前**正在使用）、`enabled`（已启用但**当前**未在使用）以及 `disabled`（未启用，未在使用）。根据系统所使用的 OpenZFS 版本以及 zpool 上启用的 feature 情况，该 zpool 可能可以被导入，也可能无法导入。稍后会进一步解释这一点。
- `SOURCE`：标明该属性值是被覆盖设置的（`local`），还是使用默认值（`default`）。如果某个属性不可更改、只能读取，则会显示一个短横线。

虽然不会对所有属性逐一说明，但有一点会立刻引起注意：有一些属性名称以 `feature@` 开头。这是什么？是历史原因 <https://wiki.gentoo.org/wiki/ZFS#cite_note-2>

传统的 zpool 版本号编号方案在 2012 年被废弃（大致是在 Oracle 停止 OpenSolaris 并转为闭门开发 ZFS 之后），并切换为 *feature flags* 机制（zpool 的版本号同时被设置为 5000，自此不再变化）。因此，才会在上述命令输出中看到各种 `feature@` 条目。

>**技巧**
>
>某个 ZFS 实现所支持的最新 *legacy* 版本号，可以通过 `zpool upgrade -v` 查看。对于 OpenZFS/ZFS，其支持的最新 *legacy* 版本号是 28。

在版本号编号方案仍然使用的时期，当创建 zpool 时，操作系统会用其所支持的最高 zpool 版本号来标记该 zpool <https://wiki.gentoo.org/wiki/ZFS#cite_note-3>。这些版本号从 1（ZFS 初始发布）开始，到 Solaris 11.4 SRU 51 所支持的 49 为止。由于 zpool 版本号在 Solaris 的各个版本之间是单调递增的，因此较新的 Solaris 版本总是可以导入由较旧 Solaris 版本创建的 zpool。但这里有个前提：为了获得较新 Solaris 版本所带来的各种 ZFS 新特性和增强功能，必须手动升级 zpool 的版本号。在 zpool 版本号被升级之后，旧版本的 Solaris 将无法再导入该 zpool。
例如，在 Solaris 10 9/10（支持的 zpool 版本号最高为 22）下创建的 zpool，可以在 Solaris 10 1/13（支持的 zpool 版本号最高为 32）下导入，并且之后仍然可以再次在 Solaris 10 1/13 下导入——前提是该 zpool 的版本号尚未在 Solaris 10 1/13 下被升级（否则会将 zpool 标记为版本 32）。

同样的逻辑也适用于 feature flags：如果某个 zpool 启用了当前系统所使用的 ZFS 版本并不支持的 feature flag，则该 zpool 将无法被导入。与（legacy）版本号机制类似，为了获得后续 OpenZFS/ZFS 版本提供的新 feature flags，必须对 zpool 进行升级（手动操作），使其支持这些新的 feature flags。在完成这一操作后，较旧的 OpenZFS/ZFS 版本将无法再导入该 zpool。

>**重要**
>
>仅就 zpool 导入而言，feature flag 处于 `disabled` 还是 `enabled` 状态并不重要。只有在处于 `active` 状态时，才需要遵循 [Feature Flags 对照表](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/Feature%20Flags.html) 中关于只读或完全不可导入的规则。

>**警告**
>
>Feature flags 可能相当棘手：有些在被 `enabled` 后会 **立刻** 变为 `active`，有些一旦 `enabled` 就再也无法回到 `disabled`，还有一些在进入 `active` 状态后就再也无法回到 `enabled`。更多细节请参阅 [zpool-features (7)](https://openzfs.github.io/openzfs-docs/man/7/zpool-features.7.html)。为了向后兼容性，建议仅在确有需要时有选择地启用这些 feature。

如果 zpool 位于 SSD 或 NVMe 设备上，启用 `autotrim` feature 可能会比较方便，这样可以让 ZFS 自动处理相关的“日常维护”工作：

```sh
zpool get autotrim zpool_test
NAME        PROPERTY  VALUE     SOURCE
zpool_test  autotrim  off       default
```

```sh
zpool set autotrim=on zpool_test
zpool get autotrim zpool_test
NAME        PROPERTY  VALUE     SOURCE
zpool_test  autotrim  on        local
```

另一个非常有用的 feature 是数据压缩。ZFS 默认使用 LZ4，如果希望切换到 ZSTD，一个看似直接但实际上行不通的做法是：

```sh
zpool set feature@zstd_compress=active zpool_test
cannot set property for 'zpool_test': property 'feature@zstd_compress' can only be set to 'enabled' or 'disabled|output=<pre>
```

确实如此，即便该 feature 在 zpool 上已经被 `enabled`，也不能通过这种方式直接将其激活。真正的激活方式是：在数据集或 zvolume 层级，通过某个“魔法命令”修改相关属性。一旦这个“魔法命令”被执行，ZSTD 压缩算法才会真正投入使用（即变为 `active`）：

```sh
zpool get feature@zstd_compress zpool_test
NAME        PROPERTY               VALUE                  SOURCE
zpool_test  feature@zstd_compress  active                 local
 Important
```

>**重要**
>
>该变更 **只会** 作用于之后新写入的数据，zpool 中已有的数据保持不变。

如前所述，为了使用更新版本 OpenZFS/ZFS（或操作系统所使用的其他 ZFS 实现）所提供的新 feature，zpool 必须进行 *upgrade*。当需要执行 *upgrade* 时，`zpool status` 会给出提示，并建议运行 `zpool upgrade`（在本例中完整命令为 `zpool upgrade zpool_test`）：

```sh
zpool status zpool_test
```

在完成 zpool upgrade 之后：

```sh
zpool status zpool_test
```

要查看当前操作系统所使用的 ZFS 版本支持哪些 feature flags，可以使用：

```sh
zpool upgrade -v
```

#### Zpool 故障与 spare vdev

硬件并非完美，有时磁盘可能因为某些原因发生故障，或者其上的数据可能发生损坏。ZFS 提供了检测损坏并防止甚至“双比特翻转”错误的对策。如果底层 vdev 具有冗余能力，受损数据可以被修复，仿佛什么都没有发生过一样。

请记住，zpool 是跨所有 vdev 进行条带化的，当设备发生故障时可能出现两种情况：

- 要么冗余度足够，zpool 仍然可用，但处于“DEGRADED”状态
- 要么冗余度不足，zpool 进入“SUSPENDED”状态（此时必须从备份中恢复数据）

可以通过 `zpool status` 查看当前情况：

`zpool status zpool_test`

```
pool: zpool_test
 state: DEGRADED
status: One or more devices could not be used because the label is missing or
        invalid.  Sufficient replicas exist for the pool to continue
        functioning in a degraded state.
action: Replace the device using 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
config:

        NAME           STATE     READ WRITE CKSUM
        zpool_test     DEGRADED     0     0     0
          mirror-0     DEGRADED     0     0     0
            /dev/sde1  UNAVAIL      3    80     0
            /dev/sdh1  ONLINE       0     0     0
```

**Tip**
可以通过对块设备执行 `echo offline > /sys/block/<block device>/device/state` 来模拟磁盘故障（执行 `echo running > /sys/block/<block device>/device/state` 可将磁盘恢复为在线状态）。

有缺陷的磁盘（/dev/sde）需要被物理替换为另一块磁盘（此处为 /dev/sdg）。该操作首先需要将故障磁盘从 zpool 中下线：

```sh
zpool offline zpool_test /dev/sde
zpool status zpool_test
  pool: zpool_test
 state: DEGRADED
status: One or more devices has experienced an unrecoverable error.  An
        attempt was made to correct the error.  Applications are unaffected.
action: Determine if the device needs to be replaced, and clear the errors
        using 'zpool clear' or replace the device with 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-9P
config:

        NAME           STATE     READ WRITE CKSUM
        zpool_test     DEGRADED     0     0     0
          mirror-0     DEGRADED     0     0     0
            /dev/sde1  OFFLINE      3    80     0
            /dev/sdh1  ONLINE       0     0     0

errors: No known data errors
```

然后执行替换操作（ZFS 会自动对新磁盘进行分区）：

```sh
zpool replace zpool_test /dev/sde /dev/sdg
zpool status zpool_test
```

磁盘被替换后，ZFS 会在后台启动一个称为 *resilvering* 的重建过程。根据 zpool 中存储的数据量不同，该过程可能需要数小时甚至数天。在此示例中数据量很小，因此 resilvering 只需几秒钟。在大型 zpool 上，resilvering 的耗时甚至可能不可接受，这正是 draid 发挥作用的场景（这是一种与 raidz 完全不同的机制，后文将介绍）。

如果不希望这是一个手动操作，那么是否可以为 zpool 配置热备盘，使其在磁盘故障时自动完成替换？这正是名为 spare 的特殊 vdev 的用途。向 zpool 添加 spare vdev 有两种方式：在创建 zpool 时指定，或在现有 zpool 上动态添加。作为热备的磁盘应当与故障磁盘保持一致。

要添加一个 spare vdev，只需执行 `zpool add` 命令（同样，ZFS 会自动对热备磁盘进行分区）。添加到 zpool 后，热备盘将处于待命状态，直到发生磁盘故障：

```sh
zpool add zpool_test spare /dev/sdd
zpool status zpool_test
  pool: zpool_test
 state: ONLINE
  scan: resilvered 28.9M in 00:00:01 with 0 errors on Sat May  6 11:12:55 2023
config:

        NAME           STATE     READ WRITE CKSUM
        zpool_test     ONLINE       0     0     0
          mirror-0     ONLINE       0     0     0
            /dev/sdg1  ONLINE       0     0     0
            /dev/sdh1  ONLINE       0     0     0
        spares
          /dev/sdd1    AVAIL   

errors: No known data errors
```

此时热备盘处于可用状态（`AVAIL`）。如果 /dev/sdh（或 /dev/sdg）发生故障，/dev/sdd 会立即接管故障磁盘（其状态变为 `INUSE`），并在后台触发 zpool 的 resilvering 过程，整个过程无需 zpool 停机：

```sh
zpool status
  pool: zpool_test
 state: DEGRADED
status: One or more devices could not be used because the label is missing or
        invalid.  Sufficient replicas exist for the pool to continue
        functioning in a degraded state.
action: Replace the device using 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-4J
  scan: resilvered 40.7M in 00:00:01 with 0 errors on Sat May  6 11:39:28 2023
config:

        NAME             STATE     READ WRITE CKSUM
        zpool_test       DEGRADED     0     0     0
          mirror-0       DEGRADED     0     0     0
            spare-0      DEGRADED     0     0     0
              /dev/sdg1  UNAVAIL      3    83     0
              /dev/sdd1  ONLINE       0     0     0
            /dev/sdh1    ONLINE       0     0     0
        spares
          /dev/sdd1      INUSE     currently in use
```

原始磁盘会被自动、异步地移除。如果没有自动完成，可能需要使用 `zpool detach` 命令手动分离：

```sh
zpool detach zpool_test /dev/sdg
zpool status
  pool: zpool_test
 state: ONLINE
  scan: resilvered 40.7M in 00:00:01 with 0 errors on Sat May  6 11:39:28 2023
config:

        NAME           STATE     READ WRITE CKSUM
        zpool_test     ONLINE       0     0     0
          mirror-0     ONLINE       0     0     0
            /dev/sdd1  ONLINE       0     0     0
            /dev/sdh1  ONLINE       0     0     0

errors: No known data errors
```

>**技巧**
>
>故障磁盘物理替换后，可以将其重新添加到 zpool 作为新的热备盘。同样，也可以让同一个热备盘在多个 zpool 间共享使用。

在当前示例中，如果已有一个镜像 vdev，也可以将第三块磁盘直接加入到该镜像 vdev 中，而非作为热备盘。这可以通过将新磁盘附加到现有镜像 vdev 的某块磁盘上来实现：

```sh
zpool attach zpool_test /dev/sdh /dev/sdg
zpool status zpool_test
  pool: zpool_test
 state: ONLINE
  scan: resilvered 54.4M in 00:00:00 with 0 errors on Sat May  6 11:55:42 2023
config:

        NAME           STATE     READ WRITE CKSUM
        zpool_test     ONLINE       0     0     0
          mirror-0     ONLINE       0     0     0
            /dev/sdd1  ONLINE       0     0     0
            /dev/sdh1  ONLINE       0     0     0
            /dev/sdg1  ONLINE       0     0     0

errors: No known data errors
```

>**注意**
>
>`zpool attach zpool_test /dev/sdd /dev/sdg` 也会得到相同结果。

定期对 zpool 执行 *scrub* 是一种良好做法，可以确保其内容健康。如果发现数据损坏且 zpool 具有足够的冗余，损坏的数据会被自动修复。手动启动 scrub 命令：

```sh
zpool scrub zpool_test
zpool status zpool_test
  pool: zpool_test
 state: ONLINE
  scan: scrub repaired 0B in 00:00:01 with 0 errors on Sat May  6 12:06:18 2023
config:

        NAME           STATE     READ WRITE CKSUM
        zpool_test     ONLINE       0     0     0
          mirror-0     ONLINE       0     0     0
            /dev/sdd1  ONLINE       0     0     0
            /dev/sdh1  ONLINE       0     0     0
            /dev/sdg1  ONLINE       0     0     0

errors: No known data errors
```

如果发现数据损坏，输出示例如下：

```sh
zpool scrub zpool_test
zpool status zpool_test
  pool: zpool_test
 state: ONLINE
status: One or more devices has experienced an unrecoverable error.  An
        attempt was made to correct the error.  Applications are unaffected.
action: Determine if the device needs to be replaced, and clear the errors
        using 'zpool clear' or replace the device with 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-9P
  scan: scrub repaired 256K in 00:00:00 with 0 errors on Sat May  6 12:09:22 2023
config:

        NAME           STATE     READ WRITE CKSUM
        zpool_test     ONLINE       0     0     0
          mirror-0     ONLINE       0     0     0
            /dev/sdd1  ONLINE       0     0     4
            /dev/sdh1  ONLINE       0     0     0
            /dev/sdg1  ONLINE       0     0     0

errors: No known data errors
```

>**技巧**
>
>要故意破坏磁盘内容，可以执行类似 `dd if=/dev/urandom of=/dev/sdd1` 的命令（等待几秒钟以破坏足够的数据）。

数据修复完成后，执行 `zpool clear` 命令，如提示所示：

```sh
zpool clear zpool_test
zpool status zpool_test
  pool: zpool_test
 state: ONLINE
  scan: scrub repaired 256K in 00:00:00 with 0 errors on Sat May  6 12:09:22 2023
config:

        NAME           STATE     READ WRITE CKSUM
        zpool_test     ONLINE       0     0     0
          mirror-0     ONLINE       0     0     0
            /dev/sdd1  ONLINE       0     0     0
            /dev/sdh1  ONLINE       0     0     0
            /dev/sdg1  ONLINE       0     0     0

errors: No known data errors
```

>**技巧**
>
>要从三盘镜像 vdev 中分离磁盘，只需使用 `zpool detach`，如前所示。即便是两盘镜像，也可以分离其中一盘，但会失去冗余保护。

对于三盘镜像，即使仅有一块磁盘健康，zpool 仍然可以正常运行：

```sh
zpool scrub zpool_test
zpool status zpool_test
  pool: zpool_test
 state: ONLINE
status: One or more devices has experienced an unrecoverable error.  An
        attempt was made to correct the error.  Applications are unaffected.
action: Determine if the device needs to be replaced, and clear the errors
        using 'zpool clear' or replace the device with 'zpool replace'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-9P
  scan: scrub in progress since Sat May  6 13:43:09 2023
        5.47G scanned at 510M/s, 466M issued at 42.3M/s, 5.47G total
        0B repaired, 8.31% done, 00:02:01 to go
config:

        NAME           STATE     READ WRITE CKSUM
        zpool_test     ONLINE       0     0     0
          mirror-0     ONLINE       0     0     0
            /dev/sdd1  ONLINE       0     0     0
            /dev/sdh1  ONLINE       0     0 68.9K
            /dev/sdg1  ONLINE       0     0 68.9K

errors: No known data errors
```

#### zpool 销毁与恢复

当不再需要某个 zpool 时，可以使用 `zpool destroy` 销毁它。如果 zpool 不为空并包含 zvol 或 dataset，需要加 `-r` 选项。无需先导出 zpool，ZFS 会自动处理。

如果 zpool 刚被销毁，且其所有 vdev 仍完好，可以通过 `zpool import` 并加 `-D` 选项重新导入：

```sh
zpool destroy zpool_test
zpool import -D
   pool: zpool_test
     id: 628141733996329543
  state: ONLINE (DESTROYED)
 action: The pool can be imported using its name or numeric identifier.
 config:

        zpool_test     ONLINE
          mirror-0     ONLINE
            /dev/sdd1  ONLINE
            /dev/sdh1  ONLINE
            /dev/sdg1  ONLINE
```

通过这种方式导入已销毁的 zpool，也会将其“复原”：

```sh
zpool list zpool_test
cannot open 'zpool_test': no such pool
```

```sh
zpool import -D zpool_test
zpool list zpool_test
NAME         SIZE  ALLOC   FREE  CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP    HEALTH  ALTROOT
zpool_test  99.5G  5.48G  94.0G        -         -     0%     5%  1.00x    ONLINE  -
 Warning
```

>**警告**
>
>技术上讲，该操作只是将 zpool 标记为“已销毁状态”，底层 vdev 上的数据并未清除。因此，**仍可读取所有未加密的数据**。

#### 浏览 zpool 历史

有时查看 zpool 的操作历史非常有用，这时 `zpool history` 就派上用场。由于 `zpool_test` 是全新创建的，暂时没有什么有趣的记录，我们来看一个最近从远程 TrueNAS 备份恢复到工作站的生产环境 zpool 的示例：

```sh
zpool history rpool
```

也可以使用全格式显示完整信息（谁/做了什么/在哪/何时）：

```sh
zpool history -l rpool
```

注意事项：

1. 该 zpool 是使用 Linux live 环境（此处为 Gentoo LiveCD）创建的，当时环境设置了
   主机名为 `livecd`。
2. 用户 `root` 在该 live 环境下创建了两个占位（不可挂载）数据集 `rpool/ROOT` 和 `rpool/HOME`。
3. 数据集 `rpool/ROOT/gentoo-gcc13-avx512`（显然是 Gentoo 系统）由用户 `root` 从远程快照恢复。
4. 数据集 `rpool/HOME/user111`（显然是用户主目录）由用户 `root` 从远程快照恢复。
5. 某个时刻，工作站在恢复的 Gentoo 环境下重启（注意主机名变为 `wks.myhomenet.lan`），导入了该 zpool。
6. 依此类推。

#### Zpool 技巧与注意事项

- zpool 创建后，有时无法缩小 — **如果**池没有 raidz vdev，并且所有 vdev 的 ashift 相同，则可在 0.8 及以上版本使用“设备移除”功能。但此操作可能影响性能，因此 **在创建池或添加 vdev/磁盘时必须谨慎**。

- 可以在 MIRROR 创建后添加更多磁盘。示例命令（/dev/loop0 为 MIRROR 中的第一块磁盘）：

  ```sh
  zpool attach zfs_test /dev/loop0 /dev/loop2
  ```

- 有时，一个更宽的 RAIDZ vdev 不如两个（或更多）小型 RAIDZ vdev 合适。建议在最终确定前先测试预期用途。

- RAIDZ vdev 创建后无法调整大小，只能添加额外热备。硬盘可以逐块替换为更大容量，例如用 2T 硬盘替换 1T 硬盘，从而增加 zpool 可用空间。

- 可以在同一 zpool 中混合 MIRROR 和 RAIDZ vdev。例如，要在已有 RAIDZ1 vdev 的 zpool `zfs_test` 中添加两个磁盘作为 MIRROR vdev：

  ```sh
  zpool add -f zfs_test mirror /dev/loop4 /dev/loop5
  ```

>**警告**
>
>通常没有充分理由这样做。特殊 vdev 或 log vdev 可能合理，但一般会导致两者性能均下降。

>**注意**
>
>添加不匹配的 vdev 时，需要使用选项 `-f`。

#### 来自其他架构的 Zpool

可以导入来自其他平台的 zpools，即使它们使用不同的位序，只要满足以下条件：

- 版本为 28（legacy）或更早
- 对于版本号为 5000 的 zpool，所使用的 ZFS 实现至少支持该 zpool 指定的特性。

下面的例子中，一个名为 *oldpool* 的 zpool 曾在使用 <span data-type="inline-memo" data-inline-memo-content="External link for the app-emulation/qemu package.">app-emulation/qemu</span> 模拟的 FreeBSD 10/SPARC64 环境中创建。该 zpool 使用 legacy 版本 28 创建（`zpool create -o version=28`），这与运行 Solaris 10 的 SPARC64 机器所做的基本一致：

```sh
zpool import
   pool: oldpool
     id: 11727962949360948576
  state: ONLINE
status: The pool is formatted using a legacy on-disk version.
 action: The pool can be imported using its name or numeric identifier, though
        some features will not be available without an explicit 'zpool upgrade'.
 config:

        oldpool         ONLINE
          raidz1-0      ONLINE
            /dev/loop0  ONLINE
            /dev/loop1  ONLINE
            /dev/loop2  ONLINE
```

```sh
zpool import -f oldpool
zpool status oldpool
  pool: oldpool
 state: ONLINE
status: The pool is formatted using a legacy on-disk format.  The pool can
        still be used, but some features are unavailable.
action: Upgrade the pool using 'zpool upgrade'.  Once this is done, the
        pool will no longer be accessible on software that does not support
        feature flags.
config:

        NAME            STATE     READ WRITE CKSUM
        oldpool         ONLINE       0     0     0
          raidz1-0      ONLINE       0     0     0
            /dev/loop0  ONLINE       0     0     0
            /dev/loop1  ONLINE       0     0     0
            /dev/loop2  ONLINE       0     0     0

errors: No known data errors
```

注意所有 *feature@* 属性（均为 `disabled`）和 *version* 属性（`28`）的值：

```sh
zpool get all oldpool
```

>**注意**
>
>FreeBSD 9、10、11 和 12 使用的是来自 Illumos/OpenSolaris 的 ZFS 实现。FreeBSD 13 则使用 OpenZFS 2.x。

要让该 zpool 能够使用系统上 OpenZFS/ZFS 或 ZFS 实现的最新功能，可按照前面章节所述升级 zpool：

```sh
zpool upgrade oldpool
```

作为测试，对 zpool 进行 scrub：

```sh
zpool scrub oldpool
zpool status oldpool
```

关于其中的数据：

```sh
tar -tvf /oldpool/boot-fbsd10-sparc64.tar
```

即便 zpool 来自完全不同的架构（SPARC64 是 MSB 位序，而 ARM/X86_64 是 LSB 位序架构），它仍然可以被正常导入。要清理测试环境（如本节后半部分所创建）：

```sh
zpool export oldpool
losetup -D
rm /tmp/fbsd-sparc64-ada{0,1,2}.raw
```

现在 zpool 已升级，如果尝试在旧的 FreeBSD 10/SPARC64 环境导入，会发生以下情况：

```sh
zpool import -o altroot=/tmp -f oldpool
This pool uses the following feature(s) not supported by this system:
        com.delphix:spacemap_v2 (Space maps representing large segments are more efficient.)
        com.delphix:log_spacemap (Log metaslab changes on a single spacemap and flush them periodically.)
All unsupported features are only required for writing to the pool.
The pool can be imported using '-o readonly=on'.
```

以只读方式导入：

```sh
zpool import -o readonly=on -o altroot=/tmp -f oldpool
NAME      SIZE  ALLOC   FREE  EXPANDSZ   FRAG    CAP  DEDUP  HEALTH  ALTROOT
oldpool  11.9G  88.7M  11.9G         -     0%     0%  1.00x  ONLINE  /tmp
```

系统能够识别 zpool，但拒绝以读写方式导入。执行 `zpool status` 或 `zpool list` 不会显示该 zpool，但 `zpool get all` 可以查看所有属性：

```sh
zpool get all
```

注意属性 `unsupported@com.delphix:spacemap_v2` 和 `unsupported@com.delphix:log_spacemap` 的值。所有不受支持的功能都以 `unsupported@` 开头。

为了完整性，这里展示尝试导入完全不兼容 zpool 的情况。例如，当 Linux 系统（OpenZFS 2.1.x）尝试导入在 Solaris 11.4 下创建的 zpool（Solaris 仍使用 legacy 版本号方案，zpool 版本号为 42）：

```sh
zpool import -f rpool
cannot import 'rpool': pool is formatted using an unsupported ZFS version
```

>**提示**
>
>在这种情况下还有一条“救生索”：虽然 zpool 对 OpenZFS 来说是未知版本，但 Solaris 11.4 和 OpenZFS 2.1.x 报告的 ZFS 版本都是 5（不要与 zpool 版本混淆），因此 zpool 上的数据集可以先在 Solaris 环境下通过 `zfs send` 导出，然后在 Linux 环境下通过 `zfs receive` 导入。

>**重要**
>
>为了可重复性，本节剩余部分详细说明了如何在 FreeBSD/SPARC64 环境下创建上文使用的 zpool `oldpool`。如果不关心该过程，其余内容可以跳过。

创建上述 zpool `oldpool` 的步骤如下：

- 安装<span data-type="inline-memo" data-inline-memo-content="External link for the app-emulation/qemu package.">app-emulation/qemu</span>（本例使用 QEMU 8.0），确保变量 `QEMU_SOFTMMU_TARGETS` 至少包含 `sparc64`，以构建完整的 SPARC64 系统模拟器：
  `emerge --ask app-emulation/qemu`
- 从镜像站下载 FreeBSD 10/SPARC64 DVD ISO 镜像（FreeBSD 9 在 QEMU 下启动会崩溃，因此最小版本为 FreeBSD 10；FreeBSD 12 在加载所需模块时可能有问题）
- 为未来的 vdev 创建虚拟磁盘镜像（本例三个，每个 4G）：
  `for i in {0..2}; do qemu-img create -f raw /tmp/fbsd-sparc64-ada${i}.raw 4G; done;`
- 启动 QEMU（使用 `-nographic` 避免 FreeBSD 挂起，同时 Sun4u 机器有 2 条 IDE 通道，因此分配 3 个硬盘 + 1 个 ATAPI CD/DVD ROM 驱动器）：

```sh
qemu-system-sparc64 -nographic -m 2G \
  -drive format=raw,file=/tmp/fbsd-sparc64-ada0.raw,media=disk,index=0 \
  -drive format=raw,file=/tmp/fbsd-sparc64-ada1.raw,media=disk,index=1 \
  -drive format=raw,file=/tmp/fbsd-sparc64-ada2.raw,media=disk,index=2 \
  -drive format=raw,file=/tmp/FreeBSD-10.4-RELEASE-sparc64-dvd1.iso,media=cdrom,readonly=on
```

- 在 OpenBIOS 提示符 `0 >` 下输入：
  `boot cdrom:f`
- FreeBSD 应该开始启动，由于模拟较慢，启动过程可能需要一些时间。启动完成后，检查所有虚拟磁盘（ada*X*）是否被识别。

```sh
Not a bootable ELF image
Loading a.out image...
Loaded 7680 bytes
entry point is 0x4000

> > FreeBSD/sparc64 boot block
> > Boot path:   /pci@1fe,0/pci@1,1/ide@3/ide@1/cdrom@1:f
> > Boot loader: /boot/loader
> > Consoles: Open Firmware console

FreeBSD/sparc64 bootstrap loader, Revision 1.0
(root@releng1.nyi.freebsd.org, Fri Sep 29 07:57:55 UTC 2017)
bootpath="/pci@1fe,0/pci@1,1/ide@3/ide@1/cdrom@1:a"
Loading /boot/defaults/loader.conf
/boot/kernel/kernel data=0xc25140+0xe62a0 syms=[0x8+0xcd2c0+0x8+0xbf738]

Hit [Enter] to boot immediately, or any other key for command prompt.
Booting [/boot/kernel/kernel]...
jumping to kernel entry at 0xc00a8000.
Copyright (c) 1992-2017 The FreeBSD Project.
Copyright (c) 1979, 1980, 1983, 1986, 1988, 1989, 1991, 1992, 1993, 1994
The Regents of the University of California. All rights reserved.
FreeBSD is a registered trademark of The FreeBSD Foundation.
FreeBSD 10.4-RELEASE #0 r324094: Fri Sep 29 08:00:33 UTC 2017
root@releng1.nyi.freebsd.org:/usr/obj/sparc64.sparc64/usr/src/sys/GENERIC sparc64
(...)
ada0 at ata2 bus 0 scbus0 target 0 lun 0
ada0: <QEMU HARDDISK 2.5+> ATA-7 device
ada0: Serial Number QM00001
ada0: 33.300MB/s transfers (UDMA2, PIO 8192bytes)
ada0: 4096MB (8388608 512 byte sectors)
ada0: Previously was known as ad0
cd0 at ata3 bus 0 scbus1 target 1 lun 0
cd0: <QEMU QEMU DVD-ROM 2.5+> Removable CD-ROM SCSI device
cd0: Serial Number QM00004
cd0: 33.300MB/s transfers (UDMA2, ATAPI 12bytes, PIO 65534bytes)
cd0: 2673MB (1368640 2048 byte sectors)
ada1 at ata2 bus 0 scbus0 target 1 lun 0
ada1: <QEMU HARDDISK 2.5+> ATA-7 device
ada1: Serial Number QM00002
ada1: 33.300MB/s transfers (UDMA2, PIO 8192bytes)
ada1: 4096MB (8388608 512 byte sectors)
ada1: Previously was known as ad1
ada2 at ata3 bus 0 scbus1 target 0 lun 0
ada2: <QEMU HARDDISK 2.5+> ATA-7 device
ada2: Serial Number QM00003
ada2: 33.300MB/s transfers (UDMA2, PIO 8192bytes)
ada2: 4096MB (8388608 512 byte sectors)
ada2: Previously was known as ad2
(...)
Console type [vt100]:
```

- 当内核启动完成后，FreeBSD 会询问控制台类型，直接按 ENTER 接受默认选项（VT100）

- FreeBSD 安装程序启动后，使用 TAB 键两次将 `LiveCD` 高亮，然后按 ENTER 退出安装程序并进入登录提示符

- 在登录提示符下输入 root（无需密码），即可进入 BASH shell 提示符

- 依次执行命令 kldload opensolaris **然后** kldload zfs（部分警告可以忽略，因为 kldstat 会显示已加载模块）

```sh
root@:~ # kldload opensolaris
root@:~ # kldload zfs
ZFS NOTICE: Prefetch is disabled by default if less than 4GB of RAM is present;
to enable, add "vfs.zfs.prefetch_disable=0" to /boot/loader.conf.
ZFS filesystem version: 5
ZFS storage pool version: features support (5000)
root@:~ # kldstat
Id Refs Address            Size     Name
1   10 0xc0000000 e97de8   kernel
2    2 0xc186e000 106000   opensolaris.ko
3    1 0xc1974000 3f4000   zfs.ko
```

- 创建一个使用 legacy 版本方案（version 28）的 zpool，名为 `oldpool`：

```sh
zpool create -o altroot=/tmp -o version=28 oldpool raidz /dev/ada0 /dev/ada1 /dev/ada2
```

- 检查 zpool 状态，应显示 `oldpool` 为 `ONLINE`（ZFS 会提示使用 legacy 格式，不要升级！）

```sh
root@:~ # zpool status
pool: oldpool
state: ONLINE
status: The pool is formatted using a legacy on-disk format.  The pool can
still be used, but some features are unavailable.
action: Upgrade the pool using 'zpool upgrade'.  Once this is done, the
pool will no longer be accessible on software that does not support feature
flags.
scan: none requested
config:

NAME        STATE     READ WRITE CKSUM
oldpool     ONLINE       0     0     0
raidz1-0    ONLINE       0     0     0
ada0        ONLINE       0     0     0
ada1        ONLINE       0     0     0
ada2        ONLINE       0     0     0

errors: No known data errors
```

- 由于 zpool 已临时挂载在 /tmp/oldpool 下，可通过如下命令将一些数据拷贝到其中：

```sh
tar cvf /tmp/oldpool/boot-fbsd10-sparc64.tar /boot
```

- 导出 zpool：

```sh
zpool export oldpool
```

- 按 Ctrl+A X 终止 QEMU（无需正常关机，因为这是 live 环境），返回 Gentoo 主机 shell
- 最后，将原始镜像映射为 loop 设备：

```sh
for i in {0..2}; do losetup -f /tmp/fbsd-sparc64-ada${i}.raw; done;
losetup -l
NAME       SIZELIMIT OFFSET AUTOCLEAR RO BACK-FILE                  DIO LOG-SEC
/dev/loop1         0      0         0  0 /tmp/fbsd-sparc64-ada1.raw   0     512
/dev/loop2         0      0         0  0 /tmp/fbsd-sparc64-ada2.raw   0     512
/dev/loop0         0      0         0  0 /tmp/fbsd-sparc64-ada0.raw   0     512
```

### ZFS 数据集

#### 概念

就像 `/usr/sbin/zpool` 用于管理 zpool 一样，第二个 ZFS 工具是 `/usr/sbin/zfs`，用于处理与数据集相关的任何操作。理解 [zfsconcepts(7)](https://openzfs.github.io/openzfs-docs/man/7/zfsconcepts.7.html) 和 [zfs(8)](https://openzfs.github.io/openzfs-docs/man/8/zfs.8.html) 中的概念非常重要。

- 数据集（datasets）是逻辑数据容器，由 `/usr/sbin/zfs` 命令作为单一实体进行管理。每个数据集在给定 zpool 内具有唯一名称（路径），可以是文件系统（filesystem）、快照（snapshot）、书签（bookmark）或 zvolume。
- 文件系统（filesystems）是 POSIX 文件系统，可以挂载到系统 VFS 中，并像 ext4 或 XFS 文件系统一样以文件和目录的形式显示。支持扩展形式的 POSIX ACL（NFSv4 ACL）和扩展属性。

>**注意**
>
>即便文件位于同一 zpool 内，移动文件集之间的文件也是“复制后删除”（cp-then-rm）操作，而非瞬间移动。

- 快照（snapshots）是文件系统或 zvolume 的冻结只读时间点状态。ZFS 是写时复制（copy-on-write）系统，快照只保留自上一次快照以来发生的变化，因此如果没有变化，快照几乎是“免费”的。与 LVM 快照不同，ZFS 快照不需要空间预留，并且数量可以无限。快照可以通过“魔法路径”浏览，查看快照时的文件系统或 zvolume 内容，也可以用于回滚相关文件系统或 zvolume，命名格式为：*zpoolname/datasetname@snapshotname*。

>**警告**
>
>关于快照的重要事项：

- **务必备份到外部系统！** 如果 zpool 损坏/不可用或数据集被销毁，数据将永久丢失。
- 快照不是事务性的，正在进行的写入不能保证完整存储在快照中（例如，当快照创建时，一个 40GB 文件仅写入了 15GB，那么快照只会记录这 15GB）。
- 对于设置了保留（reservation）的 zvolume，其首次快照可能会产生意外的空间占用，因为它会为覆盖整个卷预留足够空间，同时考虑已有的已分配空间。
- 书签（bookmarks）类似快照，但不保存数据，仅存储时间点引用。这对于对备份系统进行增量传输非常有用，而无需在源系统保留该数据集的所有历史快照。就像书签标记在书页上一样。另一个用途是创建经过编辑的数据集，命名格式为：*zpoolname/datasetname#bookmarkname*。
- 克隆（clones）是快照的可写“视图”，可以像文件系统一样挂载到系统 VFS。其特点是引入了父子依赖关系：一旦克隆被创建，原始数据集在克隆存在期间不能被销毁。可以通过 *promote* 操作将克隆提升为父数据集，从而使原始文件系统成为子数据集（同时影响原始文件系统的快照，也会被“反转”）。
- zvolume 是模拟块设备，可像任何物理硬盘一样使用，在目录 `/dev/zvol/zpoolname` 下作为特殊块设备条目访问。

### 文件系统数据集（Filesystems datasets）

每当创建一个 zpool 时，同名的第一个文件系统数据集也会被自动创建。这个根数据集除非销毁整个 zpool，否则无法被删除。之后创建的所有数据集都通过“路径”唯一标识，并始终位于该根数据集的某个位置。之所以说“某个位置”，是因为后续创建的文件系统数据集可以嵌套，从而形成层级结构。

举例说明，重新创建 zpool `zpool_test`：

```bash
zpool create zpool_test raidz /dev/ram0 /dev/ram1 /dev/ram2 /dev/ram3
zfs list
NAME          USED  AVAIL  REFER  MOUNTPOINT
zpool_test    541K  5.68T  140K   /zpool_test
```

可以看到，根数据集的名称（*NAME* 列）是 `zpool_test`，与 zpool 名称相同。该数据集定义了挂载点（*MOUNTPOINT* 列），所以它是一个文件系统数据集。验证挂载情况：

```bash
mount | grep zpool_test
zpool_test on /zpool_test type zfs (rw,xattr,noacl)
```

>**提示**
>
>文件系统类型显示为 `zfs`，说明它是一个文件系统数据集。

查看内容：

```bash
ls -la /zpool_test
total 33
drwxr-xr-x  2 root root  2 May  8 19:15 .
drwxr-xr-x 24 root root 26 May  8 19:15 ..
```

*空的！* 现在创建额外的文件系统数据集（注意路径不带前导斜杠）：

```bash
zfs create zpool_test/fds1
zfs create zpool_test/fds1/fds1_1
zfs create zpool_test/fds1/fds1_1/fds1_1_1
zfs create zpool_test/fds1/fds1_1/fds1_1_2
zfs create zpool_test/fds2
zfs create zpool_test/fds2/fds2_1
```

`zfs list` 可以查看结果。默认情况下，挂载点层级与文件系统数据集的层级相同。挂载点可以根据需要自定义，甚至完全不同。文件系统数据集的层级也可通过重命名（`zfs rename`）更改。例如，将 `zpool_test/fds1/fds1_1/fds1_1_2` 改为 `zpool_test/fds3`：

```bash
zfs rename zpool_test/fds1/fds1_1/fds1_1_2 zpool_test/fds3
tree /zpool_test
zfs list
```

>**注意**
>
>ZFS 会相应地调整挂载点。

更复杂的情况：重命名带有子数据集的文件系统，例如将 `zpool_test/fds2` 改为 `zpool_test/fds3/fds3_1`：

```bash
zfs rename zpool_test/fds2 zpool_test/fds3/fds3_1
zfs list
```

>**提示**
>
如果想在层级中创建“占位符”（即不包含数据，仅用作定义子数据集的文件系统），先创建完整层级，然后将 `canmount` 属性设置为 `false`。ZFS 会相应调整挂载点，但子数据集名称保持不变，需要单独修改。

与使用 `zfs create` 不同的是，直接使用 `mkdir` 也能创建层级，但每个文件系统数据集是独立的“盒子”，具有独立的属性集合。ZFS 无法压缩、加密或共享单个文件，也不能对单个文件进行快照/回滚，只能针对整个文件系统数据集操作。换句话说，对 `zpool_test/fds1` 的操作（属性更改、快照、回滚等）只影响它本身，而不影响子数据集或其他数据集。*盒子里的内容，只影响盒子内部。*

>**提示**
>
运行 `zpool history zpool_test` 可以查看操作历史。当前结构存在但基本为空。属性将在下一节详细讲解。

在写入数据前，可为新的数据集启用压缩，例如创建 `zpool_test/fds4` 并复制大量易压缩数据（如 Linux 内核源码）：

```bash
zfs create -o compression=on zpool_test/fds4
cp -a /usr/src/linux/* /zpool_test/fds4
ls -l /zpool_test/fds4
```

查看使用情况：

```bash
zfs get logicalreferenced,referenced,refcompressratio zpool_test/fds4
NAME             PROPERTY           VALUE     SOURCE
zpool_test/fds4  logicalreferenced  8.97G     -
zpool_test/fds4  referenced         4.58G     -
zpool_test/fds4  refcompressratio      2.13x  -
```

- `logicalreferenced`：逻辑数据量（未考虑压缩前的实际大小）
- `referenced`：物理存储实际占用大小

压缩开启时，`logicalreferenced` 通常大于 `referenced`。另一个验证方式：

```bash
du -sh /zpool_test/fds4
du -sh --apparent-size /zpool_test/fds4
4.7G    /zpool_test/fds4
8.5G    /zpool_test/fds4
```

### 销毁文件系统数据集（Destroying a 文件系统数据集）

基础知识掌握后，现在可以销毁 `zpool_test/fds4`：

```bash
zfs destroy zpool_test/fds4
```

>**警告**
>
>一旦销毁，数据集无法恢复，请确保有多份备份！

>**提示**
>
>只有“子”数据集可以被销毁。如果数据集有子数据集（如快照或其他文件系统数据集），可以使用递归选项：

```bash
zfs destroy -r zpool_test/fdsX
```

但**务必**先用 `-nv` 查看将被删除的内容：

```bash
zfs destroy -nv zpool_test/fdsX
```

### 文件系统数据集属性（Filesystem 数据集 properties）

与 zpool 一样，数据集也有属性。在文件系统数据集的情况下，属性分为两类：

1. **固有属性（intrinsic）**：无法修改，如创建时间、压缩比或剩余可用空间等。
2. **可设置属性**：可根据上下文需求进行调整。

数据集遵循层级结构，因此属性值会被继承：

- 子数据集继承父数据集的属性值，父数据集又继承自身父级的属性，以此类推直到根数据集。
- 根数据集部分属性会继承自所在的 zpool。
- 如果某个数据集在其层级中覆盖了某个属性值，这个值会向下传播给它下方的所有子数据集，直到另一个子数据集再次覆盖该属性。

查看数据集属性的逻辑类似 zpool：

```bash
zfs get all zpool_test/the/dataset
zfs get property zpool_test/the/dataset   # 查看单个属性
```

例如，查看根数据集：

```bash
zfs get all zpool_test
```

>**重要**
>
>这里不会讲解所有属性，只列举常用的。详细信息参考 [zfsprops(7)](https://openzfs.github.io/openzfs-docs/man/7/zfsprops.7.html)。

举例：属性 `type` 描述数据集的类型，本例中为 `filesystem`，可以确认数据集性质。

*SOURCE* 列说明属性来源：

- `defaults`：默认值，可修改
- `-`（短横线）：固有属性，不可修改

例如，数据集的创建时间、压缩比、剩余可用空间都是固有属性，无法更改。

接下来可重点关注一些固有属性，以便了解数据集基本情况。

| 属性                | 功能                                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------ |
| type              | 描述数据集类型。本例中为 *filesystem*，其他可能类型包括 *volume*、*snapshot* 等。                                                                |
| used              | 数据集当前在物理存储上的占用大小（包括所有子数据集），无论类型如何。目前数据集仅包含一些元数据（尚未存放文件），所以显示的数值很小。如果启用了压缩，*used* 的值可能小于 *logical*（`df` 也会显示相应结果）。        |
| logical           | 数据集当前的表观大小（“真实”大小，包括所有子数据集），无论类型如何。目前数据集仅包含一些元数据，显示值很小。如果启用了压缩，*logical* 可能大于 *used*（`df --apparent-size` 也会显示相应结果）。     |
| available         | 当前可用于存储数据的空间大小。如果数据集配置了多份副本或快照保留了大量数据，可用空间可能会快速减少。                                                                       |
| compressratio     | “真实”数据大小与物理存储大小的比率。未压缩数据集显示为 1，压缩数据集可能大于 1。例如，110MB 数据压缩后占用 100MB，则显示为 1.10X。压缩率高的数据集会显示更高的数值。                           |
| mounted           | 指示该文件系统数据集当前是否已挂载到 VFS 中（可通过 `mount` 命令查看）。                                                                              |
| referenced        | 数据集在 zpool 上可访问的数据量（物理大小）。当前数据集仅有元数据，数值与 *used* 类似。随着克隆和快照的出现，该值会变化。如果启用压缩，*referenced* 可能小于 *logicalreferenced*。        |
| logicalreferenced | 数据集在 zpool 上可访问的表观数据量（表观大小）。当前数据集仅有元数据，数值与 *used* 类似。随着克隆和快照的出现，该值会变化。如果启用压缩，*logicalreferenced* 可能大于 *referenced*。      |
| version           | 指示数据集使用的 ZFS 磁盘格式版本，而非数据集自身版本。十多年来，该值一直为 5，即使在 Solaris 11.4（2017 年 9 月退役）中亦是如此。未来若 ZFS 磁盘格式规范升级，版本号将递增。请勿与 zpool 旧版本号混淆。 |
| written           | 自上一个快照以来写入的数据量，即前一个数据集快照所引用的数据量。                                                                                         |

| 属性          | 可选值                                             | 功能                                                                                                                                                                                                             |
| ----------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| mountpoint  | path|legacy|none                                | 指定数据集的挂载点为 *path*。设置为 *none* 时，数据集将无法挂载。设置为 *legacy* 时，挂载信息会在 /etc/fstab 中查找，同时可使用传统的 mount 命令挂载数据集（`mount -t path/to/the/dataset /where/to/mount/it`）。这是最常修改的属性之一（与 *recordsize*、*quota* 和 *compression* 一起）。 |
| canmount    | yes|no                                          | 指定数据集是否可以挂载（`yes` 表示可挂载，`no` 表示不可挂载）。此属性可用于“隐藏”数据集而不改变其 *mountpoint* 属性的当前值。(`canmount=no` 等效于 `mountpoint=none`)。                                                                                             |
| quota       | quota_value|none                                | 设置数据集及其子数据集的最大空间使用量（参见 *refquota*）。例如，`zfs set quota=4G` 设置 4GB 的空间限制。值为 *none* 时表示无限制。ZFS 支持用户配额、组配额和项目配额。                                                                                                    |
| recordsize  | recordsize_size                                 | 指定文件块大小为 *recordsize_size*。此属性在数据库等对文件系统 I/O 对齐有严格要求的场景中非常有用。默认块大小为 128K。                                                                                                                                      |
| compression | on|off|lzjb|lz4|zle|gzip{,-N}|zstd{,-fast}{,-N} | 指定数据集内容是否启用实时压缩和解压。*off* 表示不压缩，*on* 表示使用默认压缩方法（lz4，如果 zpool 启用了 `feature@lz4_compress`，否则使用 lzjb）。*zstd* 需启用 `feature@zstd_compress`，gzip 和 zstd 可指定压缩等级。压缩/解压过程透明处理，可显著减少 I/O 操作，但消耗 CPU。                     |
| sharenfs    | on|off|nfsoptions                               | 通过 NFS 共享数据集（自动修改 /etc/exports 并调用 *exportfs*）。                                                                                                                                                                |
| sharesmb    | on|off|smboptions                               | 通过 Samba 共享数据集（自动修改 /etc/samba/smb.conf）。                                                                                                                                                                      |
| exec        | on|off                                          | 控制是否允许在数据集上执行程序以及加载共享库（.so 文件）。值为 `off` 相当于 `mount -o noexec ...`。                                                                                                                                             |
| setuid      | on|off                                          | 控制 SUID/SGID 位是否生效。值为 `off` 相当于 `mount -o nosuid ...`。                                                                                                                                                         |
| readonly    | on|off                                          | 控制文件系统是否只读（`on`）或可写（`off`）。                                                                                                                                                                                    |
| atime       | on|off                                          | 控制是否更新文件访问时间。若无需访问时间，可关闭以减少大量文件访问时的额外开销。                                                                                                                                                                       |
| xattr       | on|off|sa                                       | 控制是否启用扩展属性。默认 `on` 使用目录级属性，可能带来 I/O 开销；设置为 `sa` 可缓解开销。MDAC 系统如 SELinux 需启用扩展属性，POSIX ACL（Linux）同样需要。NFSv4（FreeBSD）不存储在扩展属性中。                                                                                   |
| encryption  | on|off|algorithm                                | 控制数据是否加密（`on`）或不加密（`off`）。默认使用 AES-256-GCM，亦可指定算法。zpool 必须启用 `feature@encrypted`，创建数据集时需提供 *keyformat*。加密时，ZFS 会加密数据及部分元数据，但 **不加密 zpool 结构**。可在后续更改密钥（如密钥泄露或其他原因）。详见 *zfs-load-key(8)*。                       |

>**提示**
>
>
>如果某属性会改变存储数据的状态（例如加密、压缩等），则该属性值的修改只会影响新添加或被修改的数据。如果属性值的修改不改变存储数据的状态（例如 NFS/SMB 共享、quota 等），则新属性值会立即生效。

首先，在根数据集上启用数据压缩并观察效果：

```bash
zfs get compression zpool_test
zfs get compression zpool_test/fds1
NAME             PROPERTY     VALUE           SOURCE
zpool_test/fds1  compression  on              inherited from zpool_test
```

下面是继承关系的概览：

```sh
NAME                               PROPERTY     VALUE           SOURCE
zpool_test                         compression  on   local
zpool_test/fds1                    compression  on   inherited from zpool_test
zpool_test/fds1/fds1_1             compression  on   inherited from zpool_test
zpool_test/fds1/fds1_1/fds1_1_1_1  compression  on   inherited from zpool_test/fds1/fds1_1
```

对于根数据集 zpool_test，`local` 表示这里覆盖了默认值。而 zpool_test/fds1 及其所有子数据集继承了该值，ZFS 会智能地显示继承来源。

将 `zpool_test/fds1/fds1_1` 的 compression 属性设置为 `off`：

```sh
NAME                               PROPERTY     VALUE           SOURCE
zpool_test                         compression  on   local
zpool_test/fds1                    compression  on   inherited from zpool_test
zpool_test/fds1/fds1_1             compression  off  local
zpool_test/fds1/fds1_1/fds1_1_1_1  compression  on   inherited from zpool_test/fds1/fds1_1
```

>**注意**
>
>这里出现了两个覆盖。

若要将某个层级及以下的数据集重置为继承属性，可以使用命令：

```bash
zfs inherit -r compression zpool_test/fds1
NAME                    PROPERTY     VALUE           SOURCE
zpool_test/fds1/fds1_1  compression  on              inherited from zpool_test
```

>**提示**
>
>此时 *SOURCE* 不再是 `local`，而是重新继承自父级。

另一个示例：设置使用配额。为 `zpool_test/fds1` 和 `zpool_test/fds1/fds1_1` 设置配额：

```bash
zfs set quota=5G zpool_test/fds1
zfs set quota=2G zpool_test/fds1/fds1_1
```

>**重要**
>
>`quota` 属性不仅定义了文件系统数据集及其子集的硬性空间限制，还包括快照保留的数据。如果只想限制“活跃”数据集的空间（不计快照），应使用 refquota 属性。

测试：在 zpool_test/fds1/fds1_1_1 下创建一个大于 2GB 的文件：

```bash
dd if=/dev/random of=/zpool_test/fds1/fds1_1/fds1_1_1/test1.dd bs=1G count=3
dd: error writing '/zpool_test/fds1/fds1_1/fds1_1_1/test1.dd': Disk quota exceeded
2+0 records in
1+0 records out
1073741824 bytes (1.1 GB, 1.0 GiB) copied, 3.51418 s, 306 MB/s
```

由于继承关系，zpool_test/fds1/fds1_1 **及** zpool_test/fds1/fds1_1/fds1_1_1 都受 2GB 配额限制。

调整配额，将 `zpool_test/fds1/fds1_1/fds1_1_1` 设置为无限制：

```bash
zfs set quota=none zpool_test/fds1/fds1_1/fds1_1_1
dd if=/dev/random of=/zpool_test/fds1/fds1_1/fds1_1_1/test1.dd bs=1G count=3
3+0 records in
3+0 records out
3221225472 bytes (3.2 GB, 3.0 GiB) copied, 5.39856 s, 597 MB/s
```

至此，本章节对创建与重命名文件系统数据集，以及属性设置与继承机制的介绍已完成。

释放空间以便下一节操作：

```bash
find /zpool_test -name '*.dd' -delete
```

#### 通过 NFS/CIFS 共享 ZFS 数据集

ZFS 文件系统数据集可以直接通过 NFS 和/或 SMBFS/CIFS 共享。没有什么魔法，ZFS 会在后台自动调整 `/etc/exports.d/zfs.exports`（NFS）和 `/etc/samba/smb.conf`（Samba）文件的内容，使管理员无需手动修改。要共享数据集，只需设置 `sharenfs` 和/或 `sharesmb` 属性为所需协议即可。两种协议可以同时使用，但要注意：如果文件在读写模式下被打开，NFS 和 SMBFS/CIFS 的锁机制不会互相感知。

首先创建一个共享文件系统数据集 `zpool_test/share_test` 并通过 NFS 共享：

```bash
zfs create -o sharenfs=on zpool_test/share_test
zfs get sharenfs zpool_test/share_test
NAME                   PROPERTY  VALUE     SOURCE
zpool_test/share_test  sharenfs  on        local
```

>**注意**
>
>属性 `SOURCE` 显示为 `local`，说明此层级覆盖了默认继承值。

在本机上，可以看到 `/etc/exports.d/zfs.exports` 已被添加了内容：

```sh
# !!! DO NOT EDIT THIS FILE MANUALLY !!!

/zpool_test/share_test *(sec=sys,rw,no_subtree_check,mountpoint,crossmnt)
```

列出本机向 NFS 客户端导出的共享：

```bash
showmount --exports 127.0.0.1
Export list for 127.0.0.1:
/zpool_test/share_test *
```

>**提示**
>
>可以传递 NFS 选项而不是仅使用 `on`，例如：

```bash
zfs set sharenfs=ro,no_root_squash zpool_test/share_test
```

参考 `exports(5)` 手册页了解更多选项。

如果文件系统数据集还要作为 CIFS/SMB Samba 共享可见，前提是系统上已有正常工作的 Samba 配置。确保至少在 `/etc/samba/smb.conf` 中设置如下参数，否则 ZFS 将静默失败：

```sh
# ZFS

usershare path = /var/lib/samba/usershares
usershare max shares = 100
```

同时确保 `/var/lib/samba/usershares` 目录存在，并且拥有合适的所有权（如 `root:root`）和权限（`01770`）。

```bash
zfs set sharesmb=on zpool_test/share_test
NAME                   PROPERTY  VALUE     SOURCE
zpool_test/share_test  sharesmb  on        local
```

>**警告**
>
>如果执行 `zfs set sharesmb=on` 报错 `SMB share creation failed`，请检查 `/var/lib/samba/usershares` 目录是否存在且权限正确。

定义共享后，ZFS 会在 `/var/lib/samba/usershares` 下添加一个与数据集同名的文件：

```bash
ls -l /var/lib/samba/usershares
total 6
-rw-r--r-- 1 root root 146 Jul  1 10:35 zpool_test_share_test
```

文件内容示例：

```ini
#VERSION 2
path=/zpool_test/share_test
comment=Comment: /zpool_test/share_test
usershare_acl=S-1-1-0:F
guest_ok=n
sharename=zpool_test_share_test
```

>**提示**
>
>可以通过委托（delegation）让普通用户创建并共享数据集，这是更高级的概念，本节不再深入。

当然，也可以不使用这些属性，通过手动编辑配置文件来定义 NFS 或 Samba 共享。但使用属性方式更方便，管理起来也更简洁。

#### Zvol 数据集

Zvol 只是 ZFS 上的一个模拟块设备，可以像任何其他块设备一样使用：可以用 `fdisk` 分区，然后在上面创建文件系统（如 ext4、xfs 等），再进行挂载。技术上甚至可以在 zvol 上创建另一个 zpool。

与文件系统数据集类似，zvol 也有一套可修改的属性。其真正的强大之处在于数据管理：与文件系统数据集一样，zvol 可以被快照，从而进行回滚或克隆。

创建 zvol 使用 `zfs create` 命令：

- 普通 zvol（空间全部预分配）：

```bash
zfs create -V <zvol_size> <zpool>/<zvol_name>
```

- 稀疏 zvol（薄分配）：

```bash
zfs create -s -V <zvol_size> <zpool>/<zvol_name>
```

示例：创建一个 1G 的 zvol `zpool_test/zvol1`（全部预分配），以及一个 2G 的稀疏 zvol `zpool_test/zvol2`：

```bash
zfs create -V 1G zpool_test/zvol1
zfs create -s -V 2G zpool_test/zvol2
zfs list -t all
NAME                                         USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                  1.37G  2.17G      128K  /zpool_test
zpool_test/zvol1                            1.37G  3.54G     74.6K  -
zpool_test/zvol2                            74.6K  2.17G     74.6K  -
```

>**注意**
>
>`USED` 列显示了实际占用空间。

**重要**
与文件系统数据集不同，zvol 不能嵌套 zvol，必须创建在文件系统数据集下。

可以使用“占位符”（不可挂载的文件系统数据集）来组织 zvol：

```bash
zfs create -V 1G zpool_test/VM/zvol1
zfs create -s -V 2G zpool_test/VM/zvol2
zfs list -t all
NAME                                         USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                  1.37G  2.17G      128K  /zpool_test
zpool_test/VM                               1.37G  2.17G      128K  none
zpool_test/VM/zvol1                         1.37G  3.54G     74.6K  -
zpool_test/VM/zvol2                         74.6K  2.17G     74.6K  -
```

无论 zvol 的组织方式如何，都会在 `/dev` 和 `/dev/zvol/<zpool_name>` 下创建多个块设备节点：

```bash
ls -l /dev/zvol/zpool_test/VM
total 0
lrwxrwxrwx 1 root root 12 May 18 09:05 zvol1 -> ../../../zd0
lrwxrwxrwx 1 root root 13 May 18 09:05 zvol2 -> ../../../zd16
```

对应的特殊设备节点为：

```bash
ls -l /dev/zd*
brw-rw---- 1 root disk 230,  0 May 18 09:05 /dev/zd0
brw-rw---- 1 root disk 230, 16 May 18 09:05 /dev/zd16
```

可以使用 `fdisk` 或 `parted` 查看分区信息：

```bash
parted /dev/zvol/zpool_test/VM/zvol1
GNU Parted 3.6
Using /dev/zd0
Welcome to GNU Parted! Type 'help' to view a list of commands.
(parted) p
Error: /dev/zd0: unrecognised disk label
Model: Unknown (unknown)
Disk /dev/zd0: 1074MB
Sector size (logical/physical): 512B/8192B
Partition Table: unknown
Disk Flags:
(parted)
```

**重要**
zvol 总是报告物理扇区大小为 512 字节，而逻辑扇区大小由属性 `volblocksize` 决定（OpenZFS 2.1 默认 8K）。`volblocksize` 类似于文件系统数据集中的 `blocksize`。有关性能调优详情，请参考官方 OpenZFS 文档的 [Workload Tuning/zvol-volblocksize](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#zvol-volblocksize)。

在 `parted` 中创建一个用于 ext4 文件系统的主分区，步骤如下：先创建 GPT（或 MSDOS）分区表，然后创建分区：

- `mklabel gpt`
- `mkpart primary ext4 2048s -1`
- `q`（退出 parted）

示例操作：

```sh
(parted) mklabel gpt
(parted) mkpart primary ext4 2048s -1
(parted) p
Model: Unknown (unknown)
Disk /dev/zd0: 1074MB
Sector size (logical/physical): 512B/8192B
Partition Table: gpt
Disk Flags:

Number  Start   End     Size    File system  Name     Flags
1      1049kB  1073MB  1072MB  ext4         primary
(parted) q
```

接下来像平常一样格式化新分区：

```bash
mkfs -t ext4 /dev/zd0p1
mke2fs 1.47.0 (5-Feb-2023)
Discarding device blocks: done
Creating filesystem with 261632 4k blocks and 65408 inodes
Filesystem UUID: 9c8ae6ae-780a-413b-a3f9-ab45d97fd8b8
Superblock backups stored on blocks:
32768, 98304, 163840, 229376

Allocating group tables: done
Writing inode tables: done
Creating journal (4096 blocks): done
Writing superblocks and filesystem accounting information: done
```

挂载到所需位置：

```bash
mkdir /mnt/ext4test
mount -t ext4 /dev/zd0p1 /mnt/ext4test
df -h | grep ext4test
/dev/zd0p1                         988M   24K  921M   1% /mnt/ext4test
```

#### ZFS 快照（及回滚数据集）

就像关系型数据库可以在精确时间点进行备份和恢复一样，ZFS 数据集的状态也可以被“拍照”，然后恢复，就好像自快照创建以来什么都没发生过一样。这种功能并非 ZFS 独有：BTRFS 和 NILFS2 也提供类似功能，LVM 也支持快照。Copy-on-Write 文件系统（如 ZFS、BTRFS 或 NILFS2）中的快照与 LVM 快照的主要区别在于无需预先设定大小。这不会因数据变化过多而失效，而且可以拥有几乎无限数量的快照，每个快照仅保存与前一个快照的差异。因此，如果两个快照之间没有变化，实际占用空间仅为少量元数据（几 KB 的量级）。

**重要**
与 BTRFS 快照不同，ZFS 快照是只读的。ZFS 有可写快照的概念，称为克隆（clone），稍后会详细介绍。

创建快照使用 ZFS 命令 `zfs snapshot`，后跟快照名称，遵循格式：`zpool/the/dataset/to/be/snaphotted@snapshotname`。快照名称可以是任意字母数字序列，例如 `mysnap`、`20221214` 或 `test123` 都是有效的。唯一需要遵守的规则是使用 `@` 字符作为数据集名称与快照名称的分隔符。

>**警告**
>
>只有文件系统数据集和 zvol 可以创建快照。无法对快照或书签进行快照操作。

一旦快照创建完成，无需执行其他操作。ZFS 会在幕后透明地管理差异。只要快照未被销毁，所有变更历史都会被保留，无论是新增、删除还是修改数据。一旦快照被销毁，ZFS 会检查数据集的快照时间线，并释放不再被引用的块。

快照的配额管理可能比较棘手：如果一个文件系统包含大量小文件，但快照之间发生了大量变化，快照时间线的总大小可能会很大，即使当前数据集状态远低于阈值，配额限制也可能很快达到。若仅有少量大文件在快照间发生变化，情况也类似。

好吧，我们来演示一下。首先创建一个新的数据集并复制一些文件进去：

```sh
zfs create zpool_test/testfsds1
cp -r /usr/src/linux/drivers/* /zpool_test/testfsds1
df -h
Filesystem                         Size  Used Avail Use% Mounted on
zpool_test                         433M  256K  433M   1% /zpool_test
zpool_test/testfsds1               5.0G  4.6G  433M  92% /zpool_test/testfsds1
```

此时没有什么特别需要说明的，只注意根数据集的已用大小与 `zpool_test/testfsds1` 的大小相同（433M）。由于根数据集仅包含少量元数据而没有文件，它只占用几个 KB。

现在我们创建第一个名为 `snap1` 的快照：

```sh
zfs snapshot zpool_test/testfsds1@snap1
zfs list -t all
NAME                         USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.50G   433M      151K  /zpool_test
zpool_test/testfsds1                               4.50G   433M     4.50G  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                            0B      -     4.50G  -
```

乍一看，快照使用了 0 字节（USED 显示 `0`），因为数据没有变化。换句话说，文件系统数据集`zpool_test/testfsds1` 与其快照 `zpool_test/testfsds1@snap1` 指向完全相同的数据块。

换一个角度来看：

*文件系统数据集 `zpool_test/testfsds1` 的大小（USED 列）为 4.50G。
*文件系统数据集 `zpool_test/testfsds1` 引用的数据量（REFER 列）也是 4.50G。在此时 USED 和 REFER 两列显示相同的值，这是完全正常的。
- 快照也引用完全相同的 4.50G 数据，因此它的大小为零（快照看到的数据与文件系统数据集 看到的完全相同，因此两者差异为零）。

还记得之前看到的 `zfs get` 命令吗？我们在快照上查看：

```sh
zfs get all zpool_test/testfsds1@snap1
```

不用解释每个属性，最重要的是：

- type：这是一个 snapshot（dataset），类型自然显示为 `snapshot`
- creation：快照创建的日期/时间
- used：几乎为零，因为快照和对应的文件系统数据集 指向相同内容（8.24M 为快照元数据）
- referenced：前面看到的同样值 4.50G（如上解释）
- createtxg：快照创建时所在的事务组（TXG）编号（TXG 编号随时间递增）。这有助于追溯某个文件系统数据集 的快照创建顺序，以便应对命名不一致的情况（例如 `zpool_test/testfsds1@snap1`、`zpool_test/testfsds1@mytest`、`zpool_test/testfsds1@bug412` 等）。

现在快照已存在，我们准备删除一些文件，但首先确定要删除的数据量：

```sh
du -csh /zpool_test/testfsds1/{a,b,c}*
```

然后删除这些文件并创建第二个快照：

```sh
rm -rf /zpool_test/testfsds1/{a,b,c}*
zfs snap zpool_test/testfsds1@snap2
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.51G   432M      151K  /zpool_test
zpool_test/testfsds1                               4.50G   432M     4.20G  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                          307M      -     4.50G  -
zpool_test/testfsds1@snap2                            0B      -     4.20G  -
```

乍一看，`zpool_test/testfsds1@snap1` 的快照大小大约从 0 字节增加到删除数据的大小。换句话说：

- `zpool_test/testfsds1@snap2` 与当前 `zpool_test/testfsds1` 状态无差异，因此 USED 为 0。该快照引用的数据量为 4.20G（4.50G-307M ≈ 4.20G），即 REFER 列显示的值。
- 自 `zpool_test/testfsds1` 创建以来删除了 307M 数据，因此 `zpool_test/testfsds1@snap1` 与 `zpool_test/testfsds1@snap2` 的差异也是 307M（ZFS 与 `df` 的计算略有差异）。
- `zpool_test/testfsds1` 删除前的原始大小为 4.50G，因此 `zpool_test/testfsds1@snap1` 仍显示原始状态，REFER 列为 4.50G。

进一步操作前，一个（神奇的）技巧：虽然快照显示为不可挂载（MOUNTPOINT 列为 `-`），但可以在 `/zpool_test/testfsds1/.zfs/snapshot/snap1` 下以只读方式访问其内容（快照不可写）：


```sh
ls -l /zpool_test/testfsds1/.zfs/snapshot
total 0
drwxrwxrwx 1 root root 0 Jul  1 17:52 snap1
drwxrwxrwx 1 root root 0 Jul  1 18:15 snap2
```

```sh
ls -l /zpool_test/testfsds1/.zfs/snapshot/snap1
```

可以看到快照创建后被 `rm -rf {a,b,c}*` 删除的文件和目录。这样就可以在快照创建的精确时间点复制或检查文件，非常有用来恢复被修改或删除的文件。

检查第二个快照时，由于在创建 `zpool_test/testfsds1@snap2` 前删除了文件，所以没有文件或目录以“a”、“b”、“c”开头：

```sh
ls -l /zpool_test/testfsds1/.zfs/snapshot/snap2
```

很好，但还不够方便。如果能直接知道两个快照之间的精确差异，而不是手动检查每个文件，就更便捷了。幸运的是，ZFS 提供了解决方案，可以对快照进行 *diff*（输出已截断）：

```sh
zfs diff zpool_test/testfsds1@snap1 zpool_test/testfsds1@snap2 | sort
```

命令显示：所有以“a”、“b”、“c”开头的文件和目录已被删除（注意左边的 `-`），因此 `/zpool_test/testfsds1` 路径发生了变化（注意最后一行左边的 `M`）。

此时，我们进一步删除更多文件并再次创建快照 (`zpool_test/testfsds1@snap3`)：

```sh
find -name Makefile -delete
zfs snap zpool_test/testfsds1@snap3
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.53G   410M      151K  /zpool_test
zpool_test/testfsds1                               4.53G   410M     4.19G  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                          307M      -     4.50G  -
zpool_test/testfsds1@snap2                          186K      -     4.20G  -
zpool_test/testfsds1@snap3                            0B      -     4.19G  -
```

注意：

1. 由于 `zpool_test/testfsds1@snap3` 反映当前 `zpool_test/testfsds1` 状态，其大小为零（或仅有可忽略的元数据），*相对于*当前数据集状态。
2. `zpool_test/testfsds1@snap2` 相对于 `zpool_test/testfsds1@snap3` 的差异对应删除的 Makefile（186K，包括元数据）。
3. `zpool_test/testfsds1@snap2` 相对于 `zpool_test/testfsds1@snap1` 的大小保持不变（307M）。

再次使用 `zfs diff`（中间 `grep` 清理列表）：

```sh
zfs diff zpool_test/testfsds1@snap2 zpool_test/testfsds1@snap3 | grep -v '^M' | sort
```

>**提示**
>
>非连续的快照也可以进行 *diff*。试试：`zfs diff zpool_test/testfsds1@snap1 zpool_test/testfsds1@snap3` 并观察结果。

现在，删除 `/zpool_test/testfsds1` 下的所有内容，并观察每个快照大小的变化：

```sh
rm -rf /zpool_test/testfsds1/*
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.53G   406M      151K  /zpool_test
zpool_test/testfsds1                               4.53G   406M     12.2M  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                          307M      -     4.50G  -
zpool_test/testfsds1@snap2                          186K      -     4.20G  -
zpool_test/testfsds1@snap3                         22.0M      -     4.19G  -
```

于是：

```sh
ls -la /zpool_test/testfsds1
total 1
drwxr-xr-x 2 root root 2 Jul  1 19:04 .
drwxr-xr-x 3 root root 3 Jul  1 17:47 ..
```

哎呀……空目录！

恢复删除前内容的一种方式是复制 `/zpool_test/testfsds1/.zfs/snapshot/snap3` 下的内容，但这样会重复数据块（在 OpenZFS 2.2 及其块克隆功能下可能不是这样），总之这是一种不优雅的数据恢复方式。此时更合适的方法是回滚。

回滚会将数据集的状态恢复到某个快照的状态。若要将 `zpool_test/testfsds1` 恢复到 `zpool_test/testfsds1@snap3` 快照创建时的状态，可使用命令 `zfs rollback`：

```sh
zfs rollback zpool_test/testfsds1@snap3
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.53G   410M      151K  /zpool_test
zpool_test/testfsds1                               4.53G   410M     4.19G  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                          307M      -     4.50G  -
zpool_test/testfsds1@snap2                          186K      -     4.20G  -
zpool_test/testfsds1@snap3                            0B      -     4.19G  -
```

**瞧！** 注意 `zpool_test/testfsds1@snap3` 相对于 `zpool_test/testfsds1` 的大小：由于数据集已回滚，二者“看到”的内容相同，因此差异为 0 字节。列出 `/zpool_test/testfsds1` 也会再次显示文件。

```sh
ls -la /zpool_test/testfsds1
```

**"是否可以回滚到更早的快照？"** 答案是：可以。

回到 `zpool_test/testfsds1@snap1` 看似像前面演示的操作一样简单，但这次会有额外的提示：

```sh
zfs rollback zpool_test/testfsds1@snap1
cannot rollback to 'zpool_test/testfsds1@snap1': more recent snapshots or bookmarks exist
use '-r' to force deletion of the following snapshots and bookmarks:
zpool_test/testfsds1@snap2
zpool_test/testfsds1@snap3
```

ZFS 会智能地提示操作影响：如果在此回滚，`zpool_test/testfsds1@snap2` 和 `zpool_test/testfsds1@snap3` 将失去意义，需要被销毁。继续操作：

```sh
zfs rollback -r zpool_test/testfsds1@snap1
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.50G   432M      151K  /zpool_test
zpool_test/testfsds1                               4.50G   432M     4.50G  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                            0B      -     4.50G  -
```

回到本节开始时的状态！

最后，`zpool_test/testfsds1@snap1` 可以通过 `zfs destroy` 命令销毁，就像文件系统数据集或 zvolume 一样：

```sh
zfs destroy zpool_test/testfsds1@snap1
zfs list
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.50G   432M      151K  /zpool_test
zpool_test/testfsds1                               4.50G   432M     4.50G  /zpool_test/testfsds1
```

>**注意**
>
>如果存在后续快照，ZFS 会要求显式使用 `-r`，就像前面回滚到第一个快照的示例中一样。

#### 关于 ZFS 快照的重要注意事项

在继续之前，关于快照还有一些重要注意事项：

- 对 zvolumes 快照的操作遵循完全相同的思路，此处不再演示。
- 在回滚数据集之前：
  - 确保对应的文件系统数据集 上没有打开的文件
  - 对于 zvolume，确保它已先卸载
- 完全可以销毁中间快照，而不仅仅是最新的快照：在这种情况下，ZFS 会判断并释放所有剩余快照（以及对应的文件系统数据集）中不再被引用的数据块。zvolumes 快照亦同理。
- 在快照被销毁后，除非通过备份进行 `zfs send/receive`，否则无法恢复该快照。

>**警告**
>
>在对底层数据集使用 `zfs send/receive` 后，不要删除中间快照。ZFS 会检测到接收端存在异常，并会直接拒绝传输。可以在不破坏 `zfs send/receive` 的前提下，在发送端销毁不再使用的快照的方法是：使用书签（bookmarks），将在后文讨论。

#### ZFS 克隆

ZFS 克隆是 ZFS 快照的延续。在 ZFS 的世界中，快照是不可变对象，只能读取。不过，有一种方法可以获得可写的快照：那就是 ZFS 克隆。

直观地说，克隆是从快照派生出来的可写快照。克隆的创建方式也遵循这一思路。

首先，重新为上一节中用于快照管理的测试文件系统数据集 创建一个快照，因为在上节结束时它已被销毁：

```sh
zfs snap zpool_test/testfsds1@snap1
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.50G   432M      151K  /zpool_test
zpool_test/testfsds1                               4.50G   432M     4.50G  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                            0B      -     4.50G  -
```

看到 0 字节快照在此不应感到新奇或意外。同样不应感到意外的是，快照无法被挂载（尽管可以通过伪文件系统 `/zpool_test/testfsds1/.zfs/snapshot/snap1` 访问）也无法被修改：

```sh
touch /zpool_test/testfsds1/.zfs/snapshot/snap1/helloworld
touch: cannot touch '/zpool_test/testfsds1/.zfs/snapshot/snap1/helloworld': Read-only file system
```

可以使用以下命令为该快照创建克隆：

```sh
zfs clone zpool_test/testfsds1@snap1 zpool_test/testfsds1_clone
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.50G   432M      151K  /zpool_test
zpool_test/testfsds1                               4.50G   432M     4.50G  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                          163K      -     4.50G  -
zpool_test/testfsds1_clone                            0B   432M     4.50G  /zpool_test/testfsds1_clone
```

注意 `zpool_test/testfsds1@snap1` 的轻微大小变化，这是由于克隆创建所需的一些额外元数据，以及挂载点的定义所致。这里没有什么新奇之处。

接下来查看创建结果，这里不对所有属性都进行注释：

```sh
zfs get all zpool_test/testfsds1_clone
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
NAME                        PROPERTY              VALUE                        SOURCE
zpool_test/testfsds1_clone  type                  filesystem                   -
zpool_test/testfsds1_clone  creation              Sat Jul  1 20:44 2023        -
zpool_test/testfsds1_clone  used                  0B                           -
zpool_test/testfsds1_clone  available             432M                         -
zpool_test/testfsds1_clone  referenced            4.50G                        -
zpool_test/testfsds1_clone  compressratio         1.00x                        -
zpool_test/testfsds1_clone  mounted               yes                          -
zpool_test/testfsds1_clone  origin                zpool_test/testfsds1@snap1   -
(...)
```

将 `clone` 作为 type 是错误的！虽然它本质上是克隆，但在行为上与普通文件系统数据集 完全一致，ZFS 也将其视为普通文件系统数据集。因此看到 type 为 `filesystem` 是完全正常的。

那么如何区分克隆和普通文件系统数据集 呢？查看属性 `origin` 的设置：它指向克隆所派生的快照。作为对比，查看 `zpool_test/testfsds1` 的 origin 设置：

```sh
zfs get type,origin zpool_test/testfsds1
NAME                        PROPERTY  VALUE                       SOURCE
zpool_test/testfsds1  type      filesystem  -
zpool_test/testfsds1  origin    -           -
(...)
```

一个破折号（`-`）！也就是没有任何来源。

`zpool_test/testfsds1` 是独立的文件系统数据集，而 `zpool_test/testfsds1@snap1` 与 `zpool_test/testfsds1_clone` 之间存在父子关系。由于这种关系，除非先销毁 `zpool_test/testfsds1_clone`（及其可能存在的所有快照），否则无法销毁 `zpool_test/testfsds1@snap1` 或 `zpool_test/testfsds1`。

此时的结构可以用下图总结：

![ZFS 克隆工作流 1.png](.gitbook/assets/ZFS_clone_flow_1.png)

由于克隆是可写的，为什么不向其中添加一些内容呢？

```sh
dd if=/dev/random of=/zpool_test/testfsds1_clone/test.dd bs=1M count=20
20+0 records in
20+0 records out
20971520 bytes (21 MB, 20 MiB) copied, 0.0316403 s, 663 MB/s
```

```sh
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.52G   412M      163K  /zpool_test
zpool_test/testfsds1                               4.50G   412M     4.50G  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                          163K      -     4.50G  -
zpool_test/testfsds1_clone                         20.2M   412M     4.52G  /zpool_test/testfsds1_clone
```

可以看到大小变化约为 20MB。由于克隆现在独立存在，新增的数据不会影响其派生的快照大小。

接下来尝试销毁克隆派生的快照：

```sh
zfs destroy zpool_test/testfsds1@snap1
cannot destroy 'zpool_test/testfsds1@snap1': snapshot has dependent clones
use '-R' to destroy the following datasets:
zpool_test/testfsds1_clone
```

由于克隆与其源文件系统数据集 之间存在父子关系，ZFS 无法直接删除该快照。有几种方式可以解决：

- 方案一：打破克隆与其父快照的关系，使它们各自成为独立的 ZFS 实体。这需要：

  - 使用 `zfs send` 对 `zpool_test/testfsds1_clone` 做完整备份
  - 销毁 `zpool_test/testfsds1_clone`
  - 使用 `zfs receive` 从备份恢复 `zpool_test/testfsds1_clone`
- 方案二：反转父子关系，使 `zpool_test/testfsds1_clone` 成为 `zpool_test/testfsds1@snap1` 的父级

方案一在此无太大意义，因为会重复数据块而不是仅使用引用。因此选择方案二，并引入新的 ZFS 命令来操作克隆：`zfs promote`。该命令正如其名：将克隆“提升”（promote）为原父级的父对象，换句话说：“原本的子对象成为父对象，原本的父对象成为子对象”。

```sh
zfs promote
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.52G   412M      163K  /zpool_test
zpool_test/testfsds1                                163K   412M     4.50G  /zpool_test/testfsds1
zpool_test/testfsds1_clone                         4.52G   412M     4.52G  /zpool_test/testfsds1_clone
zpool_test/testfsds1_clone@snap1                    174K      -     4.50G  -
```

注意变化了吗？一切被“颠倒”了，现在就像 `zpool_test/testfsds1_clone` 最初被创建，然后快照为 `zpool_test/testfsds1_clone@snap1`，再克隆出 `zpool_test/testfsds1`。重新整理后，组织结构如下：

1. 克隆 `zpool_test/testfsds1_clone` 现在承担了原 `zpool_test/testfsds1` 的责任，所以其大小为 4.50GB（原 `zpool_test/testfsds1` 的大小）加上刚添加的 20MB，总计 4.52GB
2. 快照 `zpool_test/testfsds1@snap1` 已从 `zpool_test/testfsds1` “迁移”到 `zpool_test/testfsds1_clone`，并且成为 `zpool_test/testfsds1` 的父对象

查看类型和来源：

```sh
zfs get type,origin zpool_test/testfsds1_clone zpool_test/testfsds1 zpool_test/testfsds1_clone@snap1
NAME                              PROPERTY  VALUE                             SOURCE
zpool_test/testfsds1              type      filesystem                        -
zpool_test/testfsds1              origin    zpool_test/testfsds1_clone@snap1  -
zpool_test/testfsds1_clone        type      filesystem                        -
zpool_test/testfsds1_clone        origin    -                                 -
zpool_test/testfsds1_clone@snap1  type      snapshot                          -
zpool_test/testfsds1_clone@snap1  origin    -                                 -                         -
```

这一结构同样可以通过下图示意说明：

![ZFS 克隆工作流 2.png](.gitbook/assets/ZFS_clone_flow_2.png)

尽管由于克隆提升导致了层级关系发生变化，但所有这些实体本身依然完全相同。两个 ZFS 实体在生命周期上保留了相互的链接，并且可以各自拥有独立快照。

为了演示：如果删除 `/zpool_test/testfsds1_clone/test.dd` 会发生什么？为了验证，我们先对 `zpool_test/testfsds1_clone` 再创建一个快照，然后删除该文件：

```sh
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.52G   412M      163K  /zpool_test
zpool_test/testfsds1                                163K   412M     4.50G  /zpool_test/testfsds1
zpool_test/testfsds1_clone                         4.52G   412M     4.52G  /zpool_test/testfsds1_clone
zpool_test/testfsds1_clone@snap1                    174K      -     4.50G  -
zpool_test/testfsds1_clone@snap2                      0B      -     4.52G  -
```

解释起来有些复杂，但可以这样理解：由于 `/zpool_test/testfsds1_clone/test.dd` 仍被 `zpool_test/testfsds1_clone@snap2` 引用，其数据块依然保留（因此该快照显示 4.52GB）。而在 `zpool_test/testfsds1_clone@snap1`（原 `zpool_test/testfsds1@snap1`）中，该文件不存在，因此显示 4.50GB。演示中将 `zpool_test/testfsds1` 的内容设置为 `zpool_test/testfsds1_clone` 的子集，因此 ZFS 只需少量元数据即可标识各实体的内容。

另一个满分的问题：**"是否可以恢复到原始状态？"**（或换句话说：**"能提升 `zpool_test/testfsds1` 吗？"**）。首先回滚，销毁 `zpool_test/testfsds1_clone@snap2`：

```sh
zfs rollback zpool_test/testfsds1_clone@snap2
zfs destroy zpool_test/testfsds1_clone@snap2
zfs promote zpool_test/testfsds1
zfs list -t all
NAME                                                USED  AVAIL     REFER  MOUNTPOINT
zpool_test                                         4.52G   412M      163K  /zpool_test
zpool_test/testfsds1                               4.50G   412M     4.50G  /zpool_test/testfsds1
zpool_test/testfsds1@snap1                          163K      -     4.50G  -
zpool_test/testfsds1_clone                         20.2M   412M     4.52G  /zpool_test/testfsds1_clone
```

**瞧！** 恢复到原始状态了！观察父子关系：

```sh
zfs get type,origin zpool_test/testfsds1_clone zpool_test/testfsds1 zpool_test/testfsds1@snap1
zfs list -t all
NAME                        PROPERTY  VALUE                       SOURCE
zpool_test/testfsds1        type      filesystem                  -
zpool_test/testfsds1        origin    -                           -
zpool_test/testfsds1@snap1  type      snapshot                    -
zpool_test/testfsds1@snap1  origin    -                           -
zpool_test/testfsds1_clone  type      filesystem                  -
zpool_test/testfsds1_clone  origin    zpool_test/testfsds1@snap1  -
```

在 Gentoo 环境中，快照的典型用法是实验性地测试 **"如果发生这种情况会怎样？"**：克隆生产环境的文件系统数据集，然后挂载所需内容（就像克隆的是未压缩的 Gentoo stage 3 tarball），再 `chroot` 进入其中，提供一个可随意操作的测试环境。克隆避免了来回复制数百 GB 数据占满本地磁盘空间（ZFS 若直接复制而非克隆，将会复制所有数据块）。由于性能影响，ZFS 去重通常未被广泛使用。

作为文件系统数据集，可以使用已知命令销毁克隆：

```sh
zfs destroy zpool_test/testfsds1_clone
```

### 维护

#### scrub（数据校验）

要对 zpool *zfs_test* 启动一次 scrub：

```sh
zpool scrub zfs_test
```

>**注意**
>
>这可能需要一些时间，并且对 I/O 的压力较大。ZFS 会尽量减小对系统整体的影响，但有时系统即便是最低优先级的 I/O 也无法很好处理。

#### 监控 I/O

监控所有 zpool 的 I/O 活动（每 6 秒刷新一次）：

```sh
zpool iostat 6
```

### 技术细节

#### ARC

OpenZFS 使用 [ARC](https://en.wikipedia.org/wiki/Adaptive_replacement_cache "wikipedia:Adaptive replacement cache")（自适应替换缓存）页面替换算法，而不是其他文件系统使用的最近最少使用（LRU）算法。ARC 命中率更高，因此提供了更好的性能。ZFS 中 ARC 的实现与原论文有所不同：作为缓存使用的内存量是可变的。将能在系统内存紧张时通过内核的 shrinker 机制回收 ARC 内存，并在系统有空闲内存时扩展。ARC 分配的最小和最大内存量随系统内存而异。默认最小值为总内存的 1/32 或 64MB（取较大者），默认最大值为系统内存的 1/2 或 64MB（取较大者）。

Linux 对 ARC 使用的内存计量方式与页缓存不同。具体来说，ARC 使用的内存显示在 `free` 输出中的“used”项下，而非“cached”。这并不妨碍系统在内存不足时释放这些内存，但可能让人误以为 ARC（及 ZFS）会尽可能使用全部系统内存。

#### 调整 ARC 内存占用

可分别通过 `zfs_arc_min` 和 `zfs_arc_max` 调整 ARC 的最小和最大内存使用量，有三种设置方式。第一种是在运行时设置（0.6.2 版本新增）：

```sh
echo 536870912 >> /sys/module/zfs/parameters/zfs_arc_max
```

>**注意**
>
>此 sysfs 值从 ZFSOnLinux 0.6.2 开始可写。通过 sysfs 设置不会在重启后保留。如果未手动配置，该值在 sysfs 中为 `0`。可通过查看 `/proc/spl/kstat/zfs/arcstats` 中的 `c_max` 得知当前设置。

第二种是通过 `/etc/modprobe.d/zfs.conf` 进行设置：

```sh
echo "options zfs zfs_arc_max=536870912" >> /etc/modprobe.d/zfs.conf
```

>**注意**
>
>如果使用 genkernel 加载 ZFS，必须在运行 genkernel 之前设置此值，以确保文件被复制到 initramfs。

第三种是在内核命令行上指定：

`zfs.zfs_arc_max=536870912`（对应 512MB）。同样方法还可调整 `zfs_arc_min`。

## ZFS 根文件系统

本文为 [stub](https://wiki.gentoo.org/wiki/Category:Stub "Category:Stub")。请帮助 [扩展内容](https://wiki.gentoo.org/index.php?title=ZFS&action=edit) - [入门指南](https://wiki.gentoo.org/wiki/Gentoo_Wiki:Contributor%27s_guide "Gentoo Wiki:Contributor's guide")。

要从 ZFS 文件系统启动为根文件系统，需要一个支持 ZFS 的 [内核](https://wiki.gentoo.org/wiki/ZFS#Kernel "ZFS") 和包含 ZFS 用户空间工具的初始 ramdisk（initramfs）。最简单的设置方法如下。

### 引导加载器

[GRUB](https://wiki.gentoo.org/wiki/GRUB "GRUB") 应在编译时启用 USE 标志 libzfs，以便从 ZFS 数据集中启动系统：

```sh
echo "sys-boot/grub libzfs" > /etc/portage/package.use/grub
emerge -av grub
```

### 准备磁盘

虽然较新的 [GRUB](https://wiki.gentoo.org/wiki/GRUB "GRUB") 可以直接从 ZFS 存储池启动（即 `/boot` 位于 ZFS 上），但在维护 ZFS 本身时存在一些严重限制。此外，不建议将 swap 分区放在 ZFS 中，因为这可能导致死锁 <https://wiki.gentoo.org/wiki/ZFS#cite_note-4)>。总体而言，推荐使用 [Handbook 的默认分区方案](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/Disks#Default_partitioning_scheme "Handbook:AMD64/Installation/Disks")（boot 和 swap 分区，其余空间用于 zpool）：

| 分区        | 意义               | 文件系统           |
| --------- | ---------------- | -------------- |
| /dev/sda1 | EFI 系统（及 boot）分区 | FAT32          |
| /dev/sda2 | swap 分区          | swap           |
| /dev/sda3 | ZFS              | 根 ZFS pool 的空间 |

按照 [Handbook 指南](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/Disks#Partitioning_the_disk_with_GPT_for_UEFI "Handbook:AMD64/Installation/Disks") 创建分区。准备好磁盘后，格式化 boot 分区并启用 swap，然后创建 ZFS 根数据集。OpenZFS 推荐使用唯一存储标识符（WWN）而非系统设备名。可通过运行以下命令获取 WWN：

```sh
lsblk -o name,wwn
NAME                 WWN
sda                  0x50014ee2b3b4d492
├─sda1               0x50014ee2b3b4d492
├─sda2               0x50014ee2b3b4d492
├─sda3               0x50014ee2b3b4d492
```

>**注意**
>
>WWN 仅适用于 SATA/SAS 硬盘，NVMe 设备使用不同的命名，形如 `eui.6479a776500000b8`。

`/dev/sda3` 的完整名称为 `/dev/disks/by-id/wwn-0x50014ee2b3b4d492-part3`。创建 ZFS 存储池 rpool：

```sh
zpool create -o cachefile=/etc/zfs/zpool.cache \
             -o ashift=12 \
             -o autotrim=on \
             -O acltype=posixacl \
             -O xattr=sa \
             -O dnodesize=auto \
             -O compression=lz4 \
             -O normalization=formD \
             -O relatime=on \
             -O canmount=off \
             -R /mnt/gentoo rpool /dev/disks/by-id/wwn-0x50014ee2b3b4d492-part3
```

>**注意**
>
>可参考 [OpenZFS 文档](https://openzfs.github.io/openzfs-docs/Getting%20Started/Ubuntu/Ubuntu%2022.04%20Root%20on%20ZFS.html#step-2-disk-formatting) 获得各参数的含义。

现在创建 ZFS 数据集：

```sh
zfs create -o canmount=off -o mountpoint=none rpool/ROOT
zfs create -o canmount=noauto -o mountpoint=/ rpool/ROOT/gentoo
zfs mount rpool/ROOT/gentoo
```

接下来创建一些可选的数据集（例如用于 `/home` 和 `var/log`）：

```sh
zfs create rpool/home
zfs create -o canmount=off rpool/var
zfs create rpool/var/log
...
```

至此，ZFS 设置完成，目前新的根文件系统挂载在 `/mnt/gentoo`。最后一步是复制 `zpool.cache`：

```sh
mkdir -p /mnt/gentoo/etc/zfs
cp /etc/zfs/zpool.cache /mnt/gentoo/etc/zfs/
```

对于新系统，请按照 [Gentoo Handbook 安装指南](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/Stage "Handbook:AMD64/Installation/Stage") 操作至 [Linux 内核配置](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/Kernel "Handbook:AMD64/Installation/Kernel")。下一章将提供内核所需的额外配置。

### 配置内核

#### 发行版内核

在 chroot 后准备发行版内核。

文件 **/etc/portage/package.use**

```sh
# 安装 initramfs

sys-kernel/gentoo-kernel initramfs

# 确保 ZFS 在内核升级时重新编译

sys-fs/zfs-kmod dist-kernel
```

安装内核：

```sh
emerge --ask sys-kernel/gentoo-kernel
```

[Dracut](https://wiki.gentoo.org/wiki/Dracut "Dracut") 会自动检测根文件系统上的 ZFS，并将必要模块添加到 initramfs 中。

#### Genkernel

在 chroot 环境下使用 [genkernel](https://wiki.gentoo.org/wiki/Genkernel "Genkernel") 时，为了在 initrd 中嵌入 `/etc/hostid`，先生成 `/etc/hostid`：

```sh
zgenhostid
```

在 `/etc/genkernel.conf` 中启用 `ZFS="yes"`：

文件 **/etc/genkernel.conf**

```sh
# ...

# 包含对 zfs 卷管理的支持。如果未设置，genkernel 将尝试自动检测并在根文件系统位于 ZFS 时启用。

ZFS="yes"

# ...
```

随后重新生成 initramfs（并编译内核本身）：

```sh
genkernel all
```

配置 GRUB 使用 ZFS 并指定启动的数据集：

文件 **/etc/default/grub**（指定 root 设备）

```sh
GRUB_CMDLINE_LINUX="dozfs root=ZFS=rpool/ROOT/gentoo"
```

最后生成 `grub.cfg`：

```sh
grub-mkconfig -o /boot/grub/grub.cfg
```

### 完成安装

如果希望避免再次导出和导入 ZFS 存储池，可在内核命令行使用 `"zfs_force=1"`：

```sh
zpool export rpool
zpool import -d /dev/disk/by-id -R /mnt/gentoo rpool -N
```

别忘了将 zfs-import 和 zfs-mount 服务添加到启动运行等级：

```sh
rc-update add zfs-import boot
rc-update add zfs-mount boot
```

### Chroot 环境

在 LiveCD 或其他系统中修复 ZFS，请参照 [openzfs #1078](https://github.com/openzfs/zfs/issues/1078#issuecomment-984056749)：

```sh
zpool import -f -N rpool
```

如果 ZFS 文件系统已加密，则导入密钥：

```sh
zfs load-key -a
```

然后挂载文件系统：

```sh
mount -t zfs -o zfsutil rpool/ROOT/gentoo /mnt/gentoo
arch-chroot /mnt/gentoo
zfs mount -a
```

## 注意事项

- 加密：原生加密（即不使用 LUKS）在 ZFS 中存在非常多的 Bug 记载。截至 2023 年 7 月，ZFS 的加密模块没有活跃维护者，Gentoo 社区非官方地不推荐使用。部分示例 Bug 如下：

  - [https://github.com/openzfs/zfs/issues/6793](https://github.com/openzfs/zfs/issues/6793)
  - [https://github.com/openzfs/zfs/issues/11688](https://github.com/openzfs/zfs/issues/11688)
  - [https://github.com/openzfs/zfs/issues/12014](https://github.com/openzfs/zfs/issues/12014)
  - [https://github.com/openzfs/zfs/issues/12732](https://github.com/openzfs/zfs/issues/12732)
  - [https://github.com/openzfs/zfs/issues/13445](https://github.com/openzfs/zfs/issues/13445)
  - [https://github.com/openzfs/zfs/issues/13709](https://github.com/openzfs/zfs/issues/13709)
  - [https://github.com/openzfs/zfs/issues/14166](https://github.com/openzfs/zfs/issues/14166)
  - [https://github.com/openzfs/zfs/issues/14245](https://github.com/openzfs/zfs/issues/14245)
- 交换分区（Swap）：在内存压力极高的系统中，使用 zvol 作为 swap 可能导致系统锁死，无论剩余 swap 空间多少。该问题正在 [1](https://github.com/openzfs/zfs/issues/7734) 中调查。请参考最新的 [OpenZFS swap 使用文档](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ.html#using-a-zvol-for-a-swap-device-on-linux)。

## 另请参阅

- [ZFS/rootfs](https://wiki.gentoo.org/wiki/ZFS/rootfs "ZFS/rootfs") — 将 ZFS 用作根文件系统
- [Btrfs](https://wiki.gentoo.org/wiki/Btrfs "Btrfs") — 面向 Linux 的写时复制（CoW）[文件系统](https://wiki.gentoo.org/wiki/Filesystem "Filesystem")，旨在实现高级功能，同时关注容错、自愈能力和易管理性

## 外部资源

- [ZFS on Linux](http://zfsonlinux.org/)
- [OpenZFS](http://openzfs.org/)
- [ZFS 最佳实践指南](https://www.serverfocus.org/zfs-best-practices-guide)（[存档](https://web.archive.org/web/20120618012452/http://www.serverfocus.org/zfs-best-practices-guide)）
- [ZFS 恶意调优指南](https://www.serverfocus.org/zfs-evil-tuning-guide)
- [关于 Linux/Gentoo 上 ZFS 的文章（德语）](http://www.pro-linux.de/artikel/2/1181/zfs-unter-linux.html)
- [ZFS 管理](https://pthree.org/2012/12/04/zfs-administration-part-i-vdevs/)

## 参考文献

1. [不适合 ZFS 的 SSD/NVMe 硬件 — WD BLACK SN770 等](https://github.com/openzfs/zfs/discussions/14793)
2. [OpenZFS](https://en.wikipedia.org/wiki/OpenZFS)
3. [Oracle Solaris 11.4 ZFS 池版本管理](https://docs.oracle.com/en/operating-systems/solaris/oracle-solaris/11.4/manage-zfs/zfs-pool-versions.html)
4. [OpenZFS, issue #7734](https://github.com/openzfs/zfs/issues/7734)
