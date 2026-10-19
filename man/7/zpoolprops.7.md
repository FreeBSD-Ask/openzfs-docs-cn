# zpoolprops(7)

## 名称

`zpoolprops` — ZFS 存储池的属性

## 说明

每个池都有若干关联属性。部分属性为只读统计信息，另一些属性可配置，并会改变池的行为。

用户属性不影响 ZFS 的行为。你可以用它们以适合所在环境的方式为池添加注记。有关用户属性的更多信息，参见下文“用户属性”一节。

以下属性为只读：

### `allocated`

池内已使用的存储空间量。有关更多信息，参见 `fragmentation` 与 `free`。

### `available`

池内可用的剩余空间量，已按 raidz 校验开销调整。`available` 属性的计算方式为：

`usable - used`

有关更多信息，参见 `usable`、`used` 与 `free`。

### `bcloneratio`

若不使用块克隆而存储所有已克隆块所需的存储空间总量，与实际使用存储量的比值。`bcloneratio` 属性的计算方式为：

`( ( bclonesaved + bcloneused ) * 100 ) / bcloneused`

### `bclonesaved`

若未使用块克隆则额外需要的存储空间量。

### `bcloneused`

已克隆块占用的存储空间量。

### `capacity`

已使用的池空间百分比。该属性也可以用其简写的列名 `cap` 表示。

### `dedupcached`

当前已加载到 ARC 中的去重表的总大小。参见 zpool-prefetch(8)。

### `dedup_table_size`

去重表的磁盘上总大小。

### `dedupratio`

若不使用去重而存储所有经去重的块所需的存储空间总量，与实际使用存储量的比值。`dedupratio` 属性的计算方式为：

`( ( dedupsaved + dedupused ) * 100 ) / dedupused`

### `dedupsaved`

若未使用去重则额外需要的存储空间量。这表示由去重节省的空间。

### `dedupused`

经去重的块占用的存储空间量。这是去重后磁盘上实际占用的物理空间。

### `expandsize`

池或设备内可用于扩充池总容量的未初始化空间量。对于整盘 vdev，这是 GPT 末尾之外的空间——通常发生在 LUN 被动态扩容，或磁盘被更换为更大容量的情况。对于分区 vdev，这是设备加入池后被追加到分区的空间，最可能是在原地调整分区大小时产生的。通过以 `autoexpand=on` 将其上线，或使用 `zpool online -e`，可以把该空间认领给池使用。

### `fragmentation`

池中的碎片化程度。随着 `allocated` 的空间量增加，定位 `free` 空间会变得更加困难。与拥有更多未碎片化剩余空间的池相比，这可能导致更低的写入性能。

### `free`

池内可用的剩余空间量。相比之下，zfs(8) 的 `available` 属性描述可以写入 ZFS 文件系统/卷的新数据量。zpool 的 `free` 属性通常不适用于此用途，其值也可能远大于 zfs 的 `available` 空间。这种差异由若干因素造成，包括 raidz 校验；zfs 的 reservation、quota、refreservation 与 refquota 属性；以及由 `spa_slop_shift` 预留的空间（有关更多信息，参见 zfs(4)）。

### `freeing`

文件系统或快照被销毁后，其占用的空间会异步返还给池。`freeing` 是尚待回收的空间量。随着时间推移，`freeing` 会减少，而 `free` 会增加。

### `guid`

池的唯一标识符。在 Linux 上，它是该池每个已挂载文件系统 UUID 的前半部分；参见 zfsprops(7) 中的 `guid` 属性。

### `health`

池当前的健康状况。该属性可能为 `ONLINE`、`DEGRADED`、`FAULTED`、`OFFLINE`、`REMOVED`、`UNAVAIL` 之一。

### `last_scrubbed_txg`

指示最近一次 scrub 操作已检查并修复至哪一个事务组（TXG）。这可用于了解池在特定时间点的数据完整性状态。zpool-scrub(8) 在给定 `-C` 标志时可以利用该属性，仅扫描自上次 scrub 完成以来发生变化的数据。使用 `-e` 标志执行错误 scrub 时，不会更新该属性。

### `leaked`

在 `freeing` 期间因损坏而未能释放的空间，现已永久泄漏到池中。

### `load_guid`

池的唯一标识符。与 `guid` 属性不同，该标识符在每次加载池时生成（即不会在导入/导出之间保留），并且在池加载期间不会改变（即使发生 `reguid` 操作）。

### `size`

存储池的总大小。

### `unsupported@guid`

关于该池上已启用但不受支持的特性的信息。有关详细信息，参见 zpool-features(7)。

### `usable`

存储池总大小的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`usable` 是用于分配的启发式值，不应将其视为可用空间的精确度量。

### `used`

存储池内已用存储的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`used` 是用于分配的启发式值，不应将其视为已用空间的精确度量。

空间使用属性报告存储池实际可用的物理空间。该物理空间可能与任一包含数据集实际可使用的空间总量不同。在 raidz 配置中，已使用的空间量取决于所写入数据的特性。此外，ZFS 会保留一部分空间用于内部记账，zfs(8) 命令会将其计入，而 zpool 命令则不会。对于大小合理且未满的池，这些影响应该不可察觉；但对于小型池，或接近完全写满的池，这些差异可能更加明显。

以下属性为分配类别的只读指标：

* `class_dedup_allocated`、`class_dedup_available`、`class_dedup_capacity`、`class_dedup_expandsize`、`class_dedup_fragmentation`、`class_dedup_free`、`class_dedup_size`、`class_dedup_usable`、`class_dedup_used`

  该池 `dedup` metaslab 分配器类别的空间使用属性。

* `class_elog_allocated`、`class_elog_available`、`class_elog_capacity`、`class_elog_expandsize`、`class_elog_fragmentation`、`class_elog_free`、`class_elog_size`、`class_elog_usable`、`class_elog_used`

  该池 `embedded_log` metaslab 分配器类别的空间使用属性。

* `class_log_allocated`、`class_log_available`、`class_log_capacity`、`class_log_expandsize`、`class_log_fragmentation`、`class_log_free`、`class_log_size`、`class_log_usable`、`class_log_used`

  该池 `log` metaslab 分配器类别的空间使用属性。

* `class_normal_allocated`、`class_normal_available`、`class_normal_capacity`、`class_normal_expandsize`、`class_normal_fragmentation`、`class_normal_free`、`class_normal_size`、`class_normal_usable`、`class_normal_used`

  该池 `normal` metaslab 分配器类别的空间使用属性。

* `class_special_allocated`、`class_special_available`、`class_special_capacity`、`class_special_expandsize`、`class_special_fragmentation`、`class_special_free`、`class_special_size`、`class_special_usable`、`class_special_used`

  该池 `special` metaslab 分配器类别的空间使用属性。

* `class_special_elog_allocated`、`class_special_elog_available`、`class_special_elog_capacity`、`class_special_elog_expandsize`、`class_special_elog_fragmentation`、`class_special_elog_free`、`class_special_elog_size`、`class_special_elog_usable`、`class_special_elog_used`

  该池 `special_embedded_log` metaslab 分配器类别的空间使用属性。

每个分配类别由以下值描述：

#### `allocated`

该分配类别内已使用的存储空间量。

#### `available`

该分配类别内可用剩余空间的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`available` 是用于分配的启发式值，不应将其视为可用空间的精确度量。实际可用空间取决于数据集记录大小、压缩等若干因素。

#### `capacity`

已使用的分配类别空间百分比。

#### `expandsize`

该分配类别内可用于扩充分配器容量的未初始化空间量。参见池范围的 `expandsize` 属性。

#### `fragmentation`

该分配类别内剩余空间的碎片化程度。参见池范围的 `fragmentation` 属性。

#### `free`

该分配类别内可用的剩余空间量。该值未针对数据集记录大小、压缩或 raidz 校验开销等因素调整。参见池范围的 `free` 属性。

#### `size`

该分配类别的总大小。

#### `usable`

该分配类别总大小的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`usable` 是用于分配的启发式值，不应将其视为可用空间的精确度量。

#### `used`

该分配类别内已用存储的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`used` 是用于分配的启发式值，不应将其视为已用空间的精确度量。
