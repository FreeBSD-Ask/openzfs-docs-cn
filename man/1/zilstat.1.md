# zilstat(1)



## 名称

`zilstat` — 报告 ZFS 意图日志（Intent Log）统计信息

## 概述

```sh
zilstat [-v] [-a|-p 存储池|-d 数据集[,数据集…]] [-f 字段[,字段…]] [-s 分隔符] [-i 间隔]
```

## 说明

`zilstat` 将显示 ZFS 意图日志（ZFS Intent Log，ZIL）的统计信息。ZIL 用于记录同步写操作，如果系统在这些写入提交到主存储池之前崩溃，则在池导入时会重放这些日志。

在默认情况下，将显示全局 ZIL 统计信息。如果指定了存储池或数据集，则显示每个数据集的统计信息。

如果指定了间隔，输出会每隔指定秒数重复一次，显示自上一次采样以来的变化值。未指定间隔时，显示累积值。

可用的字段如下：

### time

当前时间

### pool

存储池名称

### ds

数据集名称

### obj

对象集 ID

### cc

提交次数

### cwc

提交写入器次数

### cec

提交错误次数

### csc

提交阻塞次数

### cSc

提交挂起次数

### cCc

提交崩溃次数

### ic

事务内计数

### iic

间接事务内计数

### iib

间接事务内字节数

### icc

复制事务内计数

### icb

复制事务内字节数

### inc

需要复制事务内计数

### inb

需要复制事务内字节数

### idc

直接（复制 + 需要复制）计数

### idb

直接（复制 + 需要复制）字节数

### iwc

总写入次数（间接 + 直接）


### iwb

总写入字节数（间接 + 直接）

### imnc

普通 metaslab 数量

### imnb

普通 metaslab 字节数

### imnw

普通 metaslab 写入字节数

### imna

普通 metaslab 分配字节数

### imsc

SLOG metaslab 数量

### imsb

SLOG metaslab 字节数

### imsw

SLOG metaslab 写入字节数

### imsa

SLOG metaslab 分配字节数

### imc

总 metaslab 数量（普通 + SLOG）

### imb

总 metaslab 字节数（普通 + SLOG）

### imw

总 metaslab 写入字节数（普通 + SLOG）

### ima

总 metaslab 分配字节数（普通 + SLOG）

### se%

空间效率百分比（字节 / 分配）

### sen%

普通空间效率百分比

### ses%

SLOG 空间效率百分比

### te%

总效率百分比（字节 / 写入）

### ten%

普通总效率百分比

### tes%

SLOG 总效率百分比

## 选项

### `-h`

显示帮助信息。

### `-a`

打印所有存储池中所有数据集的统计信息。

### `-d dataset`

打印指定数据集的统计信息。可以通过逗号分隔提供多个数据集。

### `-f field`

仅显示指定字段。可以通过逗号分隔提供多个字段。可用字段请参见说明。

### `-i interval`

每隔“间隔”秒打印一次统计信息。数值报告速率为每秒一次。

### `-p pool`

打印指定存储池中所有数据集的统计信息。

### `-s separator`

用自定义字符串替换默认字段分隔符（两个空格）。

### `-v`

列出所有可用字段标题及其定义。

## 环境

### Linux

将从 `/proc/spl/kstat/zfs/zil` 读取全局统计信息，从 `/proc/spl/kstat/zfs/pool/` 下的 objset 文件读取单个存储池统计信息。

### FreeBSD

通过 sysctl(8) 从 `kstat.zfs` 树中读取统计信息。

## 参考文献

zarcstat(1)、zpool-status(8)

## 作者

本手册页由 Christos Longros `<chris.longros@gmail.com>` 编写。


2026 年 3 月 9 日 Debian
