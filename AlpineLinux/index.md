# 在 Alpine Linux 中启用 ZFS 支持

## 安装

>**注意**
>
>这是在既有的 Alpine 系统上安装 ZFS。要将 ZFS 用作根（`/`）文件系统，请参见下文。

1. 安装 ZFS 包：

   ```sh
   apk add zfs zfs-lts
   ```

2. 加载内核模块：

   ```sh
   modprobe zfs
   ```

## zpool 自动导入与挂载

为避免系统启动后还需手动导入并挂载 ZFS 存储池，请务必启用相关服务。

1. 在启动时导入存储池：

   ```sh
   rc-update add zfs-import default
   ```

2. 在启动时挂载存储池：

   ```sh
   rc-update add zfs-mount default
   ```
