# 分布式 RAID（dRAID）

>**注意**
>
>本页所述功能是 OpenZFS 2.1.0 版本新增的，OpenZFS 2.0.0 版本并不适用。

## 介绍

[dRAID](https://docs.google.com/presentation/d/1uo0nBfY84HIhEqGWEx-Tbm8fPbJKtIP3ICo4toOPcJo/edit) 是 raidz 的一种变体，提供了集成的分布式热备盘，更快地重建（resilvering），同时保留 raidz 的优势。dRAID vdev 由多个内部 raidz 组构成，每组包含 D 个数据设备和 P 个校验设备。这些组分布在所有子设备上，以充分利用可用的磁盘性能。这被称为校验去聚类（parity declustering），一直是个活跃的研究领域。下图是简化示意，但有助于说明 dRAID 与 raidz 的关键区别。


![](../.gitbook/assets/raidz_draid.png)


此外，dRAID vdev 必须以一种方式重新排列其子 vdev，无论哪块磁盘发生故障，重建 I/O（包括读写）都能在所有存活磁盘之间均匀分布。这通过使用精心选择的预计算排列映射来实现。这样既可以保持存储池创建速度快，又能确保映射不会被损坏或丢失。

dRAID 与 raidz 的另一区别在于它使用固定条带宽度（必要时用零填充）。这使得 dRAID vdev 可以顺序重建（resilver），但固定条带宽度会显著影响可用容量和 IOPS。例如，默认 D=8 且磁盘扇区为 4k 时，最小分配大小为 32k。如果使用压缩，这种相对较大的分配大小可能降低实际压缩比。在使用 ZFS 卷和 dRAID 时，默认 volblocksize 属性会根据分配大小进行增加。如果 dRAID 池将存储大量小块数据，建议增加一个镜像特殊 vdev 来存储这些小块。

关于 IOPS，性能与 raidz 类似，因为任何读取操作都必须访问所有 D 个数据磁盘。可交付的随机 IOPS 可以合理地近似为 `floor((N-S)/(D+P)) * <单盘 IOPS>`。

总之，dRAID 可以提供与 raidz 相同的冗余和性能，同时还提供快速的集成分布式热备盘。

## 创建 dRAID vdev

dRAID vdev 的创建方式与其他 vdev 相同，使用命令 `zpool create` 并列出要使用的磁盘。

```sh
# zpool create <pool> draid[1,2,3] <vdevs...>
```

与 raidz 类似，校验级别紧随 vdev `draid` 类型之后指定。但与 raidz 不同，可以指定额外的冒号分隔选项。其中最重要的是选项 `:<spares>s`，用于控制要创建的分布式热备盘数量。默认情况下不创建热备盘。选项 `:<data>d` 可用于设置每个 RAID 条带中使用的数据设备数量（D+P）。如果未指定，将选择合理的默认值。

```sh
# zpool create <pool> draid[<parity>][:<data>d][:<children>c][:<spares>s] <vdevs...>
```

* **parity** - 校验级别（1-3），默认为 `1`。
* **data** - 每个冗余组中的数据设备数量。通常，较小的 D 值会提高 IOPS、改善压缩比并加快重建速度，但会减少总可用容量。默认值为 8，除非 `N-P-S` 小于 8。
* **children** - 预期的子设备数量。在列出大量设备时作为交叉检查使用。如果提供的子设备数量不符，会返回错误。
* **spares** - 分布式热备盘数量。默认值为 `0`。

例如，要创建一个 11 磁盘的 dRAID 池，具有 4+1 冗余和一个分布式热备盘，可使用以下命令：

```sh
# zpool create tank draid:4d:1s:11c /dev/sd[a-k]
# zpool status tank

  pool: tank
 state: ONLINE
config:

        NAME                  STATE     READ WRITE CKSUM
        tank                  ONLINE       0     0     0
          draid1:4d:11c:1s-0  ONLINE       0     0     0
            sda               ONLINE       0     0     0
            sdb               ONLINE       0     0     0
            sdc               ONLINE       0     0     0
            sdd               ONLINE       0     0     0
            sde               ONLINE       0     0     0
            sdf               ONLINE       0     0     0
            sdg               ONLINE       0     0     0
            sdh               ONLINE       0     0     0
            sdi               ONLINE       0     0     0
            sdj               ONLINE       0     0     0
            sdk               ONLINE       0     0     0
        spares
          draid1-0-0          AVAIL
```

>**注意**
>
>dRAID vdev 名称 `draid1:4d:11c:1s` 完全表达了配置，并列出了所有属于 dRAID 的磁盘。此外，逻辑分布式热备盘显示为可用的备用磁盘。


## 重建到分布式热备盘

dRAID 的一个主要优势是它同时支持顺序和传统重建（resilver）。在向分布式热备盘进行顺序重建时，性能按磁盘数量除以条带宽度（D+P）进行扩展。这可以大幅缩短重建时间，在通常时间的一小部分内恢复完整冗余。例如，下图显示了一个由 90 块机械硬盘构成、填充至 90% 容量的 dRAID 的实际顺序重建时间（以小时计）。


![](../.gitbook/assets/draid-resilver-hours.png)

**dRAID 顺序重建器 —— 替换一块 16TB 磁盘所需小时数 90 块 HDD，单个分布式热备盘，池容量 100%**


在使用 dRAID 和分布式热备盘时，处理故障磁盘的过程几乎与带有传统热备盘的 raidz 相同。当检测到磁盘故障时，如果有可用的热备盘，ZFS 事件守护进程（ZED）会启动重建。唯一的区别是，对于 dRAID 会启动顺序重建（sequential resilver），而 raidz 必须使用修复重建（healing resilver）。

```sh
# echo offline >/sys/block/sdg/device/state
# zpool replace -s tank sdg draid1-0-0
# zpool status

  pool: tank
 state: DEGRADED
status: One or more devices is currently being resilvered.  The pool will
        continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver (draid1:4d:11c:1s-0) in progress since Tue Nov 24 14:34:25 2020
        3.51T scanned at 13.4G/s, 1.59T issued 6.07G/s, 6.13T total
        326G resilvered, 57.17% done, 00:03:21 to go
config:

        NAME                  STATE     READ WRITE CKSUM
        tank                  DEGRADED     0     0     0
          draid1:4d:11c:1s-0  DEGRADED     0     0     0
            sda               ONLINE       0     0     0  (resilvering)
            sdb               ONLINE       0     0     0  (resilvering)
            sdc               ONLINE       0     0     0  (resilvering)
            sdd               ONLINE       0     0     0  (resilvering)
            sde               ONLINE       0     0     0  (resilvering)
            sdf               ONLINE       0     0     0  (resilvering)
            spare-6           DEGRADED     0     0     0
              sdg             UNAVAIL      0     0     0
              draid1-0-0      ONLINE       0     0     0  (resilvering)
            sdh               ONLINE       0     0     0  (resilvering)
            sdi               ONLINE       0     0     0  (resilvering)
            sdj               ONLINE       0     0     0  (resilvering)
            sdk               ONLINE       0     0     0  (resilvering)
        spares
          draid1-0-0          INUSE     currently in use
```

虽然两种类型的 resilvering 达到相同的目标，但值得花一点时间总结它们的主要区别。

* 传统的 healing resilver 会扫描整个块树。这意味着在修复过程中每个块的校验和都是可用的，并且可以立即验证。缺点是这会产生随机读取工作负载，这对性能不利。
* 顺序 resilver 则扫描空间映射，以确定哪些空间已分配、哪些必须修复。此重建过程不受块边界限制，可以顺序读取磁盘并使用较大的 I/O 进行修复。为了换取这种性能提升，块校验和在 resilvering 过程中无法验证。因此，在顺序 resilver 完成后会启动一次 scrub 来验证校验和。

关于顺序与 healing resilvering 之间差异的更深入解释，请查看在 OpenZFS Developer Summit 上展示的这些[顺序 resilver](https://docs.google.com/presentation/d/1vLsgQ1MaHlifw40C9R2sPsSiHiQpxglxMbK2SMthu0Q/edit#slide=id.g995720a6cf_1_39)幻灯片。

## 重新平衡

通过简单地用新驱动器替换任何故障驱动器，可以再次提供分布式备用空间。此过程称为重新平衡，本质上就是一次 resilver。在执行重新平衡时，推荐使用 healing resilver，因为此时池不再处于降级状态。这可确保在重建到新磁盘时验证所有校验和，并消除了随后对池进行 scrub 的必要。


```sh
# zpool replace tank sdg sdl
# zpool status

  pool: tank
 state: DEGRADED
status: One or more devices is currently being resilvered.  The pool will
        continue to function, possibly in a degraded state.
action: Wait for the resilver to complete.
  scan: resilver in progress since Tue Nov 24 14:45:16 2020
        6.13T scanned at 7.82G/s, 6.10T issued at 7.78G/s, 6.13T total
        565G resilvered, 99.44% done, 00:00:04 to go
config:

        NAME                  STATE     READ WRITE CKSUM
        tank                  DEGRADED     0     0     0
          draid1:4d:11c:1s-0  DEGRADED     0     0     0
            sda               ONLINE       0     0     0  (resilvering)
            sdb               ONLINE       0     0     0  (resilvering)
            sdc               ONLINE       0     0     0  (resilvering)
            sdd               ONLINE       0     0     0  (resilvering)
            sde               ONLINE       0     0     0  (resilvering)
            sdf               ONLINE       0     0     0  (resilvering)
            spare-6           DEGRADED     0     0     0
              replacing-0     DEGRADED     0     0     0
                sdg           UNAVAIL      0     0     0
                sdl           ONLINE       0     0     0  (resilvering)
              draid1-0-0      ONLINE       0     0     0  (resilvering)
            sdh               ONLINE       0     0     0  (resilvering)
            sdi               ONLINE       0     0     0  (resilvering)
            sdj               ONLINE       0     0     0  (resilvering)
            sdk               ONLINE       0     0     0  (resilvering)
        spares
       draid1-0-0          INUSE     currently in use
```

在 resilvering 完成后，分布式热备用再次可用，存储池已恢复到正常健康状态。
