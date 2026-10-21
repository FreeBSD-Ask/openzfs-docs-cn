# 更改存储池布局

存储池并非一成不变，但可用的操作因 vdev 类型而差别极大——其中一些还是单向的。本页汇总了哪些可以添加、扩展、替换以及撤回。

vdev 的术语见[虚拟设备（VDEV）](VDEV.md)，raidz 的几何结构见 [RAIDZ](RAIDZ.md)。

## 增加容量

`zpool add` 追加一个新的顶级 vdev。存储池在所有顶级 vdev 之间条带化，因此新 vdev 立即开始接受写入，但既有数据不会重新平衡。

```sh
zpool add pool mirror sdc sdd
zpool add -n pool mirror sdc sdd     # 试运行——打印结果布局
```

让新 vdev 的冗余与既有 vdev 相匹配。`zpool add` 会对不匹配给出警告（例如向镜像池添加一块裸盘）；用 `-f` 覆盖该警告，会给存储池引入单点故障，而当涉及 raidz 时这种操作无法撤销。

## 扩展既有 vdev

**更大的磁盘。** 用更大的设备逐一替换 vdev 中的每块设备，每次等待 resilver 完成。只有该镜像或 raidz 组中的*每一块*设备都被替换之后，空间才会变为可用。

```sh
zpool set autoexpand=on pool          # 默认值为 off
zpool replace pool sda sdX
# ……或者在底层扩展了 LUN 之后：
zpool online -e pool sda
```

`autoexpand=on` 在设备容量增大时自动调整存储池大小；否则由 `zpool online -e` 显式执行。

**RAIDZ 扩展。** 可以把一块设备附加到既有 raidz vdev 上以加宽它：

```sh
zpool attach pool raidz2-0 sdX
```

这会读取所有已分配数据，并在更宽的组上重写；`zpool status` 显示进度。整个过程中冗余始终得以维持；若某块磁盘故障，扩展会暂停，直到该 vdev 恢复健康。需要明确的几点：

* 容错能力不变——RAID-Z2 依然是 RAID-Z2。
* 旧块保持原有的数据与校验比例，只是分布在更多磁盘上；只有新块使用更宽的比例。因此在旧数据被重写之前，报告的空闲空间可能略微偏保守。
* 一个 raidz vdev 可以被扩展不止一次。

## 镜像

对镜像或普通设备执行 `zpool attach` 会增加一侧：单盘变成双向镜像，双向变成三向。新设备立即开始 resilver，正在运行的 scrub 会被取消。`zpool detach` 移除一侧。

```sh
zpool attach pool sda sdb        # sda 变为双向镜像
zpool attach -s pool sda sdb     # 顺序重建，随后自动 scrub
zpool detach pool sdb
```

`zpool split` 从每个镜像中各剥离一块设备，组成新的存储池——即整个存储池的一份即时、一致的副本。每个顶级 vdev 都必须是镜像，且不得有 resilver 正在进行。

```sh
zpool split pool newpool
```

## 替换故障设备

```sh
zpool replace pool sda sdX       # 新设备位于不同的插槽
zpool replace pool sda           # 同一插槽，设备已更换
zpool set autoreplace=on pool
```

`autoreplace=on` 让 ZFS 格式化并替换出现在此前属于该池的设备物理位置上的任何新设备；默认值为 `off`。后续过程见 [Scrub 与 resilver](../Operations/Scrub-and-Resilver.md)。

## 热备

`spare` vdev 空闲待命，直到某个活动设备故障，随后自动顶替其位置。

```sh
zpool create pool mirror sda sdb spare sdc
zpool add pool spare sdd
zpool remove pool sdd
```

一旦某个 spare 顶替上来，配置中就会出现一个新的 `spare` vdev，并一直保留，直到原设备被真正替换——那时该 spare 恢复为可用状态。因此 spare 只是争取时间的权宜之计，而不是替代品：故障磁盘仍然必须更换。

```sh
zpool replace pool sda sdNEW    # 随后 spare 自行释放
zpool detach pool sdc           # 取消正在进行的 spare 顶替
```

若改为分离*原先故障的设备*，则该 spare 会永久占据其位置，并从所有使用它的存储池的 spare 列表中移除。

spare 可以在存储池之间共享，但这带来真实风险：当前正在使用某个共享 spare 的存储池无法导出；若两个存储池在不同主机上导入，并且同时各丢失一块设备，二者可能争用同一个 spare——这种情况不会被检测到，且可能损坏数据。只应在同一台主机内共享 spare。

dRAID 有自己内置的分布式 spare 容量，resilver 速度快得多；参见 [dRAID](dRAID-Howto.md)。

## 移除设备

`zpool remove` 处理热备、缓存与日志设备毫不费力。移除 **顶级数据 vdev** 则是受限的情形：它在后台把该 vdev 上已分配的数据复制到别处来腾空它，并永久缩小存储池。

```sh
zpool remove pool mirror-1
zpool remove -n -p pool mirror-1     # 先估算映射表的开销
zpool status pool                    # 跟踪迁移进度
```

只有以下条件全部成立时才可行：

* 存储池中 **没有** 任何顶级 raidz 或 draid vdev，
* 所有顶级 vdev 具有相同的 `ashift`，
* 所有加密数据集的密钥均已加载，
* 已启用 `device_removal` 特性。

移除操作会为被迁移的块留下一张内存中的映射表，它在存储池的整个生命周期内都占用内存——`-n -p` 会报告占用量。迁移过程中出现 I/O 错误会取消移除。

要把一块设备从镜像中取出，请使用 `zpool detach`，而不是 `remove`。

> **警告**
>
> **raidz 存储池无法缩小。** 如果存储池含有任何 raidz 或 draid 顶级 vdev，则任何顶级 vdev 都永远无法移除——包括后来添加的 `special` 或 `dedup` vdev，也包括误加的一块普通磁盘。唯一的补救办法是重建存储池并恢复数据。务必先用 `zpool add -n` 试运行。

## 导入与导出

```sh
zpool export pool
zpool import                     # 列出可导入的存储池
zpool import pool
zpool import -d /dev/disk/by-id pool
zpool import -o readonly=on -N pool
```

导出会刷写所有内容，并把存储池标记为已干净分离，这正是使它可以安全迁移到另一系统的原因。`-d` 选择扫描哪些设备路径——使用 `/dev/disk/by-id` 可以避免 `sdX` 名称在多次启动之间变动的经典问题。关于选择 `/dev/` 名称，参见 [FAQ](../../Project-and-Community/FAQ.md)。

## 检查点

存储池检查点是整个存储池的撤销点，用于升级等有风险的管理操作：

```sh
zpool checkpoint pool
# ……如果情况不妙：
zpool export pool
zpool import --rewind-to-checkpoint pool
# ……如果一切正常：
zpool checkpoint -d pool
```

检查点存在期间，`zpool remove`、`attach`、`detach`、`split` 与 `reguid` 全部被禁止；它固定的空间也可能在空闲不足的存储池上突破预留边界。`zpool status` 显示检查点是否存在，`zpool list` 显示它占用了多少空间。一旦确认操作无误，就应立即丢弃它。

## 延伸阅读

* [zpool-add(8)](../../man/8/zpool-add.8.md)、[zpool-attach(8)](../../man/8/zpool-attach.8.md)、[zpool-detach(8)](../../man/8/zpool-detach.8.md)
* [zpool-replace(8)](../../man/8/zpool-replace.8.md)、[zpool-remove(8)](../../man/8/zpool-remove.8.md)、[zpool-split(8)](../../man/8/zpool-split.8.md)
* [zpool-import(8)](../../man/8/zpool-import.8.md)、[zpool-export(8)](../../man/8/zpool-export.8.md)、[zpool-checkpoint(8)](../../man/8/zpool-checkpoint.8.md)
* [zpoolprops(7)](../../man/7/zpoolprops.7.md)——`autoexpand`、`autoreplace`
