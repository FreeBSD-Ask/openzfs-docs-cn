# zpool-scrub(8)

## 名称

`zpool-scrub` — 开始或继续 ZFS 存储池的 scrub

## 概述

```sh
zpool scrub [-w] [-t] [-C | [-S 日期] [-E 日期]] -a | 池名…
```

```sh
zpool scrub -e [-w] -a | 池名…
```

```sh
zpool scrub -p -a | 池名…
```

```sh
zpool scrub -s -a | 池名…
```

## 说明

开始一次 scrub，或继续一个已暂停的 scrub。普通 scrub 会检查指定池中的所有数据，并验证每个块的校验和。彻底 scrub（thorough scrub）还会在读取块时对其进行解密和/或解压。对于冗余（镜像、raidz 或 draid）设备，ZFS 会自动修复 scrub 过程中发现的任何损坏。`zpool status` 命令会报告 scrub 的进度，并在完成后汇总 scrub 的结果。

scrub 与 resilver 是非常相似的操作。区别在于，resilver 只检查 ZFS 已知过期的数据（例如在向镜像中新建设备或替换现有设备时），而 scrub 检查所有数据，以发现因硬件故障或磁盘失效导致的静默错误。

对带有加密文件系统的池执行 scrub 时，普通的校验和验证无需加载密钥，但彻底 scrub 需要（参见下文的 `-t`）。

如果未加载密钥，并且检测到无法修复的校验和错误，则文件名无法包含在 `zpool status -v` 的详细错误报告中。

由于 scrub 与 resilver 都是 I/O 密集型操作，ZFS 只允许同时进行其中一个。

scrub 分为两部分：元数据扫描与块 scrub。元数据扫描会把块排序成较大的连续区间，从而在发起 scrub I/O 时能更高效地从磁盘读取。

如果 scrub 已暂停，`zpool scrub` 会将其继续。如果 resilver 正在进行，ZFS 在 resilver 完成前不允许开始 scrub。

注意，由于在线系统上池数据会不断变化，scrub 与 resilver 的进度有可能超过 100%。在此期间不会提供完成时间估计。

## 选项

### `-a`、`-all`

在所有池上开始、暂停（`-p`）或停止（`-s`）scrub。在多个池上启动 scrub 会给系统带来相当大的负载与内存压力，因此执行此操作应谨慎。

### `-s`

停止 scrub。除 `-a` 外，不能与其他选项组合使用。

### `-p`

暂停 scrub。除 `-a` 外，不能与其他选项组合使用。scrub 的暂停状态与进度会定期同步到磁盘。如果在 scrub 暂停期间系统重启或池被导出，即使之后重新导入，scrub 仍会保持暂停，直到被继续。继续后，scrub 会从上次检查点到磁盘的位置接着执行。要继续已暂停的 scrub，请执行 `zpool scrub`。scrub 会以其开始时的模式（普通或彻底）继续。要继续已暂停的错误 scrub，请执行 `zpool scrub -e`。

### `-w`

等待 scrub 完成后再返回。

### `-e`

只 scrub `zpool status -v` 所报告的已知数据错误涉及的文件。使用此选项要求池在启用 `head_errlog` 特性的情况下至少被 scrub 过一次。错误 scrub 不能与其他 scrub 或 resilver 同时进行，也不能在 scrub 暂停时运行。此选项不能与 `-C`、`-p`、`-s` 或 `-t` 组合使用。

### `-C`

从上次保存的 txg 继续 scrub（参见 zpool 的 `last_scrubbed_txg` 属性）。不能与 `-S`、`-E`、`-e`、`-p` 或 `-s` 组合使用。可以与彻底 scrub（`-t`）组合使用。

### `-t`

彻底 scrub。会使 scrub 在读取块时对其进行解密与解压，从而发现一类罕见的损坏——校验和与数据相符，但解密和/或解压失败。对于加密数据集，必须加载密钥才能执行彻底 scrub。如果在彻底 scrub 期间密钥未加载或被卸载，对于密钥未加载的加密块，scrub 会退回到普通 scrub。不能与 `-e`、`-p` 或 `-s` 组合使用。可以与 `-a`、`-w`、`-C` 或开始/结束日期选项（`-S`/`-E`）组合使用。

### `-S date`、`-E date`

允许为在这些日期之间创建的块指定日期范围。

* `-S`：定义开始日期。如果未指定，scrub 会从池创建时开始。
* `-E`：定义结束日期。如果未指定，scrub 会一直到最新的数据。

提供的日期应采用以下格式：“YYYY-MM-DD HH:MM”。其中：

* “YYYY” 是年份。
* “MM” 是月份的数字表示形式。
* “DD” 是月份中的天数。
* “HH” 是小时。
* “MM” 是分钟。

小时与分钟参数可以省略。时间应以机器本地时区提供。指定的日期早于启用此特性的时间时，scrub 会从池创建的日期开始。系统时钟的大幅或不连续变动（向前或向后）可能使开始和/或结束日期与池事务组的对应关系发生偏移。因此，scrub 可能不会覆盖预期的日期。

不能与 `-C` 组合使用。

## 示例

### 示例 1：正在执行 scrub 的池的状态

```sh
# zpool status
  ...
  scan: scrub in progress since Sun Jul 25 16:07:49 2021
        403M / 405M scanned at 100M/s, 68.4M / 405M issued at 10.0M/s
        0B repaired, 16.91% done, 00:00:04 to go
  ...
```

其中，引用 403M 文件数据的元数据已按 100M/s 完成扫描，而其中的 68.4M 文件数据已按 10.0M/s 顺序完成 scrub。

## 定期 scrub

在使用 systemd 的机器上，可以按池启用 scrub 定时器。提供了 `weekly` 与 `monthly` 定时器单元。

```sh
systemctl enable zfs-scrub-weekly@rpool.timer --now
systemctl enable zfs-scrub-monthly@otherpool.timer --now
```

## 参考文献

systemd.timer(5)、zpool-iostat(8)、zpool-resilver(8)、zpool-status(8)

2026 年 5 月 1 日
