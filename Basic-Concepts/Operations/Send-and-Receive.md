# 发送与接收

`zfs send` 把快照序列化为字节流，`zfs receive` 把该流还原为数据集。二者合起来构成 ZFS 原生的复制与备份机制。

由于流是根据 ZFS 自身的块级记账生成的，增量发送只需读取两个快照之间实际发生变化的块——它从不遍历目录树去查找被修改的文件。这使复制成本与变化数据量成正比，而不是与数据集大小成正比，这也是在 ZFS 上它优于 `rsync` 等基于文件的工具的主要原因。

流带有校验和，因此网络或中间存储引入的损坏会在接收时被发现。

## 完整流

一切从快照开始：

```sh
zfs snapshot pool/data@2026-07-21
zfs send pool/data@2026-07-21 | ssh backup zfs receive tank/data
```

接收端创建 `tank/data` 以及快照 `tank/data@2026-07-21`。目标数据集不得已经存在，除非你正把增量流接收进它。

流只是字节，因此也可以存入文件或经由任意管道：

```sh
zfs send pool/data@2026-07-21 | zstd -3 > /mnt/usb/data-full.zfs.zst
```

把流存入文件适合传输，但作为归档格式很差：单个字节损坏就可能使整个流无法接收，而接收后的数据集有校验、可 scrub、可修复。凡是你打算长期保存的内容，都应接收进真实存储池。

## 增量流

`-i` 发送两个快照之间的差异。源快照必须仍存在于接收端。

```sh
zfs snapshot pool/data@2026-07-22
zfs send -i pool/data@2026-07-21 pool/data@2026-07-22 \
    | ssh backup zfs receive tank/data
```

`-I` 发送两者之间的每一个中间快照，因此接收端得到相同的快照历史，而不只是两个端点：

```sh
zfs send -I pool/data@2026-07-21 pool/data@2026-07-28 | ...
```

增量源也可以是书签，这使发送端能在仍然计算差异的同时，释放旧快照占用的空间：

```sh
zfs bookmark pool/data@2026-07-21 pool/data#2026-07-21
zfs destroy pool/data@2026-07-21
zfs send -i pool/data#2026-07-21 pool/data@2026-07-22 | ...
```

书签是什么，见[快照、克隆与书签](../Datasets/Snapshots-and-Clones.md)。

## 复制整个层级

`-R` 生成复制流包：所指定的数据集及其全部后代，直到所指定的快照。接收时，属性、快照、后代文件系统与克隆均被保留。

```sh
zfs snapshot -r pool/home@2026-07-21
zfs send -R pool/home@2026-07-21 | ssh backup zfs receive -u tank/home
```

与 `-i`/`-I` 结合，它就成为常用的“让目标与源完全一致”的工具。在接收端，`-F` 还会销毁发送端已不存在的快照与文件系统，并在接收前把目标回滚到其最新的快照：

```sh
zfs send -R -I pool/home@sunday pool/home@monday \
    | ssh backup zfs receive -F -u tank/home
```

`-F` 会丢弃目标端的数据。若不确定一个流会做什么，请先运行 `-n -v`。

`-X` 从递归发送中排除指定的数据集，`-s` 则让递归发送在遇到快照缺失的数据集时跳过（并给出警告），而不是中止。

## 常用的发送选项

### `-c`（`--compressed`）

以压缩形式发送磁盘上已压缩的块。流更小，两端工作量也更少，因为无需解压再重新压缩。对启用了压缩的数据集，这通常是默认选择。

### `-L`（`--large-block`）

允许流中出现大于 128 KiB 的记录。不加此项时，`recordsize` 更大的数据集会以更小的块发送，速度更慢，且会改变接收端的块布局。若 `large_blocks` 存储池特性被禁用，或 `recordsize` 从未设置为大于 128 KiB，此项无效。

### `-e`（`--embed`）

以该形式发送使用内嵌数据（存放在块指针内部的极小数据块）的块。要求两端均具备 `embedded_data` 特性。

### `-p`（`--props`）

在流中包含数据集属性。`-R` 隐含此项。

### `-w`（`--raw`）

完全按数据在磁盘上的原样发送。对加密数据集而言，这意味着流保持加密，因此备份无需加载密钥，接收端机器也从不需要它们。参见[原生加密](../Data-Storage/Encryption.md)。

### `-h`（`--holds`）

在所发送的快照中包含用户 hold。

### `-n -v` / `-P`

试运行并估算大小；`-P` 以机器可解析的形式输出。任何大规模或破坏性传输之前都值得运行一次。

## 常用的接收选项

### `-u`

不挂载接收到的文件系统。在备份服务器上这几乎总是你想要的——目标不应遮蔽本地路径。

### `-d` / `-e`

重写目标名称：`-d` 去掉源数据集名的第一个组成部分，`-e` 只保留最后一个。两者都相对于所指定的目标文件系统。

### `-o property=value` / `-x property`

覆盖流中携带的某个属性，或将其排除，使本地设置（或继承）生效。目标端设 `-o readonly=on` 可防止意外写入，否则下一次增量接收将被迫回滚；`-x mountpoint` 是防止备份副本占用源挂载点的常用做法。

### `-F`

先把目标回滚到其最新快照；对增量复制流，还会销毁发送端已消失的数据集与快照。

### `-s`

传输中断时保留部分接收的状态，使其可以续传而不是重来。见下文。

## 续传中断的传输

通过不可靠链路进行数 TB 的首次复制，不必从头开始。当接收端使用了 `-s`，部分接收的状态会被保留，并作为目标数据集的 `receive_resume_token` 属性暴露出来：

```sh
# 接收端
zfs receive -s tank/data
# ……连接中断……
zfs get -H -o value receive_resume_token tank/data

# 发送端，使用该令牌
zfs send -t <token> | ssh backup zfs receive -s tank/data
```

这要求接收端存储池具备 `extensible_dataset` 特性。被放弃的部分接收可用 `zfs receive -A` 清理，它会释放占用的空间。

## 实践提示

**保留一个共同快照。** 两端的保留策略必须至少留下一个共同快照（或发送端的书签），否则下一次增量会失败，并需要完整重传。

**不要修改目标端。** 任何写入都会破坏下一次增量接收，直到数据集回滚；`readonly=on` 可避免此问题。

**ssh 往往是瓶颈。** 发送与接收都是突发式的，因此在两端缓冲管道（`mbuffer`、使用大块大小的 `dd`）通常有帮助。

**特性选项必须匹配。** 用 `-L`、`-c`、`-e` 或 `-w` 生成的流，需要接收端存储池具备相应特性。

手工处理快照、保留、hold 与续传令牌这些记账工作会变得繁琐。建立在 `zfs send`/`receive` 之上的第三方工具会处理这些——参见[按计划创建](../Datasets/Snapshots-and-Clones.md#按计划创建)，因为同一批工具通常两者都做。

关于 `hole_birth` 等流相关的注意事项，参见 [FAQ](../../Project-and-Community/FAQ.md)。

## 延伸阅读

* [zfs-send(8)](../../man/8/zfs-send.8.md)、[zfs-receive(8)](../../man/8/zfs-receive.8.md)
* [zfs-bookmark(8)](../../man/8/zfs-bookmark.8.md)
* [zfs-redact(8)](../../man/8/zfs-send.8.md)——发送移除了选定数据的流
* [zstream(8)](../../man/8/zstream.8.md)——检查与操作流文件
* [FAQ：发送与接收流](../../Project-and-Community/FAQ.md)
