# 快照、克隆与书签

由于 ZFS 从不就地修改块，保留数据集的旧版本，代价不过是对当时处于活动状态的块的一次引用。快照、克隆与书签都建立在这一基础之上。

## 快照

快照是文件系统或卷在某一时刻的只读副本。创建几乎瞬间完成，且初始不占用额外空间；当活动数据集发生偏离，只有快照引用的块无法再被释放时，它才开始计入空间。

快照是原子的——它包含该时间点之前完成的所有系统调用。使用 `-r` 递归创建的快照全部在同一瞬间生成，这使得递归快照可以作为跨越多个数据集的一致镜像使用。

```sh
# 为单个数据集创建快照
zfs snapshot pool/home/user@monday

# 原子地为数据集及其所有后代创建快照
zfs snapshot -r pool/home@monday

# 列出快照（默认情况下它们不会出现在普通的 "zfs list" 中）
zfs list -t snapshot -r pool/home
```

除非指定 `-t snapshot`，`zfs list` 会省略快照；存储池属性 `listsnapshots`（默认 `off`）可为整个存储池更改这一默认行为。

### 访问快照内容

文件系统快照可通过文件系统根目录下的 `.zfs/snapshot` 目录访问，无需显式挂载——它们按需挂载，一段时间后再卸载。因此恢复单个文件就是一次普通的 `cp`：

```sh
cp /home/user/.zfs/snapshot/monday/notes.txt /home/user/notes.txt
```

`snapdir` 属性控制 `.zfs` 目录是 `disabled`、`hidden`（默认——目录存在，但不会出现在 `ls` 中）还是 `visible`。

卷没有可浏览的目录。当卷的 `snapdev` 属性设为 `visible` 时，快照设备节点会出现在 `/dev/zvol/<池>` 下；默认值为 `hidden`。

### 回滚

`zfs rollback` 会丢弃自该快照以来写入的一切，并把数据集恢复到该状态。默认情况下，它拒绝回滚到除最新快照之外的任何快照：

```sh
zfs rollback pool/home/user@monday          # 仅当它是最新快照时
zfs rollback -r pool/home/user@monday       # 同时销毁更新的快照与书签
zfs rollback -R pool/home/user@monday       # 此外销毁这些快照的克隆
```

`-r` 与 `-R` 不会递归进入子数据集：只有所指定文件系统的直接快照会被销毁。要完整回滚一个递归快照，需要逐个回滚每个子数据集。

回滚要求文件系统已卸载（或可卸载）；`-f` 与 `-R` 一起使用，会强制卸载即将被销毁的克隆。

### 空间统计

两个属性可以回答大多数“我的存储池为什么满了”的问题：

* 快照上的 `used` 是*仅*销毁该快照时所能释放的空间——即不被其他快照引用、也不被活动数据集引用的块。
* 数据集上的 `usedbysnapshots` 是销毁其*全部*快照时所能释放的空间。它不是各快照 `used` 之和，因为空间可以在多个快照之间共享。

```sh
zfs list -o name,used,referenced,usedbysnapshots pool/home/user
zfs list -t snapshot -o name,used,referenced,written -r pool/home/user
```

`referenced` 是快照（或数据集）能看到多少数据，`written` 是自上一个快照以来改变了多少数据——后者对估算增量复制很有用。

一个陈旧的快照可能钉住任意数量的空间：如果某个大文件在快照创建之后被删除，其空间会一直保持分配状态，直到该快照消失。

### 保留与延迟销毁

保留（hold）是一个具名引用，用于阻止快照被销毁。复制工具使用保留，以确保数据流所基于的快照不会在传输中途消失。

```sh
zfs hold keep pool/home/user@monday
zfs holds pool/home/user@monday
zfs release keep pool/home/user@monday
```

只要保留存在，对该快照执行 `zfs destroy` 就会以 `EBUSY` 失败。`zfs destroy -d` 则会把此类快照标记为延迟销毁而不是失败：当最后一个保留被释放且它没有克隆时，它会自动消失。

### 比较快照

`zfs diff` 报告快照与之后的快照（或活动文件系统）之间发生了什么变化：

```sh
zfs diff pool/home/user@monday pool/home/user@tuesday
zfs diff pool/home/user@monday
```

### 限制快照数量

`snapshot_limit` 限制数据集及其后代上可存在的快照数量，`snapshot_count` 报告当前数量。在后代上设置的限额不会覆盖祖先的限额——而是叠加。对于有权更改该限额的用户，限额并不强制执行。

`snapshots_changed` 属性记录该数据集的快照最近一次创建或销毁的时间，这让监控与备份工具无需遍历整个快照列表，就能跳过不可能发生变化的数据集。

### 按计划创建

ZFS 负责创建快照，但不负责调度或过期清理。必须有东西决定何时创建、何时销毁，否则存储池会悄然堆满多年的每小时快照。

对于简单场景，一个调用 `zfs snapshot -r` 的定时器加上另一个销毁超过 *N* 个快照之外内容的定时器就足够了。更复杂的场景由第三方工具处理保留策略，而它们通常也处理复制——`sanoid`/`syncoid`、`zrepl` 与 `zfstools` 都是成熟的选择。它们都不属于 OpenZFS，因此应像对待任何支撑你备份的依赖一样对待它们。

有些工具会根据 `com.sun:auto-snapshot` 用户属性决定纳入哪些数据集，这正是它出现在示例中的原因，例如 [ZVOL](ZVOLs.md) 中的交换 zvol。

复制方面的内容参见 [Send 与 receive](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/Operations/Send%20and%20Receive.html)。

## 克隆

克隆是*可写*数据集，其初始内容来自某个快照。与快照一样，它几乎瞬间创建，初始不占用额外空间；随后随着写入而与其源分道扬镳。

```sh
zfs snapshot pool/vm/base@golden
zfs clone pool/vm/base@golden pool/vm/guest1
zfs clone pool/vm/base@golden pool/vm/guest2
```

克隆只能从快照创建，并且会形成依赖：只要某个快照的克隆存在，该源快照就无法销毁。克隆的 `origin` 属性指明它来自哪个快照，而 `zfs destroy` 在拒绝移除快照时会列出这类依赖。

### 提升克隆

`zfs promote` 反转父子关系：克隆成为拥有共享快照的数据集，原先的源则成为它的克隆。正是这一点使退役原数据集成为可能：

```sh
zfs promote pool/vm/guest1
zfs destroy -r pool/vm/base       # 现在可以了
```

克隆的典型用途包括：从通用黄金镜像派生虚拟机镜像、为测试而复制生产数据集的临时副本，以及在不丢弃回滚会删除的较新数据的情况下从误操作中恢复。

## 书签

书签是标记快照创建时间点的只读标记。它比快照更廉价——完全不占用额外空间——但它也不保留任何数据：无法浏览、挂载、克隆，也无法回滚到它。

```sh
zfs bookmark pool/home/user@monday pool/home/user#monday
zfs list -t bookmark -r pool/home/user
```

书签的意义在于增量复制。要发送增量流，发送端通常必须保留上一个快照。如果改为保留书签，快照本身——以及它钉住的空间——就可以销毁，而 `zfs send -i` 仍能生成增量流：

```sh
zfs send -i pool/home/user#monday pool/home/user@tuesday | ...
```

书签最初与某个快照绑定，但它能在该快照销毁后继续存在。关于它们如何融入复制工作流，参见 [Send 与 receive](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/Operations/Send%20and%20Receive.html)。

## 延伸阅读

* [zfsconcepts(7)](../../man/7/zfsconcepts.7.md)
* [zfs-snapshot(8)](../../man/8/zfs-snapshot.8.md)、[zfs-rollback(8)](../../man/8/zfs-rollback.8.md)、[zfs-destroy(8)](../../man/8/zfs-destroy.8.md)
* [zfs-clone(8)](../../man/8/zfs-clone.8.md)、[zfs-promote(8)](../../man/8/zfs-promote.8.md)
* [zfs-bookmark(8)](../../man/8/zfs-bookmark.8.md)
* [zfs-hold(8)](../../man/8/zfs-hold.8.md)、[zfs-diff(8)](../../man/8/zfs-diff.8.md)
