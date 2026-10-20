# zpool-upgrade(8)

## 名称

`zpool-upgrade` — 管理 ZFS 存储池的版本与特性标志

## 概述

```sh
zpool upgrade
```

```sh
zpool upgrade -v
```

```sh
zpool upgrade [-V version] -a | 池名…
```

## 说明

### `zpool upgrade`

显示未启用全部受支持特性的存储池，以及使用旧版 ZFS 版本号格式化的存储池。这些池可以继续使用，但某些特性可能不可用。使用 `zpool upgrade -a` 可以在所有池上启用所有特性（受 `-o compatibility` 属性限制）。

### `zpool upgrade -v`

显示此版本 ZFS 支持的旧版 ZFS 版本。有关此版本 ZFS 所支持特性的说明，参见 zpool-features(7)。

### `zpool upgrade [-V version] -a | pool …`

在给定池上启用所有受支持的特性。

如果池通过 `-o compatibility` 属性指定了兼容性特性集，则只有所有请求的兼容性集中都存在的特性才会被启用。如果此属性设为 `legacy`，则不会执行升级。

一旦完成升级，该池将无法在不支持特性标志的系统上访问。有关与那些支持特性标志、但不支持该池已启用的全部特性的系统之间的兼容性详情，参见 zpool-features(7)。

#### `-a`

在所有池上启用所有受支持的特性（如有指定的兼容性集，则来自这些兼容性集）。

#### `-V version`

升级到指定的旧版本。如果指定此选项，则不会在池上启用任何特性。此选项只能用于把版本号提升到最后一个受支持的旧版本号。

## 示例

### 示例 1：将所有 ZFS 存储池升级到当前版本

以下命令把所有 ZFS 存储池升级到软件的当前版本：

```sh
# zpool upgrade -a
This system is currently running ZFS version 2.
```

## 参考文献

zpool-features(7)、zpoolconcepts(7)、zpoolprops(7)、zpool-history(8)

2022 年 7 月 11 日
