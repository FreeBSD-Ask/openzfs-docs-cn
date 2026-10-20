# zpool-add(8)

## 名称

`zpool-add` — 向 ZFS 存储池添加 vdev

## 概述

```sh
zpool add [-fgLnP] [--allow-in-use --allow-replication-mismatch --allow-ashift-mismatch] [-o property=value] 池名 vdev …
```

## 说明

将指定的虚拟设备添加到给定的池中。`vdev` 规格说明参见 zpoolconcepts(7) 的“虚拟设备（vdevs）”一节。`-f` 选项的行为以及执行的设备检查，参见 `zpool create` 子命令。

### `-f`

强制使用 `vdev`，即使它们看起来已被占用、ashift 值冲突或指定的冗余级别冲突。并非所有设备都能以这种方式覆盖。

### `-g`

显示 `vdev` 的 GUID，而不是通常的设备名称。这些 GUID 可在 zpool detach/offline/remove/replace 命令中用来替代设备名称。

### `-L`

显示 `vdev` 的实际路径，解析所有符号链接。这可用于查找当前的块设备名称，而不受打开它时使用的 `/dev/disk` 路径影响。

### `-n`

显示将要使用的配置，但不实际添加 `vdev`。实际的池创建仍可能因权限不足或设备共享而失败。

### `-P`

显示 `vdev` 的实际路径，而不是仅显示路径的最后一个组件。可与 `-L` 标志配合使用。

### `-o property=value`

设置给定的池属性。可设置的属性列表参见 zpoolprops(7) 手册页。目前唯一支持的属性是 `ashift`。

### `--allow-ashift-mismatch`

禁用 ashift 验证，允许池中 ashift 值不匹配。添加扇区大小不同的顶级 vdev 将禁止未来的设备移除操作，参见 zpool-remove(8)。

### `--allow-in-use`

即使 `vdev` 可能已在另一个池中使用，也允许添加。

### `--allow-replication-mismatch`

允许将冗余级别冲突的 `vdev` 添加到池中。

## 示例

### 示例 1：向 ZFS 存储池添加镜像

以下命令向池 `tank` 添加两块镜像磁盘，假设该池已经由双盘镜像组成。新增空间可立即供池内的任何数据集使用。

```sh
# zpool add tank mirror sda sdb
```

### 示例 2：向 ZFS 存储池添加缓存设备

以下命令向 ZFS 存储池添加两块用作缓存设备的磁盘：

```sh
# zpool add pool cache sdc sdd
```

添加完成后，缓存设备会逐渐被主内存中的内容填满。根据你的缓存设备大小，填满可能需要一个多小时。容量和读取情况可使用 `iostat` 子命令监控，如下所示：

```sh
# zpool iostat -v pool 5
```

## 参考文献

zpool-attach(8)、zpool-import(8)、zpool-initialize(8)、zpool-online(8)、zpool-remove(8)

2024 年 3 月 8 日
