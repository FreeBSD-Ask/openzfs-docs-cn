# zpool-status(8)

## 名称

`zpool-status` — 显示 ZFS 存储池的详细健康状况

## 概述

```sh
zpool status [-DdegiLPpstx] [-v|-vv] [-c 脚本1[,脚本2,…]] [-j|--json [--json-flat-vdevs] [--json-int] [--json-pool-key-guid]] [-T d|u] [--power] [池名] [间隔 [次数]]
```

## 说明

显示给定池的详细健康状况。如果未指定池名，则显示系统中每个池的状态。有关池与设备健康状况的更多信息，参见 zpoolconcepts(7) 中的“设备故障与恢复”一节。

如果 scrub 或 resilver 正在进行，此命令会报告已完成的百分比与预计完成时间。这两项都只是近似值，因为池中的数据量与系统上的其他工作负载都可能变化。由于活动系统上存在并发写入，scrub 和 resilver 的进度都可能超过 100%。

### `-c script1[,script2,…]`

在每个 vdev 上运行一个或多个脚本，并将输出作为新的一列包含在 `zpool status` 输出中。完整细节参见 `zpool iostat` 的 `-c` 选项。

### `-D`

显示去重统计的直方图，按引用计数显示已分配（磁盘上实际存在的）与被引用（在池中被逻辑引用的）块的数量与大小。重复指定时（-DD），还会显示 DDT 有多少驻留在 ARC 中的统计信息。

### `-d`

显示顶级 VDEV 上发生过的 Direct I/O 读/写校验和验证错误的数量。有关可导致 Direct I/O 写校验和验证失败发生的条件详情，参见 zfs(4) 中的 `zfs_vdev_direct_write_verify`。如果 I/O 已发出且仍在传输途中时缓冲区内容被改动，也可能发生 Direct I/O 读校验和验证错误。发生 Direct I/O 读校验和验证错误时，该 I/O 会经由 ARC 重新发出。

### `-e`

仅显示不健康的 vdev（非 ONLINE 状态或有错误的 vdev）。

### `-g`

显示 vdev 的 GUID 而非通常的设备名。这些 GUID 可以在 zpool detach/offline/remove/replace 命令中代替设备名使用。

### `-i`

显示 vdev 的初始化状态。

### `-j`、`--json [--json-flat-vdevs] [--json-int] [--json-pool-key-guid]`

以 JSON 格式显示 ZFS 池的状态。指定 `--json-flat-vdevs` 时以扁平层次结构显示 vdev，而不是嵌套的 vdev 对象。指定 `--json-int` 时以整数格式显示数字，而不是字符串。指定 `--json-pool-key-guid` 时以池 GUID 作为池对象的键，而不是池名。

### `-L`

显示 vdev 的真实路径，解析所有符号链接。无论打开设备时使用的是 `/dev/disk/` 下的哪个路径，都可以用它查找当前的块设备名。

### `-P`

显示 vdev 的完整路径，而不是只有路径的最后一个组成部分。可以与 `-L` 标志配合使用。

### `-p`

以可解析（精确）值显示数字。

### `--power`

显示 vdev 机箱插槽的电源状态（开或关）。

### `-s`

显示叶 vdev 慢速 I/O 操作的数量。这是未在 `zio_slow_io_ms` 毫秒（默认为 30000）内完成的 I/O 操作数量。这不一定意味着这些 I/O 操作未能完成，只是耗时不合理地长。这可能表明底层存储存在问题。

### `-T d|u`

显示时间戳。指定 d 使用标准日期格式，参见 date(1)。指定 u 使用时间内部表示的可打印形式，参见 time(1)。

### `-t`

显示 vdev 的 TRIM 状态。

### `-v|-vv`

显示详细的数据错误信息，打印出自上次完整池 scrub 以来所有包含数据错误的文件的完整列表。指定两次（-vv）时，会打印出每个受损文件中所有受损记录的完整列表。如果启用了 `head_errlog` 特性且包含错误的文件已被删除，则后续运行此命令时将不再报告相应的文件名。

### `-x`

仅显示出现错误或以其他方式不可用的池的状态。不包含关于池未使用最新磁盘格式的警告。

## 示例

### 示例 1：添加输出列

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

### 示例 2：以 JSON 格式显示状态输出

指定 `-j` 时，`zpool status` 可以以 JSON 格式输出。可以使用 `-c` 在每个 VDEV 上运行脚本。

```sh
# zpool status -j -c vendor,model,size | jq
{
  "output_version": {
    "command": "zpool status",
    "vers_major": 0,
    "vers_minor": 1
  },
  "pools": {
    "tank": {
      "name": "tank",
      "state": "ONLINE",
      "guid": "3920273586464696295",
      "txg": "16597",
      "spa_version": "5000",
      "zpl_version": "5",
      "status": "OK",
      "vdevs": {
        "tank": {
          "name": "tank",
          "alloc_space": "62.6G",
          "total_space": "15.0T",
          "def_space": "11.3T",
          "read_errors": "0",
          "write_errors": "0",
          "checksum_errors": "0",
          "vdevs": {
            "raidz1-0": {
              "name": "raidz1-0",
              "vdev_type": "raidz",
              "guid": "763132626387621737",
              "state": "HEALTHY",
              "alloc_space": "62.5G",
              "total_space": "10.9T",
              "def_space": "7.26T",
              "rep_dev_size": "10.9T",
              "read_errors": "0",
              "write_errors": "0",
              "checksum_errors": "0",
              "vdevs": {
                "ca1eb824-c371-491d-ac13-37637e35c683": {
                  "name": "ca1eb824-c371-491d-ac13-37637e35c683",
                  "vdev_type": "disk",
                  "guid": "12841765308123764671",
                  "path": "/dev/disk/by-partuuid/ca1eb824-c371-491d-ac13-37637e35c683",
                  "state": "HEALTHY",
                  "rep_dev_size": "3.64T",
                  "phys_space": "3.64T",
                  "read_errors": "0",
                  "write_errors": "0",
                  "checksum_errors": "0",
                  "vendor": "ATA",
                  "model": "WDC WD40EFZX-68AWUN0",
                  "size": "3.6T"
                },
                "97cd98fb-8fb8-4ac4-bc84-bd8950a7ace7": {
                  "name": "97cd98fb-8fb8-4ac4-bc84-bd8950a7ace7",
                  "vdev_type": "disk",
                  "guid": "1527839927278881561",
                  "path": "/dev/disk/by-partuuid/97cd98fb-8fb8-4ac4-bc84-bd8950a7ace7",
                  "state": "HEALTHY",
                  "rep_dev_size": "3.64T",
                  "phys_space": "3.64T",
                  "read_errors": "0",
                  "write_errors": "0",
                  "checksum_errors": "0",
                  "vendor": "ATA",
                  "model": "WDC WD40EFZX-68AWUN0",
                  "size": "3.6T"
                },
                "e9ddba5f-f948-4734-a472-cb8aa5f0ff65": {
                  "name": "e9ddba5f-f948-4734-a472-cb8aa5f0ff65",
                  "vdev_type": "disk",
                  "guid": "6982750226085199860",
                  "path": "/dev/disk/by-partuuid/e9ddba5f-f948-4734-a472-cb8aa5f0ff65",
                  "state": "HEALTHY",
                  "rep_dev_size": "3.64T",
                  "phys_space": "3.64T",
                  "read_errors": "0",
                  "write_errors": "0",
                  "checksum_errors": "0",
                  "vendor": "ATA",
                  "model": "WDC WD40EFZX-68AWUN0",
                  "size": "3.6T"
                }
              }
            }
          }
        }
      },
      "dedup": {
        "mirror-2": {
          "name": "mirror-2",
          "vdev_type": "mirror",
          "guid": "2227766268377771003",
          "state": "HEALTHY",
          "alloc_space": "89.1M",
          "total_space": "3.62T",
          "def_space": "3.62T",
          "rep_dev_size": "3.62T",
          "read_errors": "0",
          "write_errors": "0",
          "checksum_errors": "0",
          "vdevs": {
            "db017360-d8e9-4163-961b-144ca75293a3": {
              "name": "db017360-d8e9-4163-961b-144ca75293a3",
              "vdev_type": "disk",
              "guid": "17880913061695450307",
              "path": "/dev/disk/by-partuuid/db017360-d8e9-4163-961b-144ca75293a3",
              "state": "HEALTHY",
              "rep_dev_size": "3.63T",
              "phys_space": "3.64T",
              "read_errors": "0",
              "write_errors": "0",
              "checksum_errors": "0",
              "vendor": "ATA",
              "model": "WDC WD40EFZX-68AWUN0",
              "size": "3.6T"
            },
            "952c3baf-b08a-4a8c-b7fa-33a07af5fe6f": {
              "name": "952c3baf-b08a-4a8c-b7fa-33a07af5fe6f",
              "vdev_type": "disk",
              "guid": "10276374011610020557",
              "path": "/dev/disk/by-partuuid/952c3baf-b08a-4a8c-b7fa-33a07af5fe6f",
              "state": "HEALTHY",
              "rep_dev_size": "3.63T",
              "phys_space": "3.64T",
              "read_errors": "0",
              "write_errors": "0",
              "checksum_errors": "0",
              "vendor": "ATA",
              "model": "WDC WD40EFZX-68AWUN0",
              "size": "3.6T"
            }
          }
        }
      },
      "special": {
        "25d418f8-92bd-4327-b59f-7ef5d5f50d81": {
          "name": "25d418f8-92bd-4327-b59f-7ef5d5f50d81",
          "vdev_type": "disk",
          "guid": "3935742873387713123",
          "path": "/dev/disk/by-partuuid/25d418f8-92bd-4327-b59f-7ef5d5f50d81",
          "state": "HEALTHY",
          "alloc_space": "37.4M",
          "total_space": "444G",
          "def_space": "444G",
          "rep_dev_size": "444G",
          "phys_space": "447G",
          "read_errors": "0",
          "write_errors": "0",
          "checksum_errors": "0",
          "vendor": "ATA",
          "model": "Micron_5300_MTFDDAK480TDS",
          "size": "447.1G"
        }
      },
      "error_count": "0"
    }
  }
}
```

## 参考文献

zpool-condense(8)、zpool-events(8)、zpool-history(8)、zpool-iostat(8)、zpool-list(8)、zpool-resilver(8)、zpool-scrub(8)、zpool-wait(8)

2026 年 6 月 16 日
