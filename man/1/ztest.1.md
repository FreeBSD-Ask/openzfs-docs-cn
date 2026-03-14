# ztest(1)


`ztest` — 由 ZFS 开发者编写的 ZFS 单元测试工具

```sh
ztest [-VEG] [-v 每个 vdev 的数量] [-s 每个 vdev 的大小] [-a 对齐偏移] [-m 镜像副本数] [-r raidz 磁盘数 / draid 磁盘数] [-R RAID 校验数] [-K RAID 类型] [-D draid 数据数] [-S draid 备用盘数] [-C vdev 类状态] [-d 数据集] [-t 线程数] [-g 聚合块阈值] [-i 初始化池次数] [-k 杀死比例] [-p 池名] [-T 时间] [-z ZIL 失败率]
```

```sh
ztest -X [-VG] [-s 每个 vdev 的大小] [-a 对齐偏移] [-r raidz 磁盘数] [-R RAID 校验数] [-d 数据集] [-t 线程数]
```

## 说明

`ztest` 是由 ZFS 开发者编写的 ZFS 单元测试工具。该工具与 ZFS 功能开发同步进行，作为针对每日构建的众多回归测试之一，每晚运行一次。随着 ZFS 功能的增加，单元测试也会相应加入到 `ztest` 中。此外，还有一个独立的测试开发团队编写并执行更多功能性和压力测试。

在默认情况下，`ztest` 会运行十分钟，还会使用块文件（存储在 `/tmp`）来创建池，而不是使用物理磁盘。块文件使 `ztest` 能够灵活操作 zpool 组件，而无需大型硬件配置。但如果你的 `/tmp` 目录不大，存放块文件可能不适用。

默认模式为非详细输出。这就是为什么运行上述命令时，`ztest` 会静默执行五分钟。可以使用选项 `-V` 丰富工具的详细输出。可添加多个 `-V` 选项，添加的越多，`ztest` 输出的信息就越丰富。

`ztest` 运行结束后，你会发现许多 `ztest.*` 文件留在了系统中。在运行完成后，就可以放心地删除这些文件。但在运行过程中不应删除这些文件。你可以通过 `-E` 选项在下一次 `ztest` 运行中复用这些文件。

## 选项

### `-h`、`-?`、`--help`

打印帮助摘要

### `-v`、`--vdevs=`

vdev 数量（默认值: `5`）

### `-s`、`--vdev-size=`

每个 vdev 的大小（默认值: `64M`）

### `-a`、`--alignment-shift=`

测试使用的对齐偏移（默认值: `9`，使用 `0` 表示随机）

### `-m`、`--mirror-copies=

镜像副本数量（默认值: 2）

### `-r`、`--raid-disks=`

raidz/draid 磁盘数量（raidz 默认 4，draid 默认 16）

### `-R`、`--raid-parity=`

Raid 奇偶校验数量（raidz & draid）（默认值: 1）

### `-K`、`--raid-kind=`

RAID 配置类型：raidz、eraidz、draid、random（默认值: random）。random 模式下类型将在 raidz、eraidz（可扩展 raidz）和 draid 之间随机切换

### `-D`、`--draid-data=`

dRAID 冗余组中数据盘数量（默认值: `4`）

### `-S`、`--draid-spares=`

dRAID 分布式备用盘数量（默认值: `1`）

### `-d`、`--datasets=`

数据集数量（默认值: `7`）

### `-t`、`--threads=`

线程数量（默认值: `23`）

### `-g`、`--gang-block-threshold=`

Gang 块阈值（默认值: `32K`）

### `-i`、`--init-count=`

池初始化次数（默认值: `1`）

### `-k`、`--kill-percentage=`

终止百分比（默认值: `70%`）

### `-p`、`--pool-name=`

池名称（默认值: `ztest`）

### `-f`、`--vdev-file-directory=`

vdev 文件目录（默认值: `/tmp`）

### `-M`、`--multi-host`

多主机模式；模拟在远程主机导入池

### `-E`、`--use-existing-pool`

使用现有池（而非创建新池）

### `-T`、`--run-time=`

总测试运行时间（默认值: `300s`）

### `-P`、`--pass-time=`

每轮测试时间（默认值: `60s`）

### `-F`、`--freeze-loops=`

`spa_freeze()` 最大循环次数（默认值: `50`）

### `-B`、`--alt-ztest=`

`ztest` 的备用 （“兼容”）路径，用于初始化池，并在随机的一半时间内执行测试。parallel 库目录将被添加到 `LD_LIBRARY_PATH` 前面；例如，指定 `-B ./chroots/lenny/usr/bin/ztest` 时，会加载 `./chroots/lenny/usr/lib`。

### `-C`、`--vdev-class-state=`

vdev 分配类状态：on | off | random（默认值: random）

### `-o`、`--option=可调参数=值…`

设置指定可调参数的值

### `-G`、`--dump-debug`

在错误退出前转储 zfs_dbgmsg 缓冲区

### `-V`、`--verbose`

增加详细信息（可多次使用，可提升更多详细程度）

### `-X`、`--raidz-expansion`

执行专门的 raidz 扩展测试

## 示例

要将块文件的位置从 `/tmp` 覆盖为其他路径，可以使用 `-f` 选项：

```sh
# ztest -f /
```

要了解 `ztest` 实时测试内容，可以尝试如下操作：

```sh
# ztest -f / -VVV
```

也许你想让 `ztest` 运行更长时间？只需使用 `-T` 选项，然后以秒为单位指定运行时长，如下所示：

```sh
# ztest -f / -V -T 120
```

## 环境变量

### `ZFS_HOSTID=id`

使用 *id* 代替 SPL hostid 来标识此主机。此设置主要用于 `ztest`，但该环境变量会影响那些使用 libzpool 的工具，包括 zpool(8)。由于内核不知晓此设置，除 `ztest` 之外的工具使用结果是未定义的。

### `ZFS_STACK_SIZE=堆栈大小`

将默认栈大小限制为 **堆栈大小** 字节，用于检测和调试内核栈溢出。默认值为 *32K*，是 Linux 内核默认栈大小 *16K*  的两倍。实际上，需要将栈大小设置略高一些，因为内核与用户空间的栈使用差异可能导致伪栈溢出（尤其在启用调试时）。指定值会向上取整至 `PTHREAD_STACK_MIN` 的下限，这是用户空间执行 NULL 过程所需的最小栈大小。

默认情况下，栈大小限制为 *256K*。

## 参考文献

zdb(1)、zfs(1)、zpool(1)、spl(4)

2025 年 7 月 12 日 Debian
