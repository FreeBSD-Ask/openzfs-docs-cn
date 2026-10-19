# zpool-detach(8)

## 名称

`zpool-detach` — 从 ZFS 镜像中分离设备

## 概述

```sh
zpool detach 池名 设备
```

## 说明

从镜像中分离指定设备。如果数据没有其他有效副本，该操作会被拒绝。如果该设备之后可能会重新加入池，请考虑改用 `zpool offline` 命令。

## 参考文献

zpool-attach(8)、zpool-labelclear(8)、zpool-offline(8)、zpool-remove(8)、zpool-replace(8)、zpool-split(8)

2022 年 7 月 11 日
