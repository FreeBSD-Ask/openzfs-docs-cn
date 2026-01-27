# 自定义软件包

以下说明假定你是从官方的 [tar 发行版压缩包](https://github.com/zfsonlinux/zfs/releases/latest)（版本 0.8.0 或更新）或直接从 [git 仓库](https://github.com/zfsonlinux/zfs) 进行构建。大多数用户不需要这样做，应优先使用发行版提供的软件包。一般而言，发行版的软件包集成度更高、经过广泛测试、支持更完善。然而，如果你选择的发行版未提供软件包，或者你是开发者并想自己构建，下面是操作方法。

首先需要注意的是，构建系统能够生成几种不同类型的软件包。要选择的软件包类型取决于你的平台支持情况以及具体需求。

* **DKMS** 软件包只包含用于重建内核模块的源代码和脚本。安装 DKMS 软件包后，将为所有可用内核构建内核模块。此外，当更新内核时，会自动为该内核构建新的内核模块。这对于经常接收内核更新的桌面系统尤其方便。缺点是由于 DKMS 软件包从源代码构建内核模块，因此需要完整的开发环境，这对于大规模部署可能不合适。
* **kmods** 软件包是针对特定内核版本编译的二进制内核模块。这意味着如果你更新内核，必须编译、安装新的 kmod 软件包。如果你不经常更新内核，或者管理着大批量系统，那么 kmod 软件包是个不错的选择。
* **kABI-tracking kmod** 软件包类似于标准的二进制 kmods，可用于企业级 Linux 发行版，如 Red Hat 和 CentOS。这些发行版提供稳定的 kABI（内核应用二进制接口），可在提供的新版本发行版内核上使用相同的二进制模块。注意，这些软件包并不完全遵循 Red Hat 的规则，因此在新内核上有小概率失败的可能性。概率较低，但我们建议在生产服务器上使用这些构建时禁用自动内核更新。

在默认情况下，构建系统将生成用户软件包，并同时生成 DKMS 和 kmod 风格的内核软件包（如果可能）。用户软件包可与任一内核软件包一起使用，在内核更新时无需重新构建用户软件包。你也可以通过仅构建 DKMS 或 kmod 软件包来简化构建过程，如下所示。

请注意，当直接从 git 仓库构建时，必须首先运行 *autogen.sh* 脚本来生成 *configure* 脚本。这需要安装对应发行版的软件包 GNU autotools。要执行任何构建，必须安装该发行版所需的所有开发工具和头文件。

需要注意，如果当前运行的内核的开发内核头文件未安装，将无法正确编译模块。

* [Red Hat、CentOS 和 Fedora](https://openzfs.github.io/openzfs-docs/Developer%20Resources/Custom%20Packages.html#red-hat-centos-and-fedora)
* [Debian 和 Ubuntu](https://openzfs.github.io/openzfs-docs/Developer%20Resources/Custom%20Packages.html#debian-and-ubuntu)

## RHEL、CentOS 和 Fedora

确保已安装构建最新 ZFS 2.1 版本所需的软件包：

* **RHEL/CentOS 7**：

```sh
sudo yum install epel-release gcc make autoconf automake libtool rpm-build libtirpc-devel libblkid-devel libuuid-devel libudev-devel openssl-devel zlib-devel libaio-devel libattr-devel elfutils-libelf-devel kernel-devel-$(uname -r) python python2-devel python-setuptools python-cffi libffi-devel ncompress
sudo yum install --enablerepo=epel dkms python-packaging
```

**注意：** RHEL/CentOS 7 生命周期已结束。在下面的安装说明中请使用 dnf 而非 yum。

* **RHEL/CentOS 8**：

```sh
sudo dnf install --skip-broken epel-release gcc make autoconf automake libtool rpm-build kernel-rpm-macros libtirpc-devel libblkid-devel libuuid-devel libudev-devel openssl-devel zlib-devel libaio-devel libattr-devel elfutils-libelf-devel kernel-devel-$(uname -r) kernel-abi-stablelists-$(uname -r | sed 's/\.[^.]\+$//') python3 python3-devel python3-setuptools python3-cffi libffi-devel ncompress
sudo dnf install --skip-broken --enablerepo=epel --enablerepo=powertools python3-packaging dkms
```

* **RHEL/CentOS 9**：

```sh
sudo dnf config-manager --set-enabled crb
sudo dnf install --skip-broken epel-release gcc make autoconf automake libtool rpm-build kernel-rpm-macros libtirpc-devel libblkid-devel libuuid-devel libudev-devel openssl-devel zlib-devel libaio-devel libattr-devel elfutils-libelf-devel kernel-devel-$(uname -r) kernel-abi-stablelists-$(uname -r | sed 's/\.[^.]\+$//') python3 python3-devel python3-setuptools python3-cffi libffi-devel
sudo dnf install --skip-broken --enablerepo=epel python3-packaging dkms
```

* **Fedora 41**：

```sh
sudo dnf install gcc make autoconf automake libtool rpm-build kernel-rpm-macros libtirpc-devel libblkid-devel libuuid-devel systemd-devel openssl-devel zlib-ng-compat-devel libaio-devel libattr-devel libffi-devel libunwind-devel kernel-devel-$(uname -r) python3 python3-devel openssl ncompress
sudo dnf install python3-packaging dkms
```

[下载源代码](https://openzfs.github.io/openzfs-docs/Developer%20Resources/Custom%20Packages.html#get-the-source-code)。

### DKMS

基于 rpm 的 DKMS 和用户软件包可以按如下方式构建：

```sh
$ cd zfs
$ ./configure
$ make -j1 rpm-utils rpm-dkms
$ sudo dnf install *.$(uname -m).rpm *.noarch.rpm
```

### kmod

在构建 kmod 软件包时，需要注意的关键点是必须指定特定的 Linux 内核。在配置阶段，构建系统会根据经验猜测你希望针对哪个内核构建。然而，如果 configure 找不到你的内核开发头文件，或者你想针对不同内核构建，则必须使用选项 *--with-linux* 和 *--with-linux-obj* 指定确切路径。

```sh
$ cd zfs
$ ./configure
$ make -j1 rpm-utils rpm-kmod
$ sudo dnf install *.$(uname -m).rpm *.noarch.rpm
```

>**注意：**
>
>Fedora 41 Workstation 内置 rpm 软件包 zfs-fuse，会妨碍安装你自己的软件包。在执行 `dnf install` 之前请先仅删除该软件包：

```sh
$ sudo rpm -e --nodeps zfs-fuse
```

### kABI-tracking kmod

构建 kABI-tracking kmod 的过程与构建普通 kmod 几乎相同。然而，仅在该发行版支持稳定 kABI 的情况下，才会生成可被多个内核使用的二进制文件。要请求 kABI-tracking 软件包，必须在 configure 时传入选项 *–-with-spec=redhat*。

请注意，这些软件包并不完全遵循 Red Hat 的规则，因此有小概率在新内核上无法使用。我们建议在生产服务器上使用这些构建时禁用自动内核更新。

>**注意：**
>
>这种类型的软件包在 Fedora 上不可用。

```sh
$ cd zfs
$ ./configure --with-spec=redhat
$ make -j1 rpm-utils rpm-kmod
$ sudo dnf install *.$(uname -m).rpm *.noarch.rpm
```

### Fedora 41 使用 kmod 的安全启动

在使用 UEFI 和安全启动的现代计算机上，将无法加载 zfs 内核模块：

```sh
$ sudo modprobe zfs
modprobe: ERROR: could not insert 'zfs': Key was rejected by service
```

可以选择禁用安全启动，或者**只需一次性**创建自定义机器所有者密钥（MOK），并使用该密钥手动签名当前及未来的模块：

```sh
$ sudo mkdir /etc/pki/mok
$ cd /etc/pki/mok
$ sudo openssl req -new -x509 -newkey rsa:2048 -keyout LOCALMOK.priv -outform DER -out LOCALMOK.der -nodes -days 36500 -subj "/CN=LOCALMOK/"
$ sudo mokutil --import LOCALMOK.der
```

Mokutil 会要求你创建并记住密码，然后重启计算机，UEFI 将要求导入你的密钥：

```sh
选择 "Enroll MOK"、“Continue”、“Yes”，输入 mokutil 的密码，“Reboot”
```

之后可使用该 MOK 手动签名 zfs 内核模块：

```sh
$ rpm -ql kmod-zfs-$(uname -r) | grep .ko
/lib/modules/6.11.8-300.fc41.x86_64/extra/zfs/spl.ko
/lib/modules/6.11.8-300.fc41.x86_64/extra/zfs/zfs.ko
```

```
$ sudo /usr/src/kernels/$(uname -r)/scripts/sign-file sha256 /etc/pki/mok/LOCALMOK.priv /etc/pki/mok/LOCALMOK.der /lib/modules/$(uname -r)/extra/zfs/spl.ko
$ sudo /usr/src/kernels/$(uname -r)/scripts/sign-file sha256 /etc/pki/mok/LOCALMOK.priv /etc/pki/mok/LOCALMOK.der /lib/modules/$(uname -r)/extra/zfs/zfs.ko
```

加载模块，验证其已激活：

```sh
$ sudo modprobe zfs

$ lsmod | grep zfs
zfs                  6930432  0
spl                   155648  1 zfs
```

## Debian 和 Ubuntu

确保已安装所需的软件包：

```sh
sudo apt install alien autoconf automake build-essential debhelper-compat dh-dkms dh-python dkms fakeroot gawk libaio-dev libattr1-dev libblkid-dev libcurl4-openssl-dev libelf-dev libffi-dev libpam0g-dev libssl-dev libtirpc-dev libtool libudev-dev linux-headers-generic po-debconf python3 python3-all-dev python3-cffi python3-dev python3-packaging python3-setuptools python3-sphinx uuid-dev zlib1g-dev
```

[获取源代码](https://openzfs.github.io/openzfs-docs/Developer%20Resources/Custom%20Packages.html#get-the-source-code)。

### kmod

构建 kmod 软件包时需要注意的关键点是必须指定特定的 Linux 内核。在配置阶段，构建系统会根据经验猜测你希望针对哪个内核构建。然而，如果 configure 找不到你的内核开发头文件，或者你想针对不同内核构建，则必须使用 *--with-linux* 和 *--with-linux-obj* 选项指定确切路径。

要构建 RPM 转换的 Debian 软件包：

```sh
$ cd zfs
$ ./configure --enable-systemd
$ make -j1 deb-utils deb-kmod
$ sudo apt-get install --fix-missing ./*.deb
```

从 openzfs-2.2 版本开始，可以按如下方式构建原生 Debian 软件包：

```sh
$ cd zfs
$ ./configure
$ make native-deb-utils native-deb-kmod
$ rm ../openzfs-zfs-dkms_*.deb
$ rm ../openzfs-zfs-dracut_*.deb  # 基于 deb 的系统通常使用 initramfs
$ sudo apt-get install --fix-missing ../*.deb
```

原生 Debian 软件包使用为 Debian 和 Ubuntu 预配置的路径构建。在 configure 阶段最好不要覆盖这些路径。可以通过指定环境变量 `KVERS`、`KSRC` 和 `KOBJ` 来指定安装在非默认位置的内核。

### DKMS

构建 RPM 转换的基于 deb 的 DKMS 和用户软件包可以按如下方式进行：

```sh
$ cd zfs
$ ./configure --enable-systemd
$ make -j1 deb-utils deb-dkms
$ sudo apt-get install --fix-missing ./*.deb
```

从 openzfs-2.2 版本开始，可以按如下方式构建原生基于 deb 的 DKMS 和用户软件包：

```sh
$ sudo apt-get install dh-dkms
$ cd zfs
$ ./configure
$ make native-deb-utils
$ rm ../openzfs-zfs-dracut_*.deb  # 基于 deb 的系统通常使用 initramfs
$ sudo apt-get install --fix-missing ../*.deb
```

## 获取源代码

### 发布 Tar 归档包

发布的 Tar 归档包是经过充分测试和已发布的最新 ZFS 版本。这是生产系统中使用的首选源代码位置。如果你想使用官方发布的 Tar 归档包，可以使用以下命令获取、准备源代码：

```sh
$ wget http://archive.zfsonlinux.org/downloads/zfsonlinux/zfs/zfs-x.y.z.tar.gz
$ tar -xzf zfs-x.y.z.tar.gz
```

### Git 主分支

Git *master* 分支是最新版本的软件，且可能包含那些未内置在已发布 Tar 归档包中的修复。这是打算修改 ZFS 的开发者的首选源代码位置。如果你想使用 git 版本，可以从 Github 克隆并按如下方式准备源代码：

```sh
$ git clone https://github.com/zfsonlinux/zfs.git
$ cd zfs
$ ./autogen.sh
```

源代码准备完成后，你需要决定构建哪种类型的软件包，然后跳转到上面的相应部分。请注意，并非所有平台都支持所有类型的软件包。
