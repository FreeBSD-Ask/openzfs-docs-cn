# zpool-features(7)

## 名称

`zpool-features` — ZFS 存储池特性说明

## 说明

ZFS 存储池的磁盘格式版本通过“特性”（features）指定，取代了旧的磁盘格式编号（最后支持的磁盘格式编号为 28）。要为池启用某个特性，请运行 `zpool upgrade`，或将 `feature@特性名` 属性设置为 `enabled`。有关如何成组启用特性集，另见下文“兼容性特性集”一节。

池格式不影响文件系统版本兼容性，也不影响在池之间发送文件系统的功能。

由于大多数特性可以相互独立地启用，池的磁盘格式由池中所有被标记为 `active` 的特性集合指定。如果池是由其他软件版本创建的，该集合可能包含不受支持的特性。

### 特性识别

每个特性都有一个形如 `com.example:特性名` 的 GUID。反向 DNS 名称确保该 GUID 在所有 ZFS 实现中都是唯一的。

当在池上遇到不受支持的特性时，将通过其 GUID 进行识别。有关这些特性的信息，请查阅创建该池的 ZFS 实现的文档。

每个受支持的特性还有一个短名称。按惯例，特性的短名称是其 GUID 中冒号（`:`）之后的部分，即 `com.example:特性名` 的短名称为 `特性名`。不过，如果遵循该惯例会导致名称冲突，不同 ZFS 实现之间的短名称可能会有所不同。

### 特性状态

特性可以处于以下三种状态之一：

#### `active`

该特性的磁盘格式变更已在池上生效。要以读写模式导入该池，必须支持此特性。如果此特性不是只读兼容的，那么要以只读模式导入该池也需要支持（参见“只读兼容性”一节）。

#### `enabled`

管理员已将此特性标记为在池上启用，但该特性的磁盘格式变更尚未做出。不支持此特性的软件仍然可以导入该池，但磁盘格式随时可能被更改，从而使该特性进入 `active` 状态。某些特性在变为 `active` 后可能支持回到 `enabled` 状态，详情参见各特性的具体说明。

#### `disabled`

该特性的磁盘格式变更尚未做出，且除非管理员将该特性移到 `enabled` 状态，否则也不会做出。特性一旦被启用，就无法再被禁用。

受支持特性的状态通过形如 `feature@短名称` 的池属性暴露。

### 只读兼容性

某些特性做出的磁盘格式变更不会妨碍其他软件读取池，这些特性被称为“只读兼容”。如果池上所有不受支持的特性都是只读兼容的，那么在导入时设置 `readonly` 属性即可只读导入该池（有关导入池的详细信息，参见 zpool-import(8)）。

### 不受支持的特性

对于已导入池中已启用的每个不受支持的特性，都有一个名为 `unsupported@特性名` 的池属性，说明为何允许在存在不受支持特性的情况下导入。此属性的可能取值如下：

#### `inactive`

该特性处于 `enabled` 状态，因此池的磁盘格式仍与不支持此特性的软件兼容。

#### `readonly`

该特性是只读兼容的，且池已被只读导入。

### 特性依赖

某些特性需要其他特性已启用才能发挥作用。启用某个特性时，会自动启用它所依赖的所有特性。

### 兼容性特性集

有时池需要与特定的磁盘格式保持兼容，这就需要通过启用或禁用某些特定特性来实现。`compatibility` 特性通过允许从文本文件读取特性集来支持这一需求。当设置为 `off`（默认值）时，禁用兼容性特性集（即启用所有特性）；当设置为 `legacy` 时，不启用任何特性。当设置为以逗号分隔的文件名列表时（每个文件名可以是绝对路径，也可以是相对于 `/etc/zfs/compatibility.d` 或 `/usr/share/zfs/compatibility.d` 的相对路径），将从这些文件中读取请求的特性列表，列表项之间以空白和/或逗号分隔。只有在所有文件中都出现的特性才会被启用。

对文件应用简单的健全性检查：文件大小必须在 1 B 到 16 KiB 之间，且必须以换行符结尾。

请求的特性在使用 `zpool create -o compatibility=…` 创建池时生效，并控制使用 `zpool upgrade` 时启用哪些特性。`zpool status` 不会对不属于所请求特性集的已禁用特性发出警告。

特殊值 `legacy` 会阻止启用任何特性，无论是通过 `zpool upgrade`，还是通过 `zpool set feature@特性名=enabled`。此设置还会阻止池被升级到更新的磁盘格式版本。这是一个安全措施，用于防止意外启用新特性而破坏兼容性。

按惯例，`/usr/share/zfs/compatibility.d` 中的兼容性文件由发行版提供，包含重要版本的主流发行版所支持的特性集，以及每年年初普遍支持的特性集。`/etc/zfs/compatibility.d` 中的兼容性文件（如果存在）优先于 `/usr/share/zfs/compatibility.d` 中同名的文件。

如果这些文件中发现无法识别的特性，会显示一条错误信息。如果该特性位于 `/etc/zfs/compatibility.d` 中的文件里，则视为错误并停止处理；如果位于 `/usr/share/zfs/compatibility.d` 之下，则视为警告并继续处理。这种区别是为了允许发行版包含当前已安装的二进制文件可能无法识别的特性。

兼容性文件可以包含注释：从 `#` 到行尾的任何文本都会被忽略。

**示例**：

```sh
example# cat /usr/share/zfs/compatibility.d/grub2
# 支持 GRUB2 v2.12 及更新版本的特性。
allocation_classes
async_destroy
block_cloning
bookmarks
device_rebuild
embedded_data
empty_bpobj
enabled_txg
extensible_dataset
filesystem_limits
hole_birth
large_blocks
livelist
log_spacemap
lz4_compress
project_quota
resilver_defer
spacemap_histogram
spacemap_v2
userobj_accounting
zilsaxattr
zpool_checkpoint

example# cat /usr/share/zfs/compatibility.d/grub2-2.06
# 支持 GRUB2 v2.12 之前版本的特性。
#
# 如果创建了顶级启动池的快照，GRUB 无法检测到 ZFS 池。
# 该问题在 GRUB v2.12 之前的版本中，当 ZFS 启动池启用了
# extensible_dataset 特性时会出现。
#
# 本文件列出了除 extensible_dataset 及其所依赖特性之外的
# 所有只读兼容特性。
#
allocation_classes
async_destroy
block_cloning
device_rebuild
embedded_data
empty_bpobj
enabled_txg
hole_birth
log_spacemap
lz4_compress
resilver_defer
spacemap_histogram
spacemap_v2
zpool_checkpoint

example# zpool create -o compatibility=grub2 bootpool vdev
```

参见 zpool-create(8) 与 zpool-upgrade(8) 了解特性集如何影响这些命令。

## 特性

本系统支持以下特性：

### `allocation_classes`

* **GUID**：`org.zfsonlinux:allocation_classes`
* **只读兼容**：是

此特性启用独立分配类别的支持。使用 `zpool create` 或 `zpool add` 命令创建专用分配类别 vdev（dedup 或 special）时，此特性变为 `active`。借助设备移除功能，若所有专用分配类别 vdev 都被移除，它可以回到 `enabled` 状态。

### `async_destroy`

* **GUID**：`com.delphix:async_destroy`
* **只读兼容**：是

销毁文件系统需要遍历其所有数据，才能把已用空间归还给池。若没有 `async_destroy`，在所有空间都被回收之前，文件系统都不会被完全移除。如果销毁操作因重启或断电而中断，下次打开池时将需要同步完成该销毁操作。

启用 `async_destroy` 后，文件系统的数据将由后台进程回收，从而使销毁操作无需遍历整个文件系统即可完成。池被打开后，该后台进程可以恢复被中断的销毁操作，因此无需在打开操作中将中断的销毁收尾。后台进程尚待回收的空间量可通过 `freeing` 属性查看。

仅当 `freeing` 不为零时，此特性才为 `active`。

### `blake3`

* **GUID**：`org.openzfs:blake3`
* **依赖**：`extensible_dataset`
* **只读兼容**：否

此特性启用在校验和与去重中使用 BLAKE3 哈希算法。BLAKE3 是一种注重高性能的安全哈希算法。

当 `blake3` 特性被设置为 `enabled` 时，管理员可以使用 `zfs set checksum=blake3 数据集` 在任何数据集上启用 `blake3` 校验和（参见 zfs-set(8)）。一旦 `checksum` 属性被设置为 `blake3`，此特性即变为 `active`，并且直到所有曾经把 checksum 设置为 `blake3` 的文件系统全部被销毁后，才会回到 `enabled` 状态。

### `block_cloning`

* **GUID**：`com.fudosecurity:block_cloning`
* **只读兼容**：是

启用此特性后，ZFS 会对 `copy_file_range(2)` 之类的操作使用块克隆。块克隆允许为单个块创建多个引用。它比复制数据快得多（因为实际数据既不被读取也不被写入），且不占用额外空间。在某些条件下（如 `recordsize` 相同、主加密密钥相同等），可以在数据集之间克隆块。ZFS 会尽力跨数据集克隆，包括已加密的数据集。根据操作系统和/或 ZFS 内部实现的不同，各种（非显而易见的）原因都会对此形成限制。

克隆第一个块时，此特性变为 `active`。当最后一个被克隆的块被释放时，它回到 `enabled` 状态。

### `block_cloning_endian`

* **GUID**：`com.truenas:block_cloning_endian`
* **只读兼容**：是

此特性修正块克隆所使用的块引用表（BRT）中 ZAP 条目的字节序问题。在最初的块克隆实现中，BRT 的 ZAP 条目被错误地存为 8 个单字节条目的数组，而不是单个 8 字节条目，导致池不具备字节序安全性。

创建第一个 BRT ZAP 时，此特性会被激活（这样可确保与现有池兼容）。处于 `active` 状态时，新的 BRT 条目会以正确的、字节序安全的格式存储。当所有 BRT ZAP 都被销毁后，此特性变为非活动状态。

### `bookmarks`

* **GUID**：`com.delphix:bookmarks`
* **依赖**：`extensible_dataset`
* **只读兼容**：是

此特性启用 `zfs bookmark` 命令。只要池中还存在任何书签，此特性就为 `active`。运行 `zfs list -t bookmark -r 池名` 可以列出池中的所有书签。

### `bookmark_v2`

* **GUID**：`com.datto:bookmark_v2`
* **依赖**：`bookmark`、`extensible_dataset`
* **只读兼容**：否

此特性启用更大书签的创建与管理，ZFS 中的其他特性需要它们。创建 v2 书签时，此特性变为 `active`；当所有 v2 书签都被销毁后，会回到 `enabled` 状态。

### `bookmark_written`

* **GUID**：`com.delphix:bookmark_written`
* **依赖**：`bookmark`、`extensible_dataset`、`bookmark_v2`
* **只读兼容**：否

此特性启用附加的书签记账字段，从而支持 `written#书签` 属性（自书签以来写入的空间）以及从书签开始的增量发送流大小的估算。

创建书签时，此特性变为 `active`；当所有带有这些字段的书签都被销毁后，会回到 `enabled` 状态。

### `device_rebuild`

* **GUID**：`org.openzfs:device_rebuild`
* **只读兼容**：是

此特性使 `zpool attach` 与 `zpool replace` 命令在 resilver 时能够执行顺序重建（而不是修复式重建）。

顺序重建按 LBA 顺序重建设备，而不立即校验校验和。完成后会启动一次 scrub，由其校验校验和。这种方式可以在最短的时间内恢复池的完整冗余。若把校验和校验的时间算在内，这种两阶段方式比修复式 resilver 耗时更长。不过，除非池存在其他损坏，scrub 不应报告任何校验和错误。此特性与 raidz 配置不兼容。

顺序 resilver 进行时，此特性为 `active`；resilver 完成后回到 `enabled` 状态。

### `device_removal`

* **GUID**：`com.delphix:device_removal`
* **只读兼容**：否

此特性使 `zpool remove` 命令可以移除顶级 vdev，通过迁移其数据来缩减池的总大小。对顶级 vdev 使用 `zpool remove` 命令时，此特性变为 `active`，且永不回到 `enabled` 状态。

### `draid`

* **GUID**：`org.openzfs:draid`
* **只读兼容**：否

此特性启用 `draid` vdev 类型。dRAID 是 RAID-Z 的一种变体，提供内置的分布式热备盘，可在保留 RAID-Z 优点的同时实现更快的 resilver。数据、校验与备用空间被组织成冗余组，并均匀分布到所有设备上。

创建使用 `draid` vdev 类型的池，或向现有池添加新的 `draid` vdev 时，此特性变为 `active`。

### `draid_failure_domains`

* **GUID**：`com.seagate:draid_failure_domains`
* **依赖**：`draid`
* **只读兼容**：否

此特性启用在 `draid` vdev 类型中使用故障域。故障域允许属于同一个域的整组设备故障，而不会使池离线。由于共享公共组件（如机箱、HBA 或 SAS expander）而可能同时故障的设备，是组成故障域的良好候选。例如，在多机箱的部署中，你可以把每个机箱内的设备集合定义为故障域，此时故障组会跨越各个机箱。换言之，dRAID 的排列使得每个故障组中的第 i 个设备属于第 i 个机箱，从而可以容忍整个机箱的故障。故障组的大小等于故障域的数量，且不能小于冗余组的大小（校验 + 数据 + 备用盘）。

创建配置了故障域的 `draid` vdev 类型的池，或向现有池添加带故障域的 `draid` vdev 时，此特性变为 `active`。

### `dynamic_gang_header`

* **GUID**：`com.klarasystems:dynamic_gang_header`
* **只读兼容**：否

此特性启用基于池扇区大小的更大 gang header。启用后，gang header 会使用为其分配的整个空间，而不是始终限制在 512 字节。这可以减少极端碎片化场景下对嵌套 gang tree 的需求。

写入大于 512 字节的 gang header 时，此特性变为 `active`。`zpool-upgrade(8)` 不会启用此特性，必须手动启用，或将其纳入兼容性文件。

### `edonr`

* **GUID**：`org.illumos:edonr`
* **依赖**：`extensible_dataset`
* **只读兼容**：否

此特性启用在校验和中使用 Edon-R 哈希算法，包括用于 nopwrite（如果同时启用了压缩，当写入数据与某块的校验和匹配时，对该块的覆写将被忽略）。出于充分的谨慎，Edon-R 与去重一起使用时要求校验：`zfs set dedup=edonr,verify`（参见 zfs-set(8)）。

Edon-R 是一种性能极高的哈希算法，曾参与 NIST SHA-3 竞赛。它提供极高的哈希性能（比 SHA-256 快 350% 以上），但因不适合作为通用安全哈希算法而未被选中。该实现使用了 ZFS 中的新盐值校验功能，即在把待校验的数据块送入算法之前，先用存储在池上的一个保密 256 位随机密钥对校验和进行预置。因此生成的校验和对特定池是唯一的，可以防止启用去重的系统遭到哈希碰撞攻击。

当 `edonr` 特性被设置为 `enabled` 时，管理员可以使用 `zfs set checksum=edonr 数据集` 在任何数据集上启用 `edonr` 校验和（参见 zfs-set(8)）。一旦 `checksum` 属性被设置为 `edonr`，此特性即变为 `active`，并且直到所有曾经把 checksum 设置为 `edonr` 的文件系统全部被销毁后，才会回到 `enabled` 状态。

### `embedded_data`

* **GUID**：`com.delphix:embedded_data`
* **只读兼容**：否

此特性提升高度可压缩块的性能与压缩比。内容可压缩到 112 字节或更小的块可以利用此特性。

启用此特性后，高度可压缩块的内容就存储在块“指针”本身之中（此处其实是名不副实，因为其中装的是压缩后的数据，而不是指向磁盘位置的指针）。这样就节省了该块的空间（一个扇区，通常为 512 B 或 4 KiB），读取和写入数据块也不需要额外的 I/O。

此特性一被启用即变为 `active`，且永不回到 `enabled` 状态。

### `empty_bpobj`

* **GUID**：`com.delphix:empty_bpobj`
* **只读兼容**：是

此特性提升单个文件系统或卷创建大量快照及使用这些快照的性能，同时减少所需的磁盘空间。

快照很多时，每个快照都会使用大量的块指针对象（bpobj）来跟踪与该快照关联的块。然而在常见的使用场景中，这些 bpobj 大多是空的。此特性允许按需创建每个 bpobj，从而消除空的 bpobj。

只要存在任何在启用此特性之后创建的文件系统、卷或快照，此特性就为 `active`。

### `enabled_txg`

* **GUID**：`com.delphix:enabled_txg`
* **只读兼容**：是

启用此特性后，ZFS 会记录启用新特性时所处的事务组号。这不会带来任何用户可见的影响，但其他特性可能会依赖此特性。

此特性一被启用即变为 `active`，且永不回到 `enabled` 状态。

### `encryption`

* **GUID**：`com.datto:encryption`
* **依赖**：`bookmark_v2`、`extensible_dataset`
* **只读兼容**：否

此特性启用原生加密数据集的创建与管理。创建加密数据集时，此特性变为 `active`；当所有使用此特性的数据集都被销毁后，会回到 `enabled` 状态。

### `extensible_dataset`

* **GUID**：`com.delphix:extensible_dataset`
* **只读兼容**：否

此特性允许更灵活地使用 ZFS 内部数据结构，其他特性可以依赖它。第一个依赖特性使用它时，此特性变为 `active`；当所有使用此特性的数据集都被销毁后，会回到 `enabled` 状态。

### `fast_dedup`

* **GUID**：`com.klarasystems:fast_dedup`
* **只读兼容**：是

此特性允许在新的去重表上启用更高级的去重功能。创建新的去重表后（即新建池之后，或在已启用去重的数据集上使用新的校验和之后）写入第一个被去重的块时，此特性变为 `active`。当所有使用它的被去重块都被释放后，会回到 `enabled` 状态。

### `filesystem_limits`

* **GUID**：`com.joyent:filesystem_limits`
* **依赖**：`extensible_dataset`
* **只读兼容**：是

此特性启用文件系统限制与快照限制。这些限制用于控制设置了限制的那个树位置可以创建多少个文件系统和/或快照。一旦在任何数据集上设置了任一限制属性，此特性就为 `active`，且永不回到 `enabled` 状态。

### `head_errlog`

* **GUID**：`com.delphix:head_errlog`
* **只读兼容**：否

此特性启用升级版的 errlog，它需要对磁盘上的错误日志格式做出变更。现在每个 head 数据集的错误日志会分别存储在 zap 对象中，并以 head id 作为键。启用此特性后，`zpool status` 的输出会列出每个受错误块影响的数据集。对于密钥未加载的加密文件系统，我们无法检查其快照或克隆是否存在错误，这些错误也不会被报告。错误块本身会针对文件系统报告，而不带文件名。

此特性一被启用即变为 `active`，且永不回到 `enabled` 状态。

### `hole_birth`

* **GUID**：`com.delphix:hole_birth`
* **依赖**：`enabled_txg`
* **只读兼容**：否

此特性存在或曾存在缺陷，后果是：如果你从受影响的数据集执行 `zfs send -i`（或 `-R`，因为它内部使用 `-i`），接收方不会看到任何校验和或其他错误，但接收端生成的快照与源端并不一致。因此 `zfs send -i` 默认已禁用该特性（参见 zfs(4) 中的 `send_holes_without_birth_time`）。

对于含有大量空洞的对象，此特性可提升增量发送（`zfs send -i`）与接收的性能。空洞最多的对象最常见于 zvol。

从快照 A 到快照 B 的增量发送流包含 A 与 B 之间每个发生变更的块的信息。利用一种称为“块出生时间”的元数据，可以识别那些在两个快照之间没有变化的块并让它们不出现在流中，但空洞（仅填充零的块）不会记录出生时间。由于无法区分在 A 之后创建的空洞与在 A 之前创建的空洞，整个文件系统或 zvol 中每个空洞的信息都会被包含在发送流中。

在空洞很少的工作负载中这不是问题。然而，在增量复制含有大量空洞的文件系统或 zvol 时（例如格式化成了其他文件系统的 zvol），会花大量时间发送和接收那些在接收端已经存在的空洞信息，而这些信息是多余的。

启用 `hole_birth` 特性后，所有新空洞的块出生时间都会被记录。在启用此特性之后创建的快照之间的增量发送将使用这种新元数据，避免发送接收端已经存在的空洞信息。

此特性一被启用即变为 `active`，且永不回到 `enabled` 状态。

### `large_blocks`

* **GUID**：`org.open-zfs:large_blocks`
* **依赖**：`extensible_dataset`
* **只读兼容**：否

此特性允许把数据集上的 record size 设置为大于 128 KiB。当某个数据集包含块大小超过 128 KiB 的文件时，此特性变为 `active`；当所有曾经把 recordsize 设置为大于 128 KiB 的文件系统都被销毁后，会回到 `enabled` 状态。

### `large_dnode`

* **GUID**：`org.zfsonlinux:large_dnode`
* **依赖**：`extensible_dataset`
* **只读兼容**：否

此特性允许把数据集中的 dnode 大小设置为大于 512 B。

当某个数据集包含 dnode 大于 512 B 的对象时，此特性变为 `active`，这通常是由于把 `dnodesize` 数据集属性设置为 `legacy` 以外的值所致。当所有曾经包含大于 512 B 的 dnode 的文件系统都被销毁后，此特性会回到 `enabled` 状态。较大的 dnode 可以在 bonus buffer 中存放更多数据，从而通过避免使用 spill 块来潜在提升性能。

### `large_microzap`

* **GUID**：`com.klarasystems:large_microzap`
* **依赖**：`extensible_dataset`、`large_blocks`
* **只读兼容**：是

此特性允许“micro” ZAP 增长到超过 128 KiB，而不会被升级为“fat” ZAP。micro ZAP 第一次增长到超过 128 KiB 时，此特性变为 `active`。只有当所有曾经拥有较大 micro ZAP 的数据集都被销毁后，它才会回到 `enabled` 状态。

请注意，即使启用了此特性，如果不修改 `zap_micro_max_size` 模块参数，micro ZAP 仍不能增长到超过 128 KiB。参见 zfs(4)。

### `livelist`

* **GUID**：`com.delphix:livelist`
* **依赖**：`extensible_dataset`
* **只读兼容**：是

当克隆上发生了大量随机/稀疏写入时，此特性允许以比传统方法更快的速度删除克隆。克隆创建之后所有被分配和被释放的块都由该克隆的 livelist 跟踪，删除克隆时会引用这份 livelist。创建克隆时此特性被激活，并保持 `active`，直到所有克隆都被销毁。

### `log_spacemap`

* **GUID**：`com.delphix:log_spacemap`
* **依赖**：`com.delphix:spacemap_v2`
* **只读兼容**：是

此特性提升高度碎片化池的性能，尤其适用于随机写占比较大的工作负载。其做法是：每个 TXG 把所有 metaslab 变更记录在单个 spacemap 上，而不是把多次写入分散写到所有 metaslab spacemap 上。

此特性一被启用即变为 `active`，且永不回到 `enabled` 状态。

### `longname`

* **GUID**：`org.zfsonlinux:longname`
* **依赖**：`extensible_dataset`
* **只读兼容**：否

此特性允许创建文件名最长达 1023 字节的文件和目录。同时新增了一个数据集属性 `longname`，用于单独开关每个数据集的长文件名支持。即使数据集中包含长文件名文件，此属性也可以被关闭。此时无法再创建长文件名文件，但已有的长文件名文件仍可被查找。

当数据集中创建了长度超过 255 的文件名时，此特性变为 `active`；当所有这些数据集都被销毁后，会回到 `enabled` 状态。

### `lz4_compress`

* **GUID**：`org.illumos:lz4_compress`
* **只读兼容**：否

`lz4` 是一种高性能实时压缩算法，相比旧的 `lzjb` 压缩，压缩与解压缩速度显著更快，压缩比也更高。通常，`lz4` 在可压缩数据上比 `lzjb` 快约 50%，在不可压缩数据上快约 200%。其解压缩速度也快约 80%，同时压缩比提升约 10%。

当 `lz4_compress` 特性被设置为 `enabled` 时，管理员可以使用 zfs-set(8) 命令为池上的任意数据集开启 `lz4` 压缩。所有新写入的元数据都将使用 `lz4` 算法压缩。

此特性一被启用即变为 `active`，且永不回到 `enabled` 状态。

### `multi_vdev_crash_dump`

* **GUID**：`com.joyent:multi_vdev_crash_dump`
* **只读兼容**：否

此特性允许在由多个 vdev 组成的池上配置 dump 设备。这些 vdev 可以采用任意镜像或 raidz 配置。

当 `multi_vdev_crash_dump` 特性被设置为 `enabled` 时，管理员可以使用 `dumpadm(8)` 在由多个 vdev 组成的池上配置 dump 设备。

在 FreeBSD 与 Linux 上，此特性未被使用，但为兼容性而注册。在这些系统上创建的池会启用该特性，但永远不会转为 `active`，因为崩溃转储支持不需要该功能。此特性处于 `active` 状态的现有池可以被导入。

### `obsolete_counts`

* **GUID**：`com.delphix:obsolete_counts`
* **依赖**：`device_removal`
* **只读兼容**：是

此特性是 `device_removal` 的增强，随着时间推移会减少跟踪已移除设备所需的内存。当间接块被释放或重新映射时，会将其间接映射中的对应部分标记为“obsolete”，即不再需要。

对顶级 vdev 使用 `zpool remove` 命令时，此特性变为 `active`，且永不回到 `enabled` 状态。

### `physical_rewrite`

* **GUID**：`com.truenas:physical_rewrite`
* **依赖**：`extensible_dataset`
* **只读兼容**：是

此特性启用保留逻辑出生时间的物理块重写，避免重写后的块被不必要地包含在增量 `zfs send` 流中。启用后可使用 `zfs rewrite -P` 命令。

第一次在任何数据集上使用 `zfs rewrite -P` 时，此特性变为 `active`；当所有曾经使用过物理重写的数据集都被销毁后，会回到 `enabled` 状态。

### `project_quota`

* **GUID**：`org.zfsonlinear:project_quota`
* **依赖**：`extensible_dataset`
* **只读兼容**：是

此特性允许管理员按项目标识符（ID）统计空间与对象使用情况。

项目 ID 是基于对象的属性。升级现有文件系统时，没有项目 ID 的对象会被分配为零项目 ID。启用此特性后，新创建的对象在父目录设置了继承标志（通过 `chattr [+ -]P` 或 `zfs project -s | -C`）时会继承父目录的项目 ID；否则新对象的项目 ID 为零。对象的所有者（或有权限的用户）可以随时通过 `chattr -p 项目ID` 或 `zfs project -p 项目ID` 更改对象的项目 ID。

此特性一被启用即变为 `active`，且永不回到 `disabled` 状态。

每个文件系统会在重新挂载时自动升级，或者在该文件系统下新建文件时自动升级。也可以通过 `zfs set version=current 文件系统` 触发文件系统的升级。升级过程在后台运行，对于包含大量文件的文件系统可能需要较长时间才能完成。

### `raidz_expansion`

* **GUID**：`org.openzfs:raidz_expansion`
* **依赖**：`none`
* **只读兼容**：否

此特性使 `zpool attach` 子命令能够将新设备附加到 RAID-Z 组，从而扩展池中的总可用空间。参见 zpool-attach(8)。

### `redaction_bookmarks`

* **GUID**：`com.delphix:redaction_bookmarks`
* **依赖**：`bookmarks`、`extensible_dataset`
* **只读兼容**：否

此特性启用带删减的 `zfs send`。这类发送会创建删减书签，用于保存创建该发送流的 send 所删减的块列表。有关带删减发送的更多信息，参见 zfs-send(8)。

### `redacted_datasets`

* **GUID**：`com.delphix:redacted_datasets`
* **依赖**：`extensible_dataset`
* **只读兼容**：否

此特性启用接收带删减的 `zfs send` 流，接收后会创建带删减的数据集。这些数据集缺少部分块，因此不能被安全挂载，其内容也不能被安全读取。有关带删减接收的更多信息，参见 zfs-send(8)。

### `redaction_list_spill`

* **GUID**：`com.delphix:redaction_list_spill`
* **依赖**：`redaction_bookmarks`
* **只读兼容**：否

此特性使 `zfs redact` 创建的删减列表能够容纳多得多的条目。创建条目数超过 36 的删减列表时，此特性变为 `active`；当池中不再存在长删减列表时，会回到 `enabled` 状态。有关带删减发送的更多信息，参见 zfs-send(8)。

### `resilver_defer`

* **GUID**：`com.datto:resilver_defer`
* **只读兼容**：是

此特性允许在已有 resilver 进行中的情况下推迟新的 resilver。如果没有此特性，任何新的 resilver 都会导致当前正在运行的 resilver 立即从头重新开始。

一旦有 resilver 被推迟，此特性即变为 `active`；当被推迟的 resilver 开始运行时，会回到 `enabled` 状态。

### `sha512`

* **GUID**：`org.illumos:sha512`
* **依赖**：`extensible_dataset`
* **只读兼容**：否

此特性启用在校验和与去重中使用 SHA-512/256 截断哈希算法（FIPS 180-4）。SHA-512 原生的 64 位算术使其在 64 位硬件上比 SHA-256 快约 50%，因此对于哈希性能重要、但因种种原因无法使用更快的 `skein` 与 `edonr` 算法的系统而言，它是一个改动很小的良好替换选择。

当 `sha512` 特性被设置为 `enabled` 时，管理员可以使用 `zfs set checksum=sha512 数据集` 在任何数据集上启用 `sha512` 校验和（参见 zfs-set(8)）。一旦 `checksum` 属性被设置为 `sha512`，此特性即变为 `active`，并且直到所有曾经把 checksum 设置为 `sha512` 的文件系统全部被销毁后，才会回到 `enabled` 状态。

### `skein`

* **GUID**：`org.illumos:skein`
* **依赖**：`extensible_dataset`
* **只读兼容**：否

此特性启用在校验和与去重中使用 Skein 哈希算法。Skein 是一种高性能安全哈希算法，曾是 NIST SHA-3 竞赛的入围者。它在 64 位硬件上提供极高的安全性与高性能（比 SHA-256 快 80%）。该实现同样使用了 ZFS 中的新盐值校验功能，即在把待校验的数据块送入算法之前，先用存储在池上的一个保密 256 位随机密钥对校验和进行预置。因此生成的校验和对特定池是唯一的，可以防止启用去重的系统遭到哈希碰撞攻击。

当 `skein` 特性被设置为 `enabled` 时，管理员可以使用 `zfs set checksum=skein 数据集` 在任何数据集上启用 `skein` 校验和（参见 zfs-set(8)）。一旦 `checksum` 属性被设置为 `skein`，此特性即变为 `active`，并且直到所有曾经把 checksum 设置为 `skein` 的文件系统全部被销毁后，才会回到 `enabled` 状态。

### `spacemap_histogram`

* **GUID**：`com.delphix:spacemap_histogram`
* **只读兼容**：是

此特性让 ZFS 能够维护更多关于池内空闲空间组织方式的信息。如果启用此特性，它会在创建新的空间映射对象时，或把现有空间映射升级到新格式时被激活，并且永不回到 `enabled` 状态。

### `spacemap_v2`

* **GUID**：`com.delphix:spacemap_v2`
* **只读兼容**：是

此特性启用新的空间映射编码，该编码在有益时由两个字（而非一个字）组成。新编码使空间映射能以更高的磁盘效率表示大范围的空间区域，同时提高其最大可寻址偏移量。

启用后，此特性即变为 `active`，且永不回到 `enabled` 状态。

### `userobj_accounting`

* **GUID**：`org.zfsonlinear:userobj_accounting`
* **只读兼容**：是

此特性允许管理员按用户和组统计对象使用情况。

此特性一被启用即变为 `active`，且永不回到 `enabled` 状态。

每个文件系统会在重新挂载时自动升级，或者在该文件系统下新建文件时自动升级。也可以通过 `zfs set version=current 文件系统` 触发文件系统的升级。升级过程在后台运行，对于包含大量文件的文件系统可能需要较长时间才能完成。

### `vdev_zaps_v2`

* **GUID**：`com.klarasystems:vdev_zaps_v2`
* **只读兼容**：否

此特性为根 vdev 创建一个 ZAP 对象。

在下一次 `zpool import` 或 `zpool reguid` 之后，此特性变为 `active`。

使用 `zpool get` 与 `zpool set` 可以在根 vdev 上读取或设置属性，此时 vdev 名称使用 `root`，它是 `root-0` 的别名。

### `zilsaxattr`

* **GUID**：`org.openzfs:zilsaxattr`
* **依赖**：`extensible_dataset`
* **只读兼容**：是

此特性启用 ZIL 中 `xattr=sa` 扩展属性的日志记录。启用后，只要做出变更时数据集设置了 `sync=always`，或在变更之后对该数据集调用了 `sync(2)`，扩展属性变更（包括 `xattrdir=dir` 与 `xattr=sa`）都保证持久。

为至少一个数据集创建 ZIL 时，此特性变为 `active`；当所有使用此特性的数据集的 ZIL 都被销毁后，会回到 `enabled` 状态。

### `zpool_checkpoint`

* **GUID**：`com.delphix:zpool_checkpoint`
* **只读兼容**：是

此特性启用 `zpool checkpoint` 命令，可以对池在命令发出时的状态建立检查点，之后可以回退到该检查点或将其丢弃。

使用 `zpool checkpoint` 命令为池建立检查点时，此特性变为 `active`。只有当池被回退或检查点被丢弃后，此特性才会回到 `enabled` 状态。

### `zstd_compress`

* **GUID**：`org.freebsd:zstd_compress`
* **依赖**：`extensible_dataset`
* **只读兼容**：否

`zstd` 是一种高性能压缩算法，兼具高压缩比与高速。与 `gzip` 相比，`zstd` 的压缩比略好而速度快得多。与 `lz4` 相比，`zstd` 的压缩比好得多而速度仅略慢。通常，`zstd` 的压缩速度为每线程 250 到 500 MB/s，解压缩速度超过每线程 1 GB/s。

当 `zstd` 特性被设置为 `enabled` 时，管理员可以使用 `zfs set compress=zstd 数据集` 为任意数据集开启 `zstd` 压缩（参见 zfs-set(8)）。一旦 `compress` 属性被设置为 `zstd`，此特性即变为 `active`，并且直到所有曾经把 compress 属性设置为 `zstd` 的文件系统全部被销毁后，才会回到 `enabled` 状态。

## 参考文献

zfs(8)、zpool(8)

2025 年 7 月 23 日
