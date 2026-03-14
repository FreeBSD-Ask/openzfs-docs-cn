# zarcstat(1)


## 名称

`zarcstat` — 报告 ZFS ARC 和 L2ARC 统计信息

## 概述

```sh
zarcstat [-havxp] [-f 字段[,字段…]] [-o 文件] [-s 字符串] [interval] [count]
```

## 说明

`zarcstat` 将以类似 vmstat 的方式打印 ZFS ARC 和 L2ARC 的各种统计信息。

### c

ARC 目标大小

### dh%

按需命中百分比

### di%

按需 I/O 命中百分比

### dm%

按需未命中百分比

### ddh%

按需数据命中百分比

### ddi%

按需数据 I/O 命中百分比

### ddm%

按需数据未命中百分比

### dmh%

按需元数据命中百分比

### dmi%

按需元数据 I/O 命中百分比

### dmm%

按需元数据未命中百分比

### mfu

MFU 列表每秒命中次数

### mh%

元数据命中百分比

### mi%

元数据 I/O 命中百分比

### mm%

元数据未命中百分比

### mru

MRU 列表每秒命中次数

### ph%

预取命中百分比

### pi%

预取 I/O 命中百分比

### pm%

预取未命中百分比

### pdh%

预取数据命中百分比

### pdi%

预取数据 I/O 命中百分比

### pdm%

预取数据未命中百分比

### pmh%

预取元数据命中百分比

### pmi%

预取元数据 I/O 命中百分比

### pmm%

预取元数据未命中百分比

### dhit

每秒需求命中次数

### dioh

每秒需求 I/O 命中次数

### dmis

每秒需求未命中次数

### ddhit

每秒需求数据命中次数

### ddioh

每秒需求数据 I/O 命中次数

### ddmis

每秒需求数据未命中次数

### dmhit

每秒需求元数据命中次数

### dmioh

每秒需求元数据 I/O 命中次数

### dmmis

每秒需求元数据未命中次数

### hit%

ARC 命中百分比

### hits

每秒 ARC 命中次数

### ioh%

ARC I/O 命中百分比

### iohs

每秒 ARC I/O 命中次数

### mfug

每秒 MFU 幽灵列表命中次数

### mhit

每秒元数据命中次数

### mioh

每秒元数据 I/O 命中次数

### miss

每秒 ARC 未命中次数

### mmis

每秒元数据未命中次数

### mrug

每秒 MRU 幽灵列表命中次数

### phit

每秒预取命中次数

### pioh

每秒预取 I/O 命中次数

### pmis

每秒预取未命中次数

### pdhit

每秒预取数据命中次数

### pdioh

每秒预取数据 I/O 命中次数

### pdmis

每秒预取数据未命中次数

### pmhit

每秒预取元数据命中次数

### pmioh

每秒预取元数据 I/O 命中次数

### pmmis

每秒预取元数据未命中次数

### read

每秒 ARC 总访问次数

### time

当前时间

### size

ARC 大小

### arcsz

size 的别名

### unc

每秒未缓存列表命中次数

### dread

每秒需求访问次数

### ddread

每秒需求数据访问次数

### dmread

每秒需求元数据访问次数

### eskip

每秒 evict_skip 次数

### miss%

ARC 未命中百分比

### mread

每秒元数据访问次数

### pread

每秒预取访问次数

### pdread

每秒预取数据访问次数

### pmread

每秒预取元数据访问次数

### l2hit%

L2ARC 访问命中百分比

### l2hits

每秒 L2ARC 命中次数

### l2miss

每秒 L2ARC 未命中次数

### l2read

每秒 L2ARC 总访问次数

### l2pref

每秒 L2ARC 分配的预取大小

### l2pref%

L2ARC 分配的预取大小百分比

### l2mfu

每秒 L2ARC MFU 分配大小

### l2mfu%

L2ARC MFU 分配大小百分比

### l2mru

每秒 L2ARC MRU 分配大小

### l2mru%

L2ARC MRU 分配大小百分比

### l2data

每秒 L2ARC 数据（缓冲内容）分配大小

### l2data%

L2ARC 数据（缓冲内容）分配大小百分比

### l2meta

每秒 L2ARC 元数据（缓冲内容）分配大小

### l2meta%

L2ARC 元数据（缓冲内容）分配大小百分比

### l2size

L2ARC 大小

### mtxmis

每秒互斥锁未命中次数

### l2bytes

每秒从 L2ARC 读取的字节数

### l2wbytes

每秒写入到 L2ARC 的字节数

### l2miss%

L2ARC 访问未命中百分比

### l2asize

L2ARC 实际（压缩后）大小

### cmpsz

压缩大小

### cmpsz%

压缩大小百分比

### ovhsz

开销大小

### ovhsz%

开销大小百分比

### bonsz

Bonus 大小

### bonsz%

Bonus 大小百分比

### dnosz

Dnode 大小

### dnosz%

Dnode 大小百分比

### dbusz

Dbuf 大小

### dbusz%

Dbuf 大小百分比

### hdrsz

Header 大小

### hdrsz%

Header 大小百分比

### l2hsz

L2 header 大小

### l2hsz%

L2 header 大小百分比

### abdsz

ABD 块浪费大小

### abdsz%

ABD 块浪费大小百分比

### datatg

ARC 数据目标

### datatg%

ARC 数据目标百分比

### datasz

ARC 数据大小

### datasz%

ARC 数据大小百分比

### metatg

ARC 元数据目标

### metatg%

ARC 元数据目标百分比

### metasz

ARC 元数据大小

### metasz%

ARC 元数据大小百分比

### anosz

匿名大小

### anosz%

匿名大小百分比

### anoda

匿名数据大小

### anoda%

匿名数据大小百分比

### anome

匿名元数据大小

### anome%

匿名元数据大小百分比

### anoed

匿名可回收数据大小

### anoed%

匿名可回收数据大小百分比

### anoem

匿名可回收元数据大小

### anoem%

匿名可回收元数据大小百分比

### mfutg

MFU 目标

### mfutg%

MFU 目标百分比

### mfudt

MFU 数据目标

### mfudt%

MFU 数据目标百分比

### mfumt

MFU 元数据目标

### mfumt%

MFU 元数据目标百分比

### mfusz

MFU 大小

### mfusz%

MFU 大小百分比

### mfuda

MFU 数据大小

### mfuda%

MFU 数据大小百分比

### mfume

MFU 元数据大小

### mfume%

MFU 元数据大小百分比

### mfued

MFU 可回收数据大小

### mfued%

MFU 可回收数据大小百分比

### mfuem

MFU 可回收元数据大小

### mfuem%

MFU 可回收元数据大小百分比

### mfugsz

MFU ghost 大小

### mfugd

MFU ghost 数据大小

### mfugm

MFU ghost 元数据大小

### mrutg

MRU 目标

### mrutg%

MRU 目标百分比

### mrudt

MRU 数据目标

### mrudt%

MRU 数据目标百分比

### mrumt

MRU 元数据目标

### mrumt%

MRU 元数据目标百分比

### mrusz

MRU 大小

### mrusz%

MRU 大小百分比

### mruda

MRU 数据大小

### mruda%

MRU 数据大小百分比

### mrume

MRU 元数据大小

### mrume%

MRU 元数据大小百分比

### mrued

MRU 可回收数据大小

### mrued%

MRU 可回收数据大小百分比

### mruem

MRU 可回收元数据大小

### mruem%

MRU 可回收元数据大小百分比

### mrugsz

MRU ghost 大小

### mrugd

MRU ghost 数据大小

### mrugm

MRU ghost 元数据大小

### uncsz

未缓存大小

### uncsz%

未缓存大小百分比

### uncda

未缓存数据大小

### uncda%

未缓存数据大小百分比

### uncme

未缓存元数据大小

### uncme%

未缓存元数据大小百分比

### unced

未缓存可回收数据大小

### unced%

未缓存可回收数据大小百分比

### uncem

未缓存可回收元数据大小

### uncem%

未缓存可回收元数据大小百分比

### grow

ARC 增长（grow）已禁用

### need

需要 ARC 回收

### free

ARC 理解的可用内存量，包括页面缓存中可回收的内存。由于 ARC 尝试保持 avail 大于零，观察 avail 通常比 free 更有意义。

### avail

ARC 理解的可用内存量，比 free 略少。可能暂时为负，此时 ARC 会减小目标大小 c。

## 选项

### `-a`

显示所有可能的统计信息。

### `-f`

仅显示指定字段。支持的统计字段见 DESCRIPTION。

### `-h`

显示帮助信息。

### `-o`

将统计结果写入文件，而非标准输出。

### `-p`

禁用数值字段的自动缩放（用于原始、机器可解析的值）。

### `-s`

使用指定分隔符显示数据（默认：两个空格）。

### `-x`

显示扩展统计信息（等同于 `-f time,mfu,mru,mfug,mrug,eskip,mtxmis,dread,pread,read`）。

### `-v`

显示字段标题和定义。

## 操作数

支持如下操作数：

### interval

指定采样间隔（秒）。

### count

仅显示某指定次数的报告。


2024 年 9 月 19 日 Debian

