# zpool-replace(8)

## 名称

`zpool-replace` — 在 ZFS 存储池中用新设备替换旧设备

## 概述

```sh
zpool replace [-fsw] [-o property=value] 池名 设备 [新设备]
```

## 说明

用 `new-device` 替换 `device`。这等同于附加 `new-device`、等待其完成 resilver，然后分离 `device`。任何正在进行的 scrub 都会被取消。

`new-device` 的大小必须大于或等于镜像或 raidz 配置中所有设备的最小尺寸。

如果池不具备冗余，则必须指定 `new-device`。如果未指定 `new-device`，它默认为 `device`。这种替换形式在现有磁盘故障并被物理更换后很有用。在这种情况下，新磁盘可能与旧设备具有相同的 `/dev` 路径，即使它实际上是另一块磁盘。ZFS 能够识别这一点。

### `-f`

强制使用 `new-device`，即使它看起来正在使用中。并非所有设备都能以这种方式覆盖。

### `-o property=value`

设置给定的池属性。可设置的有效属性列表参见 zpoolprops(7) 手册页。目前唯一支持的属性是 `ashift`。

### `-s`

对 `new-device` 进行顺序重建，以尽快恢复冗余。顺序重建过程中不验证校验和，因此 resilver 完成时会启动一次 scrub。顺序重建不支持 raidz 配置。

### `-w`

等待替换完成后再返回。

## 参考文献

zpool-detach(8)、zpool-initialize(8)、zpool-online(8)、zpool-resilver(8)

2022 年 7 月 11 日
