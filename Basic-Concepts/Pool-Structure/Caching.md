# 缓存与辅助设备

ZFS 有一个位于内存中的读缓存（ARC），一个可选的位于磁盘上的二级读缓存（L2ARC），以及两类常被误认为缓存、实则并非缓存的写入路径设备：独立意图日志（SLOG）与特殊分配类。

添加设备容易，撤销却不容易，因此有必要弄清每种设备实际解决的是哪个问题。

## ARC

自适应替换缓存（ARC）是 ZFS 的内存缓存。它同时保留最近使用与频繁使用的块，并在两者之间自适应调整比例，这就是它通常优于简单的 LRU 页缓存的原因。

`primarycache` 按数据集控制哪些内容可以进入 ARC：`all`（默认）、`metadata` 或 `none`。

```sh
zfs set primarycache=metadata pool/bigsequentialdata
zarcsummary                    # OpenZFS 2.4.0 之前为 arc_summary
zarcstat 1                     # OpenZFS 2.4.0 之前为 arcstat
cat /proc/spl/kstat/zfs/arcstats
```

内存是迄今为止最有效的 ZFS“调优旋钮”。在添加任何缓存设备之前，先确认 ARC 是否只是太小了——关于 `zfs_arc_max` 等参数，参见 [zfs(4)](../../man/4/zfs.4.md)。

## L2ARC（`cache` vdev）

缓存设备是位于内存与存储池之间的二级读缓存。当工作集远大于内存，且工作负载是 **对大体静态内容的随机读取** 时，它才有帮助。它对写入毫无作用。

```sh
zpool add pool cache nvme0n1
zfs set secondarycache=metadata pool/data      # all | metadata | none
```

缓存设备的特性：

* 它们不能被镜像，也不能成为 raidz 组的一部分。读取出错时只会转向存储池重新读取，因此丢掉一个并无危害。
* 其内容在重启后仍然保留（持久化 L2ARC），并在导入时异步恢复。可通过 `l2arc_rebuild_enabled=0` 禁用。小于 1 GiB 的设备不会获得重建所需的元数据。
* **L2ARC 消耗内存。** 每个缓存的块都需要在 ARC 中有一个表头，因此过大的 L2ARC 会挤占真正重要的缓存。在内存受限的系统上，L2ARC 可能让事情变慢。

## SLOG（`log` vdev）

ZFS 意图日志满足 POSIX 的持久性要求：`fsync()` 与 `O_SYNC` 写入必须在调用返回前落到稳定存储。ZIL 存在于每个存储池中——默认从主存储池的块中分配。`log` vdev 只是把它移到专用设备上。

```sh
zpool add pool log mirror nvme0n1 nvme1n1
```

有必要精确说明的几点：

* SLOG **不是写缓存** 。异步写入从不接触 ZIL；它们在内存中聚合，并在下一个事务组写出。如果你的工作负载没有同步写入，SLOG 不会带来任何变化。
* 它只在崩溃之后被*读取*，用于重放尚未提交的内容。
* 它应当是具备掉电保护的低延迟设备。没有掉电保护的消费级 SSD 照样会把数据报告为已稳定，而断电随即将其丢失。
* 多个日志设备可以负载均衡，也可以镜像；意图日志不支持 raidz。

典型受益者：NFS 服务器、数据库，以及运行同步写入密集型客户机的虚拟机宿主。`sync` 与 `logbias` 数据集属性控制其行为——`logbias=throughput` 会让数据集绕过日志设备，`sync=disabled` 则完全跳过 ZIL，以牺牲近期写入的持久性换取速度。

## 特殊 vdev（`special` 分配类）

特殊 vdev 也不是缓存——它是永久存放某一特定类块的存储：元数据、用户数据的间接块、去重表，以及可选的小文件块。

```sh
zpool add pool special mirror nvme0n1 nvme1n1
```

把元数据放在闪存上，通常是机械盘存储池所能获得的最大单项收益：目录遍历、`zfs list`、scrub 与 resilver 都会显著加快。但由于这些块*只*存在于该 vdev 上，它的冗余程度必须与存储池其余部分相当；而且在 raidz 存储池上，它一旦加入就再也无法移除。

这个主题的坑足够多，值得单独成页——参见[特殊 vdev](Special-vdev.md)。

## 如何在它们之间选择

| 症状                              | 有效手段             | 之后可否移除            |
| :-------------------------------- | :------------------- | :---------------------- |
| 读取慢，ARC 相对工作集过小        | 增加内存，其次 L2ARC | 可以                    |
| 同步写入慢（NFS、数据库、虚拟机） | 具备掉电保护的 SLOG  | 可以                    |
| 机械盘上元数据操作慢              | 特殊 vdev（镜像）    | 仅当存储池不含 raidz 时 |
| 去重表频繁换入换出                | 去重 vdev（镜像）    | 同特殊 vdev             |

## 延伸阅读

* [zpoolconcepts(7)](../../man/7/zpoolconcepts.7.md)——`Intent Log`、`Cache Devices`、`Special Allocation Class`
* [zfsprops(7)](../../man/7/zfsprops.7.md)——`primarycache`、`secondarycache`、`special_small_blocks`、`logbias`、`sync`
* [VDEV](VDEV.md)、[工作负载调优](../../Performance-Tuning/WorkloadTuning.md)、[zfs(4)](../../man/4/zfs.4.md)
