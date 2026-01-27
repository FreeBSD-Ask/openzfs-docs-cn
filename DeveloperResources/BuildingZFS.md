# 构建 ZFS

## GitHub 仓库

OpenZFS 的官方源代码由 [openzfs](https://github.com/openzfs/) 组织在 GitHub 上维护。该项目的主要 git 仓库是 [zfs](https://github.com/openzfs/zfs)。

该仓库中有两个主要组成部分：

* **ZFS**：ZFS 仓库是上游的 OpenZFS 代码，该代码已针对 Linux 和 FreeBSD 进行了适配和扩展。绝大多数核心 OpenZFS 代码是自包含的，可以无需修改直接使用。
* **SPL**：SPL 是个轻的 shim 层，负责实现 OpenZFS 所需的基础接口。正是这一层使 OpenZFS 能够在多个平台上使用。SPL 以前在单独的仓库中维护，但在 `0.8` 主版本中被合并进 [zfs](https://github.com/openzfs/zfs) 仓库。

## 安装依赖

首先需要通过安装完整的开发工具链来准备你的环境。此外，还必须具备内核以及以下软件包的开发头文件。需要注意的是，如果当前运行内核的开发内核头文件未安装，模块将无法正确编译。

要构建最新 ZFS 2.1 版本需要安装以下依赖。

* **RHEL/CentOS 7**：

```sh
sudo yum install epel-release gcc make autoconf automake libtool rpm-build libtirpc-devel libblkid-devel libuuid-devel libudev-devel openssl-devel zlib-devel libaio-devel libattr-devel elfutils-libelf-devel kernel-devel-$(uname -r) python python2-devel python-setuptools python-cffi libffi-devel git ncompress libcurl-devel
sudo yum install --enablerepo=epel python-packaging dkms
```

* **RHEL/CentOS 8, Fedora**：

```sh
sudo dnf install --skip-broken epel-release gcc make autoconf automake libtool rpm-build libtirpc-devel libblkid-devel libuuid-devel libudev-devel openssl-devel zlib-devel libaio-devel libattr-devel elfutils-libelf-devel kernel-devel-$(uname -r) python3 python3-devel python3-setuptools python3-cffi libffi-devel git ncompress libcurl-devel
sudo dnf install --skip-broken --enablerepo=epel --enablerepo=powertools python3-packaging dkms
```

* **Debian、Ubuntu**：

```sh
sudo apt install alien autoconf automake build-essential debhelper-compat dh-autoreconf dh-dkms dh-python dkms fakeroot gawk git libaio-dev libattr1-dev libblkid-dev libcurl4-openssl-dev libelf-dev libffi-dev libpam0g-dev libssl-dev libtirpc-dev libtool libudev-dev linux-headers-generic parallel po-debconf python3 python3-all-dev python3-cffi python3-dev python3-packaging python3-setuptools python3-sphinx uuid-dev zlib1g-dev
```

* **FreeBSD**：

```sh
pkg install autoconf automake autotools git gmake python devel/py-sysctl sudo
```

## 构建选项

构建 OpenZFS 有两种方案；如何选择在很大程度上取决于你的需求。

* **软件包**：通常，从 git 构建可安装到系统上的自定义软件包是很有用的。这是进行与 systemd、dracut 和 udev 集成测试的最佳方式。使用软件包的缺点是会大大增加构建、安装和测试每次更改所需的时间。
* **树内**：开发可以完全在 SPL/ZFS 源码树内完成。这通过赋能开发者快速迭代补丁来加快开发速度。在树内工作时，开发者可以利用增量构建、加载/卸载内核模块、执行工具，然后使用 ZFS 测试套件验证所有更改。

本页其余部分重点介绍 **树内** 方案，这是大多数修改推荐的开发方法。有关构建自定义软件包的更多信息，请参阅 [自定义软件包](https://openzfs.github.io/openzfs-docs/Developer%20Resources/Custom%20Packages.html) 页面。

## 树内开发

### 从 GitHub 克隆

首先从 GitHub 克隆 ZFS 仓库。该仓库有一个用于开发的 **master** 分支，以及一系列用于带标签发布的 ***-release** 分支。检出仓库后，你的克隆将默认位于 master 分支。可以通过检出具有匹配版本号的 zfs-x.y.z 标签或匹配的发布分支来构建带标签的发布版本。

```sh
git clone https://github.com/openzfs/zfs
```

### 配置与构建

对于那些正在进行修改的开发者，应始终基于 master 创建新的主题分支。这样可以方便你之后为更改打开 pull request。master 分支通过在每个 pull request 合并前后进行海量的 [回归测试](http://build.zfsonlinux.org/) 来保持稳定。我们尽一切努力尽早发现缺陷，并将其排除在源码树之外。开发者应当习惯于频繁地将自己的工作 rebase 到最新的 master 分支之上。

在本示例中，我们将使用 master 分支，演示标准的 **树内** 构建。首先检出所需的分支，然后以传统的 autotools 方式构建 ZFS 和 SPL 源码。

```sh
cd ./zfs
git checkout master
sh autogen.sh
./configure
make -s -j$(nproc)
```


>**提示：**
>
>可以向 configure 传递 `--with-linux=PATH` 和 `--with-linux-obj=PATH`，来指定安装在非默认位置的内核。

>**提示：**
>
> 可以向 configure 传递 `--enable-debug`，来启用所有 ASSERT 以及额外的正确性测试。

可选：构建软件包

```sh
make rpm # 构建用于 CentOS/Fedora 的 RPM 软件包
make deb # 构建由 RPM 转换而来的 Debian/Ubuntu 的 DEB 软件包
make native-deb # 构建用于 Debian/Ubuntu 的原生 DEB 软件包
```

>**技巧**
>
>原生 Debian 软件包使用为 Debian 和 Ubuntu 预配置的路径进行构建。最好不要在 configure 阶段覆盖这些路径。

>**技巧**
>
>对于原生 Debian 软件包，可以导出 `KVERS`、`KSRC` 和 `KOBJ` 环境变量，以指定安装在非默认位置的内核。

>**注意**
>
>对原生 Debian 打包的支持将从 openzfs-2.2 版本开始提供。

### 安装

你可以在不安装 ZFS 的情况下运行 `zfs-tests.sh`，见下文。如果你在构建之后有理由安装 ZFS，请注意你的发行版是如何处理内核模块的。例如，在 Ubuntu 上，该仓库中的模块会安装到内核模块路径 `extra` 中，而该路径不在标准的 `depmod` 搜索路径内。因此，在测试期间，需要编辑 `/etc/depmod.d/ubuntu.conf`，并将 `extra` 添加到搜索路径的开头。

随后你可以使用 `sudo make install; sudo ldconfig; sudo depmod` 进行安装。卸载则使用 `sudo make uninstall; sudo ldconfig; sudo depmod`。你也可以仅安装内核模块，使用 `sudo make -C modules/ install`。

### 运行 zloop.sh 和 zfs-tests.sh

如果你希望运行 ZFS 测试套件（ZTS），则必须安装 `ksh` 以及一些额外的工具。

* **RHEL/CentOS 7:**

```sh
sudo yum install ksh bc bzip2 fio acl sysstat mdadm lsscsi parted attr nfs-utils samba rng-tools pax perf
sudo yum install --enablerepo=epel dbench
```

* **RHEL/CentOS 8, Fedora:**

```sh
sudo dnf install --skip-broken ksh bc bzip2 fio acl sysstat mdadm lsscsi parted attr nfs-utils samba rng-tools pax perf
sudo dnf install --skip-broken --enablerepo=epel dbench
```

* **Debian：**

```sh
sudo apt install ksh bc bzip2 fio acl sysstat mdadm lsscsi parted attr dbench nfs-kernel-server samba rng-tools pax linux-perf selinux-utils quota
```

* **Ubuntu：**

```sh
sudo apt install ksh bc bzip2 fio acl sysstat mdadm lsscsi parted attr dbench nfs-kernel-server samba rng-tools pax linux-tools-common selinux-utils quota
```

* **FreeBSD**：

```sh
pkg install base64 bash checkbashisms fio hs-ShellCheck ksh93 pamtester devel/py-flake8 sudo
```

在顶层 scripts 目录中提供了一些辅助脚本，可帮助开发者进行树内构建开发。

* **zfs-helpers.sh** 某些功能（例如 `/dev/zvol/`）依赖于系统中已安装的 ZFS 提供的 udev 辅助脚本。该脚本可用于在系统中从安装位置到树内辅助脚本创建符号链接。要成功运行 ZFS 测试套件，必须存在这些链接。可以使用选项 **-i** 和 **-r** 来安装和移除这些符号链接。

```sh
sudo ./scripts/zfs-helpers.sh -i
```

* **zfs.sh** 可以使用 `zfs.sh` 加载新构建的内核模块。之后可以使用选项 **-u** 通过该脚本卸载内核模块。

```sh
sudo ./scripts/zfs.sh
```

* **zloop.sh** 用于使用随机参数反复运行 ztest 的封装脚本。ztest 命令是用户空间的压力测试工具，通过并发运行一组随机测试用例来检测正确性问题。如果发生崩溃，将收集 ztest 日志、一切相关的 vdev 文件以及转储文件（如有），然后将其移动到输出目录以供分析。

```sh
sudo ./scripts/zloop.sh
```

* **zfs-tests.sh** 用于启动 ZFS 测试套件的封装脚本。在 `/var/tmp/` 中的稀疏文件之上创建三个回环设备，并用于回归测试。有关 ZFS 测试套件的详细说明，可在顶层 tests 目录中的 [README](https://github.com/openzfs/zfs/tree/master/tests) 中找到。

```sh
./scripts/zfs-tests.sh -vx
```

>**提示：**
>
>除非为 zfs 目录及其父目录设置了组读权限，否则将跳过 **delegate** 测试。
