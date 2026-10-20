# zfs-bookmark(8)

## 名称

`zfs-bookmark` — 为 ZFS 快照创建书签

## 概述

```sh
zfs bookmark [-r] 快照|书签 新书签
```

## 说明

为给定的快照或书签创建一个新书签。书签标记了快照创建时的时间点，可以用作 `zfs send` 的增量源。

### `-r`

为所有后代数据集的给定源快照递归创建书签。源必须是一个快照，并且只为拥有同名快照的后代创建书签；没有该快照的后代将被跳过。

从现有的遮蔽书签创建书签时，生成的书签**不是**遮蔽书签。

必须先启用相应特性才能使用此功能。有关 ZFS 特性标志和 `bookmarks` 特性的详细信息，参见 zpool-features(7)。

## 示例

### 示例 1：创建书签

以下示例为一个快照创建书签。此后可以在发送流中用该书签代替快照。

```sh
# zfs bookmark rpool@snapshot rpool#bookmark
```

## 参考文献

zfs-destroy(8)、zfs-send(8)、zfs-snapshot(8)

2022 年 7 月 11 日
