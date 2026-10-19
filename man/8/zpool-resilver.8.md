# zpool-resilver(8)

## 名称

`zpool-resilver` — 对 ZFS 存储池中的设备执行 resilver

## 概述

```sh
zpool resilver 池名…
```

## 说明

对指定池启动 resilver。如果已有 resilver 正在运行，将从开头重新开始。任何被安排为延迟 resilver 的驱动器都会被加入新的 resilver。这需要 `resilver_defer` 池特性。

由于在线系统上存在并发写入，resilver 的进度有可能超过 100%。

## 参考文献

zpool-iostat(8)、zpool-online(8)、zpool-reopen(8)、zpool-replace(8)、zpool-scrub(8)、zpool-status(8)

2022 年 7 月 11 日
