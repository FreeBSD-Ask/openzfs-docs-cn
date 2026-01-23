# Alpine Linux 概述

## 安装

>**注意**
>
>这是在现有 Alpine 安装上安装 ZFS 。要将 ZFS 用作 root file system ，请参见下文。

1. 安装 ZFS 包：

   ```sh
   apk add zfs zfs-lts
   ```
2. 加载 kernel module ：

   ```sh
   modprobe zfs
   ```

## zpool 自动导入与挂载

为避免系统 boot 后需要手动导入并挂载 zpools ，请务必启用相关服务。

1. 在 boot 时导入 pools ：

   ```sh
   rc-update add zfs-import default
   ```
2. 在 boot 时挂载 pools ：

   ```sh
   rc-update add zfs-mount default
   ```
