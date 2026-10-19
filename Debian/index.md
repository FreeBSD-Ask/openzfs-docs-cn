# 在 Debian 中启用 ZFS 支持

## 安装

如果你想将 ZFS 用作根文件系统，请改为参阅[以 ZFS 为根文件系统](https://openzfs.github.io/openzfs-docs/Getting%20Started/Debian/index.html#root-on-zfs)的相关页面。

ZFS 软件包包含在 [contrib 仓库](https://packages.debian.org/source/zfs-linux) 中。[backports 仓库](https://backports.debian.org/Instructions/) 通常提供更新版本的 ZFS。你可以按如下方式使用。

添加 backports 仓库：

```sh
vi /etc/apt/sources.list.d/trixie-backports.list
```

```ini
deb http://deb.debian.org/debian trixie-backports main contrib non-free-firmware
deb-src http://deb.debian.org/debian trixie-backports main contrib non-free-firmware
```

```sh
vi /etc/apt/preferences.d/90_zfs
```

```ini
Package: src:zfs-linux
Pin: release n=trixie-backports
Pin-Priority: 990
```

安装软件包：

```sh
apt update
apt install dpkg-dev linux-headers-generic linux-image-generic
apt install zfs-dkms zfsutils-linux
```

>**注意**：
>
>如果你处于配置不良的环境中（例如某些虚拟机或容器控制台），当 apt 在首次安装时尝试弹出提示信息，它可能未能察觉实际上并没有真正可用的控制台，于是表现为无限期停滞。为避免这种情况发生，你可以在 `apt install` 命令前加上 `DEBIAN_FRONTEND=noninteractive`，形如：
>
>```sh
>DEBIAN_FRONTEND=noninteractive apt install zfs-dkms zfsutils-linux
>```
