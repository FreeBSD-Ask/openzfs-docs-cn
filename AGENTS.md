# AGENTS.md

本文件为 AI 助手与贡献者提供本仓库的工作指南。

## 仓库概览

这是 OpenZFS 官方文档（OpenZFS Documentation）的中文翻译项目，由 FreeBSD 中文社区维护。基于 GitBook 格式，由 GitBook 平台自动构建和部署，无需本地构建步骤。

* 原项目在线浏览地址：<https://openzfs.github.io/openzfs-docs/index.html>
* 原项目仓库：<https://github.com/openzfs/openzfs-docs>
* 本仓库：<https://github.com/FreeBSD-Ask/openzfs-docs-cn>

源内容为 Markdown 文件。注意：**上游 openzfs-docs 实际使用 Sphinx（rst）格式**，源文件位于其 `docs/` 目录下；本仓库将其转写为 GitBook 格式的 Markdown。上游文件与目录名普遍含空格（如 `Basic Concepts`、`Root on ZFS.rst`），但不含英文冒号，Windows 下直接 `git clone` 即可，无需下载 zip 压缩包。

**man 手册页不在上游 openzfs-docs 仓库中**：`man/` 目录内容译自 openzfs/zfs 仓库（<https://github.com/openzfs/zfs>）的 `man/man1/`、`man/man4/` 等目录（troff 格式手册页）。`msg/` 目录内容译自上游 openzfs-docs 的 `docs/msg/<消息 ID>/index.rst`。

## 版本与同步

上游仓库：<https://github.com/openzfs/openzfs-docs>（分支 master）。

当前翻译 git 版本：259438bd5f12278765eed197237be9d6ab9d5d27（CHANGELOG 2026.3.14 条目）。

**文档正文板块版本**：全仓正文仍以 `259438bd` 为判定基准，但“基础概念”板块已于 2026-10-20 整体同步至上游 master `0c1de93ff4a07394e78cfe24d9f5b67f11147f0f`（2026-10-06）：该板块按 master 重组为写时复制加四个子板块，共 30 页，旧版平铺页面对应的译文已按 master 原文重译或校订。其余板块的同步基点仍为 `259438bd`。

**man 页版本基线**：`man/` 译自 openzfs/zfs 仓库，版本独立于 openzfs-docs 单独记录。既有 10 页 man 译文基于 openzfs/zfs@b481a8bbbf32c26b014518d7c72979c557205918（2026-03-13，与译文提交日 2026-03-14 对齐）；此后上游 master 对 man/ 有较大改动（截至 2026-10-18 共 92 个文件，+2527/-1589 行）。校对既有 man 译文时，以其提交时基线（b481a8bb）的 troff 原文为翻译错误判定基准，同时向当前 master 同步版本差异；新增 man 页一律以 master 为源。man 源版本变化时在 CHANGELOG.md 记录对应 zfs commit。

同步上游或新增翻译后，需同步更新 CHANGELOG.md（记录日期、新增内容与上游 commit）及本文件中的“当前翻译 git 版本”。

### 与上游的已知结构差异（截至 2026-10-20）

上游自同步基点以来结构有较大调整。已同步与仍待同步的项目如下：

**已同步**

* 基础概念（Basic Concepts）按上游 master 重组为“写时复制 + 四个子板块”，共 30 页：写时复制（Copy-on-write）；存储池结构（Pool Structure：VDEVs、RAIDZ、dRAID Howto、Caching、Special vdev、Changing Pool Layout、Feature Flags）；数据集（Datasets：Datasets and Properties、ZVOLs、Snapshots and Clones、Quotas and Reservations、ACLs）；数据存储（Data Storage：Checksums、Compression、Deduplication、Block Cloning、Encryption）；操作（Operations：Send and Receive、Scrub and Resilver、TRIM、Sharing、Delegated Administration、Boot Process、Troubleshooting）。五个板块各设 index 概述页，目录见 `SUMMARY.md`“基础概念”分组。
* Debian 新增页面“Debian GNU Linux initrd documentation”（`Debian/Debian-GNU-Linux-initrd-documentation.md`）。
* 项目与社区（Project and Community）新增 FAQ hole birth 页面（`Project-and-Community/FAQ-hole-birth.md`）；板块概述页对应本地 `Project-and-Community.md`（SUMMARY 条目标题“概述”）。
* 开发资源（Developer Resources）板块概述页上游仅含 toctree 与一条外链，已由 `SUMMARY.md`“开发资源”分组与 `Project-and-Community/Developer_resources.md` 覆盖，不另建页面。
* man 页：openzfs/zfs master 的 man1/man4/man5/man7/man8 共 93 页已全部译出并登记，含 `zfs(8)`、`zpool(8)`、`zfsprops(7)`、`zfsconcepts(7)` 等大部头页面。

* “项目与社区”的 `SUMMARY.md` 分组收录上游 toctree 的三条外链：问题跟踪器、发布版本、路线图（`github.com/openzfs/zfs`）。
* 上游已移除的三个历史页面已复核后移除（2026-10-20）：`Admin Documentation`（本地“管理文档”）、`System Administration`（本地 wiki 快照译文，核心内容已被基础概念新页覆盖）、`Module Parameters`（本地占位页，模块参数已并入 man 页；相关 3 处正文链接改指 `zfs(4)`）。本地 `Project-and-Community/Developer_resources.md` 对应上游“开发资源”板块的外链资源，保留。

**仍待定夺**

* Gentoo：**已处理**（2026-10-20 裁决“必须与上游一致”）——本地三页已移除，`SUMMARY.md`“安装指引”按上游 toctree 改为 Gentoo Wiki 外链。
* 上游根级 `Getting Started/Fedora.rst` 与 `RHEL and CentOS.rst` 为 `:orphan:` 旧地址跳转页（无导航价值），本地不设对应页；上游两个板块 index（性能调优、开发资源）仅含 toctree 无正文，由 `SUMMARY.md` 分组承担，不另建空页。

## 内容架构

### 核心文件

* **`SUMMARY.md`** — 全书唯一数据源，定义完整目录结构和导航树。GitBook 用它来生成侧边栏。**第一行 `# Table of contents` 绝对不能变更**，否则 GitBook 同步失效。
* **`mu-lu.md`** — 由 `mulu.yml` CI 工作流从 `SUMMARY.md` 自动复制生成（首行改为 `# 目录`），**不要手动编辑**。
* **术语表 `shu-yu-biao.md`** — 全书术语翻译的唯一权威标准（已收录进 SUMMARY.md），翻译与校对以它为准；新增术语先更新该表，再用于译文。
* **`CHANGELOG.md`** — 编辑日志，记录翻译进度和同步上游的 commit。

### 目录结构

* 各发行版目录沿用上游英文目录名（空格改连字符或直接移除）：`AlpineLinux/`、`ArchLinux/`、`Debian/`、`Fedora/`、`NixOS/`、`openSUSE/`、`RHEL/`、`Slackware/`、`Ubuntu/`；Gentoo 不再有本地页面，`SUMMARY.md` 中为指向 Gentoo Wiki 的外链条目
* 内容板块目录：`Basic-Concepts/`、`Performance-Tuning/`、`Project-and-Community/`、`DeveloperResources/`（历史命名未带连字符，保持不变）
* `man/<节号>/<命令名>.<节号>.md` — 手册页，如 `man/1/cstyle.1.md`（译自 zfs 仓库 `man/man1/cstyle.1`）
* `msg/<消息 ID>.md` — ZFS 消息页，如 `msg/ZFS-8000-14.md`（译自上游 `docs/msg/ZFS-8000-14/index.rst`）
* `.gitbook/assets/` — GitBook 静态资源（logo、插图等），正文中用相对链接引用（如 `../.gitbook/assets/draid-resilver-hours.png`）

### 文件命名约束

* 新建文件与目录时，沿用上游英文原名：空格删除或改为连字符（如 `Basic Concepts` → `Basic-Concepts`），并与同目录现有文件的命名风格保持一致。
* 文件名中不得包含中文、空格或英文冒号 `:`，必须兼容 Windows 操作系统对文件名的要求。
* 上游内容页面不使用拼音命名（上游文件名本身为英文，保留原名便于与上游对照）；项目内部文件沿用既有拼音命名惯例（如 `mu-lu.md`、`shu-yu-biao.md`）。

## 标题管理（关键约束）

`sync-headers.yml` 工作流会在每次 push 时自动将 `SUMMARY.md` 中的标题同步到对应 `.md` 文件的 H1。**这意味着直接编辑 `.md` 文件的 `# 标题` 会被 CI 覆盖。** 修改页面标题时，只改 `SUMMARY.md` 中对应的 `* [标题](路径)` 条目即可。

## CI/CD 工作流

所有工作流位于 `.github/workflows/`：

| 工作流 | 触发条件 | 说明 |
| ------ | -------- | ---- |
| `sync-headers.yml` | push；`mulu.yml` 完成后 | 从 SUMMARY.md 同步一级标题到各 .md 文件，有变更自动提交 |
| `mulu.yml` | SUMMARY.md 变更时 push；手动 | 复制 SUMMARY.md → mu-lu.md（首行改为 `# 目录`），自动提交 |
| `file-name-check.yml` | push（.md 变更） | 校验 SUMMARY.md 引用的文件是否存在，缺失则自动开 issue（标签 summary-check） |
| `check-images.yml` | push（.gitbook/assets 变更）；手动 | 运行 `.github/scripts/check_images.py` 校验图片引用与 `.gitbook/assets/` 的对应关系，生成报告并开 issue |
| `Auto-Assign.yml` | issue、PR 打开时 | 自动指派维护者（配置见 `.github/auto_assign.yml`） |
| `links.yml` | 每月 15 日 UTC 18:00；手动 | lychee 死链检查，配置见 `.github/lychee.toml` |
| `create-pdf.yml` | 每周日 UTC 15:30；手动 | 导出 PDF |
| `link-arch.yml` | 手动 | 运行 `.github/scripts/link.py` 将正文外链替换为存档服务链接，自动创建 PR |
| `markdown-lint2.yml` | 手动 | markdownlint 检查（规则见 `.github/.markdownlint.json`），失败时自动修复并创建格式化 PR |
| `md-padding.yml` | 手动 | 自动在中英文、中文与数字之间添加空格 |
| `AutoCorrect.yml` | 手动 | 自动修正常见中文笔误与格式问题 |

## 编写规范

### 格式

* **命令行：** 代码块内容保持上游原样，不增删 `sudo`、提示符（`#`、`$`）与换行；示例输出沿用上游提示符。仅翻译注释。
* **提示块：** tip/important/note/warning 使用 `>` 引用块，首行加粗关键词（**提示**、**注意**、**警告**、**重要**），正文另起一行；同一文件内风格保持一致。
* **代码块：** 语言标记沿用上游（`sh`、`ini` 等），无法判断的用 ` ```sh ` 兜底；禁止使用 text 作为代码块标记，不窜改既有的 ` ```ini ` 标记。
* **表格：** 分隔行与内容行的管道符位置对齐，管道符两侧各留一个空格；对齐方式与现有译文保持一致（现状多为居中），同一表格内保持一致。
* **禁止 HTML：** 本项目不支持任何 HTML 语法。
* **路径、命令与参数：** 路径（如 `/etc/fstab`、`/usr/local/etc/`）、命令、选项、可调参数等一律使用反引号包裹；不带选项和参数的裸命令（如 mv、cp）一般不加反引号。不要混合使用 `*` 和 `` ` ``。
* **转义字符：** 含转义字符 `\` 的元素整体用反引号包裹，不在正文中裸露转义字符；逐个手动修改，禁止批量替换。
* **避免滥用“已”字：** 如“XX 已新增”应改为“新增 XX”；“已修复”应改为“修复完成”。禁止机械替换。
* **禁止篡改：** 不要篡改软件版本号、用户名、邮箱、URL、IP 地址、带圈数字（如 ①②③）、消息 ID（如 ZFS-8000-14），确保其位置、数量与上游原文一致。
* **占位符：** 路径、URI 与命令示例中的占位符（如 `<pool>`、`<name>`、`<vdevs...>`、`file:///absolute/path`）保持上游英文原样，不中文化；仅正文中不构成路径或命令的叙述性说明才可译作中文。
* **避免页面交叉引用：** 正文不写“参见上一节”这类模糊指代；跨页链接优先使用相对链接指向站内中文页面，对应中文页面尚未翻译时可链接英文原站对应页面（如 <https://openzfs.github.io/openzfs-docs/Basic%20Concepts/RAIDZ.html>），与现有译文惯例一致。
* **代码块注释翻译：** 代码块（` ``` ` 围栏）内的英文注释必须翻译为中文（如 shell 注释 `# This is a comment` → `# 这是一个注释`）。只翻译注释部分，不修改实际命令或代码，保持代码结构和格式不变。
* **引号规范：** 正文引号使用“”（中文双引号）或‘’（单引号），必须成对且方向正确（开引号在左、闭引号在右）；禁止直引号（`"`、`'`）出现在正文（代码块、行内代码、markdown 链接标题语法、英文单词内的缩字符如 won’t 除外）；**禁止使用日式半角引号（直角引号「」），一律改用“”或‘’**（2026-10-20 用户新增规则，元文档与日志一并适用）。逐个手动修改，禁止机械替换。
* **禁止 rst 残留语法：** 上游为 rst 格式，转写时不得残留 rst 语法：行内交叉引用（`:doc:`、`:ref:`）、行尾 `__` 链接后缀、指令标记（`.. note::`）等必须转为等价 Markdown。必须使用标准 markdown 链接 `[文本](路径)` 指向真实位置。
* **禁止软换行：** 所有段落必须在同一行内完成，不得跨行拼接。
* **fstab 与配置文件内容：** 代码块内的文件内容（含 fstab 表头 `# Device Mountpoint FStype Options Dump Pass#`）保持英文原样，不翻译。

### 术语

术语翻译的权威标准见 **`shu-yu-biao.md`**（术语表），翻译与校对时必须遵循；本节仅列流程性约定。

* 第二人称一律使用“你”而非“您”。
* 遇到术语表未收录的术语，先检索现有译文的用法保持一致，并把新术语提交进术语表后再动笔，禁止各页自行其是。
* 常见违规示例（校对时重点排查）：存储库 → 仓库；“拷贝” → “复制”（属性 `copies` 语境译“副本数”）；“您” → “你”；“壳/外壳” → shell。

### CJK 空格

中英文、中文与数字之间必须加半角空格。文件和命令名用反引号括起来。`md-padding.yml` 和 `AutoCorrect.yml` 工作流会自动检测修复。

### 图片

在正文中插入图片使用 markdown 格式，图片文件存放于 `.gitbook/assets/`，用相对链接引用（如 `![分布式热备 resilver 耗时](../.gitbook/assets/draid-resilver-hours.png)`）。`check-images.yml` 会校验引用与实际文件的一致性。

## 翻译流程

1. 参考官方英文原文进行人工校对或补译
2. 提交 PR 到 main 分支

**自动提交节奏**：批量校对、批量翻译期间，每完成一个批次并复核后立即提交一次（高频小步提交），提交信息格式：`校对：<批次名> <简述>`、`man：<批次名> <简述>`、`同步：<内容> <简述>`。

**代理派发纪律**：允许并发派发后台子代理，单轮同时运行的数量不超过 10 个（2026-10-20 用户批准）。每个子代理只写自己的目标文件与自己的日志，**禁止修改 `SUMMARY.md`（由主会话统一登记）、禁止修改他人文件、禁止执行任何 git 操作**；主会话在各路完成并逐路复核后统一提交。中断的批次优先以新指令恢复原代理，无法恢复时再新开。

### 原文获取

* **文档正文：** 首选克隆上游仓库读取 `docs/<板块>/<页面>.rst` 源文件；也可通过 WebFetch 抓取已发布页面 `https://openzfs.github.io/openzfs-docs/<页面路径>.html`。
* **man 手册页：** 以 openzfs/zfs 仓库 `man/man1/`、`man/man4/` 等目录的 troff 原文为准（<https://github.com/openzfs/zfs>），上游 openzfs-docs 中没有 man 页。
* **ZFS 消息：** 以上游 `docs/msg/<消息 ID>/index.rst` 为准。

### rst → Markdown 转写要点

* 标题下划线（`===` 为 H1、`---` 为 H2）按层级转为 `#`、`##`、`###`；页面 H1 由 CI 从 SUMMARY.md 同步，本地只需保证 SUMMARY.md 条目正确。
* `.. note::`、`.. warning::`、`.. tip::`、`.. important::` 指令转为 `>` 引用块并加粗关键词。
* `.. code-block:: sh` 与 `::` 引出的字面块转为对应语言的围栏代码块。
* `:doc:`、`:ref:`、`:numref:` 等交叉引用转为 markdown 链接（站内相对链接或英文原站链接）。
* 行内字面量转为反引号。
* `:orphan:`、`__` 后缀、toctree 等构建指令一律丢弃，不得带入译文。

### man 页 troff → Markdown 转写要点

man 页译自 openzfs/zfs 仓库的 troff 手册页，目标文件为 `man/<节号>/<名称>.<节号>.md`，结构沿用现有 `man/1/ztest.1.md`、`man/1/zvol_wait.1.md` 的风格：

* `.SH NAME` → `## 名称`，定义行格式为 `` `命令` — 描述 ``；`.SH SYNOPSIS` → `## 概述`（` ```sh ` 代码块）；`.SH DESCRIPTION` → `## 说明`；`.SH OPTIONS` → `## 选项`；其余 `.SH` 按语义命名（`## 示例`、`## 环境变量`、`## 文件`、`## 参考文献` 等）。
* `.TP` 选项条目 → 三级标题 `` ### `-x`、`--xxx=` ``（H3，多形式用全角顿号连接），下接描述段落；默认值写作（默认值: `N`）。
* `.B`、`.I` 字体宏 → 命令与选项用反引号，强调用加粗；`.nf`/`.fi` 字面块 → 围栏代码块（`text` 以外的语言标记按内容判断，无法判断用 `sh` 兜底）。
* 概述代码块中的参数说明沿用现有译法（如 `[-v vdevs]` → `[-v vdev 的数量]`），命令与选项本身保留英文。
* 页脚日期与系统行（如 `2021 年 5 月 27 日  Debian`）置于文末，不设标题。
* 交叉引用（如 `zpool(8)`）保留原格式不加链接；引用其他手册页时保持 `名称(节号)` 形式。
* H1 为 `# 名称(节号)`，由 CI 从 SUMMARY.md 同步。

### 翻译校对工作流程（AI 助手）

对已翻译页面进行质量审校时，参考以下步骤：

1. **获取原文**：按“原文获取”一节取得对应页面的完整英文文本。存在 rst 源文件时，以 rst 源文件为基准；已发布网页仅作辅助。

2. **逐句对照**：将中文翻译与英文原文逐句比对，重点检查以下问题类别：

   | 问题类型 | 示例 |
   | -------- | ---- |
   | 事实性错误 | “large parts” 误译为“三个文件” |
   | 漏译 | 英文原版有但中文缺失的句子 |
   | 机翻腔/表达生硬 | “在阅读本章后，你将会收获” → “通过阅读本章，你将了解” |
   | 用词不当 | “独家优势”应为“主要优势”（原文 “particular strengths”） |
   | 版本过时 | 上游已更新的命令、选项、版本号未同步 |
   | 语法/文字错误 | 重复字词、“非常地”应为“非常” |
   | 欧化汉语、倒装句、后置句、偷换主语、不必要的被动句 | 自行联网制定标准，避免语法错误和非地道汉语表述 |

3. **提交修改**：
   * 基于 `main` 创建分支 `fix/<页面名>-translation`（新增翻译用 `feat/<页面名>`）
   * 仅提交修改的 `.md` 文件，不要包含无关文件
   * 提交信息格式：`fix: 修正 <页面名> 翻译错误及同步英文原版更新`
   * 用 `gh pr create` 创建 PR，目标分支为 `main`
   * PR 描述中列出每处修改及原因
   * 新增页面或同步上游后，更新 CHANGELOG.md

4. **注意事项**：
   * 不要修改 `# 标题`——会被 `sync-headers.yml` CI 覆盖
   * 保持术语一致性，以 `shu-yu-biao.md`（术语表）为准
   * 英文原文可能比翻译版本更新，内容差异应以英文原版为准
   * 添加新内容（如上游新增的段落）时，确保翻译风格与上下文一致
   * 禁止篡改带圈数字，如 ①②③ 等，确保其位置、数量与原文一致
   * 禁止篡改代码块（包括 shell 命令、配置文件内容、ini 段等），仅修改正文翻译与代码注释
   * 禁止篡改用户名、邮箱、URL、IP 地址等技术参数
   * 禁止篡改软件版本号与消息 ID
   * 以上游 openzfs-docs（文档正文、msg）与 openzfs/zfs（man 页）的最新 master 为唯一权威源；禁止以中文版已有翻译作为修改依据，避免错误沿袭

5. **逐句校对递归工作流**（核心约束）：
   * **逐行逐句子**遍历内容，检查逻辑一致性，联网复核后修改
   * **三轮 + 一轮复查**：完整执行三轮逐句校对，然后严格、完整地复查一轮；若仍有问题，继续执行三轮，递归直至无问题
   * **逐个修改**：修改时禁止机械修改、禁止批量；必须逐个手动修改，禁止使用软件工具批量替换或批量逐个复核
   * **修改前后复核**：每次修改前确认问题真实存在、修改后确认改动准确且未引入新错误
   * **不复查旧错**：不得复查以前已经完成三轮的错误；每轮查询内容必须是新的（若与之前的复查重复则跳过、不改，只看是否有新增内容）
   * **联网复查**：对于不存在的实际访问查询（如失效链接、版本号、API 端点），需联网复查三次后修改
   * **禁止绕过审查**：不得以任何方式搜索、批量、绕过逐句子审查流程

## 与上游结构同步工作流

当中英文版本页面结构出现差异（上游新增页面、重组板块、删除页面）时，按本工作流处理：

1. **获取上游结构**：`git clone --depth 1 https://github.com/openzfs/openzfs-docs`（或更新已有克隆），列出 `docs/` 下的 rst 文件树；man 页对照 openzfs/zfs 仓库 `man/` 目录。
2. **对比差异**：将上游 rst 文件树与本地 `SUMMARY.md` 逐条对比，列出新增、删除、移动、改名的页面。已知待同步差异见“版本与同步”一节。
3. **补译新页面**：
   * 按命名规则新建 `.md` 文件并翻译，遵循术语对照表，第二人称用“你”，vdev、zvol、scrub 等保留英文
   * 在 `SUMMARY.md` 对应位置插入条目（保持 `* [标题](路径)` 格式，第一行 `# Table of contents` 不动）
   * 页面 H1 交给 CI 同步，不要手写
   * 在 CHANGELOG.md 记录新增内容，并更新本文件“当前翻译 git 版本”
4. **处理重组与改名**：上游移动、改名页面时，同步调整本地目录与文件名（用 `git mv` 保留历史），修复所有受影响的相对链接；被上游删除的页面，先在本文件或 CHANGELOG 中记录再决定去留，不要静默删除。
5. **验证**：
   * 运行 markdownlint 检查（见下节）
   * 核对 SUMMARY.md 中每个条目对应的文件都存在（`file-name-check.yml` 会在 push 后自动校验并开 issue）
   * 核对图片引用（`check-images.yml` 会自动校验并开 issue）
   * 重新对比上游文件树，确认无遗漏

## Lint 配置

* **markdownlint**（`.github/.markdownlint.json`）：本地已安装 `markdownlint-cli2 v0.22.1`（基于 `markdownlint v0.40.0`），可在本地直接运行检查与修复
  * **本地运行命令**（在仓库根目录执行）：

    ```sh
    # 检查全部中文 .md（排除 .github/、.gitbook/、node_modules/）
    markdownlint-cli2 "**/*.md" "!.github/**" "!.gitbook/**" "!node_modules/**" --config .github/.markdownlint.json

    # 自动修复可修复的问题
    markdownlint-cli2 "**/*.md" "!.github/**" "!.gitbook/**" "!node_modules/**" --config .github/.markdownlint.json --fix
    ```

  * **与 FreeBSD 手册项目的差异**：本仓库未启用 MD060 表格列风格规则，表格分隔行无需按 CJK 显示宽度对齐；MD012（多余空行）、MD013（行长）、MD029（列表编号）、MD033（内联 HTML）、MD034（裸 URL）、MD040（代码块语言）等均关闭
  * **需注意的启用规则**：
    * MD004、MD049、MD050：无序列表使用 `*`（不用 `-`），强调使用 `*`（不用 `_`）
    * MD046：代码块必须使用围栏（` ``` `），不得使用缩进式代码块
    * MD024：`siblings_only`，允许不同小节下出现重复标题，同一父级下不得重复
    * MD007：无序列表嵌套缩进保持 2 空格
    * MD041：文件首行必须是 H1
    * MD047：文件末尾保留一个空行
    * MD055、MD056：表格管道符风格一致、各行列数一致，末尾缺单元格补 `| |`
* **textlint**：本项目未配置（仓库无 `.textlintrc`），中英文空格由 `md-padding.yml` 与 `AutoCorrect.yml` 处理
* **lychee**（`.github/lychee.toml`）：6 线程、30 并发、30 秒超时、最多 3 次重试、Chrome UA；接受状态码 200、429、403、418、402；排除 `.github/` 路径、私有 IP、`localhost` 及含 `$` 的占位链接；启用 `include_verbatim`（代码块内链接也检查）
