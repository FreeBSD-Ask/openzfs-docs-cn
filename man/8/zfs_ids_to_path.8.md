# zfs_ids_to_path(8)

## 名称

`zfs_ids_to_path` — 将 objset 与对象 ID 转换为名称与路径

## 概述

```sh
zfs_ids_to_path [-v] 池名 objset-id object-id
```

## 说明

`zfs_ids_to_path` 工具把给定的 objset 与对象 ID 转换为它们所指文件的路径。

### `-v`

详细模式。分别打印数据集名称与数据集内的文件路径。即使数据集未挂载也能正确工作。

## 参考文献

zdb(8)、zfs(8)

2022 年 7 月 11 日
