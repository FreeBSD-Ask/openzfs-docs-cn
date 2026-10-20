# zfs-mount(8)

## 名称

`zfs-mount` — 管理 ZFS 文件系统的挂载状态

`zfs-unmount(8)` 是 `zfs-mount(8)` 的历史别名。

## 概述

```sh
zfs mount [-j]
```

```sh
zfs mount [-Oflv] [-o 选项] -a|-R 文件系统|文件系统
```

```sh
zfs unmount [-fu] -a|文件系统|挂载点
```

## 说明

### `zfs mount [-j]`

显示当前已挂载的所有 ZFS 文件系统。

#### `-j`、`--json`

以 JSON 格式显示所有已挂载的文件系统。

### `zfs mount [-Oflv] [-o options] -a|-R filesystem|filesystem`

将 ZFS 文件系统挂载到其 `mountpoint` 属性所描述的路径上，如果该路径存在且为空。如果 `mountpoint` 设为 `legacy`，则应改用 `mount(8)` 挂载该文件系统。

#### `-O`

执行 overlay 挂载。允许挂载到非空的 `mountpoint`。详情参见 `mount(8)`。

#### `-a`

挂载所有可用的 ZFS 文件系统。如果进行了相应配置，它会作为启动过程的一部分被自动调用。

#### `-R`

挂载指定的文件系统及其所有子文件系统。

#### `filesystem`

挂载指定的文件系统。

#### `-o options`

可选的、以逗号分隔的挂载选项列表，仅在本次挂载期间临时生效。详情参见 zfsprops(7) 的“临时挂载点属性”一节。

#### `-l`

挂载加密文件系统时加载其密钥。这相当于在挂载每个加密根之前对其执行 `zfs load-key`。注意，如果文件系统的 `keylocation` 为 `prompt`，这会导致终端在提示输入密钥后进入交互式阻塞。在支持 PAM 的系统上，pam_zfs_key(8) 可以在用户登录时自动完成此过程。

#### `-v`

报告挂载进度。

#### `-f`

尝试强制挂载所有文件系统，包括通常无法挂载的文件系统（例如遮蔽数据集）。

### `zfs unmount [-fu] -a|filesystem|mountpoint`

卸载当前已挂载的 ZFS 文件系统。

#### `-a`

卸载所有可用的 ZFS 文件系统。它在关机过程中被自动调用。

#### `-f`

强制卸载文件系统，即使它当前正在使用中。Linux 不支持此选项。

#### `-u`

卸载此命令卸载的所有加密根的密钥。

#### `filesystem|mountpoint`

卸载指定的文件系统。该命令也可以接受系统上某个 ZFS 文件系统挂载点的路径。

## 参考文献

pam_zfs_key(8)

2024 年 10 月 12 日
