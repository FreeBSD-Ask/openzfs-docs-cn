# zpool-history(8)

## 名称

`zpool-history` — 查看 ZFS 存储池的命令历史

## 概述

```sh
zpool history [-il] [池名…]
```

## 说明

显示指定池（或未指定池时的所有池）的命令历史。

### `-i`

除用户发起的事件外，还显示内部记录的 ZFS 事件。

### `-l`

以长格式显示日志记录：除标准格式外，还包括执行操作的用户名、主机名以及所在的 zone。

## 参考文献

zpool-checkpoint(8)、zpool-events(8)、zpool-status(8)、zpool-wait(8)

2022 年 7 月 11 日
