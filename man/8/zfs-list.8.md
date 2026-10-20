# zfs-list(8)

## 名称

`zfs-list` — 列出 ZFS 数据集的属性

## 概述

```sh
zfs list [-r|-d 深度] [-Hp] [-j [--json-int]] [-o 属性[,属性]…] [-s 属性]… [-S 属性]… [-t 类型[,类型]…] [文件系统|卷|快照…]
```

## 说明

默认显示所有文件系统与卷，包含以下字段：`name`、`used`、`available`、`referenced`、`mountpoint`。

当 `listsnapshots` 池属性为 `on`（默认为 `off`），或指定了 `-t snapshot` 或 `-t all` 选项时，会显示快照。

## 选项

### `-H`

用于脚本模式。不打印表头，并且字段以单个制表符而不是任意空白分隔。

### `-j`、`--json [--json-int]`

以 JSON 格式打印输出。指定 `--json-int` 时，JSON 输出中的数字以整数格式而不是字符串形式打印。

### `-d depth`

递归显示数据集的任何子级，将递归限制为 `depth` 层。深度为 `1` 时只显示该数据集及其直接子级。

### `-o property`

以逗号分隔的要显示的属性的列表。每个属性必须是以下之一：

* zfsprops(7) 的“原生属性”一节所述的属性之一
* 一个用户属性
* 值 `name`，用于显示数据集名称
* 值 `space`，用于显示文件系统与卷的空间使用属性。这是指定 `-o name,avail,used,usedsnap,usedds,usedrefreserv,usedchild -t filesystem,volume` 的快捷方式

### `-p`

以可解析的（精确）值显示数字。

### `-r`

递归显示命令行中给定的数据集的任何子级。

### `-s property`

用于按属性值升序排序输出列的属性。该属性必须是 zfsprops(7) 的属性一节所述的属性之一，或值 `name`（按数据集名称排序）。可以通过多个 `-s` 或 `-S` 选项指定多个属性来协同排序。多个 `-s` 与 `-S` 选项按从左到右的顺序求值，以按优先级递减的顺序提供排序键。属性类型的排序行为如下：

* 数值类型按数值大小排序。
* 字符串类型按字母顺序排序。
* 不适合行排序的类型会将该行排到最底部，无论指定的排序方式如何。

如果未指定排序列，或者如果两行输出在所有指定列上的排序结果相同，则数据集与书签按名称排序，而快照先按所属数据集的名称、再按创建时间排序。未指定排序列但列出了快照时，此默认行为会使快照按创建时间的先后归组到其数据集之下。

### `-S property`

与 `-s` 相同，但按 `property` 降序排序。

### `-t type`

以逗号分隔的要显示的类型的列表，其中 `type` 是 `filesystem`、`snapshot`、`volume`、`bookmark` 或 `all` 之一。例如，指定 `-t snapshot` 只显示快照。`fs`、`snap` 或 `vol` 可用作 `filesystem`、`snapshot` 或 `volume` 的别名。

## 示例

### 示例 1：列出 ZFS 数据集

以下命令列出系统中所有处于活动状态的文件系统与卷。当 `listsnaps=on` 时会显示快照。默认值为 `off`。有关池属性的更多信息，参见 zpoolprops(7)。

```sh
# zfs list
NAME                      USED  AVAIL  REFER  MOUNTPOINT
pool                      450K   457G    18K  /pool
pool/home                 315K   457G    21K  /export/home
pool/home/anne             18K   457G    18K  /export/home/anne
pool/home/bob             276K   457G   276K  /export/home/bob
```

### 示例 2：以 JSON 格式列出 ZFS 文件系统与快照

```sh
# zfs list -j -t filesystem,snapshot | jq
{
  "output_version": {
    "command": "zfs list",
    "vers_major": 0,
    "vers_minor": 1
  },
  "datasets": {
    "pool": {
      "name": "pool",
      "type": "FILESYSTEM",
      "pool": "pool",
      "properties": {
        "used": {
          "value": "290K",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "available": {
          "value": "30.5G",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "referenced": {
          "value": "24K",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "mountpoint": {
          "value": "/pool",
          "source": {
            "type": "DEFAULT",
            "data": "-"
          }
        }
      }
    },
    "pool/home": {
      "name": "pool/home",
      "type": "FILESYSTEM",
      "pool": "pool",
      "properties": {
        "used": {
          "value": "48K",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "available": {
          "value": "30.5G",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "referenced": {
          "value": "24K",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "mountpoint": {
          "value": "/mnt/home",
          "source": {
            "type": "LOCAL",
            "data": "-"
          }
        }
      }
    },
    "pool/home/bob": {
      "name": "pool/home/bob",
      "type": "FILESYSTEM",
      "pool": "pool",
      "properties": {
        "used": {
          "value": "24K",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "available": {
          "value": "30.5G",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "referenced": {
          "value": "24K",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "mountpoint": {
          "value": "/mnt/home/bob",
          "source": {
            "type": "INHERITED",
            "data": "pool/home"
          }
        }
      }
    },
    "pool/home/bob@v1": {
      "name": "pool/home/bob@v1",
      "type": "SNAPSHOT",
      "pool": "pool",
      "dataset": "pool/home/bob",
      "snapshot_name": "v1",
      "properties": {
        "used": {
          "value": "0B",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "available": {
          "value": "-",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "referenced": {
          "value": "24K",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        },
        "mountpoint": {
          "value": "-",
          "source": {
            "type": "NONE",
            "data": "-"
          }
        }
      }
    }
  }
}
```

## 参考文献

zfsprops(7)、zfs-get(8)

2025 年 8 月 25 日
