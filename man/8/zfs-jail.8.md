# zfs-jail(8)

## 名称

`zfs-jail` — 将 ZFS 文件系统附加或分离到 FreeBSD jail

`zfs-unjail(8)` 是 `zfs-jail(8)` 的历史别名。

## 概述

```sh
zfs jail jailid|jailname 文件系统
```

```sh
zfs unjail jailid|jailname 文件系统
```

## 说明

`zfs jail` 功能可以把数据集分配给正在运行的 FreeBSD jail（jail(4)），从而允许在 jail(4) 内运行 zfs(8) 管理实用程序。

要允许从 jail 内管理数据集，应设置 `jailed` 属性，并且 jail 内必须具备为暴露 `/dev/zfs` 设备所需的 devfs.conf(5) 条目。`quota` 属性无法从 jail 内更改。

要使用此功能，jail 需要将 `allow.mount` 和 `allow.mount.zfs` 参数设为 `1`，并将 `enforce_statfs` 参数设为小于 `2` 的值。

子命令如下：

### `zfs jail jailid|jailname filesystem`

把指定的 `filesystem` 附加到由 JID `jailid` 或名称 `jailname` 标识的 jail。此后，如果设置了 `jailed` 属性，该文件系统树就可以从 jail 内进行管理。

不能把某个 jailed 数据集的子数据集附加到另一个 jail。也不能附加 jail 的根文件系统，或任何需要在 jail 内运行 zfs rc 脚本之前挂载的数据集，因为它会以未挂载状态被附加，直到 jail 内的 rc 脚本将它挂载。

数据集附加到 jail 且设置了 `jailed` 属性后，无法在 jail 外挂载 jailed 文件系统，因为 jail 管理员可能已经把挂载点设置为不可接受的值。

### `zfs unjail jailid|jailname filesystem`

把指定的 `filesystem` 从由 JID `jailid` 或名称 `jailname` 标识的 jail 分离。

## 参考文献

devfs.conf(5)、zfsprops(7)、jail(8)

## 注意事项

无法用本工具把 jail 的根目录委托给该 jail，因为 jail 必须以有效的根目录运行。

jail 是 FreeBSD 的特性，在其他平台上不适用。有关管理 jail 的更多信息参见 jail(8)；Linux 上的等价功能参见 zfs-zone(8)。

2025 年 11 月 4 日
