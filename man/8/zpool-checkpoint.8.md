# zpool-checkpoint(8)

## 名称

`zpool-checkpoint` — 为 ZFS 存储池当前状态创建检查点

## 概述

```sh
zpool checkpoint [-d] [-w] pool
```

## 说明

为池的当前状态创建检查点，之后可以通过 `zpool import --rewind-to-checkpoint` 恢复到该状态。池中存在检查点时，禁止执行以下 `zpool` 子命令：`remove`、`attach`、`detach`、`split` 与 `reguid`。此外，如果池缺乏空闲空间，检查点还可能破坏预留值边界。`zpool status` 命令会指示池中是否存在检查点，或者检查点从池中丢弃的进度。可以使用 `zpool list` 查看检查点占用了池中的多少空间。

## 选项

### `-d`、`-discard`

丢弃指定池上的现有检查点。

### `-w`、`-wait`

等待检查点丢弃完成后再返回。

## 参考文献

zfs-snapshot(8)、zpool-import(8)、zpool-status(8)

2022 年 7 月 11 日
