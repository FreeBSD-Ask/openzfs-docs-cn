# zfs-clone(8)

## 名称

`zfs-clone` — 克隆 ZFS 数据集的快照

## 概述

```sh
zfs clone [-pu] [-o 属性=值]… 快照 文件系统|卷
```

## 说明

有关详情，参见 zfsconcepts(7) 的 Clones 一节。目标数据集可以位于 ZFS 层次结构中的任意位置，并以与原始数据集相同的类型创建。

### `-o property=value`

设置指定的属性；详情参见 `zfs create`。

### `-p`

创建所有不存在的父数据集。以此方式创建的数据集会按照从其父级继承的 `mountpoint` 属性自动挂载。如果多次指定 `-p` 选项，父数据集会以 `canmount=off` 创建。如果目标文件系统或卷已经存在，操作会成功完成。

### `-u`

不挂载新创建的文件系统。

## 示例

### 示例 1：创建 ZFS 克隆

以下命令创建一个可写文件系统，其初始内容与 `pool/home/bob@yesterday` 相同。

```sh
# zfs clone pool/home/bob@yesterday pool/clone
```

### 示例 2：提升 ZFS 克隆

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

## 参考文献

zfs-promote(8)、zfs-snapshot(8)

2022 年 7 月 11 日
