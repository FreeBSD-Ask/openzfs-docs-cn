# zpool-events(8)

## 名称

`zpool-events` — 列出由内核生成的最近事件

## 概述

```sh
zpool events [-vHf] [pool]
zpool events -c
```

## 说明

列出由 ZFS 内核模块生成的所有最近事件。这些事件由 zed(8) 消费，用于自动化管理任务，例如用热备盘替换失效设备。有关可生成的子类与事件有效载荷的更多信息，参见下文“事件”一节及后续各节。

## 选项

### `-c`

清除所有先前的事件。

### `-f`

跟随模式。

### `-H`

脚本模式。不显示表头，并改用单个制表符而不是任意数量的空格分隔字段。

### `-v`

打印每个事件的完整有效载荷。

## 事件

以下是不同的事件子类。完整的事件名形如 `ereport.fs.zfs.` **SUBCLASS** ，但这里只列出最后一部分。

### `checksum`

检测到校验和错误时发出。

### `io`

池中某个 vdev 出现 I/O 错误时发出。

### `data`

池中出现数据错误时发出。

### `deadman`

判定某个 I/O 请求“挂起”时发出，这可能由硬件或驱动程序不稳定导致丢失完成事件引起。有关“挂起” I/O 检测与配置的更多信息，参见 zfs(4) 中的 `zfs_deadman_failmode`。

### `delay`

已完成的 I/O 请求超过 `zio_slow_io_ms` 模块参数所允许的最大时间时发出。这可能是底层存储设备存在问题的一种指示。delay 事件的数量受 `zfs_slow_io_events_per_second` 模块参数限速。

### `dio_verify_rd`

发出 Direct I/O 读请求后出现校验和验证错误时发出。

### `dio_verify_wr`

发出 Direct I/O 写请求后出现校验和验证错误时发出。只有当模块参数 `zfs_vdev_direct_write_verify` 未设置为零时，才会发生此事件。有关 `zfs_vdev_direct_write_verify` 模块参数的详细信息，参见 zfs(4)。

### `config_sync`

每次对池进行 vdev 更改时发出。

### `zpool`

池无法导入时发出。

### `pool_create`

创建池时发出。

### `pool_destroy`

销毁池时发出。

### `pool_export`

导出池时发出。

### `pool_import`

导入池时发出。

### `pool_reguid`

检测到 REGUID（池的新唯一标识符已被重新生成）时发出。

### `vdev.unknown`

vdev 未知时发出。例如，尝试在一个已失效、被系统或池踢出且不再可用的 vdev 上清除设备错误。

### `vdev.open_failed`

无法打开某个 vdev 时发出（例如该 vdev 不存在）。

### `vdev.corrupt_data`

检测到某个 vdev 上有损坏数据时发出。

### `vdev.no_replicas`

不再有可供维持池的副本时发出。这会导致池处于 **DEGRADED** 状态。

### `vdev.bad_guid_sum`

检测到池中缺少设备时发出。

### `vdev.too_small`

系统（内核）已移除某个设备、而 ZFS 发现该设备不再存在时发出。这通常紧接着一个 `probe_failure` 事件。

### `vdev.bad_label`

标签完好但无效时发出。

### `vdev.bad_ashift`

ashift 对齐要求提高时发出。

### `vdev_remove`

某个 vdev 从镜像中分离时发出（或某个曾用于替换失效磁盘的热备盘从 vdev 分离时发出，仅当原磁盘已被重新添加时才有效）。

### `vdev_remove_aux`

移除辅助 vdev 时发出。

### `vdev_remove_dev`

从 vdev 中移除特定设备时发出。

### `vdev_clear`

清除池中的设备错误时发出。例如，对池中的某个设备运行 `zpool clear`。

### `vdev_check`

开始检查某个给定 vdev 能否被打开时发出。

### `vdev_spare`

热备盘接管并替换失效设备时发出。

### `vdev_autoexpand`

某个 vdev 可被自动扩展时发出。

### `vdev_add`

向池中添加 vdev 时发出。

### `vdev_attach`

将 vdev 附加到 mirror 或 raidz 类型的 vdev 时发出。

### `vdev_online`

某个离线 vdev 被重新上线时发出。

### `io_failure`

池中某个 vdev 出现 I/O 失败时发出。

### `probe_failure`

对某个 vdev 进行探测失败时发出。如果某个 vdev 被 ZFS 以外的方式从系统踢出（例如内核移除了该设备），就会发生这种情况。

### `log_replay`

无法重放意图日志时发出。在日志设备缺失或损坏的情况下会发生。

### `resilver_start`

启动 resilver 时发出。

### `resilver_finish`

正在运行的 resilver 完成时发出。

### `scrub_start`

在池上启动 scrub 时发出。

### `scrub_finish`

池完成 scrub 时发出。

### `scrub_abort`

池上的 scrub 被中止时发出。

### `scrub_resume`

池上的 scrub 恢复时发出。

### `scrub_paused`

池上的 scrub 被暂停时发出。

### `errorscrub_start`

在池上启动 errorscrub 时发出。

### `errorscrub_finish`

池完成 errorscrub 时发出。

### `errorscrub_abort`

池上的 errorscrub 被中止时发出。

### `errorscrub_resume`

池上的 errorscrub 恢复时发出。

### `errorscrub_paused`

池上的 errorscrub 被暂停时发出。

### `trim_start`

在池上启动 trim 时发出。

### `trim_finish`

池完成 trim 时发出。

### `trim_cancel`

池上的 trim 被取消时发出。

### `trim_resume`

池上的 trim 恢复时发出。

### `trim_suspend`

池上的 trim 被挂起时发出。

### `authentication`

出现解密或认证错误时发出。

### `config_cache_write`

无法写入配置缓存文件时发出。

### `bootfs_vdev_attach`

将 vdev 附加到已设置 bootfs 属性的根池时发出。

### `sitout`

某个 `RAIDZ` 或 `DRAID` vdev 触发 `autosit` 逻辑时发出。该逻辑检测到此类 vdev 中某块磁盘明显慢于其他磁盘时，会暂时使其暂停参与（sit out），以保持池的性能。

## 有效载荷

这是伴随事件的有效载荷（数据、信息）。

对于 zed，这些值会被设为大写，并加上前缀 `ZEVENT_`。

### `pool`

池名称。

### `pool_failmode`

失效模式：`wait`、`continue` 或 `panic`。更多信息参见 zpoolprops(7) 中的 `failmode` 属性。

### `pool_guid`

池的 GUID。

### `pool_context`

池的加载状态（0=none, 1=open, 2=import, 3=tryimport, 4=recover 5=error）。

### `vdev_guid`

相关 vdev 的 GUID（失效的 vdev，或 `zpool clear` 等操作所作用的 vdev）。

### `vdev_type`

vdev 类型：`disk`、`file`、`mirror` 等。可能的取值参见 zpoolconcepts(7) 的“虚拟设备（vdevs）”一节。

### `vdev_path`

vdev 的完整路径，包括 **-partX** 部分。

### `vdev_devid`

vdev 的 ID（如有）。

### `vdev_fru`

FRU 的物理位置。

### `vdev_state`

vdev 的状态（0=uninitialized, 1=closed, 2=offline, 3=removed, 4=failed to open, 5=faulted, 6=degraded, 7=healthy）。

### `vdev_ashift`

该 vdev 的 ashift 值。

### `vdev_complete_ts`

指定 vdev 上一个 I/O 请求完成的时间。

### `vdev_delta_ts`

自指定 vdev 上一个 I/O 请求完成以来经过的时间。

### `vdev_spare_paths`

热备盘列表，包括完整路径与 **-partX** 部分。

### `vdev_spare_guids`

热备盘的 GUID。

### `vdev_read_errors`

在该 vdev 上检测到的读错误数量。

### `vdev_write_errors`

在该 vdev 上检测到的写错误数量。

### `vdev_cksum_errors`

在该 vdev 上检测到的校验和错误数量。

### `parent_guid`

vdev 父节点的 GUID。

### `parent_type`

父节点的类型。参见 `vdev_type`。

### `parent_path`

vdev 父节点的路径（如有）。

### `parent_devid`

vdev 父节点的 ID（如有）。

### `zio_objset`

给定 I/O 请求的 objset 编号。

### `zio_object`

给定 I/O 请求的对象编号。

### `zio_level`

该块的间接层级。第 0 层为最低层，包含数据块。大于 0 的值表示相应层级的元数据块。

### `zio_blkid`

给定 I/O 请求的块 ID。

### `zio_err`

处理给定 I/O 请求失败时的错误号，与 errno(3) 兼容，其中使用 `EBADE` 值表示 ZFS 校验和错误。

### `zio_offset`

对指定 vdev 写入该 I/O 请求的字节偏移量。

### `zio_size`

该 I/O 请求的字节大小。

### `zio_flags`

描述该 I/O 请求应如何处理的一组标志。完整的 I/O 标志列表参见“I/O 标志”一节。

### `zio_stage`

该 I/O 在流水线中的当前阶段。所有 I/O 阶段的完整列表参见“I/O 阶段”一节。

### `zio_pipeline`

该 I/O 有效的流水线阶段。所有 I/O 阶段的完整列表参见“I/O 阶段”一节。

### `zio_priority`

该 I/O 请求的队列优先级。所有 I/O 优先级的完整列表参见“I/O 优先级”一节。

### `zio_tyoe`

该 I/O 请求的类型。所有 I/O 类型的完整列表参见“I/O 类型”一节。

### `zio_delay`

等待块层完成该 I/O 请求所经过的时间（单位：纳秒）。与 `zio_delta` 不同，它不包含任何 vdev 排队时间，因此完全是块层性能的度量。

### `zio_timestamp`

提交给定 I/O 请求的时间。

### `zio_delta`

服务给定 I/O 请求所需的时间。

### `prev_state`

该 vdev 的前一个状态。

### `cksum_algorithm`

使用的校验和算法。可用的校验和算法参见 zfsprops(7)。

### `cksum_byteswap`

数据是否已进行字节交换（byteswap）。

### `bad_ranges`

损坏偏移量的配对，形如 `[start, end)`。偏移量始终以 64 位边界对齐，并且可能包含若干未损坏的间隙。（参见 `bad_ranges_min_gap`）

### `bad_ranges_min_gap`

为了限制 `bad_ranges` 数组的大小，小于或等于 `bad_ranges_min_gap` 字节的未损坏间隙已与相邻的损坏区域合并。由于损坏是按 64 位字检测的，该值至少为 8 字节。

### `bad_range_sets`

该数组在 `bad_ranges` 中每个区间对应一个元素。每个元素包含该区间中在好数据里清零而在坏数据里置位的位数量。

### `bad_range_clears`

该数组在 `bad_ranges` 中每个区间对应一个元素。每个元素包含该区间中在好数据里置位而在坏数据里清零的位数量。

### `bad_set_bits`

如果该字段存在，它是 `bad data & ~(good data)` 的数组，即坏数据中置位而在好数据中清零的那些位。每个元素对应一个字节，其偏移量位于 `bad_ranges` 的某个区间内，数组按偏移量排序。因此，第一个元素是 `bad_ranges` 第一个区间中的第一个字节，最后一个元素是最后一个区间中的最后一个字节。

### `bad_cleared_bits`

与 `bad_set_bits` 类似，但包含 `good data & ~(bad data)`，即好数据中置位而在坏数据中清零的那些位。

## I/O 阶段

ZFS I/O 流水线由下列定义的若干阶段组成。各个阶段用于构建以下基本 I/O 操作：Read、Write、Free、Claim、Flush 与 Trim。这些阶段也可以设置在事件上，用来描述给定 I/O 请求的生命周期。

| 阶段 | 位掩码 | 操作 |
| :---: | :---: | :---: |
| ZIO_STAGE_OPEN | 0x00000001 | RWFCXT |
| ZIO_STAGE_READ_BP_INIT | 0x00000002 | R----- |
| ZIO_STAGE_WRITE_BP_INIT | 0x00000004 | -W---- |
| ZIO_STAGE_FREE_BP_INIT | 0x00000008 | --F--- |
| ZIO_STAGE_ISSUE_ASYNC | 0x00000010 | -WF--T |
| ZIO_STAGE_WRITE_COMPRESS | 0x00000020 | -W---- |
| ZIO_STAGE_ENCRYPT | 0x00000040 | -W---- |
| ZIO_STAGE_CHECKSUM_GENERATE | 0x00000080 | -W---- |
| ZIO_STAGE_NOP_WRITE | 0x00000100 | -W---- |
| ZIO_STAGE_DDT_READ_START | 0x00000200 | R----- |
| ZIO_STAGE_DDT_READ_DONE | 0x00000400 | R----- |
| ZIO_STAGE_DDT_WRITE | 0x00000800 | -W---- |
| ZIO_STAGE_DDT_FREE | 0x00001000 | --F--- |
| ZIO_STAGE_BRT_FREE | 0x00002000 | --F--- |
| ZIO_STAGE_GANG_ASSEMBLE | 0x00004000 | RWFC-- |
| ZIO_STAGE_GANG_ISSUE | 0x00008000 | RWFC-- |
| ZIO_STAGE_DVA_THROTTLE | 0x00010000 | -W---- |
| ZIO_STAGE_DVA_ALLOCATE | 0x00020000 | -W---- |
| ZIO_STAGE_DVA_FREE | 0x00040000 | --F--- |
| ZIO_STAGE_DVA_CLAIM | 0x00080000 | ---C-- |
| ZIO_STAGE_READY | 0x00100000 | RWFCIT |
| ZIO_STAGE_VDEV_IO_START | 0x00200000 | RW--XT |
| ZIO_STAGE_VDEV_IO_DONE | 0x00400000 | RW--XT |
| ZIO_STAGE_VDEV_IO_ASSESS | 0x00800000 | RW--XT |
| ZIO_STAGE_CHECKSUM_VERIFY | 0x01000000 | R----- |
| ZIO_STAGE_DIO_CHECKSUM_VERIFY | 0x02000000 | -W---- |
| ZIO_STAGE_DONE | 0x04000000 | RWFCXT |

## I/O 标志

流水线中的每个 I/O 请求都包含一组标志，用于描述其功能并控制其行为。这些标志将作为 `zio_flags` 有效载荷条目设置在事件上。

| 标志 | 位掩码 |
| :---: | :---: |
| ZIO_FLAG_DONT_AGGREGATE | 0x00000001 |
| ZIO_FLAG_IO_REPAIR | 0x00000002 |
| ZIO_FLAG_SELF_HEAL | 0x00000004 |
| ZIO_FLAG_RESILVER | 0x00000008 |
| ZIO_FLAG_SCRUB | 0x00000010 |
| ZIO_FLAG_SCAN_THREAD | 0x00000020 |
| ZIO_FLAG_PHYSICAL | 0x00000040 |
| ZIO_FLAG_CANFAIL | 0x00000080 |
| ZIO_FLAG_SPECULATIVE | 0x00000100 |
| ZIO_FLAG_CONFIG_WRITER | 0x00000200 |
| ZIO_FLAG_DONT_RETRY | 0x00000400 |
| ZIO_FLAG_NODATA | 0x00001000 |
| ZIO_FLAG_INDUCE_DAMAGE | 0x00002000 |
| ZIO_FLAG_ALLOC_THROTTLED | 0x00004000 |
| ZIO_FLAG_IO_RETRY | 0x00008000 |
| ZIO_FLAG_PROBE | 0x00010000 |
| ZIO_FLAG_TRYHARD | 0x00020000 |
| ZIO_FLAG_OPTIONAL | 0x00040000 |
| ZIO_FLAG_DIO_READ | 0x00080000 |
| ZIO_FLAG_BYPASSED_QUEUE | 0x00100000 |
| ZIO_FLAG_DONT_QUEUE | 0x00200000 |
| ZIO_FLAG_DONT_PROPAGATE | 0x00400000 |
| ZIO_FLAG_IO_BYPASS | 0x00800000 |
| ZIO_FLAG_IO_REWRITE | 0x01000000 |
| ZIO_FLAG_RAW_COMPRESS | 0x02000000 |
| ZIO_FLAG_RAW_ENCRYPT | 0x04000000 |
| ZIO_FLAG_GANG_CHILD | 0x08000000 |
| ZIO_FLAG_DDT_CHILD | 0x10000000 |
| ZIO_FLAG_GODFATHER | 0x20000000 |
| ZIO_FLAG_NOPWRITE | 0x40000000 |
| ZIO_FLAG_REEXECUTED | 0x80000000 |
| ZIO_FLAG_DELEGATED | 0x100000000 |
| ZIO_FLAG_PREALLOCATED | 0x200000000 |
| ZIO_FLAG_POSTREAD | 0x400000000 |

## I/O 类型

流水线中的每个 I/O 请求都有一个类型值。该值描述此 I/O 所表示的低层工作种类。该值将作为 `zio_type` 有效载荷条目设置在事件上。

| 类型 | 值 | 描述 |
| :---: | :---: | :---: |
| ZIO_TYPE_NULL | 0x0 | 内部 I/O 同步点 |
| ZIO_TYPE_READ | 0x1 | 数据读取 |
| ZIO_TYPE_WRITE | 0x2 | 数据写入 |
| ZIO_TYPE_FREE | 0x3 | 释放块 |
| ZIO_TYPE_CLAIM | 0x4 | 认领块（ZIL 重放） |
| ZIO_TYPE_FLUSH | 0x5 | 磁盘缓存刷新请求 |
| ZIO_TYPE_TRIM | 0x6 | trim（discard） |

## I/O 优先级

流水线中的每个 I/O 请求都有一个优先级值。队列代码使用该值决定接下来要派发哪个 I/O。该值将作为 `zio_priority` 有效载荷条目设置在事件上。

| 优先级 | 值 | 描述 |
| :---: | :---: | :---: |
| ZIO_PRIORITY_SYNC_READ | 0x0 | |
| ZIO_PRIORITY_SYNC_WRITE | 0x1 | ZIL |
| ZIO_PRIORITY_ASYNC_READ | 0x2 | 预取 |
| ZIO_PRIORITY_ASYNC_WRITE | 0x3 | `spa_sync()` |
| ZIO_PRIORITY_SCRUB | 0x4 | 异步 scrub/resilver 读取 |
| ZIO_PRIORITY_REMOVAL | 0x5 | 用于移除 vdev 的读写 |
| ZIO_PRIORITY_INITIALIZING | 0x6 | 初始化 I/O |
| ZIO_PRIORITY_TRIM | 0x7 | trim I/O（discard） |
| ZIO_PRIORITY_REBUILD | 0x8 | 用于重建 vdev 的读写 |
| ZIO_PRIORITY_NOW | 0xa | 非排队 I/O（例如 free） |

## 参考文献

zfs(4)、zed(8)、zpool-wait(8)

2025 年 7 月 3 日
