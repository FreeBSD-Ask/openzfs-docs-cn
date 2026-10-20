# zfs(8)

## 名称

`zfs` — 配置 ZFS 数据集

## 概述

```sh
zfs [-?V]
```

```sh
zfs version [-j]
```

```sh
zfs subcommand [arguments]
```

## 说明

`zfs` 命令用于配置 ZFS 存储池中的 ZFS 数据集，存储池本身在 zpool(8) 中描述。数据集由 ZFS 命名空间内的唯一路径标识：

`pool[/component]/component`

例如：

`rpool/var/log`

数据集名称的最大长度为 `ZFS_MAX_DATASET_NAME_LEN - 1` 个 ASCII 字符（当前为 255），且须满足 `[A-Za-z_.:/ -]`。此外，快照允许包含一个 `@` 字符，书签允许包含一个 `#` 字符。组件之间使用 `/` 作为分隔符。路径中允许的最大嵌套深度为 `zfs_max_dataset_nesting` 层。ZFS 可调参数（`zfs_*`）在 zfs(4) 中说明。

数据集可以是以下类型之一：

* **文件系统** — 可以挂载到标准系统命名空间中，其行为与其他文件系统类似。ZFS 文件系统在设计上符合 POSIX 标准，但仍存在一些已知问题，会导致某些情况下无法完全符合标准。依赖标准一致性的应用程序在检查文件系统剩余空间时，可能因非标准行为而失败。
* **卷** — 以原始设备或块设备形式导出的逻辑卷。仅当需要块设备时才应使用这种数据集类型；大多数环境中通常使用文件系统。
* **快照** — 文件系统或卷在给定时间点的只读版本。指定形式为 `filesystem@name` 或 `volume@name`。
* **书签** — 与快照非常相似，但不保留磁盘上的数据。它可以用作发送的源，但不能用于接收。指定形式为 `filesystem#name` 或 `volume#name`。

详见 zfsconcepts(7)。

### 属性

属性分为两种类型：原生属性与用户定义（user）属性。原生属性或者导出内部统计信息，或者控制 ZFS 的行为；此外，原生属性要么可编辑，要么只读。用户属性不影响 ZFS 的行为，但你可以用它们以适合所在环境的方式为数据集添加注记。有关属性的更多信息，参见 zfsprops(7)。

### 加密

启用 `encryption` 特性后，即可创建加密的文件系统与卷。ZFS 会加密文件与 zvol 数据、文件属性、ACL、权限位、目录列表、FUID 映射以及 `userused`/`groupused`/`projectused` 数据。有关加密的概述，参见 zfs-load-key(8)。

## 子命令

所有修改状态的子命令都会以其原始形式持久记录到存储池中。

### `zfs -?`

显示帮助信息。

### `zfs -V`、`zfs --version`、`zfs version [-j]`

显示 `zfs` 用户态工具与 zfs 内核模块的软件版本。使用 `-j` 选项时，以 JSON 格式输出。

### 数据集管理

* zfs-list(8) — 以表格形式列出指定数据集的属性信息。
* zfs-create(8) — 创建新的 ZFS 文件系统或卷。
* zfs-destroy(8) — 销毁指定的数据集、快照或书签。
* zfs-rename(8) — 重命名指定的数据集（文件系统或快照）。
* zfs-upgrade(8) — 管理文件系统磁盘版本（on-disk version）的升级。

### 快照

* zfs-snapshot(8) — 以给定名称创建快照。
* zfs-rollback(8) — 将指定数据集回滚到先前的快照。
* zfs-hold(8)、zfs-release(8) — 为指定快照添加或移除保留（hold）引用。如果快照上存在保留，那么使用 `zfs destroy` 命令销毁该快照的尝试将返回 `EBUSY`。
* zfs-diff(8) — 显示指定文件系统的某个快照与该文件系统在更晚时间的另一个快照、或与其当前内容之间的差异。

### 克隆

* zfs-clone(8) — 为指定快照创建克隆。
* zfs-promote(8) — 提升克隆文件系统，使其不再依赖其“origin”快照。

### 发送与接收

* zfs-send(8) — 生成发送流，其对象可以是文件系统，也可以是从书签开始的增量流。
* zfs-receive(8) — 创建一个快照，其内容由标准输入提供的流指定。如果接收的是完整流，还会创建一个新的文件系统。流通过 `zfs send` 子命令创建，该子命令默认生成完整流。
* zfs-bookmark(8) — 为指定快照或书签创建新的书签。书签标记快照创建的时间点，可用作 `zfs send` 命令的增量源。
* zfs-redact(8) — 生成新的遮蔽书签。此功能可用于在远程系统上提供文件系统的克隆，适用于其父文件系统无需可用（或必须不可用）的情形。

### 属性

* zfs-get(8) — 显示指定数据集的属性。
* zfs-set(8) — 为每个数据集将一个属性或一组属性设置为给定值。
* zfs-inherit(8) — 清除指定属性，使其从祖先数据集继承；如果没有祖先设置该属性，则恢复为默认值；使用 `-S` 选项时，若存在已接收值，则恢复为已接收值。

### 配额

* zfs-userspace(8)、zfs-groupspace(8)、zfs-projectspace(8) — 显示指定文件系统或快照中每个用户、组或项目占用的空间及其配额。
* zfs-project(8) — 列出、设置或清除文件或目录上的项目 ID 和/或继承标志。

### 挂载点

* zfs-mount(8) — 显示当前已挂载的所有 ZFS 文件系统，或者按 `mountpoint` 属性描述的路径挂载 ZFS 文件系统。
* zfs-unmount(8) — 卸载当前已挂载的 ZFS 文件系统。

### 共享

* zfs-share(8) — 共享可用的 ZFS 文件系统。
* zfs-unshare(8) — 取消共享当前已共享的 ZFS 文件系统。

### 委托管理

* zfs-allow(8) — 在指定文件系统或卷上委托权限。
* zfs-unallow(8) — 移除指定文件系统或卷上委托的权限。

### 加密

* zfs-change-key(8) — 在指定数据集上添加或更改加密密钥。
* zfs-load-key(8) — 加载指定加密数据集的密钥，使其可被访问。
* zfs-unload-key(8) — 卸载指定数据集的密钥，移除访问该数据集的能力。

### 通道程序

* zfs-program(8) — 通过 Lua 脚本语言的通道程序（channel program）以编程方式执行 ZFS 管理操作。

### 数据重写

* zfs-rewrite(8) — 重写指定文件而不做修改。

### Jail

* zfs-jail(8) — 将文件系统附加到 jail。
* zfs-unjail(8) — 将文件系统从 jail 分离。

### 等待

* zfs-wait(8) — 等待文件系统中的后台活动完成。

## 退出状态

`zfs` 工具成功时返回 0，发生错误时返回 1，指定了无效命令行选项时返回 2。

## 示例

### 示例 1：创建 ZFS 文件系统层级

以下命令创建名为 `pool/home` 的文件系统与名为 `pool/home/bob` 的文件系统。父文件系统的挂载点设置为 `/export/home`，子文件系统会自动继承该挂载点。

```sh
# zfs create pool/home
# zfs set mountpoint=/export/home pool/home
# zfs create pool/home/bob
```

### 示例 2：创建 ZFS 快照

以下命令创建名为 `yesterday` 的快照。该快照按需挂载在 `pool/home/bob` 文件系统根目录下的 `.zfs/snapshot` 目录中。

```sh
# zfs snapshot pool/home/bob@yesterday
```

### 示例 3：创建和销毁多个快照

以下命令为 `pool/home` 及其所有后代文件系统创建名为 `yesterday` 的快照。每个快照按需挂载在其文件系统根目录下的 `.zfs/snapshot` 目录中。第二条命令销毁新创建的这些快照。

```sh
# zfs snapshot -r pool/home@yesterday
# zfs destroy -r pool/home@yesterday
```

### 示例 4：禁用与启用文件系统压缩

以下命令对 `pool/home` 下的所有文件系统禁用 `compression` 属性。下一条命令为 `pool/home/anne` 显式启用 `compression`。

```sh
# zfs set compression=off pool/home
# zfs set compression=on pool/home/anne
```

### 示例 5：列出 ZFS 数据集

以下命令列出系统中所有处于活动状态的文件系统与卷。当 `listsnaps=on` 时会显示快照。默认值为 `off`。有关池属性的更多信息，参见 zpoolprops(7)。

```sh
# zfs list
NAME                      USED  AVAIL  REFER  MOUNTPOINT
pool                      450K   457G    18K  /pool
pool/home                 315K   457G    21K  /export/home
pool/home/anne             18K   457G    18K  /export/home/anne
pool/home/bob             276K   457G   276K  /export/home/bob
```

### 示例 6：为 ZFS 文件系统设置配额

以下命令为 `pool/home/bob` 设置 50 GB 的配额：

```sh
# zfs set quota=50G pool/home/bob
```

### 示例 7：列出 ZFS 属性

以下命令列出 `pool/home/bob` 的所有属性：

```sh
# zfs get all pool/home/bob
NAME           PROPERTY              VALUE                  SOURCE
pool/home/bob  type                  filesystem             -
pool/home/bob  creation              Tue Jul 21 15:53 2009  -
pool/home/bob  used                  21K                    -
pool/home/bob  available             20.0G                  -
pool/home/bob  referenced            21K                    -
pool/home/bob  compressratio         1.00x                  -
pool/home/bob  mounted               yes                    -
pool/home/bob  quota                 20G                    local
pool/home/bob  reservation           none                   default
pool/home/bob  recordsize            128K                   default
pool/home/bob  mountpoint            /pool/home/bob         default
pool/home/bob  sharenfs              off                    default
pool/home/bob  checksum              on                     default
pool/home/bob  compression           on                     local
pool/home/bob  atime                 on                     default
pool/home/bob  devices               on                     default
pool/home/bob  exec                  on                     default
pool/home/bob  setuid                on                     default
pool/home/bob  readonly              off                    default
pool/home/bob  zoned                 off                    default
pool/home/bob  snapdir               hidden                 default
pool/home/bob  acltype               off                    default
pool/home/bob  aclmode               discard                default
pool/home/bob  aclinherit            restricted             default
pool/home/bob  canmount              on                     default
pool/home/bob  xattr                 on                     default
pool/home/bob  copies                1                      default
pool/home/bob  version               4                      -
pool/home/bob  utf8only              off                    -
pool/home/bob  normalization         none                   -
pool/home/bob  casesensitivity       sensitive              -
pool/home/bob  vscan                 off                    default
pool/home/bob  nbmand                off                    default
pool/home/bob  sharesmb              off                    default
pool/home/bob  refquota              none                   default
pool/home/bob  refreservation        none                   default
pool/home/bob  primarycache          all                    default
pool/home/bob  secondarycache        all                    default
pool/home/bob  usedbysnapshots       0                      -
pool/home/bob  usedbydataset         21K                    -
pool/home/bob  usedbychildren        0                      -
pool/home/bob  usedbyrefreservation  0                      -
```

以下命令获取单个属性的值：

```sh
# zfs get -H -o value compression pool/home/bob
on
```

以下命令列出 `pool/home/bob` 所有具有本地设置的属性：

```sh
# zfs get -r -s local -o name,property,value all pool/home/bob
NAME           PROPERTY              VALUE
pool/home/bob  quota                 20G
pool/home/bob  compression           on
```

### 示例 8：回滚 ZFS 文件系统

以下命令将 `pool/home/anne` 的内容恢复到名为 `yesterday` 的快照，并删除所有中间快照：

```sh
# zfs rollback -r pool/home/anne@yesterday
```

### 示例 9：创建 ZFS 克隆

以下命令创建一个可写文件系统，其初始内容与 `pool/home/bob@yesterday` 相同。

```sh
# zfs clone pool/home/bob@yesterday pool/clone
```

### 示例 10：提升 ZFS 克隆

以下命令演示如何借助克隆、克隆提升（promote）与重命名来测试对文件系统的更改，然后用更改后的文件系统替换原文件系统：

```sh
# zfs create pool/project/production
  向 /pool/project/production 填充数据
# zfs snapshot pool/project/production@today
# zfs clone pool/project/production@today pool/project/beta
  修改 /pool/project/beta 并进行测试
# zfs promote pool/project/beta
# zfs rename pool/project/production pool/project/legacy
# zfs rename pool/project/beta pool/project/production
  旧版本不再需要时即可销毁
# zfs destroy pool/project/legacy
```

### 示例 11：继承 ZFS 属性

以下命令使 `pool/home/bob` 与 `pool/home/anne` 从其父数据集继承 `checksum` 属性。

```sh
# zfs inherit checksum pool/home/bob pool/home/anne
```

### 示例 12：远程复制 ZFS 数据

以下命令先向一台远程机器发送一个完整流，再发送一个增量流，分别恢复为 `poolB/received/fs@a` 和 `poolB/received/fs@b`。`poolB` 必须包含文件系统 `poolB/received`，而且初始时不得包含 `poolB/received/fs`。

```sh
# zfs send pool/fs@a |
   ssh host zfs receive poolB/received/fs@a
# zfs send -i a pool/fs@b |
   ssh host zfs receive poolB/received/fs
```

### 示例 13：使用 `zfs receive -d` 选项

以下命令向一台远程机器发送 `poolA/fsA/fsB@snap` 的完整流，并接收为 `poolB/received/fsA/fsB@snap`。所接收快照名称中的 `fsA/fsB@snap` 部分是根据所发送快照的名称确定的。`poolB` 必须包含文件系统 `poolB/received`。如果 `poolB/received/fsA` 不存在，则会被创建为一个空文件系统。

```sh
# zfs send poolA/fsA/fsB@snap |
   ssh host zfs receive -d poolB/received
```

### 示例 14：设置用户属性

以下示例为数据集设置用户定义的 `com.example:department` 属性：

```sh
# zfs set com.example:department=12345 tank/accounting
```

### 示例 15：执行滚动快照

以下示例展示如何使用一致的命名方案维护快照历史。要保留一周的快照，用户按如下方式销毁最旧的快照、重命名其余快照，然后创建新的快照：

```sh
# zfs destroy -r pool/users@7daysago
# zfs rename -r pool/users@6daysago@7daysago
# zfs rename -r pool/users@5daysago@6daysago
# zfs rename -r pool/users@4daysago@5daysago
# zfs rename -r pool/users@3daysago@4daysago
# zfs rename -r pool/users@2daysago@3daysago
# zfs rename -r pool/users@yesterday@2daysago
# zfs rename -r pool/users@today@yesterday
# zfs snapshot -r pool/users@today
```

### 示例 16：为 ZFS 文件系统设置 `sharenfs` 属性选项

以下命令展示如何设置 `sharenfs` 属性选项，为一组 IP 地址启用读写访问，并为系统“neo”在 `tank/home` 文件系统上启用 root 访问：

```sh
# zfs set sharenfs='rw=@123.123.0.0/16:[::1],root=neo' tank/home
```

如果使用 DNS 解析主机名，请指定完全限定主机名。

### 示例 17：在 ZFS 数据集上委托 ZFS 管理权限

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

### 示例 18：在 ZFS 数据集上委托创建时权限

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

### 示例 19：在 ZFS 数据集上定义并授予权限集

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

### 示例 20：在 ZFS 数据集上委托属性权限

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

### 示例 21：移除 ZFS 数据集上委托的 ZFS 权限

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

### 示例 22：显示快照与 ZFS 数据集之间的差异

以下示例展示如何查看 ZFS 数据集先前的某个快照与其当前状态之间发生了哪些变化。`-F` 选项用于指示受影响文件的类型信息。

```sh
# zfs diff -F tank/test@before tank/test
M       /       /tank/test/
M       F       /tank/test/linked      (+1)
R       F       /tank/test/oldname -> /tank/test/newname
-       F       /tank/test/deleted
+       F       /tank/test/created
M       F       /tank/test/modified
```

### 示例 23：创建书签

以下示例为一个快照创建书签。此书签随后可在发送流中代替快照使用。

```sh
# zfs bookmark rpool@snapshot rpool#bookmark
```

### 示例 24：为 ZFS 文件系统设置 `sharesmb` 属性选项

以下示例展示如何通过 ZFS 共享 SMB 文件系统。注意，必须提供用户及其密码。

```sh
# smbmount //127.0.0.1/share_tmp /mnt/tmp -o user=workgroup/turbo,password=obrut,uid=1000
```

需要对 `/etc/samba/smb.conf` 进行最小配置，如下所示。

Samba 需要绑定到回环接口，ZFS 工具才能与 Samba 通信。这是大多数 Linux 发行版的默认行为。

Samba 必须能够对用户进行身份验证。这可以通过多种方式完成（passwd(5)、LDAP、smbpasswd(5) 等）。具体做法不在本文档的讨论范围内，更多信息参见 smb.conf(5)。

如需在之后修改共享的任何选项，全部配置选项参见 USERSHARES 一节。请注意，如果该共享被取消共享（例如因重启），使用 net(8) 命令所做的任何更改都会被撤销。

## 环境变量

### `ZFS_COLOR`

在 `zfs diff` 与 `zfs list` 的输出中使用 ANSI 颜色。

### `ZFS_MOUNT_HELPER`

使 `zfs mount` 使用 mount(8) 来挂载 ZFS 数据集。此选项用于向后兼容旧版 ZFS。

### `ZFS_SET_PIPE_MAX`

指示 `zfs` 为发送/接收设置最大管道大小。在 Linux 上默认禁用，原因是 Linux 的管道大小处理代码中存在一个尚未修复的死锁。

### `ZFS_MODULE_TIMEOUT`

等待 `/dev/zfs` 出现的时间，以秒为单位。默认为 10，最大为 600（10 分钟）。小于 0 时一直等待；为 0 时不等待。

## 接口稳定性

**Committed**。

## 参考文献

attr(1)、gzip(1)、ssh(1)、chmod(2)、fsync(2)、stat(2)、write(2)、acl(5)、attributes(5)、exports(5)、zfsconcepts(7)、zfsprops(7)、exportfs(8)、mount(8)、net(8)、pam_zfs_key(8)、selinux(8)、zfs-allow(8)、zfs-bookmark(8)、zfs-change-key(8)、zfs-clone(8)、zfs-create(8)、zfs-destroy(8)、zfs-diff(8)、zfs-get(8)、zfs-groupspace(8)、zfs-hold(8)、zfs-inherit(8)、zfs-jail(8)、zfs-list(8)、zfs-load-key(8)、zfs-mount(8)、zfs-program(8)、zfs-project(8)、zfs-projectspace(8)、zfs-promote(8)、zfs-receive(8)、zfs-redact(8)、zfs-release(8)、zfs-rename(8)、zfs-rollback(8)、zfs-send(8)、zfs-set(8)、zfs-share(8)、zfs-snapshot(8)、zfs-unallow(8)、zfs-unjail(8)、zfs-unload-key(8)、zfs-unmount(8)、zfs-unshare(8)、zfs-upgrade(8)、zfs-userspace(8)、zfs-wait(8)、zpool(8)

2025 年 5 月 12 日
