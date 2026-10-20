# Scrub 与 resilver

ZFS 为每个块计算校验和，因此它知道数据何时出错，而不是靠猜。Scrub 与 resilver 是两种基于这一认知的后台操作：scrub 校验一切，resilver 重建已知缺失的部分。

## 自愈

每次读取都会验证块的校验和。一旦不匹配，具备冗余的存储池——镜像、raidz、draid 或 `copies>1`——会取回完好的副本，返回给应用程序，并重写损坏的那个。该错误会计入 `zpool status`，尽管数据并未丢失。

没有冗余时，ZFS 仍能检测到损坏并准确报告受影响的文件，但无法修复。这正是使用冗余存储池的全部理由：没有第二份副本的校验和，只能告诉你已经失去了什么。

## Scrub

Scrub 遍历存储池中的全部数据，逐块验证校验和，并在冗余允许时修复损坏。它是发现潜在损坏的方式——比如存放了一年没人读过的介质上的比特衰减——而且是在仍可修复的时候。

```sh
zpool scrub pool
zpool scrub -p pool          # 暂停
zpool scrub -s pool          # 停止
zpool scrub -w pool          # 等完成后再返回
zpool status -v pool
```

暂停的 scrub 在导出与导入之后仍然保持暂停，再次执行 `zpool scrub` 时会从最近的磁盘检查点继续。

有用的变体：

### `-t`（彻底）

还解密并解压每个块，以捕捉校验和匹配但解密或解压失败的罕见损坏。加密数据集需要已加载密钥；密钥不可用的块退回到普通 scrub。

### `-e`（错误 scrub）

只 scrub `zpool status -v` 已报告损坏的文件。存储池必须曾在启用 `head_errlog` 特性的情况下 scrub 过一次。

### `-C`

从上次保存的事务组（存储池属性 `last_scrubbed_txg`）继续，而不是从头开始。

### `-S 日期` / `-E 日期`

只 scrub 在某个日期范围内创建的块，格式为 `"YYYY-MM-DD HH:MM"`。

说明：

* scrub 是 I/O 密集型操作；同一时间只运行一个 scrub 或 resilver，且 resilver 进行时无法开始 scrub。
* scrub 分两个阶段运行——先扫描元数据，把块排序成较大的连续区间，然后才是实际的块读取。
* 在活动存储池上，进度可能超过 100%，因为数据在不断变化；该期间不给出完成估计。
* 普通的校验和验证不需要加密密钥，但没有它们，无法修复的错误无法在 `zpool status -v` 中归属到文件名。

频率怎么定？消费级磁盘以每月一次为常见基线，企业级每季度一次。多数发行版随附相应的 systemd 定时器或 cron 任务——添加自己的之前先检查一下。

## Resilver

Resilver 是同一套机制，但只针对 ZFS 已知过期的数据：在把设备接入镜像、替换故障设备，或在停机后让设备重新上线之后。

```sh
zpool replace pool /dev/old /dev/new
zpool attach pool /dev/existing /dev/new
zpool status pool
zpool resilver pool          # 从头重新开始正在进行的 resilver
```

`zpool resilver` 从头重启 resilver，并接管任何已安排延迟 resilver 的驱动器；这需要 `resilver_defer` 存储池特性。

### 顺序重建

`zpool replace -s` 与 `zpool attach -s` 按顺序重建新设备，而不是走遍块树。这能快得多地恢复冗余，但重建期间不验证校验和——因此它完成后会自动开始一次 scrub。顺序重建不支持 raidz。

## 解读 `zpool status`

各设备的错误计数器含义不同：

### `READ` / `WRITE`

设备自身报告的 I/O 错误。

### `CKSUM`

设备返回的数据与校验和不符——静默损坏。在其他方面健康的磁盘上出现非零 CKSUM，通常指向线缆、控制器或内存，而不是磁盘本身。

`zpool status -v` 列出有无法修复错误的文件。`zpool clear` 在根因处理完毕后重置计数器——它本身不修复任何东西。

文件上的持续性错误意味着数据已经丢失：从备份或快照恢复该文件。参见[故障排除](Troubleshooting.md)。

## 延伸阅读

* [zpool-scrub(8)](../../man/8/zpool-scrub.8.md)、[zpool-resilver(8)](../../man/8/zpool-resilver.8.md)
* [zpool-replace(8)](../../man/8/zpool-replace.8.md)、[zpool-attach(8)](../../man/8/zpool-attach.8.md)、[zpool-status(8)](../../man/8/zpool-status.8.md)
* [校验和](../Data-Storage/Checksums.md)、[VDEV](../Pool-Structure/VDEV.md)、[故障排除](Troubleshooting.md)
