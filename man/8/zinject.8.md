# zinject(8)

## 名称

`zinject` — ZFS 故障注入器

## 概述

```sh
zinject
```

```sh
zinject -b 对象集:对象:级别:起始:结束 [-f 频率] -amu [池名]
```

```sh
zinject -c 标识符 | all
```

```sh
zinject -d vdev -A degrade|fault 池名
```

```sh
zinject -d vdev -D 延迟:通道数 [-T read|write] 池名
```

```sh
zinject -d vdev [-e 设备错误] [-L 标签错误] [-T 失败] [-f 频率] [-F] 池名
```

```sh
zinject -i 秒数 池名
```

```sh
zinject -E 延迟 [-a] [-m] [-f 频率] [-l 级别] [-r 范围] [-T I/O 类型] [-t 类型 | -b 书签]
```

```sh
zinject -I [-s 秒数 | -g 事务组数] 池名
```

```sh
zinject -p 函数 池名
```

```sh
zinject -t data -C dvas [-e 设备错误] [-f 频率] [-l 级别] [-r 范围] [-amq] 路径 | zvol
```

```sh
zinject -t dnode -C dvas [-e 设备错误] [-f 频率] [-l 级别] [-amq] 路径
```

```sh
zinject -t MOS 类型 -C dvas [-e 设备错误] [-f 频率] [-l 级别] [-r 范围] [-amqu] 池名
```

## 说明

`zinject` 通过在 ZFS 存储池中模拟数据损坏或设备故障来制造人为问题。**此程序很危险。**

### `zinject`

列出注入记录。

### `zinject -b objset:object:level:start:end [-f frequency] -amu [pool]`

在书签处向存储池强制注入错误。

### `zinject -c id|all`

取消注入记录。

### `zinject -d vdev -A degrade|fault pool`

强制将某个 vdev 置于 `DEGRADED` 或 `FAULTED` 状态。

### `zinject -d vdev -D latency:lanes [-T read|write] pool`

在特定设备的 I/O 请求上添加人为延迟，使得这些请求至少需要 `latency` 毫秒才能完成。每个延迟都有一个关联的通道数（lanes），它定义了可以并发处理的 I/O 请求数量。

例如，对于单通道、10 ms 的延迟（`-D 10:1`），设备一次只能处理一个 I/O 请求，每个请求需要 10 ms 才能完成。因此，如果每 10 ms 只提交一个请求，平均延迟就是 10 ms；但如果每 10 ms 提交多个请求，平均延迟就会超过 10 ms。

类似地，如果指定的 10 ms 延迟带两个通道（`-D 10:2`），那么设备一次可以处理两个请求，每个请求的最小延迟均为 10 ms。因此，如果每 10 ms 提交两个请求，平均延迟就是 10 ms；但如果每 10 ms 提交的请求超过两个，平均延迟就会超过 10 ms。

还要注意，这些延迟是可叠加的。因此两次调用 `-D 10:1` 大致等同于一次调用 `-D 10:2`。这同时意味着，可以指定多个目标延迟各不相同的通道。例如，先调用 `-D 10:1`，再调用 `-D 25:2`，会在设备上创建 3 个通道：一个延迟为 10 ms 的通道和两个延迟为 25 ms 的通道。

### `zinject -d vdev [-e device_error] [-L label_error] [-T failure] [-f frequency] [-F] pool`

强制使某个 vdev 报错。

### `zinject -i seconds pool`

在今后的存储池导入期间添加人为延迟。此注入器会在导入完成后自动清除。

### `zinject -E delay [-a] [-m] [-f freq] [-l level] [-r range] [-T iotype] [-t type | -b bookmark]`

为给定对象或书签注入流水线就绪阶段（pipeline ready stage）延迟。延迟以毫秒为单位指定。

### `zinject -I [-s seconds | -g txgs] pool`

模拟一次不遵守缓存刷新（cache flush）的硬件故障。

### `zinject -p function pool`

在指定函数内部触发 panic。

### `zinject -t data -C dvas [-e device_error] [-f frequency] [-l level] [-r range] [-amq] path|zvol`

强制向文件或 zvol 的内容中注入错误。对于 zvol，请传入 zvol 块设备的路径。

### `zinject -t dnode -C dvas [-e device_error] [-f frequency] [-l level] [-amq] path`

强制向文件或目录的 metadnode 中注入错误。

### `zinject -t mos_type -C dvas [-e device_error] [-f frequency] [-l level] [-r range] [-amqu] pool`

强制向存储池的 MOS 中注入错误。

## 选项

### `-a`

注入前刷新 ARC。

### `-b objset:object:level:start:end`

在此书签元组处向存储池强制注入错误。每个数字都是十六进制，且只能指定一个块。

### `-C dvas`

只将给定错误注入特定的 DVA。掩码应指定为以逗号分隔、从 0 开始编号的 DVA 列表（如 `0,2`）。此选项不适用于 `decompress` 与 `decrypt` 等逻辑数据错误。

### `-d vdev`

由路径或 GUID 指定的 vdev。

### `-e device_error`

指定：

* `checksum`：对应 ECKSUM 错误，
* `decompress`：对应数据解压错误，
* `decrypt`：对应数据解密错误，
* `corrupt`：在读取后翻转数据中的一位，
* `dtl`：对应 ECHILD 错误，
* `io`：对应 EIO 错误，此时重新打开设备会成功，
* `nxio`：对应 ENXIO 错误，此时重新打开设备会失败，
* `io-prefail`：丢弃该 I/O 而不执行它，并返回失败，
* `noop`：丢弃该 I/O 而不执行它，并返回成功。

对于 EIO 与 ENXIO，“失败的”读或写操作仍然会发生。此注入只是设置 I/O 流水线报告的错误值，使其看起来像是读或写失败了。解密错误目前仅对文件数据有效。

### `-f frequency`

只按一定比例注入错误。以实数百分比表示，取值介于 `0.0001` 与 `100` 之间。

### `-F`

更快失败。执行更少的检查。

### `-f txgs`

在报告失败前运行这么多个事务组。

### `-h`

打印用法信息。

### `-l level`

在特定块级别注入错误。默认值为 `0`。

### `-L label_error`

将标签错误区域设为 `nvlist`、`pad1`、`pad2` 或 `uber` 之一。

### `-m`

自动重新挂载底层文件系统。

### `-q`

安静模式。只打印所添加的处理程序编号。

### `-r range`

在对象的特定逻辑范围上注入错误，以 `start[,end]` 形式指定。接受数字后缀 K、M、G、T、P、E。该范围会根据对象的属性转换为相应的 blkid 范围。

### `-s seconds`

在报告失败前运行这么多秒。

### `-T type`

将错误注入此类型的 I/O。

* `read`、`write`、`flush`、`claim`、`free`：基本 I/O 类型；
* `all`：所有基本 I/O 类型；
* `probe`：设备探测 I/O。

### `-t mos_type`

将其设为：

* `mos`：MOS 中的任何数据，
* `mosdir`：对象目录，
* `config`：存储池配置，
* `bpobj`：块指针列表，
* `spacemap`：空间映射，
* `metaslab`：metaslab，
* `errlog`：持久错误日志。

### `-u`

注入后卸载存储池。

## 环境变量

### `ZFS_HOSTID`

以调试模式运行 `zinject`。

## 参考文献

zfs(8)、zpool(8)

2026 年 4 月 1 日
