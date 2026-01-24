# Debian 概述

## 安装

如果你想将 ZFS 用作根文件系统，请参阅下方的 [基于 ZFS 的根文件系统](https://openzfs.github.io/openzfs-docs/Getting%20Started/Debian/index.html#root-on-zfs) 链接。

ZFS 包包含在 [contrib 仓库](https://packages.debian.org/source/zfs-linux) 中。[backports 仓库](https://backports.debian.org/Instructions/) 通常提供更新版本的 ZFS。你可以按如下方式使用。

添加 backports 仓库：

```sh
vi /etc/apt/sources.list.d/trixie-backports.list
```

```
deb http://deb.debian.org/debian trixie-backports main contrib non-free-firmware
deb-src http://deb.debian.org/debian trixie-backports main contrib non-free-firmware
```

```
vi /etc/apt/preferences.d/90_zfs
```

```
Package: src:zfs-linux
Pin: release n=trixie-backports
Pin-Priority: 990
```

安装软件包：

```
apt update
apt install dpkg-dev linux-headers-generic linux-image-generic
apt install zfs-dkms zfsutils-linux
```

**注意**：如果你处于配置不良的环境中（例如某些虚拟机或容器控制台），当 apt 在首次安装时尝试弹出提示信息，可能无法识别实际控制台不可用，从而表现为无限期挂起。为避免这种情况，你可以在 apt install 命令前加上 `DEBIAN_FRONTEND=noninteractive`，例如：

```
DEBIAN_FRONTEND=noninteractive apt install zfs-dkms zfsutils-linux
```
