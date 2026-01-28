# 开发资源

## 联系方式

* [ZFS 专家](https://openzfs.org/wiki/Contributors)
* [邮件列表](https://openzfs.org/wiki/Mailing_list)
* IRC：[#openzfs](ircs://irc.libera.chat/#openzfs) 于 [Libera.chat](https://libera.chat/)
* Twitter：[@openzfs](https://twitter.com/OpenZFS)
* [OpenZFS 办公时间](https://openzfs.org/wiki/OpenZFS_Office_Hours)：轮流由负责人 / 所有者主持
* 指向其他邮件列表和仓库的指引？

## 进行中的工作

* 测试框架
* 我们的目标之一是 [减少代码差异](https://openzfs.org/wiki/Reduce_code_differences)。

  * [平台代码差异](https://openzfs.org/wiki/Platform_code_differences) 列表
* [项目](https://openzfs.org/wiki/Projects)

  * [ZFS Channel Programs](https://openzfs.org/wiki/Projects/ZFS_Channel_Programs)

## 技术实现文档

* 源代码链接位于 [发行版](https://openzfs.org/wiki/Distributions) 页面
* 关于通用 OpenZFS 概念的架构 / 高层级文档
  * [zfs send](https://openzfs.org/wiki/Documentation/ZfsSend)
  * [管理命令](https://openzfs.org/wiki/Documentation/Administrative_Commands)（例如 `zfs snapshot -r pool/fs@snap`）
  * [zfs I/O](https://openzfs.org/wiki/Documentation/ZFS_I/O)
* [FreeBSD 书籍](http://www.amazon.com/Design-Implementation-FreeBSD-Operating-System/dp/0321968972) 有一章精彩地介绍了 ZFS——这可能是新开发者可获得的最佳概览。

### 其他网站上的资料

[ZFS On-Disk Specification – Draft](http://www.giis.co.in/Zfs_ondiskformat.pdf)（ZFSOnDiskFormat.pdf，Sun Microsystems, Inc., 2006-08）

* 有时被称为 *ZFS On-Disk Format* 文档
* 已过时，但“变化并不算大，且向后兼容性决定了它仍然可作为知识基础使用”；“这是我们所拥有的最接近全面概览的资料——而且仍然大体适用，只是没有覆盖较新的内容……例如 SA”。

[使用 mdb 和 zdb 检视 ZFS On-Disk Format](http://www.youtube.com/watch?v=BIxVSqUELNc)（2008-06-28）

* Max Bruning 在布拉格的 OpenSolaris Developer Conference 上的一场 43 分钟视频演讲。

[源代码导览](http://java.net/projects/solaris-zfs/pages/Sourcetour)（[存档](http://web.archive.org/web/20130316073014/http://hub.opensolaris.org/bin/view/Community+Group+zfs/source)）介绍了 ZFS 中的各个子组件。

### 关于 ZFS 特性的博客文章

自适应替换缓存（Adaptive Replacement Cache），也称为可调节替换缓存（Adjustable Replacement Cache，ARC）

* [对 ZFS 读缓存的一些见解——或者：ARC - c0t0d0s0.org](http://www.c0t0d0s0.org/archives/5329-Some-insight-into-the-read-cache-of-ZFS-or-The-ARC.html)（2009-02-20）
* [Brendan 的博客 » ZFS ARC 的活动](http://dtrace.org/blogs/brendan/2012/01/09/activity-of-the-zfs-arc/)（2012-01-09）
* [Aaron Toponce：ZFS 管理，第 IV 部分——可调节替换缓存](https://pthree.org/2012/12/07/zfs-administration-part-iv-the-adjustable-replacement-cache/)（2012-12-07）

块分配

* [ZFS 块分配（Jeff Bonwick 的博客）](https://blogs.oracle.com/bonwick/en_US/entry/zfs_block_allocation)（2006-11-04）

去重

* [ZFS 去重（Jeff Bonwick 的博客）](https://blogs.oracle.com/bonwick/en_US/entry/zfs_dedup)（2009-11-01）

热备盘

* [ZFS 热备盘（Eric Schrock 的博客）](https://blogs.oracle.com/eschrock/entry/zfs_hot_spares)（2006-06-06）

二级自适应替换缓存（Level 2 Adaptive Replacement Cache），也称为二级可调节替换缓存（L2ARC）

* [ZFS L2ARC（Brendan Gregg）](https://blogs.oracle.com/brendan/entry/test)（2008-07-22）
* [L2ARC 截图（Brendan Gregg）](https://blogs.oracle.com/brendan/entry/l2arc_screenshots)（2009-01-30）
* [为 L2ARC 统计更新的 arcstat.pl | Mike Harsch 的博客](http://blog.harschsystems.com/2010/09/08/arcstat-pl-updated-for-l2arc-statistics/)（2010-09-08）
* [镜像管理员的日子：L2ARC 如何工作](http://mirror-admin.blogspot.com/2011/12/how-l2arc-works.html)（2011-12）
* [Aaron Toponce：ZFS 管理，第 IV 部分——可调节替换缓存](https://pthree.org/2012/12/07/zfs-administration-part-iv-the-adjustable-replacement-cache/)（2012-12-07）

RAID-Z

* [RAID-Z（Jeff Bonwick 的博客）](https://blogs.oracle.com/bonwick/en_US/entry/raid_z)（2005-11-17）
* [ZFS RAIDZ 条带宽度](http://blog.delphix.com/matt/2014/06/06/zfs-stripe-width/)，或者：我是如何学会停止忧虑并爱上 RAIDZ 的（Matt Ahrens 的博客，2014-6-15）

Scrub 与 resilver

* [新的 Scrub 代码（Matthew Ahrens 的博客）](https://blogs.oracle.com/ahrens/entry/new_scrub_code)（2008-12-15）

快照

* [这是魔法吗？（Matthew Ahrens 的博客）](https://blogs.oracle.com/ahrens/entry/is_it_magic)（2005-11-17）

空间映射

* [空间映射（Jeff Bonwick 的博客）](https://blogs.oracle.com/bonwick/entry/space_maps)（2007-09-13）
* [metaslabs 的 OpenZFS 代码走读（Delphix 的开源博客）](http://blog.delphix.com/alex/2015/01/26/openzfs_metaslabs)（2015-01-26）

事务组

* [事务组（Adam Leventhal 的博客）](http://dtrace.org/blogs/ahl/2012/12/13/zfs-fundamentals-transaction-groups/)（2012-12-13）

VFS 交互

* [FreeBSD VFS 层（Andry Gapon 的博客）](http://www.hybridcluster.com/blog/complexity-freebsd-vfs-using-zfs-example-part-1-2/)（2014-01-14）

写入节流

* [写入节流 1.0（Adam Leventhal 的博客）](http://dtrace.org/blogs/ahl/2013/12/27/zfs-fundamentals-the-write-throttle/)（2013-12-27）
* [OpenZFS 中的写入节流（Adam Leventhal 的博客）](http://dtrace.org/blogs/ahl/2014/02/10/the-openzfs-write-throttle/)（2014-2-10）
* [调优 OpenZFS 写入节流（Adam Leventhal 的博客）](http://dtrace.org/blogs/ahl/2014/08/31/openzfs-tuning/)（2014-8-31）

ZFS 意图日志（ZIL）

* [ZFS：伐木工（Neil Perrin 的博客）](https://blogs.oracle.com/perrin/entry/the_lumberjack)（2005-11-16）
* [Aaron Toponce：ZFS 管理，第 III 部分——ZFS Intent Log](https://pthree.org/2012/12/06/zfs-administration-part-iii-the-zfs-intent-log/)（2012-12-06）

## 特定的开发者文档

* [Illumos 集成流程](https://openzfs.org/wiki/Illumos_integration_process)
* 关于如何为不同发行版开发 ZFS 的信息 / 指向相关资料（例如，如何构建 illumos）

  * 尤其是关于如何测试以及可能用于构建的脚本的文档
  * 需要由这些社区的代表编写 / 提供链接。
