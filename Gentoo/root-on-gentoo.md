# 构建以 ZFS 为根文件系统的 Gentoo

- 原文地址：[wiki/ZFS](https://wiki.gentoo.org/wiki/ZFS)，版本 2026 年 1 月 12 日 (星期一) 07:58。

本文重点介绍在 Gentoo 上将 ZFS 用作根文件系统，并设计为配合手册使用。随着时间推移，将会加入更多高级配置，请查看 TODO 部分，以了解是否有可添加内容以改进本文。


#### 分区

##### 布局

请参考 Handbook 中的[准备磁盘](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/Disks)部分，回到创建文件系统的章节。

本指南将使用下面的示例，但应足够简单以适应用户的实际需求。

```sh
/dev/sda1   | 1024 MiB      | EFI 系统分区         | /efi
/dev/sda2   | 2048 MiB      | swap                  | swap
/dev/sda3   | 剩余磁盘空间  | ZFS 分区              | /, /boot, /home, ...
```

##### 引导

创建 1GB FAT32 文件系统：

```sh
mkfs.vfat -F 32 /dev/sda1
```

##### 交换分区

在 ZFS 分区上 swap 性能较差，并且不支持使用 swapfile，因此建议使用单独的分区。

```sh
mkswap /dev/sda2
swapon /dev/sda2
```

>**注意**
>
>或者，在内存充足的系统上可以使用 zram，但请注意 ZFS 会将数据缓存到内存来提升速度。

#### ZFS 设置

##### 生成主机 ID

随机生成主机 ID 到 `/etc/hostid`，可覆盖输出。

```sh
zgenhostid -f
```

或者，设置特定主机 ID，本例中为 `0x00bab10c`。

```sh
zgenhostid -f 0x00bab10c
```

##### 创建 ZFS 池

加载 ZFS 内核模块，在 `/dev/sda3` 上创建 ZFS 池 `tank`。

```sh
modprobe zfs
zpool create -f \
-o ashift=12 \
-o autotrim=on \
-o compatibility=grub2 \
-O acltype=posixacl \
-O xattr=sa \
-O relatime=on \
-O compression=lz4 \
-m none tank /dev/sda3
```

>**注意**
>
>选项 `-o compatibility=grub2` 将确保 GRUB 能正常工作。如果使用 ZFSBootMenu，可以跳过此选项。

>**警告**
>
>对于物理扇区大小为 512 字节的磁盘，请使用 `-o ashift=9`；对于物理扇区大小为 4096 字节的磁盘，请使用 `-o ashift=12`。详见 [OpenZFS: ashift 属性定义](https://openzfs.github.io/openzfs-docs/man/v2.4/7/zpoolprops.7.html#ashift)。

##### 可选方案：使用原生加密创建 ZFS 池

>**警告**
>
>不建议使用原生加密，因为上游目前未维护此功能，详见 [https://github.com/openzfs/zfs/issues/12014](https://github.com/openzfs/zfs/issues/12014) 和 [https://github.com/openzfs/openzfs-docs/issues/494](https://github.com/openzfs/openzfs-docs/issues/494)。请优先使用 LUKS。

在创建 zpool 时，也可以通过添加额外的选项使用原生 ZFS 加密：

```sh
zpool create -f -o ashift=12 \
  -o autotrim=on \
  -o compatibility=openzfs-2.1-linux \
  -O acltype=posixacl \
  -O xattr=sa \
  -O relatime=on \
  -O compression=lz4 \
  -O encryption=aes-256-gcm \
  -O keylocation=prompt \
  -O keyformat=passphrase \
  -m none tank /dev/sda3
```

>**注意**
>
>也可以将属性 `keylocation` 设置为指向某个文件，这在使用 ZFSBootMenu 作为引导加载器时非常有用，或者在启动时希望减少输入密码次数时也可用。[参见 ZFSBootMenu 文档](https://docs.zfsbootmenu.org/en/v2.3.x/general/native-encryption.html) 了解其对加密文件系统的处理方式。

##### 创建 ZFS 文件系统

本指南只创建了 root 和 home 文件系统，但用户可根据需要创建更多文件系统。

```sh
zfs create -o mountpoint=none tank/os
zfs create -o mountpoint=/ -o canmount=noauto tank/os/gentoo
zfs create -o mountpoint=/home tank/home
```

>**注意**
>
>具有根挂载点的文件系统应设置属性 `canmount=noauto`。若省略此属性，操作系统可能会尝试自动挂载多个文件系统到 `/`，然后失败。如果打算将 `/usr`、`/etc` 或其他系统关键目录放在不同的数据集上，需确保它是根数据集的子数据集（例如 `tank/os/gentoo/usr`），并且 `canmount=on`，这样由 dracut 生成的 initramfs 才能被正确挂载。

设置池的首选引导文件系统：

```sh
zpool set bootfs=tank/os/gentoo tank
```

##### 导出并重新导入池，挂载文件系统

要导出并重新导入池，同时指定挂载点并且不自动挂载文件系统，请运行以下命令：

```sh
zpool export tank
zpool import -N -R /mnt/gentoo tank
```

然后可以挂载 root 和 home 文件系统。

>**注意**
>
>如果使用了原生加密，请先加载 ZFS 密钥：

```sh
zfs load-key tank
```

挂载文件系统：

```sh
zfs mount tank/os/gentoo
zfs mount tank/home
```

如果按照示例操作，也可以挂载 `efi` 分区：

```sh
mount --mkdir /dev/sda1 /mnt/gentoo/efi
```

挂载文件系统后，建议通过以下命令检查挂载点是否正确：

```sh
mount -t zfs
```

成功挂载时的示例输出：

```sh
tank/os/gentoo /mnt/gentoo type zfs (rw,relatime,xattr,posixacl)
tank/home on /mnt/gentoo/home type zfs (rw,relatime,xattr,posixacl)
```

更新设备符号链接：

```sh
udevadm trigger
```

返回 Handbook - [EFI_system_partition_filesystem](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/Disks#EFI_system_partition_filesystem)，直到执行 `chroot` 命令前的位置。

##### 复制 host ID 文件

```sh
cp /etc/hostid /mnt/gentoo/etc
```

返回 Handbook - [Installing Gentoo base system](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/Base#Entering_the_new_environment)，继续进行内核配置和编译。

#### 内核

用户可以在手动配置的内核或发行版内核之间进行选择。

##### 发行版内核

###### 启用 USE 标志

如果使用发行版内核，则需要启用 USE 标志 `dist-kernel`：

文件 `/etc/portage/make.conf` 在 make.conf 中启用 USE 标志 **dist-kernel**

```ini
USE="dist-kernel"
```

###### 安装发行版内核

```sh
emerge -av sys-kernel/gentoo-kernel
```

或者，如果你更喜欢使用预编译二进制，

```sh
emerge -av sys-kernel/gentoo-kernel-bin
```

##### 手动内核配置

按需配置内核，保存并构建（暂时不要安装）

```sh
make -j$(nproc) && make modules_install
```

安装 zfs 包（如果出现内核版本错误，请使用前一个版本）

```sh
emerge --ask sys-fs/zfs

然后在 dracut 中添加 zfs 内核模块，如前所述，同时将 `root=ZFS=tank/os/gentoo` 写入 `/etc/cmdline`，否则 initramfs 将无法构建。现在构建并安装，为简便起见使用 installkernel（已启用 USE 标志 dracut 和 grub）

```sh
make -j$(nproc) && make modules_install && make install
```

每次 gentoo-sources 被更新或内核配置被更改时都必须重复此操作，否则系统将无法启动。

#### ZFS 用户空间工具和内核模块

包 sys-fs/zfs 是必须的，它能让系统与 ZFS 池交互和管理。确保已设置模块标志：

```sh
emerge -av sys-fs/zfs
```

#### Initramfs

##### 配置 Dracut

如果不存在，为 Dracut 配置文件创建目录：

```sh
mkdir -p /etc/dracut.conf.d
```

然后，在该目录下创建文件 `zol.conf`，内容如下：

```sh
nano /etc/dracut.conf.d/zol.conf
```

ZFS 的 Dracut 配置文件 **/etc/dracut.conf.d/zol.conf**

```ini
nofsck="yes"
add_dracutmodules+=" zfs "
```

##### 为发行版内核构建 initramfs

```sh
emerge --config sys-kernel/gentoo-kernel
```

或者，如果安装了二进制版本，

```
emerge --config sys-kernel/gentoo-kernel-bin
```

你可以返回手册 - [配置系统](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/System)，然后在这里继续 [配置引导加载器](https://wiki.gentoo.org/wiki/Handbook:AMD64/Installation/Bootloader)。

#### 引导加载器

##### ZFSBootMenu

###### 设置内核命令行

```sh
zfs set org.zfsbootmenu:commandline="quiet loglevel=4" tank/os
```

>**注意**
>
>ZFS 属性会继承，因此 `tank/os` 的所有子数据集将继承该命令行参数。如有必要，可以在特定子数据集中覆盖该属性。

###### 挂载 EFI 系统分区


>**注意**
>
>[ZFSBootMenu 文档](https://docs.zfsbootmenu.org/en/v2.3.x/guides/general/bootenvs-and-you.html) 指出，内核和 initramfs 必须位于 ZFS 根目录的 `/boot` 下。然而，systemd 的 installkernel 会尝试定位 EFI 分区的挂载点并将内核-initramfs 对安装到那里，在我们的情况下为 `/efi`。因此，必须为 sys-kernel/installkernel 添加 USE 标志 `-systemd` 以防止出现这种问题。

如果 ESP 之前未挂载，现在需要挂载：

```sh
mkdir -p /efi
mount /dev/sda1 /efi
```

###### 从源码安装 ZFSBootMenu

可在 [GURU](https://wiki.gentoo.org/wiki/Project:GURU) 仓库中获得 ZFSBootMenu ebuild，若未添加需先添加：

```sh
emerge app-eselect/eselect-repository
eselect repository enable guru
emerge --sync
```

然后安装以下包：

```sh
emerge sys-boot/zfsbootmenu
```

之后，需要调整 ZFSBootMenu 配置以：

- 启用镜像自动管理：`ManageImages:true`
- 指向 EFI 挂载点：`BootMountPoint: /efi`
- 启用 EFI 二进制生成：EFI 部分 `Enabled: true`

ZFSBootMenu 配置文件 **/etc/zfsbootmenu/config.yaml**

```yaml
Global:
  ManageImages: true
  BootMountPoint: /efi
[...]
EFI:
  Enabled: true
```

然后生成引导加载器镜像：

```sh
generate-zbm
```

###### 安装 ZFSBootMenu（预构建）

为引导加载器创建目录并下载 EFI 二进制文件：

```sh
mkdir -p /efi/EFI/BOOT
curl -L https://get.zfsbootmenu.org/efi -o /efi/EFI/BOOT/BOOTX64.EFI
```

###### 创建 EFI 启动项

安装包 sys-boot/efibootmgr：

```sh
emerge -av sys-boot/efibootmgr
```

然后，如果 ZFSBootMenu 是从源码构建的，可使用以下命令创建 EFI 启动项：

```sh
efibootmgr -c -d /dev/sda -p 1 -L "ZFSBootMenu" -l \\EFI\\ZBM\\VMLINUZ.EFI
```

若使用预构建 ZFSBootMenu 二进制：

```sh
efibootmgr -c -d /dev/sda -p 1 -L "ZFSBootMenu" -l \\EFI\\BOOT\\BOOTX64.EFI
```

###### 可选：原生加密

如果在创建 zpool 时选择了原生加密，如 [Alternative: Create a ZFS pool with native encryption](https://wiki.gentoo.org/wiki/ZFS/rootfs#zpool_Native_Encryption) 所述，可以设置 ZFSBootMenu 仅提示一次密码，并让 dracut 在启动时访问加密密钥，或者通过设置 `org.zfsbootmenu:keysource` 属性并将密钥存储在单独的数据集中实现。

[参见 ZFSBootMenu 文档](https://docs.zfsbootmenu.org/en/v2.3.x/general/native-encryption.html) 了解正确设置方法。

##### Limine

Limine 是现代、先进、可移植、多协议的引导加载器和引导管理器，同时提供 Limine 引导协议的参考实现。

参照 [Limine](https://wiki.gentoo.org/wiki/Limine) 文章，并确保遵循 [Limine#Using_Limine_With_ZFS_Root](https://wiki.gentoo.org/wiki/Limine#Using_Limine_With_ZFS_Root) 部分。

##### 通用引导加载器（GRUB）

###### 为 GRUB 启用 ZFS 支持

在 sys-boot/grub 包上设置 libzfs 标志以启用 ZFS 支持（需要构建 sys-fs/zfs 和 sys-fs/zfs-kmod）：

```sh
echo "sys-boot/grub libzfs" >> /etc/portage/package.use/grub
```

###### 构建带 ZFS 支持的 GRUB

确保 GRUB_PLATFORMS 设置正确，以适用于带 EFI 分区的系统：

```sh
echo 'GRUB_PLATFORMS="efi-64"' >> /etc/portage/make.conf
```

构建包 sys-boot/grub：

```sh
emerge --ask sys-boot/grub
```

###### 将 GRUB 安装到已挂载的 EFI 分区

```sh
grub-install --target=x86_64-efi --efi-directory=/efi --bootloader-id=gentoo
grub-mkconfig -o /boot/grub/grub.cfg
```

#### 仅为首次启动添加 CMDLINE

```sh
nano /etc/default/grub
```

```sh
GRUB_CMDLINE_LINUX="refresh"
```

执行 `grub-mkconfig -o /boot/grub/grub.cfg`，启动进入 gentoo 后删除该项并重新配置 grub。

#### 完成设置

将 zfs-import 和 zfs-mount 添加到启动服务，否则系统将无法启动。

##### OpenRC

```sh
rc-update add zfs-import sysinit && rc-update add zfs-mount sysinit
```

#### 重启系统

退出 chroot 环境并卸载所有挂载的分区，不要忘记导出池。之后即可重启系统。

```sh
exit
cd
umount -l /mnt/gentoo/dev{/shm,/pts,}
umount -n -R /mnt/gentoo
zpool export tank
reboot
```

#### Gentoo 重启后无法启动

在 grub 条目中按 e 并在 cmdline 添加 "refresh"

#### 待办事项

需要添加的部分以完善指南：

- 添加 LUKS 加密
- 添加备用引导加载器说明
- 添加通过 `generate-zbm` 安装 ZFSBootMenu 的说明（可能需要使用 GURU）
