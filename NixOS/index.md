# 在 NixOS 中启用 ZFS 支持

## 安装

>**注意**
>
>本节是在既有 NixOS 系统上安装 ZFS。若要将 ZFS 用作根文件系统，请参见下文。

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

