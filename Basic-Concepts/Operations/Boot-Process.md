# 启动时的存储池

默认情况下，ZFS 存储池的任何信息都不写在 `/etc/fstab` 里。存储池由 ZFS 自身发现、导入、挂载与共享，这很方便——直到某个东西没能起来，而你找不到一行 fstab 可以查看。本页讲的是从加电到数据集挂载完成之间发生了什么。

## 事件顺序

1. **导入存储池。** 或从缓存文件，或通过扫描设备。
2. **挂载数据集**，按挂载点顺序，由 `zfs mount -a` 或生成的 systemd 挂载单元完成。
3. **发布共享**，由 `zfs share -a` 完成——见[共享数据集](Sharing.md)。
4. **zvol 出现**在 `/dev/zvol` 之下；任何等待它们的东西都必须等到这一步。
5. **zed 启动**，此之后的事件才会被处理。

以 ZFS 为根文件系统的系统会更早、并以不同方式执行第 1 步：根存储池在真正的根被挂载之前，由 initramfs（Linux）或 loader（FreeBSD）导入。[以 ZFS 为根文件系统指南](../../GettingStarted.md)涵盖了这种情况。

## 缓存文件

`/etc/zfs/zpool.cache` 记录哪些存储池曾被导入，使系统无需扫描每个块设备就能把它们找回来。**其中列出的每个存储池都会在启动时自动导入。**

存储池属性 `cachefile` 控制这一行为：

* 默认值（空字符串）使用标准位置；
* `none` 表示该池从不缓存——它*不会*自动回来，这正是可移动介质、集群与故障切换场景下你想要的；
* 显式路径则把它缓存到别处，之后用 `zpool import -c <路径>` 导入。

```sh
zpool get cachefile pool
zpool set cachefile=none pool          # 启动时不再导入它
zpool set cachefile= pool              # 恢复为默认值
```

该文件是二进制 nvlist；不带参数的 `zdb` 会打印其内容。如果它已过时或缺失，仍可通过扫描找到存储池（`zpool import -d`），`zfs-import-scan` 走的就是这条路径。

两种常见的意外：你曾导入过一次的存储池在重启后不断回来，因为它在缓存中；而用 `-R` 导入的存储池（会设置 `cachefile=none`）按设计*不会*回来。见[故障排除](Troubleshooting.md)。

## hostid 与在错误的机器上导入

存储池记录导入它的系统的 `hostid`。如果另一系统看到某个存储池仍被其他主机导入，它会拒绝导入——即 “pool was last accessed by another system” 消息，`-f` 可以覆盖它。

该保护是提示性的。它比较的是记录下来的 id，并不检查另一台主机是否仍在写入。强行导入一个确实在别处活动的存储池会损坏它。

在 Linux 上，该 id 来自 `/etc/hostid`；若缺失，用 `zgenhostid` 生成一个。hostid 缺失或重复，是主机名更改后存储池拒绝导入、或在集群中无法自我保护的一类典型原因。

对于两台主机确实能访问同一批设备的共享存储，存储池属性 `multihost` 把提示性检查变成主动检查：各主机周期性写入心跳，只要存储池看起来仍然存活，导入就会被拒绝——*即使*加了 `-f`。要使其生效，每台主机必须拥有唯一的 hostid。

```sh
zgenhostid                       # 若 /etc/hostid 缺失
zpool set multihost=on pool
```

注意 `multihost` *不*做什么：它在导入时保护存储池，而不是保护单块设备不被两个不同的存储池占用。

## systemd

在 Linux 上，这一序列由一组单元构成，知道它们的名字就解决了大半问题：

* `zfs-import-cache.service`——导入 `zpool.cache` 中列出的存储池。
* `zfs-import-scan.service`——改为通过扫描设备导入。通常它与缓存服务是二选一的关系，而不是配套使用。
* `zfs-import.target`——导入完成后到达；需要存储池的服务排在它之后。
* `zfs-mount.service`——运行 `zfs mount -a`。
* `zfs-share.service`——运行 `zfs share -a`。
* `zfs-volume-wait.service` / `zfs-volumes.target`——等待 zvol 设备节点出现。
* `zfs-zed.service`——事件守护进程。
* `zfs.target`——聚合目标；在启动时启用或禁用 ZFS 就改这里。

```sh
systemctl list-units 'zfs*'
systemctl status zfs-import-cache.service
journalctl -u zfs-import-cache.service -b
```

还有周期性维护定时器——`zfs-scrub-weekly@<存储池>.timer`、`zfs-scrub-monthly@<存储池>.timer` 以及对应的 `zfs-trim-*`。见 [Scrub 与 resilver](Scrub-and-Resilver.md) 与 [TRIM](TRIM.md)。

### `zfs-mount-generator`

在启动后期用一个 `zfs mount -a` 挂载所有内容，意味着 systemd 对各个挂载点一无所知，因此需要某个特定数据集的服务无法针对它排序。

`zfs-mount-generator` 通过在生成器阶段依据一份缓存的数据集属性列表，为每个数据集生成原生 `.mount` 单元来解决这个问题。`mountpoint=legacy` 或 `none` 的数据集会被跳过，`canmount=off` 的同样如此。

当某个服务在其数据挂载之前就启动时，这就是该用的手段。它还让加密数据集的密钥可以通过常规的 systemd 凭据机制请求，而不必阻塞一个 shell——见[原生加密](../Data-Storage/Encryption.md)。

## FreeBSD

缓存文件位于 `/boot/zfs/zpool.cache`。存储池由 `zfs` rc 脚本导入，在 `/etc/rc.conf` 中用 `zfs_enable="YES"` 启用；loader 在内核启动之前导入根存储池。概念——缓存文件、hostid、先挂载再共享——是一样的。

## 延伸阅读

* [zpoolprops(7)](../../man/7/zpoolprops.7.md)——`cachefile`、`multihost`
* [zfs-mount-generator(8)](../../man/8/zfs-mount-generator.8.md)、[zgenhostid(8)](../../man/8/zgenhostid.8.md)
* [zpool-import(8)](../../man/8/zpool-import.8.md)
* [故障排除](Troubleshooting.md)、[以 ZFS 为根文件系统指南](../../GettingStarted.md)
