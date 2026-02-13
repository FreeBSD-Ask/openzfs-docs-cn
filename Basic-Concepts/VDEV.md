# 虚拟设备（VDEV）

## 什么是 VDEV？

vdev（virtual device，虚拟设备）是 ZFS 存储池的基本构建单元。它意味着物理存储设备的逻辑组合，例如硬盘、固态硬盘或分区。

## 什么是叶子 vdev？

叶子 vdev 是最基本类型的 vdev，直接对应于物理存储设备。叶子 vdev 是 ZFS 存储层级中的终端节点。

## 什么是顶级 vdev？

顶级 vdev 是根 vdev 的直接子节点。顶级 vdev 可以是单个设备，也可以是多个叶子 vdev 逻辑组（如镜像或 RAIDZ 组）的聚合。ZFS 会在池中的所有顶级 vdev 上动态条带化数据。

## 什么是根 vdev？

根 vdev 位于池层级的顶部。根 vdev 将所有顶级 vdev 聚合为一个逻辑存储单元（即存储池）。

## 不同类型的 vdev

OpenZFS 支持多种类型的 vdev。顶级 vdev 承载数据，提供冗余：

* **条带磁盘（Striped Disk(s)）**：由一到多个物理设备组成的条带化 vdev（类似 RAID 0）。未提供冗余，若磁盘故障会数据将丢失。
* **镜像（Mirror）**：将相同数据存储在两块或多块磁盘上的 vdev，可提供冗余。
* [RAIDZ](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/RAIDZ.html)：通过校验提供容错能力的 vdev，类似传统 RAID 5/6。RAIDZ 有三个等级：

  > * **RAIDZ1**：单重校验，类似 RAID 5。至少需要 2 块磁盘（推荐 3 块以上），可容忍一块磁盘故障。
  > * **RAIDZ2**：双重校验，类似 RAID 6。至少需要 3 块磁盘（推荐 5 块以上），可容忍两块磁盘故障。
  > * **RAIDZ3**：三重校验。至少需要 4 块磁盘（推荐 7 块以上），可容忍三块磁盘故障。
* [dRAID](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/dRAID%20Howto.html)：分布式 RAID。提供分布式校验和热备盘，可在多块磁盘间分布冗余，从而在故障后实现更快的重建性能。

辅助 vdev 提供特定功能：

* **热备盘（Spare）**：作为热备盘的磁盘，可在另一个 vdev 出现故障时自动替换。
* **缓存（Cache，L2ARC）**：二级 ARC vdev，用于缓存频繁访问的数据，提高随机读取性能。
* **日志（Log，SLOG）**：独立日志 vdev，用于存储 ZFS 意图日志（ZIL），提升同步写入性能。
* **特殊（Special）**：专用于存储元数据，并可选存储小文件块和重复数据表（DDT）的 vdev。
* **重复数据表（Dedup）**：专门用于存储重复数据表（DDT）的 vdev。

## vdev 与存储池的关系

vdev 是 ZFS 存储池的构建单元。存储池（zpool）通过组合一个或多个顶级 vdev 创建。存储池的整体性能、容量和冗余取决于所使用的 vdev 类型和配置。

下面是示例布局，来自 [zpool-status(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html) 输出，显示了一个拥有两个 RAIDZ1 顶级 vdev 和 10 个叶子 vdev 的存储池：

```sh
数据池名 (根 vdev)
raidz1-0 (顶级 vdev)
/dev/dsk/disk0 (叶子 vdev)
/dev/dsk/disk1 (叶子 vdev)
/dev/dsk/disk2 (叶子 vdev)
/dev/dsk/disk3 (叶子 vdev)
/dev/dsk/disk4 (叶子 vdev)
raidz1-1 (顶级 vdev)
/dev/dsk/disk5 (叶子 vdev)
/dev/dsk/disk6 (叶子 vdev)
/dev/dsk/disk7 (叶子 vdev)
/dev/dsk/disk8 (叶子 vdev)
/dev/dsk/disk9 (叶子 vdev)
```


## ZFS 如何处理 vdev 故障？

ZFS 设计为能够优雅地处理 vdev 故障。如果一个 vdev 发生故障，只要存储池的冗余级别允许（例如在镜像、RAIDZ 或 dRAID 配置中），ZFS 可以继续使用池中剩余的 vdev 运行。当池中仍有足够冗余时，ZFS 会将故障的 vdev 标记为“faulted”（故障），并从剩余的 vdev 中恢复数据。管理员可以使用 [zpool-replace(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html) 将故障 vdev 替换为新 vdev，ZFS 会自动将数据重建（resilver）到新 vdev 上，使存储池恢复健康状态。

## 如何管理 ZFS 中的 vdev？

vdev 可通过 [zpool(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zpool.8.html) 命令行工具进行管理。常用操作包括：

* **创建存储池**：`zpool create` 可指定 vdev 布局。参见 [zpool-create(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-create.8.html)。
* **添加 vdev**：`zpool add` 将新的顶级 vdev 附加到现有池中，扩展容量和性能（通过增加条带宽度）。参见 [zpool-add(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-add.8.html)。
* **移除 vdev**：`zpool remove` 可以移除某些类型的顶级 vdev，并将其数据迁移到其他 vdev。参见 [zpool-remove(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-remove.8.html)。
* **更换磁盘**：`zpool replace` 将用新磁盘替换故障或容量较小的磁盘。参见 [zpool-replace(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-replace.8.html)。
* **监控状态**：`zpool status` 将显示所有 vdev 的健康状况和布局。参见 [zpool-status(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-status.8.html)。
* **监控性能**：`zpool iostat` 将显示存储池及各 vdev 的 I/O 统计信息。参见 [zpool-iostat(8)](https://openzfs.github.io/openzfs-docs/man/master/8/zpool-iostat.8.html)。

