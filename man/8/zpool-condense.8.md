# zpool-condense(8)

## 名称

`zpool-condense` — 压缩、刷新、垃圾回收或以其他方式清理池元数据

## 概述

```sh
zpool condense [-t 类型] [-c | w] -a | 池名…
```

```sh
zpool condense --types
```

## 说明

许多池内部元数据更新都会在后台执行，其速率经过特意选择，以限制对池正常使用的性能影响。有时最好能加速这些操作，即便这会影响整体性能。`condense` 允许管理员请求将某个特定的后台操作提升优先级，使其尽快完成。

### `-t`、`-type`

要压缩的内容。未指定时将压缩所有类型。以下是 `type` 的可能取值：

#### `log_spacemap`

将 log spacemap（日志空间映射）条目刷新到底层的 metaslab。

### `-a`、`-all`

对所有池开始、取消或等待压缩。

### `-c`、`-cancel`

取消先前的 `condense`。这将使后台更新恢复到正常速率。

### `-w`、`-wait`

等待压缩完成后再返回。

### `--types`

列出此 `condense` 构建所支持的压缩类型。

## 示例

### 示例 1

log_spacemap 压缩进行中的池状态：

```sh
# zpool condense -t log_spacemap
# zpool status
  pool: tank
  state: ONLINE
  condense: log_spacemap: condensing, 104/321 metaslabs done in 00:00:15
  ...
```

## 参考文献

zpool-status(8)、zpool-wait(8)

2026 年 5 月 26 日
