# zvol_wait(1)

## 名称

`zvol_wait` — 等待 ZFS 卷的设备节点在 `/dev` 中出现

## 概述

```sh
zvol_wait	
```

## 说明

当导入某 ZFS 池时，其内部的卷会作为块设备出现。随着它们的注册，udev(7) 会异步地在 `/dev/zvol` 下使用卷名创建符号链接。`zvol_wait` 会等待上述全部的符号链接创建完成后再退出。

## 参考文献

udev(7)

2021 年 5 月 27 日  Debian
