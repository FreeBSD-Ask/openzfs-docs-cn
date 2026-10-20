# zfs-userspace(8)

## 名称

`zfs-userspace` — 显示 ZFS 数据集的空间占用与配额

`zfs-groupspace(8)` 是 `zfs-userspace(8)` 的历史别名。

`zfs-projectspace(8)` 是 `zfs-userspace(8)` 的历史别名。

## 概述

```sh
zfs userspace [-Hinp] [-o field[,field]…] [-s field]… [-S field]… [-t type[,type]…] 文件系统|快照|路径
```

```sh
zfs groupspace [-Hinp] [-o field[,field]…] [-s field]… [-S field]… [-t type[,type]…] 文件系统|快照
```

```sh
zfs projectspace [-Hp] [-o field[,field]…] [-s field]… [-S field]… 文件系统|快照|路径
```

## 说明

### `zfs userspace [-Hinp] [-o field[,field]…] [-s field]… [-S field]… [-t type[,type]…] filesystem|snapshot|path`

显示指定文件系统、快照或路径中每个用户占用的空间及其配额。如果给定的是路径，则使用包含该路径的文件系统。这对应 `userused@user`、`userobjused@user`、`userquota@user` 与 `userobjquota@user` 属性。

#### `-H`

不打印表头，使用制表符分隔的输出。

#### `-S field`

按此字段逆序排序。参见 `-s`。

#### `-i`

把 SID 转换为 POSIX ID。如果不存在映射，该 POSIX ID 可能只是临时的。普通 POSIX 接口（如 stat(2)、`ls -l`）会执行这种转换，因此 `-i` 选项使 `zfs userspace` 的输出能与这些工具直接比较。但是，如果某些文件是在建立 SMB 到 POSIX 的名称映射之前由 SMB 用户创建的，`-i` 可能会引起混淆。在这种情况下，一些文件归 SMB 实体所有，另一些归 POSIX 实体所有；然而，`-i` 选项会报告 POSIX 实体拥有两者的总用量与配额。

#### `-n`

打印数字 ID，而不是用户/组名。

#### `-o field[,field]…`

只显示以下集合中的指定字段：`type`、`name`、`used`、`quota`。默认显示所有字段。

#### `-p`

使用精确（可解析）的数字输出。

#### `-s field`

按此字段排序输出。`-s` 与 `-S` 标志可以指定多次，以先按一个字段排序，再按另一个字段排序。默认为 `-s type -s name`。

#### `-t type[,type]…`

只打印以下集合中的指定类型：`all`、`posixuser`、`smbuser`、`posixgroup`、`smbgroup`。默认为 `-t posixuser,smbuser`。也可以更改默认值以包含组类型。

### `zfs groupspace [-Hinp] [-o field[,field]…] [-s field]… [-S field]… [-t type[,type]…] filesystem|snapshot`

显示指定文件系统或快照中每个组占用的空间及其配额。此子命令与 `userspace` 相同，只是默认显示的类型为 `-t posixgroup,smbgroup`。

### `zfs projectspace [-Hp] [-o field[,field]…] [-s field]… [-S field]… filesystem|snapshot|path`

显示指定文件系统或快照中每个项目占用的空间及其配额。此子命令与 `userspace` 相同，只是项目标识符是数字而不是名称。因此既不需要用于把 SID 转换为 POSIX ID 的 `-i` 选项，也不需要用于数字 ID 的 `-n` 选项和用于类型的 `-t` 选项。

## 参考文献

zfsprops(7)、zfs-set(8)

2022 年 7 月 11 日

