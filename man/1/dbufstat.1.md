# dbufstat(1)

## 名称

`dbufstat` — 显示 DMU 缓冲缓存的统计信息

## 概述

```sh
dbufstat [-bdhnrtvx] [-f 字段[,字段…]] [-F 字段=值[,…]] [-i 文件] [-o 文件] [-s 分隔符]
```

## 说明

`dbufstat` 显示 DMU（数据管理单元，Data Management Unit）缓冲缓存的统计信息，该缓存也称为 dbuf 缓存。这些信息读取自 `dbufs` kstat（Linux 上为 `/proc/spl/kstat/zfs/dbufs`，FreeBSD 上为 `kstat.zfs.misc.dbufs`）。

`dbufstat` 能以三种模式显示数据：

### `-b`

为每个单独的 dbuf（缓冲区）显示一张信息表。这是最详细的视图。

### `-d`

为每个 dnode 显示一张信息表（默认模式）。属于同一 dnode 的多个 dbuf 会被聚合。

### `-t`

为每种 dnode 类型显示一张信息表。同一类型的多个 dnode 会被聚合。

以下字段可供显示。并非所有字段都兼容所有模式；使用 `-v` 可以查看各模式下不兼容的字段。

### pool

存储池名称。

### objset

数据集标识号。

### object

对象编号。

### level

缓冲区的间接层级。

### blkid

缓冲区的块编号。

### offset

缓冲区在对象中的偏移量。

### dbsize

缓冲区大小。

### usize

附加用户数据的大小。

### meta

此缓冲区是否为元数据。

### state

缓冲区的状态（read、cached 等）。

### dbholds

缓冲区上的持有数。

### dbc

此缓冲区是否位于 dbuf 缓存中。

### list

此缓冲区位于哪个 ARC 列表中。

### atype

ARC 头部类型（data 或 metadata）。

### flags

ARC 读取标志。

### count

ARC 数据计数。

### asize

此 ARC 缓冲区的大小。

### access

此 ARC 缓冲区上次访问的时间。

### mru

位于 ARC 的 MRU 列表时的命中次数。

### gmru

位于 ARC 的 MRU 幽灵列表时的命中次数。

### mfu

位于 ARC 的 MFU 列表时的命中次数。

### gmfu

位于 ARC 的 MFU 幽灵列表时的命中次数。

### l2

位于 L2ARC 时的命中次数。

### l2_dattr

L2ARC 磁盘地址/偏移量。

### l2_asize

L2ARC 已分配的大小（取决于压缩情况）。

### l2_comp

缓冲区所用的 L2ARC 压缩算法。

### aholds

此 ARC 缓冲区上的持有数。

### dtype

Dnode 类型。

### btype

Bonus 缓冲区类型。

### data_bs

数据块大小。

### meta_bs

元数据块大小。

### bsize

Bonus 缓冲区大小。

### lvls

间接层级数量。

### dholds

dnode 上的持有数。

### blocks

已分配的块数量。

### dsize

Dnode 大小。

### cached

所有块缓存的字节数。

### direct

直接块缓存的字节数。

### indirect

间接块缓存的字节数。

### bonus

Bonus 缓冲区缓存的字节数。

### spill

spill 块缓存的字节数。

## 选项

### `-b`

为每个单独的 dbuf 显示信息。

### `-d`

为每个 dnode 显示信息（默认）。

### `-f 字段[,字段…]`

仅显示指定的字段。

### `-F 字段=值[,…]`

按字段值或正则表达式筛选输出。可以逗号分隔列表的形式指定多个筛选条件。

### `-h`

显示帮助信息。

### `-i 文件`

从指定文件而非 `dbufs` kstat 重定向输入。

### `-n`

在输出中排除表头。

### `-o 文件`

将输出重定向到指定文件而非标准输出。

### `-r`

显示原始值。指定两次时，还会显示数字形式的类型和压缩标识符，而不是名称。

### `-s 分隔符`

用自定义字符或字符串覆盖默认的字段分隔符（两个空格）。

### `-t`

为每种 dnode 类型显示信息。

### `-v`

列出所有可能的字段标题、定义以及各模式下的不兼容项。

### `-x`

显示扩展统计信息。

## 示例

显示按 dnode 划分的统计信息（默认模式）：

```sh
# dbufstat -d
       pool  objset  object                      dtype  cached
      zroot      30   34466  DMU_OT_DIRECTORY_CONTENTS    240K
      zroot      30       0               DMU_OT_DNODE     14M
      zroot      30   36343  DMU_OT_DIRECTORY_CONTENTS    1024
      zroot      30   32921 DMU_OT_PLAIN_FILE_CONTENTS    2.5K
```

显示按类型划分的统计信息：

```sh
# dbufstat -t
       pool  objset                      dtype  cached
      zroot      30  DMU_OT_DIRECTORY_CONTENTS    1.9M
      zroot      30               DMU_OT_DNODE     14M
      zroot      30 DMU_OT_PLAIN_FILE_CONTENTS    8.4M
      zroot       0           DMU_OT_DSL_PROPS    2.6M
```

显示按缓冲区划分的统计信息：

```sh
# dbufstat -b
       pool  objset  object  level  blkid  offset  dbsize
      zroot      30   34466      1      0       0    128K
      zroot      30       0      0    292    4.6M     16K
      zroot      30   34466      0      8    128K     16K
      zroot       0       4      0      0       0    128K
```

显示每个 dnode 的指定字段：

```sh
# dbufstat -d -f pool,object,objset,dsize,cached
```

显示按类型划分的统计信息，并以逗号分隔输出：

```sh
# dbufstat -t -s ","
```

显示按缓冲区划分的扩展统计信息，并应用筛选条件：

```sh
# dbufstat -bx -F dbc=1,pool=zroot
```

## 参考文献

zarcstat(1)、zfs(8)、zpool-iostat(8)

## 作者

本手册页由 Christos Longros `<chris.longros@gmail.com>` 编写。

2026 年 3 月 19 日  Debian
