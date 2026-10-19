# zfs-zone(8)

## 名称

`zfs-zone`、`zfs-unzone` — 将 ZFS 文件系统附加或分离到用户命名空间

`zfs-unzone(8)` 是 `zfs-zone(8)` 的历史别名。

## 概述

```sh
zfs zone nsfile filesystem
zfs unzone nsfile filesystem
```

## 说明

### `zfs zone nsfile filesystem`

将指定的 `filesystem` 附加到由 `nsfile` 标识的用户命名空间。从此以后，如果已设置 `zoned` 属性，该文件系统树就可以从用户命名空间内进行管理。

不能把某个 zoned 数据集的子数据集附加到另一个用户命名空间。也不能附加用户命名空间的根文件系统，或任何需要在用户命名空间内运行 zfs 服务之前就已挂载的数据集，因为它会以未挂载状态被附加，直到命名空间内的服务把它挂载。

要允许从用户命名空间内管理数据集，必须设置 `zoned` 属性，并且用户命名空间需要能够访问 `/dev/zfs` 设备。`quota` 属性无法从用户命名空间内更改。

数据集附加到用户命名空间且设置了 `zoned` 属性后，无法在用户命名空间外部挂载 zoned 文件系统，因为用户命名空间管理员可能已经把挂载点设置为不可接受的值。

### `zfs unzone nsfile filesystem`

将指定的 `filesystem` 从由 `nsfile` 标识的用户命名空间分离。

## 示例

### 示例 1：将数据集委托给用户命名空间

以下示例把数据集 `tank/users` 委托给由用户命名空间文件 `/proc/1234/ns/user` 标识的用户命名空间。

```sh
# zfs zone /proc/1234/ns/user tank/users
```

## 参考文献

zfsprops(7)、zfs-allow(8)

对于命名空间为临时存在的无根容器使用场景，可以考虑改用 `zoned_uid` 属性：它将委托权限授予属于某个 UID 的所有命名空间，而不需要附加到特定的命名空间文件。`zoned_uid` 属性采用三层累加式授权模型（UID 匹配、dsl_deleg 授权、能力层级），参见 zfsprops(7)。

2022 年 7 月 11 日
