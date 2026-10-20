# zpool-trim(8)

## 名称

`zpool-trim` — 对 ZFS 存储池中的空闲空间发起 TRIM

## 概述

```sh
zpool trim [-dw] [-r 速率] [-c | -s] [-a | 池名] [设备…]
```

## 说明

立即对池中的所有空闲空间执行一次按需 TRIM 操作。此操作会通知底层存储设备池中所有已不再分配的数据块，使精简置备设备能够回收这些空间。

无论 `autotrim` 池属性如何设置，都可以手动发起按需 TRIM 操作。有关可执行 TRIM 的 vdev 设备类型，请参见 zpoolprops(7) 中 `autotrim` 属性的说明。

### `-a`、`-all`

对所有存储池执行 TRIM 操作。

### `-d`、`-secure`

发起安全 TRIM。执行安全 TRIM 时，设备保证已擦除被 TRIM 块上存储的数据。这要求设备提供相应支持，并非所有 SSD 都支持。

### `-r`、`-rate 速率`

控制 TRIM 操作的执行速率。未指定此选项时，TRIM 会以尽可能快的速度执行。速率以字节每秒为单位表示，按 vdev 分别应用，且可以为每个叶子 vdev 设置不同的值。

### `-c`、`-cancel`

取消对指定设备的 TRIM；如果未指定设备，则取消对所有符合条件设备的 TRIM。如果一个或多个目标设备无效或当前未在执行 TRIM，该命令将失败，且不会对任何设备执行取消操作。

### `-s`、`-suspend`

暂停对指定设备的 TRIM；如果未指定设备，则暂停对所有符合条件设备的 TRIM。如果一个或多个目标设备无效或当前未在执行 TRIM，该命令将失败，且不会对任何设备执行暂停操作。随后可以在相关目标设备上运行不带任何标志的 `zpool trim` 以恢复 TRIM。

### `-w`、`-wait`

等待设备完成 TRIM 后再返回。

## 定期 TRIM

在使用 systemd 的机器上，可以按池启用 TRIM 定时器。系统提供了 `weekly` 与 `monthly` 两个定时器单元。

```sh
systemctl enable zfs-trim-weekly@rpool.timer --now
```

```sh
systemctl enable zfs-trim-monthly@otherpool.timer --now
```

## 参考文献

systemd.timer(5)、zpoolprops(7)、zpool-initialize(8)、zpool-wait(8)

2025 年 7 月 30 日
