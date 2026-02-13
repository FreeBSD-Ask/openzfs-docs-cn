# ZFS I/O (ZIO) 调度器

ZFS 向叶子 vdevs（通常为设备）发出 I/O 操作以满足并完成 I/O。由 ZIO 调度器决定这些操作何时以及以何种顺序被发出。操作被划分为九个 I/O 类，优先级按如下顺序排列：

| 优先级 | I/O 类      | 描述                           | I/O 类型 |
| :---: | :------------: | :---------------------------- | :--------: |
| 最高  | sync read    | 大多数读取                        | 交互式      |
|     | sync write   | 由应用程序定义或通过“zfs” “sync”属性定义 | 交互式      |
|     | async read   | 预取读取                         | 交互式      |
| 见下文 | async write  | 大多数写入                        | 交互式      |
|     | scrub read   | 扫描读取：包括 scrub 和 resilver     | 非交互式     |
|     | removal      | vdev 移除重排                    | 非交互式     |
|     | initializing | vdev 空间初始化                   | 非交互式     |
|     | trim         | TRIM / UNMAP 请求              | 交互式      |
| 最低  | rebuild      | 顺序重建                         | 非交互式     |

对于交互式 I/O，每个队列定义了发往设备的并发操作的最小值和最大值。每个设备还遵循一个聚合最大值 —— `zfs_vdev_max_active`。请注意，各队列最小值之和不得超过该聚合最大值。如果各队列最大值之和超过聚合最大值，则活动 I/O 数量可能达到 `zfs_vdev_max_active`，在这种情况下，无论是否已满足所有队列的最小值，都不会再发出新的 I/O。

对于非交互式 I/O（scrub、resilver、removal、initializing 和 rebuild），并发活动 I/O 数量限制为 `zfs_vdev_nia_delay`，除非 vdev 处于“idle”状态。当没有交互式 I/O（sync 或 async）处于活动状态，并且自上次交互式 I/O 以来已完成 `zfs_vdev_nia_delay` 个 I/O 时，vdev 被视为“idle”，此时并发活动的非交互式 I/O 数量将增加到 `zfs_vdev_max_active`。

| I/O 类      | 最小活动参数                             | 最大活动参数                             |
| :------------: | :---------------------------------- | :---------------------------------- |
| sync read    | `zfs_vdev_sync_read_min_active`    | `zfs_vdev_sync_read_max_active`    |
| sync write   | `zfs_vdev_sync_write_min_active`   | `zfs_vdev_sync_write_max_active`   |
| async read   | `zfs_vdev_async_read_min_active`   | `zfs_vdev_async_read_max_active`   |
| async write  | `zfs_vdev_async_write_min_active`  | `zfs_vdev_async_write_max_active`  |
| scrub read   | `zfs_vdev_scrub_min_active`        | `zfs_vdev_scrub_max_active`        |
| removal      | `zfs_vdev_removal_min_active`      | `zfs_vdev_removal_max_active`      |
| initializing | `zfs_vdev_initializing_min_active` | `zfs_vdev_initializing_max_active` |
| trim         | `zfs_vdev_trim_min_active`         | `zfs_vdev_trim_max_active`         |
| rebuild      | `zfs_vdev_rebuild_min_active`      | `zfs_vdev_rebuild_max_active`      |

I/O 队列统计信息包含大多数 I/O 类，可通过命令 `zpool iostat -q` 查看。

对于许多物理设备而言，吞吐量会随着并发操作数量增加而提升，但通常会增加延迟。此外，物理设备通常存在上限，超过该上限后增加并发操作不会提升吞吐量，甚至可能造成磁盘性能下降。

在选择下一个要发出的操作时，ZIO 调度器首先查找其最小值尚未满足的 I/O 类。待全部满足且未达到聚合最大值，调度器会查找其最大值尚未满足的类。按上述优先级进行 I/O 类的遍历顺序。如果已达到聚合最大并发操作数，或对于尚未达到最大值的 I/O 类没有排队操作，则不会发出更多操作。每当有 I/O 被加入队列或某个操作完成时，I/O 调度器都会查找新的可发出操作。

一般而言，较小的 `max_active` 值会降低同步操作的延迟。较大的 `max_active` 值可能会提高整体吞吐量，这取决于底层存储和 I/O 负载搭配。

各队列 max_active 的比率决定了读取、写入和 scrub 之间的性能平衡。例如，在存在争用时，增加 `zfs_vdev_scrub_max_active` 会使 scrub 或 resilver 更快完成，但读取和写入的延迟会增加且吞吐量会降低。

除 async write 类外，所有 I/O 类都有固定的未完成操作最大数量。异步写入表示在事务组同步阶段提交到稳定存储的数据。事务组会周期性进入同步状态，因此排队的 async write 数量会迅速突增，然后降为零。可调参数 `zfs_txg_timeout` （默认值 = 5 秒）设置 txg 同步的目标间隔。因此，每 5 秒一次的 async write 突发是正常的 ZFS I/O 模式。

ZIO 调度器并非尽可能快地处理 I/O，而是根据存储池中的脏数据量动态调整活动 async write I/O 的最大数量。由于向物理设备发出的并发操作数量增加通常会同时提升吞吐量和延迟，减少并发操作数量的突发性也有助于稳定其他队列操作的响应时间。这对于 sync read 和 sync write 队列尤为重要，因为 txg 同步的周期性 async write 突发可能导致设备级争用。概括而言，当存储池中的脏数据增多时，ZIO 调度器会从 async write 队列发出更多并发操作。


