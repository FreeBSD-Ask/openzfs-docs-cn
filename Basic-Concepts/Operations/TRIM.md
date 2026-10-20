# TRIM

TRIM（`BLKDISCARD`、ATA TRIM、SCSI UNMAP）告诉设备存储池已不再使用哪些块，从而让 SSD 回收它们以做磨损均衡，让精简供给的后端存储释放空间。没有它，SSD 最终会认为自己写过的每个块都仍在使用，写入性能随之下降。

ZFS 提供两种模式：自动的后台模式与按需模式。二者相互独立——无论 `autotrim` 如何设置，都可以运行手动 TRIM。

## 自动 TRIM

```sh
zpool set autotrim=on pool
```

默认值为 `off`。启用后，最近释放的空间会被定期 TRIM。ZFS 刻意延后这一过程，让小区间聚合成更少、更大的请求，而设备处理大请求的效果要好得多。

需要注意的是：持续 TRIM 会给底层设备带来可观压力，而不同型号吸收这种压力的能力差异极大。在低端硬件上，定期手动 TRIM 通常能以小得多的干扰获得大部分收益。

L2ARC 设备上的 TRIM 是独立的——通过把 `l2arc_trim_ahead` 模块参数设为大于 0 来启用。

## 按需 TRIM

```sh
zpool trim pool
zpool trim -r 100M pool          # 限速，字节/秒/叶子 vdev
zpool trim -w pool               # 等待完成
zpool trim -s pool               # 暂停
zpool trim pool                  # ……并恢复（不带参数）
zpool trim -c pool               # 取消
zpool trim -a                    # 所有存储池
```

不带 `-r` 时，TRIM 会以设备允许的最快速度运行；在繁忙的存储池上值得加以限制。进度会按设备显示在 `zpool status -t` 中。

`zpool trim -d`（`--secure`）请求*安全* TRIM：设备保证被 TRIM 的块上的数据已被擦除。并非所有 SSD 都支持。这是在加密密钥泄露后清理空闲空间时所提到的选项——参见[原生加密](../Data-Storage/Encryption.md)。

## 使用 systemd 定期 TRIM

OpenZFS 随附按存储池划分的每周与每月定时器单元：

```sh
systemctl enable zfs-trim-weekly@rpool.timer --now
systemctl enable zfs-trim-monthly@tank.timer --now
```

## 哪些设备可以进行 TRIM

支持 `BLKDISCARD` 的块设备——SSD、精简供给的 LUN——以及位于支持打洞（hole punching）的文件系统上的文件 vdev。对机械硬盘执行 TRIM 没有任何作用。

如果 `zpool trim` 报告设备不支持 TRIM，请检查存储链路：某些 HBA 与 USB 桥接器不会透传该命令。参见[硬件](../../Performance-Tuning/Hardware.md)中关于 ATA TRIM 的讨论。

## 延伸阅读

* [zpool-trim(8)](../../man/8/zpool-trim.8.md)
* [zpoolprops(7)](../../man/7/zpoolprops.7.md)——`autotrim`
* [zpool-initialize(8)](../../man/8/zpool-initialize.8.md)——与之对应的“写入一切”操作
* [硬件](../../Performance-Tuning/Hardware.md)
