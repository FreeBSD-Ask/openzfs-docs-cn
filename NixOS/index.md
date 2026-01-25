# 在 NixOS 中启用 ZFS 支持

## 支持

通过 [邮件列表](https://openzfs.github.io/openzfs-docs/Project%20and%20Community/Mailing%20Lists.html#mailing-lists) 或在 [Libera Chat](https://libera.chat/) 上的 IRC 频道 [#zfsonlinux](ircs://irc.libera.chat/#zfsonlinux) 与社区取得联系。

如果你有与本教程相关的 Bug 报告或功能请求，请 [提交新 issue 并 @ne9z](https://github.com/openzfs/openzfs-docs/issues/new?body=@ne9z,%20I%20have%20the%20following%20issue%20with%20the%20Nix%20ZFS%20HOWTO:)。

## 安装

>**注意**
>
>此处用于在既有 NixOS 系统上安装 ZFS。若要将 ZFS 用作根文件系统，请参见下文。

NixOS Live 镜像默认包含 ZFS 支持。

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

## ZFS 作为根文件系统

* [NixOS 上的 ZFS 根文件系统](https://openzfs.github.io/openzfs-docs/Getting%20Started/NixOS/Root%20on%20ZFS.html)

## 贡献

你可以为本文档做出贡献。复刻此仓库，编辑文档，然后提交 pull request。

1. 若要在本地测试更改，请使用此仓库中的 devShell：

   ```
   git clone https://github.com/ne9z/nixos-live openzfs-docs-dev
   cd openzfs-docs-dev
   nix develop ./openzfs-docs-dev/#docs
   ```

2. 在 openzfs-docs 仓库中构建页面：

   ```
   make html
   ```

3. 查看 make 输出中的错误和警告。如果没有错误：

   ```
   xdg-open _build/html/index.html
   ```

4. 使用 `git commit --signoff` 提交到分支，`git push`，然后创建 pull request，并 @ne9z。
