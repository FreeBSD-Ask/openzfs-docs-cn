# pam_zfs_key(8)

## 名称

`pam_zfs_key` — 用于 ZFS 加密密钥管理的 PAM 模块

## 概述

```sh
pam_zfs_key.so [选项]
```

## 说明

`pam_zfs_key` 是一个 PAM 模块，在用户认证与会话管理期间自动管理 ZFS 数据集的加密密钥。用户登录时，该模块会使用其密码解锁加密的主目录。当最后一个会话关闭时，该模块会卸载数据集并卸载密钥。

该模块通过引用计数跟踪活动会话，以支持同一用户的多次同时登录。

### 多个主目录前缀

配置多个主目录前缀时，该模块会尝试对所有匹配的数据集执行操作。即使其他操作失败，已成功的操作也不会回滚。只有所有操作都成功，该模块才返回成功。

例如，数据集 1、2、3 中数据集 2 失败时：

* 认证/会话：数据集 1 和 3 已解锁并挂载，数据集 2 则没有。
* 更改密码：数据集 1 和 3 已改用新密码，数据集 2 仍保留旧密码。

使用 `required` 时，即使数据集 1 和 3 成功，登录也会失败。使用 `optional` 时，登录会继续进行。更改密码时，数据集 1 和 3 会更新，而数据集 2 仍保留旧密码。使用 `required` 时，用户会看到错误；使用 `optional` 时，用户看到的是成功，可能不会注意到这种不一致。无论哪种方式，密码都会失去同步。

错误会记录到 syslog。部分失败后，请使用 zfs-change-key(8) 重新同步密码。

## 选项

### `homes=path[,path2…]`

用户主目录所在数据集前缀的逗号分隔列表。该模块以 `prefix/username` 的形式构造完整的数据集路径。（默认值: FreeBSD 上为 `zroot/home`，Linux 上为 `rpool/home`）

### `runstatedir=path`

用于存储会话引用计数的目录。（默认值: `/var/run/pam_zfs_key`）

### `uid_min=uid`

该模块生效的最小用户 ID。（默认值: `1000`）

### `uid_max=uid`

该模块生效的最大用户 ID。（默认值: `MAXUID`）

### `nounmount`

会话关闭时，不卸载数据集，也不卸载加密密钥。数据集保持挂载，密钥保持加载。

### `forceunmount`

即使数据集正忙也强制卸载（`MS_FORCE`）。

### `recursive_homes`

在主目录前缀下递归搜索加密数据集。

### `mount_recursively`

递归挂载与卸载子数据集。

### `prop_mountpoint`

通过将数据集的 `mountpoint` 属性与 `/etc/passwd` 中该用户的主目录相匹配来查找用户的数据集，而不是以 `prefix/username` 的形式构造数据集名称。

## 文件

`/var/run/pam_zfs_key/uid`

按用户跟踪活动登录的会话引用计数文件。

## 示例

### 示例 1：基本配置

添加到 `/etc/pam.d/system-auth`：

```sh
auth     optional  pam_zfs_key.so
password optional  pam_zfs_key.so
session  optional  pam_zfs_key.so
```

此配置使用默认设置。用户主目录数据集预期位于 FreeBSD 的 `zroot/home/username` 或 Linux 的 `rpool/home/username`。

### 示例 2：自定义主目录前缀

```sh
auth     optional  pam_zfs_key.so homes=tank/users
password optional  pam_zfs_key.so homes=tank/users
session  optional  pam_zfs_key.so homes=tank/users
```

会在 `tank/users/username` 查找用户数据集。

### 示例 3：多个数据集前缀

```sh
session  optional  pam_zfs_key.so homes=rpool/home,tank/users
```

会在 `rpool/home` 与 `tank/users` 两者中搜索用户数据集。

### 示例 4：保持数据集挂载

```sh
session  optional  pam_zfs_key.so nounmount
```

会话关闭时保持数据集挂载、密钥加载。对于有后台进程访问主目录的系统很有用。

### 示例 5：递归挂载

```sh
session  optional  pam_zfs_key.so mount_recursively
```

递归挂载子数据集；当用户数据按层级组织时很有用，例如 `rpool/home/alice/documents` 与 `rpool/home/alice/photos`。

### 示例 6：创建加密主目录数据集

```sh
# zfs create -o encryption=on \
    -o keyformat=passphrase \
    -o keylocation=prompt \
    -o canmount=on \
    -o mountpoint=/home/alice \
    rpool/home/alice
```

要自动解锁生效，用户的登录密码必须与数据集的口令短语一致。数据集必须具有由 ZFS 管理的挂载点（而非 legacy），且为 `canmount=on`，才能自动挂载。

### 示例 7：多个主目录与密码同步检查

```sh
auth     optional  pam_zfs_key.so homes=rpool/home,tank/home
password required  pam_zfs_key.so homes=rpool/home,tank/home
session  optional  pam_zfs_key.so homes=rpool/home,tank/home
```

即使某些数据集不可用，登录仍会继续进行。如果有任何数据集无法更新，更改密码将失败，从而确保用户收到同步问题的通知。失败行为参见“多个主目录前缀”一节。

## 参考文献

pam(8)、zfs-change-key(8)、zfs-load-key(8)、zfs-mount(8)

## 注释

* 仅适用于使用 `keyformat=passphrase` 的数据集。
* 数据集必须设置 `keylocation=prompt`。
* `mountpoint=legacy`、`canmount=off` 或 `canmount=noauto` 的数据集会加载密钥，但不会自动挂载。

2025 年 12 月 24 日

