# 压缩

ZFS 按记录、按数据集透明压缩。在多数工作负载上，即使在快速存储上，压缩也是净收益：写入的数据更少意味着 I/O 更少，而且现代算法的压缩速度快于磁盘吸收这一差异的速度。

自 OpenZFS 2.2.0 起，`compression` 属性默认为 `on`，因此新数据集默认启用压缩。在更早版本下创建的存储池与数据集默认为 `off` 并保持该设置——不要想当然，先查一下。

```sh
zfs get -r compression pool             # 实际设置及其来源
zfs set compression=zstd pool/data
zfs set compression=off pool/incompressible
```

更改该属性只影响新写入的数据。已有块保持写入时的状态；重写它们（`zfs send | zfs recv`、复制，或 [zfs-rewrite(8)](../../man/8/zfs-rewrite.8.md)）才是重新压缩它们的方式。

## 算法

### `on`

默认值。与其他所有取值不同，它不是固定算法——启用 `lz4_compress` 特性时为 `lz4`，否则为 `lzjb`，并且随着新算法加入，它可能改变。

### `lz4`

两个方向都很快，压缩率中等。几乎适用于一切的安全默认值。需要 `lz4_compress` 特性。

### `zstd` / `zstd-N`

更高的压缩率，更高的 CPU 代价。`N` 从 1（最快）到 19；不带数字的 `zstd` 即 `zstd-3`。`zstd-fast-N` 对应负的 zstd 级别，`N` 取 1–10、20、30……100、500、1000——`N` 越大越快、越弱。`zstd-fast` 即 `zstd-fast-1`。

### `gzip` / `gzip-N`

`N` 从 1 到 9；不带数字的 `gzip` 即 `gzip-6`。基本已被 `zstd` 取代，后者能以快得多的速度给出相近的压缩率。

### `lzjb`

最初的算法，为兼容性保留。

### `zle`

只压缩连续的零。

实际上：注重延迟与 CPU 时用 `lz4`，注重容量时用 `zstd`（3–7 级），只有对已压缩或已加密的数据才用 `off`。

## 究竟能省多少

块按 2 的 `ashift` 次方字节的整扇区分配，压缩后的记录会向上取整到扇区边界。如果压缩节省不足一个整扇区，该块就以未压缩形式存储。在此之外还有一个 12.5% 的最低节省阈值。

结果是：从空间核算上看，小记录压缩效果很差——当 `recordsize=16K`、扇区为 4K 时，一条记录占四个扇区，因此压缩必须节省至少 25%，才能在磁盘上真正省下空间。大记录给压缩留出的余地更大。

无论算法如何，除 `off` 外的任何设置都会检测全零块，并以空洞形式存储。

## 查看结果

```sh
zfs get compression,compressratio,refcompressratio pool/data
zfs list -o name,used,logicalused,compressratio -r pool
```

`compressratio` 是相对于数据集 `used` 空间（含后代）的倍数；`refcompressratio` 只覆盖 `referenced` 空间。比较 `logicalused` 与 `used` 能以字节为单位看到同一件事。

## 与其他特性的相互作用

* 压缩发生在加密**之前**，因此加密数据集仍能保留压缩率。由此引出的 CRIME 式注意事项，参见[原生加密](Encryption.md)。
* `zfs send -c` 以压缩形式发送已压缩的块——流更小，两端 CPU 都更省。参见[发送与接收](../Operations/Send-and-Receive.md)。
* 压缩与 `recordsize` 相互影响；参见[工作负载调优](../../Performance-Tuning/WorkloadTuning.md)。

## 延伸阅读

* [zfsprops(7)](../../man/7/zfsprops.7.md)——`compression`、`compressratio`、`logicalused`
* [工作负载调优](../../Performance-Tuning/WorkloadTuning.md)
