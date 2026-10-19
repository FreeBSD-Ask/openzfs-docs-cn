# zpool_influxdb(8)

## 名称

`zpool_influxdb` — 以 InfluxDB line protocol 格式收集 ZFS 存储池统计信息

## 概述

```sh
zpool_influxdb [-e | --execd] [-n | --no-histogram] [-s | --sum-histogram-buckets] [-t | --tags 键=值[,键=值]…] [池名]
```

## 说明

`zpool_influxdb` 从存储池生成兼容 InfluxDB line protocol 的指标。与 zpool 命令一样，`zpool_influxdb` 会读取当前的池状态与统计信息。与面向人类的 zpool 命令不同，`zpool_influxdb` 会以 InfluxDB line protocol 格式化输出。预期用途是作为指标采集器或聚合器（如 Telegraf）的插件。

默认情况下，`zpool_influxdb` 以 InfluxDB line protocol 格式打印池指标与状态。会打印所有存储池，类似于 zpool status 命令。提供池名则会将输出限定为指定的池。

## 选项

### `-e`、`--execd`

以与 Telegraf 的 `execd` 插件兼容的守护进程模式运行。在此模式下，标准输入每出现一个换行符，就会对所有池采样一次。

### `-n`、`--no-histogram`

不打印延迟与 I/O 大小直方图。这可以减少数据总量，但应当考虑延迟与 I/O 大小分布所能带来的洞察价值。得到的值适合用 Grafana 的 heatmap 插件绘图。

### `-s`、`--sum-histogram-buckets`

累加各桶的值。默认情况下不累加，显示的原始数据与 `zpool iostat` 所显示的一致。这对 Grafana 的 heatmap 插件效果很好。对桶求和会产生类似于 Prometheus 直方图的输出。

### `-t`、`--tags 键=值[,键=值]…`

将指定的标签添加到标签集中。不执行任何合理性检查。有关标签中所用特殊字符转义的详情，参见 InfluxDB Line Protocol 格式文档。

### `-h`、`--help`

打印用法摘要。

## 参考文献

zpool-iostat(8)、zpool-status(8)、[InfluxDB](https://github.com/influxdata/influxdb)、[Telegraf](https://github.com/influxdata/telegraf)、[Grafana](https://grafana.com)、[Prometheus](https://prometheus.io)

2021 年 5 月 26 日
