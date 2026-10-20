# zfsprops(7)

## 名称

`zfsprops` — ZFS 数据集的原生与用户定义属性

## 说明

属性分为两种类型：原生属性与用户定义（user）属性。原生属性或者导出内部统计信息，或者控制 ZFS 的行为。此外，原生属性要么可编辑，要么只读。用户属性不影响 ZFS 的行为，但你可以用它们以适合所在环境的方式为数据集添加注记。有关用户属性的更多信息，参见下文“用户属性”一节。

### 原生属性

每个数据集都有一组属性，用于导出有关该数据集的统计信息并控制其各种行为。属性从父数据集继承，除非被子数据集覆盖。部分属性仅适用于特定类型的数据集（文件系统、卷或快照）。

数值属性的值可以使用便于阅读的后缀来指定（例如 `k`、`KB`、`M`、`Gb` 等，最高到表示 zettabyte 的 `Z`）。以下写法都是有效（且相等）的规格：`1536M`、`1.5g`、`1.50GB`。

非数值属性的值区分大小写，且必须为小写，`mountpoint`、`sharenfs` 与 `sharesmb` 除外。

以下原生属性由数据集的只读统计信息组成，这些属性既不可设置，也不可继承。除非另有说明，原生属性适用于所有数据集类型。

#### `available`

在假设池中没有任何其他活动的前提下，该数据集及其所有子数据集可用的空间量。由于空间在池内共享，可用量可能受多种因素限制，包括池的物理大小、配额、预留值或池中的其他数据集。

该属性也可用其简化的列名 `avail` 表示。

#### `compressratio`

对于非快照，表示该数据集 `used` 空间所达到的压缩比，以倍数表示。`used` 属性包含后代数据集，但对于克隆，不包含与源快照共享的空间。对于快照，`compressratio` 与 `refcompressratio` 属性相同。运行 `zfs set compression=on dataset` 即可开启压缩。默认值为 `off`。

#### `createtxg`

创建该数据集的事务组（txg）。书签与其最初关联的快照具有相同的 `createtxg`。该属性适用于对快照列表排序，例如用于增量发送与接收。

#### `creation`

该数据集的创建时间。

#### `clones`

对于快照，该属性是一个逗号分隔的列表，列出以此快照为源克隆出的文件系统或卷。这些克隆的 `origin` 属性即为该快照。如果 `clones` 属性不为空，则该快照无法被销毁（即使使用 `-r` 或 `-f` 选项也是如此）。使用 `zfs promote` 命令提升克隆，即可交换源与克隆的角色。

#### `defer_destroy`

如果快照已通过 `zfs destroy -d` 命令标记为延迟销毁，则该属性为 `on`，否则为 `off`。

#### `encryptionroot`

对于加密数据集，指示该数据集当前继承其加密密钥的位置。加载或卸载 `encryptionroot` 的密钥，会隐式加载或卸载任何继承数据集的密钥（详情参见 `zfs load-key` 与 `zfs unload-key`）。克隆始终与其源共享同一个加密密钥。详情参见 zfs-load-key(8) 的“加密”一节。

#### `filesystem_count`

数据集树中位于该节点下方的文件系统与卷的总数。只有在该数据集所在子树中的某处设置了 `filesystem_limit` 时，该值才可用。

#### `keystatus`

指示加密密钥当前是否已加载到 ZFS 中。可能的取值为 `none`、`available` 与 `unavailable`。参见 `zfs load-key` 与 `zfs unload-key`。

#### `guid`

该数据集或书签的 64 位 GUID，在其整个生命周期内不会改变。当快照被发送到其他池时，接收到的快照具有相同的 GUID。因此 `guid` 适用于跨池标识快照。

在 Linux 上，每个已挂载的文件系统、快照与克隆都会向内核报告一个 128 位文件系统 UUID，该 UUID 由 `FS_IOC_GETFSUUID` ioctl 返回。UUID 的前半部分是池的 GUID，后半部分是该数据集的 `guid`，因此 UUID 的前 16 位与后 16 位十六进制数字分别显示这两个 GUID 的十六进制值。该 UUID 不是有效的 RFC 4122 UUID。Linux overlayfs 会将 UUID 存入其持久句柄，IMA 策略中的 `fsuuid=` 规则即据此匹配。

已挂载文件系统的 UUID 在下一次挂载前不会改变。下一次挂载时，`zpool reguid` 之后它会显示新的池 GUID，`zpool split` 生成的新池中亦是如此；`zfs receive` 重新创建文件系统后，它会显示新的数据集 `guid`。`zfs receive` 在同一池中创建的快照与它发送来源的快照具有相同的 `guid`，因而也拥有相同的 UUID。较早的 OpenZFS 版本报告的是空 UUID，因此升级后的第一次挂载也会改变 UUID。zpool-reguid(8) 的“文件系统 UUID 与 overlayfs”一节说明了 UUID 变化对 overlayfs 的影响以及恢复方法。zfs(4) 的 `zfs_sb_uuid` 模块参数可恢复空 UUID。

#### `logicalreferenced`

该数据集可“逻辑”访问的空间量。参见 `referenced` 属性。逻辑空间忽略 `compression` 与 `copies` 属性的影响，得到的数值更接近应用程序看到的数据量。但它确实包含元数据占用的空间。

该属性也可用其简化的列名 `lrefer` 表示。

#### `logicalused`

该数据集及其所有后代所“逻辑”占用的空间量。参见 `used` 属性。逻辑空间忽略 `compression` 与 `copies` 属性的影响，得到的数值更接近应用程序看到的数据量。但它确实包含元数据占用的空间。

该属性也可用其简化的列名 `lused` 表示。

#### `mounted`

对于文件系统，指示该文件系统当前是否已挂载。该属性可为 `yes` 或 `no`。

#### `objsetid`

该数据集在池内的唯一标识符。与数据集的 `guid` 不同，使用 send/receive 操作复制快照时，数据集的 `objsetid` 不会被转移到其他池。数据集删除后，`objsetid` 可以被重新使用（供新数据集使用）。

#### `origin`

对于克隆的文件系统或卷，即克隆所基于的快照。另参见 `clones` 属性。

#### `receive_resume_token`

对于通过 `zfs receive -s` 保存了部分完成状态的文件系统或卷，可将这个不透明令牌提供给 `zfs send -t`，以恢复并完成 `zfs receive`。

#### `redact_snaps`

对于书签，这是该书签包含 redaction 列表的快照 GUID 列表。对于快照，这是该快照被 redact 时所参照的快照 GUID 列表。

#### `referenced`

该数据集可访问的数据量，这些数据可能与池中的其他数据集共享，也可能不共享。创建快照或克隆时，由于内容完全相同，它最初引用的空间量与创建它所依据的文件系统或快照相同。

该属性也可用其简化的列名 `refer` 表示。

#### `refcompressratio`

该数据集 `referenced` 空间所达到的压缩比，以倍数表示。另参见 `compressratio` 属性。

#### `snapshot_count`

数据集树中位于该节点下方的快照总数。只有在该数据集所在子树中的某处设置了 `snapshot_limit` 时，该值才可用。

#### `type`

数据集类型：`filesystem`、`volume`、`snapshot` 或 `bookmark`。

#### `used`

该数据集及其所有后代占用的空间量。该值会与数据集的配额和预留值进行比较检查。已用空间不包含该数据集自身的预留值，但会考虑任何后代数据集的预留值。数据集从其父数据集占用的空间量，以及递归销毁该数据集时会释放的空间量，取其已用空间与预留值中较大者。

快照的已用空间（参见 zfsconcepts(7) 的“快照”一节）是指该快照独占引用的空间。如果该快照被销毁，这部分已用空间将被释放。多个快照共享的空间不计入该指标。当某个快照被销毁时，此前与该快照共享的空间可能变为相邻快照独占，从而改变这些快照的已用空间。最新快照的已用空间也会受到文件系统变更的影响。注意，快照的已用空间是其 `written` 空间的子集。

已用、可用或引用的空间量都不考虑待提交的变化。待提交的变化通常会在几秒内计入。使用 fsync(2) 或 `O_SYNC` 将变更提交到磁盘，并不一定保证空间使用信息立即更新。

#### `usedby*`

`usedby*` 属性将 `used` 属性分解为空间被占用的各种原因。具体来说，`used` = `usedbychildren` + `usedbydataset` + `usedbyrefreservation` + `usedbysnapshots`。这些属性仅对创建在 zpool `version 13` 池上的数据集可用。

#### `usedbychildren`

该数据集子数据集占用的空间量，如果销毁该数据集的所有子数据集，这部分空间将被释放。

#### `usedbydataset`

该数据集自身占用的空间量。如果先移除其上的 `refreservation` 并销毁必要的快照或后代，然后销毁该数据集，这部分空间将被释放。

#### `usedbyrefreservation`

设置在该数据集上的 `refreservation` 占用的空间量，如果移除该 `refreservation`，这部分空间将被释放。

#### `usedbysnapshots`

该数据集的快照所占用的空间量。具体而言，如果销毁该数据集的所有快照，这部分空间将被释放。注意，这并不等于各快照 `used` 属性之和，因为空间可以被多个快照共享。

#### `userused@user`

指定用户在该数据集中占用的空间量。空间按每个文件的属主计费，如 `ls -l` 所显示。所计费的空间量由 `du` 与 `ls -s` 显示。更多信息参见 `zfs userspace` 命令。

非特权用户只能访问自己的空间使用情况。root 用户或被授予 `userused` 权限（通过 `zfs allow`）的用户可以访问所有人的使用情况。

`userused@…` 属性不会显示在 `zfs get all` 的输出中。用户名必须追加在 `@` 符号之后，采用以下形式之一：

* POSIX 名称（如 `joe`）
* POSIX 数字 ID（如 `789`）
* SID 名称（如 `joe.smith@mydomain`）
* SID 数字 ID（如 `S-1-123-456-789`）

在 Linux 上创建的文件始终具有 POSIX 属主。

#### `userobjused@user`

`userobjused` 属性与 `userused` 类似，但它统计的是用户占用的对象数量。该属性统计为用户分配的所有对象，因此结果可能与 `df -i` 等系统工具不同。

当文件系统上设置了 `xattr=on` 属性时，会为每个文件创建额外对象以存储扩展属性。这些额外对象会反映在 `userobjused` 值中，并计入该用户的 `userobjquota`。当文件系统配置为使用 `xattr=sa` 时，通常不需要额外的内部对象。

#### `userrefs`

该属性设置为该快照上的用户保留数量。用户保留通过 `zfs hold` 命令设置。

#### `groupused@group`

指定组在该数据集中占用的空间量。空间按每个文件所属的组计费，如 `ls -l` 所显示。更多信息参见 `userused@user` 属性。

非特权用户只能访问自己所属各组的空间使用情况。root 用户或被授予 `groupused` 权限（通过 `zfs allow`）的用户可以访问所有组的使用情况。

#### `groupobjused@group`

指定组在该数据集中占用的对象数量。使用扩展属性时，每个文件可能会向该组计费多个对象。更多信息参见 `userobjused@user` 属性。

非特权用户只能访问自己所属各组的空间使用情况。root 用户或被授予 `groupobjused` 权限（通过 `zfs allow`）的用户可以访问所有组的使用情况。

#### `projectused@project`

指定项目在该数据集中占用的空间量。项目通过基于对象的数值属性——项目标识符（ID）来标识。对象创建时可以继承其父对象的项目 ID（前提是父对象设有“继承项目 ID”标志，该标志可通过 `chattr -/+P` 或 `zfs project -s` 设置和更改）。特权用户可以随时通过 `chattr -p` 或 `zfs project -s` 设置和更改对象的项目 ID。空间按每个文件所属的项目计费，如 `lsattr -p` 或 `zfs project` 所显示。更多信息参见 `userused@user` 属性。

root 用户或被授予 `projectused` 权限（通过 `zfs allow`）的用户可以访问所有项目的使用情况。

#### `projectobjused@project`

`projectobjused` 与 `projectused` 类似，但它统计的是项目占用的对象数量。当文件集上设置了 `xattr=on` 属性时，ZFS 会为每个文件创建额外对象以存储扩展属性。这些额外对象会反映在 `projectobjused` 值中，并计入该项目的 `projectobjquota`。当文件系统配置为使用 `xattr=sa` 时，不需要额外的内部对象。更多信息参见 `userobjused@user` 属性。

root 用户或被授予 `projectobjused` 权限（通过 `zfs allow`）的用户可以访问所有项目的对象使用情况。

#### `snapshots_changed`

提供了一种机制，可以在无需挂载数据集或遍历快照列表的情况下快速判断快照列表是否发生了变化。该属性指明数据集的快照最近一次被创建或删除的时间。

借助该属性，可以更高效地决定查询快照的频率。只有启用 `extensible_dataset` 特性时，该属性才在挂载与卸载操作之间持久保留。

#### `snapshots_changed_nsecs`

指明数据集的快照最近一次被创建或删除的 UTC 时间，以自 Unix 纪元以来的纳秒数表示。它是 `snapshots_changed` 的高精度版本，以纳秒而非秒为分辨率表示同一时刻。只有启用 `extensible_dataset` 特性时，该属性才在挂载与卸载操作之间持久保留。

#### `volblocksize`

对于卷，指定卷的块大小。卷一旦被写入，`blocksize` 就无法更改，因此应在创建卷时设置。指定大小必须是 2 的幂，且大于等于 `512 B`、小于等于 `128 KiB`。如果池上启用了 `large_blocks` 特性，大小最大可为 `16 MiB`。默认大小为 `16 KiB`。

该属性也可用其简化的列名 `volblock` 表示。

#### `written`

该数据集所引用的、自上一个快照以来被写入的空间量（即上一个快照未引用的空间）。

#### `written@snapshot`

自指定快照以来写入该数据集的 `referenced` 空间量，即该数据集引用但指定快照未引用的空间。

`snapshot` 可以指定为快照短名（即 `@` 之后的部分），此时会被解释为与该数据集位于同一文件系统中的快照。`snapshot` 也可以是完整快照名（`filesystem@snapshot`），对于克隆，这可能是源文件系统中的快照（或是源的源文件系统中的快照，依此类推）。

以下原生属性可用于改变 ZFS 数据集的行为。

#### `aclinherit=discard|noallow|restricted|passthrough|passthrough-x`

控制文件和目录创建时 ACE 如何被继承。

* `discard`：不继承任何 ACE。
* `noallow`：仅继承指定“拒绝”权限的可继承 ACE。
* `restricted`：默认值，继承 ACE 时移除 `write_acl` 与 `write_owner` 权限。
* `passthrough`：不作任何修改地继承所有可继承 ACE。
* `passthrough-x`：含义与 `passthrough` 相同，但 `owner@`、`group@` 与 `everyone@` ACE 仅在文件创建模式也请求执行位时才继承执行权限。

当属性值设为 `passthrough` 时，文件的模式由可继承的 ACE 决定。如果不存在影响模式的可继承 ACE，则模式按应用程序请求的模式设置。

`aclinherit` 属性不适用于 POSIX ACL。

#### `aclmode=discard|groupmask|passthrough|restricted`

控制 ACL 在 chmod(2) 期间如何被修改，以及可继承 ACE 如何受文件创建模式影响：

* `discard`：默认值，删除所有 ACE，表示 chmod(2) 请求的文件或目录模式的 ACE 除外。
* `groupmask`：降低 ACL 中所有 `ALLOW` 条目所授予的权限，使其不超过 chmod(2) 指定的组权限。
* `passthrough`：除创建或更新代表文件或目录新模式的必要 ACL 条目外，不修改 ACL。
* `restricted`：当对拥有非平凡 ACL（其条目无法用模式表示）的文件或目录执行 chmod(2) 时，该操作将返回错误。由于 set user ID、set group ID 与粘滞位没有等价的 ACE 条目，因此必须使用 chmod(2) 来更改文件或目录的这些位。当 `aclmode` 设为 `restricted` 时，要在拥有非平凡 ACL 的文件或目录上使用 chmod(2)，你必须先移除所有不代表当前模式的 ACE 条目。

#### `acltype=off|nfsv4|posix`

控制是否启用 ACL，以及启用时使用哪种类型的 ACL。当该属性被设置为当前平台不支持的 ACL 类型时，其行为与设置为 `off` 相同。

* `off`：在 Linux 上的默认值；文件系统的 `acltype` 属性设为 `off` 时，ACL 被禁用。
* `noacl`：`off` 的别名。
* `nfsv4`：在 FreeBSD 上的默认值，表示应使用 NFSv4 风格的 ZFS ACL。这些 ACL 可用 getfacl(1) 与 setfacl(1) 管理。Linux 尚不支持 `nfsv4` ZFS ACL 类型。
* `posix`：表示应使用 POSIX ACL。POSIX ACL 是 Linux 特有的，在其他平台上不生效。POSIX ACL 以扩展属性的形式存储，因此不会覆盖可能已设置的 NFSv4 ACL。
* `posixacl`：`posix` 的别名。

设置 `posix` 时，若要获得最佳性能，强烈建议同时设置 `xattr=sa` 属性。这会使 POSIX ACL 以更高效的方式存储在磁盘上。但由此产生的影响是，所有新扩展属性只有支持 `xattr=sa` 属性的 OpenZFS 实现才能访问。更多细节参见 `xattr` 属性。

#### `atime=on|off`

控制读取文件时是否更新其访问时间。关闭该属性可避免读取文件时产生写流量，从而带来显著的性能提升，但可能会困扰邮件客户端等类似工具。取值 `on` 与 `off` 分别等价于 `atime` 与 `noatime` 挂载选项。默认值为 `on`。另参见下文的 `relatime`。

#### `canmount=on|off|noauto`

如果该属性设为 `off`，文件系统将无法挂载，并且会被 `zfs mount -a` 忽略。将该属性设为 `off` 类似于将 `mountpoint` 属性设置为`none`，只不过数据集仍具有正常的 `mountpoint` 属性，且该属性可以被继承。将此属性设置为 `off` 可以让数据集仅用于继承属性。设置 `canmount=off` 的一个示例是让两个数据集拥有相同的 `mountpoint`，这样两个数据集的子数据集都会出现在同一个目录中，但可能具有不同的继承特性。

设置为 `noauto` 时，数据集只能通过显式操作进行挂载和卸载。数据集在创建或导入时不会被自动挂载，`zfs mount -a` 命令也不会挂载它，`zfs unmount -a` 命令也不会卸载它。

该属性不支持继承。

#### `checksum=on|off|fletcher2|fletcher4|sha256|noparity|sha512|skein|edonr|blake3`

控制用于验证数据完整性的校验和。默认值为 `on`，它会自动选择适当的算法（当前为 `fletcher4`，但未来版本可能会更改）。值 `off` 会禁用对用户数据的完整性检查。值 `noparity` 不仅会禁用完整性检查，也不会维护用户数据的校验信息。该设置由驻留在 RAID-Z 存储池上的转储设备内部使用，其他数据集不应使用。禁用校验和**并非**推荐做法。

`sha512`、`skein`、`edonr` 与 `blake3` 校验和算法要求在存储池上启用相应特性。

有关这些算法的更多信息，请参见 zpool-features(7)。

更改此属性仅影响新写入的数据。

#### `compression=on|off|gzip|gzip-N|lz4|lzjb|zle|zstd|zstd-N|zstd-fast|zstd-fast-N`

控制此数据集使用的压缩算法。

设置为 `on`（默认值）时，表示应使用当前的默认压缩算法。该默认值在压缩与解压速度以及压缩率之间取得平衡，预计在多种工作负载下都能良好运行。与此属性的其他所有设置不同，`on` 不会选择固定的压缩类型。随着 ZFS 添加新的压缩算法并在存储池上启用，默认压缩算法可能会发生变化。当前的默认压缩算法为 `lzjb`，若启用了 `lz4_compress` 特性，则为 `lz4`。

`lz4` 压缩算法是 `lzjb` 算法的高性能替代方案。它的压缩与解压速度明显更快，压缩率也比 `lzjb` 略高，但只能用于将 `lz4_compress` 特性设置为 `enabled` 的存储池。有关 ZFS 特性标志与 `lz4_compress` 特性的详细信息，请参见 zpool-features(7)。

`lzjb` 压缩算法在提供可观数据压缩的同时针对性能进行了优化。

`gzip` 压缩算法使用的压缩方式与 gzip(1) 命令相同。你可以使用值 `gzip-N` 指定 `gzip` 级别，其中 `N` 为 1（最快）到 9（最佳压缩率）之间的整数。目前 `gzip` 等效于 `gzip-6`（这也是 gzip(1) 的默认值）。

`zstd` 压缩算法兼具高压缩率与良好性能。你可以使用值 `zstd-N` 指定 `zstd` 级别，其中 `N` 为 1（最快）到 19（最佳压缩率）之间的整数。`zstd` 等效于 `zstd-3`。

可以通过设置负的 `zstd` 级别，以牺牲压缩率为代价换取更快的速度。方法是使用 `zstd-fast-N`，其中 `N` 为 `1 - 10`、`20`、`30`、`…`、`100`、`500`、`1000` 中的整数，它们会映射到负的 `zstd` 级别。级别越低，压缩速度越快——`1000` 提供最快的压缩速度与最低的压缩率。`zstd-fast` 等效于 `zstd-fast-1`。

`zle` 压缩算法会压缩连续的零。

此属性也可以用其简化的列名 `compress` 表示。更改此属性仅影响新写入的数据。

选择除 `off` 以外的任何设置时，压缩会显式检查仅由零（NUL 字节）组成的块。检测到全零块时，它会作为空洞存储，而不会使用指定的压缩算法进行压缩。

所有块都按整扇区数分配（每个扇区为 2^`ashift` 字节，例如 512B 或 4KB）。压缩可能导致大小不是扇区对齐的，此时会向上取整到整扇区数。如果压缩节省的空间不足一个整扇区，该块将以未压缩形式存储。因此，逻辑大小为少量扇区的块实际获得的压缩收益更少（例如，在 `recordsize=16K` 且扇区为 4K 时，每个块含 4 个扇区，压缩至少需要节省 25% 才真正在磁盘上节省空间）。

除扇区取整外，还存在 `12.5%` 的默认压缩阈值。

#### `context=none|SELinux-User:SELinux-Role:SELinux-Type:Sensitivity-Level`

此标志为该文件系统在挂载点下的所有文件设置 SELinux 上下文。更多信息请参见 selinux(8)。

#### `fscontext=none|SELinux-User:SELinux-Role:SELinux-Type:Sensitivity-Level`

此标志为正在挂载的文件系统设置 SELinux 上下文。更多信息请参见 selinux(8)。

#### `defcontext=none|SELinux-User:SELinux-Role:SELinux-Type:Sensitivity-Level`

此标志为未标记的文件设置 SELinux 默认上下文。更多信息请参见 selinux(8)。

#### `rootcontext=none|SELinux-User:SELinux-Role:SELinux-Type:Sensitivity-Level`

此标志为该文件系统的根 inode 设置 SELinux 上下文。更多信息请参见 selinux(8)。

#### `copies=1|2|3`

控制为此数据集存储的数据副本数。这些副本是在存储池提供的任何冗余（例如镜像或 RAID-Z）之外额外的。副本会尽可能存储在不同磁盘上。多个副本占用的空间会计入关联的文件与数据集，从而改变 `used` 属性，并计入配额与预留值。

更改此属性仅影响新写入的数据。因此，请在创建文件系统时使用 `-o copies=N` 选项设置此属性。

请记住，如果顶级 vdev 缺失，ZFS 不会导入该存储池。**不要**例如创建一个两磁盘条带池，然后在一些数据集上设置 `copies=2`，以为这样就为它们设置了冗余。当磁盘发生故障时，你将无法导入该存储池，并会丢失所有数据。

加密数据集不能设置为 `copies=3`，因为实现会将部分加密元数据存储在本应存放第三副本的位置。

#### `devices=on|off`

控制是否可以在此文件系统中打开设备节点。默认值为 `on`。值 `on` 与 `off` 分别等效于 `dev` 与 `nodev` 挂载选项。

#### `dedup=off|on|verify|sha256[,verify]|sha512[,verify]|skein[,verify]|edonr,verify|blake3[,verify]`

为此数据集配置去重。默认值为 `off`。默认的去重校验和为 `sha256`（未来可能会更改）。启用 `dedup` 时，此处定义的校验和会覆盖 `checksum` 属性。将值设置为 `verify` 与设置 `sha256,verify` 效果相同。

如果设置为 `verify`，当两个块的签名相同时，ZFS 会逐字节比较以确保块内容完全一致。对于 `edonr` 算法，必须指定 `verify`。

除非必要，否则**不**应在系统上启用去重。参见 zfsconcepts(7) 的“去重”一节。

#### `direct=disabled|standard|always`

控制 Direct I/O 请求（例如 `O_DIRECT`）的行为。Direct I/O 请求的 `standard` 行为是在可能时绕过 ARC。这些请求不会被缓存，性能会受底层磁盘的原始速度限制（这是默认行为）。`always` 会将每个对齐良好的读或写请求都视为直接请求。`disabled` 会静默忽略 `O_DIRECT` 标志，所有直接请求都由 ARC 处理。这是 OpenZFS 2.2 及更早版本的默认行为。

绕过 ARC 要求直接请求正确对齐。对于写请求，请求的起始偏移与大小必须按 `recordsize` 对齐，否则请求中未对齐的部分会被静默重定向到 ARC 处理。对于读请求，起始偏移与大小都不受 `recordsize` 对齐限制。所有直接请求都必须使用页对齐的内存缓冲区，且请求大小必须是页大小的整数倍，否则会返回错误。

并发混用指向文件重叠区域的缓存请求与直接请求会降低性能。不过，结果文件始终是一致的。例如，在缓存写入之后执行直接读取，会返回缓存写入的数据。此外，如果应用程序使用基于 mmap(2) 的文件访问方式，则为了保持一致性，在文件被映射期间所有直接请求都会转换为缓存请求。目前 Direct I/O 不支持 zvol。如果数据集启用了去重，Direct I/O 写入不会检查去重。目前去重与 Direct I/O 写入不兼容。

#### `dnodesize=legacy|auto|1k|2k|4k|8k|16k`

指定文件系统中 dnode 大小的兼容性模式或字面值。默认值为 `legacy`。将此属性设置为 `legacy` 以外的值要求启用 `large_dnode` 存储池特性。

如果数据集使用了 `xattr=sa` 属性设置且工作负载大量使用扩展属性，请考虑将 `dnodesize` 设置为 `auto`。例如，这可能适用于启用了 SELinux 的系统、Lustre 服务器与 Samba 服务器。在已知最佳大小的场景以及性能测试中支持字面值。

如果你需要在某个未启用 `large_dnode` 特性的存储池上接收该数据集的发送流，或者你需要在某个不支持 `large_dnode` 特性的系统上导入该存储池，请将 `dnodesize` 保持为 `legacy`。

此属性也可以用其简化的列名 `dnsize` 表示。

#### `encryption=off|on|aes-128-ccm|aes-192-ccm|aes-256-ccm|aes-128-gcm|aes-192-gcm|aes-256-gcm`

控制此数据集使用的加密算法套件（分组密码、密钥长度与模式）。要求存储池上启用了 `encryption` 特性。要求在创建数据集时设置 `keyformat`。

创建数据集时选择 `encryption=on` 表示将选择默认加密套件，当前为 `aes-256-gcm`。为提供一致的数据保护，加密必须在创建数据集时指定，之后无法更改。

有关加密的更多细节与注意事项，请参见 zfs-load-key(8) 的“加密”一节。

#### `keyformat=raw|hex|passphrase`

控制用户的加密密钥以何种格式提供。仅当数据集加密时才会设置此属性。

`raw` 与 `hex` 密钥长度必须为 32 字节（无论选择哪种加密套件），并且必须随机生成。可以使用以下命令生成 `raw` 密钥：

```sh
# dd if=/dev/urandom bs=32 count=1 of=/path/to/output/key
```

`passphrase` 长度必须在 8 到 512 字节之间，并且在使用前会经过 PBKDF2 处理（参见 `pbkdf2iters` 属性）。虽然加密套件在数据集创建后无法更改，但 `keyformat` 可以通过 `zfs change-key` 更改。

#### `keylocation=prompt|file:///absolute/file/path|https://address|http://address`

控制诸如 `zfs load-key` 与 `zfs mount -l` 等命令默认从何处加载用户的加密密钥。仅对作为加密根的加密数据集设置此属性。如果未指定，默认值为 `prompt`。

虽然加密套件在数据集创建后无法更改，但 `keylocation` 可以通过 `zfs set` 或 `zfs change-key` 更改。

如果选择 `prompt`，则 ZFS 会在需要访问加密数据时要求提供密钥（详情参见 `zfs load-key`）。如果标准输入（stdin）是 TTY，ZFS 会提示输入密钥；否则标准输入即被视为要使用的密钥，并按此处理。用户应注意不要将需要保密的密钥放在命令行上，因为大多数操作系统可能会将命令行参数暴露给其他进程。如果使用的 `keyformat` 为“raw”，则密钥必须通过标准输入提供。

如果选择文件 URL，密钥将从指定的绝对文件路径加载。

如果选择 HTTPS 或 HTTP URL，将根据编译时配置与运行时可用性，使用 fetch(3)、libcurl 或不使用任何工具来执行 GET 请求。可以设置 `SSL_CA_CERT_FILE` 环境变量来指定合并后的证书存储位置；设置 `SSL_CA_CERT_PATH` 环境变量可覆盖包含证书颁发机构包的目录位置；设置 `SSL_CLIENT_CERT_FILE` 与 `SSL_CLIENT_KEY_FILE` 环境变量可配置客户端证书及其密钥的路径。

#### `pbkdf2iters=iterations`

控制在将 `passphrase` 类型的加密密钥处理为加密密钥时，需要经过的 PBKDF2 迭代次数。仅当启用加密且 `keyformat` 选择 `passphrase` 时才定义此属性。PBKDF2 的目标是显著提高暴力破解用户密码短语所需的计算难度。它通过迫使攻击者将每个密码短语反复多次通过一个计算成本高昂的哈希函数，才能得到最终的密钥，从而实现这一目标。而真正知道密码短语的用户只需支付这一次成本。随着 CPU 处理能力不断增强，此数值应相应提高，以确保暴力破解仍然不可行。当前默认值为 `350000`，最小值为 `100000`。此属性可以通过 `zfs change-key` 更改。

#### `exec=on|off`

控制是否可以在此文件系统内执行进程。默认值为 `on`。值 `on` 与 `off` 分别等效于 `exec` 与 `noexec` 挂载选项。

#### `volthreading=on|off`

控制 zvol 的内部线程化。值 `off` 会禁用 zvol 线程化，zvol 转而依赖应用程序线程。默认值为 `on`，即启用 zvol 内部线程化。请注意，此属性会被 `zvol_request_sync` 模块参数覆盖。此属性仅适用于 Linux。

#### `filesystem_limit=count|none`

限制此数据集树节点之下可以存在的文件系统与卷的数量。如果用户被允许更改该限制，则该限制不会被强制执行。在已经设置 `filesystem_limit` 的文件系统的某个后代上再设置 `filesystem_limit`，不会覆盖祖先的 `filesystem_limit`，而是施加一个额外的限制。要使用此特性，必须先启用它（参见 zpool-features(7)）。

#### `special_small_blocks=size`

此值表示将小文件或 zvol 块纳入特殊分配类的阈值块大小。经过压缩与加密后小于或等于此值的块会被分配到特殊分配类，更大的块则被分配到常规类。有效取值范围为 0 到最大块大小（`16 MiB`）。默认大小为 0，表示不会有小文件或 zvol 块被分配到特殊类。

在设置此属性之前，必须先向存储池添加一个 special vdev。有关特殊分配类的更多细节，请参见 zpoolconcepts(7)。

#### `mountpoint=path|none|legacy`

控制此文件系统使用的挂载点。有关此属性用法的更多信息，请参见 zfsconcepts(7) 的“挂载点”一节。

当某个文件系统的 `mountpoint` 属性被更改时，该文件系统以及任何继承此挂载点的子数据集都会被卸载。如果新值为 `legacy`，它们将保持卸载状态；否则，如果该属性先前为 `legacy` 或 `none`，它们会自动在新的位置重新挂载。此外，任何已共享的文件系统都会被取消共享，然后在新位置重新共享。

使用 `zfs set -u` 设置 `mountpoint` 属性时，`mountpoint` 属性会被更新，但数据集不会被挂载或卸载，保持原有状态。

#### `nbmand=on|off`

控制文件系统是否应使用 `nbmand`（非阻塞强制锁定）进行挂载。此属性的更改仅在文件系统被卸载并重新挂载后才生效。此前仅 5.15 之前的 Linux 支持此特性，且当时存在缺陷；FreeBSD 不支持。在 Solaris 上，它用于 SMB 客户端。

#### `longname=on|off`

控制对长度超过 255 字节（最长 1023 字节）文件名的支持。默认值为 `off`。将此属性设置为 `on` 会激活 `longname` 存储池特性，该特性必须已启用（参见 zpool-features(7)）。一旦创建了长文件名，该特性即被激活，不支持该特性的 OpenZFS 实现将无法再导入该存储池。

#### `overlay=on|off`

允许挂载到繁忙的目录，或已经包含文件或目录的目录。这是 Linux 与 FreeBSD 文件系统的默认挂载行为。在这些平台上，此属性默认为 `on`。为与其他平台上的 OpenZFS 保持一致，可设置为 `off` 以禁用 overlay 挂载。

#### `primarycache=all|none|metadata`

控制在主缓存（ARC）中缓存的内容。如果此属性设置为 `all`，则用户数据与元数据都会被缓存；如果设置为 `none`，则用户数据与元数据都不缓存；如果设置为 `metadata`，则只缓存元数据。默认值为 `all`。

#### `quota=size|none`

限制一个数据集及其后代可以消耗的空间量。此属性对已用空间强制执行硬性限制。这包括所有后代消耗的空间，包含文件系统与快照。在已经设置配额的数据集的后代上再设置配额，不会覆盖祖先的配额，而是施加一个额外的限制。

卷不能设置配额，因为 `volsize` 属性本身就充当隐式配额。

#### `snapshot_limit=count|none`

限制可以在一个数据集及其后代上创建的快照数量。在已经设置 `snapshot_limit` 的数据集的后代上再设置 `snapshot_limit`，不会覆盖祖先的 `snapshot_limit`，而是施加一个额外的限制。如果用户被允许更改该限制，则该限制不会被强制执行。例如，这意味着从全局 zone 创建的递归快照会计入 zone 内的每个被委托的数据集。要使用此特性，必须先启用它（参见 zpool-features(7)）。

#### `userquota@user=0|none`

限制指定用户消耗的空间量。用户空间占用由 `userspace@user` 属性识别。

用户配额的强制执行可能会延迟数秒。这意味着，在系统察觉用户超出配额并开始以 EDQUOT 错误信息拒绝额外写入之前，用户可能已经超出了配额。更多信息请参见 `zfs userspace` 命令。

非特权用户只能访问其所在组的空间占用。root 用户，或通过 `zfs allow` 被授予 `userquota` 权限的用户，可以获取与设置所有人的配额。

此属性不适用于卷、版本 4 之前的文件系统，或版本 15 之前的存储池。`userquota@…` 属性不会由 `zfs get all` 显示。用户名必须紧跟在 `@` 符号之后，使用以下形式之一：

* POSIX 名称（“joe”）
* POSIX 数字 ID（“789”）
* SID 名称（“joe.smith@mydomain”）
* SID 数字 ID（“S-1-123-456-789”）

在 Linux 上创建的文件始终具有 POSIX 属主。

#### `defaultuserquota=0|none`

设置默认用户配额，应用于每个未设置专属用户配额的用户。值 `0` 会禁用 defaultuserquota。

#### `userobjquota@user=0|none`

`userobjquota` 与 `userquota` 类似，但它限制用户可以创建的对象数量。有关对象如何计数的更多信息，请参见 `userobjused`。

#### `defaultuserobjquota=0|none`

设置默认用户对象配额，应用于每个未设置专属 userobj 配额的用户。值 `0` 会禁用 defaultuserobjquota。

#### `groupquota@group=0|none`

限制指定组消耗的空间量。组空间占用由 `groupused@group` 属性识别。非特权用户只能访问其所在组的空间占用。root 用户，或通过 `zfs allow` 被授予 `groupquota` 权限的用户，可以获取与设置所有组的配额。

#### `defaultgroupquota=0|none`

设置默认组配额，应用于每个未设置专属组配额的组。值 `0` 会禁用 defaultgroupquota。

#### `groupobjquota@group=0|none`

`groupobjquota` 与 `groupquota` 类似，但它限制一个组可以消耗的对象数量。有关对象如何计数的更多信息，请参见 `userobjused`。

#### `defaultgroupobjquota=0|none`

为每个组设置默认组对象配额，适用于每个未设置专属 groupobj 配额的组。值 `0` 会禁用 defaultgroupobjquota。

#### `projectquota@project=size|none`

限制指定项目消耗的空间量。项目空间占用由 `projectused@project` 属性识别。有关项目如何标识以及如何设置和更改的更多信息，请参见 `projectused` 属性。

root 用户，或通过 `zfs allow` 被授予 `projectquota` 权限的用户，可以访问所有项目的配额。

#### `defaultprojectquota=size|none`

设置默认项目配额，应用于每个未设置专属项目配额的项目。值 `0` 会禁用 defaultprojectquota。

#### `projectobjquota@project=size|none`

`projectobjquota` 与 `projectquota` 类似，但它限制一个项目可以消耗的对象数量。有关对象如何计数的更多信息，请参见 `userobjused`。

#### `defaultprojectobjquota=size|none`

设置默认项目对象配额，应用于每个未设置专属 projectobj 配额的项目。值 `0` 会禁用 defaultprojectobjquota。

#### `readonly=on|off`

控制此数据集是否可以被修改。默认值为 `off`。值 `on` 与 `off` 分别等效于 `ro` 与 `rw` 挂载选项。

此属性也可以用其简化的列名 `rdonly` 表示。

#### `recordsize=size`

为文件系统中的文件指定建议的块大小。此属性专为以固定大小记录访问文件的数据库工作负载而设计。ZFS 会根据针对典型访问模式优化的内部算法自动调整块大小。对于创建非常大的文件但以小块随机访问的数据库，这些算法可能不是最优的。指定大于或等于数据库记录大小的 `recordsize` 可以带来显著的性能提升。强烈不建议在通用文件系统上使用此属性，否则可能对性能产生不利影响。

指定的大小必须是 2 的幂，且大于等于 `512 B`、小于等于 `128 KiB`。如果存储池上启用了 `large_blocks` 特性，大小最大可为 `16 MiB`。有关 ZFS 特性标志的详细信息，请参见 zpool-features(7)。

注意，在 x86_32 上最大大小默认仍限制为 `1 MiB`，参见 `zfs_max_recordsize` 模块参数。

更改文件系统的 `recordsize` 仅影响此后创建的文件；现有文件不受影响。

此属性也可以用其简化的列名 `recsize` 表示。

#### `redundant_metadata=all|most|some|none`

控制哪些类型的元数据以冗余方式存储。ZFS 会为元数据存储一份额外副本，这样即使单个块损坏，丢失的用户数据量也是有限的。这份额外副本独立于存储池层面提供的任何冗余（例如镜像或 RAID-Z），也独立于 `copies` 属性指定的额外副本（总计最多 3 份副本）。例如，如果池为镜像、`copies=2` 且 `redundant_metadata=most`，那么 ZFS 会为大多数元数据存储 6 份副本，为数据与部分元数据存储 4 份副本。

设为 `all` 时，ZFS 会为所有元数据存储一份额外副本。如果磁盘上的单个块损坏，最坏情况下会丢失一个块的用户数据（其长度为 `recordsize` 字节）。

设为 `most` 时，ZFS 会为大多数类型的元数据存储一份额外副本。这可以提升随机写入的性能，因为需要写入的元数据更少。实践中，如果磁盘上的单个块损坏，最坏情况下会丢失约 1000 个块（每块 `recordsize` 字节）的用户数据。哪些元数据块以冗余方式存储的确切行为在未来的发行版中可能会变化。

设为 `some` 时，ZFS 只为关键元数据存储一份额外副本。由于需要写入的元数据更少，这可以提升文件创建性能。如果磁盘上的单个块损坏，可能会丢失多个用户文件或目录。

设为 `none` 时，ZFS 不会以任何方式冗余存储元数据。如果磁盘上的单个块损坏，可能会丢失整个数据集。

默认值为 `all`。

#### `refquota=size|none`

限制一个数据集可以消耗的空间量。此属性对已用空间强制执行硬性限制。此硬性限制不包括后代的已用空间，包含文件系统与快照。

#### `refreservation=size|none|auto`

保证数据集可用的最小空间量，不包括其后代。当已用空间低于该值时，数据集被视为占用了 `refreservation` 指定的空间量。`refreservation` 预留值会计入父数据集的已用空间，并占用父数据集的配额与预留值。

如果设置了 `refreservation`，则只有在此预留值之外还有足够的池空闲空间来容纳数据集当前“引用（referenced）”的字节数时，才允许创建快照。

如果将 `refreservation` 设为 `auto`，该卷即为厚置备（thick provisioned，即“非稀疏”）。`refreservation=auto` 仅支持卷。有关稀疏卷的更多信息，参见“原生属性”一节中的 `volsize`。

此属性也可以用其简化的列名 `refreserv` 表示。

#### `relatime=on|off`

控制 `atime=on` 时访问时间的更新方式。开启此属性后，访问时间会相对于修改时间或变更时间来更新。只有当先前的访问时间早于当前的修改时间或变更时间，或者现有访问时间在过去 24 小时内未被更新过时，访问时间才会被更新。默认值为 `on`。值 `on` 与 `off` 分别等效于 `relatime` 与 `norelatime` 挂载选项。

#### `reservation=size|none`

保证数据集及其后代可用的最小空间量。当已用空间低于该值时，数据集被视为占用了其预留值指定的空间量。预留值会计入父数据集的已用空间，并占用父数据集的配额与预留值。

此属性也可以用其简化的列名 `reserv` 表示。

#### `secondarycache=all|none|metadata`

控制在二级缓存（L2ARC）中缓存的内容。如果此属性设置为 `all`，则用户数据与元数据都会被缓存；如果设置为 `none`，则用户数据与元数据都不缓存；如果设置为 `metadata`，则只缓存元数据。默认值为 `all`。

#### `prefetch=all|none|metadata`

控制推测性预取（speculative prefetch）的行为。如果此属性设置为 `all`，则用户数据与元数据都会被预取；如果设置为 `none`，则用户数据与元数据都不预取；如果设置为 `metadata`，则只预取元数据。默认值为 `all`。

请注意，模块参数 `zfs_prefetch_disable=1` 可以完全禁用推测性预取，绕过此属性所做的任何设置。

#### `setuid=on|off`

控制文件系统是否遵循 setuid 位。默认值为 `on`。值 `on` 与 `off` 分别等效于 `suid` 与 `nosuid` 挂载选项。

#### `sharesmb=on|off|opts`

控制是否使用 Samba USERSHARES 共享文件系统以及使用哪些选项。否则，文件系统通过 `zfs share` 与 `zfs unshare` 命令自动共享与取消共享。如果此属性设为 `on`，则会调用 net(8) 命令创建 USERSHARE。

由于 SMB 共享需要资源名称，系统会从数据集名称构造出一个唯一的资源名称。构造出的名称是数据集名称的副本，只是数据集名称中在资源名称里非法的字符会被替换为下划线（_）字符。Linux 目前不支持 Solaris 上可能提供的附加选项。

如果 `sharesmb` 属性设为 `off`，文件系统将被取消共享。

默认情况下，共享创建时使用的 ACL（访问控制列表）为 `Everyone:F`（“F” 表示 “full permissions”，即读写权限），并且不允许访客访问（这意味着 Samba 必须能够认证真实用户——基于 passwd(5)/shadow(5)、LDAP 或 smbpasswd(5)）。这意味着任何额外的访问控制（例如禁止特定用户的访问等）都必须在底层文件系统上完成。

使用 `zfs set -u` 更新 `sharesmb` 属性时，属性会被设置为期望的值，但不会执行共享、重新共享或取消共享数据集的操作。

#### `sharenfs=on|off|opts`

控制文件系统是否通过 NFS 共享以及使用哪些选项。`sharenfs` 属性为 `off` 的文件系统由 exportfs(8) 命令与 `/etc/exports` 文件中的条目管理。否则，文件系统通过 `zfs share` 与 `zfs unshare` 命令自动共享与取消共享。如果此属性设为 `on`，数据集将使用默认选项共享：

`sec=sys,rw,crossmnt,no_subtree_check`

请注意，这些选项以逗号分隔，与 exports(5) 中的格式不同。这样做是为了免去引号转义，也便于脚本解析。

在 FreeBSD 上，可以有多组选项，以分号分隔。每组选项必须应用于不同的主机或网络，且每组选项会在 exports(5) 中生成单独的一行。完全由空白字符组成的分号分隔选项组将被忽略。目前这种分号用法仅限 FreeBSD。

默认选项的含义参见 exports(5)。在其他情况下，系统会以与此属性内容等效的选项调用 exportfs(8) 命令。

更改数据集的 `sharenfs` 属性时，只有在该属性此前为 `off`，或者数据集在属性更改前已被共享的情况下，该数据集及任何继承此属性的子数据集才会以新选项重新共享。如果新属性值为 `off`，文件系统将被取消共享。

使用 `zfs set -u` 更新 `sharenfs` 属性时，属性会被设置为期望的值，但不会执行共享、重新共享或取消共享数据集的操作。

#### `logbias=latency|throughput`

为 ZFS 提供关于如何处理此数据集中同步写请求的提示。如果 `logbias` 设为 `latency`（默认值），ZFS 会使用池日志设备（如已配置）以低延迟处理写请求。如果 `logbias` 设为 `throughput`，ZFS 不会使用已配置的池日志设备来存储写入的数据，而是针对全局池吞吐量与资源的高效利用来优化同步操作。

#### `snapdev=hidden|visible`

控制位于 `/dev/zvol/<pool>` 下的卷快照设备是隐藏还是可见。默认值为 `hidden`。

#### `snapdir=disabled|hidden|visible`

控制文件系统根目录下的 `.zfs` 目录是禁用、隐藏还是可见，如 zfsconcepts(7) 的“快照”一节所述。默认值为 `hidden`。

#### `sync=standard|always|disabled`

控制同步请求（例如 fsync、`O_DSYNC`）的行为。`standard` 是 POSIX 规定的行为：确保所有同步请求写入稳定存储，并刷新所有设备以确保数据不被设备控制器缓存（这是默认值）。`always` 会使每个文件系统事务在其系统调用返回之前被写入并刷新。这会带来很大的性能损失。`disabled` 会禁用同步请求，文件系统事务只定期提交到稳定存储。该选项性能最高，但非常危险，因为 ZFS 将忽略数据库或 NFS 等应用提出的同步事务要求。管理员只有在理解相关风险后才应使用该选项。

#### `version=N|current`

此文件系统的磁盘上版本，独立于存储池版本。此属性只能设置为更高受支持的版本。参见 `zfs upgrade` 命令。

#### `volsize=size`

对于卷，指定卷的逻辑大小。默认情况下，创建卷会建立等大小的预留值。对于版本号为 9 或更高的存储池，改为设置 `refreservation`。对 `volsize` 的任何更改都会体现为预留值（或 `refreservation`）的等效更改。`volsize` 只能设置为 `volblocksize` 的倍数，且不能为零。

预留值保持与卷的逻辑大小相等，以防止使用者出现意外行为。没有预留值时，卷可能耗尽空间，导致未定义行为或数据损坏，具体取决于卷的使用方式。在使用卷的过程中更改卷的大小时（尤其是缩小时）也可能出现这些后果。调整卷的大小时务必格外小心。

虽然不推荐，但仍可以通过为 `zfs create -V` 命令指定 `-s` 选项，或在卷创建之后更改 `refreservation` 属性的值（在存储池版本 8 或更早的池上为 `reservation` 属性）来创建“稀疏卷”（sparse volume，也称“精简置备”，thin provisioned）。“稀疏卷”是指 `refreservation` 的值小于卷大小加上存储其元数据所需空间的卷。存储池空间不足时会返回 ENOSPC。对于稀疏卷，对 `volsize` 的更改不会反映到 `refreservation` 中。非稀疏的卷称为“厚置备”（thick provisioned）。将 `refreservation` 设为 `auto` 可以使稀疏卷变为厚置备。

#### `volmode=default|full|geom|dev|none`

此属性指定卷以何种方式暴露给操作系统。设为 `full` 时，卷作为功能完备的块设备暴露，提供最大程度的功能。值 `geom` 只是 `full` 的别名，为兼容性而保留。设为 `dev` 时，卷的分区会被隐藏。属性设为 `none` 的卷不会暴露到 ZFS 之外，但仍可以快照、克隆、复制等，适合备份用途。值 `default` 表示卷的暴露方式由系统级可调参数 `zvol_volmode` 控制，其中 `full`、`dev` 与 `none` 分别编码为 1、2、3。默认值为 `full`。

#### `vscan=on|off`

控制在文件打开与关闭时是否对常规文件进行病毒扫描。除了启用此属性之外，还必须启用病毒扫描服务，病毒扫描才会执行。默认值为 `off`。OpenZFS 不使用此属性。

#### `xattr=on|off|dir|sa`

控制此文件系统是否启用扩展属性。支持两种风格的扩展属性：基于目录（directory-based）的与基于系统属性（system-attribute-based）的。

将值设为 `dir` 即可启用基于目录的扩展属性。这种风格的扩展属性对文件上可设置的属性大小与数量没有实际限制，不过在 Linux 上，getxattr(2) 与 setxattr(2) 系统调用将最大大小限制为 `64K`。这是兼容性最好的扩展属性风格，所有 ZFS 实现都支持。

将值设为 `sa` 即可启用基于系统属性的扩展属性（默认值，等同于 `on`）。这类扩展属性的主要优势是性能更好。将扩展属性存储为系统属性可以显著减少所需的磁盘 I/O。每个文件最多可以在为系统属性预留的空间中存储 `64K` 数据。如果没有足够的空间容纳某个扩展属性，它会自动以基于目录的扩展属性形式写入。在不支持 `xattr=sa` 特性的平台上，无法访问基于系统属性的扩展属性。OpenZFS 在 FreeBSD 与 Linux 上都支持 `xattr=sa`。

强烈建议 SELinux 或 POSIX ACL 的用户使用基于系统属性的扩展属性。这两种特性都重度依赖扩展属性，能从更短的访问时间中显著受益。

值 `on` 与 `off` 分别等效于 `xattr` 与 `noxattr` 挂载选项。

#### `jailed=off|on`

控制数据集是否由 jail 管理。更多信息参见 zfs-jail(8)。jail 是 FreeBSD 的特性，此属性在其他平台上不可用。

#### `zoned=off|on`

控制数据集是否由非全局 zone 或命名空间管理。更多信息参见 zfs-zone(8)。zone 是 Linux 的特性，此属性在其他平台上不可用。

#### `zoned_uid=uid`

将数据集的可见性与管理委托给指定 UID 拥有的所有用户命名空间。此属性让无根（rootless）容器可以使用原生 ZFS 存储。例如，设置 `zoned_uid=1000` 允许用户 1000 的无根 Podman 容器使用 ZFS 作为存储层。这是 Linux 独有的特性。

授权采用累加式三层模型，所有层都必须通过：

* **L0（身份验证）**：用户命名空间属主的 UID 必须与 `zoned_uid` 值匹配。
* **L1（dsl_deleg）**：池管理员必须使用 zfs-allow(8) 在委托根上授予按操作的权限。当池委托关闭（`zpool set delegation=off`）时，无论具备何种 capability，所有写操作都会被拒绝。
* **L2（capability tier，能力层级）**：用户命名空间内的 Linux capability 决定允许的操作类别：`CAP_FOWNER` 用于非破坏性操作（创建、快照、设置属性），`CAP_SYS_ADMIN` 用于破坏性操作（销毁、重命名、克隆）。两者都是命名空间化的 capability，作用域为用户命名空间而非初始（init）命名空间。

只读操作（`zfs list`、`zfs get`）不需要任何 capability，也不需要 `zfs allow` 授权；可见性仅由 `zoned_uid` 的委托作用域控制。

可以委托的写操作包括 `zfs create`、`zfs destroy`、`zfs snapshot`、`zfs clone`、`zfs rename`（限于委托子树内）与 `zfs set`。

委托根数据集（即本地设置了 `zoned_uid` 的数据集）无法从用户命名空间内销毁，从而保护父数据集不被未经授权地删除。重命名也被限制在委托子树内。命名空间用户不能修改 `zoned_uid` 或 `zoned` 属性，也不能覆盖管理员在委托根上设置的 `filesystem_limit` 或 `snapshot_limit`（但可以对子数据集施加更严格的子限制）。

设为 `0`（或继承）即可禁用基于 UID 的委托。

与 `zfs zone`（需要已存在的命名空间文件）不同，`zoned_uid` 适用于指定 UID 拥有的任何用户命名空间，因此适合每次运行都创建新命名空间的容器运行时。命名空间专属的委托参见 zfs-zone(8)。

无根 Podman 的示例配置：

```sh
# zfs create tank/containers
# zfs set zoned_uid=1000 tank/containers
# zfs set mountpoint=none tank/containers
# zfs allow -u 1000 create,destroy,mount,snapshot,rename,clone tank/containers
```

以下三个属性在文件系统创建之后无法更改，因此应在创建文件系统时设置。如果未通过 `zfs create` 或 `zpool create` 命令设置这些属性，它们将从父数据集继承。如果父数据集因创建早于这些特性受支持的时间而缺少这些属性，新文件系统将使用这些属性的默认值。

#### `casesensitivity=sensitive|insensitive|mixed`

指示文件系统使用的文件名匹配算法是区分大小写、不区分大小写，还是允许两种匹配方式并存。`casesensitivity` 属性的默认值为 `sensitive`。传统上，Unix 与 POSIX 文件系统的文件名区分大小写。

`casesensitivity` 属性的 `mixed` 值表示文件系统可以同时支持区分大小写与不区分大小写的匹配行为请求。目前，在支持 mixed 行为的文件系统上，不区分大小写的匹配行为仅限于 SMB 服务器产品。有关 `mixed` 值行为的更多信息，参见“ZFS Administration Guide”。

#### `normalization=none|formC|formD|formKC|formKD`

指示文件系统在每次比较两个文件名时是否应执行 `Unicode` 规范化，以及应使用哪种规范化算法。文件名始终按原样存储，名称在任何比较过程中被规范化。如果此属性被设为 `none` 以外的合法值，且 `utf8only` 属性未显式指定，则 `utf8only` 属性会自动设为 `on`。`normalization` 属性的默认值为 `none`。此属性在文件系统创建之后无法更改。

#### `utf8only=on|off`

指示文件系统是否应拒绝包含 `UTF-8` 字符编码集中不存在的字符的文件名。如果此属性被显式设为 `off`，则 `normalization` 属性必须不显式设置或设为 `none`。`utf8only` 属性的默认值为 `off`。此属性在文件系统创建之后无法更改。

`casesensitivity`、`normalization` 与 `utf8only` 属性同时也是新的权限，可以使用 ZFS 委托管理特性将其授予非特权用户。

### 临时挂载点属性

文件系统被挂载时——无论是 legacy 挂载通过 mount(8)，还是普通文件系统通过 `zfs mount` 命令——其挂载选项都会根据其属性来设置。属性与挂载选项的对应关系如下：

| 属性 | 挂载选项 |
| ---- | ---- |
| `atime` | `atime/noatime` |
| `canmount` | `auto/noauto` |
| `devices` | `dev/nodev` |
| `exec` | `exec/noexec` |
| `readonly` | `ro/rw` |
| `relatime` | `relatime/norelatime` |
| `setuid` | `suid/nosuid` |
| `xattr` | `xattr/noxattr` |
| `nbmand` | `mand/nomand` |
| `context=` | `context=` |
| `fscontext=` | `fscontext=` |
| `defcontext=` | `defcontext=` |
| `rootcontext=` | `rootcontext=` |

此外，可以使用 `-o` 选项按每次挂载设置这些选项，而不影响存储在磁盘上的属性。命令行上指定的值会覆盖数据集中存储的值。`nosuid` 选项是 `nodevices,nosetuid` 的别名。`zfs get` 命令会将这些属性报告为“temporary”（临时）。如果数据集处于挂载状态时更改了这些属性，新设置会覆盖任何临时设置。

### 用户属性

除标准原生属性之外，ZFS 还支持任意的用户属性。用户属性不影响 ZFS 的行为，但应用程序或管理员可以用它们为数据集（文件系统、卷与快照）添加注记。

用户属性名必须包含冒号（`:`）字符，以便与原生属性区分。属性名可以包含小写字母、数字以及以下标点字符：冒号（`:`）、连字符（`-`）、句点（`.`）与下划线（`_`）。惯例上属性名分为两部分，例如 `module:property`，但 ZFS 并不强制这一命名空间。用户属性名最长 256 个字符，且不能以连字符（`-`）开头。

在程序中使用用户属性时，强烈建议属性名的 `module` 部分使用反向 DNS 域名，以降低两个独立开发的软件包把同一属性名用作不同用途的概率。

用户属性的值是任意字符串，始终被继承，且从不校验。所有操作属性的命令（`zfs list`、`zfs get`、`zfs set` 等）都可以用来操作原生属性与用户属性。使用 `zfs inherit` 命令清除用户属性。如果该属性未在任何父数据集中定义，它将被完全移除。属性值最长 8192 字节。

2026 年 9 月 9 日
