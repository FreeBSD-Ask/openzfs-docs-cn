# Async Write I/O 调度

为 async write I/O 类发出的并发操作数量遵循一个分段线性函数，该函数由若干可调节点定义：

```
|                   o---------| <-- zfs_vdev_async_write_max_active
  ^    |                  /^         |
  |    |                 / |         |
active |                /  |         |
 I/O   |               /   |         |
count  |              /    |         |
       |             /     |         |
       |------------o      |         | <-- zfs_vdev_async_write_min_active
      0|____________^______|_________|
       0%           |      |        100% of zfs_dirty_data_max
                    |      |
                    |      `-- zfs_vdev_async_write_active_max_dirty_percent
                    `--------- zfs_vdev_async_write_active_min_dirty_percent
```

在脏数据量未超过存储池允许脏数据最小百分比之前，I/O 调度器会将并发操作数量限制为最小值。当超过该阈值后，发出的并发操作数量会随脏数据量线性增加，并在达到所指定的允许脏数据最大百分比时达到最大值。

理想情况下，繁忙存储池中的脏数据量应保持在 `zfs_vdev_async_write_active_min_dirty_percent` 与 `zfs_vdev_async_write_active_max_dirty_percent` 之间的函数斜坡区间内。如果超过最大百分比，则表明传入数据速率大于后端存储能够处理的速率。在这种情况下，必须进一步对传入写入进行节流。详见 ZIO Transaction Delay。

参考代码： [vdev_queue.c](https://github.com/openzfs/zfs/blob/master/module/zfs/vdev_queue.c#L42)
