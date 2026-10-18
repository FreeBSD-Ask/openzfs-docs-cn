# 在 Ubuntu 中启用 ZFS 支持

## 安装

>**注意**
>
>如果你想将 ZFS 用作根文件系统，请改为参阅下文的 Root on ZFS 链接。

在 Ubuntu 上，ZFS 已包含在默认的 Linux 内核包中。要安装 ZFS 工具，请先确保在 `/etc/apt/sources.list` 中启用了 `universe`：

```ini
deb http://archive.ubuntu.com/ubuntu <Ubuntu 版本代号> main universe
```

然后安装 `zfsutils-linux`：

```sh
apt update
apt install zfsutils-linux
```
