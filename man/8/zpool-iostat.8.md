# zpool-iostat(8)

## 名称

`zpool-iostat` — 显示 ZFS 存储池的逻辑 I/O 统计信息

## 概述

```sh
zpool iostat [[[-c 脚本] [-lq]]|-rw] [-T d|u] [-ghHLnpPvy] [[池名…]|[池名 vdev…]|vdev…] [间隔 [次数]]
```

## 说明

显示给定池/vdev 的逻辑 I/O 统计信息。物理 I/O 统计信息可通过 iostat(1) 观察。如果写入位置相邻，它们可能会合并为一次更大的操作。根据 vdev 冗余级别的不同，还可能产生额外的 I/O。要过滤输出，可以传入一个池名列表、某个池及其中的 vdev 列表，或任意池中任意 vdev 的列表。如果未指定任何对象，则显示系统中每个池的统计信息。指定 `interval` 时，统计信息每隔 `interval` 秒打印一次，直到被终止。如果指定了 `-n` 标志，表头只显示一次，否则会周期性显示。如果指定了 `count`，则打印 `count` 份报告后命令退出。无论是否传入 `interval` 与 `count`，第一份报告始终是自启动以来的平均每秒统计信息。不过，可以用 `-y` 标志抑制这一行为。另请注意，报告中打印的 `K`、`M`、`G` 等单位以 1024 为基数。要获得原始值，请使用 `-p` 标志。

### `-c 脚本1[,脚本2,…]`

在每个 vdev 上运行一个（或多个）脚本，并将输出作为新的一列包含在 `zpool iostat` 的输出中。用户可以运行其 `~/.zpool.d` 目录或系统 `/etc/zfs/zpool.d` 目录中的任何脚本。脚本名不得包含斜杠（`/`）字符。可以通过设置 `ZPOOL_SCRIPTS_PATH` 环境变量来覆盖默认搜索路径。特权用户只有在设置了 `ZPOOL_SCRIPTS_AS_ROOT` 环境变量时才能运行 `-c`。如果某个脚本需要使用特权命令（如 smartctl(8)），建议你在 `/etc/sudoers` 中授予该用户访问权限。

如果不带脚本名传入 `-c`，则会打印所有脚本的列表。`-c` 还会启用详细模式（`-v`）。

脚本输出应采用 `name=value` 的形式。列名被设为 `name`，值被设为 `value`。可以使用多行输出多列。第一行不符合 `name=value` 格式的输出会不带列标题显示，其后不再显示任何输出。这可用于打印错误消息。空白或 NULL 值会打印为 `-`，以便输出能被 AWK 处理。

在运行每个脚本之前会设置以下环境变量：

#### `VDEV_PATH`

vdev 的完整路径。

#### `VDEV_UPATH`

vdev 的底层路径（`/dev/sd*`）。用于 device mapper、多路径或分区的 vdev。

#### `VDEV_ENC_SYSFS_PATH`

vdev 所在机箱（如有）的 sysfs 路径。

### `-T d|u`

显示时间戳。指定 `d` 使用标准日期格式，参见 date(1)。指定 `u` 使用时间内部表示的可打印形式，参见 time(1)。

### `-g`

显示 vdev 的 GUID 而非通常的设备名。这些 GUID 可以在 zpool detach/offline/remove/replace 命令中代替设备名使用。

### `-H`

脚本模式。不显示表头，并改用单个制表符而不是任意数量的空格分隔字段。

### `-L`

显示 vdev 的真实路径，解析所有符号链接。无论打开设备时使用的是 `/dev/disk/` 下的哪个路径，都可以用它查找当前的块设备名。

### `-n`

传入时只打印一次表头。

### `-p`

以可解析（精确）值显示数字。时间值以纳秒为单位。

### `-P`

显示 vdev 的完整路径，而不是只有路径的最后一个组成部分。可以与 `-L` 标志配合使用。

### `-r`

打印叶 vdev 的 I/O 请求大小直方图。其中包括单个 I/O（ind）与聚合 I/O（agg）的直方图。这些统计信息可用于观察 I/O 聚合的效果。请注意，TRIM I/O 可能超过 16M，但会按 16M 计算。

### `-v`

详细统计信息。除池范围的统计信息外，还会报告池中各个 vdev 的使用统计信息。

### `-y`

通常输出的第一行报告自启动以来的统计信息：抑制该行。

### `-w`

显示延迟直方图：

#### `total_wait`

总 I/O 时间（排队时间 + 磁盘 I/O 时间）。

#### `disk_wait`

磁盘 I/O 时间（读写磁盘的时间）。

#### `syncq_wait`

I/O 在同步优先级队列中花费的时间。不包含磁盘时间。

#### `asyncq_wait`

I/O 在异步优先级队列中花费的时间。不包含磁盘时间。

#### `scrub`

I/O 在 scrub 队列中花费的时间。不包含磁盘时间。

#### `rebuild`

I/O 在重建队列中花费的时间。不包含磁盘时间。

### `-l`

包含平均延迟统计信息：

#### `total_wait`

平均总 I/O 时间（排队时间 + 磁盘 I/O 时间）。

#### `disk_wait`

平均磁盘 I/O 时间（读写磁盘的时间）。

#### `syncq_wait`

I/O 在同步优先级队列中花费的平均时间。不包含磁盘时间。

#### `asyncq_wait`

I/O 在异步优先级队列中花费的平均时间。不包含磁盘时间。

#### `scrub`

在 scrub 队列中的平均排队时间。不包含磁盘时间。

#### `trim`

在 trim 队列中的平均排队时间。不包含磁盘时间。

#### `rebuild`

在重建队列中的平均排队时间。不包含磁盘时间。

### `-q`

包含活动队列统计信息。每个优先级队列都有待处理（`pend`）与活动（`activ`）的 I/O 请求。待处理请求正在等待发往磁盘，活动请求已发往磁盘并正在等待完成。这些统计信息按优先级队列细分：

#### `syncq_read/write`

同步优先级队列中的当前条目数。

#### `asyncq_read/write`

异步优先级队列中的当前条目数。

#### `scrubq_read`

scrub 队列中的当前条目数。

#### `trimq_write`

trim 队列中的当前条目数。

#### `rebuildq_write`

重建队列中的当前条目数。

所有队列统计信息都是对队列中条目数的瞬时测量。如果指定了间隔，则测量值取自该间隔的末尾。

## 示例

### 示例 13：向 ZFS 池添加缓存设备

以下命令向 ZFS 存储池添加两块磁盘用作缓存设备：

```sh
# zpool add pool cache sdc sdd
```

添加后，缓存设备会逐渐填满来自主内存的内容。视缓存设备的大小而定，填满可能需要一个多小时。可以使用 `iostat` 子命令监控容量与读取情况，如下所示：

```sh
# zpool iostat -v pool 5
```

### 示例 16：添加输出列

可以使用 `-c` 向 `zpool status` 与 `zpool iostat` 的输出添加额外的列。

```sh
# zpool status -c vendor,model,size
   NAME     STATE  READ WRITE CKSUM vendor  model        size
   tank     ONLINE 0    0     0
   mirror-0 ONLINE 0    0     0
   U1       ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U10      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U11      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U12      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U13      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U14      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T

# zpool iostat -vc size
              capacity     operations     bandwidth
pool        alloc   free   read  write   read  write  size
----------  -----  -----  -----  -----  -----  -----  ----
rpool       14.6G  54.9G      4     55   250K  2.69M
  sda1      14.6G  54.9G      4     55   250K  2.69M   70G
----------  -----  -----  -----  -----  -----  -----  ----
```

## 参考文献

iostat(1)、smartctl(8)、zpool-list(8)、zpool-status(8)

2024 年 1 月 29 日
