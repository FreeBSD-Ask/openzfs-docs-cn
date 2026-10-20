# OpenZFS 中文文档

![OpenZFS](.gitbook/assets/logo_main.png)

欢迎来到 OpenZFS 文档。本资源为使用（或贡献于）OpenZFS 项目的用户和开发者提供文档。新用户或系统管理员应参考其偏好平台的文档以开始使用。

| 入门 | 项目与社区 | 开发者资源 |
| :------------------: | :---------------------: | :-----------------------------: |
| 如何在你挚爱的平台上使用 OpenZFS         | 关于项目以及贡献方法           | 讨论 OpenZFS 实现的技术文档               |

* 错误追踪：<https://github.com/openzfs/zfs/issues>
* 发行产物：<https://github.com/openzfs/zfs/releases>
* 路线图：<https://github.com/openzfs/zfs/milestones>

## FreeBSD 中文社区项目：OpenZFS 中文文档

原项目在线浏览地址：[OpenZFS Documentation](https://openzfs.github.io/openzfs-docs/index.html)

原项目 GitHub 地址：<https://github.com/openzfs/openzfs-docs>

欢迎使用 OpenZFS 中文文档。本项目旨在为使用或参与 OpenZFS 项目的用户和开发者提供中文文档。新用户或系统管理员应参考其所使用平台的文档以便入门。

## 许可证

[OpenZFS Documentation](https://openzfs.github.io/openzfs-docs/index.html) 原文采用 CC BY 3.0 授权，因此本项目采用 BSD 和 CC BY 3.0 双许可证进行授权，读者可以选择任一许可证。

## 翻译进度（2026-10-20）

本项目已完成上游文档全部内容页与 openzfs/zfs 全部 man 手册页的中文翻译，并完成逐页校对：

| 板块 | 页数 | 源版本 |
| ---- | ---- | ---- |
| 基础概念 | 30 | openzfs-docs master（2026-10-06，`0c1de93`） |
| 手册页 man(1/4/5/7/8) | 93 | openzfs/zfs master（2026-10-18，`7c3d85aa`） |
| ZFS 消息 | 15 | 基线（2026-03-14，`259438bd`） |
| 安装指引（10 个发行版） | 30 | 基线（结构已对齐上游 master） |
| 项目与社区 / 开发资源 / 性能调优 / 许可证 | 14 | master（结构已对齐） |

* 目录以 [SUMMARY.md](SUMMARY.md) 为准，共 187 个内容页（另有 4 条上游外链）。
* 全部页面经过至少一轮逐段校对：基础概念经六路并发审校，man 页经两轮校对（C 批次 + M1–M6 终核，逐段对照 troff 原文）。
* 贡献者与维护者更新上游时，请先阅读 [AGENTS.md](AGENTS.md) 的“版本与同步”与“翻译进度快照”两节，完成后更新 [CHANGELOG.md](CHANGELOG.md) 与快照表。术语以 [术语表](shu-yu-biao.md) 为唯一权威标准。
