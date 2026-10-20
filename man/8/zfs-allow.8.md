# zfs-allow(8)

## 名称

`zfs-allow` — 把 ZFS 管理权限委托给非特权用户

`zfs-unallow(8)` 是 `zfs-allow(8)` 的历史别名。

## 概述

```sh
zfs allow [-dglu] 用户|组[,用户|组]… 权限|@集名[,权限|@集名]… 文件系统|卷
```

```sh
zfs allow [-dl] -e|everyone 权限|@集名[,权限|@集名]… 文件系统|卷
```

```sh
zfs allow -c 权限|@集名[,权限|@集名]… 文件系统|卷
```

```sh
zfs allow -s @集名 权限|@集名[,权限|@集名]… 文件系统|卷
```

```sh
zfs unallow [-dglru] 用户|组[,用户|组]… [权限|@集名[,权限|@集名]…] 文件系统|卷
```

```sh
zfs unallow [-dlr] -e|everyone [权限|@集名[,权限|@集名]…] 文件系统|卷
```

```sh
zfs unallow [-r] -c [权限|@集名[,权限|@集名]…] 文件系统|卷
```

```sh
zfs unallow [-r] -s @集名 [权限|@集名[,权限|@集名]…] 文件系统|卷
```

## 说明

### `zfs allow filesystem|volume`

显示已在指定文件系统或卷上委托的权限。有关更多信息，参见 `zfs allow` 的其他形式。

在 Linux 上，除 `mount`、`unmount`、`mountpoint`、`canmount`、`rename` 与 `share` 外，其余权限均支持委托。这些权限无法委托，因为 Linux 的 `mount` 命令只允许 root 用户修改全局命名空间。

### `zfs allow [-dglu] user|group[,user|group]… perm|@setname[,perm|@setname]… filesystem|volume`

### `zfs allow [-dl] -e|everyone perm|@setname[,perm|@setname]… filesystem|volume`

把 ZFS 管理权限委托给非特权用户。

#### `-d`

仅允许用于后代文件系统。

#### `-e`、`everyone`

指定把权限委托给所有人。

#### `-g group[,group]…`

显式指定将权限委托给该组。

#### `-l`

仅对指定文件系统本身“本地”允许该权限。

#### `-u user[,user]…`

显式指定将权限委托给该用户。

#### `user|group[,user|group]…`

指定权限的委托对象。可以用逗号分隔的列表指定多个对象。如果未指定 `-g` 与 `-u` 选项，则该参数按以下顺序解释：先是关键字 `everyone`，然后是用户名，最后是组名。要指定名为“everyone”的用户或组，请使用 `-g` 或 `-u` 选项。要指定与某用户同名的组，请使用 `-g` 选项。

#### `perm|@setname[,perm|@setname]…`

要委托的权限。可以用逗号分隔的列表指定多个权限。权限名与 ZFS 子命令名和属性名相同，属性列表见下文。也可以指定以 `@` 开头的权限集名，详见下文 `-s` 形式的说明。

如果 `-d` 与 `-l` 选项均未指定，或两者同时指定，则权限将作用于该文件系统或卷及其所有后代。

权限通常指使用某个 ZFS 子命令或更改某个 ZFS 属性的能力。可用的权限如下：

| 名称 | 类型 | 说明 |
| ---- | ---- | ---- |
| `allow` | subcommand | 还必须拥有所要允许的权限 |
| `bookmark` | subcommand | |
| `clone` | subcommand | 还必须在源文件系统中拥有 `create` 与 `mount` 能力 |
| `create` | subcommand | 还必须拥有 `mount` 能力。创建非稀疏卷还必须拥有 `refreservation` 能力 |
| `destroy` | subcommand | 还必须拥有 `mount` 能力 |
| `diff` | subcommand | 允许在给定对象编号的情况下查找数据集内的路径，以及创建 `zfs diff` 所需的快照 |
| `hold` | subcommand | 允许给快照添加用户保留 |
| `load-key` | subcommand | 允许加载与卸载加密密钥（参见 `zfs load-key` 与 `zfs unload-key`） |
| `change-key` | subcommand | 允许通过 `zfs change-key` 更改加密密钥 |
| `mount` | subcommand | 允许挂载/卸载 ZFS 数据集 |
| `promote` | subcommand | 还必须在源文件系统中拥有 `mount` 与 `promote` 能力 |
| `receive` | subcommand | 还必须拥有 `mount` 与 `create` 能力，`zfs receive -F` 需要此权限（有限的非强制接收参见 `receive:append`） |
| `release` | subcommand | 允许释放可能会销毁快照的用户保留 |
| `rename` | subcommand | 还必须在新父级中拥有 `mount` 与 `create` 能力 |
| `rollback` | subcommand | 还必须拥有 `mount` 能力 |
| `send` | subcommand | 允许发送数据集的复制流 |
| `send:raw` | subcommand | 仅允许发送原始复制流，防止加密数据集以解密后的形式发送 |
| `send:encrypted` | subcommand | 仅允许发送加密数据集的原始复制流，防止加密数据集以解密后的形式发送，并完全禁止发送已解密的数据集 |
| `share` | subcommand | 允许通过 NFS 或 SMB 协议共享文件系统 |
| `snapshot` | subcommand | 还必须拥有 `mount` 能力 |
| `receive:append` | other | 还必须拥有 `mount` 与 `create` 能力；仅具有限的接收能力（不能执行 `receive -F`） |
| `groupquota` | other | 允许访问任何 `groupquota@…` 属性 |
| `groupobjquota` | other | 允许访问任何 `groupobjquota@…` 属性 |
| `groupused` | other | 允许读取任何 `groupused@…` 属性 |
| `groupobjused` | other | 允许读取任何 `groupobjused@…` 属性 |
| `userprop` | other | 允许更改任何用户属性 |
| `userquota` | other | 允许访问任何 `userquota@…` 属性 |
| `userobjquota` | other | 允许访问任何 `userobjquota@…` 属性 |
| `userused` | other | 允许读取任何 `userused@…` 属性 |
| `userobjused` | other | 允许读取任何 `userobjused@…` 属性 |
| `projectobjquota` | other | 允许访问任何 `projectobjquota@…` 属性 |
| `projectquota` | other | 允许访问任何 `projectquota@…` 属性 |
| `projectobjused` | other | 允许读取任何 `projectobjused@…` 属性 |
| `projectused` | other | 允许读取任何 `projectused@…` 属性 |
| `aclinherit` | property | |
| `aclmode` | property | |
| `acltype` | property | |
| `atime` | property | |
| `canmount` | property | |
| `casesensitivity` | property | |
| `checksum` | property | |
| `compression` | property | |
| `context` | property | |
| `copies` | property | |
| `dedup` | property | |
| `defcontext` | property | |
| `devices` | property | |
| `dnodesize` | property | |
| `encryption` | property | |
| `exec` | property | |
| `filesystem_limit` | property | |
| `fscontext` | property | |
| `keyformat` | property | |
| `keylocation` | property | |
| `logbias` | property | |
| `mlslabel` | property | |
| `mountpoint` | property | |
| `nbmand` | property | |
| `normalization` | property | |
| `overlay` | property | |
| `pbkdf2iters` | property | |
| `primarycache` | property | |
| `quota` | property | |
| `readonly` | property | |
| `recordsize` | property | |
| `redundant_metadata` | property | |
| `refquota` | property | |
| `refreservation` | property | |
| `relatime` | property | |
| `reservation` | property | |
| `rootcontext` | property | |
| `secondarycache` | property | |
| `setuid` | property | |
| `sharenfs` | property | |
| `sharesmb` | property | |
| `snapdev` | property | |
| `snapdir` | property | |
| `snapshot_limit` | property | |
| `special_small_blocks` | property | |
| `sync` | property | |
| `utf8only` | property | |
| `version` | property | |
| `volblocksize` | property | |
| `volmode` | property | |
| `volsize` | property | |
| `vscan` | property | |
| `xattr` | property | |
| `zoned` | property | |

### `zfs allow -c perm|@setname[,perm|@setname]… filesystem|volume`

设置“创建时”权限。这些权限会（本地地）授予任何新创建的后代文件系统的创建者。

### `zfs allow -s @setname perm|@setname[,perm|@setname]… filesystem|volume`

定义权限集，或向权限集中添加权限。该权限集可供针对指定文件系统及其后代的其他 `zfs allow` 命令使用。权限集会动态求值，因此对权限集的更改会立即生效。权限集的命名限制与 ZFS 文件系统相同，但名称必须以 `@` 开头，且长度不得超过 64 个字符。

### `zfs unallow [-dglru] user|group[,user|group]… [perm|@setname[,perm|@setname]…] filesystem|volume`

### `zfs unallow [-dlr] -e|everyone [perm|@setname[,perm|@setname]…] filesystem|volume`

### `zfs unallow [-r] -c [perm|@setname[,perm|@setname]…] filesystem|volume`

移除此前用 `zfs allow` 命令授予的权限。该命令不会显式拒绝任何权限，因此其他已授予的权限仍然有效，例如由祖先授予的权限。如果未指定权限，则会移除指定用户、组或 `everyone` 的所有权限。指定 `everyone`（或使用 `-e` 选项）只会移除授予 everyone 的权限，而不会移除每个用户和组的所有权限。`-ldugec` 选项的说明参见 `zfs allow` 命令。

#### `-r`

递归移除该文件系统及其所有后代的权限。

### `zfs unallow [-r] -s @setname [perm|@setname[,perm|@setname]…] filesystem|volume`

从权限集中移除权限。如果未指定权限，则所有权限都会被移除，该权限集也随之完全删除。

## 示例

### 示例 1：在 ZFS 数据集上委托 ZFS 管理权限

以下示例展示如何设置权限，使用户 cindys 能够在 `tank/cindys` 上创建、销毁、挂载文件系统并创建快照。同时显示了 `tank/cindys` 上的权限。

```sh
# zfs allow cindys create,destroy,mount,snapshot tank/cindys
# zfs allow tank/cindys
---- Permissions on tank/cindys --------------------------------------
Local+Descendent permissions:
        user cindys create,destroy,mount,snapshot
```

由于 `tank/cindys` 挂载点的权限默认设置为 755，用户 cindys 将无法在 `tank/cindys` 之下挂载文件系统。请添加一条类似以下语法的 ACE 以提供挂载点访问：

```sh
# chmod A+user:cindys:add_subdirectory:allow /tank/cindys
```

### 示例 2：在 ZFS 数据集上委托创建时权限

以下示例展示如何授予 staff 组中的任何人在 `tank/users` 中创建文件系统的权限。该语法还允许 staff 成员销毁自己的文件系统，但不能销毁其他人的文件系统。同时显示了 `tank/users` 上的权限。

```sh
# zfs allow staff create,mount tank/users
# zfs allow -c destroy tank/users
# zfs allow tank/users
---- Permissions on tank/users ---------------------------------------
Permission sets:
        destroy
Local+Descendent permissions:
        group staff create,mount
```

### 示例 3：在 ZFS 数据集上定义并授予权限集

以下示例展示如何在 `tank/users` 文件系统上定义并授予一个权限集。同时显示了 `tank/users` 上的权限。

```sh
# zfs allow -s @pset create,destroy,snapshot,mount tank/users
# zfs allow staff @pset tank/users
# zfs allow tank/users
---- Permissions on tank/users ---------------------------------------
Permission sets:
        @pset create,destroy,mount,snapshot
Local+Descendent permissions:
        group staff @pset
```

### 示例 4：在 ZFS 数据集上委托属性权限

以下示例展示如何授予在 `users/home` 文件系统上设置配额与预留值的权限。同时显示了 `users/home` 上的权限。

```sh
# zfs allow cindys quota,reservation users/home
# zfs allow users/home
---- Permissions on users/home ---------------------------------------
Local+Descendent permissions:
        user cindys quota,reservation
cindys% zfs set quota=10G users/home/marks
cindys% zfs get quota users/home/marks
NAME              PROPERTY  VALUE  SOURCE
users/home/marks  quota     10G    local
```

### 示例 5：移除 ZFS 数据集上委托的 ZFS 权限

以下示例展示如何移除 staff 组在 `tank/users` 文件系统上的 snapshot 权限。同时显示了 `tank/users` 上的权限。

```sh
# zfs unallow staff snapshot tank/users
# zfs allow tank/users
---- Permissions on tank/users ---------------------------------------
Permission sets:
        @pset create,destroy,mount,snapshot
Local+Descendent permissions:
        group staff @pset
```

2026 年 6 月 14 日

