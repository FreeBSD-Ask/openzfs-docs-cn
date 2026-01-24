# 在 Fedora 中启用 ZFS 支持

## 安装

>**注意**：
>
>本指南适用于在既有 Fedora 系统上安装 ZFS。若要将 ZFS 用作根文件系统，请参见下文。

1. 如果系统中已安装官方 Fedora 仓库的 `zfs-fuse`，请先卸载。该软件包已不再维护，在任何情况下都不应使用：

   ```sh
   rpm -e --nodeps zfs-fuse
   ```

2. 添加 ZFS 仓库：

   ```sh
   dnf install -y https://zfsonlinux.org/fedora/zfs-release-3-0$(rpm --eval "%{dist}").noarch.rpm
   ```

   可在 [这里](https://github.com/zfsonlinux/zfsonlinux.github.com/tree/master/fedora) 查看旧版 zfs-release RPM 清单。
3. 安装内核头文件：

   ```sh
   dnf install -y kernel-devel-$(uname -r | awk -F'-' '{print $1}')
   ```

   必须在安装软件包 `zfs` 之前先安装软件包 `kernel-devel`。
4. 安装 ZFS 软件包：

   ```sh
   dnf install -y zfs
   ```

5. 加载内核模块：

   ```sh
   modprobe zfs
   ```

   如果无法加载内核模块，可能是因为 OpenZFS 尚未支持你的内核版本。
   一种选择是使用第三方提供的 COPR LTS 内核，风险自负：

   ```sh
   # 这是第三方仓库！
   # 我们已经警告过你了！
   #
   # 从以下地址选择内核：
   # https://copr.fedorainfracloud.org/coprs/kwizart/

   dnf copr enable -y kwizart/kernel-longterm-VERSION
   dnf install -y kernel-longterm kernel-longterm-devel
   ```

   重启到新的 LTS 内核后，再加载内核模块：

   ```sh
   modprobe zfs
   ```

6. 在默认情况下，当检测到存储池时，将自动加载 ZFS 内核模块。若要在开机时始终加载模块：

   ```sh
   echo zfs > /etc/modules-load.d/zfs.conf
   ```

7. 在默认情况下，ZFS 可能会因内核软件包更新而被卸载。可通过锁定内核版本，仅允许 ZFS 支持的内核，以防止被卸载：

   ```sh
   echo 'zfs' > /etc/dnf/protected.d/zfs.conf
   ```

   除内核外的软件更新仍可进行：

   ```sh
   dnf update --exclude=kernel*
   ```

## 测试仓库

默认禁用的测试仓库包含最新版本的 OpenZFS，正在积极开发中。**不应** 将这些软件包用于生产环境。

```sh
dnf config-manager --enable zfs-testing
```
