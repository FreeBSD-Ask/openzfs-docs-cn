# raidz_test(1)

## 名称

`raidz_test` — RAIDZ 实现验证与基准测试工具

## 概述

```sh
raidz_test [-StBevTD] [-a 对齐位数 (ashift)] [-o ZIO 偏移量 (zio_off_shift)] [-d RAIDZ 数据盘数量 (raidz_data_disks)] [-s ZIO 大小偏移 (zio_size_shift)] [-r 重排偏移 (reflow_offset)]
```

## 说明

该工具旨在运行所有受支持的 RAIDZ 实现并验证所有方法的结果。它还包含参数扫描选项，可验证影响 RAID-Z 块的所有参数（如 ashift 大小、数据偏移、数据大小等）。该工具还支持使用 `-B` 选项进行的基准测试模式。

## 选项

### `-h`

打印帮助摘要。

### `-a` ashift（默认值：9）

设置 ashift 值。

### `-o` zio_off_shift（默认值：0）

每个 RAID-Z 块的 ZIO 偏移量。实际偏移量为 `2^zio_off_shift`。

### `-d` raidz_data_disks（默认值：8）

RAID-Z 数据盘数量。额外的磁盘用于奇偶校验。

### `-s` zio_size_shift（默认值：19）

RAID-Z 块的数据大小。实际大小为 `2^zio_size_shift`。

### `-r` reflow_offset（默认值：uint max）

设置 RAID-Z 扩展偏移。扩展的 RAID-Z 映射分配函数会根据此值生成不同的映射配置。

### `-S`（Sweep）

在验证 RAID-Z 实现的同时扫描参数空间。此选项会穷尽 `-aods` 选项的大部分有效值，运行时间较长。

### `-t`（Timeout）

扫描测试的总时间（秒）。实际运行时间可能更长。

### `-B`（Benchmark）

对所有实现进行基于单盘数据大小递增的基准测试，结果以每盘吞吐量（MiB/s）表示。

### `-e`（Expansion）

使用扩展的 RAID-Z 映射分配函数。

### `-v`（Verbose）

增加输出详细程度。

### `-T`（Test the test）

调试选项：使所有测试失败，用于检查测试是否能正确验证位精确性。

### `-D`（Debug）

调试选项：在收到 SIGSEGV 或 SIGABRT 信号时附加 gdb 调试器。

## 参考资料

ztest(1)

2021 年 5 月 26 日 Debian
