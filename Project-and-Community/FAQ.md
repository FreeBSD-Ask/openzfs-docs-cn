# 常见问题解答

## 什么是 OpenZFS

OpenZFS 是卓越的存储平台，拥有传统文件系统、卷管理器等功能，且在所有发行版中都提供了一致的可靠性、功能性和性能。可以在 [OpenZFS 维基百科条目](https://en.wikipedia.org/wiki/OpenZFS) 中找到更多有关 OpenZFS 的信息。

## 硬件需求

由于 ZFS 最初是为 Sun Solaris 设计的，长期以来，ZFS 被认为是面向大型服务器的、能够负担得起当时最优、最强硬件的公司的文件系统。但自从 ZFS 被移植到众多开源平台（BSD、Illumos 以及 Linux——统一在“OpenZFS”这一组织框架下）之后，上述要求已经降低。

推荐的硬件需求是：

* ECC 内存。这并不是真正的硬性条件，但强烈建议。
* 为获得最佳性能，建议使用 8 GB 以上的内存。使用 2 GB 及更少的内存完全可行（而且确实有人这么做），但如果使用去重功能则需要更多内存。

## 我必须为 ZFS 使用 ECC 内存吗？

在需要最强数据完整性保障的企业环境中，强烈建议为 OpenZFS 搭配 ECC 内存。在没有 ECC 内存时，可能无法检测到由宇宙射线或故障内存引起的罕见的随机位翻转。只要发生这种情况，OpenZFS（及任何其他文件系统）都会把受损的数据写入磁盘，且无法自动检测到这种损坏。

不幸的是，消费级硬件并不总是支持 ECC 内存。即使支持，ECC 内存的价格也会更高。对家庭用户来说，ECC 内存带来的额外安全性可能不足以抵消其成本。由你自己来决定你的数据需要何种级别的保护。

## 安装

OpenZFS 可用于 FreeBSD 以及所有主流 Linux 发行版。有关安装说明的链接，请参阅 wiki 中的 [安装指引](https://openzfs.github.io/openzfs-docs/Getting%20Started/index.html) 部分。如果你的发行版或操作系统未列出，你也可以始终从最新的官方 [tarball](https://github.com/openzfs/zfs/releases) 构建 OpenZFS。

## 支持的架构

OpenZFS 会定期为以下架构进行编译：aarch64、arm、ppc、ppc64、x86、x86_64。

## 支持的 Linux 内核

某个 OpenZFS 版本的 [说明](https://github.com/openzfs/zfs/releases) 中会包含受支持内核的范围。根据需要，点发布版本会被打上标签，以支持来自 [kernel.org](https://www.kernel.org/) 的 *stable*（稳定版）内核。由于 ZFS 在企业级 Linux 发行版中的重要地位，最早支持的内核版本是 2.6.32。

## 32 位 与 64 位 系统

**极其建议** 使用 64 位内核。在 32 位系统上能够构建 OpenZFS，但你可能会遇到稳定性问题。

ZFS 最初是为 Solaris 内核开发的，而 Solaris 内核在若干重要方面与一些 OpenZFS 平台不同。对 ZFS 来说，最重要的一点或许是：在 Solaris 内核中，大量使用虚拟地址空间是一种常见做法。然而，在 Linux 内核中，极不建议使用虚拟地址空间。对于 32 位架构来说尤为如此，因为其虚拟地址空间默认仅限于 100M。在 64 位 Linux 内核上，同样不建议使用虚拟地址空间，但由于其地址空间远大于物理内存，因此问题相对较轻。

如果你在 32 位 系统上触及虚拟内存限制，你将在系统日志中看到如下信息。你可以通过启动选项 `vmalloc=512M` 来增加虚拟地址空间大小。

```sh
vmap allocation for size 4198400 failed: use vmalloc=<size> to increase size.
```

然而，即使应用了此项变更，你的系统也很可能无法完全稳定。对 32 位 系统的正确支持，取决于 OpenZFS 代码逐步摆脱对虚拟内存的依赖。这需要一定时间才能正确完成，但已经在 OpenZFS 的规划之中。预计这一变化还将改进 OpenZFS 对 ARC 缓存的管理效率，并实现与标准 Linux 页面缓存更加紧密的集成。

## 从 ZFS 启动

在 Linux 上从 ZFS 启动是可行的，而且已经有很多人如此做了。针对 [Debian](https://openzfs.github.io/openzfs-docs/Getting%20Started/Debian/index.html)、[Ubuntu](https://openzfs.github.io/openzfs-docs/Getting%20Started/Ubuntu/index.html) 以及 [Gentoo](https://github.com/pendor/gentoo-zfs-install/tree/master/install) 都有非常优秀的操作指南。

在 FreeBSD 13+ 上，从 ZFS 启动是开箱即用受支持的。

## 在创建池时选择 `/dev/` 的名称（面向 Linux）

在创建 ZFS 池时，可以指定不同的 `/dev/` 名称。每种方案都有其优缺点，如何正确选择适合你的 ZFS 存储池，实际上取决于你的需求。对于开发和测试，使用 `/dev/sdX` 式命名方式既快速又简单。普通的家用服务器可能更偏好使用 `/dev/disk/by-id/` 这种命名方式，能获得更好的简洁性和可读性。而那些拥有多个控制器、机箱和交换机的超大型配置，则很可能更倾向于使用 `/dev/disk/by-vdev` 这种命名方式，可获得最大的控制能力。但最终，如何标识你的磁盘，你说了算。

* **/dev/sdX、/dev/hdX** 最适合用于开发、测试池
  * 概要：顶层的 `/dev/` 名称是为了与其他 ZFS 实现保持一致而采用的默认方式。它们在所有 Linux 发行版中都可用，并且被广泛使用。然而，由于它们不是持久的，因此只应在开发、测试池中与 ZFS 一起使用。
  * 优点：这种方式适合快速测试，名称简短，并且在所有 Linux 发行版中都可用。
  * 缺点：这些名称不是固定的，会根据磁盘的检测顺序而变化。在系统添加或移除硬件后很容易导致名称的改变。之后你需要删除 `zpool.cache` 文件，再使用新的名称重新导入池。
  * 示例：`zpool create tank sda sdb`
* **/dev/disk/by-id/** 最适合用于小型池（少于 10 块磁盘）
  * 概要：该目录包含具有更高可读性的人类可读磁盘标识符。磁盘标识符通常由接口类型、厂商名称、型号、设备序列号以及分区号组成。这种方式更加用户友好，因为它简化了对特定磁盘的识别。
  * 优点：非常适合只有单一磁盘控制器的小型系统。由于这些名称是固定的且肯定不会改变，磁盘如何连接到系统并不重要。你可以把它们全部取出，在桌面上随意打乱，再以任意方式装回系统，仍然可以正确地自动导入池。
  * 缺点：基于物理位置来配置冗余组会变得困难且容易出错。在许多个人虚拟机环境中并不可靠，因为相关软件默认不会生成固定且唯一的名称。
  * 示例：`zpool create tank scsi-SATA_Hitachi_HTS7220071201DP1D10DGG6HMRP`
* **/dev/disk/by-path/** 适合用于大型池（超过 10 块磁盘）
  * 概要：这种方式使用包含系统中物理线缆布局的设备名称，这意味着某一块磁盘会绑定到一个特定的位置。名称包含了 PCI 总线编号，以及机箱名称和端口编号。这在配置大型池时可以提供最大的控制能力。
  * 优点：在名称中编码存储拓扑不仅有助于在大型部署中定位磁盘，还能让你在多个适配器或机箱之间明确地布局冗余组。
  * 缺点：这些名称很长、很繁琐，并且对人工管理来说较为困难。
  * 示例：`zpool create tank pci-0000:00:1f.2-scsi-0:0:0:0 pci-0000:00:1f.2-scsi-1:0:0:0`
* **/dev/disk/by-vdev/** 最适合用于大型池（超过 10 块磁盘）
  * 概要：这种方式通过配置文件 `/etc/zfs/vdev_id.conf` 提供对设备命名的管理控制。可以自动为 JBOD 中磁盘生成名称，来反映其通过机箱 ID 和槽号确定的物理位置。也可以基于现有的 udev 设备链接手动分配名称，如 `/dev/disk/by-path` 或 `/dev/disk/by-id` 中的链接。这能让你为磁盘选择自己独特且有意义的名称。这些名称会在所有 zfs 工具中显示，从而有助于理清大型复杂池的管理。更多细节请参见 `vdev_id` 和 `vdev_id.conf` 的 man 页面。
  * 优点：这种方式的主要优点是能让你选择有意义且可读的人类名称。除此之外，其优势取决于所采用的命名方法。如果名称来源于物理路径，则可以实现 `/dev/disk/by-path` 的优势；另一方面，如果基于驱动器标识符或 WWN 别名命名，则具有与 `/dev/disk/by-id` 相同的优势。
  * 缺点：此方法依赖于 `/etc/zfs/vdev_id.conf` 文件针对你的系统被正确配置。要配置此文件，请参阅章节 [设置 /etc/zfs/vdev_id.conf 文件](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ.html#setting-up-the-etc-zfs-vdev-id-conf-file)。与优点一样，缺点也可能取决于所采用的命名方法，并可能涉及 `/dev/disk/by-id` 或 `/dev/disk/by-path` 的局限性。
  * 示例：`zpool create tank mirror A1 B1 mirror A2 B2`
* **/dev/disk/by-uuid/** 不是个足够理想的方案
  * 概要：可能有人会认为使用“UUID”是理想选项——然而实际上，这只会为每个 **pool** ID 列出一个设备，这对于导入包含多块磁盘的池并不十分有用。
* **/dev/disk/by-partuuid/** / **/dev/disk/by-partlabel/**：仅适用于已有分区
  * 概要：分区 UUID 在创建时方生成，因此使用受限
  * 缺点：对于未分区的磁盘，无法在 `zpool replace`、`add` 或 `attach` 中引用其分区唯一 ID，且如果没有事先记录映射，也无法轻松找到故障磁盘。


## 设置 `/etc/zfs/vdev_id.conf` 文件

要使用 `/dev/disk/by-vdev/` 式命名，必须配置 `/etc/zfs/vdev_id.conf` 文件。该文件的格式在 `vdev_id.conf` 的 man 页面中有描述。以下为几个示例。

非多路径配置，直接连接的 SAS 机箱，以及任意的槽位重新映射：

```sh
multipath     no
topology      sas_direct
phys_per_port 4

#       PCI_SLOT HBA PORT  CHANNEL NAME
channel 85:00.0  1         A
channel 85:00.0  0         B

#    Linux      Mapped
#    Slot       Slot
slot 0          2
slot 1          6
slot 2          0
slot 3          3
slot 4          5
slot 5          7
slot 6          4
slot 7          1
```

SAS 交换机拓扑。请注意，在此示例中 `channel` 关键字只接受两个参数。

```sh
topology      sas_switch

#       SWITCH PORT  CHANNEL NAME
channel 1            A
channel 2            B
channel 3            C
channel 4            D
```

多路径配置。请注意，通道名称有多个定义——每条物理路径一个。

```sh
multipath yes

#       PCI_SLOT HBA PORT  CHANNEL NAME
channel 85:00.0  1         A
channel 85:00.0  0         B
channel 86:00.0  1         A
channel 86:00.0  0         B
```

使用设备链接别名的配置。

```sh
#     by-vdev
#     name     fully qualified or base name of device link
alias d1       /dev/disk/by-id/wwn-0x5000c5002de3b9ca
alias d2       wwn-0x5000c5002def789e
```

定义新磁盘名称后，运行 `udevadm trigger` 以提示 udev 解析配置文件。这将生成一个新的 `/dev/disk/by-vdev` 目录，其中新增了指向 `/dev/sdX` 名称的符号链接。按照上面的第一个示例，你可以使用以下命令创建新的镜像池：

```sh
$ zpool create tank \
    mirror A0 B0 mirror A1 B1 mirror A2 B2 mirror A3 B3 \
    mirror A4 B4 mirror A5 B5 mirror A6 B6 mirror A7 B7

$ zpool status
  pool: tank
 state: ONLINE
 scan: none requested
config:

    NAME        STATE     READ WRITE CKSUM
    tank        ONLINE       0     0     0
      mirror-0  ONLINE       0     0     0
        A0      ONLINE       0     0     0
        B0      ONLINE       0     0     0
      mirror-1  ONLINE       0     0     0
        A1      ONLINE       0     0     0
        B1      ONLINE       0     0     0
      mirror-2  ONLINE       0     0     0
        A2      ONLINE       0     0     0
        B2      ONLINE       0     0     0
      mirror-3  ONLINE       0     0     0
        A3      ONLINE       0     0     0
        B3      ONLINE       0     0     0
      mirror-4  ONLINE       0     0     0
        A4      ONLINE       0     0     0
        B4      ONLINE       0     0     0
      mirror-5  ONLINE       0     0     0
        A5      ONLINE       0     0     0
        B5      ONLINE       0     0     0
      mirror-6  ONLINE       0     0     0
        A6      ONLINE       0     0     0
        B6      ONLINE       0     0     0
      mirror-7  ONLINE       0     0     0
        A7      ONLINE       0     0     0
        B7      ONLINE       0     0     0

errors: No known data errors
```

## 更改现有池的 `/dev/` 名称

如何更改现有池的 `/dev/` 名称：可以通过简单地导出池，然后使用选项 `-d` 重新导入池来指定要使用的新名称。例如，要使用 `/dev/disk/by-vdev` 中的自定义名称：

```sh
$ zpool export tank
$ zpool import -d /dev/disk/by-vdev tank
```

## `/etc/zfs/zpool.cache` 文件

每当系统导入存储池时，存储池信息会被添加到 `/etc/zfs/zpool.cache` 文件中。该文件包含了存储池的配置信息，例如设备名称和池状态。如果在运行 `zpool import` 命令时存在该文件，它将用于确定可导入的池列表。当未能在缓存文件中列出某池时，需要使用 `zpool import -d /dev/disk/by-id` 命令检测再导入。

## 生成新的 `/etc/zfs/zpool.cache` 文件

当池的配置发生更改时，`/etc/zfs/zpool.cache` 文件会自动更新。然而，如果由于某种原因该文件已经过时，你可以通过设置池的 cachefile 属性来强制生成新的 `/etc/zfs/zpool.cache` 文件。

```sh
$ zpool set cachefile=/etc/zfs/zpool.cache tank
```

也还可以通过设置 `cachefile=none` 来禁用缓存文件。这对于故障切换配置非常有用，在这种配置中，应始终由故障切换软件显式导入存储池。

```sh
$ zpool set cachefile=none tank
```

## 发送与接收流

### hole_birth 漏洞

hole_birth 功能存在或曾存在漏洞，其结果是，如果你从受影响的数据集执行 `zfs send -i`（或 `-R`，因为它使用 `-i`），接收端 *不会看到任何校验或其他错误，但将无法与源匹配*。

ZoL 版本 0.6.5.8 和 0.7.0-rc1（及以上）默认在发送端忽略导致此问题的损坏元数据。

更多详情请参阅 [hole_birth FAQ](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ%20hole%20birth.html)。

### 发送大块数据

在发送包含大块（>128K）的增量流时，必须指定 `--large-block` 标志。在增量发送之间不一致地使用该标志，可能导致接收到的文件被错误地清零。原始加密的 send/recv 自动隐含 `--large-block` 标志，因此不受影响。

更多详情请参阅 [issue 6224](https://github.com/zfsonlinux/zfs/issues/6224)。

## CEPH/ZFS

可以根据在 CEPH/ZFS 上施加的工作负载进行大量调优，同时也有一些通用指南如下：

### ZFS 配置

CEPH filestore 后端高度依赖 xattrs，为获得最佳性能，所有 CEPH 工作负载都将受益于以下 ZFS 数据集参数：

* `xattr=sa`
* `dnodesize=auto`

除此之外，通常以 rbd/cephfs 为主的工作负载适合较小的 recordsize（16K-128K），而以 objectstore/s3/rados 为主的工作负载适合较大的 recordsize（128K-1M）。

### CEPH 配置（`ceph.conf`）

此外，CEPH 会根据底层文件系统内部设置各种值以处理 xattrs。由于 CEPH 官方仅支持/检测 XFS 和 BTRFS，对于其他所有文件系统，它将回退到相对 [有限的“安全”值](https://github.com/ceph/ceph/blob/4fe7e2a458a1521839bc390c2e3233dd809ec3ac/src/common/config_opts.h#L1125-L1148)。在新版本中，对较大 xattrs 的需求甚至会阻止 OSD 启动。

官方推荐的解决方法（[见此处](https://tracker.ceph.com/issues/16187#note-3)）有一些严重缺点，尤其是针对支持 xattr“有限”的文件系统，如 ext4。

ZFS 内部对 xattrs 长度没有限制，因此我们可以将其视作 CEPH 对待 XFS 的方式。我们可以设置覆盖，将 3 个内部值设置为与 XFS 使用的相同值（[见此处](https://github.com/ceph/ceph/blob/9b317f7322848802b3aab9fec3def81dddd4a49b/src/os/filestore/FileStore.cc#L5714-L5737) 和 [此处](https://github.com/ceph/ceph/blob/4fe7e2a458a1521839bc390c2e3233dd809ec3ac/src/common/config_opts.h#L1125-L1148)），从而能够正常使用而不受“官方”解决方法的严重限制。

```ini
[osd]
filestore_max_inline_xattrs = 10
filestore_max_inline_xattr_size = 65536
filestore_max_xattr_value_size = 65536
```

### 其他通用指南

* 使用独立的日志设备。尽可能不要将 CEPH 日志与 ZFS 数据集放在同一设备上，否则将很快造成严重的碎片问题，更不用说即使在未产生碎片前，性能也会非常差（CEPH 日志每次写入都会执行 dsync）。
* 使用 SLOG 设备，即使已经有独立的 CEPH 日志设备。对于某些工作负载，跳过 SLOG 并设置 `logbias=throughput` 可能是可接受的。
* 使用高质量的 SLOG/CEPH 日志设备。基于消费级的 SSD，甚至 NVMe 都不适用（例如 Samsung 830、840、850 等），原因五花八门。在此类使用下，CEPH 会很快损坏它们，而且性能也相当低。通常推荐的设备有 [Intel DC S3610, S3700, S3710, P3600, P3700] 或 [Samsung SM853, SM863]，或更好的设备。
* 如果使用高质量 SSD 或 NVMe 设备（如上所述），可以在单个设备上共享 SLOG 和 CEPH 日志，并取得良好效果。曾有报告称，4 块 HDD 对 1 块 SSD（Intel DC S3710 200GB），每个 SSD 分区（记得对齐！）划分为 4×10GB（用于 ZIL/SLOG）+ 4×20GB（用于 CEPH 日志）效果良好。

再次提醒——对消费级固态硬盘来说，CEPH + ZFS 的消耗非常快。即使忽略其缺乏断电保护和耐久度指标，在此类工作负载下，消费级固态硬盘的性能也会让你非常失望。

## 性能考虑

为了在池中获得良好性能，有一些简单的最佳实践应当遵循。

* **在控制器之间均衡分配磁盘：** 性能的限制因素往往不在磁盘本身，而是控制器。通过在控制器之间均衡分配磁盘，通常可以提升吞吐量。
* **使用整块磁盘创建池：** 在运行 `zpool create` 时使用整块磁盘名称。这能让 ZFS 自动分区以确保正确对齐，同时也能提升与其他遵循 `wholedisk` 属性的 OpenZFS 实现的互操作性。
* **拥有足够的内存：** ZFS 推荐至少 2GB 内存。当启用压缩和重复数据删除功能时，强烈建议增加内存。
* **通过设置 ashift=12 提升性能：** 对于某些工作负载，通过设置 `ashift=12` 可以提升性能。此调优只能在块设备首次加入池时设置，例如在首次创建池或向池添加新 vdev 时。对于 RAIDZ 配置，此调优参数可能会导致可用容量下降。

## 高级格式磁盘

高级格式（AF）是一种新型磁盘格式，原生使用 4,096 字节而非 512 字节的扇区大小。为了与旧系统兼容，许多 AF 磁盘会模拟 512 字节的扇区大小。在默认情况下，ZFS 会自动检测磁盘的扇区大小。这种组合可能导致磁盘访问未对齐，从而大幅降低池的性能。

因此，zpool 命令增加了设置 ashift 属性的能力。它能让用户在设备首次加入池时显式指定扇区大小（通常在创建池或向池添加 vdev 时）。ashift 的取值范围为 9 到 16，默认值 0 表示 ZFS 应自动检测扇区大小。该值实际上是位移值，因此 512 字节对应 ashift=9（2^9 = 512），而 4,096 字节对应 ashift=12（2^12 = 4,096）。

要在创建池时强制使用 4,096 字节扇区，可以运行：

```sh
$ zpool create -o ashift=12 tank mirror sda sdb
```

要在向池添加 vdev 时强制使用 4,096 字节扇区，可以运行：

```sh
$ zpool add -o ashift=12 tank mirror sdc sdd
```

## ZVOL 使用空间大于预期

根据 ZVOL 上使用的文件系统（例如 ext4）及其使用情况（例如频繁删除和创建文件），ZVOL 报告的属性 `used` 和 `referenced` 可能会大于消费者报告的“实际”使用空间。

这种情况可能是由于某些文件系统的工作方式导致的，它们倾向于在未使用的新块中分配文件，而不是使用已标记为可用的碎片块。这迫使 ZFS 引用底层文件系统曾经访问过的所有块。

问题本身不大，因为当 `used` 属性达到配置的 `volsize` 时，底层文件系统会开始重用块。但问题在于如果需要对 ZVOL 创建快照，快照引用的空间将包含未使用的块。

可以通过执行所谓的 trim（例如 Linux 上的 `fstrim` 命令）来告知内核哪些块未使用，从而防止该问题。

在创建快照前执行 trim，可确保快照占用最小空间。

在 Linux 上，通过在 `/etc/fstab` 中为挂载的 ZVOL 添加 `discard` 选项，可以有效地让内核持续执行 trim 命令，无需按需运行 fstrim。

## 在 Linux 上将 ZVOL 用作交换设备

你可以使用 ZVOL 作为交换设备，但需要进行适当配置。

>**注意：**
>
>目前在 ZVOL 上使用 swap 可能会导致死锁，如遇此情况，请将日志发送到 [此处](https://github.com/zfsonlinux/zfs/issues/7734)。

* 将卷块大小设置为与你系统页面大小一致。此调优可防止 ZFS 在系统内存不足时对较大块执行读-改-写操作。
* 设置属性 `logbias=throughput` 和 `sync=always`。写入卷的数据会立即刷新到磁盘，从而尽快释放内存。
* 设置 `primarycache=metadata`，以避免通过 ARC 在内存中保留 swap 数据。
* 请禁用交换设备的自动快照。

```sh
$ zfs create -V 4G -b $(getconf PAGESIZE) \
    -o logbias=throughput -o sync=always \
    -o primarycache=metadata \
    -o com.sun:auto-snapshot=false rpool/swap
```

## 在 Xen Hypervisor 或 Xen Dom0（Linux）上使用 ZFS

通常建议将虚拟机存储和 hypervisor 池保持相对独立。不过，也有少数人成功在同一台配置为 Dom0 的机器上部署并运行 OpenZFS。需要注意以下几点：

* 在 grub.conf 中为 Dom0 分配足够的内存。
  * `dom0_mem=16384M,max:16384M`
* 在 `/etc/modprobe.d/zfs.conf` 中为 ZFS 分配不超过 Dom0 30-40% 的内存。
  * `options zfs zfs_arc_max=6442450944`
* 在 `/etc/xen/xl.conf` 中禁用 Xen 的自动气球功能。
* 注意 Xen 的相关 bug，例如与气球功能相关的 [这个问题](https://github.com/zfsonlinux/zfs/issues/1067)。

## udisks2 为 ZVOL 创建 `/dev/mapper` 条目（Linux）

为了避免 udisks2 创建必须在 ZVOL 删除、重命名时需要手动移除、维护的 `/dev/mapper` 条目，可以创建 udev 规则，例如 `/etc/udev/rules.d/80-udisks2-ignore-zfs.rules`，内容如下：

```ini
ENV{ID_PART_ENTRY_SCHEME}=="gpt", ENV{ID_FS_TYPE}=="zfs_member", ENV{ID_PART_ENTRY_TYPE}=="6a898cc3-1dd2-11b2-99a6-080020736631", ENV{UDISKS_IGNORE}="1"
```

## 许可

许可证信息可见 [此处](https://openzfs.github.io/openzfs-docs/License.html)。

## 报告问题

你可以使用公开的 [issue tracker](https://github.com/zfsonlinux/zfs/issues) 打开新问题、搜索现有问题。问题跟踪器用于组织未解决的 bug 报告、功能请求及其他开发任务。任何人在注册 GitHub 账号后都可以发表评论。

请确保你实际遇到的是 bug，而不是支持问题。如有疑问，请先在邮件列表上咨询，如果之后被要求提交问题，再进行提交。

在打开新问题时，请在 issue 中包含以下信息：

* 你使用的发行版及其版本。
* 你使用的 spl/zfs 包及其版本。
* 描述你观察到的问题。
* 描述如何重现该问题。
* 包括系统日志中的任何警告/错误/回溯信息。

当提交新问题时，开发者可能会要求提供更多问题信息。通常，你提供的细节越多，开发者解决问题的速度就越快。例如，提供一个简单的测试用例通常非常有帮助。请准备与开发者合作，以便问题得到解决。他们可能会要求提供如下信息：

* 使用 `zdb` 或 `zpool status` 报告的池配置。
* 硬件配置，例如：

  * CPU 数量。
  * 内存大小。
  * 系统是否使用 ECC 内存。
  * 是否在 VMM/Hypervisor 下运行。
  * 内核版本。
  * spl/zfs 模块参数的值。
* 可能记录在 `dmesg` 的堆栈回溯。

## OpenZFS 有行为准则吗？

有，OpenZFS 社区有行为准则。详情请参阅 [行为准则](https://openzfs.org/wiki/Code_of_Conduct)。
