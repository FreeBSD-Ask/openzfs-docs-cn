# zhack(1)



## 名称 

`zhack` — libzpool 调试工具


## 说明

该工具能直接向 ZFS 池写入配置更改，这非常危险，可能导致数据损坏。

## 概述

### `zhack feature stat 存储池`

列出功能标志。

### `zhack feature enable [-d 描述] [-r] 存储池 guid`

向池中添加一个由 guid 唯一标识的新功能，guid 的格式与 zfs(8) 用户属性相同。

“描述”是便于理解新功能的简要说明。

`-r` 标志表示，即使系统不支持该 guid 功能，也可以用只读模式安全打开池。

### `zhack feature ref [-d|-m] 存储池 guid`

增加池中 guid 功能的引用计数。

`-d` 标志则用于减少池中 guid 功能的引用计数。

`-m` 标志表示该 guid 功能现在是读取池元对象集（Metaobject Set, MOS）所必需的。

### `zhack label repair [-cu] 设备`

根据选项修复指定设备的标签。

可以组合使用标志，将同时执行它们的功能。

* `-c` 标志将修复损坏的标签校验和
* `-u` 标志将恢复已分离设备上的标签

示例：

```sh
zhack label repair -cu 设备
```

将修复校验和并重新挂接设备。

### `zhack metaslab leak [-f] 存储池`

将由 zdb 生成的碎片化配置应用到指定的存储池。

`-f` 标志将强制应用该配置，即使存储池中的 vdevs 与碎片化配置的 metaslab 数量不一致。

## 全局选项

以下选项可在任何 `zhack` 子命令之前传入：

### `-c 缓存文件` 

从“缓存文件”读取存储池的配置，默认为 `/etc/zfs/zpool.cache`。

### `-d 目录`

在“目录”中搜索存储池成员。可指定多次。

### `-o 可调参数=值` 

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

# zhack feature enable -d 'Predict future disk failures.' tank com.示例:clairvoyance
# zhack feature ref tank com.示例:clairvoyance
```

## 参考文献

ztest(1)、zpool-features(7)、zfs(8)

2023 年 5 月 3 日  Debian



