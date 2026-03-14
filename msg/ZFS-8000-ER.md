# 消息 ID：ZFS-8000-ER

## ZFS 勘误 #1

| **类型：**   | 兼容性                                                                   |
| --------- | --------------------------------------------------------------------- |
| **严重性：**  | 中等                                                                    |
| **描述：**   | ZFS 池包含磁盘上的格式不兼容问题                                                   |
| **自动响应：** | 不会采取自动响应                                                             |
| **影响：**   | 在使用 OpenZFS 0.6.3 或更新版本对池进行 scrub（清洗）之前，旧版本的 OpenZFS 或其他 ZFS 实现可能无法导入该池|

### 建议系统管理员采取的操作

该池包含磁盘上的格式不兼容问题。必须使用当前版本的 ZFS 导入受影响的池，然后再进行 scrub。这将使池恢复到可被其他实现导入的状态。本勘误仅影响 ZFS 版本之间的兼容性，不会对用户数据造成风险。

```sh
# zpool status -x
  pool: test
 state: ONLINE
status: Errata #1 detected.
action: To correct the issue run 'zpool scrub'.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-ER
  scan: none requested
config:

    NAME            STATE     READ WRITE CKSUM
    test            ONLINE    0    0     0
      raidz1-0      ONLINE    0    0     0
        vdev0       ONLINE    0    0     0
        vdev1       ONLINE    0    0     0
        vdev2       ONLINE    0    0     0
        vdev3       ONLINE    0    0     0

errors: No known data errors

# zpool scrub test

# zpool status -x
all pools are healthy
```

## ZFS 勘误 #2

| **类型：**   | 兼容性                                       |
| --------- | ----------------------------------------- |
| **严重性：**  | 中等                                        |
| **描述：**   | 在异步销毁操作进行期间更新了 ZFS 软件包，导致池中存在磁盘上的格式不兼容问题 |
| **自动响应：** | 不会采取自动响应                                |
| **影响：**   | 在问题解决之前，无法导入该池                           |

### 建议系统管理员采取的操作

必须将受影响的池回退到先前的 ZFS 版本，以便能够正确导入。导入后，必须让所有异步销毁操作完成。随后就可以更新 ZFS 软件包，并且可以被新版本的软件干净地导入池。


```sh
# zpool import
  pool: test
    id: 1165955789558693437
 state: ONLINE
status: Errata #2 detected.
action: The pool cannot be imported with this version of ZFS due to
        an active asynchronous destroy.  Revert to an earlier version
        and allow the destroy to complete before updating.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-ER
config:

    test           ONLINE
      raidz1-0     ONLINE
        vdev0      ONLINE
        vdev1      ONLINE
        vdev2      ONLINE
        vdev3      ONLINE
```

回退到先前的 ZFS 版本，导入池，然后等待 `freeing` 属性降至零。这意味着所有未完成的异步销毁操作均已完成。

```sh
# zpool get freeing
NAME  PROPERTY  VALUE    SOURCE
test  freeing   0        default
```

此时可以更新 ZFS 软件包并导入池。现在可以在线修复磁盘上的格式不兼容问题，如 [勘误 #1](https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-ER/index.html#1) 所述。

## ZFS 勘误 #3

| **类型：**   | 兼容性                                                                                |
| --------- | ---------------------------------------------------------------------------------- |
| **严重性：**  | 中等                                                                                 |
| **描述：**   | 加密的数据集包含磁盘上的格式不兼容问题                                                               |
| **自动响应：** | 不会采取自动响应                                                                         |
| **影响：**   | 无法挂载或以写入方式打开那些在 ZFS 软件包更新之前创建的加密数据集。该勘误影响 ZFS 正确执行原始发送（raw send）的能力，因此这些数据集的此功能已被禁用 |

### 建议系统管理员采取的操作

受影响池的系统管理员需要重新创建那些在使用新版本 ZFS 之前创建的所有加密数据集。这可以通过使用 `zfs send` 和 `zfs receive` 完成。但请注意，备份不能使用原始 `zfs send -w`，因为这会使磁盘上的不兼容问题残余。系统管理员还可以使用常规工具将数据备份到新的加密数据集中。新版本的 ZFS 会阻止向受影响的数据集写入新数据，但仍可以以只读方式挂载。

```sh
# zpool status
  pool: test
    id: 1165955789558693437
 state: ONLINE
status: Errata #3 detected.
action: To correct the issue backup existing encrypted datasets to new
        encrypted datasets and destroy the old ones.
   see: https://openzfs.github.io/openzfs-docs/msg/ZFS-8000-ER
config:

    test           ONLINE
      raidz1-0     ONLINE
        vdev0      ONLINE
        vdev1      ONLINE
        vdev2      ONLINE
        vdev3      ONLINE
```

导入池并将全部既有的加密数据集备份到新的数据集中。为确保新数据集重新加密，请确保将其接收至加密根分区下，或使用 `zfs receive -o encryption=on`，然后销毁源数据集。


```sh
# zfs send test/crypt1@snap1 | zfs receive -o encryption=on -o keyformat=passphrase -o keylocation=file:///path/to/keyfile test/newcrypt1
# zfs send -I test/crypt1@snap1 test/crypt1@snap5 | zfs receive test/newcrypt1
# zfs destroy -R test/crypt1
```

可以以读写方式挂载并正常使用新的数据集。重新导入池后，勘误将被解决；仅在发现另一个存在勘误的数据集时，才会再次显示警告。为确保所有数据集均为新版本，请重新导入池，加载所有密钥，挂载所有加密数据集，并检查 `zpool status`。


```sh
# zpool export test
# zpool import test
# zfs load-key -a
Enter passphrase for 'test/crypt1':
1 / 1 key(s) successfully loaded
# zfs mount -a
# zpool status -x
all pools are healthy
```

## ZFS 勘误 #4

| **类型：**   | 兼容性                                                                                       |
| --------- | ----------------------------------------------------------------------------------------- |
| **严重性：**  | 中等                                                                                        |
| **描述：**   | 加密数据集的磁盘格式与当前系统不兼容                                                                   |
| **自动响应：** | 不会采取自动响应                                                                                |
| **影响：**   | 在 ZFS 软件包更新之前创建的加密数据集无法通过原始发送备份到更新的系统。这些数据集也无法接收额外的快照。在启用 `bookmark_v2` 功能之前，无法创建新的加密数据集 |

### 建议系统管理员采取的操作

首先，受影响池的系统管理员需要在其池上启用 `bookmark_v2` 功能。启用此功能后，在创建任何新书签后，以前版本的 ZFS 软件将无法导入（包括只读导入）该池。如果池中没有加密数据集，则这是唯一需要的步骤。如果存在现有加密数据集，则管理员需要备份这些数据集。这可以通过多种方式完成。可以像平常一样使用非原始的 `zfs send` 和 `zfs receive`，也可以使用传统备份工具。现有加密数据集的原始接收以及向现有加密数据集的原始接收当前被禁用，因为 ZFS 无法保证流和现有数据集来自一致的来源。可以禁用该检查，从而让 ZFS 接收这些流。但请注意，如果在多次增量备份过程中混合使用原始和非原始接收，可能会导致数据集出现由于身份验证错误而无法访问的数据。要禁用此限制，请将模块参数 `zfs_disable_ivset_guid_check` 设置为 1。以这种方式接收的流（以及升级前接收的任何流）需要通过读取数据手动检查，以确保数据未损坏。请注意，`zpool scrub` 无法用于此目的，因为 scrub 不会检查加密认证码。有关此问题的更多信息，请参阅 zfs 手册页中 `zfs receive` 部分，其中描述了原始发送的限制。


```sh
# zpool status
  pool: test
 state: ONLINE
status: Errata #4 detected.
        Existing encrypted datasets contain an on-disk incompatibility
        which needs to be corrected.
action: To correct the issue enable the bookmark_v2 feature and backup
        any existing encrypted datasets to new encrypted datasets and
        destroy the old ones. If this pool does not contain any
        encrypted datasets, simply enable the bookmark_v2 feature.
   see: http://openzfs.github.io/openzfs-docs/msg/ZFS-8000-ER
  scan: none requested
config:

        NAME           STATE     READ WRITE CKSUM
        test           ONLINE       0     0     0
          /root/vdev0  ONLINE       0     0     0

errors: No known data errors
```

导入池，再启用 `bookmark_v2` 功能。然后将全部既有加密数据集备份到新的数据集中。这可以使用传统工具或通过 `zfs send` 完成。当使用原始发送时，需要在接收端将 `zfs_disable_ivset_guid_check` 设置为 1。完成后，应销毁原始数据集。

```sh
# zpool set feature@bookmark_v2=enabled test
# echo 1 > /sys/module/zfs/parameters/zfs_disable_ivset_guid_check
# zfs send -Rw test/crypt1@snap1 | zfs receive test/newcrypt1
# zfs send -I test/crypt1@snap1 test/crypt1@snap5 | zfs receive test/newcrypt1
# zfs destroy -R test/crypt1
# echo 0 > /sys/module/zfs/parameters/zfs_disable_ivset_guid_check
```

重新导入池后，勘误将被解决，仅在发现另一个存在勘误的数据集时，才会再次显示警告。要检查所有数据集是否已修复，请执行 `zfs list -t all`，并在完成后检查 `zpool status`。

```sh
# zpool export test
# zpool import test
# zpool scrub # wait for completion
# zpool status -x
all pools are healthy
```



