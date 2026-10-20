# zpool-get(8)

## 名称

`zpool-get` — 获取 ZFS 存储池的属性

`zpool-set(8)` 是 `zpool-get(8)` 的历史别名。

## 概述

```sh
zpool get [-Hp] [-j [--json-int, --json-pool-key-guid]] [-o field[,field]…] all | property[,property]… [pool…]
```

```sh
zpool get [-Hp] [-j [--json-int]] [-o field[,field]…] all | property[,property]… pool [all-vdevs | vdev…]
```

```sh
zpool set property=value pool
```

```sh
zpool set property=value pool vdev
```

## 说明

### `zpool get [-Hp] [-j [--json-int, --json-pool-key-guid]] [-o field[,field]…] all | property[,property]… [pool…]`

获取指定存储池的给定属性列表（使用 `all` 时为全部属性）。这些属性以以下字段显示：

* `name` — 存储池的名称。
* `property` — 属性名。
* `value` — 属性值。
* `source` — 属性来源，`default` 或 `local`。

更多可用池属性的信息参见 zpoolprops(7) 手册页。

#### `-j`、`--json [--json-int, --json-pool-key-guid]`

以 JSON 格式显示属性列表。指定 `--json-int` 可以在 JSON 输出中以整数而不是字符串形式显示数字。指定 `--json-pool-key-guid` 可以用池 GUID 作为池对象的键，而不是用池名。

#### `-H`

脚本模式。不显示表头，各字段用单个制表符而不是任意空白分隔。

#### `-o field`

要显示的列的逗号分隔列表（默认值: `name`、`property`、`value`、`source`）。

#### `-p`

以可解析的（精确）数值显示数字。

### `zpool get [-Hp] [-j [--json-int]] [-o field[,field]…] all | property[,property]… pool [all-vdevs | vdev…]`

获取指定池中指定 vdev 的给定属性列表（使用 `all` 时为全部属性，使用 `all-vdevs` 时为全部 vdev）。这些属性以以下字段显示：

* `name` — vdev 的名称。
* `property` — 属性名。
* `value` — 属性值。
* `source` — 属性来源，`default` 或 `local`。

更多可用池属性的信息参见 vdevprops(7) 手册页。

#### `-j`、`--json [--json-int]`

以 JSON 格式显示属性列表。指定 `--json-int` 可以在 JSON 输出中以整数而不是字符串形式显示数字。

#### `-H`

脚本模式。不显示表头，各字段用单个制表符而不是任意空白分隔。

#### `-o field`

要显示的列的逗号分隔列表（默认值: `name`、`property`、`value`、`source`）。

#### `-p`

以可解析的（精确）数值显示数字。

### `zpool set property=value pool`

在指定的池上设置给定的属性。可以设置哪些属性以及可接受的取值，参见 zpoolprops(7) 手册页。

### `zpool set property=value pool vdev`

在指定池中的指定 vdev 上设置给定的属性。可以设置哪些属性以及可接受的取值，参见 vdevprops(7) 手册页。

## 参考文献

vdevprops(7)、zpool-features(7)、zpoolprops(7)、zpool-list(8)

2024 年 10 月 12 日

