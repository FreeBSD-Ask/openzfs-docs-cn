# zpool-wait(8)

## 名称

`zpool-wait` — 等待 ZFS 存储池中的活动停止

## 概述

```sh
zpool wait [-Hp] [-T u|d] [-t 活动[,活动]…] 池名 [间隔]
```

## 说明

等待指定池中所有指定类型的后台活动停止。活动可能因为已完成而停止，也可能因为被用户暂停或取消，或因为池已被导出或销毁而停止。如果未指定任何活动，该命令会等待下列所有类型的后台活动都停止。如果没有指定类型的活动正在进行，该命令会立即返回。

以下是 `activity` 的可能取值，以及各自等待的内容：

* `discard` — 等待检查点被丢弃
* `free` — 等待 `freeing` 属性变为 `0`
* `initialize` — 等待所有初始化停止
* `replace` — 等待所有设备替换停止
* `remove` — 等待设备移除停止
* `resilver` — 等待 resilver 停止
* `scrub` — 等待 scrub 停止
* `trim` — 等待手动 trim 停止
* `raidz_expand` — 等待向 RAID-Z vdev 的附加操作完成
* `condense` — 等待元数据 condense 操作完成

如果提供了 `interval`，则每 `interval` 秒打印一次每种活动剩余的工作量（以字节为单位）。

### `-H`

脚本模式。不显示表头，字段之间用单个制表符而不是任意数量的空格分隔。

### `-p`

以可解析的（精确）数值显示数字。

### `-T u`、`-T d`

显示时间戳。为 `-T` 指定 `u`，以内部时间表示的可打印形式显示，参见 time(1)；指定 `d`，使用标准日期格式显示，参见 date(1)。

## 参考文献

zpool-checkpoint(8)、zpool-condense(8)、zpool-initialize(8)、zpool-remove(8)、zpool-replace(8)、zpool-resilver(8)、zpool-scrub(8)、zpool-status(8)、zpool-trim(8)

2026 年 5 月 26 日
