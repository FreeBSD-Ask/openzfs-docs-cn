# zfs_prepare_disk(8)

## 名称

`zfs_prepare_disk` — 在磁盘加入存储池之前运行的特殊脚本

## 说明

`zfs_prepare_disk` 是一个可选脚本，由 libzfs 在把磁盘加入存储池之前调用。你可以修改该脚本，以运行使磁盘做好加入池准备所需的任何命令。例如，可以在 `zfs_prepare_disk` 中添加命令行，用来更新磁盘固件或检查磁盘健康状况。`zfs_prepare_disk` 是可选的，不需要时可以移除。libzfs 会在 `@zfsexecdir@/zfs_prepare_disk` 处查找该脚本。

### 属性

`zfs_prepare_disk` 会接收以下环境变量：

#### `POOL_NAME`

池的名称。

#### `VDEV_PATH`

磁盘的路径（如 `/dev/sda`）。

#### `VDEV_PREPARE`

磁盘为加入池而做准备的原因（`create`、`add`、`replace` 或 `autoreplace`）。如果你只希望脚本在某些操作下运行，这会很有用。

#### `VDEV_UPATH`

磁盘底层设备之一的路径。对于多路径（multipath）设备，它会返回该磁盘的某个 `/dev/sd*` 路径。如果设备不是 device mapper 设备，则 `VDEV_UPATH` 只返回与 `VDEV_PATH` 相同的值。

#### `VDEV_ENC_SYSFS_PATH`

磁盘机箱的 sysfs 路径（如果可用）。

注意，其中一些变量的值可能为空。例如，在创建池时 `POOL_NAME` 为空。

## 环境变量

`zfs_prepare_disk` 在受限的 `$PATH` 下运行。

## 退出状态

`zfs_prepare_disk` 成功时应返回 0，否则返回非零值。如果返回非零值，该磁盘将不会被加入池中。

2023 年 8 月 30 日
