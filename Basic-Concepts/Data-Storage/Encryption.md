# 原生加密

ZFS 可以自行加密数据集，无需 LUKS 或 GELI 这样的独立层。加密是按数据集设置的属性，因此单个存储池可以同时容纳加密与未加密的数据集，每个加密数据集可以有自己的密钥，并且在密钥未加载时存储池仍完全可管理——可导入、可 scrub、可 resilver、可复制。

原生加密需要 `encryption` 存储池特性。

## 加密与不加密的边界

加密的内容：

* 文件与卷数据
* 文件属性、ACL 与权限位
* 目录列表
* FUID 映射以及 `userused`/`groupused` 计量数据
* ZFS 意图日志（ZIL）

不加密的内容：

* 数据集与快照的名称
* 数据集层级
* 数据集属性
* 文件大小以及文件中空洞的位置
* 去重表（被去重的数据本身是加密的）

分界线按对象类型划定，第二份清单之所以如此，原因在于 **块树** 。只有叶子块被加密；间接块（层级 > 0）经过认证，但保持明文，并携带覆盖其下各 MAC 的 MAC。因此块指针在没有密钥时仍可读——这恰恰使存储池得以在密钥未加载时被 scrub、resilver、释放与复制，也同样泄露了每个文件有多大、它的空洞在哪里、以及数据集存了多少数据。

这就是让存储池在无密钥时仍可管理的权衡。如果你在意的是数据集是否存在及其名称，或者它们的大小与变化模式本身就属敏感信息，那么原生加密不是应对这一点的正确层次——应改在 ZFS 之下使用全盘加密，或者两者兼用。

## 创建加密数据集

`encryption` 与 `keyformat` 必须在创建时给出，可选给出 `keylocation` 与 `pbkdf2iters`。加密套件此后无法更改。

```sh
# 口令，交互式输入
zfs create -o encryption=on -o keyformat=passphrase pool/secret

# 来自文件的原始密钥
dd if=/dev/urandom bs=32 count=1 of=/root/pool.key
zfs create -o encryption=on \
           -o keyformat=raw \
           -o keylocation=file:///root/pool.key \
           pool/secret
```

`encryption=on` 选用当前默认套件，即 `aes-256-gcm`。可显式指定的套件有 `aes-128-ccm`、`aes-192-ccm`、`aes-256-ccm`、`aes-128-gcm`、`aes-192-gcm` 与 `aes-256-gcm`。在具备 AES 加速的硬件上，GCM 模式通常更快。

`keyformat` 取以下之一：

### `passphrase`

8 至 512 字节，使用前经 PBKDF2 处理。迭代次数由 `pbkdf2iters` 设定——当前默认为 350000，最小值为 100000。

### `raw`

恰好 32 字节的随机数据，与所选套件无关。

### `hex`

同样的 32 字节，以十六进制书写。

`keylocation` 指定密钥的读取位置：`prompt`（默认——交互式）、`file:///absolute/path`，或 `http://` / `https://` 地址，后者使机器可以在启动时从密钥服务器获取密钥。

## 加密根与继承

你为其提供密钥的数据集成为 **加密根** 。后代默认继承其密钥，因此在根上加载、卸载或更改密钥，对其下所有数据集同样生效。只读属性 `encryptionroot` 显示某数据集当前使用哪个根。

要打破这一关系并让子数据集拥有自己的密钥，在创建它时提供 `keyformat`，或之后对它运行 `zfs change-key`。注意：

* 子数据集的 `keyformat` 可以与父级相同，它仍会成为独立的加密根；
* 仅设置 `encryption` 属性*不会*创建新的加密根——它只是用同一密钥换用不同的加密套件；
* 克隆始终使用其原版的密钥。

正是由于最后一项例外，`keystatus`、`keyformat`、`keylocation` 与 `pbkdf2iters` 不像其他 ZFS 属性那样继承：它们的有效值来自加密根。

## 加载与卸载密钥

```sh
zfs load-key pool/secret          # 提示输入，或读取 keylocation
zfs load-key -a                   # 每个已导入池中的每个加密根
zfs load-key -r pool              # 递归处理 pool 之下的所有加密根
zfs load-key -n pool/secret       # 试运行：只验证密钥是否正确

zfs mount pool/secret             # 加载密钥不会挂载

zfs unload-key pool/secret        # 数据集不得处于打开或挂载状态
```

`zfs mount -l` 一步请求密钥并挂载。密钥加载后 `keystatus` 属性为 `available`，未加载时为 `unavailable`：

```sh
zfs get -r keystatus,encryptionroot pool
```

在带 PAM 的系统上，[pam_zfs_key(8)](../../man/8/pam_zfs_key.8.md) 可以在登录时加载用户密钥并挂载其加密的家目录。

## 更改密钥

`zfs change-key` 用新的用户密钥重新包装主密钥。它不重新加密数据，因此无论数据集多大都是瞬时完成的。现有密钥必须已加载（或使用 `-l` 先加载）。

```sh
zfs change-key pool/secret
zfs change-key -o keyformat=passphrase -o pbkdf2iters=500000 pool/secret
zfs change-key -i pool/secret/child      # 放弃自有密钥，继承父级的
```

这也是创建后更改 `keyformat` 与 `pbkdf2iters` 的唯一方式。

**更改密钥并不能撤销已经发生的泄露。** 新写入的数据仍使用与既有数据相同的主密钥，因此攻击者若同时获得了用户密钥*和*相应的已包装主密钥，仍能读取此后写入的内容。旧的已包装主密钥不在磁盘上被覆盖，可能在无法确定的一段时间内仍可通过取证分析恢复。

如果主密钥已泄露，正确的应对是安全擦除这些驱动器、创建新存储池并把数据复制回去。可以在原地近似做到：创建新数据集，把数据复制进去（例如使用 `zfs send | zfs recv`），然后在硬件支持时用 `zpool trim --secure` 清除空闲空间，否则用 `zpool initialize`。

## 原始发送

`zfs send -w`（`--raw`）完全按数据在磁盘上的原样发送，仍处于加密状态。这意味着：

* 无需加载任何密钥即可完成备份；
* 接收端机器不必被信任——它无法读取数据，也无法在不被下一次读取发现的情况下改动数据；
* 接收到的数据集保留来自源端的加密设置及其密钥。

```sh
zfs send -w pool/secret@daily | ssh backup zfs receive -u tank/secret
```

对加密数据集执行非 raw 发送需要加载密钥，并产生明文流，随后按目标端自身的属性进行加密（或不加密）。参见[发送与接收](../Operations/Send-and-Receive.md)。

## 与其他特性的相互作用

**压缩。** 加密在压缩之后应用，因此压缩率得以保留。另一面是，如果访问该数据集的应用程序让攻击者能够影响哪些内容与机密数据一同被压缩，该数据集就可能遭受类似 CRIME 的攻击。

**校验和。** 对加密数据，通常的 256 位校验和变为所选校验和的 128 位加上来自加密套件的 128 位 MAC。MAC 提供的保护针对的是*恶意*篡改，而不仅是意外损坏。

**去重** 仍然可用，但出于安全考虑，数据集只与自身、其快照及其克隆进行去重。加密下的去重会泄露数据集中哪些块相同，并且每写入一个块都有额外的 CPU 开销。

**内嵌数据。** 加密数据无法使用 `embedded_data` 特性。

**`copies=3`** 在加密数据集上不可用——其实现把加密元数据存放在第三份副本本应占据的位置。

## 延伸阅读

* [zfs-load-key(8)](../../man/8/zfs-load-key.8.md)——含完整的“加密”一节
* [zfs-change-key(8)](../../man/8/zfs-load-key.8.md)、[zfs-unload-key(8)](../../man/8/zfs-load-key.8.md)
* [zfsprops(7)](../../man/7/zfsprops.7.md)——`encryption`、`keyformat`、`keylocation`、`pbkdf2iters`、`keystatus`、`encryptionroot`
* [pam_zfs_key(8)](../../man/8/pam_zfs_key.8.md)
