# 去重

去重在块级别消除冗余数据：相同的块只存储一份，并在文件之间共享。它是同步的——每次写入都要在去重表（DDT）中查找之后才会落盘。

> **警告**
>
> 除非有明确理由，否则不要启用去重。它是 ZFS 中资源消耗最大的特性，在容量规划不当的系统上启用它会导致 I/O 变慢、管理操作变慢，最坏情况下存储池会因为 DDT 放不进内存而无法导入。先试试[压缩](Compression.md)。

## 代价

每个唯一块都会有一条 DDT 条目。查找发生在每次写入时，每次释放也必须查阅 DDT。按**每 1 TiB 存储数据至少 1.25 GiB 内存**规划；实际数字取决于块大小以及数据中真正重复的比例。

只有当重复真实且大量存在时，去重才划算——例如来自同一基础镜像的虚拟机镜像、接收大量相似系统的备份目标。对于一般文件存储，压缩通常能以零头的代价获得大部分收益。还要注意，克隆与基于 `zfs send` 的工作流本就共享块而无需去重，块克隆（`copy_file_range`）也是如此。

## 启用

`dedup` 是数据集属性，因此可以只对受益的数据集启用。它默认为 `off`，且更改只影响新写入的数据。

```sh
zfs set dedup=on pool/vmimages
zfs set dedup=blake3,verify pool/vmimages
```

取值为 `off`、`on`、`verify`，或显式指定校验和——`sha256`、`sha512`、`skein`、`edonr` 或 `blake3`——每个都可以附带 `,verify`。默认的去重校验和为 `sha256`。启用去重时，该校验和会覆盖 `checksum` 属性。

`verify` 让 ZFS 在两个块的签名相同时做逐字节比较，代价是每次匹配多一次读取。单独的 `verify` 表示 `sha256,verify`，并且它与 `edonr` 一起使用时是强制的。

## 观察这张表

```sh
zpool status -D pool
zpool get dedupratio,dedup_table_size,dedupused,dedupsaved pool
zdb -DD pool          # 详细的 DDT 直方图
```

`dedupratio` 是不去重所需存储与实际使用量之比；`dedupsaved` 以字节表达同一件事。

在打开去重之前，`zdb -S pool` 会为池中已有的数据模拟 DDT，并打印你本可获得的去重比。如果它没有明显超过 2 倍，去重就不值得。

## 让表保持有界

去重的失效模式是 DDT 无界增长。有两个机制应对它：

**配额。** 存储池属性 `dedup_table_quota` 限制 DDT 的磁盘大小。达到上限后不再添加新条目——已有条目的引用计数仍会更新。默认值为 `auto`，即在有专用去重 vdev 时按其容量确定上限；`none` 表示不限制。实际生效的大小可能略高于或略低于请求值。它同时适用于旧式与快速去重表。

```sh
zpool set dedup_table_quota=100G pool
```

**清理。** `zpool ddtprune` 移除较旧的*唯一*（非重复）条目，为较新的重复条目腾出空间；可按唯一条目的目标百分比或按天数指定。

```sh
zpool ddtprune -d 30 pool     # 30 天以前的条目
zpool ddtprune -p 25 pool     # 25% 的唯一条目
```

**快速去重**（`fast_dedup` 存储池特性）启用了更先进的去重表格式，上述机制都围绕它构建。当第一个去重块写入新的去重表时，它变为 `active`，并在所有这些块被释放后回到 `enabled`。既有存储池保留其旧式表；新表会在存储池创建时、或启用去重的数据集开始使用新校验和时创建。

**专用去重 vdev**（`zpool add pool dedup <设备>`）把 DDT 移到快速存储上，这才使去重在较大的池上切实可行。它应当具备冗余——丢失它就会丢失存储池。

## 与加密的相互作用

去重可用于加密数据集，但出于安全考虑，数据集只与自身、其快照和克隆去重。它还会泄露数据集内哪些块是相同的，并为每个写入的块增加 CPU 开销。参见[原生加密](Encryption.md)。

## 关闭它

把 `dedup` 设为 `off` 只会阻止新块被去重，不会撤销任何东西：已有块保持去重状态，DDT 会一直保留到它们全部被释放。要彻底摆脱它，必须重写数据——例如复制到新数据集再销毁旧的。

## 延伸阅读

* [zfsconcepts(7)](../../man/7/zfsconcepts.7.md)——`Deduplication`
* [zfsprops(7)](../../man/7/zfsprops.7.md)——`dedup`
* [zpoolprops(7)](../../man/7/zpoolprops.7.md)——`dedup_table_quota`、`dedup_table_size`、`dedupratio`
* [zpool-ddtprune(8)](../../man/8/zpool-ddtprune.8.md)
* [工作负载调优](../../Performance-Tuning/WorkloadTuning.md)
