# OpenZFS 系统管理

- 原文地址：[OpenZFS System Administration](https://openzfs.org/wiki/System_Administration)
- 版本 2023 年 9 月 11 日 17:16

本页面旨在记录对系统管理员有用的信息。

## 概述

ZFS 是对传统存储栈的重新设计。ZFS 中的基本存储单元是池（pool），从池中可以获得 dataset，这些 dataset 可以是挂载点（可挂载的文件系统）或块设备。ZFS 池是一个完整的存储栈，能够替代 RAID、分区、卷管理、fstab/exports 文件以及仅跨单个磁盘的传统文件系统，如 UFS 和 XFS。这使得相同的任务可以通过更少的代码、更高的可靠性以及简化的管理来完成。

从一组磁盘创建具有冗余的可用文件系统可以通过一条命令完成，并且在重启后依然保持。这是因为 ZFS 池总是包含一个可挂载的文件系统，称为根 dataset，该文件系统在池创建时被挂载。在创建时，池会被导入系统，从而在 zpool.cache 文件中创建一个条目。在导入或创建时，池会存储系统的唯一 hostid，并且为了支持多路径，除非强制，否则导入到其他系统会失败。

ZFS 本身由三层主要结构组成。最底层是存储池分配器（Storage Pool Allocator，SPA），负责将物理磁盘组织成存储空间。中间层是数据管理单元（Data Management Unit，DMU），它使用 SPA 提供的存储，以事务性的、原子方式进行读写。最顶层是 dataset 层，它将池提供的文件系统和块设备（zvol）上的操作转换为 DMU 中的操作。

### 低级存储

SPA 在池中对磁盘的组织形式是一个由 vdev（虚拟设备）构成的树。树的顶层是根 vdev。它的直接子节点可以是除自身之外的任意 vdev 类型。主要的 vdev 类型有：

* mirror（支持 n 路镜像）
* raidz

  * raidz1（1 磁盘校验，类似 RAID 5）
  * raidz2（2 磁盘校验，类似 RAID 6）
  * raidz3（3 磁盘校验，无 RAID 类比）
* disk
* file（不建议在生产环境中使用，因为另一个文件系统会增加不必要的层）

任意数量的这些 vdev 都可以作为根 vdev 的子节点，被称为顶级 vdev。此外，其中一些也可能有子节点，例如 mirror vdev 和 raidz vdev。命令行工具不支持将 raidz 作为 mirror 的子节点或 mirror 作为 raidz 的子节点，尽管这种配置在开发者测试中有使用。

使用多个顶级 vdev 会以加法方式影响 IOPS，总 IOPS 为各顶级 vdev 的 IOPS 之和。因此，任何一个主要顶级 vdev 的丢失都会导致整个池的丢失，因此必须在所有顶级 vdev 上使用适当的冗余。

支持的最小 file vdev 或 disk vdev 大小为 64MB（2^16 字节），最大值取决于平台，但所有平台应至少支持 16EB（2^64 字节）的 vdev。

还有三种特殊类型：

* spare
* cache
* log

spare 设备在磁盘故障时用于替换，前提是池的 autoreplace 属性已启用且你的平台支持该功能。它不会替换 cache 设备或 log 设备。

cache 设备用于扩展 ZFS 的内存数据缓存，它替代了页缓存（page cache），除了 mmap()，在大多数平台上 mmap() 仍使用页缓存。ZFS 使用的算法是自适应替换缓存（Adaptive Replacement Cache, ARC）算法，其命中率高于页缓存使用的最近最少使用（LRU）算法。cache 设备通常与闪存设备一起使用。存储在其中的数据是非持久的，因此可以使用廉价设备。

log 设备允许 ZFS Intent Log（ZIL）记录写入到不同设备，例如闪存设备，以提高同步写操作的性能，然后再写入主存储。除非设置了 sync=disabled dataset 属性，否则这些记录会被使用。在任何情况下，同步操作的更改会保存在内存中，直到下一个事务组提交时写入。只要下一个事务组提交成功，ZFS 可以在 log 设备丢失的情况下继续运行。如果系统在 log 默认丢失时崩溃，池将标记为故障。虽然可以恢复，但当前事务组中所做的所有同步更改将丢失，不会保存在存储在该池的 dataset 上。

### 数据完整性

ZFS 通过多种机制尝试提供数据完整性：

* 已提交的数据存储在一个 Merkle 树中，该树在每次事务组提交时以原子方式更新。
* Merkle 树使用存储在块指针中的 256 位校验和来防止错误写入，包括那些对较弱校验和可能发生碰撞的写入。sha256 被支持用于加密强保证，尽管默认是 fletcher4。
* 每个 disk/file vdev 包含四个磁盘标签（每端两个），以确保即使一端由于磁头掉落丢失数据，也不会擦除标签。
* 事务组提交使用两个阶段来确保在事务组被视为已提交之前，所有数据都已写入存储。这就是为什么每个磁盘两端都有两个标签。在机械存储上执行事务组提交需要完整的磁头扫描，并使用刷新（flush）操作以确保后半部分不会在其他操作之前执行。
* 用于同步 IO 的 ZIL 记录存储待更改的数据，这些记录是自检块，仅在系统在上一个事务组提交之前进行更改时，在池导入时读取。
* 默认情况下，所有元数据存储两份，其中包含池在特定事务组状态的对象（标签指向的对象）会写入三次。ZFS 尽量将元数据存储在相距至少 1/8 磁盘的位置，以防磁头掉落导致不可恢复的损坏。
* 标签包含一个 uberblock 历史，这允许在最坏情况下将整个池回滚到近期的某一点。使用此恢复机制需要特殊命令，因为通常不需要。
* uberblocks 包含所有 vdev GUID 的总和。只有当总和匹配时，uberblocks 才被视为有效。这可以防止已损坏的旧池的 uberblocks 被误认为是有效的。
* 支持 N 路镜像和 raidz 的最多 3 级校验，这样在使用适当冗余时，越来越常见的 2 磁盘故障[[1]](https://queue.acm.org/detail.cfm?id=1670144) 不会在恢复过程中破坏 RAID 5 或双镜像，从而避免 ZFS 池被损坏。

在 FreeNAS 论坛上曾流传一种错误信息，称在未使用 ECC 内存时，ZFS 的数据完整性功能不如其他文件系统[[2]](https://forums.freenas.org/index.php?threads/ecc-vs-non-ecc-ram-and-zfs.15449/)。这一说法已被彻底驳斥[[3]](http://jrs-s.net/2015/02/03/will-zfs-and-non-ecc-ram-kill-your-data/)。所有软件为了可靠运行都需要 ECC 内存[[4]](http://open-zfs.org/wiki/Hardware#ECC_Memory)，ZFS 在这方面与其他文件系统没有区别。

## 启动过程

在传统的 POSIX 系统中，启动过程如下：

1. CPU 开始执行 BIOS。
2. BIOS 进行基本硬件初始化并加载 bootloader。
3. bootloader 加载内核并传递包含 rootfs 的驱动信息。
4. 内核进行额外初始化，挂载 rootfs 并启动 /sbin/init。
5. /sbin/init 运行启动其他所有服务的脚本，包括挂载 fstab 中的文件系统以及通过 exports 导出 NFS 共享。

此过程存在一些变体。例如，在 Illumos（通过 boot_archive）和 FreeBSD（单独）上，bootloader 还会加载内核模块。一些 Linux 系统会加载 initramfs，这是一个临时 rootfs，包含需要加载的模块，并将部分启动逻辑移动到用户空间，通过 pivot_root 挂载真实 rootfs 并切换到它。此外，EFI 系统能够直接加载操作系统内核，从而无需 bootloader 阶段。

ZFS 对启动过程的改动如下：

1. 当 rootfs 位于 ZFS 上时，必须在内核挂载之前导入池。Illumos 和 FreeBSD 的 bootloader 会将池信息传递给内核，以便导入根池并挂载 rootfs。在 Linux 上，必须使用 initramfs，直到支持动态创建 initramfs 的 bootloader 功能实现为止。
2. 无论是否存在根池，导入的池必须显示。通过读取 zpool.cache 文件中的导入池列表实现，该文件在大多数平台上位于 /etc/zfs/zpool.cache，在 FreeBSD 上位于 /boot/zfs/zpool.cache。该文件以 XDR 编码的 nvlist 存储，可通过不带参数执行 `zdb` 命令读取。
3. 池导入后，必须挂载文件系统，并创建任何文件系统导出或 iSCSI LUN。如果 dataset 的 mountpoint 属性设置为 legacy，可以使用 fstab。否则，启动脚本将在池导入后运行 `zfs mount -a` 挂载所有 dataset。类似地，通过 NFS 或 SMB 共享文件系统，以及通过 iSCSI 共享 zvol 的 dataset，将在挂载完成后通过 `zfs share -a` 导出或共享。并非所有平台都支持在所有共享类型上使用 `zfs share -a`。在不支持自动化的系统上，必须使用传统方法。

下表显示了 `zfs share -a` 在各平台上支持的协议：

| **平台**   | **iSCSI** | **NFS** | **SMB** |
| -------- | --------- | ------- | ------- |
| FreeBSD  | 否         | 是       | 否       |
| Illumos  | 是         | 是       | 是       |
| Linux    | 否         | 是       | 是       |
| Mac OS X | 否         | 否       | 否       |
| OSv      | 否？        | 否？      | 否？      |

## 池创建

ZFS 的管理通过 `zpool` 和 `zfs` 命令执行。要创建池，可以使用 `zpool create poolname ...`。poolname 后面的部分是 vdev 树的规格。根 dataset 默认会挂载在 /poolname，除非使用 `zpool create -m none`。其他挂载点位置可以通过将其写在 `none` 位置来指定。

在指定顶级 vdev 关键字之前的任何文件或磁盘 vdev 都将成为顶级 vdev。顶级 vdev 关键字之后的任何 vdev 都将成为该 vdev 的子节点。顶级 vdev 内的不等大小磁盘或文件会将其存储限制为较小的大小。对于生产环境的池，重要的是不要创建非 raidz、mirror、log、cache 或 spare 的顶级 vdev。

更多信息可以在你的平台上的 zpool 手册页中找到。在 Illumos 上为第 1m 节，在 Linux 上为第 8 节。

### 重要信息

#### 扇区对齐

ZFS 会尝试通过从磁盘中提取物理扇区大小来确保正确对齐。每个顶级 vdev 会使用最大扇区大小，以避免部分扇区修改带来的额外开销。当磁盘错误报告其物理扇区大小时，这种方法将不正确。[性能调优](https://openzfs.org/wiki/Performance_tuning#Alignment_Shift_.28ashift.29 "Performance tuning") 页面提供了更多说明。

#### 整盘调整

在提供整盘时，ZFS 在各个平台上也会尝试进行一些微调。在 Illumos 上，ZFS 会启用磁盘缓存以提升性能。当提供的是分区时则不会启用，以保护可能不耐受磁盘缓存的其他文件系统共享该磁盘，例如 UFS。在 Linux 上，IO elevator 会被设置为 noop，以减少 CPU 开销。ZFS 有自己的内部 IO elevator，使得 Linux 的 elevator 成为冗余。[性能调优](https://openzfs.org/wiki/Performance_tuning#Whole_Disks_versus_Partitions "Performance tuning") 页面对这种行为有更详细的说明。

#### 磁盘错误恢复控制

ZFS 目前不会自动调整磁盘的 [错误恢复控制](https://openzfs.org/wiki/Hardware#Error_recovery_control "Hardware")。当磁盘遇到读取错误时，它会重复尝试读取，希望从略微不同的角度读取成功，从而允许正确重写扇区。它会一直尝试，直到达到超时，这在许多磁盘上通常为 7 秒。在此期间，磁盘可能无法处理其他 IO 请求，这会严重影响 IOPS，因为事务组提交必须等待所有 IO 完成才能开始下一步。在 ZFS 修改以控制其管理的磁盘之前，系统管理员应使用 smartctl 等工具或系统本地文件在每次启动时进行设置。

#### 磁盘或磁盘控制器挂起

类似地，如果磁盘或磁盘控制器挂起，会导致整个池挂起，并触发死锁定时器（deadman timer）。在 Illumos 上，这会触发系统重启。在 Linux 上，会尝试记录失败，但不采取其他操作。deadman timer 的默认超时为 1000 秒。

#### 硬件

ZFS 设计用于使用商用硬件可靠存储数据，但某些硬件配置本身不可靠，以至于任何文件系统都无法补偿。有关硬件配置的建议，请参见 [Hardware](http://open-zfs.org/wiki/Hardware) 页面。

#### 硬件 RAID

不应在 ZFS 上使用硬件 RAID。原因可见 [Hardware](https://openzfs.org/wiki/Hardware#Hardware_RAID_controllers "Hardware") 页面。

#### 性能

ZFS 具有自我调优能力，但有一些参数可优化特定应用。这些内容在 [性能调优](https://openzfs.org/wiki/Performance_tuning "Performance tuning") 页面中有说明。

#### 冗余

双盘故障发生的概率足够高[[5]](https://queue.acm.org/detail.cfm?id=1670144)，因此 raidz1 vdev 不应在生产环境中用于数据存储。双盘镜像也存在风险，但不如 raidz1 vdev 高，除非仅使用两块磁盘。这是因为在双盘镜像中，所有磁盘都失败的概率统计上低于在奇偶校验配置（如 raidz1）中仅两块磁盘失败的概率，除非仅使用两块磁盘，此时风险相同。同样的风险也适用于 RAID 1 和 RAID 5。

单盘 vdev（不包括 log 和 cache 设备）在生产环境中不应使用，因为它们没有冗余。然而，可以通过使用 `zpool attach` 将单盘池的磁盘转换为镜像，从而实现冗余。

## 一般管理

一般管理在池级通过 `zpool` 命令进行，在 dataset 级通过 `zfs` 命令进行。文档可在各自平台的 zpool 和 zfs 手册页中找到。在 Linux 上为第 8 节，在 Illumos 上为第 1m 节。

有关部分手册页链接，请参见 [平台/发行版文档](https://openzfs.org/wiki/System_Administration#Platform.2FDistribution_documentation "System Administration")。请注意，一个平台的手册页在其他平台上可能也适用。

## 其他资源

### 第三方工具

* [bdrewery/zfstools](https://github.com/bdrewery/zfstools) 提供快照管理工具，使用 Ruby 编写。
* [fearedbliss/bliss-zfs-scripts](https://github.com/fearedbliss/bliss-zfs-scripts) 提供“ZFS 快照与备份管理”工具，遵循 MPL 2.0，针对 Gentoo Linux 设计。
* [jimsalterjrs/sanoid](https://github.com/jimsalterjrs/sanoid) 基于策略的快照管理和复制工具，遵循 GPL，在 Linux 和 FreeBSD 上测试。
* [Rudd-O/zfs-tools](https://github.com/Rudd-O/zfs-tools) 提供快照管理和复制工具，使用 Python 编写。
* [ZFS Watcher](http://zfswatcher.damicon.fi/) 是一个池监控与通知守护进程。

### 一般文档

* [功能](https://openzfs.org/wiki/Features "Features")
* [出版物与会议演讲](https://openzfs.org/wiki/Publications "Publications")
* [历史](https://openzfs.org/wiki/History "History")
* [性能调优](https://openzfs.org/wiki/Performance_tuning "Performance tuning")
* 手册页：[zdb](http://illumos.org/man/1m/zdb) | [zfs](http://illumos.org/man/1m/zfs) | [zpool](http://illumos.org/man/1m/zpool) | [zpool-features](http://illumos.org/man/5/zpool-features) | [zstreamdump](http://illumos.org/man/1m/zstreamdump) – *来自 Illumos；更好的渲染页面会更好*
* [Oracle Solaris ZFS 管理指南](http://docs.oracle.com/cd/E26505_01/html/E37384/index.html) – 大部分内容适用
* [ZFS – 文件系统的最后方案](http://www.snia.org/sites/default/files2/sdc_archives/2008_presentations/monday/JeffBonwick-BillMoore_ZFS.pdf) – 来自 SNIA 2008 的概览
* [Aaron Toponce 关于 ZFS 的系列博客文章](https://pthree.org/2012/04/17/install-zfs-on-debian-gnulinux/)
* [Kateley Co 视频教程](http://kateleyco.com/?page_id=783)
* [RAID-Z 条带宽度](http://blog.delphix.com/matt/2014/06/06/zfs-stripe-width/)
* [RAID-Z 计算工具](http://wintelguy.com/raidcalc.pl) – 包含 RAID-Z1/Z2/Z3 计算

### 平台/发行版文档

#### FreeBSD

* 手册页：[zdb](http://www.freebsd.org/cgi/man.cgi?query=zdb&manpath=FreeBSD+8.4-RELEASE) | [zfs](http://www.freebsd.org/cgi/man.cgi?query=zfs&manpath=FreeBSD+8.4-RELEASE) | [zpool](http://www.freebsd.org/cgi/man.cgi?query=zpool&manpath=FreeBSD+8.4-RELEASE) | [zpool-features](http://www.freebsd.org/cgi/man.cgi?query=zpool-features&manpath=FreeBSD+8.4-RELEASE) | [zstreamdump](http://www.freebsd.org/cgi/man.cgi?query=zstreamdump&manpath=FreeBSD+8.4-RELEASE)
* *The FreeBSD Handbook* 的 [ZFS 章节](https://www.freebsd.org/doc/en_US.ISO8859-1/books/handbook/zfs.html)
* [FreeBSD ZFS Wiki](https://wiki.freebsd.org/ZFS)

#### Gentoo

* [Wiki 页面](https://wiki.gentoo.org/wiki/ZFS)
* [Richard Yao 的 Gentoo 安装笔记](https://github.com/ryao/zfs-overlay/blob/master/zfs-install)

#### illumos

* 手册页：[zdb](http://www.illumos.org/man/1m/zdb) | [zfs](http://illumos.org/man/1m/zfs) | [zpool](https://www.illumos.org/man/1M/zpool) | [zpool-features](https://www.illumos.org/man/5/zpool-features) | [zstreamdump](http://illumos.org/man/1m/zstreamdump)
* [Wiki 页面](http://wiki.illumos.org/display/illumos/ZFS)
* OpenIndiana [ZFS 管理指南](http://wiki.openindiana.org/oi/ZFS)
