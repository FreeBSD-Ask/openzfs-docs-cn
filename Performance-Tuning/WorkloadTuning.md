# 工作负载调优


## 基本概念

本文说明了对应用程序性能有影响的 ZFS 内部机制。

### 自适应替换缓存

几十年来，操作系统一直使用内存作为缓存，以避免等待极其缓慢的磁盘 I/O。这个概念称为页面替换。在 ZFS 出现之前，几乎所有文件系统都使用最近最少使用（LRU）的页面替换算法，其中最近最少使用的页面最先被替换。不幸的是，LRU 算法容易受到缓存刷新影响，即偶尔发生的短暂工作负载变化会将所有经常使用的数据从缓存中移除。为取代 LRU，ZFS 实现了自适应替换缓存（ARC）算法。它通过维护四个列表来解决这一问题：

1. 一个用于最近被缓存条目的列表。
2. 一个用于最近被缓存且被访问超过一次的条目的列表。
3. 一个用于从 #1 中被驱逐的条目的列表。
4. 一个用于从 #2 中被驱逐的条目的列表。

数据会从第一个列表中被驱逐，同时会尽力保留第二个列表中的数据。通过这种方式，ARC 能够通过提供更高的命中率而优于 LRU。

此外，可以向存储池中添加专用的缓存设备（通常是固态硬盘），使用 `zpool add POOLNAME cache DEVICENAME`。该缓存设备由 L2ARC 管理，它会扫描即将被驱逐的条目并将其写入缓存设备。可以分别通过 `primarycache` 和 `secondarycache` 这两个 zfs 属性控制存储在 ARC 和 L2ARC 中的数据，这些属性既适用于 zvol，也可以用于数据集。可选的设置值为 `all`、`none` 和 `metadata`。当某个 zvol 或数据集承载的应用程序本身实现了缓存机制时，仅缓存元数据可以提升性能。一个例子是使用 ZFS 的虚拟机。另一个例子是自行管理缓存的数据库系统（例如 Oracle）。相比之下，PostgreSQL 在很大程度上依赖操作系统级别的文件缓存。

### 对齐位移（ashift）

顶层 vdev 包含内部属性 ashift，即 alignment shift。它是在创建 vdev 时设置的，且不可更改。可以使用命令 `zdb` 读取。它被计算为任一子 vdev 的物理扇区大小的以 2 为底的最大对数，并据此改变磁盘格式，使写入始终按照该对齐方式进行。这使得 2^ashift 成为 vdev 上可能的最小 I/O。正确配置 ashift 非常重要，因为部分扇区写入会带来负面性能，即在写入之前必须先将该扇区读入缓冲区。ZFS 隐含地假设驱动器报告的扇区大小是正确的，然后据此计算 ashift。

在理想情况下，能够始终正确地报告物理扇区大小，因此无需对此加以关注。可惜，天不遂人愿。在基于闪存的固态硬盘出现之前，所有存储设备的扇区大小都是 512 字节。一些操作系统（例如 Windows XP）即是在这一假设下编写的，当驱动器报告不同的扇区大小时将无法正常工作。

大约在 2007 年，基于闪存的固态硬盘进入了市场。这些设备会报告 512 字节的扇区，但实际的闪存页（大致对应于扇区）从来都不是 512 字节。早期型号使用 4096 字节的页，而较新的型号已转向 8192 字节的页。此外，还出现了“Advanced Format”（AT，高级格式）硬盘，同样使用 4096 字节的扇区大小。部分页写入会遭受与部分扇区写入类似的性能下降。在某些情况下，NAND 闪存的设计会使这种性能下降更加严重，但这超出了本文的范围。

正确报告扇区大小是块设备层的职责。由于许多设备错误地报告其扇区大小，而 ZFS 又依赖块设备层来获取这些信息，因此各个平台都发展出了不同的变通方案。各平台特定的方法如下：

* illumos 上的 [sd.conf](http://wiki.illumos.org/display/illumos/ZFS+and+Advanced+Format+disks#ZFSandAdvancedFormatdisks-OverridingthePhysicalBlockSize)
* FreeBSD 上的 [gnop(8)](https://www.freebsd.org/cgi/man.cgi?query=gnop&sektion=8&manpath=FreeBSD+10.2-RELEASE)；例如参见 [在 4K 扇区驱动器上使用 FreeBSD](http://web.archive.org/web/20151022020605/http://ivoras.sharanet.org/blog/tree/2011-01-01.freebsd-on-4k-sector-drives.html)（2011-01-01）
* ZFS on Linux 上的 [ashift=](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/FAQ.html#advanced-format-disks)
* `-o ashift=` 同样适用于 MacZFS（存储池版本 8）和 ZFS-OSX（存储池版本 5000）。

`-o ashift=` 使用起来很方便，但它存在缺陷：当创建包含多个具有不同最优扇区大小的顶层 vdev 的存储池时，需要使用多条命令。已经讨论过一种[较新的语法](http://www.listbox.com/member/archive/182191/2013/07/search/YXNoaWZ0/sort/time_rev/page/2/entry/16:58/20130709002459:82E21654-E84F-11E2-A0FF-F6B47351D2F5/)，该语法将依赖于实际的扇区大小，作为跨平台替代方案，并且很可能在后续进行实现。

此外，ZFS on Linux 项目中还存在一个[已知错误报告扇区大小的驱动器数据库](https://github.com/openzfs/zfs/blob/master/cmd/zpool/os/linux/zpool_vdev_os.c#L98)。该数据库用于在无需系统管理员干预的情况下自动调整 ashift。当驱动器标识被模糊使用时（例如虚拟机、iSCSI LUN、某些罕见的固态硬盘），这种方法无法完全补偿错误报告的扇区大小，但它仍然带来了大量积极效果。其格式大致与 illumos 的 sd.conf 兼容，预计其他实现会在后续版本中集成该数据库。严格来说，这个数据库并不属于 ZFS，但由于对 Linux 内核打补丁（尤其是较旧版本）存在困难，因此有必要在 Linux 的 ZFS 实现中直接完成这一功能。MacZFS 的情况也是如此。然而，FreeBSD 和 illumos 都能够在正确的层面实现这一机制。

### 压缩

在内部，ZFS 使用设备扇区大小的整数倍来分配数据，通常是 512 字节或 4 KB（见上文）。当启用压缩时，可以为每个块分配更少数量的扇区。未压缩的块大小由 `recordsize`（默认 128 KB）或 `volblocksize`（自 v 2.2 起默认 16 KB）属性设置（分别用于文件系统与卷）。

以下是可用的压缩算法：

* LZ4

  * 在功能标志创建之后新增的算法。在所有测试指标中都显著优于 LZJB。它是 OpenZFS 中的[新的默认压缩算法](https://github.com/illumos/illumos-gate/commit/db1741f555ec79def5e9846e6bfd132248514ffe)（compression=on）。截至 2020 年，已在所有平台上可用。
* LZJB

  * ZFS 最初的默认压缩算法（compression=on）。它的设计目标是满足文件系统对压缩算法的需求，具体而言：提供适度的压缩率、较高的压缩速度、较高的解压速度，并能快速识别不可压缩的数据。
* GZIP（1 到 9）

  * 经典的 Lempel-Ziv 实现。它能提供较高的压缩率，但通常会使 I/O 受限于 CPU。
* ZLE（Zero Length Encoding）

  * 一种非常简单的算法，只压缩零值。
* ZSTD（Zstandard）

  * Zstandard 是一种现代的、高性能的通用压缩算法，能够提供与 GZIP 相当或更好的压缩率，但性能要好得多。Zstandard 提供了非常宽泛的性能、压缩率权衡范围，并且具有极其快速的解码器。自 [OpenZFS 2.0 版本](https://github.com/openzfs/zfs/pull/10278) 起可用。

如果你想使用压缩但不确定该选择哪个，请使用 LZ4。它的平均压缩率为 2.1:1，而 gzip-1 的平均压缩率为 2.7:1，但 gzip 要慢得多。这两个数据均来自 LZ4 项目在 Silesia 语料库上的[测试结果](https://github.com/lz4/lz4)。gzip 较高的压缩率通常只对很少访问的数据才值得使用。

### RAID-Z 条带宽度

根据你的 IOPS 需求以及你愿意为校验信息投入的空间数量来选择 RAID-Z 条带宽度。如果你需要更多的 IOPS，就在每个条带中使用更少的磁盘。如果你需要更多的可用空间，就在每个条带中使用更多的磁盘。几乎在所有情况下，试图基于精确数值来优化 RAID-Z 条带宽度都是没有意义的。更多细节请参见这篇[博客文章](https://www.delphix.com/blog/delphix-engineering/zfs-raidz-stripe-width-or-how-i-learned-stop-worrying-and-love-raidz/)。

### 数据集 recordsize

ZFS 数据集默认使用 128 KB 的内部 recordsize。数据集 recordsize 是用于文件内部写时复制的基本数据单位。部分记录写入要求必须从 ARC（成本低）或磁盘（成本高）中读取数据。recordsize 可以设置为从 512 字节到 1 MB 之间的任意 2 的幂。以固定记录大小写入的软件（例如数据库）将从使用匹配的 recordsize 中获益。

数据集上的 recordsize 变动只会对新文件生效。如果你因为应用程序在使用不同 recordsize 时性能会更好而更改了它，那么你需要重新创建这些文件。对每个文件执行一次 cp 再跟一次 mv 就足够了。或者，在进行一次完整接收时，send/recv 会以正确的 recordsize 重新创建文件。

#### 更大的 recordsize

在启用存储池特性 large_blocks 的情况下，最大支持 16 M 的 recordsize；在支持该特性的系统上，新建存储池默认启用该特性。

在 OpenZFS v 2.2 之前，默认禁用大于 1 M 的 recordsize，除非设置了 zfs_max_recordsize 内核模块参数以允许使用大于 1 M 的大小。

`zfs send` 操作必须指定 `-L`，以确保发送大于 128 KB 的块，并且接收端的存储池必须支持 large_blocks 特性。

### zvol volblocksize

Zvol 具有类似于 `recordsize` 的属性 `volblocksize`。当前默认值（自 v2.2 起为 16 KB）在大多数存储池配置中，由于 4 KB 磁盘物理块对齐（尤其是在 RAIDZ 和 DRAID 上），在元数据开销、压缩机会和空间效率之间取得了平衡，同时在使用较小块大小的客户文件系统上会产生一定的写放大 [7](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#volblocksize)。

建议用户测试自身场景，判断是否需要更改 `volblocksize` 以偏向某一目标：

* 客户文件系统的扇区对齐至关重要
* 大多数客户文件系统使用默认块大小为 4–8 KB，因此：

  * 较大的 `volblocksize` 有助于主要顺序工作负载，并可提高压缩效率
  * 较小的 `volblocksize` 有助于随机工作负载并最小化 IO 放大，但会使用更多元数据（例如，ZFS 会生成更多小型 IO）并可能降低空间效率（尤其是在 RAIDZ 和 DRAID 上）
  * 将 `volblocksize` 设置小于客户文件系统块大小或 [ashift](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#alignment-shift-ashift) 是没有意义的
  * 更多信息请参见 [数据集 recordsize](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#dataset-recordsize)

### 去重

去重使用基于磁盘的哈希表，采用 ZAP（ZFS Attribute Processor）中实现的[可扩展哈希](http://en.wikipedia.org/wiki/Extensible_hashing)。每个缓存条目会占用略多于 320 字节的内存。DDT 代码依赖 ARC 缓存 DDT 条目，因此不会产生双重缓存或内核内存分配器的内部碎片。每个存储池都有一个全局去重表，供在其上启用去重的所有数据集和 zvol 共享。哈希表中的每个条目记录了存储池中的一个唯一块。（块大小由属性 `recordsize` 或 `volblocksize` 设置。）

哈希表（也称为 DDT 或去重表）必须在每次写入或释放可去重块时访问（无论其是否有多个引用）。如果内存不足以缓存 DDT，每次缓存未命中都需要从磁盘读取随机块，从而导致性能下降。例如，在单个 7200 RPM 驱动器（可执行 100 io/s）的情况下，未缓存的 DDT 读取将限制整体写入吞吐量为每秒 100 块，使用 4 KB 块时约为 400 KB/s。

因此，为了获得良好性能，需要有足够的内存来存储去重数据。去重数据被视为元数据，因此如果将属性 `primarycache` 或 `secondarycache` 设置为 `metadata`，可以缓存去重数据。此外，去重表会与其他元数据竞争存储空间，这可能会对性能产生负面影响。可以使用 zdb 的选项 `-D` 模拟给定存储池所需的去重表条目数。然后通过简单地乘以 320 字节即可得到大致内存需求。或者，你也可以通过将计划在每个数据集上使用的存储量（考虑到部分记录在去重计算中按完整 recordsize 计数）除以 recordsize，每个 zvol 除以 volblocksize，再求和并乘以 320 字节，来估算唯一块数的上限。

### Metaslab 分配器

ZFS 顶层 vdev 被划分为 metaslab，从中可以独立分配块，以便并发 IO 在分配时互不阻塞。

默认情况下，metaslab 的选择偏向较低的 LBA，以提高转速磁盘的性能，但这种做法在固态介质上无意义。可以通过将 ZFS 模块的全局可调参数 `metaslab_lba_weighting_enabled` 设置为 0 来全局调整此行为。该可调参数仅建议在存储池仅使用固态介质的系统上使用。

当 metaslab 的空闲空间大于或等于 4% 时，metaslab 分配器将按首次适配（first-fit）分配块；当空闲空间小于 4% 时，将按最佳适配（best-fit）分配块。前者比后者快得多，但无法通过存储池的空闲空间判断何时发生这种行为。不过，命令 `zdb -mmm $POOLNAME` 可以提供该信息。

### 存储池几何结构

如果小型随机 IOPS 是首要考虑因素，镜像 vdev 的性能将优于 raidz vdev。镜像的读 IOPS 会随着每个镜像中的磁盘数量线性增加，而 raidz vdev 的 IOPS 将受到最慢磁盘的限制。

如果顺序写入是首要考虑因素，raidz 的性能将优于镜像 vdev。raidz 的顺序写入吞吐量会随着数据盘数量线性增加，而镜像 vdev 的写入速度受最慢磁盘限制。顺序读取性能在两者之间应大致相同。

无论是 raidz 还是镜像，每个顶层 vdev 的 IOPS 和吞吐量的总和都会增加整体的 IOPS 和吞吐量。

### 整盘与分区

在不同平台上，当提供整盘时，ZFS 的行为会有所不同。

在 illumos 上，ZFS 会尝试在整盘上启用写缓存。在启用写缓存时，illumos 的 UFS 驱动无法保证完整性，因此在默认情况下，使用 UFS 文件系统启动的 Sun/Solaris 系统出厂时驱动禁用了写缓存（很久以前，当 Sun 仍是独立公司时）。为了在 illumos 上的安全性，如果 ZFS 未被分配整盘，磁盘可能会与 UFS 共享，因此不适合让 ZFS 启用写缓存。在这种情况下，写缓存设置不会改变，将保持原样。如今，大多数厂商出厂时默认启用写缓存。

在 Linux 上，由于 ZFS 自带 IO 调度器，在很大程度上，Linux 的 IO 调度器是多余的。

当在 illumos 的 x86/amd64 平台或 Linux 上为整盘创建池时，ZFS 还会创建 GPT 分区表和自己的分区。这主要是为了能够通过 UEFI 进行启动，因为 UEFI 需要一个小的 FAT 分区以便启动系统。ZFS 驱动可以通过标签中的字段 `whole_disk` 判断池是否被分配了整盘。

在 FreeBSD 上不会这样做。FreeBSD 创建的存储池其 `whole_disk` 字段总是设置为 true，因此在其他平台导入由 FreeBSD 创建的存储池时，将始终被视为整盘已分配给 ZFS。

## 操作系统/发行版特定建议

### Linux

#### init_on_alloc

作为安全防护措施，一些 Linux 发行版（至少包括 Debian、Ubuntu）默认启用选项 `init_on_alloc`。此选项可以帮助[6](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#id38)：

> 防止可能的信息泄露，并使依赖未初始化值的控制流漏洞更具确定性。

可惜的是，它将显著降低 ARC 吞吐量（参见[漏洞](https://github.com/openzfs/zfs/issues/9910)）。

如果你准备应对这些安全风险[6](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#id38)，可以通过在 GRUB 内核启动参数中设置 `init_on_alloc=0` 来禁用 `init_on_alloc`。

## 通用建议

### 对齐位移

请确保创建存储池时，使 vdev 具有适合存储设备大小的正确对齐位移。如果使用闪存介质，这通常为 12（4K 扇区）或 13（8K 扇区）。对于 Amazon EC2 上的固态硬盘临时存储，正确的设置为 `12`。

### Atime 更新

将 `relatime=on` 或 `atime=off` 设置为最小化用于更新访问时间戳的 IO。为了向少量支持该特性的旧软件兼容，优先使用 `relatime`，并应在整个存储池上设置。应更有选择性地使用 `atime=off` 。

### 可用空间

保持存储池的可用空间在 10% 以上，避免许多 metaslab 达到 4% 的空闲空间阈值，从而从首次适配（first-fit）切换到最佳适配（best-fit）分配策略。当达到该阈值时，[Metaslab 分配器](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#metaslab-allocator) 会消耗大量 CPU 尝试保护自身免受碎片影响。这会降低 IOPS——尤其是当更多 metaslab 达到 4% 阈值时。

推荐使用 10% 而非 5%，因为 metaslab 选择会同时考虑位置和空闲空间，除非全局可调参数 `metaslab_lba_weighting_enabled` 设置为 `0`。当该可调参数为`0` 时，ZFS 仅考虑空闲空间，因此通过保持可用空间高于 5% 可以避免最佳适配分配器的开销。该设置应仅在存储池全部由固态硬盘组成的系统上使用，因为在机械硬盘上会降低顺序 IO 性能。

### LZ4 压缩

在存储池的根数据集上设置 `compression=lz4`，以便所有数据集继承该设置，除非有理由不启用。用户空间对单线程不可压缩数据的 LZ4 压缩测试显示，其处理速度可达 10 GB/秒，因此即使在不可压缩数据上也不太可能成为瓶颈。此外，不可压缩数据将以未压缩形式存储，因此启用压缩时读取不可压缩数据不会进行解压。写入速度非常快，因此不可压缩数据使用 LZ4 压缩也不太可能受到性能影响。LZ4 减少的 IO 通常会带来性能提升。

注意，较大的 recordsize 通过能让压缩算法一次处理更多数据，会提高可压缩数据的压缩比。

### NVMe 低级格式化

参见[NVMe 低级格式化](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Hardware.html#nvme-low-level-formatting)。

### 存储池几何结构

不要在 raidz 中放置超过约 16 块磁盘。当存储池已满时，机械磁盘的重建时间会过长。

### 同步 I/O

如果你的工作负载涉及 fsync 或 O_SYNC，且存储池使用机械存储，考虑添加一到多个 SLOG 设备。具有多个 SLOG 设备的存储池会在它们之间分配 ZIL 操作。SLOG 设备的最佳选择可能是 Optane / 3D XPoint SSD。参见[Optane / 3D XPoint SSD](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Hardware.html#optane-3d-xpoint-ssds)了解其描述。如果可以使用 Optane / 3D XPoint SSD，则无需继续阅读本节关于同步 I/O 的内容。如果无法使用 Optane / 3D XPoint SSD，请参见[NAND Flash SSD](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Hardware.html#nand-flash-ssds)获取 NAND 闪存 SSD 的建议，并阅读以下信息。

为了确保在基于 NAND 闪存固态硬盘的 SLOG 设备上取得最大的 ZIL 性能，你还应为备用区域进行预留空间以提高 IOPS [1](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#ssd-iops)。只需约 4 GB，其余部分可作为预留空间存储。选择 4 GB 有些任意，大多数系统在事务组提交之间写入 ZIL 的数据远小于 4 GB，因此将所有超出 4 GB 分区的存储作为预留空间通常是可以的。如果工作负载需要更多，不应超过最大 ARC 大小。即使在极端负载下，ZFS 也不会从超过最大 ARC 大小的 SLOG 存储中受益。在 Linux 上，最大 ARC 大小为系统内存的一半，在 illumos 上为系统内存的 3/4。

#### 通过安全擦除和分区表技巧预留空间

你可以通过安全擦除和分区表技巧组合来实现，如下所示：

1. 对 NAND 闪存 SSD 执行安全擦除。
2. 在 NAND 闪存 SSD 上创建分区表。
3. 创建一个 4 GB 分区。
4. 将该分区交给 ZFS 用作日志设备。

如果使用安全擦除和分区表技巧，请 **不要** 将未分区空间用于其他用途，即使是临时使用。那会通过标记页为脏页而降低或消除预留空间效果。

另外，一些设备能更改其报告的大小。这也可以实现，不过应在更改报告大小之前先执行安全擦除，以确保 SSD 识别额外的备用区域。在支持此功能的驱动器上，可以使用系统中的 `hdparm -N` 来更改报告大小。

#### NVMe 预留空间

在 NVMe 上，可以使用命名空间来实现预留空间：

1. 执行 sanitize 命令以确保设备完全清洁作为预防措施。
2. 删除默认命名空间。
3. 创建一个 4 GB 的新命名空间。
4. 将该命名空间交给 ZFS 用作日志设备，例如：`zfs add tank log /dev/nvme1n1`。

### 整盘

应将整盘分配给 ZFS，而非分区。如果必须使用分区，请确保分区正确对齐，以避免读-修改-写开销。有关正确对齐的说明，请参见[对齐位移 (ashift)](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#alignment-shift-ashift)章节。有关在分区上操作时 ZFS 行为变化的说明，请参见[整盘与分区](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#whole-disks-versus-partitions)章节。

来自 RAID 控制器的单盘 RAID 0 阵列不等同于整盘。[硬件 RAID 控制器](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Hardware.html#hardware-raid-controllers) 页面对此有详细说明。

## Bit Torrent

Bit torrent 执行 16 KB 的随机读/写。16 KB 的写操作会引发读-修改-写开销。当写入数据量超过系统内存时，128 KB 的 recordsize 会使读-修改-写开销降低性能最多 16 倍。可以通过为 Bit torrent 下载创建专用数据集并设置 `recordsize=16KB` 来避免此问题。

当文件通过 HTTP 服务器顺序读取时，由文件生成时的随机性造成的碎片会降低 7200 RPM 硬盘上的顺序读取性能约一半。如果性能是问题，可以通过以下两种方式之一顺序重写文件以消除碎片：

第一种方法是配置客户端将文件下载到临时目录，下载完成后再复制到最终位置，前提是客户端支持此操作。

第二种方法是使用 send/recv 顺序重建数据集。

实际上，对通过 Bit torrent 获取的文件进行碎片整理通常只会在文件存储在磁盘上且创建后会进行大量顺序读取时提升性能。


## 数据库工作负载

设置 `redundant_metadata=most` 可以通过消除间接块树最低层的冗余元数据，将 IOPS 提升至少几个百分点。但需要注意，如果指向数据块的元数据块损坏且没有重复副本，将会发生数据丢失，不过在镜像或 raidz vdev 的生产环境中，这通常不是问题。

### MySQL

#### InnoDB

为 InnoDB 的数据文件和日志文件创建单独的数据集。将 InnoDB 数据文件的 `recordsize` 设置为 16K，以避免昂贵的部分记录写入，并将日志文件的 `recordsize` 保持为 128K。在两者上设置 `primarycache=metadata`，以优先使用 InnoDB 的缓存[2](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#mysql-basic)。将数据集的 `logbias` 设置为 `throughput`，以阻止 ZIL 执行双写。

在 my.cnf 中设置 `innodb_doublewrite=0`，可防止 InnoDB 双写。双写是为了保护部分写入记录导致的损坏而设计的数据完整性特性，但在 ZFS 上不会出现这种情况。需要注意的是，[Percona 博客曾建议](https://www.percona.com/blog/2014/05/23/improve-innodb-performance-write-bound-loads/) 在 ext4 配置中关闭双写以提升性能，但后来收回了建议，因为这会导致数据损坏。在适时断电后，像 ext4 这样的就地文件系统可能会出现 8 KB 记录的一半是旧数据，而另一半是新数据。这就是导致 Percona 收回建议的损坏原因。然而，ZFS 的写时复制设计会在断电后返回旧的正确数据（无论时序如何），从而防止了双写特性旨在避免的损坏。因此，在 ZFS 上双写功能是多余的，可以安全关闭来获得更高性能。

在 Linux 上，驱动的 AIO 实现只是兼容性 shim，仅勉强满足 POSIX 标准。使用 InnoDB 默认 AIO 路径会影响性能。在 `my.cnf` 中设置 `innodb_use_native_aio=0` 和 `innodb_use_atomic_writes=0` 以禁用 AIO。必须同时禁用这两个设置才能完全禁用 AIO。

### PostgreSQL

为 PostgreSQL 的数据和 WAL 创建单独的数据集。在两者上设置 `compression=lz4` 和 `recordsize=32K`（64K 也可，128K 默认值也可）。为 PostgreSQL 配置 `full_page_writes = off`，因为 ZFS 永远不会提交部分写入。对于更新量大的数据库，可以在 PostgreSQL 的数据上尝试设置 `logbias=throughput` 以避免双写，但需注意，使用此设置时较小的更新可能导致严重碎片化。

### SQLite

为数据库创建单独的数据集。将 `recordsize` 设置为 64K。将 SQLite 页大小设置为 65536 字节[3](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#sqlite-ps)。

请注意，SQLite 数据库通常使用频率不足以需要特殊调优，但上述设置可实现优化。请参考 SQLite.org 提到的缓存大小副作用[4](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#sqlite-ps-change)。

## 文件服务器

为被服务的文件创建专用数据集。

有关配置建议，请参见[顺序工作负载](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#sequential-workloads)。

### Samba

Windows/DOS 客户端不支持区分大小写的文件名。如果你的主要工作负载不需要对其他支持的客户端进行大小写敏感操作，可使用 `zfs create -o casesensitivity=insensitive` 创建数据集，以便 Samba 后续能更快地搜索文件名[5](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#fs-casefold-fl)。

请参见 [smb.conf(5)](https://www.samba.org/samba/docs/current/man-html/smb.conf.5.html) 中的 `case sensitive` 选项。

## 顺序工作负载

对受顺序工作负载影响的数据集设置 `recordsize=1M`。在设置 1M recordsize 前，请阅读[更大记录大小](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#larger-record-sizes) 以了解相关注意事项。

根据通用建议，为数据集设置 `compression=lz4`，[LZ4 压缩](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#lz4-compression)。

## 视频游戏目录

创建专用数据集，使用 `chown` 使其对用户可访问（或在其下创建目录并对该目录使用 `chown`），然后配置游戏下载应用将游戏放置在此目录下。各应用的具体配置方法如下。

在安装游戏前，请参阅[顺序工作负载](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#sequential-workloads)获取配置建议。

请注意，此调优带来的性能提升可能较小，仅限于加载时间。然而，1M recordsize 与 LZ4 的组合可以存储更多游戏，这也是该调优被记录的原因。对应用了这些调整的 300 款游戏（大多数来自 Humble Bundle）的 Steam 库，观察到节省空间 20%。在可压缩游戏上进行此调优，可同时实现更快的加载时间和显著的空间节约。游戏资产已压缩的情况下，几乎不会获得任何好处。

### Lutris

左键点击右上角的三条杠图标打开上下文菜单。进入“Preferences”，然后切换到“System options”标签。更改默认安装目录并点击保存。

### Steam

进入“Settings” -> “Downloads” -> “Steam Library Folders”，使用“Add Library Folder”设置 Steam 存储游戏的目录。关闭对话框前，右键该目录并选择“Make Default Folder”以将其设为默认。

如果你打算使用 Proton 运行非原生游戏，请创建数据集 `zfs create -o casesensitivity=insensitive`，以便 Wine 后续能更快地搜索文件名[5](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#fs-casefold-fl)。

## Wine

Windows 文件系统的标准行为不区分大小写。请创建数据集 `zfs create -o casesensitivity=insensitive`，以便 Wine 后续能更快地搜索文件名[5](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#fs-casefold-fl)。

## 虚拟机

ZFS 上的虚拟机镜像应使用 zvol 或原始文件存储，可避免不必要的开销。可以配置 recordsize/volblocksize 与虚拟机文件系统匹配，从而避免部分记录修改带来的开销，参见[zvol volblocksize](https://openzfs.github.io/openzfs-docs/Performance%20and%20Tuning/Workload%20Tuning.html#zvol-volblocksize)。如果使用原始文件，应使用单独的数据集，以便独立于 ZFS 上存储的其他内容配置 recordsize。

### QEMU / KVM / Xen

在使用文件作为虚拟机存储时，应使用 AIO 以最大化 IOPS。
