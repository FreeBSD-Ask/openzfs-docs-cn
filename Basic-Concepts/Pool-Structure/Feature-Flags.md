# 特性标志

ZFS 的磁盘格式最初使用单一数字进行版本控制，每当格式发生变化时该数字就会增加。这种编号方式在 ZFS 由单一组织开发时是可行的。

对于 OpenZFS 的分布式开发，版本编号方式不适用。任何对数字的修改，都需要所有实现就磁盘格式的每一次更改达成一致。

OpenZFS 特性标志——作为传统版本编号的替代—— **可为磁盘格式的每次更改设置唯一命名的池属性** 。这种方法支持：

* 独立的格式更改
* 相互依赖的格式更改

## 特性状态

每个特性都表现为名为 `feature@<short-name>` 的池属性，并处于以下三种状态之一：

* `disabled`：磁盘格式尚未更改，且除非管理员启用，否则不会更改。
* `enabled`：已标记为启用，但磁盘格式更改 **尚未发生** 。池仍可被不了解该特性的软件导入——直到某个操作触发该更改（随时可能发生），该特性随即转为 `active`。
* `active`：格式更改已生效。软件必须支持该特性才能以读写方式导入该池。

```sh
zpool get all pool | grep feature@
zpool get feature@large_blocks pool
```

**特性一旦启用便无法禁用。** 部分特性在使用它的对象被释放后可以从 `active` 返回 `enabled`（例如 `block_cloning` 在最后一个克隆块消失后），但这取决于具体特性。

启用某个特性会自动启用它所依赖的所有特性。

## 只读兼容

有些格式更改不会妨碍其他软件*读取*池。如果池上所有不受支持的特性都是只读兼容的，该池仍能以只读方式导入：

```sh
zpool import -o readonly=on pool
```

对于已导入池上每个不受支持的特性，属性 `unsupported@<feature-name>` 会说明为何允许导入：`inactive`（该特性仅为 `enabled`，格式仍然兼容）或 `readonly`（该特性只读兼容，且池以只读方式导入）。

## 兼容性

当池使用的所有 **特性** 都被多个 OpenZFS 实现支持时，磁盘格式即可在这些实现之间移植。

启用后具有独占性的特性应定期移植到所有发行版。

## 兼容性特性集

`compatibility` 池属性把池固定到某个具名的磁盘格式，使其在别处——较早的发行版、其他操作系统或引导加载程序——仍可导入。

* `off`（默认）：不做限制，任何特性都可以启用。
* `legacy`：完全不允许启用任何特性——无论通过 `zpool upgrade` 还是设置 `feature@…=enabled` 都无法启用，也不能把池升级到更新的磁盘版本。这是有意的安全限制。
* `file[,file…]`：一个或多个特性集文件。只有 **所有** 列出的文件中都存在的特性才可启用。

```sh
zpool create -o compatibility=grub2-2.12 bpool ...
zpool set compatibility=openzfs-2.1-linux tank
zpool get compatibility tank
```

特性集名称会按 `/etc/zfs/compatibility.d`（本地，优先）或 `/usr/share/zfs/compatibility.d`（由发行版随附）解析，也可以直接给出绝对路径。随附的特性集覆盖各平台的 OpenZFS 版本（`openzfs-2.1-linux`、`openzfs-2.2`、`openzfs-2.3`、`openzfs-2.4`、`openzfs-2.0-freebsd` 等）、较早的 ZoL 与 FreeBSD 版本、GRUB（`grub2-2.06`、`grub2-2.12`），以及按年份命名的基线（`compat-2018` … `compat-2021`）。

```sh
ls /usr/share/zfs/compatibility.d/
```

实际用途主要有两种：一是把 **启动池** 限制在引导加载程序所能理解的范围内，二是让池在较旧的系统上仍可导入。设置 `compatibility` 还能让 `zpool status` 不再就所选集合之外的未启用特性反复提醒。

## 升级存储池

```sh
zpool upgrade                   # 列出含有未启用特性的池
zpool upgrade -v                # 本次构建支持哪些特性
zpool upgrade pool              # 在某个池上启用这些特性
zpool upgrade -a                # 在所有池上启用
```

`zpool upgrade` 会启用所有受支持的特性，但受 `compatibility` 约束：如果某个特性集正在生效，则只启用该集合内的特性；若为 `legacy`，则什么也不会发生。

> **警告**
>
> **升级是单向的。** 特性之后无法禁用。一旦启用的特性变为 `active`，池便无法再被不支持这些特性的软件导入——包括你可能需要回退启动的旧内核、应急 U 盘，以及根池上的引导加载程序。
>
> 升级要有意识地进行，不要因为 `zpool status` 提示了就条件反射地升级。未升级的池照常工作，只是不提供较新的特性。

注意，`zpool status` 报告“some supported features are not enabled”只是提示性信息。尤其在根池或启动池上，请先确认引导加载程序支持哪些特性——参见[以 ZFS 为根文件系统的指南](../../GettingStarted.md)。

## `zfs upgrade` 是另一回事

数据集带有自己的磁盘版本，与池的特性无关。

```sh
zfs upgrade                     # 列出未处于最新版本的文件系统
zfs upgrade -v                  # 本次构建支持哪些版本
zfs upgrade -r pool/data        # 升级某个子树
zfs upgrade -a                  # 全部升级
```

这里也存在同样的单向限制，并且多一层后果：升级之后，由这些文件系统的*新*快照生成的 `zfs send` 流也无法被较旧的 ZFS 版本接收。如果你要复制到较旧的系统，受影响的不只是本地挂载，复制本身也会中断。

## 参考资料

[ZFS Feature Flags](http://web.archive.org/web/20160419064650/http://blog.delphix.com/csiden/files/2012/01/ZFS_Feature_Flags.pdf)（Christopher Siden，2012-01，Internet Archive Wayback Machine）特别指出：“… 对于池版本 1-28，遗留版本号仍然存在 …”。

[zpool-features(7) 手册页](../../man/7/zpool-features.7.md) - OpenZFS

[zpool-features](http://illumos.org/man/5/zpool-features) (5) – illumos

## 各操作系统的特性标志实现

| 特性标志                             | 只读兼容 | OpenZFS 0.6.5.11 | OpenZFS 0.7.13 | OpenZFS 0.8.6 | OpenZFS 2.0.7 | OpenZFS 2.1.16 | OpenZFS 2.2.11 | OpenZFS 2.3.9 | OpenZFS 2.4.4 | OpenZFS master | FreeBSD(pre-OpenZFS) 12 | Illumos master | Joyent master | NetBSD main | Nexenta 4.0.5-FP | Nexenta master | OmniOS CE r151056 | OmniOS CE r151058 | OmniOS CE master | OpenZFS on OS X 2.4.1 | OpenZFS on OS X 2.4.1p1 | OpenZFS on OS X 2.4.4rc1 | OpenZFS on OS X main |
| :----------------------------------- | :------- | :--------------- | :------------- | :------------ | :------------ | :------------- | :------------- | :------------ | :------------ | :------------- | :---------------------- | :------------- | :------------ | :---------- | :--------------- | :------------- | :---------------- | :---------------- | :--------------- | :-------------------- | :---------------------- | :----------------------- | :------------------- |
| org.zfsonlinux:allocation_classes    | 是       | 否               | 否             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:async_destroy            | 是       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.openzfs:blake3                   | 否       | 否               | 否             | 否            | 否            | 否             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.fudosecurity:block_cloning       | 是       | 否               | 否             | 否            | 否            | 否             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.truenas:block_cloning_endian     | 是       | 否               | 否             | 否            | 否            | 否             | 否             | 否            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 否                   |
| com.datto:bookmark_v2                | 否       | 否               | 否             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:bookmark_written         | 否       | 否               | 否             | 否            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:bookmarks                | 是       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.nexenta:class_of_storage         | 是       | 否               | 否             | 否            | 否            | 否             | 否             | 否            | 否            | 否             | 否                      | 否             | 否            | 否          | 是               | 是             | 否                | 否                | 否               | 否                    | 否                      | 否                       | 否                   |
| org.openzfs:device_rebuild           | 是       | 否               | 否             | 否            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:device_removal           | 否       | 否               | 否             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 否          | 否               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.openzfs:draid                    | 否       | 否               | 否             | 否            | 否            | 是             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.seagate:draid_failure_domains    | 否       | 否               | 否             | 否            | 否            | 否             | 否             | 否            | 否            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 否                    | 否                      | 是                       | 否                   |
| com.klarasystems:dynamic_gang_header | 否       | 否               | 否             | 否            | 否            | 否             | 否             | 否            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 否                   |
| org.illumos:edonr                    | 否       | 是¹              | 是¹            | 是¹           | 是¹           | 是¹            | 是             | 是            | 是            | 是             | 否                      | 是             | 是            | 否          | 否               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:embedded_data            | 否       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 否               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:empty_bpobj              | 是       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:enabled_txg              | 是       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.datto:encryption                 | 否       | 否               | 否             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 是²            | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:extensible_dataset       | 否       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.klarasystems:fast_dedup          | 是       | 否               | 否             | 否            | 否            | 否             | 否             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.joyent:filesystem_limits         | 是       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:head_errlog              | 否       | 否               | 否             | 否            | 否            | 否             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:hole_birth               | 否       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.open-zfs:large_blocks            | 否       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 否               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.zfsonlinux:large_dnode           | 否       | 否               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.klarasystems:large_microzap      | 是       | 否               | 否             | 否            | 否            | 否             | 否             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:livelist                 | 是       | 否               | 否             | 否            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:log_spacemap             | 是       | 否               | 否             | 否            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.zfsonlinux:longname              | 否       | 否               | 否             | 否            | 否            | 否             | 否             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| org.illumos:lz4_compress             | 否       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.nexenta:meta_devices             | 是       | 否               | 否             | 否            | 否            | 否             | 否             | 否            | 否            | 否             | 否                      | 否             | 否            | 否          | 是               | 是             | 否                | 否                | 否               | 否                    | 否                      | 否                       | 否                   |
| com.joyent:multi_vdev_crash_dump     | 否       | 否               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:obsolete_counts          | 是       | 否               | 否             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 否          | 否               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.truenas:physical_rewrite         | 是       | 否               | 否             | 否            | 否            | 否             | 否             | 否            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 否                   |
| org.zfsonlinux:project_quota         | 是       | 否               | 否             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.openzfs:raidz_expansion          | 否       | 否               | 否             | 否            | 否            | 否             | 否             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:redacted_datasets        | 否       | 否               | 否             | 否            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:redaction_bookmarks      | 否       | 否               | 否             | 否            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:redaction_list_spill     | 否       | 否               | 否             | 否            | 否            | 否             | 否             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.datto:resilver_defer             | 是       | 否               | 否             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.illumos:sha512                   | 否       | 否               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 否               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.illumos:skein                    | 否       | 否               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 否               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:spacemap_histogram       | 是       | 是               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 是          | 是               | 是             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:spacemap_v2              | 是       | 否               | 否             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.zfsonlinux:userobj_accounting    | 是       | 否               | 是             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.nexenta:vdev_properties          | 是       | 否               | 否             | 否            | 否            | 否             | 否             | 否            | 否            | 否             | 否                      | 否             | 否            | 否          | 是               | 是             | 否                | 否                | 否               | 否                    | 否                      | 否                       | 否                   |
| com.klarasystems:vdev_zaps_v2        | 否       | 否               | 否             | 否            | 否            | 否             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |
| com.nexenta:wbc                      | 否       | 否               | 否             | 否            | 否            | 否             | 否             | 否            | 否            | 否             | 否                      | 否             | 否            | 否          | 否               | 是             | 否                | 否                | 否               | 否                    | 否                      | 否                       | 否                   |
| org.openzfs:zilsaxattr               | 是       | 否               | 否             | 否            | 否            | 否             | 是             | 是            | 是            | 是             | 否                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| com.delphix:zpool_checkpoint         | 是       | 否               | 否             | 是            | 是            | 是             | 是             | 是            | 是            | 是             | 是                      | 是             | 是            | 否          | 否               | 否             | 是                | 是                | 是               | 是                    | 是                      | 是                       | 是                   |
| org.freebsd:zstd_compress            | 否       | 否               | 否             | 否            | 是            | 是             | 是             | 是            | 是            | 是             | 否                      | 否             | 否            | 否          | 否               | 否             | 否                | 否                | 否               | 是                    | 是                      | 是                       | 是                   |

**注释**

1. [FreeBSD 在内置 OpenZFS 2.1 版本之前未启用 Edonr 支持](https://github.com/openzfs/zfs/pull/12735)
2. 对于 `com.datto:encryption`，[虽然 Illumos 的加密逻辑几乎相同，但其格式与 OpenZFS 加密格式并非 100% 兼容，因此跨平台加密可能存在问题](https://illumos.topicbox.com/groups/discuss/Ta2162fbb2358fa0e)

此表格由解析特性标志手册页生成，完全依赖于良好且准确的文档。

最后更新时间（上游生成）：2026-10-20T03:24:04.253165Z，使用 [compatibility_matrix.py](https://github.com/openzfs/openzfs-docs/tree/master/scripts/compatibility_matrix.py)。
