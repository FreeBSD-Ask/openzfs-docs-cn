# 术语表

本表为全书术语翻译的唯一权威标准。翻译与校对时以此为准；新增术语或调整译法时，先更新本表（提交 PR 审核后生效），再用于正文。“保留英文”指不翻译，且大小写与现有译文保持一致。

## 核心术语对照

| 术语 | 译法 | 说明 |
| ---- | ---- | ---- |
| pool | 存储池 | |
| dataset | 数据集 | |
| filesystem（数据集类型） | 文件系统 | 与“文件系统”一般概念同形 |
| volume（数据集类型） | 卷 | |
| snapshot | 快照 | |
| clone | 克隆 | |
| vdev | 保留英文（小写） | 标题或首次出现可写作“虚拟设备（vdev）” |
| zvol | 保留英文（小写） | 上游命令输出中的 ZVOL 大写保持原样 |
| mirror | 镜像 | |
| stripe、striping | 条带、条带化 | |
| parity | 校验 | RAIDZ 语境 |
| redundancy | 冗余 | |
| scrub | 保留英文 | 描述扫描验证动作时可译“清洗”，全文统一 |
| resilver | 保留英文 | 泛指重建数据的动作时可译“重建”，全文统一 |
| TRIM | 保留英文 | |
| initialize | 初始化 | zpool initialize 子命令语境 |
| ARC、L2ARC、ZIL、SLOG、ZED、ZEDLET | 保留英文 | 大小写与现有译文一致 |
| feature flags | 特性标志 | |
| checksum | 校验和 | |
| compression | 压缩 | |
| deduplication、dedup | 去重 | |
| encryption | 加密 | |
| copies | 副本数 | 属性 `copies` 名保留英文 |
| checkpoint | 检查点 | |
| bookmark | 书签 | |
| hold | 保留（建议） | `zfs hold` 语境；ARC/引用计数语境的 holds 译"持有数"，按上下文区分 |
| enclosure | 机箱 | 磁盘机箱 |
| channel | 通道 | |
| switch | 交换机 | SAS 拓扑语境 |
| slot | 插槽 | 磁盘插槽语境统一用"插槽"（不写"槽位"） |
| spill block | spill 块（保留） | 与 `zfs.4` 现有译法一致，不译"溢出块" |
| property | 属性 | dataset property 译“数据集属性”，user property 译“用户属性” |
| quota | 配额 | |
| refquota | 引用配额（建议） | |
| reservation | 预留值 | |
| refreservation | 引用预留值（建议） | |
| send、receive | 发送、接收 | `zfs send/receive` 作为命令名时保留英文 |
| import、export | 导入、导出 | `zpool import/export` 作为命令名时保留英文 |
| attach、detach | 附加、分离 | |
| mount、unmount/umount | 挂载、卸载 | |
| share | 共享 | |
| delegation | 委托（建议） | `zfs allow` 委托管理语境 |
| key | 密钥 | encryption root 暂译“加密根”（建议） |
| raw | 保留英文 | `zfs send -w` 语境不译；形容词可用“原始的” |
| block cloning | 块克隆 | |
| special vdev | special vdev（保留） | 首次出现可写作“特殊 vdev（special vdev）” |
| Root on ZFS | 以 ZFS 为根文件系统 | 页面标题统一句式“构建以 ZFS 为根文件系统的 <发行版>” |
| distribution | 发行版 | |
| repository | 仓库 | 不用“存储库” |
| upstream | 上游 | |
| man page | 手册页 | |
| subcommand | 子命令 | |
| OpenZFS、ZFS | 保留英文 | `zpool`、`zfs`、`zdb`、`ztest`、`zinject`、`zstream`、`zed`、`vdev_id` 等命令名保留英文小写 |
| 消息 ID（ZFS-8000-XX） | 保留原样 | 字符、顺序不得改动 |
| 拷贝 | 复制 | 禁止使用“拷贝”；属性 `copies` 语境译“副本数” |
| shell | shell | 不译“壳”、“外壳” |

## 一般约定

* 第二人称一律使用“你”而非“您”。
* 避免滥用“已”字：“XX 已新增”应为“新增 XX”，“已修复”应为“修复完成”。
* 遇到本表未收录的术语，先检索现有译文的用法保持一致，并提交 PR 将其收录进本表；禁止各页自行其是。
* FreeBSD 特有概念（Ports、Jail、pkgbase 等）不适用于本项目，照抄英文原名即可。
