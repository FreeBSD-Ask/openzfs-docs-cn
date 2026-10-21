# 配额与预留

各数据集共享存储池的空闲空间，因此默认情况下任何一个都可能把池填满。配额限制一个数据集最多可以消耗多少空间；预留则保证它始终能主张多少空间。两者都是属性，都按位置而非按值继承，且都分两种：含后代与快照（`quota`、`reservation`）或不含（`refquota`、`refreservation`）。

## 配额

### `quota`

对数据集 **及其所有后代（含快照）** 所用空间的硬性上限。

### `refquota`

对数据集自身 `referenced` 空间的硬性上限——后代与快照不计入。

```sh
zfs set quota=100G pool/home/alice
zfs set refquota=80G pool/home/alice
zfs get quota,refquota,used,referenced,available pool/home/alice
```

在后代上设置的配额不会覆盖祖先的——它只是增加一条限制，最紧的那条生效。配额不能设在卷上：`volsize` 本身就充当隐式配额。

实际区别很重要。在普通 `quota` 下，快照会吃掉用户的额度，因此自动快照计划可能让写入失败，即便用户删除了文件。而在 `refquota` 下，用户看到的是稳定上限，快照增长改由父级承担。常见模式是：用 `refquota` 设用户可见的上限，再用父级数据集上的 `quota` 框定总量。

## 预留

### `reservation`

保证给数据集及其后代的最小空间。

### `refreservation`

保证给数据集自身的最小空间。

当使用量低于预留时，该数据集按用满预留量记账。这部分空间计入父级的 `used`，并占用父级的配额与预留——这正是它成为“保证”的原因：池中其他任何东西都无法分配它。

```sh
zfs set reservation=50G pool/critical
zfs set refreservation=none pool/vm/disk0
```

设置了 `refreservation` 时，只有在预留之外有足够空闲空间容纳数据集当前 `referenced` 字节数，才能创建快照。

`refreservation=auto` 仅适用于卷：它会为 zvol 厚置备，预留足够空间容纳整个 `volsize` 并计入元数据。设为 `none` 则让卷变成稀疏——创建更快、占用更少，但存储池填满时写入可能以 `ENOSPC` 失败。

## 用户、组与项目配额

在单个数据集内，还可以按用户、组或项目限制空间：

```sh
zfs set userquota@alice=10G pool/home
zfs set groupquota@staff=200G pool/home
zfs set projectquota@42=50G pool/data

zfs userspace pool/home
zfs groupspace pool/home
```

`defaultuserquota`、`defaultgroupquota` 与 `defaultprojectquota` 为所有未单独设置配额者设定兜底值（`0` 表示禁用）。`*objquota@` 系列限制*对象数量*而非字节数。

强制执行是异步的：用户可以略微超出配额，随后写入才开始以 `EDQUOT` 失败。

## 限制数量而非空间

`filesystem_limit` 与 `snapshot_limit` 限制树中某一点之下可以存在多少个数据集或快照。与配额一样，后代的限额是叠加在祖先之上而非取代，且对有权更改它的用户不强制执行。`filesystem_limit` 需要 `filesystem_limits` 存储池特性。

```sh
zfs set snapshot_limit=200 pool/home
zfs get filesystem_count,snapshot_count pool/home
```

## 余量空间

你无需手动预留应急空间——ZFS 已经这么做了。存储池最后 `1/2^spa_slop_shift`（默认 3.2%）会被扣留，普通写入无法占用。一旦空闲空间低于它，`write`、`create` 等普通操作就会返回 `ENOSPC`。

这份预留的意义在于恢复手段仍然可用：

* 删除文件与多数管理操作可以使用其中 **一半** ；
* 几乎确定能释放空间的操作，例如 `zfs destroy`，最多可用其 **四分之三** ；
* 少数内部操作无论空闲空间多少都始终允许执行——原则上，正是它们能把一个存储池真正跑满，并使其永久只读。

在极小的存储池上，该预留会提高到至少 128 MiB；在极大的存储池上，它被限制为不超过 128 GiB，但它从不超过存储池的一半。

在大池上可以调高 `spa_slop_shift` 来回收其中一部分空间——设为 6 得 1.6%，设为 7 得 0.8%——代价是恢复余量更薄。参见 [zfs(4)](../../man/4/zfs.4.md) 的模块参数一节，以及[工作负载调优](../../Performance-Tuning/WorkloadTuning.md)，后者建议为分配性能保持 10% 以上的空闲空间——这与余量预留是两个问题，而通常先遇到的是前者。

## 延伸阅读

* [zfsprops(7)](../../man/7/zfsprops.7.md)——`quota`、`refquota`、`reservation`、`refreservation`、`userquota@`、`filesystem_limit`、`snapshot_limit`
* [zfs-userspace(8)](../../man/8/zfs-userspace.8.md)、[zfs-project(8)](../../man/8/zfs-project.8.md)
* [数据集与属性](Datasets-and-Properties.md)
