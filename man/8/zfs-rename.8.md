# zfs-rename(8)

## 名称

`zfs-rename` — 重命名 ZFS 数据集

## 概述

```sh
zfs rename [-f] 文件系统|卷|快照 文件系统|卷|快照
```

```sh
zfs rename -p [-f] 文件系统|卷 文件系统|卷
```

```sh
zfs rename -u [-f] 文件系统 文件系统
```

```sh
zfs rename -r 快照 快照
```

## 说明

### `zfs rename [-f] filesystem|volume|snapshot filesystem|volume|snapshot`

### `zfs rename -p [-f] filesystem|volume filesystem|volume`

### `zfs rename -u [-f] filesystem filesystem`

重命名指定的数据集。新目标可以位于 ZFS 层次结构中的任意位置，快照除外。快照只能在父文件系统或卷内重命名。重命名快照时，无需在第二个参数中指定该快照的父文件系统。重命名后的文件系统可以继承新的挂载点，此时它们会先被卸载，再挂载到新的挂载点。

#### `-f`

强制卸载在此过程中需要卸载的所有文件系统。此标志与 `-u` 标志一起使用时无效。

#### `-p`

创建所有不存在的父数据集。以此方式创建的数据集会按照从其父级继承的 `mountpoint` 属性自动挂载。另一种情况是，如果多次指定 `-p` 选项，父数据集会以 `canmount=off` 创建。

#### `-u`

重命名期间不重新挂载文件系统。如果文件系统的 `mountpoint` 属性设为 `legacy` 或 `none`，则即使未指定此选项，也不会卸载该文件系统。

### `zfs rename -r snapshot snapshot`

递归重命名所有后代数据集的快照。快照是唯一可以递归重命名的数据集。

## 示例

### 示例 1：提升 ZFS 克隆

以下命令演示如何使用克隆、克隆提升与重命名来测试对文件系统的更改，再用更改后的文件系统替换原始文件系统：

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

### 示例 2：执行滚动快照

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

2022 年 7 月 11 日
