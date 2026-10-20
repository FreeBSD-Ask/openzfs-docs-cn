# zfs-share(8)

## 名称

`zfs-share` — 共享与取消共享 ZFS 文件系统

## 概述

```sh
zfs share [-l] -a | 文件系统
```

```sh
zfs unshare -a | 文件系统 | 挂载点
```

## 说明

### `zfs share [-l] -a | filesystem`

共享可用的 ZFS 文件系统。

#### `-l`

在挂载加密文件系统的过程中加载其密钥。这等同于在挂载前对每个加密根执行 `zfs load-key`。注意，如果某个文件系统的 `keylocation` 为 `prompt`，这会使终端在索取密钥后交互式阻塞。

#### `-a`

共享所有可用的 ZFS 文件系统。作为引导过程的一部分自动调用。

#### `filesystem`

按照 `sharenfs` 与 `sharesmb` 属性共享指定的文件系统。设置了 `sharenfs` 或 `sharesmb` 属性时，文件系统即被共享。

### `zfs unshare -a | filesystem | mountpoint`

取消共享当前已共享的 ZFS 文件系统。

#### `-a`

取消共享所有可用的 ZFS 文件系统。作为关机过程的一部分自动调用。

#### `filesystem | mountpoint`

取消共享指定的文件系统。该命令也可以接受系统中某个已共享 ZFS 文件系统的路径。

## 参考文献

exports(5)、smb.conf(5)、zfsprops(7)

2022 年 7 月 11 日
