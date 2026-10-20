# zfs-set(8)

## 名称

`zfs-set` — 设置 ZFS 数据集的属性

`zfs-get(8)` 是 `zfs-set(8)` 的历史别名。

`zfs-inherit(8)` 是 `zfs-set(8)` 的历史别名。

## 概述

```sh
zfs set [-u] 属性=值 [属性=值]… 文件系统|卷|快照…
```

```sh
zfs get [-r|-d 深度] [-Hp] [-j [--json-int]] [-o 字段[,字段]…] [-s 来源[,来源]…] [-t 类型[,类型]…] all|属性[,属性]… [文件系统|卷|快照|书签…]
```

```sh
zfs inherit [-rS] 属性 文件系统|卷|快照…
```

## 说明

### `zfs set [-u] property=value [property=value]… filesystem|volume|snapshot…`

只有部分属性可以编辑。有关哪些属性可以设置以及可接受的值的更多信息，参见 zfsprops(7)。数值可以指定为精确值，也可以使用后缀 `B`、`K`、`M`、`G`、`T`、`P`、`E`、`Z`（分别表示字节、千字节、兆字节、吉字节、太字节、拍字节、艾字节、泽字节）的易读形式。用户属性可以设置在快照上。有关更多信息，参见 zfsprops(7) 的“用户属性”一节。

#### `-u`

更新 `mountpoint`、`sharenfs`、`sharesmb` 属性，但不挂载或共享该数据集。

### `zfs get [-r|-d depth] [-Hp] [-j [--json-int]] [-o field[,field]…] [-s source[,source]…] [-t type[,type]…] all|property[,property]… [filesystem|volume|snapshot|bookmark…]`

显示给定数据集的属性。如果未指定数据集，则该命令显示系统中所有数据集的属性。对于每个属性，显示以下列：

* `name` — 数据集名称
* `property` — 属性名称
* `value` — 属性值
* `source` — 属性来源：`local`、`default`、`inherited`、`temporary`、`received` 或 `-`（无）
* `received` — 属性的已接收值（如果有）。默认不显示此列。

默认显示 `name`、`property`、`value` 与 `source` 列，不过可以通过 `-o` 选项控制这一点。此命令接受以逗号分隔的属性列表，详见 zfsprops(7) 的“原生属性”与“用户属性”两节。

值 `all` 可用于显示适用于给定数据集类型（`filesystem`、`volume`、`snapshot` 或 `bookmark`）的所有属性。

#### `-j`、`--json [--json-int]`

以 JSON 格式显示输出。指定 `--json-int` 时，JSON 输出中的数字以整数格式而不是字符串形式显示。

#### `-H`

以便于脚本解析的形式显示输出。省略所有表头，并且字段以单个制表符而不是任意数量的空白分隔。

#### `-d depth`

递归显示数据集的任何子级，将递归限制为 `depth` 层。深度为 `1` 时只显示该数据集及其直接子级。

#### `-o field`

以逗号分隔的要显示的列的列表。支持的字段为 `name`、`property`、`value`、`received`、`source`，或 `all`（选择全部五列）。默认值为 `name`、`property`、`value`、`source`。

#### `-p`

以可解析的（精确）值显示数字。

#### `-r`

递归显示任何子级的属性。

#### `-s source`

以逗号分隔的要显示的来源的列表。来源不在此列表中的属性会被忽略。每个来源必须是以下之一：`local`、`default`、`inherited`、`temporary`、`received` 或 `none`。默认值为所有来源。

#### `-t type`

以逗号分隔的要显示的类型的列表，其中 `type` 是 `filesystem`、`snapshot`、`volume`、`bookmark` 或 `all` 之一。`fs`、`snap` 或 `vol` 可用作 `filesystem`、`snapshot` 或 `volume` 的别名。

### `zfs inherit [-rS] property filesystem|volume|snapshot…`

清除指定的属性，使其从某个祖先数据集继承；如果没有祖先数据集设置该属性，则恢复为默认值；如果存在已接收值，则配合 `-S` 选项恢复为已接收值。有关默认值列表以及哪些属性可以继承的详情，参见 zfsprops(7)。

#### `-r`

为所有子级递归继承给定的属性。

#### `-S`

将属性恢复为已接收值（如果存在）；否则，对于不可继承的属性，恢复为默认值；否则，按未指定 `-S` 选项的情况处理。

## 示例

### 示例 1：创建 ZFS 文件系统层级

以下命令创建名为 `pool/home` 的文件系统与名为 `pool/home/bob` 的文件系统。父文件系统的挂载点设置为 `/export/home`，子文件系统会自动继承该挂载点。

```sh
# zfs create pool/home
# zfs set mountpoint=/export/home pool/home
# zfs create pool/home/bob
```

### 示例 2：禁用与启用文件系统压缩

以下命令对 `pool/home` 下的所有文件系统禁用 `compression` 属性。下一条命令为 `pool/home/anne` 显式启用 `compression`。

```sh
# zfs set compression=off pool/home
# zfs set compression=on pool/home/anne
```

### 示例 3：为 ZFS 文件系统设置配额

以下命令为 `pool/home/bob` 设置 50 GB 的配额：

```sh
# zfs set quota=50G pool/home/bob
```

### 示例 4：列出 ZFS 属性

以下命令列出 `pool/home/bob` 的所有属性：

```sh
# zfs get all pool/home/bob
NAME           PROPERTY              VALUE                  SOURCE
pool/home/bob  type                  filesystem             -
pool/home/bob  creation              Tue Jul 21 15:53 2009  -
pool/home/bob  used                  21K                    -
pool/home/bob  available             20.0G                  -
pool/home/bob  referenced            21K                    -
pool/home/bob  compressratio         1.00x                  -
pool/home/bob  mounted               yes                    -
pool/home/bob  quota                 20G                    local
pool/home/bob  reservation           none                   default
pool/home/bob  recordsize            128K                   default
pool/home/bob  mountpoint            /pool/home/bob         default
pool/home/bob  sharenfs              off                    default
pool/home/bob  checksum              on                     default
pool/home/bob  compression           on                     local
pool/home/bob  atime                 on                     default
pool/home/bob  devices               on                     default
pool/home/bob  exec                  on                     default
pool/home/bob  setuid                on                     default
pool/home/bob  readonly              off                    default
pool/home/bob  zoned                 off                    default
pool/home/bob  snapdir               hidden                 default
pool/home/bob  acltype               off                    default
pool/home/bob  aclmode               discard                default
pool/home/bob  aclinherit            restricted             default
pool/home/bob  canmount              on                     default
pool/home/bob  xattr                 on                     default
pool/home/bob  copies                1                      default
pool/home/bob  version               4                      -
pool/home/bob  utf8only              off                    -
pool/home/bob  normalization         none                   -
pool/home/bob  casesensitivity       sensitive              -
pool/home/bob  vscan                 off                    default
pool/home/bob  nbmand                off                    default
pool/home/bob  sharesmb              off                    default
pool/home/bob  refquota              none                   default
pool/home/bob  refreservation        none                   default
pool/home/bob  primarycache          all                    default
pool/home/bob  secondarycache        all                    default
pool/home/bob  usedbysnapshots       0                      -
pool/home/bob  usedbydataset         21K                    -
pool/home/bob  usedbychildren        0                      -
pool/home/bob  usedbyrefreservation  0                      -
```

以下命令获取单个属性的值：

```sh
# zfs get -H -o value compression pool/home/bob
on
```

以下命令以 JSON 格式递归获取单个属性的值：

```sh
# zfs get -j -r mountpoint pool/home | jq
{
  "output_version": {
    "command": "zfs get",
    "vers_major": 0,
    "vers_minor": 1
  },
  "datasets": {
    "pool/home": {
      "name": "pool/home",
      "type": "FILESYSTEM",
      "pool": "pool",
      "createtxg": "10",
      "properties": {
        "mountpoint": {
          "value": "/pool/home",
          "source": {
            "type": "DEFAULT",
            "data": "-"
          }
        }
      }
    },
    "pool/home/bob": {
      "name": "pool/home/bob",
      "type": "FILESYSTEM",
      "pool": "pool",
      "createtxg": "1176",
      "properties": {
        "mountpoint": {
          "value": "/pool/home/bob",
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

以下命令列出 `pool/home/bob` 所有具有本地设置的属性：

```sh
# zfs get -r -s local -o name,property,value all pool/home/bob
NAME           PROPERTY              VALUE
pool/home/bob  quota                 20G
pool/home/bob  compression           on
```

### 示例 5：继承 ZFS 属性

以下命令使 `pool/home/bob` 与 `pool/home/anne` 从其父级继承 `checksum` 属性。

```sh
# zfs inherit checksum pool/home/bob pool/home/anne
```

### 示例 6：设置用户属性

以下示例为数据集设置用户自定义的 `com.example:department` 属性：

```sh
# zfs set com.example:department=12345 tank/accounting
```

### 示例 7：在 ZFS 文件系统上设置 sharenfs 属性选项

以下命令演示如何设置 `sharenfs` 属性选项，以允许一组 IP 地址进行读写访问，并为 `tank/home` 文件系统上的系统“neo”开放 root 访问：

```sh
# zfs set sharenfs='rw=@123.123.0.0/16:[::1],root=neo' tank/home
```

如果你使用 DNS 解析主机名，请指定完全限定的主机名。

## 参考文献

zfsprops(7)、zfs-list(8)

2026 年 3 月 15 日
