# zpool-destroy(8)

## 名称

`zpool-destroy` — 销毁 ZFS 存储池

## 概述

```sh
zpool destroy [-f] 池名
```

## 说明

销毁给定的池，将其设备释放供其他用途使用。该命令会在销毁池之前尝试卸载所有活动数据集。

### `-f`

强制卸载所有活动数据集。

## 示例

### 示例 1：销毁 ZFS 存储池

以下命令销毁池 `tank` 及其中包含的所有数据集：

```sh
# zpool destroy -f tank
```

2022 年 7 月 11 日
