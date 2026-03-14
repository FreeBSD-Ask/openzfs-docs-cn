# 消息 ID：ZFS-8000-EY

## ZFS 标签主机 ID 不匹配

| 类型   | 错误                   |
| :---------: | :-------------------- |
| 严重性  | 重要                  |
| 描述  | 该 ZFS 池上次被其他系统/主机访问过 |
| 自动响应 | 不会采取自动响应           |
| 影响  | ZFS 文件系统不可用        |

## 建议系统管理员采取的操作

该池曾被另一台主机写入，并且未从另一系统正确导出。在多台系统上同时主动导入同一池，会导致池损坏并进入不可恢复状态。要确定最后访问该池的系统，请运行 `zpool import` 命令：

```sh
# zpool import
  pool: test
    id: 14702934086626715962
 state: ONLINE
status: The pool was last accessed by another system.
action: The pool can be imported using its name or numeric identifier and
        the '-f' flag.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-EY
config:

        test              ONLINE
          c0t0d0          ONLINE

# zpool import test
cannot import 'test': pool may be in use from other system, it was last
accessed by 'tank' (hostid: 0x1435718c) on Fri Mar  9 15:42:47 2007
use '-f' to import anyway
```

如果确定该池未被另一系统主动访问，则可以使用 `zpool import` 的 `-f` 选项强制导入该池。

## 详细信息

消息 ID：`ZFS-8000-EY` 表示该池无法导入，因为它上次被另一系统访问。请按照文档中的操作解决该问题。
