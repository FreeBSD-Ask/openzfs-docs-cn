# Debian GNU Linux initrd 文档

## 支持的引导参数

* `rollback=<on|yes|1>` 回滚到指定的快照。
* `zfs_debug=<on|yes|1>` 调试 initrd 脚本。
* `zfs_force=<on|yes|1>` 强制导入存储池。通常没有必要。
* `zfs=<off|no|0>` 不尝试导入任何存储池、挂载任何文件系统，甚至不加载模块。
* `rpool=<pool>` 指定用作根存储池的池。
* `bootfs=<pool>/<dataset>` 指定用作根文件系统的数据集。
* `root=<pool>/<dataset>` 指定用作根文件系统的数据集。
* `root=ZFS=<pool>/<dataset>` 指定用作根文件系统的数据集。
* `root=zfs:<pool>/<dataset>` 指定用作根文件系统的数据集。
* `root=zfs:AUTO` 尝试自动探测存储池与根文件系统。

在以上所有情形中，`<dataset>` 也可以是 `<dataset>@<snapshot>`。

之所以提供这么多指定根文件系统的引导选项，是因为目前存在多种不同的 ZFS 引导方式，我们希望确保它们都得到支持。

## 存储池导入

### 使用 `/dev/disk/by-*` 导入

如果在文件 `/etc/default/zfs` 中设置了变量 `USE_DISK_BY_ID`，initrd 将使用 `/dev/disk/by-*` 链接导入。它会按以下顺序尝试导入：

1. `/dev/disk/by-vdev`
2. `/dev/disk/by-*`
3. `/dev`

### 使用缓存文件导入

如果以上导入均失败（或未设置 `USE_DISK_BY_ID`），initrd 接着会尝试使用缓存文件导入。

### 最后的导入尝试

如果那样也失败，它还会再试一次，不带任何 `-d` 或 `-c` 选项。

## 引导

### 从快照引导

按照下面的示例，为 `root=` 参数指定快照：

```sh
linux   /BOOT/debian@/boot/vmlinuz-5.10.0-9-amd64 root=ZFS=rpool/ROOT/debian@some_snapshot ro
```

这会把快照 `rpool/ROOT/debian@some_snapshot` 克隆到文件系统 `rpool/ROOT/debian_some_snapshot`，并将其用作根文件系统。此情况下原始文件系统与快照保持不动。

**警告**：它首先会毫无节制地销毁 `rpool/ROOT/debian_some_snapshot` 文件系统，然后才尝试把快照重新克隆进去。因此，如果你之前从同一快照引导过，并在该根文件系统中做过更改，这些更改会随文件系统的销毁而丢失。

### 快照回滚

自 0.6.4-1-3 版本起，也可以指定 `rollback=1` 来回滚快照，而不是克隆它。**警告**：这会销毁指定快照之后的**所有**快照。

### 动态选择快照

自 0.6.4-1-3 版本起，还可以指定空的快照名（例如 `root=rpool/ROOT/debian@`）；此时 initrd 脚本会列出该文件系统（不含 `@`）下的所有快照，输出列表供用户选择。

### 从原生加密文件系统引导

尽管 ZFS On Linux 目前尚不支持原生加密，但社区中流传着相关补丁，initrd 支持加载密钥并解锁此类加密文件系统。

## 独立的文件系统

### 派生的文件系统

如果存在独立的文件系统（例如为 `/usr` 单独建立的数据集），快照引导代码会尝试在每个文件系统下找到对应快照并进行克隆（或回滚）。

示例：

```sh
rpool/ROOT/debian@some_snapshot
rpool/ROOT/debian/usr@some_snapshot
```

（在不回滚的情况下）它们会分别创建以下文件系统：

```sh
rpool/ROOT/debian_some_snapshot
rpool/ROOT/debian/usr_some_snapshot
```

initrd 代码会使用原始（不含快照部分）数据集中的 `mountpoint` 选项（如果有）来确定应当在何处挂载该数据集；或者使用根文件系统（本例为 `rpool/ROOT/debian`）之下的数据集名称作为挂载点。
