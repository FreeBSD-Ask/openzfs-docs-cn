# 在 RHEL 及其衍生版中启用 ZFS 支持

[DKMS](https://en.wikipedia.org/wiki/Dynamic_Kernel_Module_Support) 和 [kABI-tracking kmod](https://elrepoproject.blogspot.com/2016/02/kabi-tracking-kmod-packages.html) 风格的软件包由 OpenZFS 仓库提供，适用于基于 x86_64 的 RHEL 和 CentOS 发行版。这些软件包会随着新版本发布而更新。每个当前主要版本的仓库仅为当前次版本更新软件包。

为了简化安装，提供了软件包 *zfs-release*，其中包含 zfs.repo 的配置文件和公钥。所有官方 OpenZFS 软件包均使用该密钥签名，默认情况下，yum/dnf 会在批准安装前验证软件包签名。强烈建议用户使用此处列出的指纹验证 OpenZFS 公钥的真实性。

**密钥位置：** `/etc/pki/rpm-gpg/RPM-GPG-KEY-openzfs`（之前为 `-zfsonlinux`）

**当前发行版软件包：** [EL7](https://zfsonlinux.org/epel/zfs-release-2-3.el7.noarch.rpm)、[EL8](https://zfsonlinux.org/epel/zfs-release-2-3.el8.noarch.rpm)、[EL9](https://zfsonlinux.org/epel/zfs-release-2-3.el9.noarch.rpm)、[EL10](https://zfsonlinux.org/epel/zfs-release-3-0.el10.noarch.rpm)

**归档发行版软件包：** [参见仓库页面](https://github.com/zfsonlinux/zfsonlinux.github.com/tree/master/epel)

**签名密钥 1（EL8 及之前版本，Fedora 36 及之前版本）** [pgp.mit.edu](https://pgp.mit.edu/pks/lookup?search=0xF14AB620&op=index&fingerprint=on) / [直链](https://raw.githubusercontent.com/zfsonlinux/zfsonlinux.github.com/master/zfs-release/RPM-GPG-KEY-openzfs-key1)

**指纹：** C93A FFFD 9F3F 7B03 C310 CEB6 A9D5 A1C0 F14A B620

**签名密钥 2（EL9+，Fedora 37+）** [pgp.mit.edu](https://pgp.mit.edu/pks/lookup?search=0xA599FD5E9DB84141&op=index&fingerprint=on) / [直链](https://raw.githubusercontent.com/zfsonlinux/zfsonlinux.github.com/master/zfs-release/RPM-GPG-KEY-openzfs-key2)

**指纹：** 7DC7 299D CF7C 7FD9 CD87 701B A599 FD5E 9DB8 4141

对于 EL7，运行：

```sh
yum install https://zfsonlinux.org/epel/zfs-release-2-3$(rpm --eval "%{dist}").noarch.rpm
```

对于 EL8-10，运行：

```sh
dnf install https://zfsonlinux.org/epel/zfs-release-3-0$(rpm --eval "%{dist}").noarch.rpm
```

安装 *zfs-release* 软件包并验证公钥后，用户可以选择安装 DKMS 或 kABI-tracking kmod 风格的软件包。对于运行非发行版内核或希望对 OpenZFS 进行本地定制的用户，推荐使用 DKMS 软件包。大多数用户则推荐使用 kABI-tracking kmod 软件包，以避免每次内核更新都需要重建 OpenZFS。

## DKMS

安装 DKMS 风格的软件包，请执行以下命令。首先添加提供 DKMS 的 [EPEL 仓库](https://fedoraproject.org/wiki/EPEL)，安装 *epel-release* 软件包，然后安装 *kernel-devel* 和 *zfs* 软件包。请确保为当前运行的内核安装匹配的 *kernel-devel* 软件包，因为 DKMS 需要它来构建 OpenZFS。

对于 EL6 和 EL7，分别运行：

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
>从 DKMS 切换到 kABI-tracking kmod 时，先卸载现有的 DKMS 软件包。这会删除所有已安装内核的模块，然后再按下文说明安装 kABI-tracking kmod。

## kABI-tracking kmod

默认情况下，*zfs-release* 软件包配置为安装 DKMS 风格的软件包，以兼容大多数的内核。若要安装 kABI-tracking kmod，需要将默认仓库从 *zfs* 切换到 *zfs-kmod*。请注意，kABI-tracking kmod 仅验证可用于发行版提供的、非 Stream 内核。

对于 EL6 和 EL7，运行：

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

默认情况下，当检测到 ZFS pool 时，OpenZFS 内核模块会自动加载。如果希望在启动时始终加载这些模块，可以在 `/etc/modules-load.d` 中创建配置：

```sh
echo zfs >/etc/modules-load.d/zfs.conf
```

>**注意**
>
>当升级到新的 EL 次版本时，现有 kmod 软件包可能因内核上游 kABI 变更而无法工作。当前发行版软件包的配置可能已提供更新的软件包，但如果版本号不比已安装的高，包管理器可能不会自动安装。在升级时，用户应确认 *kmod-zfs* 软件包提供了合适的内核模块，如有必要重新安装 *kmod-zfs* 软件包。

## 以前的次版本 EL 发行版

当前发行版软件包使用 `${releasever}` 而非指定具体次版本，这与以前的软件包方式不同。通常，会将 `${releasever}` 解析为主版本（如 8），仓库 URL 会自动指向当前次版本（如 8.7），但你可以通过 `--releasever` 指定使用以前的仓库版本。

示例：

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

在上例中，前面的软件包为 EL8.7 构建，后面的为 EL8.6 构建。

## 测试仓库

除了主要的 *zfs* 仓库外，还提供 *zfs-testing* 仓库。该仓库默认禁用，包含正在积极开发的 OpenZFS 最新版本。提供此仓库的目的是收集用户反馈，测试即将发布的功能和稳定性。**不应在生产系统中使用**。安装方式如下：

对于 EL6 和 EL7，运行：

```sh
yum-config-manager --enable zfs-testing
yum install kernel-devel zfs
```

对于 EL8 及更新版本，运行：

```sh
dnf config-manager --enable zfs-testing
dnf install kernel-devel zfs
```

**注意**

* zfs-testing 用于 DKMS 软件包
* zfs-testing-kmod 用于 kABI-tracking kmod 软件包
