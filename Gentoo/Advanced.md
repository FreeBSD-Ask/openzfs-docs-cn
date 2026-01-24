# Gentoo ZFS 高级教程

- 原文：[ZFS/Advanced](https://wiki.gentoo.org/wiki/ZFS/Advanced)，最后编辑于 2025 年 4 月 21 日 (星期一) 11:05

## 概述

本节将深入探讨 ZFS 用户的高级主题，包括广泛的高级功能和优化技术。用户将学习自动化脚本以简化日常任务和系统维护，以及全面的 ZFS 调优策略，以在不同工作负载场景中最大化性能。内容包括高级数据集管理、用于监控和维护的自定义脚本、通过 ARC 和 ZIL 调优实现性能优化、复杂的备份与恢复流程，以及企业级高可用性配置。此外，本节还探讨高级加密方法、RAID-Z 扩展技术、特殊 VDEV 优化和容器集成策略。无论是管理家庭服务器还是企业存储基础设施，这些高级主题都将帮助用户通过适当的系统集成、自动化维护和性能监控充分发挥 ZFS 的潜力。特别关注实际场景和实践应用，确保用户能够将这些高级概念有效应用于其特定用例。

## 自动化脚本

**概述：** 手动更新 ZFS 内核模块可能耗时且易出错，比如：

- 监控 OpenZFS GitHub 发布页面的更新
- 检查每个新版本的内核兼容性
- 下载并安装适当版本
- 确保 ZFS 模块与内核版本之间的系统一致性

**系统要求：** 确保具备以下前提条件：

- 配备 bash shell 的 Linux 系统
- 安装 curl 用于下载发布信息
- 可访问 GitHub 的网络连接
- 安装内核模块和更新所需的权限
- 脚本操作所需目录具有写权限

#### 使用 eix post sync

下面的脚本将由脚本 `system_update.sh` 触发。在每次更新系统时用户都应执行它。如果根据提供的参数没有新更新，脚本将退出。这是为了确保脚本在 post-sync 后检查任何新内核版本。在 `postsync.d` 下创建你的 hook 脚本：

```sh
sudo nano -w /etc/portage/postsync.d/zfs-check
```

为文件 `/etc/portage/postsync.d/zfs-check` 设置 **eix post sync**

```sh
#!/bin/bash
/etc/hooks.d/zfs/system_update.sh stable 0 "/home/masterkuckles"
```

>**注意**
>
>将 `stable` 替换为 `testing` 或 `unknown`，如需调试数据结构，将 `0` 改为 `1`，并将 `"/home/masterkuckles"` 改为你希望复制内核配置的路径。

现在使其可执行：

```sh
chmod +x /etc/portage/postsync.d/zfs-check
```

#### 系统更新脚本

>**注意**
>
>bash 编程语言是图灵完备的。然而，它缺少 try、catch、except、throw 等关键字，这使得调试更困难。此外，即使语法略有错误，bash 仍会运行，因此需要注意。有关正则解析，请访问 [此处](https://www.gnu.org/software/sed/manual/html_node/Regular-Expressions.html)。如 error 等函数及数据结构定义在另一个脚本中。

>**注意**
>
>可能存在一些未知的极端情况。如果 DOM 树结构发生变化，脚本可能会失效。解决方法之一是在 `parse_linux_compatibility` 中前置另一个 if 语句，但需要检查 [这里](https://github.com/openzfs/zfs/releases) 以找到正确的表达式。目前：`Linux: compatible with ... kernels` 和 `Linux kernels ...` 将兼容从 zfs-3.0 到 zfs-2.2.5。如果这太复杂且你认为有问题，可以在启用 DEBUG 后运行 `debug_releases()` 并创建 pull request [这里](https://github.com/alphastigma101/BashScripts)，或提交 bug 报告。

>**警告**
>
>截至 25 年 2 月 12 日，上述脚本仍在测试中。大部分已在 Gentoo 机器上测试过并可运行。它将根据 CLI 中传入的参数（如 stable、testing、unknown）安装新内核版本。仍存在一些需要解决的 bug，例如安装新的 ZFS 模块以及删除旧的内核目录。此外，该脚本仅用 stable 参数测试过。如果使用 testing 或 unknown，也应能正常工作。如脚本崩溃，你会知道如何处理。

该脚本将从 Portage 树中安装最新可用内核版本，并删除那些过期的内核。如果在内核安装、编译或安装新的 ZFS 模块过程中出现错误，脚本会捕获错误再退出。脚本功能依赖于提供的参数。

系统更新文件 `/etc/hooks.d/zfs/system_update.sh`：

```sh
#!/bin/bash
source ./compatibility.sh 
TYPE=$(uname -m)
KEY=""
ZFS_KEY=""
STATUS="$1"
CONFIG_PATH="$3"

# 检查是否有更新的函数
check_kernel() {
    # 假设用户已从 Portage 合并内核源代码
    local pkg=$(cat /var/lib/portage/world | grep -E '^sys-kernel\/[[:alpha:]]+-[[:alpha:]]+:[0-9]+\.[0-9]+\.[0-9]+$')
    if echo $pkg | grep -Eq 'gentoo-sources'; then

    # 无法将数组直接赋值给映射。因此，将其转换为字符串
    # 然后使用 mapfile 再将其转换回数组
        INSTALLED_KERNELS["gentoo-sources"]=$pkg
        KEY="gentoo-sources"
        # 待办事项：需要找到最新的稳定版本并在此基础上 +1
        touch /etc/portage/package.mask/gentoo-sources
        #echo >=
    else
        if echo $pkg | grep -Eq 'gentoo-kernel-bin'; then
            INSTALLED_KERNELS["gentoo-kernel-bin"]=$pkg
            KEY="gentoo-kernel-bin"
            # 待办事项：需要找到最新的稳定版本并在此基础上 +1
            touch /etc/portage/package.mask/gentoo-kernel-bin
            #echo >=
        else
            system_update_bug_report
            exit 0
        fi 
    fi
    return 0
}
# 检查 ZFS 是否有可用更新的函数
check_zfs() {
    # 重新更新已安装内核的映射
    check_kernel
    curl -s https://packages.gentoo.org/packages/sys-fs/zfs > gentoo_zfs_sources.html
    local line=$(grep -oP 'title="\d+\.\d+\.\d+ [^"]+"' gentoo_zfs_sources.html)
    local installed_zfs=$(cat /etc/portage/package.mask/zfs | sed 's/^[^a-zA-Z]*//;s/[[:space:]]*$//')
    installed_zfs=$(echo "$installed_zfs" | sed 's/[[:space:]]*$//')
    # 创建数组，用于保存 zfs 和 zfs-kmod 包的版本
    mapfile -t CURRENT_ZFS <<< "$(echo "$installed_zfs" | tr ' ' '\n')"
    local current=${CURRENT_ZFS[0]}
    while read -d '"' -r chunk; do
        if [[ $chunk =~ ^title= ]]; then
            continue  # 跳过 "title=" 这一部分
        fi
        if [[ $chunk =~ ^([0-9]+\.[0-9]+\.[0-9]+)[[:space:]]is[[:space:]](testing|stable|unknown)[[:space:]]on[[:space:]]([a-z0-9]+)$ ]]; then
            version="${BASH_REMATCH[1]}"
            status="${BASH_REMATCH[2]}"
            architecture="${BASH_REMATCH[3]}"
            # 如果为空则初始化
            ZFS_DICT[$architecture]="${ZFS_DICT[$architecture]:-}"
            # 追加新值
            ZFS_DICT[$architecture]+="$status:$version "
        fi
    done < <(echo "$line")
    local zfs_releases=""
    if [ "$TYPE" == "x86_64" ]; then
        zfs_releases=${ZFS_DICT["amd64"]}
    else 
        zfs_releases=${ZFS_DICT[$TYPE]}
    fi
    IFS=' ' read -r -a lines <<< "$zfs_releases"
    for line in "${lines[@]}"; do
        IFS=':' read -r status_val version_val <<< "$line"
        if [[ "$DEBUG" -eq 1 ]]; then
            echo "Printing out Versions:"
            echo $status_val
            echo "====================================="
 
        fi
        # 注意：如果 DOM 树结构发生变化导致版本顺序改变，此处可能会出现问题
        if [ "$STATUS" == "$status_val" ]; then 
            if [ ! -n "$ZFS_KEY" ]; then
                ZFS_KEY="zfs-$version_val"
            fi
            if [ ! -n "$current" ]; then
                current="sys-fs/zfs-$version_val"
            fi
            AVAILABLE_ZFS["$status_val"]+="sys-fs/zfs-$version_val "
        fi
    done
    # 检查用户是否拥有最新版本
    local new_zfs=${AVAILABLE_ZFS["$STATUS"]}
    local usr_version=$(echo "$current" | sed 's/.*-\(.*\)/\1/')
    IFS=' ' read -r -a zfs <<< "$new_zfs"
    for ele in "${zfs[@]}"; do
        available_version=$(echo "$ele" | sed 's/^[^:]*://')
        if [[ "$(echo -e "$usr_version\n$available_version" | sort -V | head -n 1)" == "$usr_version" && "$usr_version" != "$available_version" ]]; then
            echo "A zfs update is available! Going to update"
            if [ -d "/etc/portage/package.mask" ]; then 
                rm /etc/portage/package.mask/zfs
                echo ">=sys-fs/$ZFS_KEY" >> /etc/portage/package.mask/zfs
                echo ">=sys-fs/zfs-kmod-$available_version" >> /etc/portage/package.mask/zfs
            else
                echo ">=sys-fs/$ZFS_KEY" >> /etc/portage/package.mask
                echo ">=sys-fs/zfs-kmod-$available_version" >> /etc/portage/package.mask
            fi
            return 0
        else 
            echo "System has the latest version already installed!"
            exit 0
        fi
    done
    return 0
}

# 安装新内核的函数
install_kernel() {
    local usr_kernel_str=${INSTALLED_KERNELS[$KEY]}
    local output=0
    local copy_config=0
    for build in "${BUILD_KERNELS[@]}"; do
        version=$(echo "$build" | sed 's/^[^-]*-//')
        eselect kernel set $build
        cd /usr/src/linux || error "install_kernel" "Folder /usr/src/linux does not exist!"
        # 注意：需要将配置文件复制到 home 以外的位置
        if [ "$copy_config" -ne 1 ]; then
            config=$(ls $CONFIG_PATH/*-config | head -n 1)
            cp -Prv $config ./.config
            copy_config=1
        fi
        if [ ! -d "/lib/modules/$version-$TYPE" ]; then 
            make menuconfig
            make -j3 || error "install_kernel" "Failed to compile" && \
            make modules_install || error "install_kernel" "Failed to install modules" && \
            make install || error "install_kernel" "Failed to install kernel"
            cp -Prv arch/x86/boot/bzImage /boot/"vmlinuz-$version-$TYPE"
        fi
        if [ -d "/usr/src/initramfs" ]; then
            new_path="$version-$TYPE"
            if [[ "$output" -eq 0 ]]; then
                echo "====================================="
                echo "Creating the directories in /usr/src/initramfs!"
                output=1
            fi
            if [ -d "/usr/src/initramfs/lib" ] && [ -d "/usr/src/initramfs/lib/modules" ]; then
                if [ ! -d "/usr/src/initramfs/lib/modules/$new_path" ]; then  
                    mkdir -vp /usr/src/initramfs/lib/modules/$new_path
                fi
            else
                if [ ! -d  "/usr/src/initramfs/lib" ]; then
                    mkdir -vp /usr/src/initramfs/lib 
                fi
                if [ ! -d "/usr/src/initramfs/lib/modules" ]; then 
                    mkdir -vp /usr/src/initramfs/lib/modules
                fi
                if [ ! -d "/usr/src/initramfs/lib/modules/$new_path" ]; then 
                    mkdir -vp /usr/src/initramfs/lib/modules/$new_path
                fi
            fi
            if [ ! -d "/usr/src/initramfs/lib/modules/$new_path/extra" ]; then
                echo "Creating the extra folder to copy over the modules!"
                mkdir -vp /usr/src/initramfs/lib/modules/$new_path/extra
            fi
        fi
    done
    mapfile -t usr_kernel_arr <<< "$usr_kernel_str"
    local clean_up=0
    for usr_kernels in "${usr_kernel_arr[@]}"; do
        if [ "$clean_up" -ne 0 ]; then
            echo "====================================="
            echo "Cleaning up old directories in /usr/src/initramfs/lib/modules!"
            echo "====================================="
            clean_up=1
        fi
        # 去掉包名和冒号，仅提取版本号
        usr_version=$(echo "$usr_kernels" | sed 's/^[^:]*://')
        if [ -d "/usr/src/initramfs/$usr_version-gentoo-$TYPE" ]; then
            if [ -d "/usr/src/initramfs/lib/modules/$usr_version-gentoo-$TYPE" ]; then 
                echo "====================================="
                echo "Removing old folders from /usr/src/initramfs/modules/$usr_version-gentoo-$TYPE"
                rm -r /usr/src/initramfs/lib/modules/"$usr_version-gentoo-$TYPE" || error "install_kernel" "Failed to remove $usr_version-gentoo-$TYPE from /usr/src/initramfs/lib/modules/"
            fi
            if [ -d "/lib/modules/$usr_version-gentoo-$TYPE" ]; then 
                echo "====================================="
                echo "Removing old folders from /lib/modules/$usr_version-gentoo-$TYPE"
                rm -r /lib/modules/"$usr_version-gentoo-$TYPE" || error "install_kernel" "Failed to remove $usr_version-gentoo-$TYPE from /lib/modules/"
            fi 
            if [ -d "/boot/vmlinuz-$usr_version-gentoo-$TYPE" ]; then 
                echo "====================================="
                echo "Removing the old vmlinuz from /boot/vmlinuz-$usr_version-gentoo-$TYPE"
                rm  /boot/"vmlinuz-$usr_version-gentoo-$TYPE" || error "install_kernel" "Failed to remove vmlinuz-$usr_version-$TYPE from /boot"
            fi 
            if [ -d "/boot/initramfs-$usr_version-$TYPE.img" ]; then 
                echo "====================================="
                echo "Removing the old initramfs from /boot/initramfs-$usr_version-$TYPE.img"
                rm /boot/"initramfs-$usr_version-$TYPE.img" || error "install_kernel" "Failed to remove initramfs-$usr_version-$TYPE.img from /boot"
            fi 
        else 
            if [ -d "/lib/modules/$usr_version-gentoo-$TYPE" ]; then 
                echo "====================================="
                echo "Removing old folders from /lib/modules/$usr_version-gentoo-$TYPE"
                rm -r /lib/modules/"$usr_version-gentoo-$TYPE" || error "install_kernel" "Failed to remove $usr_version-gentoo-$TYPE from /lib/modules/"
            fi 
            if [ -d "/boot/vmlinuz-$usr_version-gentoo-$TYPE" ]; then 
                echo "====================================="
                echo "Removing the old vmlinuz from /boot/vmlinuz-$usr_version-gentoo-$TYPE"
                rm  /boot/"vmlinuz-$usr_version-gentoo-$TYPE" || error "install_kernel" "Failed to remove vmlinuz-$usr_version-$TYPE from /boot"
            fi 
            if [ -d "/boot/initramfs-$usr_version-$TYPE.img" ]; then 
                echo "====================================="
                echo "Removing the old initramfs from /boot/initramfs-$usr_version-$TYPE.img"
                rm /boot/"initramfs-$usr_version-$TYPE.img" || error "install_kernel" "Failed to remove initramfs-$usr_version-$TYPE.img from /boot"
            fi 
        fi
    done
    return 0
}

# 函数将仅根据运行前传入的参数安装特定版本
install_kernel_resources() {
    local usr_kernel_str=${INSTALLED_KERNELS[$KEY]}
    local available_kernel_str=""
    local build_str=""
    if [ "$TYPE" == "x86_64" ]; then
        available_kernel_str=${ARCH_DICT["amd64"]}
    else 
        available_kernel_str=${ARCH_DICT[$TYPE]}
    fi
    if [ ! -n "$available_kernel_str" ] || [ ! -n "$usr_kernel_str" ]; then
        system_update_bug_report
        exit 0
    fi
    # 在空格处拆分行
    IFS=' ' read -r -a lines <<< "$available_kernel_str"
    for line in "${lines[@]}"; do
        IFS=':' read -r status_val version_val <<< "$line"
        if [[ "$DEBUG" -eq 1 ]]; then
            echo "Printing out Versions:"
            echo $status_val
            echo "====================================="
        fi
        if [ "$STATUS" == "$status_val" ]; then 
            AVAILABLE_KERNELS["$status_val"]+="sys-kernel/$KEY:$version_val "
        fi
    done
    mapfile -t usr_kernel_arr <<< "$usr_kernel_str"
    IFS=' ' read -r -a kernel_arr <<< "${AVAILABLE_KERNELS["$STATUS"]}"
    local copy_config=0
    local kernel_update=0
    for usr_kernels in "${usr_kernel_arr[@]}"; do
        # 去掉包名和冒号，只提取版本号
        usr_version=$(echo "$usr_kernels" | sed 's/^[^:]*://')
        if [ ! -n "$usr_version" ]; then
            system_update_bug_report
            exit 0
        fi
        for available_kernels in "${kernel_arr[@]}"; do
            # 去掉包名和冒号，仅保留版本号
            available_version=$(echo "$available_kernels" | sed 's/^[^:]*://')
            if [ ! -n "$available_kernels" ]; then
                system_update_bug_report
                exit 0
            fi
            if [[ "$(echo -e "$usr_version\n$available_version" | sort -V | head -n 1)" == "$usr_version" && "$usr_version" != "$available_version" ]]; then
                if [[ ! "$build_str" =~ "linux-$available_version-gentoo" ]]; then
                    build_str+="linux-$available_version-gentoo "
                fi
                # 注意：需要将配置文件复制到 home 之外的位置
                if [ "$copy_config" -ne 1 ]; then
                    copy_config=1
                    kernel_update=1
                    cp -Prv /usr/src/"linux-$usr_version-gentoo"/.config $CONFIG_PATH/"$usr_version-gentoo-$TYPE-config"
                fi
                if ! equery list =sys-kernel/"$KEY-$available_version" > /dev/null; then 
                    emerge -v =sys-kernel/"$KEY-$available_version" || error "install_kernel_resources" "Failed to install the new kernel!"
                    emerge --deselect =sys-kernel/"$KEY-$available_version" || error "install_kernel_resources" "Failed to deselect the old kernels"
                    if [ -d "/usr/src/linux-$available_version-gentoo" ]; then 
                        rm -r  /usr/src/"linux-$available_version-gentoo"
                    fi
		        else 
			        echo "Kernel $KEY-available_version is already installed"
		        fi
            fi
        done 
    done
    if [ "$kernel_update" -ne 0 ]; then
        # 去除末尾的空格和换行符
        build_str=$(echo "$build_str" | sed 's/[[:space:]]*$//')
        mapfile -d ' ' -t BUILD_KERNELS <<< "$build_str"
        install_kernel
        emerge -a --depclean
    else 
        echo "====================================="
        echo "Already have the latest kernel version installed!"
        echo "Exiting script..."
        echo "====================================="
        clean_up
        exit 0
    fi
    return 0
}

# 更新到最新 ZFS 的函数
install_zfs() {
    local compatible_kernel_ranges=${COMPATIBLE_RELEASES[$ZFS_KEY]}
    local installed_kernels_str=${INSTALLED_KERNELS[$KEY]}
    local start=$(echo "$compatible_kernel_ranges" | cut -d '-' -f1)
    local end=$(echo "$compatible_kernel_ranges" | sed 's/^[^-]*-//')
    mapfile -t kernels <<< "$installed_kernels_str"
    for ele in "${kernels[@]}"; do
        # 去掉包名和冒号，仅提取版本号
        version=$(echo "$ele" | sed 's/^[^:]*://')
        if version_greater_than_equal "$version" "$start" && version_less_than_equal "$version" "$end"; then
            new_path="$version-$TYPE"
            zfs_version=$(echo $ZFS_KEY | sed 's/^[^-]*-//')
            echo "Kernel version $kernel is within the range ($start - $end)."
            emerge --deselect ${CURRENT_ZFS[0]} || error "install_zfs" "Failed to uninstall the old zfs"
            emerge --deselect ${CURRENT_ZFS[1]} || error "install_zfs" "Failed to uninstall the old zfs kmod"
            emerge -1 =sys-fs/$ZFS_KEY || error "install_zfs" "Failed to install the newer zfs!"
            emerge -1 =sys-fs/zfs"-"kmod"-"$zfs_version || error "install_zfs" "Failed to install the new zfs-kmod!"
            if [ -d "/usr/src/initramfs" ]; then 
                cp -Prv /lib/modules/$new_path/extra/* /usr/src/initramfs/lib/modules/$new_path/extra/ || error "install_zfs" "Failed to copy over modules!"
                cp -Prv /lib/modules/$new_path/modules.* /usr/src/initramfs/lib/modules/$new_path/
            fi 
        else
            echo "====================================="
            echo "Kernel version $kernel is outside the range ($start - $end)."
        fi
    done 
    return 0
}
update_init() {
    local usr_kernel_str=${INSTALLED_KERNELS[$KEY]}
    mapfile -t usr_kernel_arr <<< "$usr_kernel_str"
    if [ -d "/usr/src/initramfs" ]; then 
        cd /usr/src/initramfs
    fi 
    for usr_kernels in "${usr_kernel_arr[@]}"; do
        usr_version=$(echo "$usr_kernels" | sed 's/^[^:]*://')
        if [ -d "/usr/src/initramfs/lib/modules/$usr_version-gentoo-$TYPE" ]; then
            lddtree --copy-to-tree /usr/src/initramfs /sbin/zfs 
            lddtree --copy-to-tree /usr/src/initramfs /sbin/zpool 
            lddtree --copy-to-tree /usr/src/initramfs /sbin/zed 
            lddtree --copy-to-tree /usr/src/initramfs /sbin/zgenhostid
            lddtree --copy-to-tree /usr/src/initramfs /sbin/zvol_wait 
            find . -not -path "/lib/modules/*" -o -path "./lib/modules/$usr_version-gentoo-$TYPE/*" -print0 | cpio --null --create --verbose --format=newc | gzip -9 > boot/initramfs-"$usr_version-gentoo-$TYPE".img
            echo "====================================="
        else 
            Dracut=$(cat /var/lib/portage/world | grep -E '^sys-kernel\/dracut-+:[0-9]+\.[0-9]+\.[0-9]+$')
            # 需要检查字符串是否为空
            if [[ -n "$Dracut" ]]; then
                # 如果非空，则使用 dracut 生成 initramfs
                dracut --force --kver="$usr_version" /boot/initramfs-"$usr_version-gentoo-$TYPE".img || error "update_init" "Failed to create initramfs using dracut!"
            fi
            GenKernel=$(cat /var/lib/portage/world | grep -E '^sys-kernel\/genkernel-+:[0-9]+\.[0-9]+\.[0-9]+$')
            # 需要检查字符串是否为空
            if [[ -n "$GenKernel" ]]; then
                # 如果非空，则使用 genkernel 生成 initramfs
                genkernel --kernel-config=/usr/src/linux-$usr_version-gentoo/.config initramfs --kerneldir=/usr/src/linux-$usr_version-gentoo || error "update_init" "Failed to create initramfs using genkernel!"
            else 
                error "update_init" "Error: The 'Dracut' and 'GenKernel' variables are empty.\nThis indicates a bug in the script. Please file a bug report or submit a pull request to resolve the issue at: https://github.com/alphastigma101/BashScripts\n\nSteps to follow:\n1. Provide details of your environment (e.g., OS, Bash version).\n2. Describe how to reproduce the issue.\n3. Submit a pull request with a fix if possible.\n\nIf you are unable to submit a fix, please report the issue with as much detail as you can."
            fi  
        fi 
    done 
    return 0
}

populate_data_structures() {
    curl -s https://packages.gentoo.org/packages/sys-kernel/$KEY > kernel_sources.html
    local line=$(grep -oP 'title="\d+\.\d+\.\d+ [^"]+"' kernel_sources.html)
    while read -d '"' -r chunk; do
        if [[ $chunk =~ ^title= ]]; then
            continue  # 跳过 "title=" 这个部分
        fi
        if [[ $chunk =~ ^([0-9]+\.[0-9]+\.[0-9]+)[[:space:]]is[[:space:]](testing|stable|unknown)[[:space:]]on[[:space:]]([a-z0-9]+)$ ]]; then
            version="${BASH_REMATCH[1]}"
            status="${BASH_REMATCH[2]}"
            architecture="${BASH_REMATCH[3]}"
            # 如果为空则初始化
            ARCH_DICT[$architecture]="${ARCH_DICT[$architecture]:-}"
            # 附加新值
            ARCH_DICT[$architecture]+="$status:$version "
        fi
    done < <(echo "$line")
    return 0
}

clean_up() {
    remove_html 
    return 0
}

main() {
    populate_zfs_releases
    check_kernel
    populate_data_structures
    install_kernel_resources "$STATUS"
    check_zfs
    install_zfs
    update_init
    update_bootloader
    clean_up
}
main
if [[ "$DEBUG" -eq 1 ]]; then
    debug_releases
    debug_arch_dict
    debug_installed_kernel
    debug_stable_kernel
    debug_testing_kernel
fi
```

#### 兼容脚本

该脚本通过网页抓取 [此页面](https://github.com/openzfs/zfs/releases) 来查找最新更新的 ZFS 模块及其支持的内核版本。请注意，GitHub 上 OpenZFS 支持的最新 ZFS 模块版本通常高于 Gentoo 当前的版本。明智的做法是使用被 Gentoo 标记为 stable 的 ZFS 模块。

>**注意**
>
>其函数和数据结构在另一个脚本中使用，该脚本将在本节后面进一步说明。

兼容性脚本：

```sh
#!/bin/bash
source ./bug_report.sh
source ./debug_data_structures.sh 
source ./helper_functions.sh
source ./error_handling.sh
DEBUG="$2"

# 用于存储兼容版本的关联数组
declare -A COMPATIBLE_RELEASES
declare -a RANGES
# 提取 Linux 内核兼容性的函数
parse_linux_compatibility() {
    local url="$1"
    local release_name="$2"
    curl -s $url > $release_name".html"
    # 使用 grep 和 sed 提取 Linux 内核兼容性相关行
    local linux_line=$(grep -A10 "Supported Platforms:" "$release_name.html" | grep "Linux kernels" | sed -e 's/^\s*//; s/\s*$//')
    # 检查 Linux 兼容性相关行是否存在
    if [[ -z "$linux_line" ]]; then
        linux_line=$(grep -A10 "Supported Platforms" "$release_name.html" | grep -oP "Linux: compatible with [0-9.]+ - [0-9.]+ kernels" | sed -e 's/^\s*//; s/\s*$//')
    fi
    # 使用正则表达式提取最小和最大内核版本
    if [[ "$linux_line" =~ Linux:\ compatible\ with\ ([0-9.]+)\ -\ ([0-9.]+)\ kernels ]]; then
        min_version="${BASH_REMATCH[1]}"
        max_version="${BASH_REMATCH[2]}"
    fi
    if [[ "$linux_line" =~ Linux\ kernels\ ([0-9]+\.[0-9]+)\ -\ ([0-9]+\.[0-9]+) ]]; then
        min_version="${BASH_REMATCH[1]}"
        max_version="${BASH_REMATCH[2]}"
    fi
    # 将结果存储到 RANGES 和 COMPATIBLE_RELEASES 中
    RANGES[0]="$min_version"
    RANGES[1]="$max_version"
    COMPATIBLE_RELEASES["$release_name"]="${RANGES[0]}-${RANGES[1]}"
    return 1
}

populate_releases() {
    # 下载 releases 页面内容
    curl -s https://github.com/openzfs/zfs/releases > zfs_releases.html
    mapfile -t RELEASES_PAGE < <(
        awk 'BEGIN{RS="<div"; ORS="<div"} /class="Box-body"/{flag=1} flag; /<\/div>/{flag=0}' zfs_releases.html | \
        grep -oP 'href="\/openzfs\/zfs\/releases\/tag\/[^"]+"' | cut -d '"' -f 2
    )
    for url in "${RELEASES_PAGE[@]}"; do
        release_name=$(echo $url | grep -oP 'zfs-.*$')
        # 试图解压 Linux 内核兼容性文件
        parse_linux_compatibility "https://github.com$url" "$release_name"
    done
}
debug_releases() {
    # 打印兼容性文件的 releases
    echo "Compatible ZFS Releases:"
    for release in "${!COMPATIBLE_RELEASES[@]}"; do
        echo "$release: Linux kernel ${COMPATIBLE_RELEASES[$release]}"
    done
}
remove_html() {
    rm -f *.html
}
# 检查 DEBUG 是否设置为 1
if [[ "$DEBUG" -eq 1 ]]; then
    # 如果启用 DEBUG，则调用函数 populate_releases 
    populate_releases
    debug_releases
fi
```

#### Bug 报告脚本

如果在运行时发生崩溃，该脚本将通过调用特定函数执行。它会提供详细的信息，说明可以采取的操作。请注意，如果被抓取网页的 DOM 结构发生任何变化，该脚本可能会变得非常脆弱并失效。

Bug 报告脚本 `/etc/hooks.d/zfs/bug_report.sh`：

```sh
#!/bin/bash
system_update_bug_report() {
    echo -e "### Bug Report: Issue with Kernel Update Detection in bash script\n"
    echo -e "#### Description:\n"
    echo -e "The script fails to correctly parse or match kernel packages ending with numeric versions. This issue affects the detection of installed kernel versions when running the script for Gentoo systems. Specifically, `gentoo-sources` or other kernel packages with numeric versions are not being detected properly, which impacts further operations in the script.\n"
    echo -e "#### Steps to Reproduce:\n"
    echo -e "#### How to Report a Bug:\n"
    echo -e "1. Visit the repository issues page: https://github.com/alphastigma101/BashScripts/issues\n"
    echo -e "2. Click on 'New Issue' to create a bug report.\n"
    echo -e "3. Provide a detailed description of the issue, including steps to reproduce the error and the expected vs. actual behavior.\n"
    echo -e "4. Include the relevant logs or output from running the script, as well as any error messages.\n"
    echo -e "5. Be sure to include your system and environment details such as Gentoo version, Portage version, and Bash version.\n"
    echo -e "\n#### Expected Behavior:\n"
    echo -e "The script should correctly parse and list installed kernel versions with numeric versioning, specifically matching lines like 'sys-kernel/gentoo-sources:6.1.118'.\n"
    echo -e "\n#### Actual Behavior:\n"
    echo -e "The script fails to detect or properly handle kernel packages that end with numeric versions (e.g., 'sys-kernel/gentoo-sources:6.1.118') and does not store them in the dictionary.\n"
    echo -e "\n#### Environment:\n"
    echo -e " - Operating System: Gentoo Linux\n"
    echo -e " - Script Version: $(git describe --tags)\n"
    echo -e " - Bash version: $(bash --version | head -n 1)\n"
    echo -e " - Portage version: $(emerge --info | grep -i 'portage' | head -n 1)\n"
    echo -e "\n#### Logs/Output:\n"
    echo -e "Please provide any additional log output below that could help identify the root cause of the issue.\n"
    echo -e "For example:\n"
    echo -e " - Output from running the kernel update script.\n"
    echo -e " - Any error messages.\n"
}
```

#### 调试数据结构脚本

该脚本提供已实现函数的列表，当 DEBUG 设置为 1 时可用于调试数据结构。这在出现意外行为时非常有用。其中一个可能原因是特定数据结构中没有数据，这将导致脚本崩溃。

调试数据结构脚本 `/etc/hooks.d/zfs/debug_data_structures.sh`：


```sh
#!/bin/bash
declare -A INSTALLED_KERNELS
declare -A ARCH_DICT
declare -A ZFS_DICT
declare -A STABLE_KERNELS
declare -A TESTING_KERNELS
declare -A AVAILABLE_KERNELS
declare -A AVAILABLE_ZFS
declare -a BUILD_KERNELS
declare -a CURRENT_ZFS

debug_zfs_releases() {
    # Print out the compatible releases
    echo "Compatible ZFS Releases:"
    for release in "${!COMPATIBLE_RELEASES[@]}"; do
        echo "$release: Linux kernel ${COMPATIBLE_RELEASES[$release]}"
    done
    echo "====================================="
}

debug_arch_dict() {
    for arch in "${!ARCH_DICT[@]}"; do
        echo "Architecture: $arch"
        echo "Versions: ${ARCH_DICT[$arch]}"
        echo "-------------------"  
    done
    echo "====================================="
    return 0
}

debug_installed_kernel() {
    echo "Kernel Packages:"
    for key in "${!INSTALLED_KERNELS[@]}"; do
        echo "$key: ${INSTALLED_KERNELS[$key]}"
    done
    echo "====================================="
    return 0
}

debug_available_kernel() {
    echo "AVAILABLE_KERNELS:"
    for key in "${!AVAILABLE_KERNELS[@]}"; do
        echo "$key: ${AVAILABLE_KERNELS[$key]}"
    done
    return 0
}
```

#### 辅助函数脚本

包含一系列在 `system_update.sh` 或其他地方使用的函数。创建此脚本的主要原因是为了使代码更有组织并便于维护。

辅助函数脚本 `/etc/portage/postsync.d/helper_functions.sh`：

```sh
#!/bin/bash

# 用于比较版本是否大于或等于指定版本的函数
version_greater_than_equal() {
    [[ "$(echo -e "$1\n$2" | sort -V | head -n 1)" == "$2" ]]
}

# 用于比较版本是否小于或等于指定版本的函数
version_less_than_equal() {
    [[ "$(echo -e "$1\n$2" | sort -V | tail -n 1)" == "$2" ]]
}
```

#### 错误处理脚本

如果在运行时发生问题，该脚本会记录发生异常行为的函数名的字符串字面量，以及简短的说明发生了什么。请注意，由于缺少文件夹或文件，有些错误可能是误报。这不是问题，仅意味着需要添加额外的 if 语句。

错误处理脚本 `/etc/portage/postsync.d/error_handling.sh`：

```sh
#!/bin/bash

# 用于打印错误的函数
error() {
    local x="$1"
    local y="$2"
    local arr="$3"
    if [ "$x" == "install_kernel" ]; then
        echo "[ERROR:] In $x. $y! "
        echo "Cleaning up...."
        make clean || cd /usr/src/linux && make clean
        make mrproper
        exit 0
    elif  [ "$x" == "install_kernel_resources" ]; then
        echo "[ERROR:] In $x. $y! "
        exit 0
    elif [ "$x" == "install_zfs" ]; then 
        echo "[ERROR:] In $x. $y! "
        exit 0
    elif [ "$x" == "update_init" ]; then 
        echo "[ERROR:] In $x. $y! "
        exit 0
    fi
    exit 0
}
```

#### 完成设置

在所有内容实现和配置完成后，使 `/etc/hooks.d/zfs` 内的脚本可执行：

```sh
chmod +x /etc/hooks.d/zfs/*.sh
```

