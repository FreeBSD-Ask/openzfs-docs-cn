# zed(8)

## 名称

`zed` — ZFS 事件守护进程

## 概述

```sh
zed [-fFhILMvVZ] [-d zedlet 目录] [-p pid 文件] [-P 路径] [-s 状态文件] [-j 任务数] [-b 缓冲区长度]
```

## 说明

`zed`（ZFS Event Daemon，ZFS 事件守护进程）监视由 ZFS 内核模块生成的事件。当提交一个 zevent（ZFS 事件）时，`zed` 会运行所有已针对相应 zevent 类启用的 ZEDLET（ZFS Event Daemon Linkage for Executable Tasks，可执行任务的 ZFS 事件守护进程链接）。

## 选项

### `-h`

显示命令行选项摘要。

### `-L`

显示许可证信息。

### `-V`

显示版本信息。

### `-v`

详细模式。

### `-f`

尽可能强制守护进程运行，禁用安全检查，并不顾一切风险。不建议在生产环境中使用。

### `-F`

不转入后台（daemonize）：保持附着在控制终端上，并记录到标准 I/O 流。

### `-M`

锁定虚拟内存地址空间中当前与未来的所有页。当系统承受较大内存压力时，这有助于守护进程保持响应能力。

### `-I`

请求守护进程在内核模块未加载时保持空闲，而不是退出。内核模块（重新）加载后，事件处理会开始或恢复。在 Linux 上，守护进程运行期间无法卸载内核模块。

### `-Z`

将守护进程的状态清零，从而让仍留在内核中的 zevent 得以重新处理。

### `-d zedletdir`

从指定目录读取已启用的 ZEDLET。

### `-p pidfile`

将守护进程的进程 ID 写入指定文件。

### `-P path`

供 zedlet 使用的自定义 `$PATH`。通常 zedlet 运行在受限环境中，其中包含指向 ZFS 命令的硬编码路径（`$ZFS`、`$ZPOOL`、`$ZED` 等）以及硬编码的 `$PATH`。这样做是出于安全考虑。不过，ZFS 测试套件为其 ZFS 命令使用自定义 PATH，并通过 `-P` 将其传给 `zed`。简而言之，`-P` 只应由 ZFS 测试套件使用；绝不要在生产环境中使用它！

### `-s statefile`

将守护进程的状态写入指定文件。

### `-j jobs`

最多允许 `jobs` 个 ZEDLET 并发运行，新 ZEDLET 的执行会推迟到它们完成之后。（默认值: `16`）

### `-b buflen`

将内核事件缓冲区的增长上限限制为 `buflen` 个条目。当守护进程漏掉一个事件时，该缓冲区会增长，但会导致内核中无法回收的内存占用。值为 `0` 时移除该上限。（默认值: `1048576`）

## zevents

zevent 由一组 nvpair（名称/值对）构成。每个 zevent 都包含一个 EID（Event IDentifier，事件标识符），它在该 ZFS 内核模块加载期间唯一标识该事件；EID 是一个单调递增的整数，每次加载内核模块时都会重置为 1。每个 zevent 还包含一个类字符串，用于标识事件的类型。为简明起见，另定义了子类字符串，它省略了类字符串的前导部分。此外还有若干 nvpair 用于提供事件详情。

内核维护一份最近 zevent 的列表，可以使用 `zpool events -v` 命令查看（连同其关联的 nvpair 列表）。

## 配置

用于响应 zevent 而调用的 ZEDLET 位于 `enabled-zedlets` 目录（`zedletdir`）中。可以从 `installed-zedlets` 目录创建指向它们的符号链接，也可以将其复制过来；符号链接能随已安装的 ZEDLET 自动更新，而副本则保留本地修改。作为一种安全措施，由于更改所有者属于特权操作，ZEDLET 必须归 root 所有。它们必须对用户具有执行权限，但不得对组或其他用户具有写权限。以点开头的文件会被忽略。

ZEDLET 以其应响应调用的 zevent 类命名。具体来说，如果某个 zevent 的类字符串或子类字符串是 ZEDLET 文件名的前缀（且其后跟一个非字母字符），该 ZEDLET 就会针对此 zevent 被调用。作为特例，前缀 `all` 匹配所有 zevent。一个 zevent 可以调用多个 ZEDLET。

## ZEDLET

ZEDLET 是由 `zed` 针对给定 zevent 调用的可执行文件。编写时应假定它们可能被并发调用，并且应使用适当的锁来访问任何共享资源。唯一的例外是“同步 zedlet”，本页后文会加以说明。ZEDLET 使用的公共变量可以存放在默认 rc 文件中，该文件由脚本 source 载入；这些变量应以 `ZED_` 为前缀。

zevent 的 nvpair 会以环境变量的形式传给 ZEDLET。每个 nvpair 名称按以下方式转换为环境变量：

1. 加上 `ZEVENT_` 前缀；
2. 转换为大写；
3. 每个非字母数字字符都转换为下划线。

另有一些环境变量用于以更方便的形式呈现某些 nvpair 值。以下是一份不完整的 zevent 环境变量列表：

### `ZEVENT_EID`

事件标识符。

### `ZEVENT_CLASS`

zevent 类字符串。

### `ZEVENT_SUBCLASS`

zevent 子类字符串。

### `ZEVENT_TIME`

提交该 zevent 的时间，形式为自纪元以来的“秒 纳秒”。

### `ZEVENT_TIME_SECS`

`ZEVENT_TIME` 的秒分量。

### `ZEVENT_TIME_NSECS`

`ZEVENT_TIME` 的纳秒分量。

### `ZEVENT_TIME_STRING`

`ZEVENT_TIME` 的近似符合 RFC3339 的字符串。

此外还定义了以下 ZED 与 ZFS 变量：

### `ZED_PID`

守护进程的进程 ID。

### `ZED_ZEDLET_DIR`

守护进程当前的 `enabled-zedlets` 目录。

### `ZFS_ALIAS`

守护进程所属 ZFS 发行版的别名（`名称-版本-发布号`）字符串。

### `ZFS_VERSION`

守护进程所属的 ZFS 版本。

### `ZFS_RELEASE`

守护进程所属的 ZFS 发布号。

ZEDLET 可能需要调用其他 ZFS 命令。以下可执行文件的安装路径被定义为环境变量：`ZDB`、`ZED`、`ZFS`、`ZINJECT` 与 `ZPOOL`。这些变量可以在 rc 文件中覆盖。

## 同步 ZEDLET

`zed` 的正常行为是并行启动 zedlet，并忽略它们的完成顺序。这意味着 `zed` 可能在事件 ID 编号为 1 的 zedlet 尚未完成时，就已开始运行事件 ID 编号为 2 的 zedlet。大多数情况下这没有问题，而且在系统被数百个事件淹没时反而有帮助。

不过，有时你希望 zedlet 按事件 ID 顺序执行。同步 zedlet 正是为此而设。

在运行同步 zedlet 之前，`zed` 会等待此前启动的所有 zedlet 完成。同步 zedlet 保证是唯一正在运行的 zedlet。其他任何 zedlet 都不会与同步 zedlet 并行运行。用户应仅在确有需要时使用同步 zedlet，因为它们会降低并行度。

要使某个 zedlet 同步，只需在 zedlet 文件名中紧跟事件名之后加上 `-sync-`：

`EVENT_NAME-sync-ZEDLETNAME.sh`

例如，如果你需要一个同步的 statechange 脚本：

`statechange-sync-myzedlet.sh`

## 文件

### `@sysconfdir@/zfs/zed.d`

已启用 ZEDLET 的默认目录。

### `@sysconfdir@/zfs/zed.d/zed.rc`

ZEDLET 所用公共变量的默认 rc 文件。

### `@zfsexecdir@/zed.d`

已安装 ZEDLET 的默认目录。

### `@runstatedir@/zed.pid`

包含守护进程进程 ID 的默认文件。

### `@runstatedir@/zed.state`

包含守护进程状态的默认文件。

## 信号

### `SIGHUP`

重新配置守护进程，并重新扫描目录以查找已启用的 ZEDLET。

### `SIGTERM`、`SIGINT`

终止守护进程。

## 参考文献

zfs(8)、zpool(8)、zpool-events(8)

## 注意

`zed` 需要 root 权限。

不要招惹 `zed`。

## 缺陷

ZEDLET 无法向内核返回状态/状态信息。

尚未添加基于 gettext 的国际化支持。

2022 年 8 月 22 日
