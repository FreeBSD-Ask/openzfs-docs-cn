# dracut.zfs(7)

## 名称

`dracut.zfs` — ZFS dracut 钩子概述

## 概述

```text
                      parse-zfs.sh → dracut-cmdline.service
                          |                     ↓
                          |                     …
                          |                     ↓
                          \—————————→ dracut-initqueue.service
                                                |                      zfs-import-opts.sh
   zfs-load-module.service                      ↓                          |       |
     |                  |                sysinit.target                    ↓       |
     ↓                  |                       |        zfs-import-scan.service   ↓
zfs-import-scan.service ↓                       ↓           | zfs-import-cache.service
     |   zfs-import-cache.service         basic.target      |     |
     \__________________|                       |           ↓     ↓
                        ↓                       |     zfs-load-key.sh
     zfs-env-bootfs.service                     |         |
                        ↓                       ↓         ↓
                 zfs-import.target → dracut-pre-mount.service
                        |          ↑            |
                        | dracut-zfs-generator  |
                        | _____________________/|
                        |/                      ↓
                        |                   sysroot.mount ←——— dracut-zfs-generator
                        |                       |
                        |                       ↓
                        |             initrd-root-fs.target ←— zfs-nonroot-necessities.service
                        |                       |                                 |
                        |                       ↓                                 |
                        ↓             dracut-mount.service                        |
       zfs-snapshot-bootfs.service              |                                 |
                        |                       ↓                                 |
                        ↓                       …                                 |
       zfs-rollback-bootfs.service              |                                 |
                        |                       ↓                                 |
                        |          /sysroot/{usr,etc,lib,&c.} ←——————————————————/
                        |                       |
                        |                       ↓
                        |                initrd-fs.target
                        \______________________ |
                                               \|
                                                ↓
        export-zfs.sh                      initrd.target
              |                                 |
              ↓                                 ↓
   dracut-shutdown.service                      …
                                                |
                                                ↓
                 zfs-needshutdown.sh → initrd-cleanup.service
```

完整流程图请对照 dracut.bootup(7)。

## 说明

在 dracut 下，以 ZFS 作为根文件系统启动由 `90zfs` 模块中的若干钩子协助完成。

以 ZFS 数据集为根启动，要求包含根文件系统的数据集（下称“启动数据集”）设置了 `mountpoint=/`，并且至少满足以下其一：该数据集设置了 `bootfs` 属性，或内核命令行（或 dracut drop-in）参数 `root=` 指定了它。

启动数据集中所有 `canmount=on` 且挂载点匹配 `/etc`、`/bin`、`/lib`、`/lib??`、`/libx32` 与 `/usr` 通配模式的子数据集被视为必要数据集，也会被一并挂载。

为了系统此后正常运作（正确的挂载属性、重新挂载等），建议使用 zfs-mount-generator(8)。

## 命令行

### 标准

#### `root=zfs:dataset`、`root=ZFS=dataset`

使用 dataset 作为启动数据集。所有加号（`+`）都会被替换为空格。

#### `root=zfs:AUTO`、`root=zfs:`、`root=zfs`、`[root=]`

导入后，搜索第一个设置了 `bootfs` 属性的池，并将其值视作上文指定的 dataset 使用。

#### `rootfstype=zfs root=dataset`

等效于 `root=zfs:dataset`。

#### `rootfstype=zfs` `[root=]`

等效于 `root=zfs:AUTO`。

#### `rootflags=flags`

以 `-o flags` 挂载启动数据集；参见 zfsprops(7) 中的“临时挂载点属性”。这些属性不会持久保留，因为所有文件系统稍后会从真实根重新挂载。

#### `debug`

如果指定，dracut-zfs-generator 会记录日志到 journal。

请小心不要同时省略 `rootfstype=zfs` 与 `root=zfs:dataset`——其他自动启动选择机制（例如 systemd-gpt-auto-generator 与 systemd-fstab-generator）可能会优先生效。

### ZFS 专用

#### `bootfs.snapshot[=snapshot-name]`

在切换到真实根之前执行 `zfs snapshot boot-dataset@snapshot-name`。snapshot-name 默认为当前内核版本号。

#### `bootfs.rollback[=snapshot-name]`

在切换到真实根之前执行 `zfs rollback -Rf boot-dataset@snapshot-name`。snapshot-name 默认为当前内核版本号。

#### `spl_hostid=host-id`

使用 zgenhostid(8) 将主机 ID 设置为 host-id；否则使用从真实根继承的 `/etc/hostid`。

#### `zfs_force`、`zfs.force`、`zfsforce`

为所有 `zpool import` 调用追加 `-f`；主要在与 `spl_hostid=` 结合使用、或没有继承到主机 ID 时有用。

## 文件

### `parse-zfs.sh`（cmdline）

处理 `spl_hostid=`。如果 `root=` 匹配上述已知模式，则提供 `/dev/root`，并把 initqueue 推迟到 zfs(4) 加载完成之后。

### `zfs-import-opts.sh`（systemd 环境生成器）

把 `zfs_force`、`zfs.force` 或 `zfsforce` 转换为 `ZPOOL_IMPORT_OPTS=-f`，供 `zfs-import-scan.service` 或 `zfs-import-cache.service` 使用。

### `zfs-load-key.sh`（pre-mount）

为启动数据集及其必要子数据集加载加密密钥。

* `keylocation=prompt`：通过 systemd-ask-password 提示输入三次。
* `keylocation=https://URL`、`keylocation=http://URL`：加载之前先启动 network-online.target。
* `keylocation=file://path`：如果 path 不存在，执行 `udevadm settle`；如果仍不存在，最多等待 10 秒。

### `zfs-env-bootfs.service`（systemd service）

池导入后，按迭代顺序把 systemd 环境中的 `BOOTFS=` 设置为第一个非空的 `bootfs` 值。

### `dracut-zfs-generator`（systemd generator）

生成 `sysroot.mount`（使用 `rootflags=`，如有的话）。如果显式指定了启动数据集，还会生成必要的挂载点（`sysroot-etc.mount`、`sysroot-bin.mount` 等）；否则生成 `zfs-nonroot-necessities.service`，在挂载 `/sysroot` 后使用 `BOOTFS=` 显式挂载它们。

### `zfs-snapshot-bootfs.service`、`zfs-rollback-bootfs.service`（systemd services）

按“命令行”一节所述消费 `bootfs.snapshot` 与 `bootfs.rollback`。未显式指定启动数据集时使用 `BOOTFS=`。

### `zfs-needshutdown.sh`（cleanup）

如果导入了任何池，则发出需要关机钩子的信号。

### `export-zfs.sh`（shutdown）

强制导出所有池。

### `/etc/hostid`、`/etc/zfs/zpool.cache`、`/etc/zfs/vdev_id.conf`（常规文件）

hostonly 模式下原样收录。

### `mount-zfs.sh`（mount）

在 systemd 系统上不执行任何操作（当 dracut-zfs-generator 成功时）。否则从控制台或通过 plymouth 为启动数据集加载加密密钥。它可能完全不起作用！

## 参考文献

dracut.bootup(7)、zfsprops(7)、zpoolprops(7)、dracut-shutdown.service(8)、systemd-fstab-generator(8)、systemd-gpt-auto-generator(8)、zfs-mount-generator(8)、zgenhostid(8)

2024 年 7 月 13 日
