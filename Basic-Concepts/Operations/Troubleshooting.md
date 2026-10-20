# 故障排除

存储池出问题时该查什么、如何读懂 ZFS 给出的信息，以及在提交缺陷报告之前需要收集哪些材料。

## 先看这些

```sh
zpool status -v                 # 健康状态，以及受损文件清单
zpool status -x                 # 仅列出有问题的存储池
zpool status -es                # 仅列出不健康的 vdev，并附慢 I/O 计数
zpool events -v                 # 事件历史，信息最详细
dmesg -T | grep -i zfs          # 内核层面的错误
zfs version
```

如果 `zpool status -x` 输出 `all pools are healthy`，下文的大部分情形就可以排除。

## 读懂 `zpool status`

存储池的健康状况只有三种状态：**ONLINE**（一切正常）、**DEGRADED**（有设备故障，但冗余仍在支撑）、**FAULTED**（元数据损坏，或剩余副本已不足以维持运行）。

单个 vdev 会报告更细的状态：

**`ONLINE`**：工作正常。

**`DEGRADED`**：校验和错误、慢 I/O 或 I/O 错误超出可接受水平。ZFS 会继续使用该设备，同时标记它可能有问题。

**`FAULTED`**：设备能打开，但内容与预期不符，或者错误计数高到 ZFS 已停止使用它。

**`OFFLINE`**：通过 `zpool offline` 主动下线。

**`REMOVED`**：运行中被物理拔出。能否检测到取决于硬件。

**`UNAVAIL`**：完全无法打开。若导入时该设备缺失，则显示 GUID 而非路径——那条路径从未有效过。

三列计数器的含义各不相同，区分清楚很重要：

**`READ` / `WRITE`**：设备自身报告的 I/O 错误。

**`CKSUM`**：设备返回的数据未能通过校验和——静默损坏。

ZFS 能重建的受损块，记在持有坏副本的那块磁盘上。它**无法**重建的块——比如 raidz2 中有三块磁盘受损——则无法归因，于是校验和错误会记到持有该块的*每一块*磁盘上。因此一排磁盘同时显示 CKSUM 错误，通常只是一个不可恢复的块，而不是整排磁盘同时故障。

某块磁盘没有 I/O 错误却有非零 CKSUM，更可能指向线缆、HBA 或内存，而不是磁盘本身。

`zpool clear pool` 只是重置计数器，并不修复任何东西——先排除原因，再清除，然后观察计数器是否重新出现。

## 永久性错误

`zpool status -v` 会列出存在不可修复错误的文件。这些数据已经丢失：请从备份或快照中恢复相应文件。如果清单中显示的是十六进制对象号而非路径，说明该文件已被删除，或者数据集未挂载。

这些条目会一直保留，直到一次 scrub 确认错误已经消失，因此恢复之后要运行 scrub。参见 [Scrub 与 resilver](Scrub-and-Resilver.md)。

错误若出现在元数据而非某个文件上，或者显示 `<metadata>` 标记，则更为严重——这正是冗余存在的意义所在；没有冗余，存储池可能无法完全恢复。

## 无法导入的存储池

按下面的阶梯逐级尝试，破坏性最小的排在最前。**下面标出的选项会破坏数据**——使用其中任何一个之前，请先读下一节。

```sh
zpool import                              # 究竟能看到什么
zpool import -d /dev/disk/by-id           # 扫描指定路径
zpool import -o readonly=on -N pool       # 只查看，不做任何改动
zpool import -f pool                      # 上次由另一系统使用
zpool import -m pool                      # 丢失数据：丢弃缺失的日志
zpool import -F -n pool                   # 试运行：能否回退？
zpool import -F pool                      # 丢失数据：丢弃事务
zpool import -FX pool                     # 丢失更多数据：扩展回退
```

不带参数的 `zpool import` 与 `-d` 是安全的——它们只做扫描。`-f` 会绕过“存储池上次由另一系统使用”这一保护；它本身不丢弃任何东西，但如果存储池确实仍在另一台主机上活动，导入会损坏它。

对于你在意的存储池，第一步应当是 `-o readonly=on -N`：它在不挂载、不写入的情况下完成导入，因此可以先看清楚再作决定。

### 每个破坏性选项的实际代价

**`-m`——丢弃意图日志。** 这是数据丢失，而且很容易被忽略，因为这个参数看上去只是图个方便。缺失或损坏的 SLOG 中保存着那些已向应用确认、但尚未写入存储池的同步写入。用 `-m` 导入会把它们扔掉：存储池状态是一致的，但应用被告知已经持久化的事务一去不返。对数据库或 NFS 服务器而言，这是应用层面的静默损坏，而不是 ZFS 层面的——ZFS 会把存储池报告为健康。

在动用 `-m` 之前，先设法让日志设备重新可读。这也正是 SLOG 应当做镜像的理由。

**`-F`——丢弃最近几个事务组。** 把存储池回退到较早的一致状态。该时间点之后写入的一切都将无法挽回，而且并非每个受损的存储池都能借此恢复。务必先运行 `-F -n`：它会报告回退能否成功，而不会真的执行。

**`-X`——扩展回退。** 向更早的时间点搜索，因此可能丢失的内容也相应更多。仅在 `-F` 失败之后使用。

如果存储池有检查点，`zpool import --rewind-to-checkpoint` 是比 `-F` 更干净、定义更明确的撤销手段，因为回到哪个点由你选定。注意，一旦在不带 `readonly` 的情况下完成导入，这一操作同样不可逆。

关于检查点，参见[更改存储池布局](../Pool-Structure/Changing-Pool-Layout.md)。

被**销毁**的存储池不会立刻消失。`zpool import -D` 会列出已销毁的存储池，而带 `-D` 导入可以把它找回来——前提是它的设备没有被重新使用：

```sh
zpool import -D                 # 还有哪些内容可以恢复
zpool import -D pool
```

在不寻常的场合导入——救援环境，或者存储池的挂载点会与正在运行的系统冲突——正是 `-R` 的用途。它会设置 `altroot`，给每个挂载点加上前缀，并设置 `cachefile=none`，使这次导入不被记住：

```sh
zpool import -R /mnt -N pool
```

设备名称在两次启动之间发生变化，是存储池“消失”的常见原因——用 `-d /dev/disk/by-id` 导入，并参见[常见问题解答](../../Project-and-Community/FAQ.md)中关于选择 `/dev/` 名称的内容。

## 挂起的存储池

当到底层设备的连接中断时，存储池会被挂起，由 `failmode` 属性决定后续行为：

**`wait`**：默认值。阻塞所有 I/O，直到连接恢复并用 `zpool clear` 清除错误。

**`continue`**：对新写入返回 `EIO`，但仍从健康设备提供读取。未提交的写入继续保持阻塞。

**`panic`**：打印一条消息并使系统崩溃，生成转储。

`failmode=wait` 的挂起存储池看起来与卡死一模一样：访问它的命令会永久阻塞，且无法终止。在断定 ZFS 死锁之前，先看看另一个存储池的 `zpool status`，以及 `dmesg`。

## 进程挂起与慢 I/O

*症状*：`zfs` 或 `zpool` 命令一直不返回，也无法终止。

*常见原因*：内核线程卡住、存储池挂起，或硬件确实很慢。

ZFS 为此设有 *deadman* 定时器。一次存储池同步耗时超过 `zfs_deadman_synctime_ms`，或单次 I/O 超过 `zfs_deadman_ziotime_ms`，就会被判定为挂起。在默认的 `zfs_deadman_failmode=wait` 下，这只会被*记录*下来——所以证据在日志里，而不在你的终端上。存储池一旦挂起，deadman 会自动停用。

存储变慢但并未挂起时，更容易直接观察到：

```sh
zpool status -s                 # 每个叶子 vdev 的慢 I/O 计数
zpool iostat -l 1               # 延迟分布
zpool iostat -w                 # 延迟直方图
```

`-s` 统计耗时超过 `zio_slow_io_ms`（默认 30 秒）的 I/O。它们未必失败——但某块磁盘不断累积这类 I/O，是硬盘即将损坏的典型征兆；在 RAIDZ 上，它还会拖慢整个组（参见 [RAIDZ](../Pool-Structure/RAIDZ.md)）。

## 日志文件

**内核日志。** `dmesg -T`、`/var/log/syslog`，或 `rsyslogd` 发送内核消息的任何位置。卡住线程的栈回溯会落在这里——有时要等 deadman 定时器超时后才会出现。

**ZFS 调试消息。** 模块维护一个内部日志缓冲区，当模块参数 `zfs_dbgmsg_enable` 为 1 时，可从 `/proc/spl/kstat/zfs/dbgmsg` 读取。这常常正是开发者索要的内容。

**每个存储池的 I/O 统计。** Linux 上位于 `/proc/spl/kstat/zfs/<pool>/`。

**这个存储池上做过什么。** `zpool history` 会回放存储池经历过的管理命令——这些记录保存在存储池自身之中，因此重启后依然存在，并随存储池迁移到另一台主机。这常常是回答“改了什么”最快的方式。

```sh
zpool history pool
zpool history -l pool           # 谁、从哪台主机
zpool history -i pool           # 包含内部记录的事件
```

日志基础设施——elasticsearch、fluentd、influxdb、splunk——能大幅简化这些日志与系统事件的关联分析。

## ZFS 事件

ZFS 通过事件通道报告值得关注的事件。ZFS 事件守护进程（`zed`）负责监听并处理这些事件；它可扩展，因此脚本可以订阅事件并采取行动。通常安装在 `/etc/zfs/zed.d/all-syslog.sh` 的脚本会把格式化后的消息写入 syslog。参见 `zed(8)`。

```sh
zpool events                    # 自模块加载以来的历史，涵盖所有存储池
zpool events -v                 # 每个事件的完整细节
zpool events -f                 # 持续跟踪
```

历史记录保存在内存中，数量受 `zfs_zevent_len_max` 限制。`zed` 内部有限流机制，因此单个设备故障不会耗尽系统资源。

每个事件都带有一个用于过滤事件类型的类：

**`sysevent.fs.zfs.*`**：存储池管理——导入、导出、配置更新、`zpool history` 条目。

**`ereport.*`**：错误。一次故障常常会产生多个 ereport，因为软件的每一层都会报告它：一块故障磁盘可能在读取时抛出一个 `ereport.io`，并在存储池层面产生一个 `ereport.fs.zfs.checksum`。这些事件与 `zpool status` 中的计数器相对应——如果你在那里看到错误，这里就存在对应的 ereport。

**`ereport.fs.zfs.delay`**：慢 I/O，包括 RAIDZ 子 vdev 被置于 *sit out*（暂停参与）状态。

详细事件的具体内容会随版本变化；请把它们当作诊断细节，而不是稳定的接口。

## 报告问题

在提交 issue 之前，先确认这是一个缺陷而不是求助问题——后者应当发到[邮件列表](../../Project-and-Community/MailingLists.md)。然后收集以下内容：

* `zfs version`，以及发行版与内核版本
* `zpool status -v` 与 `zpool get all <pool>`
* `dmesg` 与 `/proc/spl/kstat/zfs/dbgmsg` 中的相关部分
* 故障前后的 `zpool events -v`
* 非默认的模块参数
* 系统是否使用 ECC 内存，以及是否为虚拟化环境
* 可复现步骤（如有）——这比上面任何一项都重要

[常见问题解答](../../Project-and-Community/FAQ.md)中有完整清单和 issue 跟踪器链接。

## 延伸阅读

* [zpool-status(8)](../../man/8/zpool-status.8.md)、[zpool-events(8)](../../man/8/zpool-events.8.md)、[zpool-import(8)](../../man/8/zpool-import.8.md)
* [zpoolconcepts(7)](../../man/7/zpoolconcepts.7.md)——`Device Failure and Recovery`
* [zed(8)](../../man/8/zed.8.md)
* [ZFS 消息](https://openzfs.github.io/openzfs-docs/msg/index.html)——`zpool status` 中出现的 `ZFS-8000-*` 代码
