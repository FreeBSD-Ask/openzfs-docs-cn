# 构建以 ZFS 为根文件系统的 Slackware


本页面展示了一些将 Slackware 配置为使用 ZFS 作为根文件系统的可能方法。

实现这种设置的方法多种多样，特别是考虑到 ZFS 提供的灵活性。这里仅展示一个简单方案，并提供进一步自定义的指引。

## 内核考虑

在这个迷你教程中，我们将使用通用内核（generic kernel）并自定义默认的 initrd。

如果你使用的是 huge 内核，你可能需要先切换到通用内核，并安装 `kernel-generic` 和 `mkinitrd` 软件包。这会更方便，因为我们需要使用 initrd。

如果你完全不想使用 initrd，请参见下文“其他选项”。

## 问题空间

为了将根文件系统放在 ZFS 上，需要解决两个问题：

1. 引导加载程序必须能够加载内核及其 initrd。
2. 内核（或者说 initrd）必须能够挂载 ZFS 根文件系统并运行 `/sbin/init`。

第二个问题相对容易处理，只需对默认的 Slackware initrd 脚本进行少量修改即可。

第一个问题则存在多种可能情形。例如，在 PC 上，你可能会遇到以下启动方式：

1. UEFI 模式，通过额外的引导加载程序（如 elilo）：此时内核及 initrd 被放在 ESP 上，额外的引导程序无需理解 ZFS。
2. UEFI 模式，直接由固件启动内核：所有 Slackware 内核都启用了 `EFI_STUB=Y`，因此如果你将内核和 initrd 复制到 ESP 并用 `efibootmgr` 配置启动项即可（注意内核文件必须有 `.efi` 扩展名）。
3. 传统 BIOS 模式，使用 lilo 或 grub 等：lilo 不支持 ZFS，即使是最新的 grub 也只支持有限功能（例如，不支持 zstd 压缩）。如果必须使用传统 BIOS 模式，最佳方案是将 `/boot` 放在引导程序能识别的单独分区上（例如 ext4）。

如果你不是使用 PC，情况可能会大不相同，请参考对应平台的硬件文档。例如，在 Raspberry Pi 上，固件从 FAT32 分区加载内核和 initrd，因此情形类似于 PC 的 UEFI 启动。

本教程讨论的最简单设置是使用 UEFI。如果你在传统 BIOS 模式启动，必须确保所选引导程序能够加载内核映像。

## 分区布局

重新分区现有系统磁盘以为 ZFS 根分区腾出空间留给读者自行操作（这与 ZFS 本身无关）。

提示：如果你从一个完整的 ext4 文件系统开始，可以使用 `resize2fs` 将其缩小到磁盘大小的一半，然后用 `sfdisk` 将其移动到磁盘的后半部分。之后，你可以在前半部分创建 ZFS 分区，并使用 `cp` 或 `rsync` 复制数据。这种方法的好处是，如果出现问题，仍有一定的恢复机制。当你对最终设置满意后，可以删除 ext4 分区并扩展 ZFS 分区。

无论如何，建议准备一个救援 CD，并且该 CD 原生支持 ZFS。Ubuntu Live CD 即可满足需求。

在本教程中，假设我们在 UEFI 模式下启动，单磁盘配置如下：

```
/dev/sda1 # EFI 系统分区
/dev/sda2 # ZFS 池（包含“根”文件系统）
```

由于我们是在磁盘分区内创建 zpool（而不是占用整个磁盘），请确保分区类型设置正确（GPT 下，54 或 67 都是合适的选择）。

创建 ZFS 文件系统时，应设置 `mountpoint=legacy`，以便文件系统能以传统方式通过 `mount` 挂载；Slackware 的启动和关机脚本依赖这种方式。

回到本教程，这是一个可用的示例：

```
zpool create -o ashift=12 -O mountpoint=none tank /dev/sda2
zfs create -o mountpoint=legacy -o compression=zstd tank/root
# 根据需要添加更多：
# zfs create -o mountpoint=legacy [..] tank/home
# zfs create -o mountpoint=legacy [..] tank/usr
# zfs create -o mountpoint=legacy [..] tank/opt
```

可以根据个人需求调整选项；虽然根文件系统必须设置 `mountpoint=legacy`，但其他文件系统并非必需。上述示例中，我们对所有文件系统都应用了该选项，这只是个人偏好问题。同样，将 zpool 本身设置为 `mountpoint=none` 以默认不挂载也可根据需求选择（注意 zpool 的 `mountpoint=none` 需要大写 `-O`）。

可以通过以下命令检查设置：

```
zpool list
zfs list
```

然后，将 `/etc/fstab` 调整为类似如下内容：

```
tank/root    /       zfs   defaults   0   0
# 根据需要添加更多：
# tank/home    /home   zfs   defaults   0   0
# tank/usr     /usr    zfs   defaults   0   0
# tank/opt     /opt    zfs   defaults   0   0
```

这样，一旦使用 `zpool import tank` 导入池后，我们就可以像平常一样挂载和卸载这些文件系统。接下来就是…

## 修补并重建 initrd

由于我们使用的是 generic 内核，因此已经有一个可用的 `/boot/initrd-tree/`（如果没有，可先运行一次 `mkinitrd` 创建）。

将 ZFS 用户空间工具复制到其中（`/sbin/zfs` 并非严格必要，但在救援无法启动的系统时可能很有用）：

```
install -m755 /sbin/zpool /sbin/zfs /boot/initrd-tree/sbin/
```

编辑 `/boot/initrd-tree/init`；找到第一个设置 `ROOTDEV` 的 `case` 语句，其内容类似：

```
root=/dev/*)
  ROOTDEV=$(echo $ARG | cut -f2 -d=)
;;
root=LABEL=*)
  ROOTDEV=$(echo $ARG | cut -f2- -d=)
;;
root=UUID=*)
  ROOTDEV=$(echo $ARG | cut -f2- -d=)
;;
```

将上述三种情况替换为：

```
root=*)
  ROOTDEV=$(echo $ARG | cut -f2 -d=)
;;
```

这样我们就可以指定类似 `root=tank/root` 的参数（仔细查看脚本会发现，原来的 `/dev/*`、`LABEL=*`、`UUID=*` 与新添加的情况可以合并为一个）。

在脚本中靠下的位置，找到处理 `RESUMEDEV`（“# Resume state from swap”）的部分，并在其之前插入：

```
# 支持 ZFS 根文件系统：
if [ x"$ROOTFS" = xzfs ]; then
  POOL=${ROOTDEV%%/*}
  echo "Importing zfs pool: $POOL"
  zpool import -o cachefile=none -N $POOL
fi
```

最后，用如下命令重建 initrd：

```
mkinitrd -m zfs
```

建议使用 `-o` 选项，将 initrd.gz 创建在另一个文件中以防万一。更多细节可参考 `/boot/README.initrd`。

重建 initrd 时，也会将所需的库（如 `libzfs.so` 等）复制到 `/lib/` 下；可通过以下命令验证：

```
chroot /boot/initrd-tree /sbin/zpool --help
```

确认无误后，记得将新的 `initrd.gz` 复制到 ESP 分区。

还有其他方法可以确保 ZFS 二进制文件和文件系统模块始终内建到 initrd 中——参见 `man initrd` 获取更多信息。

## 配置引导加载器

以下三种方法均可：

1. 在引导加载器配置中追加 `rootfstype=zfs root=tank/root`（例如 `elilo.conf` 或等效文件）。
2. 修改上一步中的 `/boot/initrd-tree/rootdev` 和 `/boot/initrd-tree/rootfs`，然后重建 initrd。
3. 在重建 initrd 时使用 `-f zfs -r tank/root` 选项。

如果使用 elilo，配置示例如下：

```
image=vmlinuz
  label=linux
  initrd=initrd.gz
  append="root=tank/root rootfstype=zfs"
```

不言而喻，请确保 `initrd` 所引用的文件是你刚生成的文件（例如使用 ESP 时，确保已将新建的 initrd 复制过去）。

## 重启前

请确保手头有紧急内核以防万一。如果升级内核或软件包，请使用快照功能。

## 其他选项

你可以将 ZFS 支持直接编译进内核。如果这样做并且不想使用 initrd，可以在内核映像中嵌入一个小型 initramfs 来执行 `zpool import` 步骤。

## 快照与启动环境

上述修改也允许你创建根文件系统的克隆并从中启动，示例：

```
zfs snapshot tank/root@mysnapshot
zfs clone tank/root@mysnapshot tank/root-clone
zfs set mountpoint=legacy tank/root-clone
zfs promote tank/root-clone
```

调整启动参数以挂载 `tank/root-clone` 而非 `tank/root`（在 ESP 上复制一份已知良好的内核和 initrd 是个不错的主意）。

## 支持

如需帮助，可通过 [邮件列表](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/Mailing%20Lists.html#mailing-lists) 联系社区，或在 [Libera Chat](https://libera.chat/) 的 [#zfsonlinux](ircs://irc.libera.chat/#zfsonlinux) IRC 频道咨询。如果你在使用本教程时发现错误或有功能请求，请 [提交新 issue 并提及 @a-biardi](https://github.com/openzfs/openzfs-docs/issues/new?body=@a-biardi,%20re.%20Slackware%20Root%20on%20ZFS%20HOWTO)。
