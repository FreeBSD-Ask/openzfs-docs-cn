# vdevprops(7)

## 名称

`vdevprops` — ZFS vdev 的原生属性与用户属性

## 说明

属性分为两种类型：原生（native）属性与用户定义（user）属性。原生属性或者导出内部统计信息，或者控制 ZFS 的行为。此外，原生属性要么可编辑，要么只读。用户属性不影响 ZFS 的行为，但你可以用它们以适合所在环境的方式为 vdev 添加注记。有关用户属性的更多信息，参见下文“用户属性”一节。

### 原生属性

每个 vdev 都有一组属性，用于导出有关该 vdev 的统计信息并控制其各种行为。属性不会从顶级 vdev 继承，但 checksum_n、checksum_t、io_n、io_t、slow_io_events、slow_io_n 与 slow_io_t 除外。

数值属性的值可以使用便于阅读的后缀来指定（例如 `k`、`KB`、`M`、`Gb` 等，最高到表示 zettabyte 的 `Z`）。以下写法都是有效（且相等）的规格：`1536M`、`1.5g`、`1.50GB`。

非数值属性的值区分大小写，且必须为小写。

以下原生属性由 vdev 的只读统计信息组成，这些属性不可更改。

#### `capacity`

vdev 空间的已用百分比

#### `state`

该 vdev 的状态，例如 online、faulted 或 offline

#### `guid`

该 vdev 的全局唯一 ID

#### `asize`

该 vdev 的可分配大小

#### `psize`

该 vdev 的物理大小

#### `ashift`

该 vdev 的物理扇区大小，以 2 的幂表示

#### `size`

该 vdev 的总大小

#### `free`

该 vdev 上的剩余可用空间量

#### `allocated`

该 vdev 上已分配的空间量

#### `expandsize`

该 vdev 可以扩容多少

#### `fragmentation`

该 vdev 的碎片化百分比

#### `parity`

该 vdev 的校验级别

#### `failure_domain`

启用 failure domains 特性的 dRAID vdev 中，该子 vdev 的故障域 ID

#### `failure_group`

启用 failure domains 特性的 dRAID vdev 中，该子 vdev 的故障组 ID

#### `devid`

该 vdev 的设备 ID

#### `physpath`

设备的物理路径

#### `encpath`

设备的机箱路径

#### `fru`

现场可更换单元（Field Replaceable Unit），通常为型号

#### `parent`

该 vdev 的父 vdev

#### `children`

该 vdev 各子 vdev 的逗号分隔列表

#### `numchildren`

该 vdev 拥有的子 vdev 数量

#### `read_errors`、`write_errors`、`checksum_errors`、`initialize_errors`、`trim_errors`

该 vdev 遇到的各类错误的数量

#### `slow_ios`

表示该 vdev 遇到的慢速 I/O 操作数量。慢速 I/O 指未在 `zio_slow_io_ms` 阈值（默认 `30000` 毫秒）内完成的操作。对于 RAIDZ 与 dRAID 配置，该值还表示此 vdev 被判定为异常落后者而排除在读取 I/O 之外的次数。

#### `null_ops`、`read_ops`、`write_ops`、`free_ops`、`claim_ops`、`trim_ops`

该 vdev 执行的各类型 I/O 操作的数量

#### `null_bytes`、`read_bytes`、`write_bytes`、`free_bytes`、`claim_bytes`、`trim_bytes`

该 vdev 执行的各类型操作的累计大小

#### `removing`

该设备当前是否正在从池中移除

#### `raidz_expanding`

在该 RAID-Z vdev 上进行 `zpool attach` 扩容期间被置位；完成时清除。参见 zpool-attach(8)。

#### `trim_support`

指示叶子设备是否支持 TRIM 操作。

#### `rotational`

指示支撑该 vdev 的设备是否为旋转式存储介质。

以下原生属性可用于改变 vdev 的行为。

#### `checksum_n`、`checksum_t`、`io_n`、`io_t`、`slow_io_n`、`slow_io_t`

通过分别指定 <T> 秒内 <N> 个校验和/IO 错误的阈值来调整故障管理守护进程。这些属性可以在叶子 vdev 与顶级 vdev 上设置。当叶子 vdev 与顶级 vdev 都设置了该属性时，以叶子 vdev 的值为准；如果只在顶级 vdev 上设置，则使用该值。这些属性的值不会在 vdev 更换后保留，因此建议把属性设置在顶级 vdev 上，而不是叶子 vdev 本身。`slow_io_n` 与 `slow_io_t` 必须手动设置才能启用慢速 I/O 诊断，没有内置默认值。在 OpenZFS on Linux 上，`checksum_n`、`checksum_t`、`io_n` 与 `io_t` 的默认值为 600 秒内 10 个错误；OpenZFS on FreeBSD 的默认值参见 zfsd(8)。

#### `slow_io_events`

控制是否生成慢速 I/O 事件。即使禁用，慢速 I/O 仍会出现在 `zpool status -s` 的输出中。

#### `comment`

最长 8192 字符的文本注释

#### `bootsize`

为 EFI 系统分区预留的空间量

#### `failfast=inherit|on|off`

该设备是否应将 BIO 错误传播回 ZFS，用于禁用 failfast。`inherit` 使 vdev 沿树向上递归采用其父 vdev 的行为。

#### `sit_out`

仅对 RAIDZ 与 dRAID vdev 有效。当检测到慢速磁盘异常落后者且该 vdev 当前处于轮休（sit out）状态时为 true。可以手动设置该属性使 vdev 轮休；若启用了 `autosit` 逻辑，也会自动设置。轮休期间，vdev 不参与正常读取，其数据将按需由校验信息重建。

#### `autosit`

仅对 RAIDZ 与 dRAID vdev 有效。设置后启用内核级的慢速磁盘检测逻辑。该逻辑会自动使性能显著落后的 vdev 轮休，如 `sit_out` 属性所述。

#### `path`

该 vdev 的设备路径

#### `allocating`

该设备是否应执行新的分配，用于在设备计划稍后移除时将其停用。参见 zpool-remove(8)。

#### `alloc_bias=none|log|special|dedup`

控制顶级 vdev 的分配类别。更改在池导出并重新导入后生效。不支持改为或改出 log，因为日志设备故障时可能导致数据丢失。设置为 `special` 与 `dedup` 需要启用 `feature@allocation_classes`。至少要有一个顶级 vdev 保持在 normal（即 `none`）类别。

#### `scheduler=auto|on|off`

控制读写该 vdev 时 I/O 请求加入 vdev 队列的方式。该属性可以在叶子 vdev 上设置。这些属性的值不会在 vdev 更换后保留。取值：`auto` 由 ZFS 选择它认为最佳的计划方式，目前若 vdev 背后是旋转式块设备或文件则对 I/O 排队，否则不排队；`on` 始终将 I/O 请求加入 vdev 队列；`off` 从不将 I/O 请求加入 vdev 队列，不建议在机械盘支撑的 vdev 上使用，否则可能导致请求饥饿。

### 用户属性

除标准原生属性之外，ZFS 还支持任意的用户属性。用户属性不影响 ZFS 的行为，但应用程序或管理员可以用它们为 vdev 添加注记。

用户属性名必须包含冒号（`:`）字符，以便与原生属性区分。属性名可以包含小写字母、数字以及以下标点字符：冒号（`:`）、连字符（`-`）、句点（`.`）与下划线（`_`）。惯例上属性名分为两部分，例如 `module:property`，但 ZFS 并不强制这一命名空间。用户属性名最长 256 个字符，且不能以连字符（`-`）开头。

在程序中使用用户属性时，强烈建议属性名的 `module` 部分使用反向 DNS 域名，以降低两个独立开发的软件包把同一属性名用作不同用途的概率。

用户属性的值是任意字符串，且从不校验。使用 `zpool set` 命令并以空值即可清除用户属性。属性值最长 8192 字节。

## 参考文献

zpoolprops(7)、zpool-set(8)

2024 年 7 月 23 日
