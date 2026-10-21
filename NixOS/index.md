# 在 NixOS 中启用 ZFS 支持

## 支持

通过[邮件列表](../Project-and-Community/MailingLists.md)或 Libera Chat 上的 IRC 频道 [#zfsonlinux](ircs://irc.libera.chat/#zfsonlinux) 联系社区。如果你有与本教程相关的 Bug 报告或功能请求，请[提交新的 issue 并提及 @ne9z](https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Nix%20ZFS%20HOWTO:)。

## 安装

> **注意**
>
>本节是在既有 NixOS 系统上安装 ZFS。若要将 ZFS 用作根文件系统，请参阅《[构建以 ZFS 为根文件系统的 NixOS](NixOS-Root-on-ZFS.md)》。

NixOS Live 镜像默认内置了 ZFS 支持。

请注意，即使你不需要从 ZFS 启动，也必须应用这些设置。在完成这些更改并重启之前，将无法通过 modprobe 使用内核模块“zfs.ko”。

1. 编辑 `/etc/nixos/configuration.nix`，添加以下选项：

   ```ini
   boot.supportedFilesystems = [ "zfs" ];
   boot.zfs.forceImportRoot = false;
   networking.hostId = "yourHostId";
   ```

   其中可通过以下方式生成 hostId：

   ```sh
   head -c4 /dev/urandom | od -A none -t x4
   ```

2. 应用配置更改：

   ```sh
   nixos-rebuild boot
   ```

3. 重启：

   ```sh
   reboot
   ```

## 贡献

你可以为本文档作出贡献：复刻（fork）本仓库，编辑文档，然后提交拉取请求。

1. 要在本地测试你的更改，请使用本仓库中的 devShell：

   ```sh
   git clone https://github.com/ne9z/nixos-live openzfs-docs-dev
   cd openzfs-docs-dev
   nix develop ./openzfs-docs-dev/#docs
   ```

2. 在 openzfs-docs 仓库中构建页面：

   ```sh
   make html
   ```

3. 检查 make 输出中的错误与警告。如果没有错误：

   ```sh
   xdg-open _build/html/index.html
   ```

4. 将更改 `git commit --signoff` 到某个分支，`git push`，并创建拉取请求，提及 @ne9z。

