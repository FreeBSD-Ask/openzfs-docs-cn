# zfs-mount-generator(8)

## 名称

`zfs-mount-generator` — 为 ZFS 文件系统生成 systemd 挂载单元

## 概述

```sh
@systemdgeneratordir@/zfs-mount-generator
```

## 说明

`zfs-mount-generator` 是一个 systemd.generator(7) 生成器，为已配置的 ZFS 数据集生成原生的 systemd.mount(5) 单元。

### 属性

#### `mountpoint=`

值为 `legacy` 或 `none` 时跳过。

#### `canmount=`

值为 `off` 时跳过。如果给定挂载点下只存在 `noauto` 数据集，且这样的数据集不止一个，也会跳过。对于同一挂载点，值为 `yes` 的数据集优先于值为 `noauto` 的数据集。值为 `noauto` 时，设置逻辑上的 **noauto** 标志。加密根始终生成 `zfs-load-key@root.service`，即使值为 `off`。

#### `atime=`、`relatime=`、`devices=`、`exec=`、`readonly=`、`setuid=`、`nbmand=`

用于生成与 `zfs mount` 等价的挂载选项。

#### `encroot=`、`keylocation=`

如果数据集是加密根，其挂载单元将绑定到 `zfs-load-key@root.service`，并带有如下附加依赖项：

* `keylocation=prompt`：无附加依赖，使用 systemd-ask-password(1)。
* `keylocation=https://URL`（等）：`Wants=`、`After=`：`network-online.target`
* `keylocation=file://<path>`：`RequiresMountsFor=path`

该服务还使用与挂载单元相同的 `Wants=`、`After=`、`Requires=` 与 `RequiresMountsFor=`。

#### `org.openzfs.systemd:requires=path[ path]…`

为挂载单元与密钥加载单元设置 `Requires=`。

#### `org.openzfs.systemd:requires-mounts-for=path[ path]…`

为挂载单元与密钥加载单元设置 `RequiresMountsFor=`。

#### `org.openzfs.systemd:before=unit[ unit]…`

为挂载单元设置 `Before=`。

#### `org.openzfs.systemd:after=unit[ unit]…`

为挂载单元设置 `After=`。

#### `org.openzfs.systemd:wanted-by=unit[ unit]…`

设置逻辑上的 **noauto** 标志（见下文）。如果值不是 `none`，则为挂载单元设置 `WantedBy=`。

#### `org.openzfs.systemd:required-by=unit[ unit]…`

设置逻辑上的 **noauto** 标志（见下文）。如果值不是 `none`，则为挂载单元设置 `RequiredBy=`。

#### `org.openzfs.systemd:nofail=(unset)|on|off`

增强或减弱挂载单元默认反向依赖的强度，见下文。

#### `org.openzfs.systemd:ignore=on|off`

值为 `on` 时跳过（默认值: `off`）。

### 单元顺序与依赖

此外，除非数据集所在的池在生成时已经导入，否则两个单元都会获得 `Wants=zfs-import.target` 与 `After=zfs-import.target`。

此外，除非设置了逻辑上的 **noauto** 标志，否则挂载单元会为 `local-fs.target` 获得一个反向依赖，其强度如下：

| `nofail` 取值 | 生成的依赖 |
| :---: | :---: |
| `(unset)` | `WantedBy=` 与 `Before=` |
| `on` | `WantedBy=` |
| `off` | `RequiredBy=` 与 `Before=` |

### 缓存文件

由于 ZFS 存储池在启动过程的早期可能尚不可用，ZFS 挂载点的信息必须单独存放。对于应由 systemd 挂载的数据集，`zfs list -Ho name,<上述每个属性，按顺序>` 的输出应保存在 `@sysconfdir@/zfs/zfs-list.cache/poolname`；如果该文件可写，那么在启用后，`history_event-zfs-list-cacher.sh` ZEDLET 会为整个池保持其同步（参见 zed(8)）。

## 环境变量

如果环境变量 `ZFS_DEBUG` 非零（或者未设置且 `/proc/cmdline` 包含 `debug`），则在结束时打印汇总统计信息。

## 示例

首先，为存储池启用跟踪：

```sh
# touch @sysconfdir@/zfs/zfs-list.cache/poolname
```

然后启用负责跟踪的 ZEDLET：

```sh
# ln -s @zfsexecdir@/zed.d/history_event-zfs-list-cacher.sh @sysconfdir@/zfs/zed.d
# systemctl enable zfs-zed.service
# systemctl restart zfs-zed.service
```

如果队列中没有历史事件，可以在池中某处设置一个受监视的属性，以此注入一个事件，确保 ZEDLET 运行并刷新缓存文件：

```sh
# zfs set relatime=off poolname/dset
# zfs inherit relatime poolname/dset
```

要测试生成器的输出：

```sh
$ mkdir /tmp/zfs-mount-generator
$ @systemdgeneratordir@/zfs-mount-generator /tmp/zfs-mount-generator
```

如果生成的单元符合预期，可指示 systemd 重新运行所有生成器：

```sh
# systemctl daemon-reload
```

## 参考文献

systemd.mount(5)、systemd.target(5)、zfs(5)、systemd.generator(7)、systemd.special(7)、zed(8)、zpool-events(8)

2021 年 11 月 30 日
