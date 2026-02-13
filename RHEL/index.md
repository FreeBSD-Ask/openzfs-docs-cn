# 在 RHEL 及其衍生版中启用 ZFS 支持

针对基于 x86_64 的 RHEL 和 CentOS 发行版，OpenZFS 仓库提供了 [DKMS](https://en.wikipedia.org/wiki/Dynamic_Kernel_Module_Support) 和 [kABI 跟踪 kmod](https://elrepoproject.blogspot.com/2016/02/kabi-tracking-kmod-packages.html) 风格的软件包。这些软件包会随着新版本发布而更新。每个当前主版本中，只有对应的当前点版本仓库会更新新软件包。

为简化安装，提供了软件包 *zfs-release*，其中包含 zfs.repo 配置文件和公钥签名。所有官方 OpenZFS 软件包均使用该密钥签名，默认情况下，yum 或 dnf 会在实际安装软件包前验证其签名。强烈建议用户使用此处列出的指纹验证 OpenZFS 公钥的真实性。

**密钥位置：** `/etc/pki/rpm-gpg/RPM-GPG-KEY-openzfs`（之前为 -zfsonlinux）

**当前发行版软件包：** [EL7](https://zfsonlinux.org/epel/zfs-release-2-3.el7.noarch.rpm)、[EL8](https://zfsonlinux.org/epel/zfs-release-3-0.el8.noarch.rpm)、[EL9](https://zfsonlinux.org/epel/zfs-release-3-0.el9.noarch.rpm)、[EL10](https://zfsonlinux.org/epel/zfs-release-3-0.el10.noarch.rpm)

**存档发行版软件包：** [参见仓库页面](https://github.com/zfsonlinux/zfsonlinux.github.com/tree/master/epel)

**签名密钥1（EL8 及更早版本，Fedora 36 及更早版本）** [pgp.mit.edu](https://pgp.mit.edu/pks/lookup?search=0xF14AB620&op=index&fingerprint=on) / [直接链接](https://raw.githubusercontent.com/zfsonlinux/zfsonlinux.github.com/master/zfs-release/RPM-GPG-KEY-openzfs-key1)

**指纹：** C93A FFFD 9F3F 7B03 C310 CEB6 A9D5 A1C0 F14A B620

**签名密钥2（EL9+，Fedora 37+）** [pgp.mit.edu](https://pgp.mit.edu/pks/lookup?search=0xA599FD5E9DB84141&op=index&fingerprint=on) / [直接链接](https://raw.githubusercontent.com/zfsonlinux/zfsonlinux.github.com/master/zfs-release/RPM-GPG-KEY-openzfs-key2)

**指纹：** 7DC7 299D CF7C 7FD9 CD87 701B A599 FD5E 9DB8 4141

对于 EL 7，运行：

```sh
yum install https://zfsonlinux.org/epel/zfs-release-2-3$(rpm --eval "%{dist}").noarch.rpm
```

对于 EL 8-10，运行：

```sh
dnf install https://zfsonlinux.org/epel/zfs-release-3-0$(rpm --eval "%{dist}").noarch.rpm
```

安装 *zfs-release* 软件包并验证公钥后，用户可以选择安装 DKMS 或 kABI 跟踪 kmod 风格的软件包。对于运行非发行版内核或希望对 OpenZFS 应用本地自定义的用户，推荐使用 DKMS 软件包。对于大多数用户，为避免在每次内核更新时重新编译 OpenZFS，推荐使用 kABI 跟踪 kmod 软件包。

## DKMS

要安装 DKMS 风格的软件包，请执行以下命令。首先通过安装 *epel-release* 软件包添加提供 DKMS 的 [EPEL 仓库](https://fedoraproject.org/wiki/EPEL)，然后安装 *kernel-devel* 和 *zfs* 软件包。请注意，必须确保为正在运行的内核安装匹配的 *kernel-devel* 软件包，因为 DKMS 构建 OpenZFS 时需要它。

对于 EL7，分别运行：

```sh
yum install -y epel-release
yum install -y kernel-devel
yum install -y zfs
```

对于 EL8 及更新版本，分别运行：

```sh
dnf install -y epel-release
dnf install -y kernel-devel
dnf install -y zfs
```

>**注意**
>
>从 DKMS 切换到 kABI 跟踪 kmod 时，请首先卸载现有的 DKMS 软件包。这将移除所有已安装内核的内核模块，然后可以按照下节所述安装 kABI 分支 kmod。

## kABI 分支 kmod

默认情况下，*zfs-release* 软件包配置为安装 DKMS 风格的软件包，以便兼容广泛的内核。要安装 kABI 跟踪 kmod，必须将默认仓库从 *zfs* 切换为 *zfs-kmod*。请注意，kABI 分支 kmod 仅经过验证可在发行版提供的非 Stream 内核上使用。

对于 EL7，运行：

```sh
yum-config-manager --disable zfs
yum-config-manager --enable zfs-kmod
yum install zfs
```

对于 EL8 及更新版本，运行：

```sh
dnf config-manager --disable zfs
dnf config-manager --enable zfs-kmod
dnf install zfs
```

在默认情况下，当检测到 ZFS 池时，会自动加载 OpenZFS 内核模块。如果希望在启动时始终加载这些模块，可以在 `/etc/modules-load.d` 中创建如下配置：

```sh
echo zfs >/etc/modules-load.d/zfs.conf
```

>**注意**
>
>当更新到新的 EL 点版本时，由于内核中上游 kABI 的变化，现有 kmod 软件包可能无法工作。当前发行版软件包的配置可能已提供了更新的软件包，但如果版本号不更新，包管理器可能不会自动安装该软件包。升级时，用户应验证 *kmod-zfs* 软件包是否提供了适用的内核模块，如有必要重新安装 *kmod-zfs* 软件包。

## 以前的 EL 点版本

当前发行版软件包使用 `${releasever}`，而不是像以前的发行版软件包那样指定特定的点版本。通常会将 `${releasever}` 解析为主版本号（例如 `8`），生成的仓库 URL 会被别名为当前点版本（例如 8.7），但可以通过指定 `–releasever` 使用以前的仓库。

```sh
[vagrant@localhost ~]$ dnf list available --showduplicates kmod-zfs
Last metadata expiration check: 0:00:08 ago on tor 31 jan 2023 17:50:05 UTC.
Available Packages
kmod-zfs.x86_64                          2.1.6-1.el8                          zfs-kmod
kmod-zfs.x86_64                          2.1.7-1.el8                          zfs-kmod
kmod-zfs.x86_64                          2.1.8-1.el8                          zfs-kmod
kmod-zfs.x86_64                          2.1.9-1.el8                          zfs-kmod
[vagrant@localhost ~]$ dnf list available --showduplicates --releasever=8.6 kmod-zfs
Last metadata expiration check: 0:16:13 ago on tor 31 jan 2023 17:34:10 UTC.
Available Packages
kmod-zfs.x86_64                          2.1.4-1.el8                          zfs-kmod
kmod-zfs.x86_64                          2.1.5-1.el8                          zfs-kmod
kmod-zfs.x86_64                          2.1.5-2.el8                          zfs-kmod
kmod-zfs.x86_64                          2.1.6-1.el8                          zfs-kmod
[vagrant@localhost ~]$
```

在上例中，前面的软件包是为 EL8.7 构建的，后面的为 EL8.6 构建的。

## 最新仓库（EL8+）

*zfs-latest* 仓库包含最新发布的、正在积极开发的 OpenZFS 版本。它将包含最新功能，并被认为是稳定的，但实际使用测试较少，相比 *zfs-legacy*。*zfs-latest* 相当于 Fedora 上的默认 *zfs* 仓库。来自最新仓库的软件包可以按如下方式安装。

对于 EL8 及更新版本，运行：

```sh
sudo dnf config-manager --disable "zfs*"
sudo dnf config-manager --enable zfs-latest
sudo dnf install zfs
```

>**注意**
>
>DKMS 软件包使用 *zfs-latest*，kABI 跟踪 kmod 软件包使用 *zfs-latest-kmod*。

## 传统仓库（EL8+）

*zfs-legacy* 仓库包含以前发布的、仍在积极更新的 OpenZFS 版本。通常，该仓库提供与 RHEL 和 CentOS 基础发行版的主 *zfs* 仓库相同的软件包。来自传统仓库的软件包可以按如下方式安装。

对于 EL8 及更新版本，运行：

```sh
sudo dnf config-manager --disable "zfs*"
sudo dnf config-manager --enable zfs-legacy
sudo dnf install zfs
```

>**注意**
>
>DKMS 软件包使用 *zfs-legacy*，kABI 跟踪 kmod 软件包使用 *zfs-legacy-kmod*。

## 版本特定仓库（EL8+）

版本特定仓库为希望运行特定分支（例如 2.3.x）ZFS 的用户提供。来自版本特定仓库的软件包可以按如下方式安装。

对于 EL8 及更新版本，启用 ZFS 分支 x.y 的版本特定仓库，运行：

```sh
sudo dnf config-manager --disable "zfs*"
sudo dnf config-manager --enable zfs-x.y
sudo dnf install zfs
```

>**注意**
>
>DKMS 软件包使用 *zfs-x.y*，kABI 跟踪 kmod 软件包使用 *zfs-x.y-kmod*。

## 测试仓库（已弃用）

*zfs-testing* 和 *zfs-testing-kmod* 仓库已弃用，推荐使用 *zfs-latest*。
