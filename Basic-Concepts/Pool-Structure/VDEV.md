# 虚拟设备（VDEV）

## 什么是 VDEV？

vdev（virtual device，虚拟设备）是 ZFS 存储池的基本构建单元。它代表物理存储设备的逻辑组合，例如硬盘、固态硬盘或分区。

## 什么是叶子 vdev？

叶子 vdev 是最基本的 vdev 类型，直接对应于物理存储设备。叶子 vdev 是 ZFS 存储层级中的终端节点。

## 什么是顶级 vdev？

顶级 vdev 是根 vdev 的直接子节点。顶级 vdev 既可以是单个设备，也可以是聚合多个叶子 vdev 的逻辑组（如镜像或 RAIDZ 组）。ZFS 会在池中的所有顶级 vdev 上动态条带化数据。

## 什么是根 vdev？

根 vdev 位于池层级的顶部。根 vdev 将所有顶级 vdev 聚合为一个逻辑存储单元（即存储池）。

## 不同类型的 vdev

OpenZFS 支持多种类型的 vdev。顶级 vdev 承载数据，提供冗余：

* **单设备（Single device）** ：由单独一块磁盘、一个文件或一个分区充当的顶级 vdev。它不提供冗余，一旦丢失，整个池都会丢失。注意 ZFS 中并不存在“stripe” vdev 类型——条带化是池在其各顶级 vdev **之间** 做的事，而不是一种独立的 vdev。
* **镜像（Mirror）** ：将相同数据存储在两块或多块磁盘上的 vdev，可提供冗余。
* [RAIDZ](RAIDZ.md)：通过校验提供容错能力的 vdev，类似传统 RAID 5/6。RAIDZ 有三个等级：

  * **RAIDZ1** ：单重校验，类似 RAID 5。至少需要 2 块磁盘（推荐 3 块以上），可容忍一块磁盘故障。
  * **RAIDZ2** ：双重校验，类似 RAID 6。至少需要 3 块磁盘（推荐 5 块以上），可容忍两块磁盘故障。
  * **RAIDZ3** ：三重校验。至少需要 4 块磁盘（推荐 7 块以上），可容忍三块磁盘故障。

* [dRAID](dRAID-Howto.md)：分布式 RAID。提供分布式校验与热备盘，可在多块磁盘间分布冗余，从而在故障后实现更快的重建性能。

辅助 vdev 提供特定功能：

* **热备盘（Spare）** ：充当热备盘的磁盘，可在另一个 vdev 中的磁盘发生故障时自动替换故障磁盘。
* **缓存（Cache，L2ARC）** ：二级 ARC vdev，用于缓存频繁访问的数据，提高随机读取性能。它只保存池中已有数据的第二份副本，因此丢失它并无影响。
* **日志（Log，SLOG）** ：独立日志 vdev，用于存储 ZFS 意图日志（ZIL），提升同步写入性能。它不是写缓存——只有同步写入才会用到它。
* **特殊（Special）** ：专用于存储元数据，并可选存储小文件块和去重表（DDT）的 vdev。
* **去重（Dedup）** ：专门用于存储去重表（DDT）的 vdev。

`special` 与 `dedup` vdev 是池中这些块唯一的数据来源，因此它们必须与池中普通 vdev 具有同样的冗余——丢失一个就会丢池。关于何时值得添加这些设备，参见[缓存与辅助设备](Caching.md)。

## vdev 与存储池的关系

vdev 是 ZFS 存储池的构建单元。存储池（zpool）通过组合一个或多个顶级 vdev 创建。存储池的整体性能、容量和冗余取决于所使用的 vdev 类型和配置。

下面的示例布局来自 [zpool-status(8)](../../man/8/zpool-status.8.md) 输出，展示了一个拥有两个 RAIDZ1 顶级 vdev 和 10 个叶子 vdev 的存储池：

```sh
   datapoolname (root vdev)
     raidz1-0 (top-level vdev)
       /dev/dsk/disk0 (leaf vdev)
       /dev/dsk/disk1 (leaf vdev)
       /dev/dsk/disk2 (leaf vdev)
       /dev/dsk/disk3 (leaf vdev)
       /dev/dsk/disk4 (leaf vdev)
     raidz1-1 (top-level vdev)
       /dev/dsk/disk5 (leaf vdev)
       /dev/dsk/disk6 (leaf vdev)
       /dev/dsk/disk7 (leaf vdev)
       /dev/dsk/disk8 (leaf vdev)
       /dev/dsk/disk9 (leaf vdev)
```

## ZFS 如何处理 vdev 故障？

ZFS 的冗余位于顶级 vdev **内部** ，而不是跨顶级 vdev 之间。镜像即使损失除一块之外的所有叶子 vdev 仍能存活；raidz*N* 可承受 *N* 块故障。当叶子 vdev 发生故障时，ZFS 会将其标记为“faulted”，继续由同一顶级 vdev 中存活的成员提供读写，并从这些成员重建缺失的数据。

更值得注意的是其推论： **顶级 vdev 一旦丢失，池就丢失。** 因为数据条带化分布在所有顶级 vdev 之上，其他任何地方都没有其内容的副本。因此，在一个原本由镜像组成的池中加入单块非冗余磁盘，会让整个池的存亡取决于这一块磁盘。

管理员可以用 [zpool-replace(8)](../../man/8/zpool-replace.8.md) 将故障的叶子 vdev 更换为新设备，ZFS 会自动将数据 resilver（重建）到新设备上，使池恢复健康状态。参见 [Scrub 与 Resilver](../Operations/Scrub-and-Resilver.md)。

## 如何管理 ZFS 中的 vdev？

vdev 可通过 [zpool(8)](../../man/8/zpool.8.md) 命令行工具进行管理。常用操作包括：

* **创建存储池** ：`zpool create` 可指定 vdev 布局。参见 [zpool-create(8)](../../man/8/zpool-create.8.md)。
* **添加 vdev** ：`zpool add` 将新的顶级 vdev 附加到现有池中，扩展容量和性能（通过增加条带宽度）。参见 [zpool-add(8)](../../man/8/zpool-add.8.md)。
* **扩容 vdev** ：`zpool attach` 为镜像或现有 raidz 组添加设备（RAIDZ 扩容）。参见 [zpool-attach(8)](../../man/8/zpool-attach.8.md)。
* **移除 vdev** ：`zpool remove` 可以移除某些类型的顶级 vdev，并将其数据迁移到其他 vdev。如果池中包含 raidz 或 draid 顶级 vdev，则完全无法移除。参见 [zpool-remove(8)](../../man/8/zpool-remove.8.md)。
* **更换磁盘** ：`zpool replace` 将用新磁盘替换故障或容量较小的磁盘。参见 [zpool-replace(8)](../../man/8/zpool-replace.8.md)。
* **监控状态** ：`zpool status` 将显示所有 vdev 的健康状况和布局。参见 [zpool-status(8)](../../man/8/zpool-status.8.md)。
* **监控性能** ：`zpool iostat` 将显示存储池及各 vdev 的 I/O 统计信息。参见 [zpool-iostat(8)](../../man/8/zpool-iostat.8.md)。

[更改存储池布局](Changing-Pool-Layout.md)详细说明了这些操作及其约束。

