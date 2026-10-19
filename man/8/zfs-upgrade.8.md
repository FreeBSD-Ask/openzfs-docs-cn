# zfs-upgrade(8)

## 名称

`zfs-upgrade` — 管理 ZFS 文件系统的磁盘格式版本

## 概述

```sh
zfs upgrade
```

```sh
zfs upgrade -v
```

```sh
zfs upgrade [-r] [-V version] -a | 文件系统
```

## 说明

### `zfs upgrade`

列出并非最新版本的文件系统。

### `zfs upgrade -v`

列出当前支持的文件系统版本。

### `zfs upgrade [-r] [-V version] -a | filesystem`

将文件系统升级到新的磁盘格式版本。升级完成后，这些文件系统将无法在运行旧版本 ZFS 的系统上访问。由这些文件系统的新快照生成的 `zfs send` 流，也无法在运行旧版本 ZFS 的系统上访问。

一般情况下，文件系统版本与池版本相互独立。有关 ZFS 存储池特性的信息，参见 zpool-features(7)。

在某些情况下，文件系统版本与池版本相互关联，必须先升级池版本，才能升级文件系统版本。

#### `-V version`

升级到 `version` 指定的版本。如果未指定，则升级到最新版本。此选项只能用于增大版本号，并且最多只能增大到此版本 ZFS 所支持的最新版本。

#### `-a`

升级所有已导入的池中的所有文件系统。

#### `filesystem`

升级指定的文件系统。

#### `-r`

升级指定的文件系统及其所有后代文件系统。

## 参考文献

zpool-upgrade(8)

2022 年 7 月 11 日
