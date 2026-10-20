# zpoolprops(7)

## 名称

`zpoolprops` — ZFS 存储池的属性

## 说明

每个池都有若干关联属性。部分属性为只读统计信息，另一些属性可配置，并会改变池的行为。

用户属性不影响 ZFS 的行为。你可以用它们以适合所在环境的方式为池添加注记。有关用户属性的更多信息，参见下文“用户属性”一节。

以下属性为只读：

### `allocated`

池内已使用的存储空间量。有关更多信息，参见 `fragmentation` 与 `free`。

### `available`

池内可用的剩余空间量，已按 raidz 校验开销调整。`available` 属性的计算方式为：

`usable - used`

有关更多信息，参见 `usable`、`used` 与 `free`。

### `bcloneratio`

若不使用块克隆而存储所有已克隆块所需的存储空间总量，与实际使用存储量的比值。`bcloneratio` 属性的计算方式为：

`( ( bclonesaved + bcloneused ) * 100 ) / bcloneused`

### `bclonesaved`

若未使用块克隆则额外需要的存储空间量。

### `bcloneused`

已克隆块占用的存储空间量。

### `capacity`

已使用的池空间百分比。该属性也可以用其简写的列名 `cap` 表示。

### `dedupcached`

当前已加载到 ARC 中的去重表的总大小。参见 zpool-prefetch(8)。

### `dedup_table_size`

去重表的磁盘上总大小。

### `dedupratio`

若不使用去重而存储所有经去重的块所需的存储空间总量，与实际使用存储量的比值。`dedupratio` 属性的计算方式为：

`( ( dedupsaved + dedupused ) * 100 ) / dedupused`

### `dedupsaved`

若未使用去重则额外需要的存储空间量。这表示由去重节省的空间。

### `dedupused`

经去重的块占用的存储空间量。这是去重后磁盘上实际占用的物理空间。

### `expandsize`

池或设备内可用于扩充池总容量的未初始化空间量。对于整盘 vdev，这是 GPT 末尾之外的空间——通常发生在 LUN 被动态扩容，或磁盘被更换为更大容量的情况。对于分区 vdev，这是设备加入池后被追加到分区的空间，最可能是在原地调整分区大小时产生的。通过以 `autoexpand=on` 将其上线，或使用 `zpool online -e`，可以把该空间认领给池使用。

### `fragmentation`

池中的碎片化程度。随着 `allocated` 的空间量增加，定位 `free` 空间会变得更加困难。与拥有更多未碎片化剩余空间的池相比，这可能导致更低的写入性能。

### `free`

池内可用的剩余空间量。相比之下，zfs(8) 的 `available` 属性描述可以写入 ZFS 文件系统/卷的新数据量。zpool 的 `free` 属性通常不适用于此用途，其值也可能远大于 zfs 的 `available` 空间。这种差异由若干因素造成，包括 raidz 校验；zfs 的 reservation、quota、refreservation 与 refquota 属性；以及由 `spa_slop_shift` 预留的空间（有关更多信息，参见 zfs(4)）。

### `freeing`

文件系统或快照被销毁后，其占用的空间会异步返还给池。`freeing` 是尚待回收的空间量。随着时间推移，`freeing` 会减少，而 `free` 会增加。

### `guid`

池的唯一标识符。在 Linux 上，它是该池每个已挂载文件系统 UUID 的前半部分；参见 zfsprops(7) 中的 `guid` 属性。

### `health`

池当前的健康状况。该属性可能为 `ONLINE`、`DEGRADED`、`FAULTED`、`OFFLINE`、`REMOVED`、`UNAVAIL` 之一。

### `last_scrubbed_txg`

指示最近一次 scrub 操作已检查并修复至哪一个事务组（TXG）。这可用于了解池在特定时间点的数据完整性状态。zpool-scrub(8) 在给定 `-C` 标志时可以利用该属性，仅扫描自上次 scrub 完成以来发生变化的数据。使用 `-e` 标志执行错误 scrub 时，不会更新该属性。

### `leaked`

在 `freeing` 期间因损坏而未能释放的空间，现已永久泄漏到池中。

### `load_guid`

池的唯一标识符。与 `guid` 属性不同，该标识符在每次加载池时生成（即不会在导入/导出之间保留），并且在池加载期间不会改变（即使发生 `reguid` 操作）。

### `size`

存储池的总大小。

### `unsupported@guid`

关于该池上已启用但不受支持的特性的信息。有关详细信息，参见 zpool-features(7)。

### `usable`

存储池总大小的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`usable` 是用于分配的启发式值，不应将其视为可用空间的精确度量。

### `used`

存储池内已用存储的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`used` 是用于分配的启发式值，不应将其视为已用空间的精确度量。

空间使用属性报告存储池实际可用的物理空间。该物理空间可能与任一包含数据集实际可使用的空间总量不同。在 raidz 配置中，已使用的空间量取决于所写入数据的特性。此外，ZFS 会保留一部分空间用于内部记账，zfs(8) 命令会将其计入，而 zpool 命令则不会。对于大小合理且未满的池，这些影响应该不可察觉；但对于小型池，或接近完全写满的池，这些差异可能更加明显。

以下属性为分配类的只读指标：

* `class_dedup_allocated`、`class_dedup_available`、`class_dedup_capacity`、`class_dedup_expandsize`、`class_dedup_fragmentation`、`class_dedup_free`、`class_dedup_size`、`class_dedup_usable`、`class_dedup_used`

  该池 `dedup` metaslab 分配器类别的空间使用属性。

* `class_elog_allocated`、`class_elog_available`、`class_elog_capacity`、`class_elog_expandsize`、`class_elog_fragmentation`、`class_elog_free`、`class_elog_size`、`class_elog_usable`、`class_elog_used`

  该池 `embedded_log` metaslab 分配器类别的空间使用属性。

* `class_log_allocated`、`class_log_available`、`class_log_capacity`、`class_log_expandsize`、`class_log_fragmentation`、`class_log_free`、`class_log_size`、`class_log_usable`、`class_log_used`

  该池 `log` metaslab 分配器类别的空间使用属性。

* `class_normal_allocated`、`class_normal_available`、`class_normal_capacity`、`class_normal_expandsize`、`class_normal_fragmentation`、`class_normal_free`、`class_normal_size`、`class_normal_usable`、`class_normal_used`

  该池 `normal` metaslab 分配器类别的空间使用属性。

* `class_special_allocated`、`class_special_available`、`class_special_capacity`、`class_special_expandsize`、`class_special_fragmentation`、`class_special_free`、`class_special_size`、`class_special_usable`、`class_special_used`

  该池 `special` metaslab 分配器类别的空间使用属性。

* `class_special_elog_allocated`、`class_special_elog_available`、`class_special_elog_capacity`、`class_special_elog_expandsize`、`class_special_elog_fragmentation`、`class_special_elog_free`、`class_special_elog_size`、`class_special_elog_usable`、`class_special_elog_used`

  该池 `special_embedded_log` metaslab 分配器类别的空间使用属性。

每个分配类由以下值描述：

#### `allocated`

该分配类内已使用的存储空间量。

#### `available`

该分配类内可用剩余空间的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`available` 是用于分配的启发式值，不应将其视为可用空间的精确度量。实际可用空间取决于数据集记录大小、压缩等若干因素。

#### `capacity`

已使用的分配类空间百分比。

#### `expandsize`

该分配类内可用于扩充分配器容量的未初始化空间量。参见池范围的 `expandsize` 属性。

#### `fragmentation`

该分配类内剩余空间的碎片化程度。参见池范围的 `fragmentation` 属性。

#### `free`

该分配类内可用的剩余空间量。该值未针对数据集记录大小、压缩或 raidz 校验开销等因素调整。参见池范围的 `free` 属性。

#### `size`

该分配类的总大小。

#### `usable`

该分配类总大小的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`usable` 是用于分配的启发式值，不应将其视为可用空间的精确度量。

#### `used`

该分配类内已用存储的估计值，已按 raidz 校验开销调整。该调整假设使用固定的 128KiB 记录大小来计算数据与校验的比值。`used` 是用于分配的启发式值，不应将其视为已用空间的精确度量。

以下属性可在创建时和导入时设置：

### `altroot`

备用根目录。设置后，该目录会前置到池内任何挂载点之前。在检查一个挂载点不可信的未知池，或在典型路径无效的备用引导环境中时，可以这样使用。`altroot` 不是持久属性，仅在系统运行期间有效。设置 `altroot` 会使 `cachefile=none` 成为默认值，但可以通过显式设置覆盖。

以下属性只能在导入时设置：

### `readonly=on|off`

设置为 `on` 时，池将以只读模式导入。该属性也可以用其简写的列名 `rdonly` 表示。

以下属性可在创建时和导入时设置，并可用 `zpool set` 命令随后更改：

### `ashift=ashift`

池扇区大小的指数（以 2 为底，内部称 `ashift`）。9 到 16（含）之间的值有效；此外，值 0（默认值: `0`）表示使用内核的块层和 ZFS 内部例外表自动检测。I/O 操作将按指定大小的边界对齐。此外，最小（磁盘）写入大小也会设为指定大小，因此这代表空间与性能之间的权衡。为获得最佳性能，池扇区大小应大于或等于底层磁盘的扇区大小。设置该属性的典型场景是：性能很重要，且底层磁盘使用 4KiB 扇区，但出于兼容性考虑向操作系统报告 512B 扇区；在这种情况下，设置 `ashift=12`（即 `1<<12 = 4096`）。设置后，该属性会作为后续 vdev 操作（添加、附加与替换）的默认提示值。更改此值不会修改任何现有 vdev，即使更换磁盘也不例外；不过它可以用于，例如，用一个更新的 4KiB 扇区设备替换一块即将故障的 512B 扇区磁盘：这很可能导致性能变差，但同时可以避免数据丢失。

### `autoexpand=on|off`

控制底层 LUN 扩容时的自动池扩容。设置为 `on` 时，池会按照扩容后设备的大小重新调整大小。如果该设备是镜像或 raidz 的一部分，则该镜像/raidz 组内的所有设备都必须先扩容，新空间才会向池可用。默认值为 `off`。该属性也可以用其简写的列名 `expand` 表示。

### `autoreplace=on|off`

控制自动设备替换。设置为 `off` 时，设备替换必须由管理员使用 `zpool replace` 命令发起。设置为 `on` 时，任何出现在先前属于该池的设备同一物理位置的新的设备都会被自动格式化并替换。默认值为 `off`。该属性也可以用其简写的列名 `replace` 表示。使用虚拟磁盘（如 device mapper）时也可以使用 autoreplace，前提是使用由 vdev_id.conf 设置的 `/dev/disk/by-vdev` 路径。有关更多详细信息，参见 vdev_id(8) 手册页。autoreplace 与 autoonline 需要配置并运行 ZFS Event Daemon。有关更多详细信息，参见 zed(8) 手册页。

### `autotrim=on|off`

设置为 `on` 时，最近被释放且池不再分配的空间会被定期 TRIM。这使得支持 BLKDISCARD 的块设备 vdev（例如 SSD），或底层文件系统支持 hole-punching 的文件 vdev，能够回收未使用的块。该属性的默认值为 `off`。

自动 TRIM 不会在释放后立即回收块。相反，它会乐观地延迟，让较小的范围聚合成少数较大的范围，然后更高效地下发到存储上。对 L2ARC 设备启用 TRIM 的方式是将 `l2arc_trim_ahead > 0`。

请注意，自动修剪最近释放的数据块会给底层存储设备带来相当的压力。具体情况取决于特定设备处理这些指令的能力。对于低端设备，通过定期使用 `zpool trim` 命令执行按需（手动）TRIM，往往也能获得自动修剪的大部分收益。

### `bootfs=(unset)|pool[/dataset]`

标识根池的默认可引导数据集。该属性主要由安装与升级程序设置。并非所有 Linux 发行版的引导流程都使用 bootfs 属性。

### `cachefile=path|none`

控制池配置缓存的位置。系统启动时查找所有池，需要在根文件系统上存储一份配置数据的缓存副本。该缓存中的所有池会在系统启动时自动导入。某些环境（如安装与集群环境）需要将此信息缓存到其他位置，以免池被自动导入。设置该属性会将池配置缓存到其他位置，之后可用 `zpool import -c` 导入。设置为 `none` 会创建一个从不缓存的临时池；设置为空字符串 `""` 则使用默认位置。

多个池可以共享同一个缓存文件。由于内核会在池添加与移除时销毁并重建该文件，因此尝试访问此文件时需谨慎。当最后一个使用该 `cachefile` 的池被导出或销毁后，该文件将为空。

### `comment=text`

由可打印 ASCII 字符组成的字符串，即使池发生故障也会被存储并保持可用。管理员可以用该属性为池提供附加信息。

### `compatibility=off|legacy|file[,file]…`

指定池需与特定特性集保持兼容。设置为 `off`（或未设置）时禁用兼容模式（可启用所有特性）；设置为 `legacy` 时不得启用任何特性。设置为逗号分隔的文件名列表时（每个文件名可以是绝对路径，也可以是相对于 `/etc/zfs/compatibility.d` 或 `/usr/share/zfs/compatibility.d` 的路径），请求的特性列表将从这些文件中读取，文件内以空白和/或逗号分隔。只有所有文件中都存在的特性才可以启用。

有关兼容特性集运行机制的更多信息，参见 zpool-features(7)、zpool-create(8) 与 zpool-upgrade(8)。

### `dedup_table_quota=number|none|auto`

该属性限制池去重表的磁盘上大小。达到该大小后，将不再向去重表中添加条目；如果已存在去重表且大于该大小，设置此属性时也不会删除其中的条目。现有条目的引用计数仍会更新。

由于表条目的磁盘上实际大小（在计算配额时可能采用近似值）会影响表的大小限制，实际限制值可能高于或低于配额。也就是说，把配额设为 1M 可能导致最大大小略低于或略高于该值。设置为 `none` 可禁用。默认使用自动模式，此时以专用 dedup vdev 的大小作为配额上限。

`dedup_table_quota` 属性适用于 legacy 去重表与 fast 去重表。

### `dedupditto=number`

该属性已弃用，不再有任何作用。

### `delegation=on|off`

控制是否根据数据集上定义的数据集权限授予非特权用户访问权限。有关 ZFS 委托管理的更多信息，参见 zfs(8)。

### `failmode=wait|continue|panic`

控制池发生灾难性故障时的系统行为。这种情况通常源于与底层存储设备失去连接，或池内所有设备故障。此类事件的行为如下：

#### `wait`

阻止所有 I/O 访问，直到设备连接恢复并通过 `zpool clear` 清除错误。这是默认行为。

#### `continue`

对任何新的写入 I/O 请求返回 `EIO`，但允许读取任何剩余的健康设备。尚未提交到磁盘的写入请求会被阻塞。

#### `panic`

向控制台打印消息，并生成系统崩溃转储。

### `feature@feature_name=enabled`

该属性的值是 `feature_name` 的当前状态。设置该属性时唯一有效的值是 `enabled`，它会将 `feature_name` 置为已启用状态。有关特性状态的详细信息，参见 zpool-features(7)。

### `listsnapshots=on|off`

控制在没有 `-t` 选项运行 `zfs list` 时，是否输出与该池关联的快照信息。默认值为 `off`。该属性也可以用其简写名称 `listsnaps` 表示。

### `multihost=on|off`

控制 `zpool import` 期间是否执行池活动检查。一旦判定某池处于活动状态，即使使用 `-f` 选项也无法导入。该属性旨在用于多台主机访问共享存储上同一池的故障切换配置。

multihost 仅在导入时提供保护。无论 vdev 类型如何，它都不能防止单个设备被用于多个池。参见 `zpool create` 下的相关讨论。

该属性为 `on` 时，会定期向存储写入，以表明该池正在使用。参见 zfs(4) 手册页中的 `zfs_multihost_interval`。要启用该属性，每台主机都必须设置唯一的 hostid。有关更多详情，参见 genhostid(1)、zgenhostid(8) 与 spl(4)。默认值为 `off`。

### `version=version`

池当前的磁盘上版本。它可以增大，但绝不能减小。更新池的首选方式是使用 `zpool upgrade` 命令，但在需要特定版本以保持向后兼容时，也可以使用该属性。一旦池中启用了特性标志，该属性将不再有效。

### 用户属性

除标准原生属性之外，ZFS 还支持任意用户属性。用户属性不影响 ZFS 的行为，但应用程序或管理员可以用它们为池添加注记。

用户属性名必须包含冒号 `:` 字符，以便与原生属性区分。属性名可以包含小写字母、数字以及以下标点字符：冒号 `:`、连字符 `-`、句点 `.` 与下划线 `_`。惯例上属性名分为两部分，例如 `module:property`，但 ZFS 并不强制这一命名空间。用户属性名最长 255 个字符，且不能以连字符 `-` 开头。

在程序化地使用用户属性时，强烈建议属性名的 `module` 部分使用反向 DNS 域名，以降低两个独立开发的软件包把同一属性名用作不同用途的概率。

用户属性的值是任意字符串，且从不校验。所有操作属性的命令（`zpool list`、`zpool get`、`zpool set` 等）都可以用来操作原生属性与用户属性。使用 `zpool set name=` 清除用户属性。属性值最长 8192 字节。

2026 年 9 月 9 日
