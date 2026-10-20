# zfs-snapshot(8)

## 名称

`zfs-snapshot` — 创建 ZFS 数据集的快照

## 概述

```sh
zfs snapshot [-r] [-o 属性=值]… 数据集@快照名…
```

## 说明

为某个数据集创建快照，或为不同数据集创建多个快照。

快照以原子方式创建。也就是说，快照是数据集在特定时间点的一致映像；它包含在该时间点之前成功完成的系统调用对数据集所做的全部修改。通过 `-r` 选项创建的递归快照都在同一时间创建。

`zfs snap` 可以用作 `zfs snapshot` 的别名。

详情参见 zfsconcepts(7) 的 Snapshots 一节。

### `-o property=value`

设置指定的属性；详情参见 `zfs create`。

### `-r`

为所有后代数据集递归创建快照。

## 示例

### 示例 1：创建 ZFS 快照

以下命令创建一个名为 `yesterday` 的快照。该快照按需挂载在 `pool/home/bob` 文件系统根目录的 `.zfs/snapshot` 目录中。

```sh
# zfs snapshot pool/home/bob@yesterday
```

### 示例 2：创建并销毁多个快照

以下命令为 `pool/home` 及其所有后代文件系统创建名为 `yesterday` 的快照。每个快照按需挂载在其文件系统根目录的 `.zfs/snapshot` 目录中。第二条命令销毁新建的快照。

```sh
# zfs snapshot -r pool/home@yesterday
# zfs destroy -r pool/home@yesterday
```

### 示例 3：提升 ZFS 克隆

以下命令演示如何使用克隆、克隆提升与重命名来测试对文件系统的更改，再用更改后的文件系统替换原始文件系统：

```sh
# zfs create pool/project/production
  用数据填充 /pool/project/production
# zfs snapshot pool/project/production@today
# zfs clone pool/project/production@today pool/project/beta
  对 /pool/project/beta 做出更改并进行测试
# zfs promote pool/project/beta
# zfs rename pool/project/production pool/project/legacy
# zfs rename pool/project/beta pool/project/production
  当不再需要 legacy 版本时，可以销毁它
# zfs destroy pool/project/legacy
```

### 示例 4：执行滚动快照

以下示例展示如何以一致的命名方案维护快照历史。若要保留一周的快照，用户先销毁最旧的快照，再重命名其余快照，然后创建一个新的快照，如下所示：

```sh
# zfs destroy -r pool/users@7daysago
# zfs rename -r pool/users@6daysago@7daysago
# zfs rename -r pool/users@5daysago@6daysago
# zfs rename -r pool/users@4daysago@5daysago
# zfs rename -r pool/users@3daysago@4daysago
# zfs rename -r pool/users@2daysago@3daysago
# zfs rename -r pool/users@yesterday@2daysago
# zfs rename -r pool/users@today@yesterday
# zfs snapshot -r pool/users@today
```

## 参考文献

zfs-bookmark(8)、zfs-clone(8)、zfs-destroy(8)、zfs-diff(8)、zfs-hold(8)、zfs-rename(8)、zfs-rollback(8)、zfs-send(8)

2022 年 7 月 11 日
