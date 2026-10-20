# 编辑日志

* 2026.10.20
  * 完成 man 页全量翻译（源：openzfs/zfs master 7c3d85aa，2026-10-18），新增 83 页：
    * man(1)：dbufstat、zarcsummary
    * man(5)：vdev_id.conf
    * man(7)：dracut.zfs、vdevprops、zfsconcepts、zfsprops、zpool-features、zpoolconcepts、zpoolprops
    * man(8)：fsck.zfs、mount.zfs、pam_zfs_key、vdev_id、zdb、zed、zfs、zfs-allow、zfs-bookmark、zfs-clone、zfs-create、zfs-destroy、zfs-diff、zfs-hold、zfs-jail、zfs-list、zfs-load-key、zfs-mount、zfs-mount-generator、zfs-program、zfs-project、zfs-promote、zfs-receive、zfs-rename、zfs-rewrite、zfs-rollback、zfs-send、zfs-set、zfs-share、zfs-snapshot、zfs-upgrade、zfs-userspace、zfs-wait、zfs-zone、zfs_ids_to_path、zfs_prepare_disk、zgenhostid、zinject、zpool、zpool-add、zpool-attach、zpool-checkpoint、zpool-clear、zpool-condense、zpool-create、zpool-ddtprune、zpool-destroy、zpool-detach、zpool-events、zpool-export、zpool-get、zpool-history、zpool-import、zpool-initialize、zpool-iostat、zpool-labelclear、zpool-list、zpool-offline、zpool-prefetch、zpool-reguid、zpool-remove、zpool-reopen、zpool-replace、zpool-resilver、zpool-scrub、zpool-split、zpool-status、zpool-sync、zpool-trim、zpool-upgrade、zpool-wait、zpool_influxdb、zstream
  * man(8) 同步补齐 16 个历史别名说明：zfs-change-key、zfs-get、zfs-groupspace、zfs-inherit、zfs-projectspace、zfs-recv、zfs-redact、zfs-release、zfs-unallow、zfs-unjail、zfs-unload-key、zfs-unmount、zfs-unzone、zpool-online、zpool-set、zstreamdump
  * 完成全书正文逐段校对（C1–C10）：msg 15 页、基础概念 6 页、Debian 6 页、Ubuntu 6 页、Alpine/Arch/Fedora/FreeBSD 7 页、NixOS/openSUSE/RHEL/Slackware 9 页、Gentoo/开发资源/License 6 页、项目与社区 10 页、性能调优 6 页、man(1) 8 页、man(4) 2 页
  * 补译 Debian、Ubuntu、NixOS、openSUSE 各页缺失的“支持”“贡献”两节；修正 Ubuntu 22.04 树莓派页版本错配的下载链接、openSUSE Tumbleweed 页包名与路径错误、RHEL 页代码块内被误译的示例对话
  * 基础概念（Basic Concepts）按上游 master `0c1de93ff4a07394e78cfe24d9f5b67f11147f0f`（2026-10-06）重组为“写时复制 + 存储池结构 / 数据集 / 数据存储 / 操作”五板块共 30 页，新增译 10 页：原生加密、数据集与属性、发送与接收、更改存储池布局、启动时的存储池，以及五个板块的概述页；`SUMMARY.md`“基础概念”分组登记 30 页，与 `Basic-Concepts/` 下实体文件一一对应
  * 修复基础概念重组后未同步的站内相对链接缺陷 12 处（含 `Copy-on-write.md` 上跳层级错误、`Pool-Structure` 两页图片路径、`ArchLinux/index.md` 邮件列表链接、`man/8/zfs-create.8.md` FAQ 链接），并把 `Snapshots-and-Clones.md` 两处指向英文原站的链接改为站内中文页
  * 新增站内相对链接校验脚本 `script/link-audit.py`（本地工具，按 `.gitignore` 不入库），纳入批次复核流程
  * 基础概念 30 页完成 6 路并发审校（批次 BC1–BC6，约 131 处修改）：修正事实性错误 5 处（快照定时销毁条件、zvol 特性主体、volmode `dev` 取值含义、`zdb -S` 输出含义、VDEV“单设备”类型与故障处理语义反转）；`Operations/Troubleshooting.md` 经判定上游已整页重写，按 master（`0c1de93`）整页重译（48 行 → 193 行，11 节逐一对应）；`Pool-Structure/RAIDZ.md` 补译“读取”“一块慢盘”“扩容”三节，`Feature-Flags.md` 补译“特性状态”“只读兼容”“兼容性特性集”“升级存储池”四节正文与“`zfs upgrade` 是另一回事”整节
  * 术语表新增 24 条：txg（事务组）、leaf vdev（叶子 vdev）、thorough scrub（彻底 scrub）、error scrub（错误 scrub）、thin provisioning（精简置备）、thick provisioning（厚置备）、slop space（余量空间）、pin（钉住）、consumer（使用方）、replication stream package（复制流包）、usershare（用户共享/USERSHARE）、allowlist（许可名单）、BRT（块引用表）、livelist（保留）、condense（保留英文）、objset（对象集）、redup/reduplicated（反去重）、gang block（gang 块）、logical birth time（逻辑出生时间）、tree quota（目录树配额）、redacted（遮蔽数据集）、overlay（overlay 挂载）、quiescing（静止）、bit rot（保留英文）、deadman（deadman 定时器）、allocation class（分配类）
  * `AGENTS.md` 同步：基础概念结构差异标记为已同步并记录板块版本（master `0c1de93`）；代理派发纪律改为“允许并发、单轮不超过 10 路”；新增“占位符保持上游英文原样”编写规范
  * 重建 `Pool-Structure/Feature-Flags.md` 特性矩阵表：解析上游当日生成的矩阵页，转为 54 行 × 24 列 Markdown 表（特性标志、只读兼容、22 个实现/版本列），版本列更新至 2.2.11/2.3.9/2.4.4/master，修正 `org.zfsonlinux:allocation_classes` 等行数据，edonr 脚注改为页内“注释”节，“最后更新时间”更新为 2026-10-20T03:24:04Z
  * 全仓术语归并 45 处（13 个文件）：boot pool 统一为“启动池”、thin provisioning 统一为“精简置备”、allocation class 统一为“分配类”、sit out 统一为“暂停参与”；四组旧译法经 grep 复核归零
  * `Operations/Troubleshooting.md` 的 vdev 状态、计数器、`failmode`、事件类四组枚举（14 处）由加粗冒号独立段统一为列表项，与全仓定义列表体例（清单用 H3、短枚举用列表）对齐
  * 按用户裁决处理三项结构遗留：`Pool-Structure/RAIDZ.md` 移除六个校验开销小节与六张静态图，跟随上游改为指向在线校验开销表的链接；复核后移除三个历史页面（`Performance-Tuning/ModuleParameters.md` 占位页、`Project-and-Community/index.md`“管理文档”与 `System_Administration.md` wiki 快照译文，上游已分别删除或从未收录，核心内容已被基础概念新页覆盖），相关 3 处正文链接改指 `zfs(4)`；`SUMMARY.md`“项目与社区”分组收录上游 toctree 的三条外链（问题跟踪器、发布版本、路线图）
  * 按用户裁决“必须与上游一致”完成结构终核：移除 Gentoo 三页并在 `SUMMARY.md` 按上游 toctree 改为 Gentoo Wiki 外链；移除本地特有的 `Performance-Tuning/Async-Write.md`（内容已由 `man/4/zfs.4.md` 的相关参数条目与“ZFS I/O 调度器”页覆盖）；`Git 和 GitHub 入门指南` 由 `Project-and-Community/` 迁至 `DeveloperResources/` 对齐上游目录；`GettingStarted.md` 按上游修正——删除残留的 Aaron Toponce 推荐句，补译“首次使用者应从基础概念的写时复制与 VDEV 读起”一段
  * 经上游树映射比对确认不再存在的差异：上游根级 `Fedora.rst`/`RHEL and CentOS.rst` 为 `:orphan:` 跳转页、两个板块 index 无正文，本地均不设对应页（`SUMMARY.md` 分组即 toctree）；msg 15 页与上游一致
  * 表格管道符按 CJK 显示宽度全量对齐（6 张表：校验和两表、块克隆、共享数据集、缓存、特性矩阵），分隔行统一左对齐；新增本地工具 `script/align-table.py`，特性矩阵生成脚本输出已同步为对齐格式
  * 完成 man 页 93 页终核（批次 M1–M6，逐段对照 openzfs/zfs `7c3d85aa` troff）：修复 `zpool-features` 特性 GUID 错拼 2 处（`org.zfsonlinear`→`org.zfsonlinux`）、`zfs-send` 概述漏 `-U`、`zpool-iostat`/`zpool-list` 的 `-T u|d` 顺序、`zpoolconcepts` draid 标题缺 `[parity]` 段、`zpool-create` 多余的“选项”节（上游无 OPTIONS 节）、`zpool-condense` 长选项单横线→双横线、`zfs.4` 六处段落软换行、三页滚动快照示例快照名补空格、占位符篡改还原约 30 处；机器校验全量（93 页与上游清单一一对应、属性/选项计数吻合、lint 0 错误、链接 0 悬空）；上游自身缺陷 5 处记录于校对工作单待反馈
  * 术语表收录终核批次候选 11 条（rotational=机械盘并全仓统一、hold、enclosure、channel、switch、slot、spill block、demand、DMU buffer cache 等），`man/4/zfs.4.md` 六处“轮替盘/轮替 vdev”误译统一为“机械盘”
  * 新增引号规则（用户指示）：禁止使用日式半角引号（直角引号「」），一律改用“”或‘’；全仓排查正文内容页零残留，`AGENTS.md`、`CHANGELOG.md`、校对工作单三个元文档共 57 对已统一替换，规则写入 `AGENTS.md` 引号规范
  * 翻译进度与目录复核：SUMMARY 191 条（内链 187、外链 4）与实体文件双向核对零缺漏，187 页 H1 与登记标题全量一致；进度快照固化至 `AGENTS.md`「翻译进度快照」（板块 × 页数 × 源基线 × 校对批次）与 `README.md`「翻译进度」节，并更新“当前翻译 git 版本”与 man 页基线表述，便于下次上游同步时接手
* 2026.10.18
  * 新增 AGENTS.md（AI 助手与贡献者工作指南，适配本项目）
  * 修复 `.github/.markdownlint.json` 无效语法（MD004 配置对象错位、`siblings_only` 类型错误、末尾逗号），此前 markdown-lint2 工作流无法解析该配置
  * 新增术语表 `shu-yu-biao.md` 并收录进目录，作为全书术语唯一权威标准
  * 确立 man 页版本基线：既有 10 页基于 openzfs/zfs@b481a8bb（2026-03-13）；本次校对与全量翻译以 zfs master（7c3d85aa，2026-10）为目标版本
  * 启动全书逐段校对与 man 页全量翻译（工作单见 `script/校对工作单.md`）
* 2026.3.14
  * 新增“ZFS 消息”
  * 新增“用户命令（User Commands (1)）”
  * 当前版本 <https://github.com/openzfs/openzfs-docs/commit/259438bd5f12278765eed197237be9d6ab9d5d27>
* 2026.2.13
  * 新增“OpenZFS 事务延迟”
  * 新增“ZFS I/O（ZIO）调度器”
  * 新增“Async Write I/O 调度”
  * 新增“基础概念”
  * 当前版本 [93ac90cde77c8bd1ac92fb67c075d008110ddb36](https://github.com/openzfs/openzfs-docs/commit/93ac90cde77c8bd1ac92fb67c075d008110ddb36)
* 2026.2.5
  * 新增“硬件”
  * 新增“模块参数”（为空，不具有翻译意义）
  * 新增“工作负载调优”
* 2026.1.28
  * 新增“开发资源”
* 2026.1.26
  * 新增“Ubuntu”
  * 新增“OpenZFS 系统管理”
* 2026.1.25
  * 新增“NixOS”
  * 新增“openSUSE”
  * 新增“RHEL”
  * 新增“Slackware”
* 2026.1.24
  * 新增“Debian”
  * 新增“Fedora”
  * 新增“FreeBSD”
  * 新增“Gentoo”
* 2026.1.23
  * 项目开始，当前版本 [5ad3a5ff6227a499f576d886592692fd59b7d6c5](https://github.com/openzfs/openzfs-docs/commit/5ad3a5ff6227a499f576d886592692fd59b7d6c5)
  * 新增“Alpine Linux”
  * 新增“Arch Linux”
