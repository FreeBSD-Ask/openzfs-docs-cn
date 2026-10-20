# Table of contents

* [OpenZFS 中文文档](README.md)
* [编辑日志](CHANGELOG.md)
* [目录](mu-lu.md)
* [术语表](shu-yu-biao.md)

## 安装指引

* [概述](GettingStarted.md)
* Alpine Linux
  * [在 Alpine Linux 中启用 ZFS 支持](AlpineLinux/index.md)
  * [构建以 ZFS 为根文件系统的 Alpine Linux](AlpineLinux/RootonZFS.md)
* Arch Linux
  * [在 Arch Linux 中启用 ZFS 支持](ArchLinux/index.md)
  * [构建以 ZFS 为根文件系统的 Arch Linux](ArchLinux/ArchLinuxRoot.md)
* Debian
  * [在 Debian 中启用 ZFS 支持](Debian/index.md)
  * [构建以 ZFS 为根文件系统的 Debian 13 (Trixie)](Debian/Debian-Trixie-13.md)
  * [构建以 ZFS 为根文件系统的 Debian 12 (Bookworm)](Debian/Debian-Bookworm-12.md)
  * [构建以 ZFS 为根文件系统的 Debian 11 (Bullseye)](Debian/Debian-Bullseye-11.md)
  * [构建以 ZFS 为根文件系统的 Debian 10 (Buster)](Debian/Debian-Buster-10.md)
  * [构建以 ZFS 为根文件系统的 Debian 9 (Stretch)](Debian/Debian-Stretch-9.md)
* Fedora
  * [在 Fedora 中启用 ZFS 支持](Fedora/index.md)
  * [构建以 ZFS 为根文件系统的 Fedora](Fedora/fedora-Root-on-ZFS.md)
* FreeBSD
  * [FreeBSD 中的 ZFS 支持](FreeBSD.md)
* Gentoo
  * [在 Gentoo 中启用 ZFS 支持](Gentoo/index.md)
  * [构建以 ZFS 为根文件系统的 Gentoo](Gentoo/root-on-gentoo.md)
  * [Gentoo ZFS 高级教程](Gentoo/Advanced.md)
* NixOS
  * [在 NixOS 中启用 ZFS 支持](NixOS/index.md)
  * [构建以 ZFS 为根文件系统的 NixOS](NixOS/NixOS-Root-on-ZFS.md)
* openSUSE
  * [在 openSUSE 中启用 ZFS 支持](openSUSE/index.md)
  * [构建以 ZFS 为根文件系统的 openSUSE Leap](openSUSE/zfs-on-leap.md)
  * [构建以 ZFS 为根文件系统的 openSUSE Tumbleweed](openSUSE/zfs-on-Tumbleweed.md)
* 基于 RHEL 的衍生发行版
  * [在 RHEL 及其衍生版中启用 ZFS 支持](RHEL/index.md)
  * [构建以 ZFS 为根文件系统的 Rocky Linux](RHEL/zfs-root-on-rockylinux.md)
* Slackware
  * [在 Slackware 中启用 ZFS 支持](Slackware/index.md)
  * [构建以 ZFS 为根文件系统的 Slackware](Slackware/zfs-on-Slackware.md)  
* Ubuntu
  * [在 Ubuntu 中启用 ZFS 支持](Ubuntu/index.md)
  * [构建以 ZFS 为根文件系统的 Ubuntu 22.04](Ubuntu/22.04-zfs.md)
  * [在树莓派上构建以 ZFS 为根文件系统的 Ubuntu 22.04](Ubuntu/22.04-rpi.md)
  * [构建以 ZFS 为根文件系统的 Ubuntu 20.04](Ubuntu/20.04-zfs.md)
  * [在树莓派上构建以 ZFS 为根文件系统的 Ubuntu 20.04](Ubuntu/20.04-rpi.md)
  * [构建以 ZFS 为根文件系统的 Ubuntu 18.04](Ubuntu/18.04-zfs.md)

## 项目与社区

* [概述](Project-and-Community.md)
* [系统管理](Project-and-Community/index.md)
  * [OpenZFS 系统管理](Project-and-Community/System_Administration.md)
* [捐赠](Project-and-Community/Donate.md)
* [常见问题解答](Project-and-Community/FAQ.md)
* [邮件列表](Project-and-Community/MailingLists.md)
* [签名密钥](Project-and-Community/SigningKeys.md)

## 开发资源

* [自定义软件包](DeveloperResources/CustomPackages.md)
* [构建 ZFS](DeveloperResources/BuildingZFS.md)
* [开发资源](Project-and-Community/Developer_resources.md)
* [Git 和 GitHub 入门指南（ZoL 版）](Project-and-Community/Git-and-GitHub.md)

## 性能调优

* [硬件](Performance-Tuning/Hardware.md)
* [模块参数](Performance-Tuning/ModuleParameters.md)
* [工作负载调优](Performance-Tuning/WorkloadTuning.md)
* [OpenZFS 事务延迟](Performance-Tuning/Transaction-Delay.md)
* [ZFS I/O (ZIO) 调度器](Performance-Tuning/ZIO-Scheduler.md)
* [Async Write I/O 调度](Performance-Tuning/Async-Write.md)

## 基础概念

* [ZFS 的校验和及其用途](Basic-Concepts/Checksums.md)
* [特性标志](Basic-Concepts/Feature-Flags.md)
* [RAIDZ (ZFS RAID)](Basic-Concepts/RAIDZ.md)
* [故障排除](Basic-Concepts/Troubleshooting.md)
* [虚拟设备（VDEV）](Basic-Concepts/VDEV.md)
* [分布式 RAID (dRAID)](Basic-Concepts/dRAID.md)

## 手册页

* 用户命令（User Commands (1)）
  * [cstyle(1)](man/1/cstyle.1.md)
  * [dbufstat(1)](man/1/dbufstat.1.md)
  * [raidz_test(1)](man/1/raidz_test.1.md)
  * [test-runner(1)](man/1/test-runner.1.md)
  * [zarcstat(1)](man/1/zarcstat.1.md)
  * [zarcsummary(1)](man/1/zarcsummary.1.md)
  * [zhack(1)](man/1/zhack.1.md)
  * [zilstat(1)](man/1/zilstat.1.md)
  * [ztest(1)](man/1/ztest.1.md)
  * [zvol_wait(1)](man/1/zvol_wait.1.md)
* 设备及特殊文件（Devices and Special Files (4)）
  * [spl(4)](man/4/spl.4.md)
  * [zfs(4)](man/4/zfs.4.md)
* 文件格式（File Formats (5)）
  * [vdev_id.conf(5)](man/5/vdev_id.conf.5.md)
* 杂项（Miscellaneous (7)）
  * [dracut.zfs(7)](man/7/dracut.zfs.7.md)
  * [vdevprops(7)](man/7/vdevprops.7.md)
  * [zfsconcepts(7)](man/7/zfsconcepts.7.md)
  * [zfsprops(7)](man/7/zfsprops.7.md)
  * [zpool-features(7)](man/7/zpool-features.7.md)
  * [zpoolconcepts(7)](man/7/zpoolconcepts.7.md)
  * [zpoolprops(7)](man/7/zpoolprops.7.md)
* 系统管理命令（System Administration (8)）
  * [fsck.zfs(8)](man/8/fsck.zfs.8.md)
  * [mount.zfs(8)](man/8/mount.zfs.8.md)
  * [pam_zfs_key(8)](man/8/pam_zfs_key.8.md)
  * [vdev_id(8)](man/8/vdev_id.8.md)
  * [zdb(8)](man/8/zdb.8.md)
  * [zed(8)](man/8/zed.8.md)
  * [zfs(8)](man/8/zfs.8.md)
  * [zfs-allow(8)](man/8/zfs-allow.8.md)
  * [zfs-bookmark(8)](man/8/zfs-bookmark.8.md)
  * [zfs-clone(8)](man/8/zfs-clone.8.md)
  * [zfs-create(8)](man/8/zfs-create.8.md)
  * [zfs-destroy(8)](man/8/zfs-destroy.8.md)
  * [zfs-diff(8)](man/8/zfs-diff.8.md)
  * [zfs-hold(8)](man/8/zfs-hold.8.md)
  * [zfs-jail(8)](man/8/zfs-jail.8.md)
  * [zfs-list(8)](man/8/zfs-list.8.md)
  * [zfs-load-key(8)](man/8/zfs-load-key.8.md)
  * [zfs-mount(8)](man/8/zfs-mount.8.md)
  * [zfs-mount-generator(8)](man/8/zfs-mount-generator.8.md)
  * [zfs-program(8)](man/8/zfs-program.8.md)
  * [zfs-project(8)](man/8/zfs-project.8.md)
  * [zfs-promote(8)](man/8/zfs-promote.8.md)
  * [zfs-receive(8)](man/8/zfs-receive.8.md)
  * [zfs-rename(8)](man/8/zfs-rename.8.md)
  * [zfs-rewrite(8)](man/8/zfs-rewrite.8.md)
  * [zfs-rollback(8)](man/8/zfs-rollback.8.md)
  * [zfs-send(8)](man/8/zfs-send.8.md)
  * [zfs-set(8)](man/8/zfs-set.8.md)
  * [zfs-share(8)](man/8/zfs-share.8.md)
  * [zfs-snapshot(8)](man/8/zfs-snapshot.8.md)
  * [zfs-upgrade(8)](man/8/zfs-upgrade.8.md)
  * [zfs-userspace(8)](man/8/zfs-userspace.8.md)
  * [zfs-wait(8)](man/8/zfs-wait.8.md)
  * [zfs-zone(8)](man/8/zfs-zone.8.md)
  * [zfs_ids_to_path(8)](man/8/zfs_ids_to_path.8.md)
  * [zfs_prepare_disk(8)](man/8/zfs_prepare_disk.8.md)
  * [zgenhostid(8)](man/8/zgenhostid.8.md)
  * [zinject(8)](man/8/zinject.8.md)
  * [zpool(8)](man/8/zpool.8.md)
  * [zpool-add(8)](man/8/zpool-add.8.md)
  * [zpool-attach(8)](man/8/zpool-attach.8.md)
  * [zpool-checkpoint(8)](man/8/zpool-checkpoint.8.md)
  * [zpool-clear(8)](man/8/zpool-clear.8.md)
  * [zpool-condense(8)](man/8/zpool-condense.8.md)
  * [zpool-create(8)](man/8/zpool-create.8.md)
  * [zpool-ddtprune(8)](man/8/zpool-ddtprune.8.md)
  * [zpool-destroy(8)](man/8/zpool-destroy.8.md)
  * [zpool-detach(8)](man/8/zpool-detach.8.md)
  * [zpool-events(8)](man/8/zpool-events.8.md)
  * [zpool-export(8)](man/8/zpool-export.8.md)
  * [zpool-get(8)](man/8/zpool-get.8.md)
  * [zpool-history(8)](man/8/zpool-history.8.md)
  * [zpool-import(8)](man/8/zpool-import.8.md)
  * [zpool-initialize(8)](man/8/zpool-initialize.8.md)
  * [zpool-iostat(8)](man/8/zpool-iostat.8.md)
  * [zpool-labelclear(8)](man/8/zpool-labelclear.8.md)
  * [zpool-list(8)](man/8/zpool-list.8.md)
  * [zpool-offline(8)](man/8/zpool-offline.8.md)
  * [zpool-prefetch(8)](man/8/zpool-prefetch.8.md)
  * [zpool-reguid(8)](man/8/zpool-reguid.8.md)
  * [zpool-remove(8)](man/8/zpool-remove.8.md)
  * [zpool-reopen(8)](man/8/zpool-reopen.8.md)
  * [zpool-replace(8)](man/8/zpool-replace.8.md)
  * [zpool-resilver(8)](man/8/zpool-resilver.8.md)
  * [zpool-scrub(8)](man/8/zpool-scrub.8.md)
  * [zpool-split(8)](man/8/zpool-split.8.md)
  * [zpool-status(8)](man/8/zpool-status.8.md)
  * [zpool-sync(8)](man/8/zpool-sync.8.md)
  * [zpool-trim(8)](man/8/zpool-trim.8.md)
  * [zpool-upgrade(8)](man/8/zpool-upgrade.8.md)
  * [zpool-wait(8)](man/8/zpool-wait.8.md)
  * [zpool_influxdb(8)](man/8/zpool_influxdb.8.md)
  * [zstream(8)](man/8/zstream.8.md)

## ZFS 消息

* [消息 ID：ZFS-8000-14](msg/ZFS-8000-14.md)
* [消息 ID：ZFS-8000-2Q](msg/ZFS-8000-2Q.md)
* [消息 ID：ZFS-8000-3C](msg/ZFS-8000-3C.md)
* [消息 ID：ZFS-8000-4J](msg/ZFS-8000-4J.md)
* [消息 ID：ZFS-8000-5E](msg/ZFS-8000-5E.md)
* [消息 ID：ZFS-8000-6X](msg/ZFS-8000-6X.md)
* [消息 ID：ZFS-8000-72](msg/ZFS-8000-72.md)
* [消息 ID：ZFS-8000-8A](msg/ZFS-8000-8A.md)
* [消息 ID：ZFS-8000-9P](msg/ZFS-8000-9P.md)
* [消息 ID：ZFS-8000-A5](msg/ZFS-8000-A5.md)
* [消息 ID：ZFS-8000-ER](msg/ZFS-8000-ER.md)
* [消息 ID：ZFS-8000-EY](msg/ZFS-8000-EY.md)
* [消息 ID：ZFS-8000-HC](msg/ZFS-8000-HC.md)
* [消息 ID：ZFS-8000-JQ](msg/ZFS-8000-JQ.md)
* [消息 ID：ZFS-8000-K4](msg/ZFS-8000-K4.md)

## 许可证

* [许可证](License-ZFS.md)
