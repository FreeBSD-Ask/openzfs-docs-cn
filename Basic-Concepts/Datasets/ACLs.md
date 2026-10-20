# ACL 与扩展属性

ZFS 支持两种互不相关的 ACL 模型——NFSv4 风格的 ACL，它是 ZFS 自身的一部分；以及 POSIX ACL，它属于 Linux 设施，以扩展属性形式存储。可用哪一种取决于平台，而弄错这一点是“我的权限没有生效”这类意外的常见来源。

## 选择 ACL 类型

`acltype` 属性选择模型：

### `off`

禁用 ACL。**Linux 上的默认值。**（`noacl` 与 `disabled` 作为别名接受。）

### `posix`

POSIX ACL，仅 Linux，以扩展属性存储。（`posixacl` 是别名。）需要以 `CONFIG_FS_POSIX_ACL` 构建的内核；没有它，ZFS 会退回到 `off`。

### `nfsv4`

NFSv4 风格的 ZFS ACL，用 `getfacl`/`setfacl` 管理。**FreeBSD 上的默认值**；Linux 不支持。

>**警告**
>
> 设置平台不支持的类型**不会**报错。在 Linux 上，`acltype=nfsv4` 与 `off` 的处理完全相同——但 `zfs get acltype` 仍然报告 `nfsv4`。因此，数据集可能看起来启用了 ACL，实际上却静默地没有任何 ACL。

```sh
zfs set acltype=posix pool/home        # Linux
zfs set acltype=nfsv4 pool/data        # FreeBSD
```

由于 POSIX ACL 存放在扩展属性中，它们不会覆盖可能已设置的 NFSv4 ACL。

在 Linux 上，记得与 `acltype=posix` 一同设置 `xattr=sa`——见下文。

## NFSv4 ACL 行为

有两个属性决定 ZFS ACL 如何与传统 Unix 权限位交互。二者都不适用于 POSIX ACL。

### `aclinherit`——创建文件与目录时 ACE 如何继承

#### `discard`

什么都不继承。

#### `noallow`

只继承指定了*deny*权限的可继承 ACE。

#### `restricted`

默认值。继承时剥除 `write_acl` 与 `write_owner`。（`secure` 作为旧别名接受。）

#### `passthrough`

原样继承一切。文件的模式随后由可继承的 ACE 决定；若没有 ACE 影响模式，则使用应用程序请求的模式。

#### `passthrough-x`

与 `passthrough` 相同，只是 `owner@`、`group@` 与 `everyone@` 仅在创建模式要求时才继承执行位。

### `aclmode`——`chmod(2)` 对既有 ACL 做什么

#### `discard`

默认值。删除除代表所请求模式之外的所有 ACE。

#### `groupmask`

压低所有 ALLOW 条目中的权限，使其不超过 `chmod` 赋予组的权限。

#### `passthrough`

除表示新模式所必需的条目外，不做其他改动。

#### `restricted`

让 `chmod` 在任何带有无法用模式表示的非平凡 ACL 的文件上失败。

对于由客户机管理 ACL 的 Samba 或 NFS 服务器，`aclinherit=passthrough` 配 `aclmode=passthrough` 是能阻止一次误操作的 `chmod` 静默丢弃 ACL 的组合。默认值（`restricted` /`discard`）则偏向 Unix 权限位语义。

## 扩展属性

`xattr` 属性选择扩展属性的存储方式：

### `sa`

基于系统属性（`on` 是它的别名）。内联存放在为系统属性保留的空间中，能显著减少磁盘 I/O。有两个限制：单个属性最多 **32 KiB**（`DXATTR_MAX_ENTRY_SIZE`），单个文件上的全部 SA xattr 最多 **64 KiB**（`DXATTR_MAX_SA_SIZE`）。超出任一项都不是错误——该属性会透明地改以目录形式存放。

### `dir`

基于目录：每个带 xattr 的文件都会得到一个存放它们的隐藏目录。大小或数量没有实际限制（不过 Linux 的 `getxattr(2)`/`setxattr(2)` 把单个属性限制在 64K）。这是兼容性最好的方式，每个 ZFS 实现都支持。

### `off`

禁用。

>**注意**
>
> **默认值变过。** 自 OpenZFS 2.3.0 起 `xattr` 默认 `sa`；在 2.2.x 及更早版本上默认值为 `dir`。在旧版本下创建的数据集保持 `dir`——请用 `zfs get xattr` 确认，不要想当然。

这一点对 POSIX ACL 尤其重要，因为在 Linux 上它们*就是*扩展属性：ZFS 通过与其他 xattr 相同的代码路径，以标准名称 `system.posix_acl_access` 与 `system.posix_acl_default` 存储它们。用 `xattr=dir` 时，每次 ACL 查找都要打开并读取那个隐藏目录；用 `xattr=sa` 时，ACL 随 dnode 一同到来。这就是 `xattr=sa` 成为 Linux 上 `acltype=posix` 标准搭配的原因。

同理，`xattr=off` 会完全禁用 POSIX ACL，无论 `acltype` 怎么说。

```sh
zfs set xattr=sa pool/home
zfs set acltype=posix pool/home
```

注意，基于 `sa` 的 xattr 无法被早于该特性的 ZFS 实现读取——如果这个存储池必须在别处可导入，这一点相关。

由于这两个属性都只影响新写入的数据和新创建的文件，请尽可能在数据集创建时设置：

```sh
zfs create -o xattr=sa -o acltype=posix pool/home/alice
```

## 延伸阅读

* [zfsprops(7)](../../man/7/zfsprops.7.md)——`acltype`、`aclinherit`、`aclmode`、`xattr`、`nbmand`
* [数据集与属性](Datasets-and-Properties.md)、[数据集共享](../Operations/Sharing.md)
