# zarcsummary(1)

## 名称

`zarcsummary` — 打印 ZFS ARC 和子系统统计信息

## 概述

```sh
zarcsummary [-adghr] [-p 页] [-s 小节]
```

## 说明

`zarcsummary` 从正在运行的内核收集统计信息，并打印一份易于阅读的报告，说明 ZFS 自适应替换缓存（Adaptive Replacement Cache，ARC）及若干相关子系统的状态。输出是某一时刻的快照；如需周期性采样，请改用 zarcstat(1)。

不带参数调用时，`zarcsummary` 会依次打印所有小节。使用 `-s` 选项可以选择单个小节。

报告分为以下小节：

### arc

当前与目标的 ARC 大小、最近使用（Most Recently Used，MRU）列表与最常使用（Most Frequently Used，MFU）列表之间的划分、总体命中率与未命中率、压缩节省量，以及 ARC 是否正承受内存压力。

### archits

从按需读取与预取、数据与元数据两个维度划分的 ARC 命中与未命中明细。

### dmu

数据管理单元预测性预取器的统计信息，包括流的命中次数、未命中次数，以及在当前流之前和之后发出的 I/O。

### l2arc

附加到已导入存储池的任何缓存设备的二级 ARC 统计信息。仅当存在 L2ARC 设备时才显示此小节，内容涵盖读取和写入的字节数、命中率以及淘汰活动。

### spl

Solaris 移植层（Solaris Porting Layer）内存分配器的统计信息。此小节仅在 Linux 上可用。

### tunables

控制 ARC 行为的内核可调参数的当前值，包括 `zfs_arc_max` 和 `zfs_arc_min`。将此小节与 `-d` 结合使用，会为每个可调参数附加简要说明。

### zil

ZFS 意图日志的统计信息：提交的事务计数、发往稳定存储的刷新请求，以及普通 vdev 与任何独立日志（SLOG）设备之间的字节级划分。

## 选项

### `-a`、`--alternate`

为 tunables 和 SPL 小节使用替代布局。

### `-d`、`--description`

在每个可调参数和 SPL 条目旁打印简短说明。

### `-h`、`--help`

显示帮助信息。

### `-g`、`--graph`

打印当前 ARC 使用情况的 ASCII 图表并退出。

### `-p 页`、`--page 页`

按旧版页码打印小节。**不推荐使用**；请改用 `-s`。

### `-r`、`--raw`

以最少的格式化输出所有可用数据。

### `-s 小节`、`--section 小节`

仅打印指定名称的小节。有效的小节名称列表见“说明”一节。

## 环境

### Linux

统计信息读取自 `/proc/spl/kstat/zfs/`。

### FreeBSD

统计信息通过 sysctl(3) 从 `vfs.zfs` 和 `kstat.zfs.misc` 树中读取。必须安装 `py-sysctl` 包，`zarcsummary` 才能正常工作。

## 退出状态

`zarcsummary` 成功时退出状态为 0，出错时大于 0。

## 示例

打印完整报告：

```sh
# zarcsummary
```

仅显示 ARC 大小和命中率信息：

```sh
# zarcsummary -s arc
```

以可视化方式概览 ARC 的健康状况：

```sh
# zarcsummary -g
```

搜索所有包含 “hit” 的统计信息：

```sh
# zarcsummary -r | grep hit
```

查看所有可调参数及其说明：

```sh
# zarcsummary -d -s tunables
```

## 参考文献

zarcstat(1)、zpool-status(8)

## 历史

`zarcsummary` 最初是名为 `arc_summary` 的 Perl 脚本，由 Ben Rockwood 于 2008 年为 Solaris 编写。Martin Matuska 于 2010 年将其移植到 FreeBSD，随后由 Jason J. Hellenthal 接手维护。Scot W. Stevenson 于 2017 年贡献了用 Python 3 完成的彻底重写，引入了 `-g`、`-r`、`-s` 选项以及基于小节的输出布局。2025 年，为与 OpenZFS 的命令命名约定保持一致，该工具由 `arc_summary` 更名为 `zarcsummary`。

## 作者

本手册页由 Christos Longros `<chris.longros@gmail.com>` 编写。

2026 年 3 月 14 日  Debian
