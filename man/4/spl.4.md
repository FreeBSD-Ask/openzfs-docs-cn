# spl(4)


## 名称

`spl` — SPL 内核模块的参数

## 说明

### `spl_kmem_cache_kmem_threads=4`（无符号整数类型 uint）

为 spl_kmem_cache 任务队列创建的线程数量。该任务队列负责为 kmem 缓存分配新的 slabs 以供使用。对于大多数系统和工作负载，仅需少量线程。

### `spl_kmem_cache_obj_per_slab=8`（无符号整数类型 uint）

缓存中每个 slab 的首选对象数量。一般来说，较大的值会增加缓存的内存占用，同时减少执行分配所需的时间。而较小的值可最小化内存占用并改善缓存回收时间，但单次分配可能需要更长时间。

### `spl_kmem_cache_max_size=32`（64 位）或 `spl_kmem_cache_max_size=4`（32 位）（无符号整数类型 uint）

kmem 缓存 slab 的最大大小（MiB）。这实际上将缓存对象的最大大小限制为 **spl_kmem_cache_max_size**/**spl_kmem_cache_obj_per_slab**。

缓存所创建的对象，其最大尺寸受制于此限制。

### `spl_kmem_cache_slab_limit=16384`（无符号整数类型 uint）

对于小对象，应使用 Linux slab 分配器以最有效地利用内存。可是 Linux slab 不支持大对象，因此建议使用 SPL 实现。该值用于确定小对象和大对象的分界点。

体积为 **spl_kmem_cache_slab_limit** 及更小的对象将使用 Linux slab 分配器分配，较大的对象使用 SPL 分配器。对于使用 4K 页的架构，16K 的分界被认为是最优的。

### `spl_kmem_alloc_warn=32768`（无符号整数类型 uint）

一般来说，`kmem_alloc` 的分配应保持较小值，最好只占用几页，因为它们必须在物理上连续。因此，对于任何超过合理阈值的 `kmem_alloc`() 分配，将在控制台打印限速警告。

默认警告阈值设置为八页，但为了适应使用大页的系统，最大限制为 32K。选择该值是为了足够小，以确保最大的分配能够被快速发现和修复，同时又足够大，以避免在分配大小超过最优但不严重时记录警告。由于该值可调，开发者在测试时被鼓励将其设置得更低，以便快速捕获任何新的较大分配。通过将阈值设置为零，可以禁用这些警告。

### `spl_kmem_alloc_max=KMALLOC_MAX_SIZE/4`（无符号整数类型 uint）

较大的 `kmem_alloc` 分配若超过 **KMALLOC_MAX_SIZE** 将会失败。略小于该限制的分配可能会成功，但由于寻找连续空闲页的开销，仍应避免。因此，设置了一个具有合理安全余量 4 倍的最大 kmem 大小。大于此最大值的 `kmem_alloc` 分配会迅速失败。小于或等于此值的 `vmem_alloc` 分配将使用 `kmalloc`，但超过此值时会切换到 `vmalloc`。


### `spl_kmem_cache_magazine_size=0`（无符号整数类型 uint）

缓存 magazine 是一种优化手段，旨在最小化分配内存的开销。它通过维护每个 CPU 的最近释放对象缓存来实现，可以在不加锁的情况下重新分配这些对象。这能提高高度竞争缓存的性能。然而，由于 magazine 中的对象会阻止原本空闲的 slab 被立即释放，因此在低内存机器上可能并不理想。

因此，可以使用 **spl_kmem_cache_magazine_size** 来设置最大 magazine 大小。当该值设置为 `0` 时，magazine 大小将根据对象大小自动确定。否则，magazine 将限制为每个 magazine（即每个 CPU）2-256 个对象。在此实现中，magazine 永远不会被完全禁用。

### `spl_hostid=0`（无符号长整数类型 unsigned long）

系统主机 ID（hostid），在设置后可用于唯一标识一台系统。默认情况下，该值为 `0`，表示 hostid 被禁用。可以通过在 `/etc/hostid` 中放置唯一的非零值来显式启用。

### `spl_hostid_path=/etc/hostid`（指向字符的指针 `char *`）

指定时用于定位系统 hostid 的预期路径。对于非标准配置，可以覆盖此值。

### `spl_panic_halt=0`（无符号整数类型 uint）

在断言失败时引起内核 panic。未启用时，线程会被暂停以便进行进一步调试。

设置为非零值即可启用。

### `spl_taskq_kick=0`（无符号整数类型 uint）

触发卡住的 taskq 以生成线程。向其写入非零值时，会扫描所有 taskq。如果其中有任何待处理任务超过 5 秒未处理，它将触发生成更多线程。当你发现偶尔发生死锁，因为一个或多个 taskq 在应生成线程时未生成线程时，可以使用此功能。

### `spl_taskq_thread_bind=0`（整数数据类型 int）

将 taskq 线程绑定到特定 CPU。启用后，所有 taskq 线程将在可用 CPU 上均匀分布。在默认情况下，为了让 Linux 调度器最大限度地灵活决定线程的运行位置，已禁用此行为。

### `spl_taskq_thread_dynamic=1`（整数数据类型 int）

允许动态 taskq。启用后，设置了 **TASKQ_DYNAMIC** 标志的 taskq 默认只创建单个线程。将按需创建新的线程，直到达到允许的最大数量，以促进未完成任务的处理。不再需要的线程会被及时销毁。在默认情况下，已启用此行为；但为了帮助性能分析或故障排除，可以禁用。

### `spl_taskq_thread_priority=1`（整数数据类型 int）

为新创建的 taskq 线程设置非默认调度器优先级。在启用后，创建 taskq 时指定的优先级将应用于该 taskq 创建的所有线程。禁用时，所有线程将使用 Linux 内核的默认线程优先级。在默认情况下，此行为已启用。

### `spl_taskq_thread_sequential=4`（整数数据类型 int）

taskq 工作线程在请求生成新工作线程之前必须连续处理的任务数量。此设置用于控制 taskq 增加处理队列线程数量的速度。由于 Linux 线程的创建和销毁相对廉价，因此选择了较小的默认值。这意味着线程通常会积极创建，这是理想的。增加该值将导致线程创建速度变慢，对于某些配置可能更为合适。

### `spl_taskq_thread_timeout_ms=5000`（无符号整数类型 uint）

动态 taskq 的最小空闲线程退出间隔。较小的值能让空闲线程更频繁地退出，并可能按需重新生成，从而造成更多的线程波动。

2025 年 5 月 7 日	Debian













