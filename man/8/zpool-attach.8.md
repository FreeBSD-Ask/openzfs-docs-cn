# zpool-attach(8)

## 名称

`zpool-attach` — 把新设备附加到现有 ZFS vdev

## 概述

```sh
zpool attach [-fsw] [-o 属性=值] 池名 vdev 新设备
```

## 说明

把 `new_device` 附加到现有 `vdev`。具体行为取决于现有 `vdev` 是 RAID-Z 设备还是镜像/普通设备。

如果现有 vdev 是镜像或普通设备（例如指定为 `sda` 或“mirror-7”），新设备将与现有 vdev 组成镜像，随后启动 resilver；resilver 完成后，新设备将贡献额外的冗余。如果 `vdev` 目前不属于镜像配置，`device` 会自动变成 `device` 与 `new_device` 组成的双向（two-way）镜像。如果 `vdev` 已是双向镜像，附加 `new_device` 将创建三向（three-way）镜像，依此类推。无论哪种情况，`new_device` 都会立即开始 resilver，任何正在进行的 scrub 都会被取消。

如果现有 vdev 是 RAID-Z 设备（例如指定为“raidz2-0”），新设备将成为该 RAID-Z 组的一部分。系统会启动“RAID-Z 扩容”（raidz expansion），扩容完成后，新设备将为该 RAID-Z 组贡献额外的空间。扩容需要读取 RAID-Z 组中所有现有磁盘上已分配的空间，并将其重写到该 RAID-Z 组中的新磁盘上（包括新加入的 `device`）。其进度可以用 `zpool status` 监控。

扩容期间与扩容之后，数据冗余都得以保持。如果扩容进行期间有磁盘发生故障，扩容将暂停，直到 RAID-Z vdev 的健康状况恢复（例如更换故障磁盘并等待重建完成）。扩容不会改变不发生数据丢失所能容忍的故障数量（例如 RAID-Z2 扩容后仍是 RAID-Z2）。一个 RAID-Z vdev 可以多次扩容。每次扩容都会使用 ZFS 在每块磁盘开头附近预留的 3.5 MiB 启动区作为暂存空间，该区域必须为扩容后的 vdev 中的每块磁盘存放一个扇区：例如，在 `ashift=16` 下，RAID-Z vdev 最多可扩容到 56 块磁盘。

扩容完成后，旧块仍保持其原有的数据与校验比（例如 5 宽 RAID-Z2 有 3 块数据与 2 块校验），但分布在更大的磁盘集合中。可以用 zfs-rewrite(8) 按新比例重写这些块。新块将按新的数据与校验比写入（例如 5 宽 RAID-Z2 扩容一次到 6 宽后，有 4 块数据与 2 块校验）。但是，vdev 假定的校验比不会改变，因此根据 `zfs list`、`df`、`ls -s` 及类似工具的报告，新写入块的空间可能略少于预期。

扩容结束时，系统会在整个池范围内启动 scrub，以验证扩容过程中复制的所有块的校验和。

### `-f`

强制使用 `new_device`，即使它看起来正在使用中。并非所有 vdev 都能以这种方式覆盖。

### `-o property=value`

设置给定的池属性。可设置的有效属性列表参见 zpoolprops(7) 手册页。目前唯一支持的属性是 `ashift`。

### `-s`

附加到镜像或普通 vdev 时，`new_device` 会按顺序重建，以尽快恢复冗余。顺序重建期间不验证校验和，因此 resilver 完成后会启动 scrub。

### `-w`

等待 `new_device` 完成 resilver 或扩容后才返回。

## 示例

### 示例 1：把非镜像的 ZFS 存储池变为镜像

以下命令通过把第二块设备 `sdb` 附加到现有单块设备 `sda`，将其转换为镜像：

```sh
# zpool attach tank sda sdb
```

### 示例 2：用一块额外磁盘扩容 RAID-Z vdev

以下命令把 `sdg` 添加到 `tank` 中现有的 `raidz2-0` vdev，将 6 宽 RAID-Z2 变成 7 宽 RAID-Z2：

```sh
# zpool attach tank raidz2-0 sdg
```

进度由 `zpool status` 报告。此操作需要 `raidz_expansion` 池特性，且 `sdg` 必须至少与该 vdev 中现有最小磁盘一样大。旧块保持其原有的数据与校验比，只有扩容后写入的块使用新比例。

## 参考文献

zfs-rewrite(8)、zpool-add(8)、zpool-detach(8)、zpool-import(8)、zpool-initialize(8)、zpool-online(8)、zpool-replace(8)、zpool-resilver(8)

2026 年 10 月 13 日

