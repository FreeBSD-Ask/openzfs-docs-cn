# zpool-remove(8)

## 名称

`zpool-remove` — 从 ZFS 存储池移除设备

## 概述

```sh
zpool remove [-npw] 池名 设备…
```

```sh
zpool remove -s 池名
```

## 说明

### `zpool remove [-npw] pool device…`

从池中移除指定设备。此命令支持移除热备盘、缓存设备、日志设备，以及镜像和非冗余的顶级主 vdev（包括 dedup 与 special vdev）。

只有当池的主存储中不含顶级 `raidz` 或 `draid` vdev、所有顶级 vdev 的 ashift 大小相同，且所有加密数据集的密钥均已加载时，才能移除顶级 vdev。

移除顶级 vdev 会减少存储池的总空间。指定设备将通过把所有已分配空间复制到池中其他设备的方式腾空。在这种情况下，`zpool remove` 命令只启动移除操作随即返回，腾空过程在后台继续进行。移除进度可以用 `zpool status` 监控。如果在移除过程中遇到 I/O 错误，移除将被取消。移除顶级 vdev 必须启用 `device_removal` 特性标志，参见 zpool-features(7)。

镜像的顶级设备（日志或数据）可以通过指定相应的顶级镜像来移除。属于镜像配置的非日志设备或数据设备可以用 `zpool detach` 命令移除。

#### `-n`

不实际执行移除操作（空操作），而是打印移除完成后映射表（mapping table）将占用的内存的估算量。该值仅对顶级 vdev 非零。

#### `-p`

与 `-n` 选项配合使用，以可解析的（精确）数值显示数字。

#### `-w`

等待移除完成后才返回。

### `zpool remove -s pool`

停止并取消正在进行中的顶级 vdev 移除操作。

## 示例

### 示例 1：移除镜像的顶级（日志或数据）设备

以下命令移除镜像日志设备 `mirror-2` 与镜像的顶级数据设备 `mirror-1`。

给定如下配置：

```sh
  pool: tank
 state: ONLINE
 scrub: none requested
config:

         NAME        STATE     READ WRITE CKSUM
         tank        ONLINE       0     0     0
           mirror-0  ONLINE       0     0     0
             sda     ONLINE       0     0     0
             sdb     ONLINE       0     0     0
           mirror-1  ONLINE       0     0     0
             sdc     ONLINE       0     0     0
             sdd     ONLINE       0     0     0
         logs
           mirror-2  ONLINE       0     0     0
             sde     ONLINE       0     0     0
             sdf     ONLINE       0     0     0
```

移除镜像日志设备 `mirror-2` 的命令为：

```sh
# zpool remove tank mirror-2
```

此时日志设备已不存在（镜像的两侧均已移除）：

```sh
  pool: tank
 state: ONLINE
  scan: none requested
config:

        NAME        STATE     READ WRITE CKSUM
        tank        ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            sda     ONLINE       0     0     0
            sdb     ONLINE       0     0     0
          mirror-1  ONLINE       0     0     0
            sdc     ONLINE       0     0     0
            sdd     ONLINE       0     0     0
```

移除镜像数据设备 `mirror-1` 的命令为：

```sh
# zpool remove tank mirror-1
```

`mirror-1` 腾空后，池仍然保持冗余，但总空间减少：

```sh
  pool: tank
 state: ONLINE
  scan: none requested
config:

        NAME        STATE     READ WRITE CKSUM
        tank        ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            sda     ONLINE       0     0     0
            sdb     ONLINE       0     0     0
```

## 参考文献

zpool-add(8)、zpool-detach(8)、zpool-labelclear(8)、zpool-offline(8)、zpool-replace(8)、zpool-split(8)

2024 年 11 月 19 日

