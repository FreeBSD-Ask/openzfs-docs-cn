# 故障排除

>**注意**
>
>此页目前是草稿状态。

## 关于日志文件

日志文件对于故障排查非常有用。在某些情况下，有趣的信息可能分布在多个日志文件中，并与系统事件相关联。

>**专业提示**
>
>像 *elasticsearch*、*fluentd*、*influxdb* 或 *splunk* 这种日志基础设施工具能够简化日志分析和事件关联。

### 通用内核日志

通常，可以通过 `dmesg -T`、`/var/log/syslog` 或内核日志消息发送的目标获取（例如由 `rsyslogd` 发送）Linux 内核日志消息。

### ZFS 内核模块调试信息

ZFS 内核模块使用内部日志缓冲区记录详细的日志信息。对于启用了 ZFS 模块参数 [zfs_dbgmsg_enable = 1](https://github.com/zfsonlinux/zfs/wiki/ZFS-on-Linux-Module-Parameters#zfs_dbgmsg_enable) 的 ZFS 构建，可以在伪文件 `/proc/spl/kstat/zfs/dbgmsg` 中获取该日志信息。

## 无法终止的进程

症状：`zfs` 或 `zpool` 命令似乎挂起，不返回，并且无法终止。

可能原因：内核线程挂起或内核 panic。

关注日志文件：[通用内核日志](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/Troubleshooting.html#generic-kernel-log)、[ZFS 内核模块调试信息](https://openzfs.github.io/openzfs-docs/Basic%20Concepts/Troubleshooting.html#zfs-kernel-module-debug-messages)

>**重要信息**
>
>如果内核线程卡住，则卡住线程的回溯可能记录在日志中。在某些情况下，在挂起检测计时器触发之前不会记录线程。另请参见 [调试可调参数](https://github.com/zfsonlinux/zfs/wiki/ZFS-on-Linux-Module-Parameters#debug)。

## ZFS 事件

ZFS 使用基于事件的消息接口，将重要事件传递给系统上运行的其他消费者。ZFS 事件守护进程（zed）是一个用户态守护进程，用于监听这些事件并进行处理。zed 可扩展，因此你可以编写 shell 脚本或其他程序订阅事件并采取相应操作。例如，通常安装在 `/etc/zfs/zed.d/all-syslog.sh` 的脚本会将格式化的事件消息写入 `syslog`。更多信息请参见 `zed(8)` 手册页。

事件历史也可以通过 `zpool events` 命令查看。此历史记录从 ZFS 内核模块加载开始，包括来自任意池的事件。这些事件存储在 RAM 中，并且数量受内核可调参数 [zfs_event_len_max](https://github.com/zfsonlinux/zfs/wiki/ZFS-on-Linux-Module-Parameters#zfs_zevent_len_max) 限制。`zed` 内部具有限流机制，以防止处理 ZFS 事件时过度消耗系统资源。

使用 `zpool events -v` 可以观察到更详细的事件信息。详细事件的内容可能随事件类型及事件发生时可用信息而变化。

每个事件都有一个用于过滤事件类型的类标识符。常见事件通常与池管理相关，类为 `sysevent.fs.zfs.*`，包括导入、导出、配置更新以及更新 `zpool history`。

与错误相关的事件报告为类 `ereport.*`，对于故障排查非常有价值。一些故障可能在软件的不同层次处理时产生多个 ereport。例如，对于没有奇偶校验保护的简单池，读取损坏磁盘时可能产生一个 `ereport.io`，从而在池级别生成一个 `ereport.fs.zfs.checksum`。这些事件也会反映在 `zpool status` 中的错误计数器中。如果在 `zpool status` 中看到校验和或读写错误，则在 `zpool events` 输出中应该有一个或多个对应的 ereport。
