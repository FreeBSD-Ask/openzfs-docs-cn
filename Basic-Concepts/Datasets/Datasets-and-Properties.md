# 数据集与属性

存储池是一整块空间；数据集是划分它的方式。创建数据集成本很低，也不预分配任何东西，因此 ZFS 的通常做法是创建许多数据集——每个工作负载、每个用户、每个应用程序各一个——而不是一个带目录的大文件系统。

## 数据集类型

* **文件系统** ——POSIX 文件系统，挂载在某处。默认类型。
* **卷（zvol）** ——块设备，导出为 `/dev/zvol/<pool>/<name>`。用于虚拟机磁盘、iSCSI 目标、交换空间，或 ZFS 未实现的其他文件系统。
* **快照** 与 **书签** ——只读，见[快照、克隆与书签](Snapshots-and-Clones.md)。

```sh
zfs create pool/home
zfs create pool/home/alice
zfs create -V 40G pool/vm/disk0        # 创建一个 zvol

zfs list                               # 文件系统与卷
zfs list -t all -r pool                # 递归列出所有内容
zfs destroy pool/home/alice
```

数据集构成与名称对应的层级，大多数属性沿该层级向下继承——这正是需要有意嵌套它们的主要原因。

## 属性

数据集行为的方方面面都是属性：挂载在哪里、如何压缩、是否只读、可以使用多少空间。

```sh
zfs get all pool/home/alice
zfs get -r compression,recordsize pool
zfs get -o name,property,value,source -s local all pool/home

zfs set compression=zstd pool/home
zfs inherit compression pool/home/alice     # 回退到父级的值
zfs inherit -S compression pool/home/alice  # 恢复为接收时的值
```

有些属性是只读的（`used`、`available`、`creation`、`compressratio`），有些只能在创建时设置（`casesensitivity`、`normalization`、`encryption`、`volblocksize`），其余可以随时更改。影响数据写入方式的属性——`recordsize`、`compression`、`checksum`、`dedup`、`copies`——其更改只对新增写入的块生效。

### 属性来源

`zfs get` 会报告每个值的来源：

* `local`——直接设置在此数据集上。
* `inherited from <数据集>`——设置在某个祖先上。
* `default`——任何地方都未设置；内置默认值。
* `temporary`——仅通过挂载选项对当前挂载有效。
* `received`——随 `zfs receive` 流一同接收。
* `none`——只读属性，没有来源。

当数据集行为不符合预期时，这是首先要检查的地方——从上方三层继承来的值很容易被忽略。

## 值得了解的属性

### 布局与挂载

#### `mountpoint`

文件系统挂载的位置。`legacy` 把控制权交给 `/etc/fstab` 或 `mount`；`none` 表示不挂载。继承它的子数据集会自动延伸父级的路径。

#### `canmount`

`on`、`off` 或 `noauto`。`off` 使数据集成为纯粹用于属性继承的容器，永不挂载，同时仍拥有可继承的 `mountpoint`。`noauto` 表示仅在明确要求时挂载——启动环境的基础。

#### `readonly`

阻止写入该数据集。复制目标上的标准设置。

### 数据布局

#### `recordsize`

文件系统的最大块大小。默认 128 KiB；让它与应用 I/O 大小匹配，对数据库与虚拟机镜像至关重要。

#### `volblocksize`

zvol 的固定块大小。仅在创建时设置。

#### `compression`、`checksum`、`dedup`、`copies`

参见[压缩](../Data-Storage/Compression.md)、[校验和](../Data-Storage/Checksums.md)与[去重](../Data-Storage/Deduplication.md)。

### 行为

#### `atime` / `relatime`

访问时间的更新。`atime=off` 消除了每次读取所带来的一次写入；`relatime=on` 是通常的折中。

#### `sync`

`standard`、`always` 或 `disabled`。`disabled` 忽略 fsync——它不会损坏存储池，但崩溃时会丢失最近写入的数据。

#### `exec`、`setuid`、`devices`

常规挂载选项语义，以属性形式提供。

#### `sharenfs`、`sharesmb`

导出该数据集；参见[共享数据集](../Operations/Sharing.md)。

#### `quota`、`refquota`、`reservation`、`refreservation`

参见[配额与预留](Quotas-and-Reservations.md)。

### 空间计量

#### `used`

计入此数据集及其后代的空间。

#### `referenced`

仅从此数据集可达的空间——对它做快照会引用的量。

#### `available`

扣除配额与预留之后仍可用的空间。

#### `logicalused` / `logicalreferenced`

压缩之前的同一量。

#### `usedby*`

`usedbydataset`、`usedbysnapshots`、`usedbychildren` 与 `usedbyrefreservation` 把 `used` 细分——是查清空间去向的最快方式。

```sh
zfs list -o name,used,usedbydataset,usedbysnapshots,usedbychildren -r pool
```

## 用户属性

可以为数据集附加任意属性，供工具使用。它们对 ZFS 本身没有影响。用户属性名必须包含冒号，这正是它与原生属性的区别；惯例是 `module:property`，其中模块部分通常是反向域名。

```sh
zfs set com.example:backup=daily pool/home
zfs get -r -o name,value com.example:backup pool
```

由于它们像原生属性一样继承，用户属性是从数据集树本身驱动快照与复制策略的便捷方式。

## 延伸阅读

* [zfsconcepts(7)](../../man/7/zfsconcepts.7.md)
* [zfsprops(7)](../../man/7/zfsprops.7.md)——完整的属性参考
* [zfs-create(8)](../../man/8/zfs-create.8.md)、[zfs-get(8)](../../man/8/zfs-set.8.md)、[zfs-set(8)](../../man/8/zfs-set.8.md)、[zfs-inherit(8)](../../man/8/zfs-set.8.md)
* [工作负载调优](../../Performance-Tuning/WorkloadTuning.md)
