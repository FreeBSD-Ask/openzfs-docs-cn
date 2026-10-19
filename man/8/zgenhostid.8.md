# zgenhostid(8)

## 名称

`zgenhostid` — 生成主机 ID 并写入 `/etc/hostid`

## 概述

```sh
zgenhostid [-f] [-o 文件名] [主机 ID]
```

## 说明

创建 `/etc/hostid` 文件并在其中存储主机 ID。如果提供了主机 ID，则校验并存储该值；否则随机生成一个 ID。

## 选项

### `-h`

显示命令行选项的摘要。

### `-f`

允许覆盖输出文件。

### `-o 文件名`

写入 `filename`，而不是默认的 `/etc/hostid`。

### `主机 ID`

指定要写入 `/etc/hostid` 的值。它应为 1 到 2^32-1 之间的数字；如果为 **0**，则生成随机 ID。该值在你的各系统之间**必须**唯一，并且**必须**是 8 位长的十六进制数，可以选择加上“0x”前缀。

## 文件

`/etc/hostid`

## 示例

### 生成随机主机 ID 并存储

```sh
# zgenhostid
```

### 将 libc 生成的主机 ID 记录到 /etc/hostid

```sh
# zgenhostid "$(hostid)"
```

### 将自定义主机 ID（0xdeadbeef）记录到 /etc/hostid

```sh
# zgenhostid deadbeef
```

### 将自定义主机 ID（0x01234567）记录到 `/tmp/hostid`，并在文件存在时覆盖

```sh
# zgenhostid -f -o /tmp/hostid 0x01234567
```

## 参考文献

genhostid(1)、hostid(1)、sethostid(3)、spl(4)

## 历史

`zgenhostid` 模拟 genhostid(1) 工具，为不包含该工具或不提供 sethostid(3) 函数的系统而提供。

2022 年 7 月 11 日
