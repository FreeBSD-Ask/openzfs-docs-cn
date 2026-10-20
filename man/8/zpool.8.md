# zpool(8)

## 名称

`zpool` — 配置 ZFS 存储池

## 概述

```sh
zpool -?V
```

```sh
zpool version [-j]
```

```sh
zpool 子命令 [参数]
```

## 说明

`zpool` 命令用于配置 ZFS 存储池。存储池是一组设备的集合，为 ZFS 数据集提供物理存储与数据复制。存储池内的所有数据集共享同一空间。管理数据集的相关信息参见 zfs(8)。

有关创建与管理 ZFS 存储池的概述，参见 zpoolconcepts(7) 手册页。

## 子命令

所有修改状态的子命令都会以其原始形式持久记录到池中。

`zpool` 命令提供用于创建与销毁存储池、为存储池增加容量以及提供存储池信息的子命令。支持以下子命令：

### `zpool -?`

显示帮助消息。

### `zpool -V`、`-version`

### `zpool version [-j]`

显示 `zpool` 用户态实用程序与 ZFS 内核模块的软件版本。使用 `-j` 选项以 JSON 格式输出。

### 创建

#### zpool-create(8)

创建一个新的存储池，其中包含命令行上指定的虚拟设备。

#### zpool-initialize(8)

开始初始化，向指定设备上的所有未分配区域写入；如果未单独指定设备，则向池中所有符合条件的设备写入。

### 销毁

#### zpool-destroy(8)

销毁给定的池，将其中的设备释放供其他用途使用。

#### zpool-labelclear(8)

从指定 `device` 中移除 ZFS 标签信息，使所有数据在没有专用恢复工具的情况下都无法访问。该操作无法用 ZFS 工具撤销。

### 虚拟设备

#### zpool-attach(8)/zpool-detach(8)

将非冗余磁盘转换为镜像，或提升现有镜像的冗余级别（`attach`）；或执行相反操作（`detach`）。

#### zpool-add(8)/zpool-remove(8)

将指定的虚拟设备添加到给定池中，或从池中移除指定设备。

#### zpool-replace(8)

用新设备替换现有设备（该设备可能已故障）。

#### zpool-split(8)

通过拆分现有池中的所有镜像来创建新池（这会降低原池的冗余）。

### 属性

可用的池属性在 zpoolprops(7) 手册页中列出。

#### zpool-list(8)

列出给定池及其健康状况与空间使用情况。

#### zpool-get(8)/zpool-set(8)

检索指定存储池的给定属性列表（使用 `all` 时检索全部属性）。

### 监控

#### zpool-status(8)

显示给定池的详细健康状况。

#### zpool-iostat(8)

显示给定池/vdev 的逻辑 I/O 统计信息。物理 I/O 操作可通过 iostat(1) 观察。

#### zpool-events(8)

列出 ZFS 内核模块生成的所有最近事件。这些事件由 zed(8) 消费，用于自动化管理任务，例如用热备盘替换失效设备。该手册页还描述了可生成的子类与事件有效载荷。

#### zpool-history(8)

显示指定池的命令历史记录；若未指定池，则显示所有池的命令历史记录。

### 维护

#### zpool-prefetch(8)

预取特定类型的池数据。

#### zpool-scrub(8)

启动 scrub 或恢复已暂停的 scrub。

#### zpool-condense(8)

压缩、刷新、垃圾回收或以其他方式清理池元数据。

#### zpool-checkpoint(8)

为 `pool` 的当前状态创建检查点，之后可以通过 `zpool import --rewind-to-checkpoint` 恢复到该状态。

#### zpool-trim(8)

对池中所有空闲空间立即发起按需 TRIM 操作。该操作会告知底层存储设备池中哪些块不再被分配，使精简置备（thinly provisioned）的设备能够回收这些空间。

#### zpool-sync(8)

该命令强制将内存中的所有脏数据写入主池存储而非 ZIL。它还会更新管理信息，包括配额报告。不带参数时，`zpool sync` 会同步系统上的所有池；否则只同步指定的池。

#### zpool-upgrade(8)

管理存储池的磁盘格式版本。

#### zpool-wait(8)

等待给定池中给定类型的所有后台活动全部停止。

### 故障处理

#### zpool-offline(8)/zpool-online(8)

将指定物理设备离线，或使其重新上线。

#### zpool-resilver(8)

启动 resilver。如果已有 resilver 正在运行，它将从头重新开始。

#### zpool-reopen(8)

重新打开与池关联的所有 vdev。

#### zpool-clear(8)

清除池中的设备错误。

### 导入与导出

#### zpool-import(8)

使包含 ZFS 存储池的磁盘可在系统上使用。

#### zpool-export(8)

从系统导出给定的池。

#### zpool-reguid(8)

为池生成新的唯一标识符。

## 退出状态

返回以下退出值：

### `0`

成功完成。

### `1`

发生错误。

### `2`

指定了无效的命令行选项。

## 示例

### 示例 1：创建 RAID-Z 存储池

以下命令创建一个池，其中包含一个由六块磁盘组成的 raidz 根 vdev：

```sh
# zpool create tank raidz sda sdb sdc sdd sde sdf
```

### 示例 2：创建镜像存储池

以下命令创建一个包含两个镜像的池，每个镜像包含两块磁盘：

```sh
# zpool create tank mirror sda sdb mirror sdc sdd
```

### 示例 3：使用分区创建 ZFS 存储池

以下命令使用两个磁盘分区创建一个非冗余池：

```sh
# zpool create tank sda1 sdb2
```

### 示例 4：使用文件创建 ZFS 存储池

以下命令使用文件创建一个非冗余池。虽然不推荐，但基于文件的池可用于实验目的。

```sh
# zpool create tank /path/to/file/a /path/to/file/b
```

### 示例 5：将非镜像的 ZFS 存储池转换为镜像

以下命令通过附加第二块设备 `sdb`，将现有的单设备 `sda` 转换为镜像：

```sh
# zpool attach tank sda sdb
```

### 示例 6：向 ZFS 存储池添加镜像

以下命令向池 `tank` 添加两块镜像磁盘，假定该池已由双向镜像构成。新增空间可立即供池内的所有数据集使用。

```sh
# zpool add tank mirror sda sdb
```

### 示例 7：列出可用的 ZFS 存储池

以下命令列出系统上所有可用的池。此例中，池 `zion` 因缺少设备而处于故障（faulted）状态。该命令的结果与以下内容类似：

```sh
# zpool list
NAME    SIZE  ALLOC   FREE  EXPANDSZ   FRAG    CAP  DEDUP  HEALTH  ALTROOT
rpool  19.9G  8.43G  11.4G         -    33%    42%  1.00x  ONLINE  -
tank   61.5G  20.0G  41.5G         -    48%    32%  1.00x  ONLINE  -
zion       -      -      -         -      -      -      -  FAULTED -
```

### 示例 8：销毁 ZFS 存储池

以下命令销毁池 `tank` 及其中包含的所有数据集：

```sh
# zpool destroy -f tank
```

### 示例 9：导出 ZFS 存储池

以下命令导出池 `tank` 中的设备，以便将其移往他处或稍后导入：

```sh
# zpool export tank
```

### 示例 10：导入 ZFS 存储池

以下命令显示可用的池，然后导入池 `tank` 供系统使用。该命令的结果与以下内容类似：

```sh
# zpool import
  pool: tank
    id: 15451357997522795478
 state: ONLINE
action: The pool can be imported using its name or numeric identifier.
config:

        tank        ONLINE
          mirror    ONLINE
            sda     ONLINE
            sdb     ONLINE

# zpool import tank
```

### 示例 11：将所有 ZFS 存储池升级到当前版本

以下命令将所有 ZFS 存储池升级到当前软件版本：

```sh
# zpool upgrade -a
This system is currently running ZFS version 2.
```

### 示例 12：管理热备盘

以下命令创建一个带可用热备盘的新池：

```sh
# zpool create tank mirror sda sdb spare sdc
```

如果其中一块磁盘发生故障，池将降级到 degraded 状态。可以使用以下命令替换故障设备：

```sh
# zpool replace tank sda sdd
```

数据 resilver 完成后，热备盘会被自动移除，并在其他设备再次发生故障时重新投入使用。可以使用以下命令将热备盘从池中永久移除：

```sh
# zpool remove tank sdc
```

### 示例 13：创建带镜像独立意图日志的 ZFS 池

以下命令创建一个 ZFS 存储池，由两个双向镜像和镜像的日志设备组成：

```sh
# zpool create pool mirror sda sdb mirror sdc sdd log mirror sde sdf
```

### 示例 14：向 ZFS 池添加缓存设备

以下命令向 ZFS 存储池添加两块用作缓存设备的磁盘：

```sh
# zpool add pool cache sdc sdd
```

添加后，缓存设备会逐渐填满来自主内存的内容。视缓存设备的大小而定，填满可能需要一个多小时。可以使用 `iostat` 子命令监控容量与读取情况，如下所示：

```sh
# zpool iostat -v pool 5
```

### 示例 15：移除镜像的顶级（日志或数据）设备

以下命令移除镜像日志设备 `mirror-2` 与镜像顶级数据设备 `mirror-1`。

给定以下配置：

```sh
  pool: tank
 state: ONLINE
 scrub: none requested
config:

         NAME        STATE     READ WRITE CKSUM
         tank        ONLINE       0     0     0
           mirror-0  ONLINE       0     0     0
             sda     ONLINE       0     0     0
             sdb     ONLINE       0     0     0
           mirror-1  ONLINE       0     0     0
             sdc     ONLINE       0     0     0
             sdd     ONLINE       0     0     0
         logs
           mirror-2  ONLINE       0     0     0
             sde     ONLINE       0     0     0
             sdf     ONLINE       0     0     0
```

移除镜像日志 `mirror-2` 的命令为：

```sh
# zpool remove tank mirror-2
```

此时，日志设备已不复存在（镜像的两侧均已被移除）：

```sh
  pool: tank
 state: ONLINE
  scan: none requested
config:

        NAME        STATE     READ WRITE CKSUM
        tank        ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            sda     ONLINE       0     0     0
            sdb     ONLINE       0     0     0
          mirror-1  ONLINE       0     0     0
            sdc     ONLINE       0     0     0
            sdd     ONLINE       0     0     0
```

移除镜像数据 `mirror-1` 的命令为：

```sh
# zpool remove tank mirror-1
```

`mirror-1` 腾空后，池仍保持冗余，但总空间量减少了：

```sh
  pool: tank
 state: ONLINE
  scan: none requested
config:

        NAME        STATE     READ WRITE CKSUM
        tank        ONLINE       0     0     0
          mirror-0  ONLINE       0     0     0
            sda     ONLINE       0     0     0
            sdb     ONLINE       0     0     0
```

### 示例 16：显示设备上扩展的空间

以下命令显示池 `data` 的详细信息。该池由单个 raidz vdev 组成，其中一个设备的容量增加了 10 GiB。在此示例中，在 raidz vdev 下的所有设备都完成扩展之前，池将无法利用这部分额外容量。

```sh
# zpool list -v data
NAME         SIZE  ALLOC   FREE  EXPANDSZ   FRAG    CAP  DEDUP  HEALTH  ALTROOT
data        23.9G  14.6G  9.30G         -    48%    61%  1.00x  ONLINE  -
  raidz1    23.9G  14.6G  9.30G         -    48%
    sda         -      -      -         -      -
    sdb         -      -      -       10G      -
    sdc         -      -      -         -      -
```

### 示例 17：添加输出列

可以使用 `-c` 向 `zpool status` 与 `zpool iostat` 的输出添加额外的列。

```sh
# zpool status -c vendor,model,size
   NAME     STATE  READ WRITE CKSUM vendor  model        size
   tank     ONLINE 0    0     0
   mirror-0 ONLINE 0    0     0
   U1       ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U10      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U11      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U12      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U13      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T
   U14      ONLINE 0    0     0     SEAGATE ST8000NM0075 7.3T

# zpool iostat -vc size
              capacity     operations     bandwidth
pool        alloc   free   read  write   read  write  size
----------  -----  -----  -----  -----  -----  -----  ----
rpool       14.6G  54.9G      4     55   250K  2.69M
  sda1      14.6G  54.9G      4     55   250K  2.69M   70G
----------  -----  -----  -----  -----  -----  -----  ----
```

## 环境变量

### `ZFS_ABORT`

使 `zpool` 在退出时转储核心（core dump），以便运行 `::findleaks`。

### `ZFS_COLOR`

在 `zpool status` 与 `zpool iostat` 的输出中使用 ANSI 颜色。

### `ZPOOL_AUTO_POWER_ON_SLOT`

运行 `zpool online` 或 `zpool clear` 命令时，自动尝试打开驱动器所在机箱插槽的电源。其效果等同于向这些命令传递 `--power` 选项。

### `ZPOOL_POWER_ON_SLOT_TIMEOUT_MS`

写入后等待插槽电源 sysfs 值返回正确结果的最长时间（毫秒）。例如，向 sysfs 机箱插槽的 `power_control` 文件写入“on”后，机箱可能需要一段时间才能对插槽下电，并在读回 `power_control` 值时返回“on”。未设置时默认为 30 秒（30000ms）。

### `ZPOOL_IMPORT_PATH`

供池使用的设备或文件的搜索路径。这是一个以冒号分隔的目录列表，`zpool` 会在其中查找设备节点与文件。类似于 `zpool import` 的 `-d` 选项。

### `ZPOOL_IMPORT_UDEV_TIMEOUT_MS`

`zpool import` 等待预期设备变为可用的最长时间（毫秒）。

### `ZPOOL_STATUS_NON_NATIVE_ASHIFT_IGNORE`

如果设置此变量，将抑制 `zpool status` 中关于 vdev 非原生 ashift 的警告。该变量的值不会被使用，只关心其存在与否。

### `ZPOOL_VDEV_NAME_GUID`

使 `zpool` 子命令默认输出 vdev 的 GUID。该行为与 `zpool status` 的 `-g` 命令行选项相同。

### `ZPOOL_VDEV_NAME_FOLLOW_LINKS`

使 `zpool` 子命令默认跟随链接来解析 vdev 名称。该行为与 `zpool status` 的 `-L` 命令行选项相同。

### `ZPOOL_VDEV_NAME_PATH`

使 `zpool` 子命令默认输出 vdev 的完整路径名。该行为与 `zpool status` 的 `-P` 命令行选项相同。

### `ZFS_VDEV_DEVID_OPT_OUT`

在旧版 OpenZFS 实现中，如果池配置中存在 `devid` NVP 值，尝试显示池配置中的 vdev 名称时会出现问题。

例如，源自 illumos 平台的池配置中会带有 `devid` 值，`zpool status` 在列出配置时会失败。对于未来基于 Linux 的池也是如此。

通过设置 `ZFS_VDEV_DEVID_OPT_OUT`，可以在导入时移除池中的所有 `devid` 值，或防止 `zpool create` 与 `zpool add` 添加此类值。

### `ZPOOL_SCRIPTS_AS_ROOT`

允许特权用户运行 `zpool status`/`zpool iostat -c`。通常只允许非特权用户运行 `-c`。

### `ZPOOL_SCRIPTS_PATH`

运行 `zpool status`/`zpool iostat -c` 时脚本的搜索路径。这是一个以冒号分隔的目录列表，会覆盖默认的 `~/.zpool.d` 与 `/etc/zfs/zpool.d` 搜索路径。

### `ZPOOL_SCRIPTS_ENABLED`

允许用户运行 `zpool status`/`zpool iostat -c`。如果未设置 `ZPOOL_SCRIPTS_ENABLED`，则假定允许用户运行 `zpool status`/`zpool iostat -c`。

### `ZFS_MODULE_TIMEOUT`

等待 `/dev/zfs` 出现的时间（秒）。默认为 `10`，最大为 `600`（10 分钟）。若小于 `0`，则无限等待；若为 `0`，则不等待。

## 接口稳定性

**演进中**（Evolving）。

## 参考文献

zfs(4)、zpool-features(7)、zpoolconcepts(7)、zpoolprops(7)、zed(8)、zfs(8)、zpool-add(8)、zpool-attach(8)、zpool-checkpoint(8)、zpool-clear(8)、zpool-create(8)、zpool-ddtprune(8)、zpool-destroy(8)、zpool-detach(8)、zpool-events(8)、zpool-export(8)、zpool-get(8)、zpool-history(8)、zpool-import(8)、zpool-initialize(8)、zpool-iostat(8)、zpool-labelclear(8)、zpool-list(8)、zpool-offline(8)、zpool-online(8)、zpool-prefetch(8)、zpool-reguid(8)、zpool-remove(8)、zpool-reopen(8)、zpool-replace(8)、zpool-resilver(8)、zpool-scrub(8)、zpool-set(8)、zpool-split(8)、zpool-status(8)、zpool-sync(8)、zpool-trim(8)、zpool-upgrade(8)、zpool-wait(8)

2026 年 5 月 26 日
