# mount.zfs(8)

## 名称

`mount.zfs` — 挂载 ZFS 文件系统

## 概述

```sh
mount.zfs [-sfnvh] [-o options] dataset mountpoint
```

## 说明

`mount.zfs` 辅助程序被 mount(8) 用于挂载文件系统快照和 `mountpoint=legacy` 的 ZFS 文件系统；在未设置 `ZFS_MOUNT_HELPER` 环境变量时，也被 zfs(8) 使用。在大多数情况下，你应当调用 mount(8) 或 zfs(8)。

`options` 依据 zfsprops(7) 的“临时挂载点属性”一节处理，下文所述的选项除外。

如果 `/etc/mtab` 是普通文件且未指定 `-n`，则它会通过 libmount 更新。

## 选项

### `-s`

忽略未知的挂载选项（宽松处理）。

### `-f`

执行除实际调用系统调用之外的全部操作。

### `-n`

从不更新 `/etc/mtab`。

### `-v`

打印已解析的挂载选项与解析器状态。

### `-h`

打印用法说明。

### `-o zfsutil`

此私有标志表示 mount(8) 正由 zfs(8) 命令调用。

## 参考文献

fstab(5)、mount(8)、zfs-mount(8)

2021 年 5 月 24 日
