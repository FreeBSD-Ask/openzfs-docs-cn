# zpool-sync(8)

## 名称

`zpool-sync` — 将数据刷写到 ZFS 存储池的主存储

## 概述

```sh
zpool sync [池名…]
```

## 说明

该命令强制把所有内核中的脏数据写入池的主存储，而不是写入 ZIL。它还会更新管理信息，包括配额报告。不带参数时，`zpool sync` 会同步系统上的所有池；否则只同步指定的池。

## 参考文献

zpoolconcepts(7)、zpool-export(8)、zpool-iostat(8)

2022 年 7 月 11 日
