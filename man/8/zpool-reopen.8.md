# zpool-reopen(8)

## 名称

`zpool-reopen` — 重新打开 ZFS 存储池关联的 vdev

## 概述

```sh
zpool reopen [-n] [池名…]
```

## 说明

重新打开指定池（未指定时为所有池）关联的全部 vdev。

## 选项

### `-n`

不要重新开始正在进行的 scrub 操作。不建议这样做：除非再执行一次 scrub，否则可能导致设备只被部分 resilver。

2022 年 7 月 11 日
