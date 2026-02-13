# 在 Fedora 中启用 ZFS 支持

## 安装

>**注意**
>
>以下内容适用于在已有的 Fedora 系统上安装 ZFS。如需将 ZFS 用作根文件系统，请见下文。

1. 如果已安装来自官方 Fedora 仓库的 `zfs-fuse`，请先卸载它。该软件包已不再维护，任何情况下都不应使用：

   ```sh
   rpm -e --nodeps zfs-fuse
   ```

2. 添加 ZFS 仓库：

   ```sh
   dnf install -y https://zfsonlinux.org/fedora/zfs-release-3-0$(rpm --eval "%{dist}").noarch.rpm
   ```

   旧版 zfs-release RPM 列表可见 [此处](https://github.com/zfsonlinux/zfsonlinux.github.com/tree/master/fedora)。

3. 安装内核头文件：

   ```sh
   dnf install -y kernel-devel-$(uname -r | awk -F'-' '{print $1}')
   ```

   必须先安装软件包 `kernel-devel`，然后才能安装软件包 `zfs`。

4. 安装 ZFS 软件包：

   ```sh
   dnf install -y zfs
   ```

5. 加载内核模块：

   ```sh
   modprobe zfs
   ```

   如果无法加载内核模块，说明当前内核版本可能尚不被 OpenZFS 支持。一个方案是使用第三方提供的 COPR LTS 内核，请自行承担风险：

   ```sh
   # 这是第三方仓库！
   # 你已经被警告过了。
   #
   # 可从以下地址选择内核：
   # https://copr.fedorainfracloud.org/coprs/kwizart/

   dnf copr enable -y kwizart/kernel-longterm-VERSION
   dnf install -y kernel-longterm kernel-longterm-devel
   ```

   重启至新的 LTS 内核，然后加载内核模块：

   ```sh
   modprobe zfs
   ```

6. 默认情况下，检测到池时 ZFS 内核模块会自动加载。若希望在启动时始终加载模块，可创建如下配置：

   ```sh
   echo zfs > /etc/modules-load.d/zfs.conf
   ```

7. 默认情况下，ZFS 可能会因内核软件包更新而被移除。若希望锁定内核版本，仅使用 ZFS 支持的内核以防止被卸载，可执行：

   ```sh
   echo 'zfs' > /etc/dnf/protected.d/zfs.conf
   ```

   未完成的非内核更新仍可执行：

   ```sh
   dnf update --exclude=kernel*
   ```

## 最新仓库（Fedora 41+）

*zfs-latest* 仓库包含最新发布的、正在积极开发的 OpenZFS 版本。它将包含最新功能，并被认为是稳定的，但实际使用测试较少，相比 *zfs-legacy*。该仓库相当于 Fedora 的默认 *zfs* 仓库。来自最新仓库的软件包可按如下方式安装。

对于 Fedora 41 及更新版本，运行：

```sh
sudo dnf config-manager setopt zfs*.enabled=0
sudo dnf config-manager setopt zfs-latest.enabled=1
sudo dnf install zfs
```

## 传统仓库（Fedora 41+）

*zfs-legacy* 仓库包含以前发布的、仍在积极更新的 OpenZFS 版本。通常，该仓库提供的软件包与 RHEL 和 CentOS 基础发行版的主 *zfs* 仓库相同。来自传统仓库的软件包可按如下方式安装。

对于 Fedora 41 及更新版本，运行：

```sh
sudo dnf config-manager setopt zfs*.enabled=0
sudo dnf config-manager setopt zfs-legacy.enabled=1
sudo dnf install zfs
```

## 版本特定仓库（Fedora 41+）

版本特定仓库为希望运行特定分支（例如 2.3.x）ZFS 的用户提供。来自版本特定仓库的软件包可按如下方式安装。

对于 Fedora 41 及更新版本，启用 ZFS 分支 x.y 的版本特定仓库，运行：

```sh
sudo dnf config-manager setopt zfs*.enabled=0
sudo dnf config-manager setopt zfs-x.y.enabled=1
sudo dnf install zfs
```

## 测试仓库（已弃用）

*zfs-testing* 仓库已弃用，推荐使用 *zfs-latest*。
