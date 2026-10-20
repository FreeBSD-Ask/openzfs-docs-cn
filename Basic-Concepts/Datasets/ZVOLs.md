# ZVOL

zvol 是作为块设备而非文件系统导出的数据集。数据集该有的其他特性它一样不少——校验和、压缩、快照、克隆、复制、加密——同时向使用方呈现一个原始设备：虚拟机磁盘、iSCSI LUN、ZFS 未实现的文件系统，或交换空间。

```sh
zfs create -V 40G pool/vm/disk0
ls -l /dev/zvol/pool/vm/disk0
```

## 容量：`volsize` 与 `volblocksize`

### `volsize`

设备的逻辑大小。它必须是 `volblocksize` 的倍数，且不能为零。之后可以更改，但缩小它的危险程度与在活动文件系统下缩小任何块设备相同。

### `volblocksize`

固定的块大小。**只能在创建时设定**——此后除了重建卷并复制数据，无法更改。有效值是从 512 B 到 16 MiB 的 2 的幂；默认值为 16 KiB。

与文件系统的 `recordsize` 不同（后者是上限，ZFS 会按文件调整），`volblocksize` 对卷内每个块都是固定的。这使它成为影响最大的 zvol 决策。

指导原则是匹配使用方的 I/O 大小：

* 过于**小**：每次客户机 I/O 都要付出更多元数据代价，RAIDZ 的空间效率也会崩塌——RAIDZ 上的小块会接近镜像级别的开销（参见 [RAIDZ](../Pool-Structure/RAIDZ.md)）；
* 过于**大**：每次小写入都会变成对整个块的读-改-写，并且压缩要处理客户机并未更改的数据。

对于使用 4 KiB 块的客户机文件系统，8 KiB 到 64 KiB 是常见范围；默认的 16 KiB 是个合理的起点。针对不同工作负载的建议参见[工作负载调优](../../Performance-Tuning/WorkloadTuning.md)。

## 稀疏与厚置备

默认情况下，创建卷时还会建立与其大小相等的 `refreservation`，从而预先保证空间。此处刻意让预留量等于逻辑大小：没有它，卷可能在写入途中耗尽空间，而大多数使用方都处理不好这种情况。

`zfs create -s` 创建**稀疏**卷，不带预留：

```sh
zfs create -s -V 100G pool/vm/thin      # 稀疏
zfs create -V 100G pool/vm/thick        # 厚置备

zfs set refreservation=auto pool/vm/thin   # 之后改为厚置备
zfs set refreservation=none pool/vm/thick  # 之后改为稀疏
```

`refreservation=auto` 仅在卷上受支持，它会预留足够空间容纳整个 `volsize` 并计入元数据。

稀疏卷允许超售，代价是存储池填满时写入可能以 `ENOSPC` 失败——而客户机会把这视为硬件错误，而不是磁盘已满。超售意味着必须监控存储池空间。

还要注意，厚置备卷的快照也需要为预留留出空间，因此 `volsize` 并非全部代价。参见[配额与预留](Quotas-and-Reservations.md)。

## 设备如何呈现

`volmode` 控制操作系统看到什么：

### `full`（别名 `geom`）

完整的块设备，扫描并暴露其中的分区。

### `dev`

不带分区的设备。通常是虚拟机磁盘或 LUN 所需的形式——主机没有理由去扫描客户机的分区表。

### `none`

完全不向 ZFS 之外暴露。仍然可以快照、克隆和复制，适合作为纯备份目标。

### `default`

遵循系统级的 `zvol_volmode` 可调参数。

快照设备只在 `snapdev` 为 `visible` 时才出现在 `/dev/zvol/<pool>` 下；默认值为 `hidden`。卷没有 `.zfs/snapshot` 目录——要访问卷快照的内容，请克隆它并挂载克隆。

## 预留、快照与空间

zvol 的 `used` 可能超过客户机自认为正在使用的空间，有时差距巨大。原因在于：除非得到通知，ZFS 无法知道某个块已在客户机文件系统内部被释放；文件系统倾向于分配到新块而不是重用已释放的块，因此久而久之 ZFS 最终会引用客户机曾经触碰过的每个块。

解决办法是来自使用方的 discard/TRIM：

* 以 `discard` 挂载客户机文件系统，或定期运行 `fstrim`；
* 在制作快照**之前**发起 trim，否则快照会钉住客户机已视为空闲的块。

参见 [TRIM](../Operations/TRIM.md) 与 [FAQ](../../Project-and-Community/FAQ.md) 中关于 zvol 空间使用的条目。

## 在 zvol 上使用交换空间

可行，但需要小心；在 Linux 上，内存压力下仍可能死锁——参见 [issue #7734](https://github.com/openzfs/zfs/issues/7734)。如果你确实要这样做：

```sh
zfs create -V 4G -b $(getconf PAGESIZE) \
    -o logbias=throughput -o sync=always \
    -o primarycache=metadata \
    -o com.sun:auto-snapshot=false rpool/swap
```

让 `volblocksize` 匹配页面大小，让交换数据不进 ARC，并且绝不要为交换设备制作快照。

## 延伸阅读

* [zfsprops(7)](../../man/7/zfsprops.7.md)——`volsize`、`volblocksize`、`volmode`、`refreservation`、`snapdev`
* [zfs-create(8)](../../man/8/zfs-create.8.md)
* [数据集与属性](Datasets-and-Properties.md)、[数据集共享](../Operations/Sharing.md)
* [工作负载调优](../../Performance-Tuning/WorkloadTuning.md)——虚拟机与数据库两节
