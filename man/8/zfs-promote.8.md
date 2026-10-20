# zfs-promote(8)

## 名称

`zfs-promote` — 提升克隆数据集，使其不再依赖源快照

## 概述

```sh
zfs promote 克隆
```

## 说明

`zfs promote` 命令使你能够销毁创建该克隆的源数据集。克隆与源数据集之间的父子依赖关系会反转，源数据集变为指定数据集的克隆。

被克隆的快照以及该快照之前的所有快照，现在归提升后的克隆所有。它们所占用的空间从源数据集转移到提升后的克隆，因此必须有足够的空间容纳这些快照。此操作不会消耗新的空间，但空间统计会相应调整。提升后的克隆自身不能有任何冲突的快照名，可用 `zfs rename` 子命令重命名冲突的快照。

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

## 参考文献

zfs-clone(8)、zfs-rename(8)

2022 年 7 月 11 日
