# vdev_id.conf(5)

## 名称

`vdev_id.conf` — vdev_id(8) 的配置文件

## 说明

`vdev_id.conf` 是 vdev_id(8) 的配置文件。它在将磁盘设备名称映射为别名时，控制 vdev_id(8) 的默认行为。

`vdev_id.conf` 文件使用的格式很简单：单行内由一个关键字后跟一个或多个值组成。任何不以可识别关键字开头的行都会被忽略。注释行可以选择以井号字符开头。

本文件使用以下关键字和值。

### `alias name devlink`

将 `/dev` 目录层次结构中的设备链接映射为新的设备名称。定义该设备链接的 udev 规则必须在 vdev_id(8) 运行之前执行。定义好的别名优先于由拓扑推导出的名称，除此之外，两种命名方式可以共存。例如，可以用 `sas_direct` 拓扑为 JBOD 中的磁盘命名，同时用别名命名内部的 L2ARC 设备。

`name` 是将在 `/dev/disk/by-vdev` 下创建的、指向该设备的链接名称。

`devlink` 是 udev 中已经定义的设备链接名称，可以是绝对路径，也可以是基本文件名。

### `channel [pci_slot] port name`

将物理路径映射为通道名称（通常代表单个磁盘机箱）。

### `enclosure_symlinks yes|no`

额外创建指向磁盘机箱 `sg` 设备的 `/dev/by-enclosure` 符号链接，命名规则取自 `vdev_id.conf`。`enclosure_symlinks` 仅在 `sas_direct` 模式下允许使用。

### `enclosure_symlinks_prefix prefix`

指定机箱符号链接的前缀，形式为 `/dev/by-enclosure/<prefix>-<channel><num>`。

默认值为 `enc`。

### `slot prefix new [channel]`

将操作系统报告的磁盘插槽编号映射为另一个插槽编号。如果指定了 `channel` 参数，则该映射仅应用于指定通道中的插槽，否则应用于所有通道。第一条能够匹配插槽的 `slot` 规则优先生效。因此，针对某一插槽的通道专属映射通常应排在同一插槽的通用映射之前。这样，就可以对特定通道应用自定义映射，而对其余通道应用默认映射。

### `zpad_slot digits`

用零填充插槽编号，使其长度为 `digits` 位，这有助于使磁盘名称长度一致并且更易于排序。

### `multipath yes|no`

指定 vdev_id(8) 是否仅处理 dm-multipath 设备。如果设为 `yes`，则 vdev_id(8) 会检查驱动程序命令所提供的 dm-multipath 设备中第一个处于运行状态的组件磁盘，以此确定物理路径。

### `topology sas_direct|sas_expander|sas_switch|scsi`

指定决定物理路径如何映射到通道的物理拓扑：

* `sas_direct` 和 `scsi`：通道由 PCI 插槽和 HBA 端口号唯一标识
* `sas_expander`：通道由设备路径中最右侧扩展器的 SAS 地址唯一标识
* `sas_switch`：通道由 SAS 交换机端口号唯一标识

### `phys_per_port num`

指定与某个 SAS HBA 端口或 SAS 交换机端口关联的 PHY 设备数量。vdev_id(8) 内部使用该值来判断设备连接到哪个 HBA 端口或交换机端口。默认值为 `4`。

### `slot bay|phy|port|id|lun|bay_lun|ses`

指定从 SAS 标识符的哪个元素中获取插槽编号。默认值为 `bay`：

* `bay`：从 bay 标识符读取插槽编号。
* `phy`：从 phy 标识符读取插槽编号。
* `port`：使用 SAS 端口作为插槽编号。
* `id`：使用 scsi id 作为插槽编号。
* `lun`：使用 scsi lun 作为插槽编号。
* `bay_lun`：从 bay 标识符读取插槽编号，并追加 lun 编号。适用于多 lun 多执行器的硬盘。
* `ses`：使用 SCSI Enclosure Services（SES）机箱设备的插槽编号，该编号由 sg_ses(8) 报告。仅适用于不支持 `bay` 的系统，需要注意的是，`port` 和 `id` 在更换磁盘后可能不稳定。

## 文件

### `/etc/zfs/vdev_id.conf`

vdev_id(8) 的配置文件。

## 示例

非多路径配置，直连 SAS 机箱，以及任意的插槽重映射：

```sh
multipath     no
topology      sas_direct
phys_per_port 4
slot          bay

#       PCI_SLOT HBA PORT  CHANNEL NAME
channel 85:00.0  1         A
channel 85:00.0  0         B
channel 86:00.0  1         C
channel 86:00.0  0         D

# Custom mapping for Channel A

#    Linux      Mapped
#    Slot       Slot      Channel
slot 1          7         A
slot 2          10        A
slot 3          3         A
slot 4          6         A

# Default mapping for B, C, and D

slot 1          4
slot 2          2
slot 3          1
slot 4          3
```

SAS 交换机拓扑。请注意，在此示例中 `channel` 关键字只接受两个参数：

```sh
topology      sas_switch

#       SWITCH PORT  CHANNEL NAME
channel 1            A
channel 2            B
channel 3            C
channel 4            D
```

SAS 扩展器拓扑。请注意，在此示例中 `channel` 关键字只接受两个参数：

```sh
topology      sas_expander

#       EXPANDER ADDR      CHANNEL NAME
channel 0x500304000000000f J1A
channel 0x500304000000001f J1B
channel 0x500304000000002f J2A
channel 0x500304000000003f J2B
```

多路径配置。请注意，通道名称有多个定义——每条物理路径一个：

```sh
multipath yes

#       PCI_SLOT HBA PORT  CHANNEL NAME
channel 85:00.0  1         A
channel 85:00.0  0         B
channel 86:00.0  1         A
channel 86:00.0  0         B
```

启用 `enclosure_symlinks` 的配置：

```sh
multipath yes
enclosure_symlinks yes

#          PCI_ID      HBA PORT     CHANNEL NAME
channel    05:00.0     1            U
channel    05:00.0     0            L
channel    06:00.0     1            U
channel    06:00.0     0            L
```

除磁盘符号链接外，此配置还会创建：

```sh
/dev/by-enclosure/enc-L0
/dev/by-enclosure/enc-L1
/dev/by-enclosure/enc-U0
/dev/by-enclosure/enc-U1
```

使用设备链接别名的配置：

```sh
#     by-vdev
#     name     fully qualified or base name of device link
alias d1       /dev/disk/by-id/wwn-0x5000c5002de3b9ca
alias d2       wwn-0x5000c5002def789e
```

## 参考文献

vdev_id(8)

2024 年 10 月 8 日  Debian
