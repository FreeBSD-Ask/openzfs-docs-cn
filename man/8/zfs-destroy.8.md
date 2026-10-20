# zfs-destroy(8)

## 名称

`zfs-destroy` — 销毁 ZFS 数据集、快照或书签

## 概述

```sh
zfs destroy [-Rfnprv] 文件系统 | 卷
```

```sh
zfs destroy [-Rdnprv] 文件系统 | 卷@快照[%快照[,%快照[%快照]]]…
```

```sh
zfs destroy 文件系统 | 卷#书签
```

## 说明

### `zfs destroy [-Rfnprv] filesystem | volume`

销毁给定的数据集。默认情况下，该命令会取消共享当前处于共享状态的文件系统，卸载当前处于挂载状态的文件系统，并拒绝销毁存在活动依赖项（子项或克隆）的数据集。

#### `-R`

递归销毁所有依赖项，包括目标层次结构之外由克隆得到的文件系统。

#### `-f`

强制卸载文件系统。此选项对非文件系统或未挂载的文件系统没有影响。

#### `-n`

执行一次空操作（No-op）的模拟删除。不会删除任何数据。此选项与 `-v` 或 `-p` 标志配合使用时很有用，可以用来确定将删除哪些数据。

#### `-p`

打印关于被删除数据的、机器可解析的详细信息。

#### `-r`

递归销毁所有子项。

#### `-v`

打印关于被删除数据的详细信息。

应用 `-r` 或 `-R` 选项时务必格外小心，因为它们可能销毁池的很大一部分，并对正在使用中的已挂载文件系统造成意外行为。

### `zfs destroy [-Rdnprv] filesystem | volume@snap[%snap[,%snap[%snap]]]…`

尝试销毁给定的快照。如果存在该快照的任何克隆，或者该快照被施加了保留，此操作将失败。这种情况下，默认 `zfs destroy` 不会产生任何效果，并以错误退出。如果指定了 `-d` 选项，该命令会改为将给定快照标记为“一旦符合条件即自动销毁”。在被标记为待销毁期间，该快照仍然可见，你可以从它创建新的克隆，也可以对它施加新的保留。

只读快照属性 `defer_destroy` 和 `userrefs` 由 `zfs destroy` 用来判定销毁资格与标记状态。

用百分号分隔第一个和最后一个快照，即可指定一个包含两端的快照范围。第一个和/或最后一个快照可以留空，此时将隐含使用该文件系统最旧或最新的快照。

同一文件系统或卷的多个快照（或多个快照范围）可以在一个以逗号分隔的快照列表中指定。使用范围或逗号分隔列表标识多个快照时，只应指定快照的短名称（即 `@` 之后的部分）。

#### `-R`

递归销毁这些快照的所有克隆，包括克隆、快照和子项。如果指定了此标志，`-d` 标志将不起任何作用。

#### `-d`

当给定的快照不符合立即销毁的条件时，不返回错误，而是将其标记为延迟销毁，待其符合条件后自动销毁。

#### `-n`

执行一次空操作（No-op）的模拟删除。不会删除任何数据。此选项与 `-p` 或 `-v` 标志配合使用时很有用，可以用来确定将删除哪些数据。

#### `-p`

打印关于被删除数据的、机器可解析的详细信息。

#### `-r`

销毁后代文件系统中所有具有此名称的快照（或将其标记为延迟删除）。

#### `-v`

打印关于被删除数据的详细信息。

应用 `-r` 或 `-R` 选项时务必格外小心，因为它们可能销毁池的很大一部分，并对正在使用中的已挂载文件系统造成意外行为。

### `zfs destroy filesystem | volume#bookmark`

给定的书签会被销毁。

## 示例

### 示例 1：创建并销毁多个快照

以下命令为 `pool/home` 及其所有后代文件系统创建名为 `yesterday` 的快照。每个快照都会按需挂载在其文件系统根目录的 `.zfs/snapshot` 目录下。第二条命令销毁新创建的快照。

```sh
# zfs snapshot -r pool/home@yesterday
# zfs destroy -r pool/home@yesterday
```

### 示例 2：提升 ZFS 克隆

以下命令展示如何使用克隆、克隆提升和重命名来测试对文件系统的更改，然后用更改后的文件系统替换原始文件系统：

```sh
# zfs create pool/project/production
  向 /pool/project/production 填充数据
# zfs snapshot pool/project/production@today
# zfs clone pool/project/production@today pool/project/beta
  修改 /pool/project/beta 并进行测试
# zfs promote pool/project/beta
# zfs rename pool/project/production pool/project/legacy
# zfs rename pool/project/beta pool/project/production
  旧版本不再需要时即可销毁
# zfs destroy pool/project/legacy
```

### 示例 3：执行滚动快照

以下示例展示如何以一致的命名方案维护快照历史。若要保留一周的快照，用户先销毁最旧的快照，再重命名其余快照，然后创建一个新的快照，如下所示：

```sh
# zfs destroy -r pool/users@7daysago
# zfs rename -r pool/users@6daysago @7daysago
# zfs rename -r pool/users@5daysago @6daysago
# zfs rename -r pool/users@4daysago @5daysago
# zfs rename -r pool/users@3daysago @4daysago
# zfs rename -r pool/users@2daysago @3daysago
# zfs rename -r pool/users@yesterday @2daysago
# zfs rename -r pool/users@today @yesterday
# zfs snapshot -r pool/users@today
```

## 参考文献

zfs-create(8)、zfs-hold(8)、zfsprops(8)

2025 年 2 月 5 日
