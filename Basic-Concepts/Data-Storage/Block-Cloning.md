# 块克隆

块克隆制作文件或其一部分的浅副本：新文件引用已有的数据块，而不是复制它们。之后对任一侧的写入都会为受影响的块取一份私有副本。这就是实现*reflink*（文件级写时复制）的机制。

复制一个 50 GiB 的文件几乎是瞬间的，也不占用额外空间，因为没有数据被读取或写入——只创建了引用。

块克隆需要 `block_cloning` 存储池特性，它会在第一个块被克隆时变为 `active`，并在最后一个克隆块被释放时回到 `enabled`。

## 如何触发

与去重不同，克隆从不是自动的——必须由程序主动请求，通常经由 `copy_file_range(2)`。许多常用工具已经这样做了：

```sh
cp --reflink=auto bigfile copy       # GNU coreutils
cp bigfile copy                      # 较新版本默认尝试这种方式
```

要了解某个工具是否会尝试块克隆，请在其文档中查找“clone”“reflink”或“dedupe”。

## 限制

以下情况无法克隆块：

* 只克隆块的一部分——克隆以整个块为单位；
* 数据尚未写入磁盘；
* 源与目标的 `recordsize` 不同；
* 数据集不共用同一个主加密密钥。

ZFS 确实会尝试跨数据集克隆（包括加密数据集），但操作系统另有自己的限制——多数 Linux 版本根本不允许跨数据集克隆。当克隆无法进行时，复制会静默退化为读取并写入数据，因此一个看起来慢的 `cp`，通常是克隆没有发生。

## 块克隆与去重

两者最终都让一个块被多次引用，但它们不是彼此的替代品：

|  | 块克隆 | 去重 |
| ---- | ---- | ---- |
| 触发方式 | 程序的显式请求 | 每次写入，同步进行 |
| 记账结构 | 块引用表（BRT），开销极小 | 去重表（DDT），庞大且吃内存 |
| 可以一直开着 | 可以 | 只有在仔细规划容量后才行 |
| 发现重复块 | 否——只克隆被告知克隆的内容 | 是，存储池内任意位置 |

由于 BRT 的开销极小，块克隆完全可以一直保持启用——这对[去重](../Data-Storage/Deduplication.md)并不成立。

## 核算收益

```sh
zpool get bcloneused,bclonesaved,bcloneratio pool
zdb -T pool          # BRT 统计
```

`bcloneused` 是被克隆块占用的空间，`bclonesaved` 是若不克隆所需的空间，`bcloneratio` 则以倍数表达同一含义。

相关的特性 `block_cloning_endian` 修正了 BRT 条目最初存储方式中的字节序问题；它在第一个 BRT ZAP 被创建时激活，以保持既有存储池的兼容性。

## 延伸阅读

* [zfsconcepts(7)](../../man/7/zfsconcepts.7.md)——`Block cloning`
* [zpool-features(7)](../../man/7/zpool-features.7.md)——`block_cloning`、`block_cloning_endian`
* [zpoolprops(7)](../../man/7/zpoolprops.7.md)——`bcloneused`、`bclonesaved`、`bcloneratio`
* [去重](../Data-Storage/Deduplication.md)、[快照、克隆与书签](../Datasets/Snapshots-and-Clones.md)
