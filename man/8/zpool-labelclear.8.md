# zpool-labelclear(8)

## 名称

`zpool-labelclear` — 从设备移除 ZFS 标签信息

## 概述

```sh
zpool labelclear [-f] 设备
```

## 说明

从指定设备移除 ZFS 标签信息。如果该设备是缓存设备，还会一并移除 L2ARC 头部（持久化 L2ARC）。该设备不能属于活动池配置。

该操作会覆盖池元数据，导致设备上的所有数据在没有专用恢复工具的情况下无法访问。与 `zpool destroy` 不同，此操作无法通过 ZFS 工具撤销。只有当你不在意设备上的数据时才可使用。

### `-f`

把已导出或外来的设备视为非活动设备。

## 参考文献

zpool-destroy(8)、zpool-detach(8)、zpool-remove(8)

2022 年 7 月 11 日
