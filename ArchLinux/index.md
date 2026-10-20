# 在 Arch Linux 中启用 ZFS 支持

## 支持

你可以通过[邮件列表](../Project-and-Community/MailingLists.md)或 Libera Chat 上的 `#zfsonlinux` IRC 频道与社区取得联系。

如果对本指南有错误报告或功能建议，请[提交新 issue 并提及 @ne9z](https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Arch%20Linux%20ZFS%20HOWTO:)。

## 概览

由于许可不兼容，ZFS 并未包含在 Arch Linux 官方仓库中。

ZFS 支持由第三方 [archzfs 仓库](https://github.com/archzfs/archzfs) 提供。

## 安装

参见 [Archlinux Wiki](https://wiki.archlinux.org/title/ZFS)。

## 以 ZFS 为根文件系统

ZFS 可以作为 Arch Linux 的根文件系统使用。安装指南参见[构建以 ZFS 为根文件系统的 Arch Linux](ArchLinuxRoot.md)。

## 参与贡献

1. Fork 并克隆[本仓库](https://github.com/openzfs/openzfs-docs)。

2. 安装工具：

   ```sh
   sudo pacman -S --needed python-pip make

   pip3 install -r docs/requirements.txt

   # 将 ~/.local/bin 添加到 "${PATH}"，例如在 ~/.bashrc 中加入：
   [ -d "${HOME}"/.local/bin ] && export PATH="${HOME}"/.local/bin:"${PATH}"
   ```

3. 完成你的修改。

4. 测试：

   ```sh
   cd docs
   make html
   sensible-browser _build/html/index.html
   ```

5. 使用 `git commit --signoff` 提交到分支，`git push`，然后创建 PR 并提及 @ne9z。
