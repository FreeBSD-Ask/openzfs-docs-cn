# Git 和 GitHub 入门指南（ZoL 版）

这是一份关于如何使用 Git 和 GitHub 进行修改的非常基础的概述。

推荐阅读：[ZFS on Linux CONTRIBUTING.md](https://github.com/zfsonlinux/zfs/blob/master/.github/CONTRIBUTING.md)

## 首次设置

如果你从未使用过 Git，在开始之前需要做一些基本设置。

```sh
git config --global user.name "My Name"
git config --global user.email myemail@noreply.non
```

## 克隆初始仓库

最简单的入门方式是点击主仓库页面顶部的 fork 图标。然后你需要将 fork 后的仓库下载一份到你的计算机上：

```sh
git clone https://github.com/<your-account-name>/zfs.git
```

这会将你的 fork 仓库设置为 “origin” 仓库。这在创建 pull request 时会很有用。为了在上游仓库发生变更时方便拉取更新，非常有必要将 upstream 仓库配置为另一个 remote（man git-remote）：

```sh
cd zfs
git remote add upstream https://github.com/zfsonlinux/zfs.git
```

## 准备进行修改

为了进行修改，推荐先创建一个分支，这样可以同时处理多个互不相关的改动。除非你拥有该仓库，否则也不建议直接在 master 分支上进行修改。

```sh
git checkout -b my-new-branch
```

从这里开始，你可以进行你的修改，然后进入下一步。

推荐阅读：[C Style and Coding Standards for SunOS](https://www.cis.upenn.edu/~lee/06cse480/data/cstyle.ms.pdf)，[ZFS on Linux Developer Resources](https://github.com/zfsonlinux/zfs/wiki/Developer-Resources)，[OpenZFS Developer Resources](https://openzfs.org/wiki/Developer_resources)

## 在推送前测试你的补丁

在提交并推送之前，你可能想先测试下你的补丁。有多种测试可以针对你的分支运行，例如风格检查和功能测试。所有 pull request 在被推送到主仓库之前都会经过这些测试，不过在本地测试可以减轻构建 / 测试服务器的负载。此步骤是可选的，但强烈建议。不过，测试套件应当在虚拟机或当前未使用 ZFS 的主机上运行。你可能需要安装 `shellcheck` 和 `flake8`，以便正确运行 `checkstyle`。

```sh
sh autogen.sh
./configure
make checkstyle
```

推荐阅读：[Building ZFS](https://github.com/zfsonlinux/zfs/wiki/Building-ZFS)，[ZFS Test Suite README](https://github.com/zfsonlinux/zfs/blob/master/tests/README.md)

## 提交你的修改以便推送

当你完成了分支上的修改后，在创建 pull request 之前还需要完成几个步骤。

```sh
git commit --all --signoff
```

该命令会打开一个编辑器，并添加你分支中所有未暂存的文件。在这里你需要说明你的修改，并添加一些内容：

```sh
# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
# On branch my-new-branch
# Changes to be committed:
#   (use "git reset HEAD <file>..." to unstage)
#
#   modified:   hello.c
#
```

首先需要添加的是 commit message。这是显示在 git log 中的内容，应当是对修改的简短描述。按照风格指南，其长度必须少于 72 个字符。

在 commit message 下面，你可以添加更详细的描述文本。本节中的每一行也必须少于 72 个字符。

完成后，commit 应该如下所示：

```sh
Add hello command

This is a test commit with a descriptive commit message.
This message can be more than one line as shown here.

Signed-off-by: My Name <myemail@noreply.non>
Closes #9998
Issue #9999
# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
# On branch my-new-branch
# Changes to be committed:
#   (use "git reset HEAD <file>..." to unstage)
#
#   modified:   hello.c
#
```

如果你是针对已有 issue 提交 pull request，也可以像上面那样引用 issue 和 pull request。完成后保存并退出编辑器。

## 推送并创建 pull request

最后阶段。你已经完成了修改并提交了 commit，现在是推送的时候了。

```sh
git push --set-upstream origin my-new-branch
```

这一步会要求你输入 GitHub 凭据，并将你的修改上传到你的仓库。

最后一步是前往你的仓库或上游仓库的 GitHub 页面，你应该能看到用于为你最近提交的分支创建新的 pull request 的按钮。

## 修正 pull request 中的问题

有时事情并不会总是按计划进行，你可能需要对 pull request 中的 commit message 或修改内容进行修正。这可以通过重新推送分支来完成。如果你需要进行代码修改或 `git add` 文件，现在可以完成这些操作，然后执行以下命令：

```sh
git commit --amend
git push --force
```

这会再次进入 commit 编辑器界面，并将你的修改覆盖到旧的提交之上。请注意，这会重新触发当前正在运行的构建 / 测试服务器流程，过于频繁地推送可能会导致所有 pull request 的处理延迟。

## 维护你的仓库

当你后续想再次进行修改时，应当先获取上游仓库的最新副本作为修改基础。以下是保持更新的方法：

```sh
git checkout master
git pull upstream master
git push origin master
```

这将确保你位于仓库的 master 分支，从 upstream 获取变更，然后再推送回你的仓库。

## 将提交回移植到发布分支

用户可能希望将 `master` 分支中的提交回移植到某个发布分支。为此，首先切换到你希望引入提交的发布版本对应的 “staging” 分支。例如，如果你想将 `master` 中的提交 XYZ 回移植到未来的 `zfs-2.3.6` 发布版本，先切换到 `zfs-2.3.6-staging` 分支，然后使用 `git cherry-pick XYZ` 拉取该提交（并解决任何合并冲突）。随后，你可以针对 `zfs-2.3.6-staging` 分支打开一个 PR（确保在 PR 目标下拉框中选择该分支）。

在进行回移植时，请保持 commit message 不变。这意味着作者保持不变，所有证明行也保持不变（Signed-off-by、Reviewed-by 等）。这些证明行被认为是指向 `master` 中的原始提交，而不一定是回移植后的提交（即使回移植过程中可能需要进行修改）。

如果需要，你可以选择性地添加一行 `Backported-by:` 并附上你的名字。

有时你可能需要添加一个仅适用于发布分支的小型、特定版本提交。在这种情况下，请在 commit 行中添加一个带有发布版本的标记，格式为 `[x.y.z-only]`。例如：

```sh
[2.3.6-only] Disable feature X by default

Unlike the master branch, turn feature X off by default
for the zfs-2.3.6 release.

Signed-off-by: Tony Hutter <hutter2@llnl.gov>
```

## 最后说明

这是对 Git 和 GitHub 的非常基础的介绍，但应当足以帮助你开始为许多开源项目做出贡献。并非所有项目都有风格要求，而且在提交修改时的流程也可能不同，因此请参考各自的文档，确认是否需要执行不同的步骤。本文未涉及的一个主题是 `git rebase` 命令，它对于本 wiki 文章来说稍微偏高级。

附加资源：[Github Help](https://help.github.com/)，[Atlassian Git Tutorials](https://www.atlassian.com/git/tutorials)
