# 在 Ubuntu 中启用 ZFS 支持

## 安装

>**注意**
>
>如果你想将 ZFS 用作根文件系统，请参阅下文。

在 Ubuntu 上，在默认的 Linux 内核包中已经内置了对 ZFS 的支持。要安装 ZFS 工具，请首先确保在 `/etc/apt/sources.list` 中启用了 `universe`：

```ini
deb http://archive.ubuntu.com/ubuntu <Ubuntu 版本代号> main universe
```

然后安装 `zfsutils-linux`：

```sh
apt update
apt install zfsutils-linux
```
