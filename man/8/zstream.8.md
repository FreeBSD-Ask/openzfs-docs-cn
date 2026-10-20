# zstream(8)

## 名称

`zstream` — 对 ZFS 发送流执行各种操作

`zstreamdump(8)` 是 `zstream(8)` 的历史别名。

## 概述

```sh
zstream decompress [-v] [对象[,偏移[,压缩类型]…]] [文件]
```

```sh
zstream drop_records [-v] [对象[,偏移…]] [文件]
```

```sh
zstream dump [-Cvd] [文件]
```

```sh
zstream raw [-v] [-b 最大缓冲区数] [-g 来源 GUID] 镜像 | 设备 [文件]
```

```sh
zstream recompress [-t 线程数] 压缩类型 [文件]
```

```sh
zstream redup [-v] 文件
```

```sh
zstream token 恢复令牌
```

## 说明

`zstream` 对 `zfs send` 命令创建的发送流执行各种操作。除 `token` 子命令（它接受的是一个恢复令牌，而不是流）外，每个子命令都会从作为其最后一个参数的 `file` 读取发送流；未指定 `file` 时，则从标准输入读取。`redup` 子命令需要一个 `file`；它会重新读取流的较早部分来解析去重记录，因此无法从管道接受输入。

### `zstream decompress [-v] [object[,offset[,compress_type]…]] [file]`

解压发送流中指定的记录。当 ZFS 元数据中记录的压缩类型不正确时，可以用此子命令来恢复数据。请指定每个待解压记录的对象编号与字节偏移，也可以另外指定（真正的）压缩类型 `compress_type`。

`compress_type` 可以是 `compression` 属性接受的任何值，但不能是 `on`，例如 `off`、`gzip`、`lz4`、`lzjb`、`zstd` 或 `zle`。压缩级别（如 `gzip-3` 或 `zstd-5`）可以接受但会被忽略；解压时只有算法是重要的。

如果未指定 `compress_type`，则使用记录自身元数据中记录的压缩类型。

对于该对象，从该偏移开始的每一条记录都会被解压（如果可能的话）。但有时可能无法做到，因为一条记录可能在流的某些快照中损坏，而在其他快照中并未损坏。

将压缩类型指定为 `off` 会相应地更改流的元数据，而不尝试解压。如果记录本身已经未压缩，但元数据坚称其已压缩，此选项就很有用。

修复后的流写入标准输出。

#### `-v`

详细模式。打印已解压记录的摘要。

### `zstream drop_records [-v] [object[,offset…]] [file]`

从指定的 `file` 或标准输入读取的发送流中，移除按对象编号与字节偏移选定的记录。目前只能移除 WRITE 与 WRITE_EMBEDDED 记录。修复后的流写入标准输出。

#### `-v`

详细模式。打印已移除记录的摘要。

### `zstream dump [-Cvd] [file]`

打印指定发送流的信息，包括头部与记录数量。该流从指定的 `file` 或标准输入读取。

#### `-C`

跳过校验和的验证。

#### `-v`

详细模式。打印每条记录的元数据。重复此选项还会打印记录校验和。

#### `-d`

除校验和外，还转储每条记录中包含的数据。隐含详细模式。

`zstreamdump` 别名用于保持兼容，等同于运行 `zstream dump`。

### `zstream raw [-v] [-b max_buffers] [-g fromguid] image | device [file]`

将从指定 `file` 或标准输入读取的 zvol 发送流应用到一个原始镜像或块设备。默认情况下，一次最多可以写入 32 个 `SPA_MAXBLOCKSIZE` 缓冲区。将 `max_buffers` 设为 1 到 `IOV_MAX` 之间的某个值时，连续的写入记录会被合并为一次写入操作，最多使用这么多缓冲区，代价是占用更多内存。

当提供了 `fromguid` 时，会检查流的初始 fromguid，以确保它与给定值匹配。完成后，流的最终 toguid 会打印到标准输出。

使用 `-v` 选项时，会以类似于 `zstream dump` 的方式打印流中各记录的详细信息。

### `zstream recompress [-t num_threads] compress_type [file]`

使用指定的 `compress_type` 重新压缩从指定 `file` 或标准输入读取的发送流，并将修改后的流写入标准输出。发送流中所有 WRITE 记录都会被压缩，除非压缩无法使其大小小于未压缩时的大小。`compress_type` 可以是 `compression` 属性接受的任何值（`on` 除外），包括那些指定了压缩级别的值，如 `gzip-3` 或 `zstd-5`。`compress_type` 为 `off` 会解压每条记录，让流保持未压缩状态。请注意，加密发送流无法重新压缩。

#### `-t num_threads`

指定压缩工作线程的数量。默认情况下，`zstream recompress` 会为每个 CPU 核心创建一个线程。把 `num_threads` 提高到该默认值之上通常没有好处。在某些架构上，当大量线程同时活跃时，对内存缓存等资源的争用会降低效率。在这些系统上，用较少的线程运行可能会有帮助，特别是在共享服务器上自动化执行操作时。

#### `-l level`

此选项已弃用。它此前用于为 `zstd` 指定数值压缩级别。请改用标准的压缩指定符，如 `zstd-5`。

### `zstream redup [-v] file`

过去可以用 `zfs send -D` 选项创建去重发送流。然而，流级去重支持已弃用，并从 `zfs send` 与 `zfs receive` 中移除。

`zstream redup` 从指定的 `file` 读取去重流，并在标准输出上输出一个等价的、非去重的发送流。因此，去重流可以通过运行以下命令来接收：

```sh
# zstream redup file | zfs receive …
```

此处需要一个真正的 `file`，因为解析去重记录涉及重新读取流的较早部分。

#### `-v`

详细模式。打印已反去重记录的摘要。

### `zstream token resume_token`

转储 ZFS 恢复令牌信息。

## 示例

### 从 OpenZFS bug #12762 恢复

首先，确定哪些记录已损坏。这无法自动完成；它需要 ZFS 元数据之外的信息。如果对象 `128` 在偏移 `0` 处损坏，并使用 `lz4` 压缩，则运行此命令：

```sh
# zfs send -c … | zstream decompress 128,0,lz4 | \
zfs recv …
```

### 从 OpenZFS bug #18239 恢复

虚假记录的偏移量通常大得离谱，可以通过运行 `zdb -ddddd 数据集 对象` 或 `zstream dump -v` 来发现。要恢复，请发送该数据集并使用 `zstream` 移除虚假记录，然后将其接收到一个新数据集中。

```sh
# zfs send … | zstream drop_records 3545761,18446744073709486080 | \
zfs recv …
```

### 从 zvol 迁移到物理磁盘

假定有一块容量足够的物理磁盘 `/dev/sdd` 和一个 zvol `tank/vol`，其上有快照 `@1`、`@2` 与 `@3`：

```sh
# zfs send -Lec tank/vol@1 | zstream raw /dev/sdd
16731506615198184313
# zfs send -Lec -I @1 tank/vol@3 | zstream raw -g 16731506615198184313 /dev/sdd
10690368765373298656
```

## 参考文献

zdb(8)、zfs(8)、zfs-receive(8)、zfs-send(8)、[issue #12762](https://github.com/openzfs/zfs/issues/12762)、[issue #18239](https://github.com/openzfs/zfs/issues/18239)

2026 年 9 月 3 日
