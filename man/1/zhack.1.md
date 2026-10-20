# zhack(1)



## 名称

`zhack` — libzpool 调试工具


## 说明

该工具能直接向 ZFS 池写入配置更改，这非常危险，可能导致数据损坏。

## 概述

### `zhack feature stat pool`

列出功能标志。

### `zhack feature enable [-d description] [-r] pool guid`

向池中添加一个由 guid 唯一标识的新功能，guid 的格式与 zfs(8) 用户属性相同。

“描述”是便于理解新功能的简要说明。

`-r` 标志表示，即使系统不支持该 guid 功能，也可以用只读模式安全打开池。

### `zhack feature ref [-d|-m] pool guid`

增加池中 guid 功能的引用计数。

`-d` 标志则用于减少池中 guid 功能的引用计数。

`-m` 标志表示该 guid 功能现在是读取池元对象集（Metaobject Set, MOS）所必需的。

### `zhack label repair [-cu] device`

根据选项修复指定设备的标签。

可以组合使用标志，从而同时发挥各标志的作用。

* `-c` 标志将修复损坏的标签校验和
* `-u` 标志将恢复已分离设备上的标签

示例：

```sh
zhack label repair -cu device
```

将修复校验和并重新附加设备。

### `zhack mmp reclaim pool`

导入一个存储池：其 uberblock 声明（claim）无法到达配置仍期望存在的每一个镜像 leg；随后将不可达的 leaf 标记为离线，使常规导入得以成功，最后再次导出该存储池。

该命令只针对一种情形：某台主机连同其所连接的镜像 leg 一同故障，而现存的标签仍将这些 leg 描述为健康，于是之后每次导入都要求向它们写入，但无人能够完成。

**这本身并不能使操作变得安全**。若某台活动主机所拥有的 leg 从此处全部不可见，任何写入与读取方案都无法检测到它，本命令会将存储池从该主机上夺走。运行本命令之前，请隔离（fence）故障主机，或以其他方式证明其已断电。

活动检查本身并未改变：可达 leg 所允许的每一次写入、等待以及重新读取仍会照常进行，因此若存在与本主机共享任一 leg 的竞争主机，仍会被检测到并拒绝导入。只有声明所要求的写入次数被降低，且仅针对本主机无法打开的镜像 leg，这些 leg 随后会被标记为离线。

存储池会保持导出状态，此后可在这些 leaf 离线的情况下降级导入。硬件恢复后，可用 zpool-online(8) 将每个 leaf 重新上线。持有某些数据唯一副本的 leaf 无法置于离线：系统会报告该 leaf 并使其保持在线，来自其他主机的导入仍会被拒绝。对于未设置 **multihost** 的存储池，不会将任何 leaf 标记为离线，因为此类存储池不运行声明，常规导入本就能成功。log、cache 和 spare vdev 的 leaf 不会被改动，因为声明不会向它们写入。

### `zhack metaslab leak [-f] pool`

将由 zdb 生成的碎片化配置应用到指定的存储池。

`-f` 标志将强制应用该配置，即使存储池中的 vdev 与碎片化配置的 metaslab 数量不一致。

### `zhack mos scan pool`

扫描存储池 MOS 中泄漏的对象，并报告可回收的候选对象。仅当对象既未被引用又为空时，才算是候选对象：即条目数为零、且没有任何 DSL 目录引用的 DSL 目录克隆 ZAP（DSL dir clones ZAP），或没有任何分配、且不被 DTL、metaslab、obsolete、checkpoint 或日志空间映射消费者引用的空间映射对象。未被引用但非空的对象会被报告并跳过。本子命令为只读操作，适用于已导入的存储池。

### `zhack mos reclaim [-w] pool`

回收 `mos scan` 识别为候选对象的泄漏 MOS 对象。不带 `-w` 时为干运行，不会做任何更改。带上 `-w` 时，候选对象会在同步上下文中被释放，且该操作会记录到存储池历史中。存储池必须处于导出状态。

### `zhack mos leak [-w] [-c count] [-s count] pool`

在可丢弃的存储池上创建合成的泄漏 MOS 对象，用于测试 `mos scan` 和 `mos reclaim`。`-c` 和 `-s` 标志分别设置要注入的泄漏 DSL 克隆映射与泄漏空间映射的数量，默认各注入一个。不带 `-w` 时为干运行，不会做任何更改。存储池必须处于导出状态。

## 全局选项

以下选项可在任何 `zhack` 子命令之前传入：

### `-c cachefile`

从“缓存文件”读取存储池的配置，默认为 `/etc/zfs/zpool.cache`。

### `-d dir`

在“目录”中搜索存储池成员。可指定多次。

### `-o var=value`

将给定的可调参数设置为指定值。


## 示例

```sh
# zhack feature stat tank
for_read_obj:
	org.illumos:lz4_compress = 0
for_write_obj:
	com.delphix:async_destroy = 0
	com.delphix:empty_bpobj = 0
descriptions_obj:
	com.delphix:async_destroy = Destroy filesystems asynchronously.
	com.delphix:empty_bpobj = Snapshots use less space.
	org.illumos:lz4_compress = LZ4 compression algorithm support.

# zhack feature enable -d 'Predict future disk failures.' tank com.example:clairvoyance
# zhack feature ref tank com.example:clairvoyance
```

在确认对端主机已宕机后，恢复其与镜像 leg 一同失效的存储池：

```sh
# zpool import -f tank
cannot import 'tank': the multihost claim could not be written to a device
the pool configuration expects to be present.
If the device is permanently gone, recover with 'zhack mmp reclaim'.
# zhack mmp reclaim tank
tank: marked absent leaf 5646371977210937898 offline
# zpool import tank
# zpool online tank /dev/disk/by-id/...
```

## 参考文献

ztest(1)、zpool-features(7)、zpoolprops(7)、zfs(8)、zpool-import(8)、zpool-online(8)

2026 年 8 月 9 日  Debian



