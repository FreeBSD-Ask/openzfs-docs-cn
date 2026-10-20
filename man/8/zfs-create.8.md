# zfs-create(8)

## 名称

`zfs-create` — 创建 ZFS 数据集

## 概述

```sh
zfs create [-Pnpuv] [-o 属性=值]… 文件系统
```

```sh
zfs create [-ps] [-b 块大小] [-o 属性=值]… -V 大小 卷
```

## 说明

### `zfs create [-Pnpuv] [-o property=value]… filesystem`

创建一个新的 ZFS 文件系统。除非使用 `-u` 选项，否则该文件系统会根据从父数据集继承的 `mountpoint` 属性自动挂载。

#### `-o property=value`

设置指定属性，效果等同于在创建该数据集的同时执行 `zfs set property=value` 命令。任何可编辑的 ZFS 属性都可以在创建时设置。可以指定多个 `-o` 选项。如果在多个 `-o` 选项中指定了同一属性，则会报错。

#### `-p`

创建所有不存在的父数据集。以这种方式创建的数据集会根据从父数据集继承的 `mountpoint` 属性自动挂载。通过 `-o` 选项在命令行上指定的任何属性都会被忽略。如果多次指定 `-p` 选项，父数据集会以 `canmount=off` 创建。如果目标文件系统已存在，该操作会成功完成。

#### `-n`

执行一次试运行（dry-run，即“空操作”）创建，不会创建任何数据集。这与 `-v` 或 `-P` 标志配合使用非常有用，可以验证通过 `-o` 选项传递的属性以及由其他选项隐含的属性。实际创建数据集时仍可能因权限不足或可用容量不足而失败。

#### `-P`

打印关于所创建数据集的、机器可解析的详细信息。输出的每一行包含一个键和一或两个值，全部以制表符分隔。`create_ancestors` 键与 `create` 键的唯一取值为 `filesystem`。只有使用 `-p` 选项时才会出现 `create_ancestors` 键。`property` 键有两个取值：属性名与该属性的值。对于每个因使用 `-o` 选项而将在 `filesystem` 上本地设置的属性，`property` 键会出现一次。

#### `-u`

不要挂载新创建的文件系统。

#### `-v`

打印关于所创建数据集的详细信息。

### `zfs create [-ps] [-b blocksize] [-o property=value]… -V size volume`

创建指定大小的卷。该卷会作为块设备导出到 `/dev/zvol/path`，其中 `path` 是该卷在 ZFS 命名空间中的名称。`size` 表示设备导出的逻辑大小。默认会创建等大小的预留值。

`size` 会自动向上取整为 `blocksize` 的倍数。

#### `-b blocksize`

等效于 `-o volblocksize=blocksize`。如果此选项与 `-o volblocksize` 同时指定，则行为未定义。

#### `-o property=value`

设置指定属性，效果等同于在创建该数据集的同时执行 `zfs set property=value` 命令。任何可编辑的 ZFS 属性都可以在创建时设置。可以指定多个 `-o` 选项。如果在多个 `-o` 选项中指定了同一属性，则会报错。

#### `-p`

创建所有不存在的父数据集。以这种方式创建的数据集会根据从父数据集继承的 `mountpoint` 属性自动挂载。通过 `-o` 选项在命令行上指定的任何属性都会被忽略。如果多次指定 `-p` 选项，父数据集会以 `canmount=off` 创建。如果目标文件系统已存在，该操作会成功完成。

#### `-s`

创建没有预留值的稀疏卷。有关稀疏卷的更多信息，参见 zfsprops(7) 的“原生属性”一节中的 `volsize`。

#### `-n`

执行一次试运行（dry-run，即“空操作”）创建，不会创建任何数据集。这与 `-v` 或 `-P` 标志配合使用非常有用，可以验证通过 `-o` 选项传递的属性以及由其他选项隐含的属性。实际创建数据集时仍可能因权限不足或可用容量不足而失败。

#### `-P`

打印关于所创建数据集的、机器可解析的详细信息。输出的每一行包含一个键和一或两个值，全部以制表符分隔。`create_ancestors` 键与 `create` 键的唯一取值为 `volume`。只有使用 `-p` 选项时才会出现 `create_ancestors` 键。`property` 键有两个取值：属性名与该属性的值。对于每个因使用 `-b` 或 `-o` 选项而将在 `volume` 上本地设置的属性，以及在卷为非稀疏时设置的 `refreservation`，`property` 键会出现一次。

#### `-v`

打印关于所创建数据集的详细信息。

### ZFS 用作交换空间

将 swap 放到 ZFS 卷上容易导致死锁，不建议这样做。参见 [OpenZFS FAQ](../../Project-and-Community/FAQ.md) 的“在 Linux 上将 ZVOL 用作交换设备”一节。

不支持将 swap 放到 ZFS 文件系统内的文件上。

## 示例

### 示例 1：创建 ZFS 文件系统层级结构

以下命令创建一个名为 `pool/home` 的文件系统和一个名为 `pool/home/bob` 的文件系统。父文件系统的挂载点设为 `/export/home`，并被子文件系统自动继承。

```sh
# zfs create pool/home
# zfs set mountpoint=/export/home pool/home
# zfs create pool/home/bob
```

### 示例 2：提升 ZFS 克隆

以下命令演示了如何测试对文件系统的更改，然后用更改后的文件系统替换原文件系统，其中用到了克隆、克隆提升与重命名：

```sh
# zfs create pool/project/production
  向 /pool/project/production 填充数据
# zfs snapshot pool/project/production@today
# zfs clone pool/project/production@today pool/project/beta
  对 /pool/project/beta 进行修改并测试
# zfs promote pool/project/beta
# zfs rename pool/project/production pool/project/legacy
# zfs rename pool/project/beta pool/project/production
  不再需要旧版本后，可以将其销毁
# zfs destroy pool/project/legacy
```

## 参考文献

zfs-destroy(8)、zfs-list(8)、zpool-create(8)

2023 年 6 月 2 日
