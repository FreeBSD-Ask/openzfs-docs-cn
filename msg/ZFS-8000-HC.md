# 消息 ID：ZFS-8000-HC

## ZFS 池 I/O 故障

| 类型   | 错误                      |
| :---------: | :----------------------- |
| 严重性  | 重要                    |
| 描述   | ZFS 池目前发生了无法恢复的 I/O 故障 |
| 自动响应 | 不会采取自动响应              |
| 影响   | 读写 I/O 无法处理          |

## 建议系统管理员采取的操作

该池发生了 I/O 故障。由于 ZFS 池属性 `failmode` 设置为‘wait’，所有 I/O（读写）都被阻塞。有关 `failmode` 属性的更多信息，请参阅 zpoolprops(8) 手册页。需要手动干预以处理 I/O。

可以通过运行 `zpool status -x` 查看受影响的设备：

```sh
# zpool status -x
  pool: test
 state: FAULTED
status: There are I/O failures.
action: Make sure the affected devices are connected, then run 'zpool clear'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-HC
 scrub: none requested
config:

        NAME        STATE     READ WRITE CKSUM
        test        FAULTED      0    13     0  insufficient replicas
          c0t0d0    FAULTED      0     7     0  experienced I/O failures
          c0t1d0    ONLINE       0     0     0

errors: 1 data errors, use '-v' for a list
```

在确认受影响的设备已连接后，运行 `zpool clear` 以重新允许对池的 I/O 操作：

```sh
# zpool clear test
```

如果 I/O 故障仍然发生，则池上的应用程序和命令可能会挂起。此时，可能需要重启系统以再次允许对池的 I/O 操作。

## 详细信息

消息 ID：`ZFS-8000-HC` 表示该池发生了 I/O 故障。请按照文档中的操作解决该问题。
