# zpool-reguid(8)

## 名称

`zpool-reguid` — 为 ZFS 存储池生成新的唯一标识符

## 概述

```sh
zpool reguid [-g GUID] 池名
```

## 说明

为池生成一个新的唯一标识符。执行此操作之前，你必须确保池中的所有设备都在线且状态正常。

### `-g GUID`

将池 GUID 设置为提供的值。GUID 可以是 strtoull(3) 在十进制下接受的任何 64 位值。如果提供的 GUID 已被其他池使用，`zpool reguid` 会返回错误。

### 文件系统 UUID 与 overlayfs

在 Linux 上，池 GUID 是池中每个已挂载文件系统向内核报告的文件系统 UUID 的前半部分；zfsprops(7) 中的 `guid` 属性描述了该 UUID。池 GUID 的变更会在该文件系统下次挂载时体现在其 UUID 中。

Linux overlayfs 会把底层文件系统的 UUID 存储在其 `index` 与 `nfs_export` 特性的文件句柄中，以及被复制到上层（copied up）的文件的原始文件句柄中。overlayfs 层的 UUID 发生变更会使这些文件句柄失效：使用 `index=on` 挂载 overlay 会失败，内核日志中会出现“failed to verify upper root origin”消息；通过 NFS 导出该 overlay 的客户端会得到失效的文件句柄；并且在变更之前被复制到上层的文件，其 inode 号可能会改变。在这些特性使用期间，不要更改承载 overlayfs 层的池的 GUID。如果 overlay 的所有层都位于同一个文件系统上，可以从首次挂载起使用 overlayfs 挂载选项 `uuid=off`（Linux 5.11 及更高版本）；这样它会在文件句柄中存储 null UUID，而 GUID 变更不会影响这些句柄。内核的 overlayfs 文档（`Documentation/filesystems/overlayfs.rst`）描述了这些文件句柄与挂载选项。

要在 `zpool reguid` 之后恢复，先卸载受影响的 overlay 及其 ZFS 层。`zpool history -i pool` 输出中的“guid change”记录会显示先前的 GUID。如果该 GUID 尚未被其他池使用，可以用 `zpool reguid -g oldguid pool` 将其恢复。然后按原来的选项重新挂载 ZFS 层与 overlay。如果数据集 GUID 未变，这会恢复先前的文件系统 UUID。不要通过删除 overlay 的 `index` 目录来恢复：该目录可能保存着指向被复制到上层的文件的已修改数据的唯一上层链接，而使用 `index=off` 挂载可能会改为显示原始的下层数据。

较早的 OpenZFS 版本报告的文件系统 UUID 为 null UUID，因此升级后的首次挂载与 GUID 变更具有相同的效果。升级之前创建的 overlay，其文件句柄中保存的是 null UUID，因此如果其所有层都位于同一个文件系统上，该 overlay 可以在 `uuid=off` 下重新挂载。或者，把 zfs(4) 的 `zfs_sb_uuid` 模块参数设为 `0`，这会为之后挂载的文件系统恢复 null UUID。按照 zfs(4) 的说明，在首次挂载之前通过内核命令行或在 initramfs 中设置该参数。

## 参考文献

zfs(4)、zfsprops(7)、zpool-export(8)、zpool-import(8)

2026 年 9 月 9 日
