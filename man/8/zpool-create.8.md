# zpool-create(8)

## 名称

`zpool-create` — 创建 ZFS 存储池

## 概述

```sh
zpool create [-dfn] [-m 挂载点] [-o 属性=值]… [-o feature@feature=值] [-o compatibility=off|legacy|文件[,文件]…] [-O 文件系统属性=值]… [-R 根目录] [-t 临时池名] 池名 vdev…
```

## 说明

创建一个新存储池，其中包含命令行上指定的虚拟设备（vdev）。vdev 规格说明参见 zpoolconcepts(7) 的“虚拟设备（vdevs）”一节。

池名必须以字母开头，且只能包含字母数字字符以及下划线（`_`）、连字符（`-`）、冒号（`:`）、空格（` `）和句点（`.`）。池名 `mirror`、`raidz`、`draid`、`spare` 和 `log` 为保留名，以 `mirror`、`raidz`、`draid` 和 `spare` 开头的名称同样保留。

该命令会尝试验证指定的每个设备均可访问，且当前未被其他子系统使用。但此检查并不足够稳健，即使设置了 `multihost=enabled`，也无法检测在多个池中同时尝试使用同一个新设备的情况。管理员必须确保 `zpool replace`、`zpool create`、`zpool add` 或 `zpool labelclear` 的任意组合的并行调用不会引用同一设备。在两个池中使用同一设备将导致池损坏。

某些使用情况（例如设备当前已被挂载，或被指定为专用转储设备）会使该设备永远无法被 ZFS 使用。其他使用情况（例如设备上已存在 UFS 文件系统）则可以用 `-f` 覆盖。

该命令还会检查池的冗余策略是否一致。除非指定 `-f`，否则在单个池中混合冗余与非冗余存储，或混合使用磁盘与文件，都会报错。除非指定 `-f`，否则在单个 raidz 或镜像组中使用大小不同的设备也会被视为错误。

除非指定 `-R` 选项，否则默认挂载点为 `/pool`。挂载点必须不存在或为空，否则根数据集将无法挂载。可以用 `-m` 选项覆盖此行为。

默认情况下，新池会启用所有支持的 feature flags（特性标志）。`-d` 选项与 `-o compatibility` 属性（例如 `-o compatibility=2020`）可用于限制启用的特性标志，从而使该池可以在其他版本的 ZFS 上导入。

## 选项

### `-d`

不在新池上启用任何特性标志。可以通过 `-o` 将各个特性标志对应的属性设为 `enabled` 来单独启用它们。有关特性标志属性的详情，参见 zpool-features(7)。

### `-f`

强制使用指定的 vdev，即使它们看起来正在使用中，或指定了冲突的冗余级别。并非所有设备都能以此方式覆盖。

### `-m mountpoint`

设置根数据集的挂载点。如果指定了 `altroot`，默认挂载点为 `/pool` 或 `altroot/pool`。挂载点必须是绝对路径、`legacy` 或 `none`。有关数据集挂载点的更多信息，参见 zfsprops(7)。

### `-n`

显示将要使用的配置，而不实际创建池。实际创建池时仍可能因权限不足或设备共用而失败。

### `-o property=value`

设置给定的池属性。有关可设置的有效属性列表，参见 zpoolprops(7)。

### `-o compatibility=off|legacy|file[,file]…`

指定兼容特性集。有关兼容特性集的更多信息，参见 zpool-features(7)。

### `-o feature@feature=value`

设置给定的池特性标志。参见 zpool-features(7) 了解可设置的有效特性标志列表。取值可以为 `disabled` 或 `enabled`。

### `-O file-system-property=value`

在池的根文件系统上设置给定的文件系统属性。参见 zfsprops(7) 了解可设置的有效属性列表。

### `-R root`

等效于 `-o cachefile=none -o altroot=root`。

### `-t tname`

将内存中的池名设为 `tname`，而磁盘上的名称将为指定为 `pool` 的名称。这会将 `cachefile` 属性的默认值设为 `none`。这是为了处理为其他系统（例如虚拟机，或其池位于网络块设备上的物理机）创建池时的命名空间冲突。

## 示例

### 示例 1：创建 RAID-Z 存储池

以下命令创建一个由六块磁盘组成的、包含单个 raidz 根 vdev 的池：

```sh
# zpool create tank raidz sda sdb sdc sdd sde sdf
```

### 示例 2：创建镜像存储池

以下命令创建一个包含两个镜像的池，每个镜像包含两块磁盘：

```sh
# zpool create tank mirror sda sdb mirror sdc sdd
```

### 示例 3：使用分区创建 ZFS 存储池

以下命令使用两个磁盘分区创建一个非冗余池：

```sh
# zpool create tank sda1 sdb2
```

### 示例 4：使用文件创建 ZFS 存储池

以下命令使用文件创建一个非冗余池。虽然不推荐，但基于文件的池可用于实验目的。

```sh
# zpool create tank /path/to/file/a /path/to/file/b
```

### 示例 5：管理热备盘

以下命令创建一个带可用热备盘的新池：

```sh
# zpool create tank mirror sda sdb spare sdc
```

### 示例 6：创建带镜像独立意图日志的 ZFS 存储池

以下命令创建一个由两个两路镜像和镜像日志设备组成的 ZFS 存储池：

```sh
# zpool create pool mirror sda sdb mirror sdc sdd log mirror sde sdf
```

### 示例 7：创建带 dRAID vdev 的 ZFS 存储池

以下命令创建一个带 dRAID vdev 的 ZFS 存储池，该 vdev 具有一个校验盘、四个数据盘和一个分布式热备盘，共 6 块设备：

```sh
# zpool create pool draid1:4d:6c:1s sda sdb sdc sdd sde sdf
```

### 示例 8：创建带故障域的 dRAID vdev 的 ZFS 存储池

以下命令创建一个带 dRAID vdev 的 ZFS 存储池，具有五个故障组和六个故障域（例如机箱）。以下命令等价：

```sh
# zpool create pool draid1:4d:6c:30w:5s \
    enc0d0 enc1d0 enc2d0 enc3d0 enc4d0 enc5d0 \
    enc0d1 enc1d1 enc2d1 enc3d1 enc4d1 enc5d1 \
    enc0d2 enc1d2 enc2d2 enc3d2 enc4d2 enc5d2 \
    enc0d3 enc1d3 enc2d3 enc3d3 enc4d3 enc5d3 \
    enc0d4 enc1d4 enc2d4 enc3d4 enc4d4 enc5d4
```

```sh
# zpool create pool draid1:5s \
    fgroup enc0d0 enc1d0 enc2d0 enc3d0 enc4d0 enc5d0 \
    fgroup enc0d1 enc1d1 enc2d1 enc3d1 enc4d1 enc5d1 \
    fgroup enc0d2 enc1d2 enc2d2 enc3d2 enc4d2 enc5d2 \
    fgroup enc0d3 enc1d3 enc2d3 enc3d3 enc4d3 enc5d3 \
    fgroup enc0d4 enc1d4 enc2d4 enc3d4 enc4d4 enc5d4
```

```sh
# zpool create pool draid1:5s \
    fdomain enc0d0 enc0d1 enc0d2 enc0d3 enc0d4 \
    fdomain enc1d0 enc1d1 enc1d2 enc1d3 enc1d4 \
    fdomain enc2d0 enc2d1 enc2d2 enc2d3 enc2d4 \
    fdomain enc3d0 enc3d1 enc3d2 enc3d3 enc3d4 \
    fdomain enc4d0 enc4d1 enc4d2 enc4d3 enc4d4 \
    fdomain enc5d0 enc5d1 enc5d2 enc5d3 enc5d4
```

## 参考文献

zpool-destroy(8)、zpool-export(8)、zpool-import(8)

2022 年 7 月 11 日
