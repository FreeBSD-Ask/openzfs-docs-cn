# 委托管理

`zfs allow` 让非特权用户在特定数据集上执行 ZFS 操作——创建自己的快照、设置自己的属性、接收自己的复制流——而不必交出 root 权限。

委托由存储池属性 `delegation` 控制，默认为 `on`：

```sh
zpool get delegation pool
```

## 授予与撤销

```sh
zfs allow alice snapshot,destroy,mount pool/home/alice
zfs allow -g devs create,mount,snapshot pool/scratch
zfs allow pool/home/alice              # 显示已委托的内容
zfs unallow alice snapshot pool/home/alice
```

授予对象：

* 不带前缀的名称依次按 `everyone`、用户、组解释——用 `-u` 或 `-g` 可显式指定；
* `-e`（或字面的 `everyone`）授予所有用户。

作用范围：

* `-l`——仅本数据集（locally）；
* `-d`——仅其后代；
* 两者都不用或都用——该数据集及其所有后代（默认）。

`zfs unallow` 接受相同的选择器，另加 `-r` 递归移除委托。

## 哪些内容可以委托

权限名就是 ZFS 的子命令与属性名：`snapshot`、`clone`、`send`、`receive`、`rollback`、`destroy`、`hold`、`load-key`、`compression`、`quota`、`recordsize`，等等。对数据集执行不带参数的 `zfs allow` 会打印当前的授予情况。

有些权限会隐含其他权限，这也是困惑的常见来源：

* `create` 还需要 `mount`（非稀疏卷还需要 `refreservation`）；
* `destroy`、`rollback` 与 `snapshot` 还需要 `mount`；
* `clone` 需要源文件系统中的 `create` 加 `mount`；
* `rename` 需要新父级中的 `mount` 与 `create`；
* `receive` 需要 `mount` 与 `create`，也正是它让 `zfs receive -F` 成为可能——若需要一种无法强制回滚的接收权限，请用 `receive:append`；
* `allow` 让用户可以继续向下委托，但只能委托他们自己持有的权限。

针对加密数据还存在范围更窄的发送变体：`send:raw` 只允许原始流，`send:encrypted` 只允许加密数据集的原始流——两者都防止加密数据集以解密形式被发送。参见[原生加密](../Data-Storage/Encryption.md)。

>**注意**
>
> 在 Linux 上，`mount`、`unmount`、`mountpoint`、`canmount`、`rename` 与 `share` 权限无法委托，因为 `mount(8)` 只允许 root 修改全局命名空间。由于 `create`、`destroy`、`snapshot` 等都需要 `mount`，在 Linux 上搭建完全自助的环境仍然需要 root 或 setuid 辅助程序的帮助。

## 权限集

具名权限集把若干权限归为一组，便于整组授予、日后在一处修改。集合名以 `@` 开头。

```sh
zfs allow -s @backup send,snapshot,hold,destroy pool/data
zfs allow backupuser @backup pool/data
zfs unallow -s @backup pool/data
```

## 创建时权限

`zfs allow -c` 设置创建时权限：它们被本地授予给创建新后代文件系统的人。正是这一点，让有权创建数据集的用户自动获得管理自己创建的数据集的能力。

```sh
zfs allow -c snapshot,destroy,mount pool/scratch
```

## 延伸阅读

* [zfs-allow(8)](../../man/8/zfs-allow.8.md)——完整的权限表；`zfs unallow` 是其历史别名
* [zpoolprops(7)](../../man/7/zpoolprops.7.md)——`delegation`
