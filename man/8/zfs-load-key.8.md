# zfs-load-key(8)

## 名称

`zfs-load-key` — 加载、卸载或更改 ZFS 数据集的加密密钥

`zfs-change-key(8)` 是 `zfs-load-key(8)` 的历史别名。

`zfs-unload-key(8)` 是 `zfs-load-key(8)` 的历史别名。

## 概述

```sh
zfs load-key [-nr] [-L keylocation] -a | filesystem
zfs unload-key [-r] -a | filesystem
zfs change-key [-l] [-o keylocation=value] [-o keyformat=value] [-o pbkdf2iters=value] [-o user:prop=value] filesystem
zfs change-key -i [-l] filesystem
```

## 说明

### `zfs load-key [-nr] [-L keylocation] -a | filesystem`

载入 `filesystem` 的密钥，使该数据集以及所有继承 `keylocation` 属性的子数据集可以被访问。密钥将按 `keyformat` 属性指定的格式、`keylocation` 属性指定的位置提供。注意，如果 `keylocation` 设置为 `prompt`，终端将交互等待输入密钥。加载密钥不会自动挂载数据集。如果需要该功能，`zfs mount -l` 会请求密钥并挂载数据集（参见 zfs-mount(8)）。对于用户登录时的自动化密钥管理，pam_zfs_key(8) 可以在支持 PAM 的系统上加载密钥并挂载加密的主目录。密钥加载后，`keystatus` 属性将变为 `available`。

#### `-r`

递归载入指定文件系统及所有后代加密根的密钥。

#### `-a`

载入所有已导入池中所有加密根的密钥。

#### `-n`

执行空操作（no-op）的 `load-key` 试运行。这只让 `zfs` 检查所提供的密钥是否正确。即使密钥已经加载，此命令也可以运行。

#### `-L keylocation`

使用 `keylocation` 而不是 `keylocation` 属性。这不会更改数据集上该属性的值。注意，如果与 `-r` 或 `-a` 一起使用，`keylocation` 只能指定为 `prompt`。

### `zfs unload-key [-r] -a | filesystem`

从 ZFS 卸载密钥，移除访问该数据集以及所有继承 `keylocation` 属性的子数据集的能力。这要求数据集当前未打开也未挂载。密钥卸载后，`keystatus` 属性将变为 `unavailable`。

#### `-r`

递归卸载指定文件系统及所有后代加密根的密钥。

#### `-a`

卸载所有已导入池中所有加密根的密钥。

### `zfs change-key [-l] [-o keylocation=value] [-o keyformat=value] [-o pbkdf2iters=value] [-o user:prop=value] filesystem`、`zfs change-key -i [-l] filesystem`

更改用于访问数据集的用户密钥（例如口令短语）。此命令要求该数据集的现有密钥已加载。此命令还可用于按需更改 `keylocation`、`keyformat` 与 `pbkdf2iters` 属性，以及设置用户属性。如果该数据集此前不是加密根，它将变为加密根。或者，可以提供 `-i` 标志，使加密根改为继承父数据集的密钥。

如果用户密钥泄露，`zfs change-key` 未必能保护已有数据或新写入的数据免受攻击。新写入的数据将继续使用与现有数据相同的 master key 加密。如果攻击者获取了用户密钥以及对应的被包裹的 master key，则 master key 视为泄露。目前，`zfs change-key` 不会覆盖磁盘上之前的被包裹 master key，因此它在一段不确定的时间内仍可通过取证分析访问。

发生 master key 泄露时，理想情况下应将驱动器安全擦除，以移除所有旧数据（这些数据可以用泄露的 master key 读取），然后创建新池并把数据复制回去。可以通过创建新数据集、复制数据（例如使用 `zfs send | zfs recv`），然后在硬件支持时用 `zpool trim -secure` 清除空闲空间、否则用 `zpool initialize`，来近似实现原地擦除。

#### `-l`

确保在尝试更改密钥之前先加载密钥。这实际上等同于运行 `zfs load-key filesystem`；`zfs change-key filesystem`

#### `-o property=value`

允许用户在更改密钥时设置加密密钥属性（`keyformat`、`keylocation` 与 `pbkdf2iters`）与用户属性。这是数据集创建后更改 `keyformat` 与 `pbkdf2iters` 的唯一方式。

#### `-i`

指示 zfs 让 `filesystem` 继承其父数据集的密钥。注意，此命令只能在与加密父数据集关联的加密根上运行。

### 加密

启用 `encryption` 特性即可创建加密的文件系统与卷。ZFS 将加密文件与卷数据、文件属性、ACL、权限位、目录列表、FUID 映射以及 `userused`/`groupused` 数据。ZFS 不会加密与池结构相关的元数据，包括数据集与快照名称、数据集层级、属性、文件大小、文件空洞以及去重表（尽管去重后的数据本身是加密的）。

密钥轮换由 ZFS 管理。更改用户密钥（例如口令短语）不需要重新加密整个数据集。在加密密钥未加载的情况下，数据集仍可执行 scrub、resilver、重命名与删除操作（有关密钥加载的更多信息，参见 `load-key` 子命令）。

创建加密数据集时，需要在创建时指定 `encryption` 与 `keyformat` 属性，并可选择指定 `keylocation` 与 `pbkdf2iters`。输入加密密钥后，所创建的数据集将成为加密根。所有后代数据集默认从加密根继承其加密密钥，这意味着对加密根加载、卸载或更改密钥，会隐式地对所有继承的数据集做同样的操作。如果不需要这种继承，只需在创建子数据集时提供一个 `keyformat`，或使用 `zfs change-key` 断开现有关系、在子数据集上创建一个新的加密根。注意，子数据集的 `keyformat` 可以与父数据集相同，但仍然会创建新的加密根；而且仅更改 `encryption` 属性不会创建新的加密根，那只会使用不同的密码套件，但仍沿用其加密根的相同密钥。唯一例外是克隆始终使用其源数据集的加密密钥。由于该例外，某些加密相关属性（即 `keystatus`、`keyformat`、`keylocation` 与 `pbkdf2iters`）不像其他 ZFS 属性那样继承，而是使用由其加密根决定的值。加密根的继承关系可以通过只读的 `encryptionroot` 属性进行跟踪。

加密会改变一些 ZFS 操作的行为。加密在压缩之后应用，因此压缩率得以保留。通常 ZFS 中的校验和为 256 位，但对于加密数据，校验和由用户所选校验和的 128 位与加密套件的 128 位 MAC 组成，这可为数据提供抵御恶意篡改的额外保护。启用加密后仍可以进行去重，但出于安全考虑，数据集只会与自身、其快照及其克隆进行去重。

加密数据集有一些限制。加密数据不能通过 `embedded_data` 特性嵌入。加密数据集不能把 `copies` 设为 **3**，因为实现把部分加密元数据存储在本应存放第三个副本的位置。由于压缩在加密之前应用，如果访问数据的应用程序允许这样做，数据集可能会受到类似 CRIME 的攻击。加密环境下的去重会泄露数据集中哪些块等价的信息，并且每写入一个块都会产生额外的 CPU 开销。

## 参考文献

zfsprops(7)、pam_zfs_key(8)、zfs-create(8)、zfs-set(8)

2026 年 1 月 30 日
