# vdev_id(8)

## 名称

`vdev_id` — 为 JBOD 磁盘生成易于使用的名称

## 概述

```sh
vdev_id -d 设备 -c 配置文件 -g sas_direct|sas_expander|sas_switch|scsi -m -p 每端口 PHY 数量
```

## 说明

vdev_id 是一个 udev 辅助工具，它通过解析 vdev_id.conf(5) 将存储拓扑中的物理路径映射为通道名称。通道名称与磁盘机箱插槽编号组合，生成一个反映磁盘物理位置的别名。在更换故障磁盘之类的任务中，这一点尤其有用。如果默认编号不能令人满意，还可以对插槽编号进行重映射。磁盘别名将以符号链接的形式创建在 `/dev/disk/by-vdev` 中。

当前支持的拓扑有 sas_direct、sas_expander、sas_switch 和 scsi。还支持一种多路径模式，该模式下通过检查驱动程序所报告的第一个处于运行状态的组件磁盘来处理 dm-mpath 设备。在多路径模式下，通往给定机箱的每条路径都应在配置文件中包含一个同名的通道定义。

vdev_id 还支持使用配置文件关键字 `alias`，基于 `/dev` 层次结构中现有的 udev 链接创建别名。详情参见 vdev_id.conf(5)。

## 选项

### `-d device`

要分类的设备节点，例如 `/dev/sda`。

### `-c config_file`

指定备用配置文件的路径。默认值为 `/etc/zfs/vdev_id.conf`。

### `-g sas_direct|sas_expander|sas_switch|scsi`

标识决定物理路径如何映射到通道的物理拓扑：

* `sas_direct` 和 `scsi`：通道由 PCI 插槽和 HBA 端口号唯一标识
* `sas_expander`：通道由设备路径中最右侧扩展器的 SAS 地址唯一标识
* `sas_switch`：通道由 SAS 交换机端口号唯一标识

### `-m`

仅处理 dm-multipath 设备。如果指定此选项，则检查驱动程序所提供的 dm-multipath 设备中第一个处于运行状态的组件磁盘，以此确定物理路径。

### `-p phys_per_port`

指定与某个 SAS HBA 端口或 SAS 交换机端口关联的 PHY 设备数量。vdev_id 内部使用该值来判断设备连接到哪个 HBA 端口或交换机端口。默认值为 `4`。

### `-h`

打印用法摘要。

## 参考文献

vdev_id.conf(5)

2021 年 5 月 26 日
