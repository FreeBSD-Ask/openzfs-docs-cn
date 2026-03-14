# zfs(4)

## 名称

`zfs` — ZFS 内核模块调优

## 说明

ZFS 模块支持以下若干参数。

### **dbuf_cache_max_bytes** = **UINT64_MAX**B (u64)

dbuf 缓存的最大字节数。目标大小由 MIN 与目标 ARC 大小的 1/2^**dbuf_cache_shift**（1/32）决定。dbuf 缓存及其相关设置的行为可通过 kstat `/proc/spl/kstat/zfs/dbufstats`  进行观察。

### **dbuf_metadata_cache_max_bytes** = **UINT64_MAX**B (u64)

元数据 dbuf 缓存的最大字节数。目标大小由 MIN 与目标 ARC 大小的 1/2^**dbuf_metadata_cache_shift**（1/64）决定。可通过 kstat `/proc/spl/kstat/zfs/dbufstats` 观察元数据 dbuf 缓存及其相关设置的行为。

### **dbuf_cache_hiwater_pct** = **10**% (uint)

当 dbuf 必须被直接淘汰时，相对于 **dbuf_cache_max_bytes** 的百分比。

### **dbuf_cache_lowater_pct** = **10**% (uint)

当淘汰线程停止淘汰 dbuf 时，相对于 **dbuf_cache_max_bytes** 的百分比。

### **dbuf_cache_shift** = **5** (uint)

将 dbuf 缓存（**dbuf_cache_max_bytes**）的大小设置为目标 ARC 大小的 log2 分数。

### **dbuf_metadata_cache_shift** = **6** (uint)

将元数据 dbuf 缓存（**dbuf_metadata_cache_max_bytes**）的大小设置为目标 ARC 大小的 log2 分数。

### **dbuf_mutex_cache_shift** = **0** (uint)

设置 dbuf 缓存的互斥锁数组大小。设置为 **0** 时，数组大小会根据系统总内存动态调整。

### **dmu_object_alloc_chunk_shift** = **7** (128) (uint)

以 2 的幂分配单次操作中 dnode 插槽的数量。默认值可最小化批量操作时的锁竞争。

### **dmu_ddt_copies** = **3** (uint)

控制去重表（DDT）对象存储的副本数量。将副本数量从原默认的 3 降至 1 可以减少去重引起的写放大。这假设数据的冗余由 vdev 层提供。如果 DDT 损坏，当 DDT 无法报告正确引用计数时，可能会导致空间泄漏（未释放）。

### **dmu_prefetch_max** = **134217728**B (128 MiB) (uint)

限制单次调用可预取的数据量（以字节计）。这有助于限制预取操作使用的内存量。

### **l2arc_feed_again** = **1**|0 (int)

L2ARC 极速预热。当 L2ARC 为冷状态时，填充间隔将尽可能快。

### **l2arc_feed_min_ms** = **200** (u64)

最小填充间隔（毫秒）。需要 **l2arc_feed_again**=1，仅在相关情况下适用。

### **l2arc_feed_secs** = **1** (u64)

L2ARC 写入间隔（秒）。

### **l2arc_headroom** = **8** (u64)

每个周期搜索 ARC 列表以寻找可缓存到 L2ARC 内容的深度，表示为有效写入大小的倍数。设置为 **0** 可禁用每周期的 headroom 限制。当持久化标记激活时，扫描深度还受 **l2arc_ext_headroom_pct** 限制。

### **l2arc_headroom_boost** = **200**% (u64)

当 L2ARC 内容在写入前成功压缩时，将 **l2arc_headroom** 按此百分比放大。设置为 100 表示禁用此功能。

### **l2arc_dwpd_limit** = **100** (uint)

L2ARC 设备每日写入量（DWPD）限制，用于保护 SSD 耐久性，以百分比表示，其中 100 等于 1.0 DWPD。值为 100 表示每个 L2ARC 设备每天可写入自身容量一次。较低值支持分数 DWPD（50 = 0.5 DWPD，30 = 0.3 DWPD，用于 QLC SSD）。较高值允许更多写入（300 = 3.0 DWPD）。有效写入速率始终受 **l2arc_write_max** 限制。设置为 0 则完全禁用 DWPD 限制。DWPD 限制仅在初始填充完成且总 L2ARC 容量至少为 arc_c_max 两倍时生效。

### **l2arc_exclude_special** = **0**|1 (int)

控制是否将存在于特殊 vdev 上的缓冲区缓存到 L2ARC。如果设置为 1，则排除特殊 vdev 上的 dbuf 被缓存到 L2ARC。

### **l2arc_mfuonly** = **0**|1|2 (int)

控制是否仅将 ARC 中的 MFU（Most Frequently Used，最常使用）元数据和数据缓存到 L2ARC。当读取/写入大量数据且这些数据预计不会被重复访问时，这样做可以避免浪费 L2ARC 空间。

默认值为 **0**，表示 MRU（Most Recently Used，最近使用）和 MFU 的数据及元数据都会被缓存。即便关闭此功能（设置为 0），部分 MRU 缓冲仍会存在于 ARC 并最终被缓存到 L2ARC。如果 **l2arc_noprefetch**=0，则一些预取的缓冲会被缓存到 L2ARC，它们可能随后转为 MRU，这时 **l2arc_mru_asize** arcstat 不会为 0。

* 设置为 **1**：只将 MFU 数据和元数据缓存到 L2。
* 设置为 **2**：缓存所有元数据（MRU + MFU），但仅缓存 MFU 数据（即 MRU 数据不缓存）。这种设置适合在数据更替频繁的情况下尽可能缓存更多元数据。

无论 **l2arc_noprefetch** 如何，一些 MFU 缓冲可能从 ARC 驱逐，但随后被访问作为预取并转为 MRU，如果再次访问，它们会被计为 MRU，**l2arc_mru_asize** arcstat 不会为 0。

L2ARC 缓冲首次缓存到 L2ARC 时的 ARC 状态，可通过 **l2arc_mru_asize**、**l2arc_mfu_asize** 和 **l2arc_prefetch_asize** arcstats 查看（在导入池或上线缓存设备时，如果启用持久化 L2ARC）。

**evict_l2_eligible_mru** arcstat 不受此选项影响，可参考 **evict_l2_eligible_m[rf]u** arcstats 来判断是否适合为当前工作负载切换此选项。


### **l2arc_meta_percent** = **33**% (uint)

允许用于 L2ARC 专用头的 ARC 大小百分比。由于 L2ARC 缓冲区在内存压力下不会被淘汰，如果系统的 L2ARC 过大且头部过多，可能会导致性能下降或无法使用。此参数限制 L2ARC 写入和重建，以达到目标。

### **l2arc_trim_ahead** = **0**% (u64)

如果 L2ARC 设备已填满，则按写入大小的一定百分比提前对 L2ARC 设备执行 TRIM。如果设置为 **100**，则 TRIM 的空间为即将写入数据所需空间的两倍。TRIM 的最小量为 **64 MiB**。该选项还会在创建 L2ARC 设备、将其添加到现有池、导入池或上线缓存设备时设备头无效的情况下，对整个 L2ARC 设备执行 TRIM。设置为 **0** 则完全禁用 L2ARC 上的 TRIM，这是默认值，因为 TRIM 可能对底层存储设备造成较大压力。具体效果取决于设备对 TRIM 命令的支持情况。

### **l2arc_noprefetch** = **1**|0 (int)

如果缓冲区是被预取但未被应用程序使用的，则不将其写入 L2ARC。如果 L2ARC 中已有预取缓冲区，之后设置此选项，则不会从 L2ARC 读取这些预取缓冲区。取消设置此选项对将磁盘的顺序读取缓存到 L2ARC 并在之后从 L2ARC 提供这些读取可能有用。当 L2ARC 设备在顺序读取上明显快于池中的磁盘时，这尤其有利。

使用 **1** 禁用，将预取缓存写入/读取到 L2ARC；使用 **0** 启用。

### **l2arc_norw** = **0**|1 (int)

写入期间不进行读取。

### **l2arc_ext_headroom_pct** = **25** (u64)

每个 ARC 状态在重置标记到尾部之前可扫描的百分比。较低值在高负载下可使标记保持靠近尾部。设置为 0 可禁用扫描深度限制。

### **l2arc_meta_cycles** = **2** (u64)

元数据可连续占用写入预算的周期数，之后将跳过以让数据运行。默认值 2 在持续负载下大约给元数据 67%、数据 33% 的 L2ARC 写入带宽。较高值偏向元数据；设置为 0 可禁用。

### **l2arc_write_max** = **33554432**B (32 MiB) (u64)

每个 L2ARC 设备的最大写入速率（字节/秒）。在初始填充、DWPD 限制禁用或非持久 L2ARC 时直接使用。启用 DWPD 限制时，写入速率受此上限约束。总 L2ARC 吞吐量随池中缓存设备数量线性扩展。

### **l2arc_rebuild_enabled** = **1**|0 (int)

在导入池时重建 L2ARC（持久化 L2ARC）。如果在导入池或附加 L2ARC 设备时遇到问题（例如 L2ARC 设备读取存储日志元数据速度慢，或元数据已碎片化/不可用），可以禁用此功能。

### **l2arc_rebuild_blocks_min_l2size** = **1073741824**B (1 GiB) (u64)

写入 L2ARC 日志块所需的 L2ARC 设备最小尺寸。日志块用于在导入池时重建持久化 L2ARC。

对于小于 **1 GiB** 的 L2ARC 设备，`l2arc_evict` 驱逐的数据量相比于恢复的 L2ARC 数据量来说非常大。在这种情况下，为避免浪费空间，不会在 L2ARC 中写入日志块。

### **metaslab_aliquot** = **2097152**B (2 MiB) (u64)

每个子 vdev 在 metaslab 组中的分配粒度（字节）。大致相当于传统 RAID 阵列中的“条带大小”。在正常操作中，ZFS 会尝试在每个顶级 vdev 的子设备上写入此大小的数据，然后再移动到下一个顶级 vdev。

### **metaslab_bias_enabled** = **1**|0 (int)

根据 metaslab 组相对于 metaslab 类平均值的过度或不足利用启用偏置分配。如果禁用，每个 metaslab 组将按其容量比例进行分配。

### **metaslab_perf_bias** = **1**|0|2 (int)

控制基于写入性能的 metaslab 组偏向分配。设置为 **0** 时，所有 metaslab 组将获得固定数量的分配。设置为 **2** 时，更快的 metaslab 组可以获得更多分配。设置为 **1** 时，如果池受写入吞吐量限制，则等同于 **2**；否则等同于 **0**。也就是说，如果池的性能受写入速度限制，则优先从更快的 metaslab 组分配，否则尝试均匀分配。

### **metaslab_force_ganging** = **16777217**B (16 MiB + 1 B) (u64)

将超过某个大小的块强制为 gang 块。该选项用于测试套件以便测试。

### **metaslab_force_ganging_pct** = **3**% (uint)

对于可被强制为 gang 块的块（由 **metaslab_force_ganging** 决定），强制其中的百分比块为 gang 块。

### **brt_zap_prefetch** = **1**|0 (int)

控制即将克隆的块的 BRT 记录是否进行预取。

### **brt_zap_default_bs** = **13** (8 KiB) (int)

默认 BRT ZAP 数据块大小，以 2 的幂表示。注意，在池上创建 BRT 后更改此值不会影响现有 BRT，只会影响新创建的 BRT。

### **brt_zap_default_ibs** = **13** (8 KiB) (int)

默认 BRT ZAP 间接块大小，以 2 的幂表示。注意，在池上创建 BRT 后更改此值不会影响现有 BRT，只会影响新创建的 BRT。

### **ddt_zap_default_bs** = **15** (32 KiB) (int)

默认 DDT ZAP 数据块大小，以 2 的幂表示。注意，在池上创建 DDT 后更改此值不会影响现有 DDT，只会影响新创建的 DDT。

### **ddt_zap_default_ibs** = **15** (32 KiB) (int)

默认 DDT ZAP 间接块大小，以 2 的幂表示。注意，在池上创建 DDT 后更改此值不会影响现有 DDT，只会影响新创建的 DDT。

### **zfs_default_bs** = **9** (512 B) (int)

默认 dnode 块大小，以 2 的幂表示。

### **zfs_default_ibs** = **17** (128 KiB) (int)

默认 dnode 间接块大小，以 2 的幂表示。

### **zfs_dio_enabled** = **1**|0 (int)

启用 Direct I/O。如果此设置为 0，则所有 I/O 请求将通过 ARC 定向处理，就像数据集属性 **direct** 设置为 **disabled** 一样。

### **zfs_dio_strict** = **0**|1 (int)

严格执行 Direct I/O 请求的对齐，如果未按页对齐，则返回 **EINVAL**，而不是静默回退到未缓存 I/O。

### **zfs_history_output_max** = **1048576**B (1 MiB) (u64)

在尝试将 ioctl 输出 nvlist 记录到磁盘历史时，如果输出大于此大小（字节），则不会存储。该值必须小于 **DMU_MAX_ACCESS**（64 MiB）。主要适用于 `zfs_ioc_channel_program`（参见 zfs-program(8)）。

### **zfs_keep_log_spacemaps_at_export** = **0**|1 (int)

防止在池导出或销毁时销毁日志空间映射。

### **zfs_metaslab_segment_weight_enabled** = **1**|0 (int)

启用/禁用基于段的 metaslab 选择。

### **zfs_metaslab_switch_threshold** = **2** (int)

使用基于段的 metaslab 选择时，继续从活动 metaslab 分配，直到耗尽该选项指定数量的桶。

### **metaslab_debug_load** = **0**|1 (int)

在池导入时加载所有 metaslab。

### **metaslab_debug_unload** = **0**|1 (int)

防止 metaslab 被卸载。

### **metaslab_fragmentation_factor_enabled** = **1**|0 (int)

启用在计算 metaslab 权重时使用碎片化指标。

### **metaslab_df_max_search** = **16777216**B (16 MiB) (uint)

从上一个偏移量向前搜索的最大距离。没有此限制时，碎片化的池可能会经历超过 *100 000* 次迭代，且 [`metaslab_block_picker`](https://openzfs.github.io/openzfs-docs/man/master/4/zfs.4.html#metaslab_block_picker)() 成为高性能存储上的性能瓶颈。

在默认设置 **16 MiB** 下，即使对于高度碎片化且 **ashift**=9 的池，通常也只会出现少于 *500* 次迭代。可能的最大迭代次数为 **metaslab_df_max_search / 2^(ashift+1)**。以默认 **16 MiB** 设置计算，**ashift**=9 时为 *16 × 1024*，**ashift**=12 时为 *2 × 1024*。


### **metaslab_df_use_largest_segment** = **0**|1 (int)

如果未向前搜索（由于 **metaslab_df_max_search**、**metaslab_df_free_pct** 或 **metaslab_df_alloc_threshold**），该可调参数控制使用哪个段。设置为 1 时使用最大空闲段；未设置时使用至少满足请求大小的段。

### **zfs_metaslab_max_size_cache_sec** = **3600**秒 (1 小时) (u64)

当我们卸载一个 metaslab 时，会缓存其最大空闲块的大小。我们使用这个缓存的大小来决定在进行分配时是否加载该 metaslab。随着该 metaslab 在未加载状态下的空闲块数量不断增加，缓存的最大块大小会越来越不准确。在经过由此可调参数控制的若干秒后，我们将不再使用缓存的最大块大小，而只考虑直方图信息。

### **zfs_metaslab_mem_limit** = **25**% (uint)

在加载新的 metaslab 时，我们会检查用于存储 metaslab 范围树的内存使用量。如果超过阈值，系统会尝试卸载最近最少使用的 metaslab，以防止范围树占满系统内存。该可调参数设置了作为阈值的系统总内存百分比。


### **zfs_metaslab_try_hard_before_gang** = **0**|1 (int)

* 如果未设置，系统将首先尝试普通分配。
  * 如果失败，则进行 gang 分配。
  * 如果仍失败，则进行“尽力” gang 分配。
  * 如果仍失败，则使用多层 gang 块。

* 如果已设置，系统将首先尝试普通分配。
  * 如果失败，则进行“尽力”分配。
  * 如果仍失败，则进行 gang 分配。
  * 如果仍失败，则进行“尽力” gang 分配。
  * 如果仍失败，则使用多层 gang 块。


### **zfs_metaslab_find_max_tries** = **100** (uint)

当不使用“尽力”策略时，我们只考虑数量有限的最佳 metaslab。这能提升性能，尤其是在每个 vdev 上 metaslab 数量很多且当前分配无法满足时（否则系统将会遍历所有 metaslab）。


### **zfs_vdev_default_ms_count** = **200** (uint)

新增 vdev 时，每个顶层 vdev 的目标 metaslab 数量。

### **zfs_vdev_default_ms_shift** = **29** (512 MiB) (uint)

metaslab 大小的默认下限。

### **zfs_vdev_max_ms_shift** = **34** (16 GiB) (uint)

metaslab 大小的默认上限。

### **zfs_vdev_max_auto_ashift** = **14** (uint)

在为新的顶层 vdev 优化逻辑 → 物理扇区大小时使用的最大 ashift。可以增加到 **ASHIFT_MAX**（16），但这可能会对存储池的空间效率产生负面影响。

### **zfs_vdev_direct_write_verify** = **Linux 1** | **FreeBSD 0** (uint)

如果非零，则每次发起 Direct I/O 写入时都会验证校验和，并在提交到块指针之前进行检查。如果校验和无效，该 I/O 操作将返回 **EIO**。此模块参数可用于检测在执行 Direct I/O 写入过程中用户缓冲区的内容是否发生变化，也有助于识别报告的校验和错误是否与 Direct I/O 写入相关。每次验证错误都会触发一个 zevent **dio_verify_wr**。Direct Write I/O 校验和验证错误可以通过 `zpool status -d` 查看。该参数在 Linux 上的默认值为 1，但在 FreeBSD 上为 0，因为在 FreeBSD 中，用户页面可以在发起 Direct I/O 写入之前被设置为写保护。


### **zfs_vdev_min_auto_ashift** = **ASHIFT_MIN** (9) (uint)

创建新顶层 vdev 时使用的最小 ashift。

### **zfs_vdev_min_ms_count** = **16** (uint)

顶层 vdev 中创建的最少 metaslab 数量。

### **vdev_validate_skip** = **0**|1 (int)

在导入池时跳过标签验证步骤。仅在了解风险并恢复损坏标签时修改，否则不推荐更改。

### **zfs_vdev_ms_count_limit** = **131072** (128k) (uint)

顶层 vdev 的 metaslab 总数的实际上限。

### **metaslab_preload_enabled** = **1**|0 (int)

启用 metaslab 组预加载。

### **metaslab_preload_limit** = **10** (uint)

每组可预加载的最大 metaslab 数量。

### **metaslab_preload_pct** = **50** (uint)

用于 metaslab 预加载任务的 CPU 百分比。

### **metaslab_lba_weighting_enabled** = **1**|0 (int)

给低 LBA 的 metaslab 更高权重，假设它们带宽更大，这通常适用于现代恒速盘（CAV）硬盘。

### **metaslab_unload_delay** = **32** (uint)

在一个 metaslab 被使用之后，我们会保持其加载状态 **此处指定的 TXG 数**，以尽量减少不必要的重新加载。注意，只有当这些 TXG 数和 **metaslab_unload_delay_ms** 所指定的毫秒数都过去之后，才会卸载该 metaslab。

### **metaslab_unload_delay_ms** = **600000** 毫秒 (10 分钟) (uint)

在一个 metaslab 被使用之后，我们会保持其加载状态 **此处指定的毫秒数**，以尽量减少不必要的重新加载。注意，只有当这段毫秒数和 **metaslab_unload_delay** 所对应的 TXG 都过去之后，才会卸载该 metaslab。

### **reference_history** = **3** (uint)

在启用 **reference_tracking_enable** 时，跟踪的最大引用持有者数量。

### **raidz_expand_max_copy_bytes** = **160MB** (ulong)

RAID-Z 扩展 I/O 可使用的最大内存量。限制一次性可挂起的 I/O 数量。

### **raidz_expand_max_reflow_bytes** = **0** (ulong)

用于测试，当重排（reflow）量达到该值时暂停 RAID-Z 扩展。

### **raidz_io_aggregate_rows** = **4** (ulong)

在扩展 RAID-Z 中，对超过此行数的读取进行聚合。

### **reference_tracking_enable** = **0**|1 (int)

跟踪 **refcount_t** 对象的引用持有者（仅调试构建）。

### **send_holes_without_birth_time** = **1**|0 (int)

启用时，不使用 **hole_birth** 优化，`zfs send` 总是发送所有 hole。适用于怀疑数据集受 **hole_birth** 错误影响的情况。

### **spa_config_path** = /etc/zfs/zpool.cache (charp)

SPA 配置文件路径。

### **spa_asize_inflation** = **24** (uint)

用于根据写入数据的大小估算实际磁盘占用的乘数因子。默认值为最坏情况的估算，但根据具体池的配置，较低的值也可能有效。熟悉相关因素的池管理员可能希望指定一个更贴近实际的膨胀因子，尤其是在接近配额或容量限制时。

### **spa_load_print_vdev_tree** = **0**|1 (int)

在池导入时，是否在调试消息缓冲区打印 vdev 树。

### **spa_load_verify_data** = **1**|0 (int)

在进行“极端回滚”（`-X`）导入时是否遍历数据块。

极端回滚导入通常会对池中的所有块进行完整遍历以进行校验。如果未设置此参数，则遍历会跳过非元数据块。导入开始后可切换此参数，以停止或启动对非元数据块的遍历。

### **spa_load_verify_metadata** = **1**|0 (int)

在进行“极端回滚”（`-X`）池导入时是否遍历块。

极端回滚导入通常会对池中的所有块进行完整遍历以进行校验。如果未设置此参数，则不会执行遍历。导入开始后可切换此参数，以停止或启动遍历。


### **spa_load_verify_shift** = **4** (1/16) (uint)

在池导入期间，设置最多消耗的字节数，相对于目标 ARC 大小的 log2 分数。

### **spa_slop_shift** = **5** (1/32) (int)

通常情况下，不允许池中最后 **3.2%**（**1/2^spa_slop_shift**）的空间被使用。这确保了由于未计入的更改（例如对 MOS 的修改），池不会完全耗尽空间。同时，它也限制了最坏情况下的空间分配时间。如果剩余可用空间少于该数量，大多数 ZPL 操作（如写入、创建）将返回 **ENOSPC**。


### **spa_num_allocators** = **4** (int)

确定每个 spa 实例使用的块分配器数量。该数量会通过 **spa_cpus_per_allocator** 限制，不会超过系统中实际 CPU 的数量。

请注意，将此值设置过高可能导致性能下降和/或过度碎片化。该设置仅对之后导入或创建的池生效。


### **spa_cpus_per_allocator** = **4** (int)

每个 SPA 实例的块分配器对应的最少 CPU 数量。仅对之后导入/创建的池生效。

### **spa_upgrade_errlog_limit** = **0** (uint)

在启用 **head_errlog** 特性时，限制转换为新格式的磁盘错误日志条目数量。默认是转换所有日志条目。

### **vdev_read_sit_out_secs** = **600** 秒 (10 分钟) (ulong)

当检测到某个磁盘异常缓慢时，该磁盘会被置于“sit out”状态。在 sit out 状态下，该磁盘不会参与正常读操作，其数据将按需通过校验重建。即便磁盘处于 sit out 状态，scrub 操作仍会从该磁盘读取数据。RAID-Z 或 dRAID vdev 中允许同时有多个磁盘处于 sit out 状态，但不超过校验磁盘的数量。为了保持完整冗余，写操作仍会发送到处于 sit out 状态的磁盘。默认值为 600 秒，设置为 0 则完全禁用磁盘 sit out，包括慢速磁盘异常检测。


### **vdev_raidz_outlier_check_interval_ms** = **1000** ms (1 秒) (ulong)

每个 RAID-Z 和 dRAID vdev 检查慢速磁盘异常的频率。增加此间隔会降低检测的灵敏度（因为统计数据包括自上次检查以来的所有 I/O），但会延迟对磁盘出现问题的响应。默认值为每秒一次；设置过小可能会对性能产生负面影响。

### **vdev_raidz_outlier_insensitivity** = **50** (uint)

在对 RAID-Z 和 dRAID vdev 执行慢速异常磁盘检查时，此值用于确定一个异常磁盘必须偏离多远才算作需要考虑的事件。该参数被描述为“不敏感度”，因为数值越大，检测到的异常越少。数值越小，则可能更积极地将可能有问题的磁盘置于 sit-out 状态，但可能显著增加误判的 sit-out 频率。

更技术地说，该参数是 Tukey’s Fence 检测算法中使用的四分位距（IQR）倍数。由于所考虑的分布很可能是极值分布而非典型的高斯分布，因此该倍数远高于常规 Tukey’s Fence 的 k 值。


### **vdev_removal_max_span** = **32768** B (32 KiB) (uint)

在顶级 vdev 移除过程中，数据块会从该 vdev 复制过来，其中可能包含空闲空间，以便通过增加带宽来换取 IOPS。此参数用于确定在复制的数据块中被视为“非必要”数据的最大空闲空间跨度（以字节为单位）。

这里的默认值选择与 **zfs_vdev_read_gap_limit** 对齐，该参数在执行常规读取时具有类似作用（但两者不必相同）。

### **vdev_file_logical_ashift** = **9** (512 B) (u64)

文件型设备的逻辑 ashift。

### **vdev_file_physical_ashift** = **9** (512 B) (u64)

文件型设备的物理 ashift。

### **zap_iterate_prefetch** = **1**|0 (int)

如果设置，在迭代 ZAP 对象时，预取整个对象（所有叶子块）。受 **dmu_prefetch_max** 限制。

### **zap_micro_max_size** = **131072** B (128 KiB) (int)

微型 ZAP 的最大尺寸。超过该大小后，“微型” ZAP 会升级为“胖” ZAP。默认最大 128 KiB，除非启用 **large_microzap** 功能。

### **zap_shrink_enabled** = **1**|0 (int)

如果设置，相邻空 ZAP 块会被合并以减少磁盘占用。

### **zfetch_min_distance** = **4194304** B (4 MiB) (uint)

每个流的最小预取字节数。预取距离从按需访问大小开始，并会快速增长到此值，每次命中时翻倍。在此之后，它可能每次命中再增加 1/8，但仅在自上次以来有些预取未能及时完成以满足按需请求的情况下，也就是说，预取深度未覆盖读取延迟或池已饱和。



### **zfetch_max_distance** = **67108864** B (64 MiB) (uint)

每个流的最大预取字节数。

### **zfetch_max_idistance** = **67108864** B (64 MiB) (uint)

每个流的间接块最大预取字节数。

### **zfetch_max_reorder** = **16777216** B (16 MiB) (uint)

与当前预取流位置相距在此字节范围内的请求被视为流的一部分，由于并行处理而重新排序。这类请求不会立即推进流位置，除非达到 **zfetch_hole_shift** 的填充阈值，但会被保存以便稍后填充流中的空洞。

### **zfetch_max_streams** = **8** (uint)

每个文件的最大预取流数。

### **zfetch_min_sec_reap** = **1** (uint)

非活动预取流被回收前的最短时间（秒）。

### **zfetch_max_sec_reap** = **2** (uint)

非活动预取流被删除前的最长时间（秒）。

### **zfs_abd_scatter_enabled** = **1**|0 (int)

启用 ARC 使用 scatter/gather 列表，并强制所有分配在内核内存中为线性分配。禁用此功能可以在某些代码路径下提高性能，但代价是内核内存可能会变得碎片化。


### **zfs_abd_scatter_max_order** = **MAX_ORDER-1** (uint)

scatter/gather 列表中单个块连续分配的最大内存页数。

**MAX_ORDER** 的取值依赖于内核配置。


### **zfs_abd_scatter_min_size** = **1536** B (1.5 KiB) (uint)

使用 scatter（基于页）ABD 的最小分配大小。较小分配将使用线性 ABD。

### **zfs_arc_dnode_limit** = **0** B (u64)

当 ARC 中 dnode 消耗的字节数超过此值时，会尝试在非元数据需求下取消固定其中一部分。该值作为 dnode 元数据的上限，默认为 **0**，表示根据 **zfs_arc_dnode_limit_percent** 的百分比，从 ARC 元缓冲区中划分可用于 dnode 的部分。


### **zfs_arc_dnode_limit_percent** = **10** % (u64)

ARC 元缓冲区中可被 dnode 消耗的百分比。

另见 **zfs_arc_dnode_limit**，其作用类似，但在非零时具有更高优先级。

### **zfs_arc_dnode_reduce_percent** = **10** % (u64)

当 dnode 消耗的字节数超过 **zfs_arc_dnode_limit** 时，尝试扫描的 ARC dnode 百分比，以响应对非元数据的需求。


### **zfs_arc_average_blocksize** = **8192** B (8 KiB) (uint)

ARC 的缓冲区哈希表大小是基于平均块大小假定的值来确定的。按此计算，每 1 GiB 物理内存大约需要 1 MiB 的哈希表（使用 8 字节指针）。对于已知平均块较大的配置，可以增加此值以减少内存占用。


### **zfs_arc_eviction_pct** = **200** % (uint)

当 `arc_is_overflowing` 调用时，`arc_get_data_impl` 会等待所请求数据量的一定百分比被回收。例如，默认情况下，每回收 *2 KiB* 数据，其中 *1 KiB* 可以被新分配“重用”。由于这个比例超过 **100**%，它保证了 **arc_size** 会向低于 **arc_c** 的目标推进。因为这是有限值，即使 **arc_size** 超过 **arc_c** 的时间较长，也能保证分配仍能进行。


### **zfs_arc_evict_batch_limit** = **10** (uint)

每个子列表在切换到下一个子列表之前要淘汰的 ARC 头数量。这种批处理式操作可以防止整个子列表一次性被淘汰，但代价是增加了额外的解锁和加锁开销。


### **zfs_arc_evict_batches_limit** = **5** (uint)

在高负载下，每个并行淘汰任务处理的 **zfs_arc_evict_batch_limit** 批次数，以减少上下文切换次数。

### **zfs_arc_evict_threads** = **0** (int)

设置用于 ARC 驱逐的线程数量。

如果设置大于 0，ZFS 将最多使用该数量的线程进行 ARC 驱逐。每个线程一次处理一个子列表，直到达到驱逐目标或所有子列表均已处理完毕。当设置为 0 时，ZFS 将根据 CPU 数量计算合理的驱逐线程数。


| CPU 数    | 线程数 |
| :-------: | :-------: |
| 1-4     | 1       |
| 5-8     | 2       |
| 9-15    | 3       |
| 16-31   | 4       |
| 32-63   | 6       |
| 64-95   | 8       |
| 96-127  | 9       |
| 128-160 | 11      |
| 160-191 | 12      |
| 192-223 | 13      |
| 224-255 | 14      |
| 256+    | 16      |


更多线程可能提高 ZFS 对内存压力的响应能力。当 ARC 驱逐成为读写瓶颈时，这对性能尤为重要。

此参数仅能在模块加载时进行设置。


### **zfs_arc_grow_retry** = **0**s (uint)

若设置为非零值，会替代默认 **arc_grow_retry**（5s）。该值表示 ARC 在内存压力事件后尝试恢复增长前等待的秒数。

### **zfs_arc_lotsfree_percent** = **10** % (int)

当系统空闲内存低于总内存的该百分比时，限制 I/O。设置为 **0** 可禁用限制。

### **zfs_arc_max** = **0** B (u64)

ARC 最大大小（以字节为单位）。如果为 **0**，则 ARC 最大大小由系统安装的内存量决定。使用 **all_system_memory - 1 GiB** 与 **all_system_memory × 5/8** 中较大的值作为上限。该值必须至少为 **67108864**B（64 MiB）。

此值可以动态修改，但有一些限制：运行时不能将其重新设置为 **0**，且将其减小到当前 ARC 大小以下不会导致 ARC 自动收缩，除非有内存压力触发收缩。

### **zfs_arc_meta_balance** = **500** (uint)

调整 ghost hits 时元数据与数据的平衡。值大于 100 时增加元数据缓存，同时按比例降低 ghost 数据命中对目标数据/元数据速率的影响。

### **zfs_arc_min** = **0** B (u64)

ARC 的最小大小（以字节为单位）。如果设置为 **0**，则 **arc_c_min** 默认为 **32 MiB** 与 **all_system_memory ÷ 32** 中的较大值。

### **zfs_arc_min_prefetch_ms** = **0** ms (≡1 s) (uint)

预取块在 ARC 中被锁定的最短时间。

### **zfs_arc_min_prescient_prefetch_ms** = **0** ms (≡6 s) (uint)

“预测性预取”块在 ARC 中被锁定的最短时间。这类块会被较激进地预取，提前于可能使用它们的代码。

### **zfs_arc_prune_task_threads** = **1** (int)

arc_prune 线程的数量。FreeBSD 不需要超过一个。Linux 理论上可以为每个挂载点使用一个线程，最多不超过 CPU 数量，但尚未证明这样有实际用处。

### **zfs_max_missing_tvds** = **0** (int)

允许在只读模式下导入池时缺失的顶层 vdev 数量。

### **zfs_max_nvlist_src_size** = **0** B (u64)

允许传递给 `/dev/zfs` 上 ioctl 的 **zc_nvlist_src_size** 的最大字节数。此设置可防止用户导致内核分配过多内存。当超过此限制时，ioctl 会返回 **EINVAL**，并在 zfs-dbgmsg 日志中记录错误描述。正常情况下无需修改此参数。如果为 **0**，在 FreeBSD 下相当于用户固定内存限制的四分之一，在 Linux 下相当于 **134217728**B（128 MiB）。

### **zfs_multilist_num_sublists** = **0** (uint)

为了允许更细粒度的锁定，每个 ARC 状态包含用于数据和元数据对象的一系列列表。锁定在这些“子列表”级别进行。此参数控制每个 ARC 状态的子列表数量，同时也适用于 multilist 数据结构的其他用途。如果为 **0**，则相当于在线 CPU 数量与 **4** 中的较大值。

### **zfs_arc_overflow_shift** = **8** (int)

当 ARC 大小超过当前 ARC 目标大小（**arc_c**）达到由此参数确定的阈值时，认为 ARC 已溢出。超过 (**arc_c** >> **zfs_arc_overflow_shift**) / 2 时开始 ARC 回收过程。如果仍不足以控制，超过 (**arc_c** >> **zfs_arc_overflow_shift**) × 1.5 时，将阻止新的缓冲区分配，直到回收线程赶上。已启动的回收过程会持续，直到 ARC 大小降至目标大小以下。

默认值 **8** 会导致 ARC 在超过目标大小 0.2% 时开始回收，在超过 0.6% 时阻止分配。

### **zfs_arc_shrink_shift** = **0** (uint)

若非零，会更新 **arc_shrink_shift**（默认 **7**）为新值。

### **zfs_arc_pc_percent** = **0** % (off) (uint)

ARC 回收目标占页缓存的百分比。

此可调参数允许 ZFS ARC 更好地与内核的 LRU 页缓存协作。它可以保证在页缓存扫描压力下 ARC 大小不会崩溃，但在必要时仍允许将 ARC 回收到 **zfs_arc_min**。该值以页缓存大小的百分比表示（通过 **NR_ACTIVE_FILE** + **NR_INACTIVE_FILE** 测量），百分比可超过 **100**。此设置仅在内存压力/回收时生效。

### **zfs_arc_shrinker_limit** = **0** (int)

这是 ARC 缩减器在一次页面分配尝试中可用于驱逐的页面数量限制。

注意，在实际操作中，内核的 shrinker 对一次分配尝试可能要求驱逐大约四倍于此值的页面。为了降低 OOM 风险，此限制仅对 kswapd 回收应用。例如，值为 **10000**（实际约为每次分配尝试 160 MiB，使用 4 KiB 页面）将尝试回收 ARC 内存的时间限制在每次分配尝试小于 100 ms，即使平均压缩块大小约为 8 KiB。

此参数可设置为 0（禁用限制），仅适用于 Linux。

### **zfs_arc_shrinker_seeks** = **2** (int)

在 Linux 上 ARC 回收的相对代价，即恢复被驱逐页面所需的寻道次数。较大的值会使 ARC 更“珍贵”，驱逐的量相对较小，与其他内核子系统相比更保守。值为 4 表示与页缓存相当。

### **zfs_arc_sys_free** = **0** B (u64)

ARC 应保留作为系统空闲内存的目标字节数。如果为零，则相当于 **512 KiB** 与 **all_system_memory/64** 中的较大值。

### **zfs_checksum_events_per_second** = **20**/s (uint)

将校验和事件的速率限制为每秒指定次数。注意，这个值不应低于 ZED 阈值（当前为 10 次校验和/10 秒），否则守护进程可能不会触发任何操作。

### **zfs_commit_timeout_pct** = **10**% (uint)

此参数控制当 ZIL 块（lwb）未“满”且有线程等待将其提交到稳定存储时，该块保持“打开”的时间。超时时间根据最近一次 lwb 延迟的百分比进行调整，以避免显著影响每个事务记录（itx）的延迟。

### **zfs_condense_indirect_commit_entry_delay_ms** = **0** ms (int)

Vdev 间接层（用于设备移除）在生成映射时会休眠指定毫秒数。用于测试套件中，以控制 vdev 移除速度。

### **zfs_condense_indirect_obsolete_pct** = **25**% (uint)

在 vdev 映射中尝试压缩所需的最小过时字节百分比（参见 **zfs_condense_indirect_vdevs_enable**）。用于测试套件，以便在需要时触发压缩。

### **zfs_condense_indirect_vdevs_enable** = **1** | 0 (int)

启用压缩间接 vdev 映射。设置后，如果映射使用的内存超过 **zfs_condense_min_mapping_bytes**，且过时空间映射对象在磁盘上使用的字节数超过 **zfs_condense_max_obsolete_bytes**，则尝试压缩间接 vdev 映射。压缩过程旨在通过移除过时映射来节省内存。

### **zfs_condense_max_obsolete_bytes** = **1073741824** B (1 GiB) (u64)

仅当过时空间映射对象在磁盘上的大小超过此字节数时，才尝试压缩间接 vdev 映射（参见 **zfs_condense_indirect_vdevs_enable**）。

### **zfs_condense_min_mapping_bytes** = **131072** B (128 KiB) (u64)

尝试压缩的最小 vdev 映射大小（参考 **zfs_condense_indirect_vdevs_enable**）。

### **zfs_dbgmsg_enable** = **1** | 0 (int)

在内部，ZFS 会维护一个小型日志以便调试。该日志默认启用，可以通过取消设置此选项来禁用。日志内容可通过读取 /proc/spl/kstat/zfs/dbgmsg 访问。向该文件写入 **0** 会清空日志。

此设置不影响 **zfs_flags** 引起的调试输出。

### **zfs_dbgmsg_maxsize** = **4194304** B (4 MiB) (uint)

ZFS 内部调试日志的最大大小。

### **zfs_dbuf_state_index** = **0** (int)

历史上用于控制 /proc/spl/kstat/zfs 下可用的报告内容，但现在没有任何作用。

### **zfs_deadman_checktime_ms** = **60000** ms (1 min) (u64)

检查时间（毫秒）。定义了检查“挂起”I/O 请求的频率，并在必要时触发 **zfs_deadman_failmode** 行为。

### **zfs_deadman_enabled** = **1** | 0 (int)

当池同步操作耗时超过 **zfs_deadman_synctime_ms**，或单个 I/O 操作耗时超过 **zfs_deadman_ziotime_ms** 时，该操作被视为“挂起”。如果 **zfs_deadman_enabled** 已启用，则会根据 **zfs_deadman_failmode** 调用 deadman 行为。默认情况下，deadman 已启用且设置为 **wait**，这会导致仅记录“挂起”的 I/O 操作。当池被挂起时，deadman 会自动禁用。

### **zfs_deadman_events_per_second** = **1**/s (int)

Deadman 生成 zevent（报告挂起 I/O）的速率限制，每秒允许数量。

### **zfs_deadman_failmode** = **wait** (charp)

控制 Deadman 检测到“挂起” I/O 操作时的处理方式。有效值包括：

#### **wait**

  等待“挂起”操作完成。每个挂起操作都会生成一个 Deadman 事件，描述该操作。

#### **continue**

  尝试通过重新派发 I/O 来恢复“挂起”操作（如果可能）。

#### **panic**

  触发系统 panic，可用于配合自动故障转移到已配置的备用节点。

### **zfs_deadman_synctime_ms** = **600000**ms (10 min) (u64)

定义 Deadman 被触发的时间间隔，同时也表示池同步操作被视为“挂起”的时间。超过此限制后，Deadman 会每 **zfs_deadman_checktime_ms** 毫秒触发一次，直到池同步完成。

### **zfs_deadman_ziotime_ms** = **300000**ms (5 min) (u64)

定义单个 I/O 操作被视为“挂起”的时间间隔。只要该操作仍然挂起，Deadman 将每 **zfs_deadman_checktime_ms** 毫秒触发一次，直到操作完成。

### **zfs_dedup_prefetch** = 0 | 1 (int)

启用对即将释放的去重块进行预取。

### **zfs_dedup_log_flush_min_time_ms** = **1000**ms (uint)

每个事务在刷新去重日志时至少花费的时间。即使会延迟事务，也会确保至少执行此时长的日志刷新，直到达到 **zfs_txg_timeout**。

### **zfs_dedup_log_flush_entries_min** = **100** (uint)

每个事务至少刷新此数量的条目。OpenZFS 会在每个 TXG 中刷新日志的一部分，以保持日志大小与写入速率成比例（参见 **zfs_dedup_log_flush_txgs**）。此设置定义了该估算的最小值，防止在写入速率下降时积压完全清空。提高该值可以迫使 OpenZFS 更积极地刷新日志，更快将积压降至零，但可能在日志刷新与其他 I/O 竞争过大时降低系统的回退能力。

### **zfs_dedup_log_flush_entries_max** = **UINT_MAX** (uint)

每个事务最多刷新这么多条目。主要用于调试。

### **zfs_dedup_log_flush_txgs** = **100** (uint)

处理整个去重日志所需的目标 TXG 数。每个 TXG，OpenZFS 会处理 DDT 积压大小的 1/100，从而保持积压与写入速率大致匹配。增大此值可提高去重日志效率，但会增加导入时间。

### **zfs_dedup_log_cap** = **UINT_MAX** (uint)

去重日志的软上限。如果日志大小超过此值，系统会增加刷新强度以尽量将日志降低到软上限。设置该值可减少导入时间，但会降低 DDT 日志效率，增加刷新同等数据量所需的 I/O 次数。

### **zfs_dedup_log_hard_cap** = 0 | 1 (uint)

是否将日志上限视为严格上限。

设置为 0（默认值）时，**zfs_dedup_log_cap** 会增加在给定 TXG 中刷新的最大日志条目数。这会将积压大小降低至上限附近，但不会导致 TXG 同步时间延长。如果设置为 1，上限更像是硬上限而非软上限；同时会增加每个 TXG 刷新的最小日志条目数。启用该选项会缩短最坏情况下的导入时间，但代价是增加 TXG 同步时间。

### **zfs_dedup_log_flush_flow_rate_txgs** = **10** (uint)

用于计算日志刷新流速的事务数量。OpenZFS 会基于最近若干事务的指数加权移动平均，计算条目变化率、刷新率和刷新时间率，并合成整体“流速”。增大此值可平滑处理峰值负载，但流速对持续写入率变化的响应会变慢。

### **zfs_dedup_log_txg_max** = **8** (uint)

刷新去重日志前允许累计的最大事务数。OpenZFS 维护两个去重日志：一个接收新变更，另一个用于刷新。若无待刷条目，最多累积此数量的事务后开始切换日志并刷新。

### **zfs_dedup_log_mem_max** = **0** (u64)

用于去重日志的最大内存。OpenZFS 在内存使用达到此值的一半时开始刷新。默认 0 表示由 **zfs_dedup_log_mem_max_percent** 来确定实际限制。

### **zfs_dedup_log_mem_max_percent** = **1**% (uint)

去重日志使用的最大内存占总内存的百分比。
如果 **zfs_dedup_log_mem_max** 未设置，则会按系统总内存的这个百分比初始化。

### **zfs_delay_min_dirty_percent** = **60**% (uint)

当脏数据量达到此百分比（相对于 **zfs_dirty_data_max**）时，开始延迟每个事务。
此值应至少与 **zfs_vdev_async_write_active_max_dirty_percent** 相等。参见 ZFS 事务延迟。

### **zfs_delay_scale** = **500000** (int)

控制事务延迟增长到无穷大的速度。
值越大，给定脏数据量的延迟越长。为了最平滑的延迟，该值应约等于 10^9 除以最大每秒操作数。这可平滑处理高于或低于此操作数的情况。
**zfs_delay_scale × zfs_dirty_data_max** 必须小于 2^64。

### **zfs_dio_write_verify_events_per_second** = **20**/s (uint)

限制 Direct I/O 写验证事件的速率，每秒不超过此值。

### **zfs_disable_ivset_guid_check** = 0 | 1 (int)

禁用加密数据集原始接收时 IVset GUID 必须存在且匹配的要求。
用于早期 OpenZFS 版本创建的池，现在可能存在兼容性问题的用户。

### **zfs_key_max_salt_uses** = 400000000 (4×10^8) (ulong)

单个盐值在生成新盐值前的最大使用次数，用于加密数据集。默认值即为最大值。

### **zfs_object_mutex_size** = **64** (uint)

用于 znode 哈希表的锁大小。
由于对象可能尚不存在，内核不会为每个对象创建互斥锁，而是使用哈希表管理，哈希冲突时对象会等待，即使实际上没有同对象的竞争。

### **zfs_slow_io_events_per_second** = **20**/s (int)

限制慢 I/O 报告事件（delay zevents）的速率，每秒不超过此值。

### **zfs_unflushed_max_mem_amt** = **1073741824**B (1 GiB) (u64)

日志空间映射在内存中持有的未刷写元数据变更的上限（以字节为单位）。

### **zfs_unflushed_max_mem_ppm** = **1000**ppm (0.1%) (u64)

ZFS 允许用于未刷写元数据变更的系统总内存比例，以百万分之一计。

### **zfs_unflushed_log_block_max** = **131072** (128k) (u64)

描述每个池允许的日志空间映射块的最大数量。默认值表示所有日志空间映射中的空间总和不能超过 **131072** 块（意味着在压缩和复制块之前的逻辑空间约为 *16 GiB*，假设块大小为 *128 KiB*）。

这个可调参数的重要性在于，它涉及“非干净导出后的导入时间”与“元块刷新频率”之间的权衡。数值越高，池处于活动状态时允许的日志块越多，这意味着刷新元块的频率降低，从而减少每个 TXG 对空间映射更新的 I/O 操作次数。但同时，这也意味着在发生非干净导出时，需要读取的日志空间映射块更多，从而增加池导入时间的开销。数值越低，刷新频率增加，日志块在变为过时后会更快被销毁，从而在崩溃后的导入过程中需要读取的块更少。

每个在池导入期间存在的日志空间映射块会导致大约一次额外的逻辑 I/O。这也是为什么该参数以块数而非使用空间的形式暴露出来的原因。

### **zfs_unflushed_log_block_min** = **1000** (u64)

当 metaslab 数量较少且写入速率较高时，可能出现每个 TXG 都刷写所有 metaslab 的情况。此参数确保至少允许存在这么多日志块。

### **zfs_unflushed_log_block_pct** = **400**% (u64)

用于确定日志空间映射可使用块数，相对于池中未刷写 metaslab 总数的百分比。

### **zfs_unflushed_log_txg_max** = **1000** (u64)

限制任意 metaslab 在未刷写状态下可持续的最大 TXG 数。有效地限制了未正常导出池后需要读取的每 TXG 日志块的最大数量。

### **zfs_unlink_suspend_progress** = **0**|1 (uint)

启用后，文件不会被异步从待删除列表移除，所占空间会暂时“泄漏”。禁用此选项并重新挂载数据集后，待删除操作会被处理，释放的空间返回池中。此选项主要用于测试套件。

### **zfs_delete_blocks** = **20480** (ulong)

定义大文件的阈值。大于 **zfs_delete_blocks** 的文件将异步删除，小于该值的文件同步删除。降低此值可减少 unlink(2) 系统调用的执行时间，但会延长释放空间的延迟。仅适用于 Linux。

### **zfs_dirty_data_max** = (int)

定义脏数据空间的上限（字节）。超过此上限后，新写入将被阻塞，直至空间释放。此参数优先于 **zfs_dirty_data_max_percent**。默认值为 **physical_ram/10**，并受 **zfs_dirty_data_max_max** 限制。

### **zfs_dirty_data_max_max** = (int)

**zfs_dirty_data_max** 的最大允许值（字节）。此限制仅在模块加载时生效，如果之后修改 **zfs_dirty_data_max** 将被忽略。该参数优先于 **zfs_dirty_data_max_max_percent**。默认值为 **min(physical_ram/4, 4GiB)**，32 位系统为 **min(physical_ram/4, 1GiB)**。

### **zfs_dirty_data_max_max_percent** = **25**% (uint)

**zfs_dirty_data_max** 的最大允许值，以物理内存百分比表示。仅在模块加载时生效，之后修改 **zfs_dirty_data_max** 会被忽略。优先级低于 **zfs_dirty_data_max_max**。

### **zfs_dirty_data_max_percent** = **10**% (uint)

确定脏数据空间的上限，以系统总内存的百分比表示。一旦超过该上限，新的写入将被暂停，直到空间释放。参数 **zfs_dirty_data_max** 优先于此设置。参见 ZFS 事务延迟。受 **zfs_dirty_data_max_max** 限制。

### **zfs_dirty_data_sync_percent** = **20**% (uint)

当脏数据达到 **zfs_dirty_data_max** 的此百分比时，开始同步事务组。应小于 **zfs_vdev_async_write_active_min_dirty_percent**。

### **zfs_wrlog_data_max** = (int)

写事务 ZIL 日志数据的上限（字节）。当接近此上限时，写入操作将被限流，直到事务组同步后日志数据被清理。因存在额外开销，应至少设为 **zfs_dirty_data_max** 的两倍以保障写入吞吐，同时不得超过 slog 设备大小（如果存在）。默认值为 **zfs_dirty_data_max × 2**。

### **zfs_fallocate_reserve_percent** = **110**% (uint)

由于 ZFS 是写时复制文件系统且支持快照，不能为文件预先分配块以保证后续写入不会耗尽空间。`fallocate(2)` 仅检查池或用户项目配额当前是否有足够空间，然后创建所请求大小的稀疏文件。请求空间会乘以 **zfs_fallocate_reserve_percent** 以预留间接块和其他内部元数据所需的额外空间。设置为 **0** 会禁用 `fallocate(2)` 支持，并返回 **EOPNOTSUPP**。

### **zfs_fletcher_4_impl** = **fastest** (string)

选择 Fletcher 4 校验算法的实现。可选值包括：**fastest**、**scalar**、**sse2**、**ssse3**、**avx2**、**avx512f**、**avx512bw** 和 **aarch64_neon**。除 **fastest** 和 **scalar** 外，其余选项需要 CPU 指令集支持，并仅在运行时检测到可用时出现。若有多个实现，**fastest** 会通过微基准测试选择最快者。选择 **scalar** 使用原始 CPU 计算；选择其他选项则使用对应向量指令。

### **zfs_bclone_enabled** = **1**|0 (int)

启用块克隆功能。若设为 0，即使 feature@block_cloning 已启用，尝试克隆块的函数和系统调用也会表现为功能被禁用。

### **zfs_bclone_strict_properties** = **1**|0 (int)

限制不同属性（校验和、压缩、拷贝数、去重或 special_small_blocks）的数据集之间的块克隆。

### **zfs_bclone_wait_dirty** = **1**|0 (int)

设置为 1 时，FICLONE 和 FICLONERANGE ioctl 会等待所有脏数据写入磁盘后再继续，保证克隆操作可靠，即使文件在修改后立即被克隆。对小文件可能比直接复制慢。设置为 0 时，如遇脏块克隆操作会立即失败。默认启用等待。

### **zfs_blake3_impl** = **fastest** (string)

选择 BLAKE3 校验算法的实现。可选值包括：**cycle**、**fastest**、**generic**、**sse2**、**sse41**、**avx2**、**avx512**。除 **cycle**、**fastest** 和 **generic** 外，其余选项需要 CPU 指令集支持，仅在运行时检测到可用时出现。如果多个实现可用，**fastest** 会通过微基准测试选择最快者。可通过读取 `/proc/spl/kstat/zfs/chksum_bench` 查看基准结果。

### **zfs_free_bpobj_enabled** = **1**|0 (int)

启用或禁用 free_bpobj 对象的处理。

### **zfs_async_block_max_blocks** = **UINT64_MAX** (u64)

单个 TXG 中释放的最大块数（无限制）。

### **zfs_max_async_dedup_frees** = **250000** (u64)

单个 TXG 中可释放的去重、克隆或 gang 块的最大数量。这些释放可能需要额外 I/O，因此成本更高。

### **zfs_async_free_zio_wait_interval** = **2000** (u64)

释放此数量的去重、克隆或 gang 块后，等待所有挂起 I/O 完成再继续。

### **zfs_vdev_async_read_max_active** = **3** (uint)

每个设备最大异步读 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_async_read_min_active** = **1** (uint)

每个设备最小异步读 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_async_write_active_max_dirty_percent** = **60**% (uint)

当池中脏数据超过此百分比时，使用 **zfs_vdev_async_write_max_active** 限制活动异步写。若脏数据介于最小与最大之间，活动 I/O 限制按线性插值计算。参见 ZFS I/O 调度器。

### **zfs_vdev_async_write_active_min_dirty_percent** = **30**% (uint)

当池中脏数据低于此百分比时，使用 **zfs_vdev_async_write_min_active** 限制活动异步写。若脏数据介于最小与最大之间，活动 I/O 限制按线性插值计算。参见 ZFS I/O 调度器。

### **zfs_vdev_async_write_max_active** = **10** (uint)

每个设备最大异步写 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_async_write_min_active** = **2** (uint)

每个设备最小异步写 I/O 操作数。较低值有助于轮替盘延迟优化，但可能降低 resilver 性能。默认值 **2** 是折中选择，设置为 **3** 可进一步提升 resilver 性能，但会增加延迟。

### **zfs_vdev_initializing_max_active** = **1** (uint)

每个设备最大初始化 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_initializing_min_active** = **1** (uint)

每个设备最小初始化 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_max_active** = **1000** (uint)

每个设备允许的最大 I/O 操作总数，理想值应至少等于各队列 **max_active** 之和。参见 ZFS I/O 调度器。

### **zfs_vdev_open_timeout_ms** = **1000** (uint)

导入时等待设备响应的超时值（毫秒），用于处理因 udev 事件导致的临时路径丢失问题。

### **zfs_vdev_rebuild_max_active** = **3** (uint)

每个设备最大顺序 resilver I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_rebuild_min_active** = **1** (uint)

每个设备最小顺序 resilver I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_removal_max_active** = **2** (uint)

每个设备最大移除 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_removal_min_active** = **1** (uint)

每个设备最小移除 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_scrub_max_active** = **2** (uint)

每个设备最大 scrub I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_scrub_min_active** = **1** (uint)

每个设备最小 scrub I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_sync_read_max_active** = **10** (uint)

每个设备最大同步读 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_sync_read_min_active** = **10** (uint)

每个设备最小同步读 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_sync_write_max_active** = **10** (uint)

每个设备最大同步写 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_sync_write_min_active** = **10** (uint)

每个设备最小同步写 I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_trim_max_active** = **2** (uint)

每个设备最大 trim/discard I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_trim_min_active** = **1** (uint)

每个设备最小 trim/discard I/O 操作数。参见 ZFS I/O 调度器。

### **zfs_vdev_nia_delay** = **5** (uint)

对于非交互 I/O（scrub、resilver、removal、initialize 和 rebuild），同时活跃的 I/O 操作数限制为对应的 **zfs_*_min_active**，除非设备处于“空闲”状态。当没有交互 I/O 操作活动（同步或其他）且自上一次交互操作以来已有 **zfs_vdev_nia_delay** 个操作完成，则该设备被视为空闲，并将非交互操作的并发数增加至 **zfs_*_max_active**。参见 ZFS I/O 调度器。

### **zfs_vdev_nia_credit** = **5** (uint)

某些 HDD 会强烈优先顺序 I/O，以至于并发随机 I/O 延迟达到数秒。即使将 **zfs_*_max_active** 设置为 **1** 也无法缓解。为了防止 scrub 等非交互 I/O 垄断设备，当存在未完成的交互操作时，不允许发送超过 **zfs_vdev_nia_credit** 个非交互操作。此机制确保 HDD 在合理时间内响应交互 I/O。参见 ZFS I/O 调度器。

### **zfs_vdev_failfast_mask** = **1** (uint)

定义驱动在遇到特定错误类型时是否立即放弃重试。可以按位组合以下选项：

| 值 | 名称        | 描述         |
| :---: | :---------: | :----------: |
| 1 | Device    | 设备错误时驱动不重试 |
| 2 | Transport | 传输错误时驱动不重试 |
| 4 | Driver    | 驱动错误时驱动不重试 |

### **zfs_vdev_disk_max_segs** = **0** (uint)

BIO 可添加的最大段数（最小为 4）。如果超过设备队列或内核允许的最大值，将被限制。设置为 0 时使用内核理想值。仅适用于 Linux。

### **zfs_expire_snapshot** = **300** s (int)

**.zfs/snapshot** 下快照过期前的等待时间（秒）。

### **zfs_admin_snapshot** = **0**|1 (int)

允许通过 **.zfs/snapshot** 目录创建、删除或重命名条目来触发快照的创建、销毁或重命名。启用后，此功能在本地和设置了 *no_root_squash* 的 NFS 导出上均可用。

### **zfs_snapshot_no_setuid** = **0**|1 (int)

是否禁用快照挂载的 *setuid/setgid* 支持，通过在挂载时加上 *nosuid* 选项实现。

### **zfs_flags** = **0** (int)

设置附加调试标志。以下标志可按位组合：

|       | 值     | 名称                          | 说明                                                           |
| :-----: | :-----: | :---------------------------: | :------------------------------------------------------------ |
|       | 1     | ZFS_DEBUG_DPRINTF           | 在调试日志中启用 dprintf 条目。                                         |
| 注 | 2     | ZFS_DEBUG_DBUF_VERIFY       | 启用额外的 dbuf 验证。                                               |
| 注 | 4     | ZFS_DEBUG_DNODE_VERIFY      | 启用额外的 dnode 验证。                                              |
|       | 8     | ZFS_DEBUG_SNAPNAMES         | 启用快照名称验证。                                                    |
| 注 | 16    | ZFS_DEBUG_MODIFY            | 检查 ARC 缓冲区是否被非法修改。                                           |
|       | 64    | ZFS_DEBUG_ZIO_FREE          | 启用块释放验证。                                                     |
|       | 128   | ZFS_DEBUG_HISTOGRAM_VERIFY  | 启用额外的 spacemap 直方图验证。                                        |
|       | 256   | ZFS_DEBUG_METASLAB_VERIFY   | 验证磁盘上的空间计数是否与内存中的 **range_trees** 匹配。                        |
|       | 512   | ZFS_DEBUG_SET_ERROR         | 在调试日志中启用 **SET_ERROR** 和 dprintf 条目。                         |
|       | 1024  | ZFS_DEBUG_INDIRECT_REMAP    | 验证由设备移除导致的拆分块。                                               |
|       | 2048  | ZFS_DEBUG_TRIM              | 验证 TRIM 范围始终在可分配范围树内。                                        |
|       | 4096  | ZFS_DEBUG_LOG_SPACEMAP      | 验证日志摘要与 spacemap 日志一致，并启用 **zfs_dbgmsgs** 用于 metaslab 加载和刷新。 |
|       | 8192  | ZFS_DEBUG_METASLAB_ALLOC    | 当分配失败时启用调试消息。                                                |
|       | 16384 | ZFS_DEBUG_BRT               | 启用与 BRT 相关的调试消息。                                             |
|       | 32768 | ZFS_DEBUG_RAIDZ_RECONSTRUCT | 启用 raidz 重建的调试消息。                                            |
|       | 65536 | ZFS_DEBUG_DDT               | 启用与 DDT 相关的调试消息。                                             |

注：需要调试版本构建。

### **zfs_btree_verify_intensity** = **0** (uint)

启用 btree 验证，以下设置可累加：

|       | 值 | 描述                 |
| :-----: | :---: | :------------------ |
|       | 1 | 验证高度              |
|       | 2 | 验证从子节点到父节点的指针     |
|       | 3 | 验证元素计数           |
|       | 4 | 验证元素顺序（开销大）       |
| 注 | 5 | 验证未使用内存是否被毒化（开销大） |

注：需要调试版本构建。

### **zfs_free_leak_on_eio** = **0** | 1 (int)

当销毁操作在读取元数据（如间接块）时遇到 **EIO** 错误，通常引用这些缺失元数据的空间无法释放。默认情况下，这会导致后台销毁“暂停”，因为无法继续前进。在暂停状态下，所有待释放的空间会“暂时泄漏”。
设置此标志会忽略 **EIO** 错误，永久泄漏无法读取的间接块空间，同时继续释放其余可释放空间。

默认的“暂停”行为在存储部分失败（即部分 I/O 操作失败）然后恢复的情况下非常有用。此时可以在部分失败期间继续池操作，并在恢复后继续释放空间，无泄漏。然而，这种情况实际较少发生。

通常，存储池要么：

1. 完全失败（可能是暂时的，例如顶级 vdev 离线），
2. 出现局部永久错误（例如磁盘因位翻转或固件错误返回错误数据）。

对于第一种情况，此设置无影响，因为池会被挂起，同步线程无法前进。对于第二种情况，由于错误是永久性的，设置此标志可以最小化空间泄漏。因此，通常可以设置该标志，但出于保守考虑，默认不设置，以避免在“部分暂时性”失败情况下泄漏空间。

### **zfs_free_min_time_ms** = **500**ms (uint)

在使用 **async_destroy** 功能的 `zfs destroy` 操作中，每个 TXG 至少花费此时间用于释放块。

### **zfs_obsolete_min_time_ms** = **500**ms (uint)

与 **zfs_free_min_time_ms** 类似，但用于清理已移除 vdev 的旧间接记录。

### **zfs_immediate_write_sz** = **32768**B (32 KiB) (s64)

当 **logbias** = **latency** 时，将数据直接写入 ZIL 的最大写入大小。较大的写入会以间接方式写入，类似 **logbias** = **throughput**。如果存在 SLOG，此参数被忽略，相当于无限大，所有写入数据都会写入 ZIL，不依赖常规 vdev 的延迟。

### **zil_special_is_slog** = **1** | 0 (int)

启用后，当写入块到达普通 vdev 时，将当前的 special vdev 当作 SLOG 处理。写入 special vdev 的块仍以间接方式写入，类似 **logbias** = **throughput**。如果已经存在 SLOG，此参数被忽略。

### **zfs_import_defer_txgs** = **5** (uint)

在导入池后等待的事务组数量，才开始后台操作，如异步释放块（来自快照、克隆或去重）以及 scrub 或 resilver。可让池导入和文件系统挂载更快完成，避免后台干扰。默认值 5 事务组通常足够大多数系统使用。

### **zfs_initialize_value** = **16045690984833335022** (0xDEADBEEFDEADBEEE) (u64)

由 zpool-initialize(8) 写入 vdev 空闲空间的模式值。

### **zfs_initialize_chunk_size** = **1048576**B (1 MiB) (u64)

zpool-initialize(8) 写入的块大小。测试套件使用此选项。

### **zfs_livelist_max_entries** = **500000** (5×10^5) (u64)

创建新子 livelist 的阈值（以块指针计）。较大的子列表占用更多内存，但子列表越少，插入成本越低。

### **zfs_livelist_min_percent_shared** = **75**% (int)

快照与克隆间共享空间低于此阈值时，克隆关闭 livelist 并回退至旧的删除方法。因为当克隆被覆盖足够多时，livelist 已不再有优势。

### **zfs_livelist_condense_new_alloc** = **0** (int)

在 condense livelist 时，每次添加额外 ALLOC blkptr 都会递增此值。测试套件用于跟踪竞态条件。

### **zfs_livelist_condense_sync_cancel** = **0** (int)

在 `spa_livelist_condense_sync` 中每次 condense 被取消时递增。用于测试竞态条件。

### **zfs_livelist_condense_sync_pause** = **0** | 1 (int)

启用时，livelist condense 进程在执行同步任务 `spa_livelist_condense_sync` 前无限暂停。用于测试竞态条件。

### **zfs_livelist_condense_zthr_cancel** = **0** (int)

在 `spa_livelist_condense_cb` 中，每次 condense 被取消时递增。用于测试竞态条件。

### **zfs_livelist_condense_zthr_pause** = **0** | 1 (int)

启用时，livelist condense 进程在执行 `spa_livelist_condense_cb` 中的 open context condensing 工作前无限暂停。测试套件用于触发竞态条件。

### **zfs_lua_max_instrlimit** = **100000000** (10^8) (u64)

ZFS 通道程序可设置的最大执行时间限制，以 Lua 指令数量计。

### **zfs_lua_max_memlimit** = **104857600** (100 MiB) (u64)

ZFS 通道程序可设置的最大内存限制，以字节计。

### **zfs_max_dataset_nesting** = **50** (int)

嵌套数据集的最大深度。可临时调整以修复已存在的超过预设限制的数据集。

### **zfs_max_log_walking** = **5** (u64)

日志 spacemap 功能刷新算法用于估算即将写入的日志块的过去 TXG 数量。

### **zfs_max_logsm_summary_length** = **10** (u64)

spacemap 日志摘要允许的最大行数。

### **zfs_max_recordsize** = **16777216** (16 MiB) (uint)

支持的块大小范围为 512 B 至 16 MiB。大块可提高 I/O 效率，但修改单字节时需 COW 整块，可能影响 I/O 延迟和内存分配器。历史上默认禁止创建大于 1 MiB 的块，但可以通过调整创建更大块。x86_32 系统默认仍限制为 1 MiB，因为 Linux 3/1 内存划分无法容纳 16M 块。

### **zfs_allow_redacted_dataset_mount** = **0** | 1 (int)

允许挂载通过 redacted send/receive 接收的数据集。通常禁用，因为这些数据集可能缺失关键数据。

### **zfs_min_metaslabs_to_flush** = **1** (u64)

每个 dirty TXG 至少要刷新的 metaslab 数量。

### **zfs_metaslab_fragmentation_threshold** = **77**% (uint)

当 metaslab 的碎片率不超过此值时，保持其 active 状态。超过阈值的 active metaslab 将失去 active 状态，以便选择更优的 metaslab。

### **zfs_mg_fragmentation_threshold** = **95**% (uint)

当 metaslab group 的碎片率（百分比）小于或等于此值时，认为其可用于分配。如果 metaslab group 超过该阈值，则会被跳过，除非同一 metaslab class 内的所有 metaslab group 也都超过该阈值。

### **zfs_mg_noalloc_threshold** = **0**% (uint)

定义 metaslab 组可分配空间的阈值。该值以空闲空间的百分比表示，超过此百分比的 metaslab 组始终可进行分配。如果 metaslab 组的空闲空间小于或等于该阈值，分配器将避免向该组分配，除非池中所有组都已达到该阈值。一旦所有组都达到阈值，所有组均允许接受分配。默认值 **0** 禁用该功能，使所有 metaslab 组都可分配。

此参数适用于处理 vdev 不平衡的池，例如添加新 vdev 后的情况。将阈值设置为非零百分比可以阻止向未填充到指定百分比的 vdev 分配，并允许填充较少的 vdev 获取比旧 **zfs_mg_alloc_failures** 功能下更多的分配。

### **zfs_ddt_data_is_special** = **1** | 0 (int)

启用时，ZFS 会将 DDT 数据放入 special 分配类。

### **zfs_user_indirect_is_special** = **1** | 0 (int)

启用时，ZFS 会将用户数据的 indirect block 放入 special 分配类。

### **zfs_multihost_history** = **0** (uint)

保留最近指定数量的多主机更新历史统计，可在 `/proc/spl/kstat/zfs/⟨pool⟩/multihost` 查看。

### **zfs_multihost_interval** = **1000**ms (1 s) (u64)

控制在 **multihost** 属性启用时多主机写入的频率，也是导入期间活动检查长度的参考因素之一。多主机写入周期为 **zfs_multihost_interval** ÷ **leaf-vdevs**。平均而言，每个 leaf vdev 每 **zfs_multihost_interval** 毫秒会执行一次多主机写入。实际观察到的周期可能随 I/O 负载变化，并且该延迟值会存储在 uberblock 中。

### **zfs_multihost_import_intervals** = **20** (uint)

用于控制导入时活动测试的持续时间。较小的 **zfs_multihost_import_intervals** 值会缩短导入时间，但增加无法检测到活动池的风险。总活动检查时间不得低于一秒。

导入时，活动检查的最短等待时间由 **zfs_multihost_interval × zfs_multihost_import_intervals** 决定，或者由最后导入该池的主机计算的同一乘积决定，以较大者为准。如果最佳 uberblock 中的 MMP 延迟值显示实际多主机更新发生间隔长于 **zfs_multihost_interval**，则活动检查时间可能进一步延长。最小值为 *100 ms*。

**0** 等同于 **1**。

### **zfs_multihost_fail_intervals** = **10** (uint)

控制在检测到多主机写入失败或延迟时池的行为。

当 **0** 时，多主机写入失败或延迟将被忽略。失败仍会报告给 ZED，ZED 根据其配置可能会采取操作，例如挂起池或将设备下线。

否则，如果在 **zfs_multihost_fail_intervals × zfs_multihost_interval** 毫秒内没有成功的 MMP 写入，池将被挂起。这保证了在池被导入时活动测试能检测到 MMP 写入。**1** 等同于 **2**；这是为了防止因正常的小幅 I/O 延迟波动而挂起池。

### **zfs_no_scrub_io** = **0** | 1 (int)

设置为 1 可禁用 scrub I/O。此时 scrub 操作仅进行元数据扫描，而不实际检查或修复数据。

### **zfs_no_scrub_prefetch** = **0** | 1 (int)

设置为 1 可禁用 scrub 操作的块预取。

### **zfs_nocacheflush** = **0** | 1 (int)

禁用写入时对磁盘的缓存刷新操作。如果启用易失的乱序写缓存，设置此项可能在断电时导致池损坏。

### **zfs_nopwrite_enabled** = **1** | 0 (int)

允许执行无操作写入（nopwrite）。nopwrite 的实际发生还取决于其他池属性，例如校验和和压缩算法。

### **zfs_dmu_offset_next_sync** = **1** | 0 (int)

启用强制 TXG 同步以发现文件空洞。启用时，使用 **SEEK_HOLE** 或 **SEEK_DATA** 标志可以准确报告文件中的空洞；禁用时，最近修改的文件中的空洞不会被报告。

### **zfs_pd_bytes_max** = **52428800** B (50 MiB) (int)

在池遍历（如 `zfs send` 或其他数据扫描操作）期间应预取的字节数。

### **zfs_traverse_indirect_prefetch_limit** = **32** (uint)

在池遍历（如 `zfs send` 或其他数据扫描操作）期间，应预取的间接块（非 L0 块）指向的块数量。

### **zfs_per_txg_dirty_frees_percent** = **30**% (u64)

控制每个 TXG 中允许的脏间接块释放百分比。超过该阈值后，额外的释放操作将等待到下一个 TXG。**0** 表示禁用此限流。

### **zfs_prefetch_disable** = **0** | 1 (int)

禁用预测性预取。注意，它不会影响“先见”预取（例如用于 `zfs send`），因为先见预取从不执行无用 I/O，不会影响性能。

### **zfs_qat_checksum_disable** = **0** | 1 (int)

禁用 QAT 硬件加速的 SHA256 校验和。只要支持已编译且 QAT 驱动存在，ZFS 模块加载后可取消此设置以初始化 QAT 硬件。

### **zfs_qat_compress_disable** = **0** | 1 (int)

禁用 QAT 硬件加速的 gzip 压缩。同样，在支持编译且 QAT 驱动存在的情况下，可在 ZFS 模块加载后取消此设置以初始化 QAT 硬件。

### **zfs_qat_encrypt_disable** = **0** | 1 (int)

禁用 QAT 硬件加速的 AES-GCM 加密。只要支持已编译且 QAT 驱动存在，ZFS 模块加载后可取消此设置以初始化 QAT 硬件。

### **zfs_vnops_read_chunk_size** = **33554432** B (32 MiB) (u64)

每次读取操作的块大小（以字节为单位）。

### **zfs_read_history** = **0** (uint)

保留最近指定数量的读取操作历史统计，可在 `/proc/spl/kstat/zfs/⟨pool⟩/reads` 查看。

### **zfs_read_history_hits** = **0** | 1 (int)

在读取历史中是否包含缓存命中。

### **zfs_rebuild_max_segment** = **1048576** B (1 MiB) (u64)

在顺序重建（resilver）顶级 vdev 时，单次最大读取段大小。

### **zfs_rebuild_scrub_enabled** = **1** | 0 (int)

顺序重建完成后，自动启动池 scrub 以验证已重建块的校验和。默认启用，强烈推荐保持开启。

### **zfs_rebuild_vdev_limit** = **67108864** B (64 MiB) (u64)

顺序重建每个叶设备允许的最大并发 I/O 总量（以字节为单位）。

### **zfs_reconstruct_indirect_combinations_max** = **4096** (int)

如果间接拆分块在重建时可能的唯一组合超过此数量，则认为计算代价过高，不会全部检查。每次访问块时，最多随机尝试该数量的组合，以确保各段副本公平参与重建，并避免重复使用错误副本。

### **zfs_recover** = **0** | 1 (int)

尝试从致命错误中恢复。仅在万不得已时使用，因为通常会导致空间泄漏或更严重的问题。

### **zfs_removal_ignore_errors** = **0** | 1 (int)

在设备移除过程中忽略严重 I/O 错误。启用后，即使设备在移除时遇到硬件 I/O 错误，移除操作也不会取消。这可能导致原本可恢复的数据块永久损坏，因此不推荐使用，仅在无法在移除设备前将池恢复到健康状态时作为最后手段。

### **zfs_removal_suspend_progress** = **0** | 1 (uint)

供测试套件使用，用于确保在设备移除过程中某些操作能够在特定中间状态发生。

### **zfs_remove_max_segment** = **16777216** B (16 MiB) (uint)

移除设备时尝试分配的最大连续段大小。如果大块分配影响性能，可考虑减小该值。默认值也是允许的最大值。

### **zfs_resilver_disable_defer** = **0** | 1 (int)

忽略 **resilver_defer** 功能，使本应延迟的重建操作立即启动当前正在进行的重建。

### **zfs_resilver_defer_percent** = **10** % (uint)

如果当前重建进度低于该阈值，即使启用了 **resilver_defer** 功能，新重建也会从头开始，而不是等待当前重建完成后再延迟。

### **zfs_resilver_min_time_ms** = **1500** ms (uint)

重建操作由同步线程处理。在重建期间，每个 TXG 刷新之间至少花费此时间处理重建任务。

### **zfs_scan_ignore_errors** = **0** | 1 (int)

启用后，即使池扫描（scrub）中存在无法修复的错误，也会在完成后清除 DTL（dirty time list）。用于池修复或恢复，以便下次导入时停止重建。

### **zfs_scrub_after_expand** = **1** | 0 (int)

RAIDZ 扩展完成后自动启动池 scrub，以验证扩展过程中复制的所有块的校验和。默认启用，强烈推荐保持开启。

### **zfs_scrub_min_time_ms** = **750** ms (uint)

scrub 操作由同步线程处理。每个 TXG 刷新之间至少花费此时间处理 scrub 任务。

### **zfs_scrub_error_blocks_per_txg** = **4096** (uint)

每个 TXG 中待 scrub 的错误块数量。

### **zfs_scan_checkpoint_intval** = **7200** s (2 小时) (uint)

为了在重启后保留进度，顺序扫描算法会定期停止元数据扫描，并将所有验证 I/O 写入磁盘。此刷新频率由该参数控制。

### **zfs_scan_fill_weight** = **3** (uint)

该参数影响 scrub 和 resilver 操作中 I/O 段的调度顺序。数值越大表示更重视段内填充密度，数值越小表示更关注范围大小而不考虑段内空隙。该值仅在模块加载时可调，加载后修改不会影响 scrub 或 resilver 性能。

### **zfs_scan_issue_strategy** = **0** (uint)

确定 scrub 或 resilver 时验证数据的顺序。

#### **1**

  尽可能按顺序验证数据，受为 scrub 保留的内存量限制（参见 **zfs_scan_mem_lim_fact**）。如果池中数据非常碎片化，这种方式可能提高 scrub 性能。

#### **2**

  优先验证找到的最大几乎连续的数据块。通过延迟处理小段数据，后续可能找到相邻数据合并，从而增大段大小。

#### **0**

  在普通验证时使用策略 **1**，在执行 checkpoint 时使用策略 **2**。

### **zfs_scan_legacy** = **0** | 1 (int)

未设置时，scrub 和 resilver 会先在内存中收集元数据，再发起顺序 I/O。设置时使用传统算法，即发现 I/O 即刻执行。对已在进行中的 scrub 或 resilver 无影响。

### **zfs_scan_max_ext_gap** = **2097152** B (2 MiB) (int)

设置 scrub/resilver I/O 操作间仍被视为顺序的最大字节间隙。改变此值不会影响已进行中的操作。

### **zfs_scan_mem_lim_fact** = **20**^-1 (uint)

顺序扫描算法用于 I/O 排序的最大内存比例。达到此硬限制时，会停止扫描元数据并开始数据验证 I/O，直到低于软限制为止。

### **zfs_scan_mem_lim_soft_fact** = **20**^-1 (uint)

由顺序扫描算法确定 I/O 排序软限制的硬限制比例。当从下方越过此限制时，不会采取任何操作。当从上方越过此限制时，说明我们正在发出验证 I/O。在这种情况下（除非元数据扫描已完成），我们会停止发出验证 I/O，并重新开始扫描元数据，直到达到硬限制。

### **zfs_scan_report_txgs** = **0** | 1 (uint)

在报告 resilver 吞吐量和预计完成时间时，使用大约最近 **zfs_scan_report_txgs** 个 TXG 的性能数据。当设置为 `0` 时，性能将根据检查点之间的时间计算。


### **zfs_scan_strict_mem_lim** = **0** | 1 (int)

顺序扫描进行时，是否严格限制池扫描的内存使用。禁用时，高速磁盘可能会超出限制。

### **zfs_scan_suspend_progress** = **0** | 1 (int)

冻结正在进行的 scrub/resilver，但实际上不暂停。用于测试或调试。

### **zfs_scan_vdev_limit** = **16777216** B (16 MiB) (int)

每个叶子设备在 scrub 和 resilver 中一次性可发起的最大并发数据量（字节）。

### **zfs_send_corrupt_data** = **0** | 1 (int)

允许发送损坏数据（发送时忽略读取/校验错误）。

### **zfs_send_unmodified_spill_blocks** = **1** | 0 (int)

在发送流中包含未修改的 spill 块。在某些情况下，旧版本的 ZFS 可能会错误地从现有对象中移除 spill 块。包含未修改的 spill 块副本可生成向后兼容的发送流，在 spill 块被错误移除时重新创建它。


### **zfs_send_no_prefetch_queue_ff** = **20**^-1 (uint)

`zfs send` 内部队列的填充比例，用于控制内部线程唤醒的时机。

### **zfs_send_no_prefetch_queue_length** = **1048576** B (1 MiB) (uint)

`zfs send` 内部队列允许的最大字节数。

### **zfs_send_queue_ff** = **20**^-1 (uint)

`zfs send` 预取队列的填充比例，用于控制内部线程唤醒的时机。

### **zfs_send_queue_length** = **16777216** B (16 MiB) (uint)

`zfs send` 可预取的最大字节数。此值必须至少为使用的最大块大小的两倍。

### **zfs_recv_queue_ff** = **20**^-1 (uint)

`zfs receive` 队列的填充比例，用于控制内部线程唤醒的时机。

### **zfs_recv_queue_length** = **16777216** B (16 MiB) (uint)

`zfs receive` 队列允许的最大字节数。此值必须至少为使用的最大块大小的两倍。

### **zfs_recv_write_batch_size** = **1048576** B (1 MiB) (uint)

`zfs receive` 在一次 DMU 事务中写入的最大数据量（以字节为单位）。即使接收的是压缩发送流，此值也指未压缩大小。该设置不会将写入大小降低到单个块以下，最大限制为 **32 MiB**。


### **zfs_recv_best_effort_corrective** = **0** (int)

当此变量设置为非零时，修复性接收（corrective receive）将：

1. 不强制要求源快照和目标快照的 GUID 匹配。
2. 如果在修复过程中发生错误，接收不会终止，而是继续处理下一个记录。


### **zfs_override_estimate_recordsize** = **0** | 1 (uint)

设置此变量会覆盖执行 `zfs send` 时用于估算块大小的默认逻辑。默认启发式方法是假定平均块大小为当前的 recordsize。如果数据集中大多数数据的大小与此不同，并且你需要准确的 zfs send 大小估算，则应覆盖此值。

### **zfs_sync_pass_deferred_free** = **2** (uint)

数据刷新到磁盘按多个 pass 执行。从此 pass 开始延迟释放空间。

### **zfs_spa_discard_memory_limit** = **16777216** B (16 MiB) (int)

在丢弃 checkpoint 时，每个 vdev 为预取 checkpoint 空间映射可使用的最大内存。

### **zfs_spa_note_txg_time** = **600** (uint)

此参数以秒为单位定义 TXG 时间数据库记录新 TXG 的频率（仅在 TXG 发生变化时）。在指定时间间隔过去后，如果 TXG 号已变化，数据库将记录新的值。这些时间戳可用于更精细的操作，例如 scrub。


### **zfs_spa_flush_txg_time** = **600** (uint)

此参数以秒为单位定义 ZFS 刷新 TXG 时间数据库到磁盘的频率。它确保数据实际写入持久存储，有助于在意外关机时保护数据库。导出操作过程中，数据库也会自动刷新。

### **zfs_special_class_metadata_reserve_pct** = **25**% (uint)

仅当特殊（special）和去重（dedup）vdev 上的可用空闲空间百分比超过此值时，才允许在这些 vdev 上分配小数据块。这可确保当特殊 vdev 接近容量时，池元数据仍有保留空间可用。

### **zfs_sync_pass_dont_compress** = **8** (uint)

从该 sync pass 开始禁用压缩（包括元数据压缩）。在默认设置下，实际上我们没有这么多 sync pass，因此此设置无效。

最初的意图是禁用压缩有助于 sync pass 收敛。然而实际上，禁用压缩会增加平均 sync pass 的数量；因为关闭压缩后，许多块的大小会发生变化，因此必须重新分配（而不是覆盖）这些块。同时，它也会增加 *128 KiB* 分配的数量（例如用于间接块和空间映射），因为这些块不会被压缩。*128 KiB* 分配在高度碎片化的系统上尤其影响性能，因为这类系统可能几乎没有足够大小的空闲段，并可能需要加载新的 metaslab 来满足这些分配。

### **zfs_sync_pass_rewrite** = **2** (uint)

从此 sync pass 开始重写新块指针。

### **zfs_trim_extent_bytes_max** = **134217728** B (128 MiB) (uint)

TRIM 命令的最大范围。超过此大小的范围将被拆分为不大于此值的块后再发出。

### **zfs_trim_extent_bytes_min** = **32768** B (32 KiB) (uint)

TRIM 命令的最小大小。小于此范围的 TRIM 将被跳过，除非它们属于被拆分的大范围 TRIM。之所以这样做，是因为这些小 TRIM 通常会对整体性能产生负面影响。

### **zfs_trim_metaslab_skip** = **0** | 1 (uint)

在 TRIM 过程中跳过未初始化的 metaslab。此选项对由大容量精简配置设备构成的池特别有用，因为 TRIM 操作较慢。随着池的使用，池中越来越多的 metaslab 会被初始化，该选项的效果会逐渐降低。此设置在启动手动 TRIM 时保存，并在整个请求的 TRIM 过程中保持有效。

### **zfs_trim_queue_limit** = **10** (uint)

每个叶子 vdev 最大排队 TRIM 命令数。设备上并发 TRIM 命令数量由 **zfs_vdev_trim_min_active** 和 **zfs_vdev_trim_max_active** 控制。

### **zfs_trim_txg_batch** = **32** (uint)

在向设备发出 TRIM 操作之前，应聚合的事务组（transaction groups）数量的 frees。此设置在发出更大、更高效的 TRIM 操作与最近释放空间可供设备使用之间存在权衡。

增加此值将允许 frees 聚合更长时间，从而产生更大的 TRIM 操作，并可能增加内存使用量。减少此值则会产生相反效果。默认值 **32** 被认为是一个合理的折中选择。

### **zfs_txg_history** = **100** (uint)

/ proc / spl / kstat / zfs / ⟨pool⟩/TXGs 中可查看最近 **100** 个 TXG 的历史统计信息。

### **zfs_txg_timeout** = **5** s (uint)

最少每隔该时间将脏数据刷新到磁盘（TXG 的最大持续时间）。

### **zfs_vdev_aggregation_limit** = **1048576** B (1 MiB) (uint)

vdev I/O 最大聚合大小。

### **zfs_vdev_aggregation_limit_non_rotating** = **131072** B (128 KiB) (uint)

非轮替介质 vdev 的最大 I/O 聚合大小。

### **zfs_vdev_mirror_rotating_inc** = **0** (int)

负载均衡算法用于轮替 vdev 时选择最空闲镜像成员的增量值。当 I/O 紧跟前一个操作时，用于基于负载做决策。

### **zfs_vdev_mirror_rotating_seek_inc** = **5** (int)

负载均衡算法用于轮替 vdev 时选择最空闲镜像成员的增量值。当 I/O 不具备前一个操作的局部性（由 **zfs_vdev_mirror_rotating_seek_offset** 定义）时使用。位于此偏移范围内但不紧跟前一操作的 I/O 增量取一半。

### **zfs_vdev_mirror_rotating_seek_offset** = **1048576** B (1 MiB) (int)

轮替 vdev 上最后排队的 I/O 操作被视为具备局部性的最大距离。详见 ZFS I/O 调度器。

### **zfs_vdev_mirror_non_rotating_inc** = **0** (int)

非轮替 vdev 上，当 I/O 操作不紧跟前一操作时，负载均衡算法选择最空闲镜像成员时的负载增量值。

### **zfs_vdev_mirror_non_rotating_seek_inc** = **1** (int)

非轮替 vdev 上，当 I/O 操作不具备由 **zfs_vdev_mirror_rotating_seek_offset** 定义的局部性时，负载均衡算法选择最空闲镜像成员的负载增量值。位于此偏移范围内但不紧跟前一操作的 I/O 增量取一半。

### **zfs_vdev_read_gap_limit** = **32768** B (32 KiB) (uint)

如果磁盘上读 I/O 操作之间的间隔小于该阈值，则对这些操作进行聚合。

### **zfs_vdev_write_gap_limit** = **4096** B (4 KiB) (uint)

如果磁盘上写 I/O 操作之间的间隔小于该阈值，则对这些操作进行聚合。

### **zfs_vdev_raidz_impl** = **fastest** (string)

选择要使用的 raidz 校验实现。

不依赖于特定 CPU 特性的变体可在模块加载时选择，因为它们在所有系统上均受支持。其余选项只能在模块加载后设置，因为它们仅在已编译并且在运行系统上受支持的情况下可用。

在模块加载后，`/sys/module/zfs/parameters/zfs_vdev_raidz_impl` 将显示可用选项，当前选择的实现会用方括号括起。


| **选项**              | **说明**                 |                      |
| :------------------- | :---------------------- | :-------------------- |
| **fastest**         | 内置基准测试选择最快实现           |                      |
| **original**        | 原始实现                   |                      |
| **scalar**          | 标量实现                   |                      |
| **sse2**            | SSE2 指令集               | 64 位 x86           |
| **ssse3**           | SSSE3 指令集              | 64 位 x86           |
| **avx2**            | AVX2 指令集               | 64 位 x86           |
| **avx512f**         | AVX512F 指令集            | 64 位 x86           |
| **avx512bw**        | AVX512F & AVX512BW 指令集 | 64 位 x86           |
| **aarch64_neon**    | NEON                   | Aarch64/64 位 ARMv8 |
| **aarch64_neonx2**  | NEON 更高展开版本            | Aarch64/64 位 ARMv8 |
| **powerpc_altivec** | Altivec                | PowerPC              |

### **zfs_zevent_len_max** = **512** (uint)

事件队列最大长度。可用 zpool-events(8) 查看队列中的事件。

### **zfs_zevent_retain_max** = **2000** (int)

保留最近 zevent 记录以进行重复检查的最大数量。设置为 **0** 将禁用重复检测。

### **zfs_zevent_retain_expire_secs** = **900** 秒 (15 分钟) (int)

为重复检查保留的最近 ereport 的有效期。

### **zfs_zil_clean_taskq_maxalloc** = **1048576** (int)

允许缓存的最大 taskq 条目数。超过此限制时，事务记录 (itxs) 将同步清理。

### **zfs_zil_clean_taskq_minalloc** = **1024** (int)

taskq 创建时预填充的条目数，创建后可立即使用。

### **zfs_zil_clean_taskq_nthr_pct** = **100%** (int)

控制 **dp_zil_clean_taskq** 使用的线程数。默认 **100%** 将为每个 CPU 创建最多一个线程。

### **zil_maxblocksize** = **131072**B (128 KiB) (uint)

设置 ZIL 使用的最大块大小。在高度碎片化的池中，将其降低（通常为 **36 KiB**）可以改善性能。

### **zil_maxcopied** = **7680**B (7.5 KiB) (uint)

通过 WR_COPIED 记录的最大写入字节数。此参数在额外内存拷贝与日志空间效率之间做权衡，同时影响范围锁/解锁操作的次数。

### **zil_nocacheflush** = **0**|1 (int)

禁用 ZIL 在 LWB 写完成后发送到磁盘的缓存刷新命令。若启用且存在易失性乱序写缓存，会导致 ZIL 在断电时损坏。

### **zil_replay_disable** = **0**|1 (int)

禁用 intent log 重放。可在恢复损坏的 ZIL 时禁用。

### **zil_slog_bulk** = **67108864**B (64 MiB) (u64)

限制同步优先级提交时每次 SLOG 写入大小。超出部分将以异步优先级执行，防止单个活跃 ZIL 写入者滥用 SLOG 设备。

### **zfs_zil_saxattr** = **1**|0 (int)

将此可调参数设置为 `0` 会在池启用 **org.openzfs:zilsaxattr** 功能时，禁用对新 **xattr**=**sa** 记录的 ZIL 日志。这通常仅在需要规避该记录类型的 ZIL 日志或重放代码中的错误时才有必要。如果该功能未启用，则此可调参数不起作用。

### **zfs_embedded_slog_min_ms** = **64** (uint)

通常，每个普通和特殊类 vdev 的一个 metaslab 会专门用于 ZIL 记录同步写入。然而，如果 vdev 中的 metaslab 数量少于 **zfs_embedded_slog_min_ms**，则禁用此功能。这可确保不会为 ZIL 留出不合理的空间。

### **zstd_earlyabort_pass** = **1** (uint)

启用使用 LZ4 和 zstd-1 pass 对 zstd 等级 ≥3 的不可压缩数据的早期终止启发式检测。

### **zstd_abort_size** = **131072** (uint)

早期终止启发式检测尝试的最小未压缩记录大小（含边界）。

### **zio_deadman_log_all** = **0**|1 (int)

如果非零，zio deadman 将为所有 zio 生成调试消息（参见 **zfs_dbgmsg_enable**），而不仅仅是拥有 vdev 的叶子 zio。此选项供开发者使用，用于获取不涉及互斥锁或其他锁原语的挂起情况的诊断信息：通常是 zio 流水线中的线程无限循环的情况。

### **zio_slow_io_ms** = **30000**ms (30 s) (int)

当 I/O 操作耗时超过该阈值时，将被标记为慢操作。每次慢操作都会触发延迟 zevent。慢 I/O 计数可通过 `zpool status -s` 查看。

### **zio_dva_throttle_enabled** = **1**|0 (int)

在 I/O 管道中限制块分配。这使得分配可以根据设备性能动态分配。

### **zfs_xattr_compat** = 0|1 (int)

控制在用户命名空间中设置新 xattr 时使用的命名方案。如果为 **0**（Linux 默认值），用户命名空间的 xattr 名称会加上命名空间前缀，以向后兼容以前版本的 Linux ZFS。如果为 **1**（FreeBSD 默认值），用户命名空间的 xattr 名称不加前缀，以向后兼容以前版本的 illumos 和 FreeBSD ZFS。

无论此可调参数如何设置，本版本及未来版本的 ZFS 都可以读取任一命名方案，但旧版 illumos 或 FreeBSD ZFS 无法读取 Linux 格式写入的用户命名空间 xattr，而旧版 Linux ZFS 无法读取旧 ZFS 格式写入的用户命名空间 xattr。

当覆盖 xattr 时，如果存在另一种命名方案的同名 xattr，会将其删除以避免重复累积。

### **zio_requeue_io_start_cut_in_line** = **0**|1 (int)

优先处理重新排队的 I/O。

### **zfs_delete_inode** = **0**|1 (int)

设置内核在最后一个引用释放后是释放 inode 结构，还是将其缓存于内存中。用于测试/调试。

活跃的 inode 结构会“固定”多个内部 OpenZFS 结构在内存中，这可能导致在拥有大量不常访问文件的系统上出现大量“不可用”内存，直到内核的内存压力机制要求 OpenZFS 释放这些结构。

默认值 **0** 始终缓存仍在磁盘上存在的 inode。设置为 **1** 将立即释放未使用的 inode 及其关联内存回 dbuf 缓存或 ARC 以供重用，但如果 inode 被频繁逐出并重新加载，可能会降低性能。

此参数仅在 Linux 上可用。


### **zfs_delete_dentry** = **0**|1 (int)

设置内核在不再需要 dentry 结构时是释放它，还是将其保存在 dentry 缓存中。用于测试/调试。由于 dentry 结构持有 inode 引用，缓存的 dentry 可能会无限期“固定” inode 在内存中，以及相关的 OpenZFS 结构（参见 **zfs_delete_inode**）。

默认值 **0** 指示内核在条目及其关联的 inode 不再被直接引用时仍进行缓存，并通过内核的正常缓存管理过程回收它们。设置为 **1** 将指示内核在文件系统不再引用目录条目时立即释放这些条目及其 inode。

此参数仅在 Linux 上可用。


### zio_taskq_batch_pct = 80 (uint)

运行 I/O 工作线程的在线 CPU 百分比。这些工作线程负责处理 I/O 相关任务，如压缩、加密、校验和和奇偶校验计算。小数部分的 CPU 数量将向下取整。

默认值为 **80%**，选择此值是为了避免占用全部 CPU，从而导致延迟问题和应用性能不稳定，尤其在启用较慢的压缩和/或校验计算时。设置的值仅适用于之后导入或创建的池。

### zio_taskq_batch_tpq = 0 (uint)

每个 taskq 的工作线程数。较高的值可提升 I/O 排序和 CPU 利用率，而较低的值可减少锁争用。设置的值仅适用于之后导入或创建的池。如果为 **0**，则生成接近每个 taskq 6 个线程的系统依赖值。

### zio_taskq_write_tpq = 16 (uint)

确定每个写入 issue taskq 的最小线程数。较高的值可在高吞吐量下提升 CPU 利用率，而较低的值可在高 IOPS 下减少 taskq 锁争用。设置的值仅适用于之后导入或创建的池。

### zio_taskq_read = fixed,1,8 null scale null (charp)

设置 IO 读队列的队列和线程配置。这是一个高级调试参数。除非你了解其作用，否则不要更改。四个值分别对应 issue、issue 高优先级、interrupt 和 interrupt 高优先级队列。有效值为 **fixed,N,M**（M 个队列，每个队列 N 个线程）、**scale[,MIN]**（随 CPU 数量缩放，总线程数至少为 MIN）、**sync** 和 **null**。设置的值仅适用于之后导入或创建的池。

### zio_taskq_write = sync null scale null (charp)

设置 IO 写队列的队列和线程配置。这是一个高级调试参数。除非你了解其作用，否则不要更改。四个值分别对应 issue、issue 高优先级、interrupt 和 interrupt 高优先级队列。有效值为 **fixed,N,M**（M 个队列，每个队列 N 个线程）、**scale[,MIN]**（随 CPU 数量缩放，总线程数至少为 MIN）、**sync** 和 **null**。设置的值仅适用于之后导入或创建的池。


### zio_taskq_free = scale,32 null null null (charp)

设置 IO free 队列的队列和线程配置。这是一个高级调试参数。除非你了解其作用，否则不要更改。四个值分别对应 issue、issue 高优先级、interrupt 和 interrupt 高优先级队列。有效值为 **fixed,N,M**（M 个队列，每个队列 N 个线程）、**scale[,MIN]**（随 CPU 数量缩放，总线程数至少为 MIN）、**sync** 和 **null**。默认情况下使用至少 32 个线程，以提高 frees 过程中 DDT 和 BRT 元数据操作的并行性。设置的值仅适用于之后导入或创建的池。


### zvol_inhibit_dev = 0|1 (uint)

不创建 zvol 设备节点。在拥有大量 zvol 的系统上，这可能略微提高启动速度。

### zvol_major = 230 (uint)

zvol 块设备的主设备号。

### zvol_max_discard_blocks = 16384 (long)

对 zvol 执行的丢弃（TRIM）操作将按此数量的块分批进行，其中块大小由 zvol 的 **volblocksize** 属性决定。


### zvol_prefetch_bytes = 131072B (128 KiB) (uint)

向系统添加 zvol 时，从卷的起始和末尾预取此数量的字节。预取卷的这些区域是有益的，因为它们很可能会被 blkid(8) 和内核分区程序立即访问。


### zvol_request_sync = 0|1 (uint)

在处理 zvol 的 I/O 请求时，以同步方式提交。这实际上将每个 I/O 提交者的队列深度限制为 *1*。如果未设置，请求将由线程池异步处理。可并发处理的请求数量由 **zvol_threads** 控制。在支持块多队列（`blk-mq`）的内核上，**zvol_request_sync** 会被忽略。

### zvol_num_taskqs = 0 (uint)

zvol 任务队列的数量。如果设置为 **0**（默认），则内部按比例调整，优先为每个任务队列分配 6 个线程。此设置仅适用于 Linux。


### zvol_threads = 0 (uint)

用于处理 zvol 块 I/O 的系统级线程数。如果设置为 **0**（默认），则内部将 **zvol_threads** 设置为系统中 CPU 的数量或 32（取较大者）。

### zvol_blk_mq_threads = 0 (uint)

每个 zvol 用于排队 I/O 请求的线程数。此参数仅在内核支持 `blk-mq` 时出现，并且仅在 zvol 加载时读取和赋值。如果设置为 **0**（默认），则内部将 **zvol_blk_mq_threads** 设置为系统中 CPU 的数量。


### zvol_use_blk_mq = 0|1 (uint)

设置为 **1** 以对 zvol 使用 `blk-mq` API。设置为 **0**（默认）以使用传统的 zvol API。根据工作负载，此设置可能提升或降低 zvol 性能。此参数仅在内核支持 `blk-mq` 时出现，并且仅在 zvol 加载时读取和赋值。


### zvol_blk_mq_blocks_per_thread = 8 (uint)

如果启用 **zvol_use_blk_mq**，则每个 zvol 线程将处理此数量的 **volblocksize** 大小的块。该调节参数可用于优化 zvol 读性能（较小值）或写性能（较大值）。如果设为 **0**，则 zvol 层将处理每个线程所能处理的最大块数。此参数仅在内核支持 `blk-mq` 时出现，并且仅在每个 zvol 加载时生效。


### zvol_blk_mq_queue_depth = 0 (uint)

zvol `blk-mq` 接口的队列深度（queue_depth）值。只有在内核支持 `blk-mq` 时此参数才会出现，并且仅在每个 zvol 加载时生效。如果设为 **0**（默认值），则使用内核的默认队列深度。设定值会被限制在内核的 `BLKDEV_MIN_RQ` 和 `BLKDEV_MAX_RQ`/`BLKDEV_DEFAULT_RQ` 范围内。

### zvol_volmode = 1 (uint)

定义 zvol 块设备在 volmode=default 时的行为：

#### 1

等同于 full

#### 2

等同于 dev

#### 3

等同于 none

### zvol_enforce_quotas = 0|1 (uint)

启用严格的 ZVOL 配额执行。严格配额执行可能会影响性能。

## ZFS I/O 调度器

ZFS 向叶子 vdev 发出 I/O 操作以满足并完成 I/O 请求。调度器负责决定这些操作的发出时机和顺序。调度器将操作分为五类 I/O 队列，优先级顺序如下：同步读取、同步写入、异步读取、异步写入，以及 scrub/resilver。每个队列定义了可向设备发出的并发操作的最小值和最大值。此外，设备还具有一个总的并发最大值，即 **zfs_vdev_max_active**。需要注意的是，各队列最小值之和不能超过总最大值。如果各队列最大值之和超过总最大值，则活动操作数可能达到 **zfs_vdev_max_active**，此时无论各队列最小值是否已满足，都不会再发出新的操作。


对于许多物理设备，吞吐量会随着并发操作数量的增加而提升，但延迟通常会变高。此外，物理设备通常存在一个阈值，超过该阈值更多的并发操作对吞吐量没有效果，甚至可能导致吞吐量下降。

调度器选择下一个要执行的操作时，首先查找未达到最小操作数的 I/O 类。一旦所有最小值都满足且总并发最大值尚未达到，调度器再查找未达到最大操作数的 I/O 类。对 I/O 类的迭代按照上述顺序进行。如果总并发最大值已达到，或某个 I/O 类没有排队操作且其最大值已达到，则不再发出操作。每当有新的 I/O 操作入队或某操作完成时，调度器会重新查找可发出的新操作。

一般而言，较小的 **max_active** 会降低同步操作的延迟。较大的 **max_active** 则可能提高整体吞吐量，这取决于底层存储设备。

各队列 **max_active** 的比值决定了读、写和 scrub 操作的性能平衡。例如，增加 **zfs_vdev_scrub_max_active** 会让 scrub 或 resilver 更快完成，但会导致读写操作延迟增加、吞吐量下降。


除了异步写类之外，所有 I/O 类都有固定的最大未完成操作数。异步写代表事务组在同步阶段提交到稳定存储的数据。事务组会定期进入同步状态，因此排队的异步写操作数量会迅速激增，然后逐渐降至零。I/O 调度器不会尽可能快地处理它们，而是根据池中脏数据的数量调整最大活跃异步写操作数。由于向物理设备发出的并发操作数量增加通常会提升吞吐量和延迟，降低同时操作数量的突发性还能稳定其他队列操作的响应时间，尤其是同步队列。大体而言，I/O 调度器会随着池中脏数据增加而增加从异步写队列发出的并发操作数。


### 异步写入

异步写 I/O 类发出的并发操作数量遵循一个分段线性函数，该函数由若干可调节点定义：

```sh
       |              o---------| <-- zfs_vdev_async_write_max_active
  ^    |             /^         |
  |    |            / |         |
active |           /  |         |
 I/O   |          /   |         |
count  |         /    |         |
       |        /     |         |
       |-------o      |         | <-- zfs_vdev_async_write_min_active
      0|_______^______|_________|
       0%      |      |       100% of zfs_dirty_data_max
               |      |
               |      `-- zfs_vdev_async_write_active_max_dirty_percent
               `--------- zfs_vdev_async_write_active_min_dirty_percent
```

在池中允许的脏数据量超过最小百分比之前，I/O 调度器会将并发操作数量限制在最小值。超过该阈值后，发出的并发操作数量会线性增加，到达池中允许的脏数据量的最大百分比时达到最大值。

理想情况下，繁忙池中的脏数据量应保持在 **zfs_vdev_async_write_active_min_dirty_percent** 与 **zfs_vdev_async_write_active_max_dirty_percent** 之间的斜率部分。如果超过最大百分比，则表明进入的数据速率高于后端存储能够处理的速率。在这种情况下，必须进一步限制写入速率，如下一节所述。


## ZFS 事务延迟

当我们判断后端存储无法跟上写入速率时，会对事务引入延迟。

如果已有事务在等待，我们的延迟是相对于该事务完成等待的时间计算的，这样计算出的延迟时间不会受同时执行事务线程数量的影响。

如果我们是唯一的等待者，则相对于事务开始的时间计算，而非当前时间。这会“抵扣”事务已经花费的时间，例如读取间接块的时间。

事务所需的最短时间计算如下：


```sh
min_time = min(zfs_delay_scale × (dirty - min) / (max - dirty), 100ms)
```

延迟有两个可通过调节参数控制的自由度。开始引入延迟时的脏数据百分比由 **zfs_delay_min_dirty_percent** 决定。通常应设置在 **zfs_vdev_async_write_active_max_dirty_percent** 之上，这样只有在全速写入仍无法跟上写入速率时才开始引入延迟。曲线的幅度由 **zfs_delay_scale** 决定，粗略来说，该变量决定曲线中点处的延迟量。


```sh
延迟
 10ms +-------------------------------------------------------------*+
      |                                                             *|
  9ms +                                                             *+
      |                                                             *|
  8ms +                                                             *+
      |                                                            * |
  7ms +                                                            * +
      |                                                            * |
  6ms +                                                            * +
      |                                                            * |
  5ms +                                                           *  +
      |                                                           *  |
  4ms +                                                           *  +
      |                                                           *  |
  3ms +                                                          *   +
      |                                                          *   |
  2ms +                                              (midpoint) *    +
      |                                                  |    **     |
  1ms +                                                  v ***       +
      |             zfs_delay_scale ---------->     ********         |
    0 +-------------------------------------*********----------------+
      0%                    <- zfs_dirty_data_max ->               100%
```

需要注意的是，由于延迟会加到最近一次事务剩余的未完成时间上，它实际上与 IOPS 成反比。这里，500 微秒的中点相当于 2000 IOPS。曲线的形状被设计为在前四分之三的脏数据积累量发生小幅变化时，产生的延迟差异也相对较小。

当将延迟量用对数刻度表示时，其效果更容易理解：


```sh
延迟
100ms +-------------------------------------------------------------++
      +                                                              +
      |                                                              |
      +                                                             *+
 10ms +                                                             *+
      +                                                           ** +
      |                                              (midpoint)  **  |
      +                                                  |     **    +
  1ms +                                                  v ****      +
      +             zfs_delay_scale ---------->        *****         +
      |                                             ****             |
      +                                          ****                +
100us +                                        **                    +
      +                                       *                      +
      |                                      *                       |
      +                                     *                        +
 10us +                                     *                        +
      +                                                              +
      |                                                              |
      +                                                              +
      +--------------------------------------------------------------+
      0%                    <- zfs_dirty_data_max ->               100%
```

需要注意的是，只有当脏数据量接近其上限时，延迟才会开始快速增加。一个调优良好的系统目标应当是保持脏数据量远离该范围：首先确保为 I/O 调度器设置了合适的限制，以便在后端存储上达到最佳吞吐量；然后通过调整 **zfs_delay_scale** 的值来增加延迟曲线的陡峭程度。


2025 年 9 月 15 日 | Debian

