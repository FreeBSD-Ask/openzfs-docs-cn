# 共享数据集

ZFS 可以从数据集属性驱动 NFS 与 SMB 导出，因此共享跟随数据集，而不必存放在一份需要与之保持同步的独立配置文件里。块级导出（iSCSI）则不同——它使用 zvol 与外置目标框架。

## 它只是一个包装层

**ZFS 不实现 NFS 或 SMB。** `sharenfs` 与 `sharesmb` 属性为平台的标准服务器生成配置，然后通知它重新加载：

| 平台           | ZFS 写入                     | ZFS 随后运行                   |
| :------------- | :--------------------------- | :----------------------------- |
| Linux（NFS）   | `/etc/exports.d/zfs.exports` | `/usr/sbin/exportfs`           |
| FreeBSD（NFS） | `/etc/zfs/exports`           | 向 `mountd` 发信号             |
| Linux（SMB）   | 一个 Samba 用户共享          | `net usershare add` / `delete` |

其余的一切——认证、Kerberos、ACL 语义、性能、调优——都是服务器的工作，并以服务器的方式配置。便利性真实存在，后果同样真实：

**服务器必须已经安装并配置好。** ZFS 会检查 `exportfs` 是否存在，若不存在则静默地什么都不做。在一台没有 nfs-utils 的主机上设置 `sharenfs` 看似成功，实则什么也没导出。同理，`sharesmb` 需要先让 Samba 在 `127.0.0.1` 上监听并启用用户共享（`usershare max shares`、`usershare owner only`）才能真正工作。

**现在有两份配置文件描述你的导出。** ZFS 掌管 `/etc/exports.d/zfs.exports`；你手写的内容仍在 `/etc/exports` 里。两者都处于活动状态。当某个共享行为异常时，两份都要看，并用 `exportfs -v` 查看内核实际持有的内容。

**选项集合是一个许可名单，而非透传。** 尽管外表相似，`sharenfs` 并不接受任意的 `exports(5)` 选项。在 Linux 上，受认可的键为 `sec`、`ro`、`rw`，外加：`all_squash`、`anongid`、`anonuid`、`async`、`auth_nlm`、`crossmnt`、`fsid`、`fsuid`、`hide`、`insecure`、`insecure_locks`、`mountpoint`、`mp`、`no_acl`、`no_all_squash`、`no_auth_nlm`、`no_root_squash`、`no_subtree_check`、`no_wdelay`、`nohide`、`refer`、`replicas`、`root_squash`、`secure`、`secure_locks`、`subtree_check`、`sync`、`wdelay`。其余任何键都会作为语法错误被拒绝。

**当功能不够用时，把它关掉。** 若需要针对单个共享的 Samba 调优、超出 `sec=` 的 Kerberos，或该名单之外的导出选项，请将属性设为 `off` 并以原生方式管理导出。对同一数据集混用两种方式，正是那些“重启后又出现”或“怎么都删不掉”的共享的成因。

## NFS

```sh
zfs set sharenfs=on pool/export
zfs set sharenfs=rw=@192.168.1.0/24,no_root_squash pool/export
zfs set sharenfs=off pool/export
```

`sharenfs=on` 以默认选项 `sec=sys,rw,crossmnt,no_subtree_check` 共享。任何其他取值都是一个选项列表，先按上面的许可名单校验，再被翻译成一条 `/etc/exports` 风格的条目。

注意语法：选项**以逗号分隔**，这与 [exports(5)](https://man7.org/linux/man-pages/man5/exports.5.html) 不同。这样就不必处理引号问题，也便于由脚本生成该属性。在 FreeBSD 上可以给出多组选项，彼此以分号分隔，每组应用于不同的主机或网络。

当 `sharenfs=off` 时，数据集完全不由 ZFS 管理——请通过 `/etc/exports` 与 `exportfs` 以传统方式导出。

由于每个数据集都是独立的文件系统，客户端挂载父数据集不会自动看到子数据集，除非 `crossmnt` 生效（在 `sharenfs=on` 时它确实生效）。

## SMB

```sh
zfs set sharesmb=on pool/export
```

在 Linux 上这使用 **Samba 用户共享**：ZFS 调用 `net(8)` 来创建一个 USERSHARE（用户共享）。必须先配置 Samba 允许用户共享，这项功能才能生效。

需要了解：

* 共享名取自数据集名称，其中在资源名里非法的字符会被替换为下划线。
* 共享以 ACL `Everyone:F` 创建，且不开放访客访问——Samba 必须能认证一个真实用户。一切更细粒度的访问控制都必须在文件系统本身上完成。
* Linux 不支持 Solaris 上可用的那些额外 `sharesmb` 选项。

另见[工作负载调优](../../Performance-Tuning/WorkloadTuning.md)中的 Samba 小节。

## 应用共享

数据集会在开机与关机时，以及属性发生变化时，自动共享与取消共享：

```sh
zfs share -a                 # 共享一切（开机过程的一部分）
zfs share pool/export
zfs unshare pool/export
zfs unshare -a
```

`zfs share -l` 会在挂载加密文件系统时为其加载密钥；当 `keylocation=prompt` 时，它会阻塞在终端上。

## iSCSI 与其他块级导出

OpenZFS 中没有 `shareiscsi` 属性。请改为导出一个 zvol，并把一个 iSCSI 目标框架（LIO/`targetcli`、SCST，或 FreeBSD 上的 `ctld`）指向由此产生的设备：

```sh
zfs create -V 100G pool/iscsi/lun0
ls -l /dev/zvol/pool/iscsi/lun0
```

`volmode` 属性控制一个 zvol 在操作系统中的呈现方式：

### `full`（别名 `geom`）

完整的块设备，分区也包括在内。

### `dev`

分区被隐藏的块设备——通常是 LUN 或虚拟机磁盘所需的形式，因为主机不应去扫描客户机的分区表。

### `none`

完全不向 ZFS 之外暴露。仍然可以快照、克隆与复制——适合作为备份目标。

### `default`

遵循系统级的 `zvol_volmode` 可调参数。

请在创建时设定 `volblocksize` 以匹配使用方的 I/O 大小；参见[工作负载调优](../../Performance-Tuning/WorkloadTuning.md)。

## 延伸阅读

* [zfsprops(7)](../../man/7/zfsprops.7.md)——`sharenfs`、`sharesmb`、`volmode`、`volsize`
* [zfs-share(8)](../../man/8/zfs-share.8.md)——同时记载了 `zfs share` 与 `zfs unshare`
* [数据集与属性](../Datasets/Datasets-and-Properties.md)
