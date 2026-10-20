# zpool-list(8)

## 名称

`zpool-list` — 列出 ZFS 存储池的信息

## 概述

```sh
zpool list [-HgLpPv] [-j [--json-int, --json-pool-key-guid]] [-o 属性[,属性]…] [-T u|d] [池名]… [间隔 [次数]]
```

## 说明

列出给定池及其健康状况与空间使用情况。如果未指定池名，则列出当前已导入的所有池。要列出可供导入的池，参见 zpool-import(8)。指定 `interval` 时，信息每隔 `interval` 秒打印一次，直到被终止。如果指定了 `count`，则打印 `count` 份报告后命令退出。

### `-j`、`--json [--json-int, --json-pool-key-guid]`

以 JSON 格式显示池的列表。指定 `--json-int` 时以整数格式显示数字，而不是字符串。指定 `--json-pool-key-guid` 时以池 GUID 作为池对象的键，而不是池名。

### `-g`

显示 vdev 的 GUID 而非通常的设备名。这些 GUID 可以在 zpool detach/offline/remove/replace 命令中代替设备名使用。

### `-H`

脚本模式。不显示表头，并改用单个制表符而不是任意数量的空格分隔字段。

### `-o 属性`

要显示的属性列表，以逗号分隔。有效属性列表参见 zpoolprops(7) 手册页。默认列表为 `name`、`size`、`allocated`、`free`、`checkpoint`、`expandsize`、`fragmentation`、`capacity`、`dedupratio`、`health`、`altroot`。

### `-L`

显示 vdev 的真实路径，解析所有符号链接。无论打开设备时使用的是 `/dev/disk` 下的哪个路径，都可以用它查找当前的块设备名。

### `-p`

以可解析（精确）值显示数字。

### `-P`

显示 vdev 的完整路径，而不是只有路径的最后一个组成部分。可以与 `-L` 标志配合使用。

### `-T u|d`

显示时间戳。指定 `u` 使用时间内部表示的可打印形式，参见 time(1)。指定 `d` 使用标准日期格式，参见 date(1)。

### `-v`

详细统计信息。除池范围的统计信息外，还会报告池中各个 vdev 的使用统计信息。

## 示例

### 示例 1：列出可用的 ZFS 存储池

以下命令列出系统上所有可用的池。在本例中，池 `zion` 因缺少设备而处于故障状态。该命令的结果与以下内容类似：

```sh
# zpool list
NAME    SIZE  ALLOC   FREE  EXPANDSZ   FRAG    CAP  DEDUP  HEALTH  ALTROOT
rpool  19.9G  8.43G  11.4G         -    33%    42%  1.00x  ONLINE  -
tank   61.5G  20.0G  41.5G         -    48%    32%  1.00x  ONLINE  -
zion       -      -      -         -      -      -      -  FAULTED -
```

### 示例 2：显示设备上扩展的空间

以下命令显示池 `data` 的详细信息。该池由单个 raidz vdev 组成，其中一个设备的容量增加了 10 GiB。在此示例中，在 raidz vdev 下的所有设备都完成扩展之前，池将无法利用这部分额外容量。

```sh
# zpool list -v data
NAME         SIZE  ALLOC   FREE  EXPANDSZ   FRAG    CAP  DEDUP  HEALTH  ALTROOT
data        23.9G  14.6G  9.30G         -    48%    61%  1.00x  ONLINE  -
  raidz1    23.9G  14.6G  9.30G         -    48%
    sda         -      -      -         -      -
    sdb         -      -      -       10G      -
    sdc         -      -      -         -      -
```

### 示例 3：以 JSON 格式列出可用的存储池

以下命令以 JSON 格式列出系统上所有可用的池。

```sh
# zpool list -j | jq
{
  "output_version": {
    "command": "zpool list",
    "vers_major": 0,
    "vers_minor": 1
  },
  "pools": {
    "tank": {
      "name": "tank",
      "type": "POOL",
      "state": "ONLINE",
      "guid": "15220353080205405147",
      "txg": "2671",
      "spa_version": "5000",
      "zpl_version": "5",
      "properties": {
        "size": {
          "value": "111G",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "allocated": {
          "value": "30.8G",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "free": {
          "value": "80.2G",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "checkpoint": {
          "value": "-",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "expandsize": {
          "value": "-",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "fragmentation": {
          "value": "0%",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "capacity": {
          "value": "27%",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "dedupratio": {
          "value": "1.00x",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "health": {
          "value": "ONLINE",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "altroot": {
          "value": "-",
          "source": {
            "type": "DEFAULT",
            "data": "-"
          }
        }
      }
    }
  }
}
```

## 参考文献

zpool-import(8)、zpool-status(8)

2024 年 10 月 12 日
