# Arch Linux 概述

## 支持

可通过 [邮件列表](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/Mailing%20Lists.html#mailing-lists) 或在 [Libera Chat](https://libera.chat/) 的 [#zfsonlinux](ircs://irc.libera.chat/#zfsonlinux) IRC 频道联系社区。

如果你有与本手册相关的错误报告或功能请求，请 [新建 issue 并 @ne9z](https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Arch%20Linux%20ZFS%20HOWTO:)。

## 概览

由于许可不兼容，在 Arch Linux 官方仓库中未包含对 ZFS 的支持。

ZFS 支持由第三方的 [archzfs 仓库](https://github.com/archzfs/archzfs) 提供。

## 安装

参见 [Arch Linux Wiki](https://wiki.archlinux.org/title/ZFS)。

## 基于 ZFS 的根文件系统

可以将 ZFS 用作 Arch Linux 的根文件系统。安装指南参见：

* [根文件系统基于 ZFS 的 Arch Linux](ArchLinuxRoot.md)

## 贡献

1. 复刻并克隆 [该仓库](https://github.com/openzfs/openzfs-docs)。
2. 安装工具：

   ```sh
   sudo pacman -S --needed python-pip make

   pip3 install -r docs/requirements.txt

   # 将 ~/.local/bin 添加到 "${PATH}"，例如在 ~/.bashrc 中添加：
   [ -d "${HOME}"/.local/bin ] && export PATH="${HOME}"/.local/bin:"${PATH}"
   ```

3. 进行你的修改。
4. 测试：

   ```sh
   cd docs
   make html
   sensible-browser _build/html/index.html
   ```

5. 使用 `git commit --signoff` 提交到分支，`git push`，然后创建 pull request。然后 @ne9z。
