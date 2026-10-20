# zfs-program(8)

## 名称

`zfs-program` — 执行 ZFS 通道程序

## 概述

```sh
zfs program [-jn] [-t 指令数上限] [-m 内存上限] 池名 脚本 [脚本参数]
```

## 说明

ZFS 通道程序接口允许以 Lua 脚本的方式编程执行 ZFS 管理操作。整个脚本以原子方式执行，期间不会有其他管理操作并发生效。通道程序脚本可以使用一套 ZFS 调用库。通道程序只能以 root 权限运行。

运行通道程序脚本使用的是一个经过修改的 Lua 5.2 解释器。Lua 5.2 手册见 <http://www.lua.org/manual/5.2/>。

由 `script` 给定的通道程序将在 `pool` 上运行，任何访问或修改其他池的尝试都会导致错误。

## 选项

### `-j`、`--json`

以 JSON 格式显示通道程序的输出。指定此标志且标准输出为空时，表示通道程序遇到了错误。错误的详细信息将以纯文本形式打印到标准错误。

### `-n`

执行只读通道程序，速度更快。程序不能通过调用 `zfs.sync` 子模块中的函数来更改磁盘状态。该程序可用于收集信息（例如属性），以及判断变更是否会成功（`zfs.check.*`）。只读通道程序也可以在以只读方式导入的池上运行。其他通道程序则要求池可写。不使用此标志时，必须先把所有待处理的更改同步到磁盘，通道程序才能完成执行。

### `-t instruction-limit`

限制执行的 Lua 指令数量。如果通道程序执行的指令超过指定数量，它将被停止并返回错误。默认限制为 1000 万条指令，最大可设置为 1 亿条指令。

### `-m memory-limit`

内存上限，以字节为单位。如果通道程序试图分配的内存超过给定上限，它将被停止并返回错误。默认内存上限为 10 MiB，最大可设置为 100 MiB。

其余所有参数字符串都会直接传递给 Lua 脚本，具体见下文“Lua 接口”一节。

## Lua 接口

通道程序既可以从命令行调用，也可以通过库调用 `lzc_channel_program()` 来调用。

### 参数

传递给通道程序的参数会被转换为一个 Lua 表。如果从命令行调用，传递给 Lua 脚本的额外参数将以数组的形式提供，存储在参数表中键为 `argv` 的条目里：

```lua
args = ...
argv = args["argv"]
-- argv == {1="arg1", 2="arg2", ...}
```

如果通过 libzfs 接口调用，则可以向通道程序传递任意的参数列表，在 Lua 中通过同样的 `...` 语法访问：

```lua
args = ...
-- args == {"foo"="bar", "baz"={...}, ...}
```

注意，由于 Lua 数组的索引从 1 开始，通过 libzfs 接口传递给 Lua 的数组，其索引会加 1。也就是说，传递给通道程序的 C 数组中 `arr[0]` 处的元素，从 Lua 访问时位于 `arr[1]` 处。

### 返回值

Lua 的 return 语句采用如下形式：`return ret0, ret1, ret2, ...`

在通道程序脚本内部，return 语句可以返回多个值；但试图从通道程序顶层返回多于一个值是不允许的，会抛出错误。不过，仍然可以返回包含多个值的表。如果从命令行调用，return 语句：

```lua
a = {foo="bar", baz=2}
return a
```

其输出格式如下：

```sh
Channel program fully executed with return value:
    return:
        baz: 2
        foo: 'bar'
```

### 致命错误

如果通道程序在运行过程中遇到致命错误，将返回非零退出状态。如果可以获得关于该错误的更多信息，将返回一个仅含单个元素的列表，其中详细描述该错误：

`error: "error string, including Lua stack trace"`

如果返回了致命错误，通道程序可能完全没有执行，可能执行了一部分，也可能已经完整执行但未能把返回值传回用户态。

如果通道程序耗尽了指令或内存上限，将产生致命错误，程序会被停止，处于部分执行的状态。系统不会尝试撤销或回退已经执行的任何操作。注意，对于相同的输入和文件系统状态，通道程序使用的指令数与内存量都是确定的，因此只要一个通道程序成功运行过一次，就可以保证它在规模相近的系统上也能成功运行完毕。

如果通道程序试图返回过大的值，程序会完整执行，但会以非零状态码退出，并且没有返回值。

**注意**：ZFS API 函数在正确调用时不会产生致命错误，它们会返回一个错误码，通道程序继续执行。有关各函数错误返回码的具体信息，参见下文“ZFS API”一节。

### Lua 与 C 之间的值转换

通过 libzfs 接口调用通道程序时，需要把参数与返回值从 Lua 值转换为对应的 C 值，反之亦然。

C 中的 nvlist 值与 Lua 表之间存在对应关系。通道程序返回的 Lua 表会被递归转换为 nvlist，表中的值会被转换为各自自然的等价类型：

| Lua 值 | C 等价类型 |
| ------ | ---------- |
| `string` | `string` |
| `number` | `int64` |
| `boolean` | `boolean_value` |
| `nil` | `boolean`（无值） |
| `table` | `nvlist` |

同样，表的键会被替换为对应的字符串形式：

| Lua 键类型 | 转换结果 |
| ---------- | -------- |
| `string` | 无变化 |
| `number` | 有符号十进制字符串（`"%lld"`） |
| `boolean` | 字符串形式的 `true` 或 `false` |

如果表的键字符串发生冲突（例如字符串 `true` 与布尔值 `true`），将导致致命错误。

Lua 数字在内部表示为有符号 64 位整数。

## Lua 标准库

以下 Lua 内置基础库函数可用：

`assert`、`rawlen`、`collectgarbage`、`rawget`、`error`、`rawset`、`getmetatable`、`select`、`ipairs`、`setmetatable`、`next`、`tonumber`、`pairs`、`tostring`、`rawequal`、`type`。

`coroutine`、`string` 与 `table` 内置子模块中的所有函数同样可用。这些模块的完整列表与文档见 Lua 手册。

以下基础库函数已被禁用，无法在通道程序中使用：

`dofile`、`loadfile`、`load`、`pcall`、`print`、`xpcall`。

## ZFS API

### 函数参数

每个 API 函数都接受一组固定的必选位置参数，以及可选的关键字参数。例如，destroy 函数接受一个位置字符串参数（要销毁的数据集的名称）和一个可选的关键字布尔参数 `defer`。使用圆括号为 Lua 函数指定参数时，只能使用位置参数：

`zfs.sync.destroy("rpool@snap")`

要使用关键字参数，必须以单个参数调用函数，该参数是一个 Lua 表，其中的条目把整数映射到位置参数、把字符串映射到关键字参数：

`zfs.sync.destroy({1="rpool@snap", defer=true})`

Lua 语言允许用花括号代替圆括号，作为这种调用约定的语法糖：

`zfs.sync.snapshot({"rpool@snap", defer=true})`

### 函数返回值

API 函数成功时返回 0。失败时返回一个错误码，通道程序继续执行。除非发生不可恢复的内部文件系统错误，API 函数不会产生致命错误。

除返回错误码外，一些函数还会返回描述错误原因的额外细节。这些额外细节作为第二个返回值给出，并且始终是一个 Lua 表；如果没有返回错误细节，则为 `Nil`。错误细节表中包含哪些键，取决于具体的函数与错误情形。调用这类函数时，可以只期望接收一个返回值：

`errno = zfs.sync.promote(dataset)`

或者，也可以获取错误细节：

```lua
errno, details = zfs.sync.promote(dataset)
if (errno == EEXIST) then
    assert(details ~= Nil)
    list_of_conflicting_snapshots = details
end
```

为便于在通道程序中使用，为 API 函数的错误返回码定义了以下全局别名：

`EPERM`、`ECHILD`、`ENODEV`、`ENOSPC`、`ENOENT`、`EAGAIN`、`ENOTDIR`、`ESPIPE`、`ESRCH`、`ENOMEM`、`EISDIR`、`EROFS`、`EINTR`、`EACCES`、`EINVAL`、`EMLINK`、`EIO`、`EFAULT`、`ENFILE`、`EPIPE`、`ENXIO`、`ENOTBLK`、`EMFILE`、`EDOM`、`E2BIG`、`EBUSY`、`ENOTTY`、`ERANGE`、`ENOEXEC`、`EEXIST`、`ETXTBSY`、`EDQUOT`、`EBADF`、`EXDEV`、`EFBIG`。

### API 函数

有关任何 ZFS 管理操作确切行为的详细说明，参见主手册页 zfs(8)。

#### `zfs.debug(msg)`

在 `zfs_dbgmsg` 日志中记录一条调试消息。这些消息的日志可以通过 mdb 的 `::zfs_dbgmsg` 命令打印，也可以通过运行以下命令实时监视：

```sh
dtrace -n 'zfs-dbgmsg{trace(stringof(arg0))}'
```

* `msg (string)` — 要打印的调试消息。

#### `zfs.exists(dataset)`

如果给定的数据集存在，则返回 true；否则返回 false。如果数据集不在目标池中，将抛出致命错误。也就是说，在运行于 rpool 上的通道程序中，`zfs.exists("rpool/nonexistent_fs")` 返回 false，而 `zfs.exists("somepool/fs_that_may_exist")` 会报错。

* `dataset (string)` — 要检查是否存在的数据集。必须位于目标池中。

#### `zfs.get_prop(dataset, property)`

返回两个值。第一个是字符串、数字或表，包含给定数据集的属性值。第二个是字符串，包含属性的来源（即设置该属性的数据集的名称；如果属性是只读的，则为 `nil`）。如果数据集无效或属性不存在，将抛出 Lua 错误。注意，Lua 只支持 int64 数字类型，而 ZFS 的数字属性是 uint64。这意味着非常大的值（例如 GUID）可能会回绕并显示为负数。

* `dataset (string)` — 要从中获取属性的文件系统或快照路径。
* `property (string)` — 要获取的属性的名称。支持所有文件系统、快照与卷属性，`mounted` 与 `iscsioptions` 除外。还支持 `written@snap`、`written#bookmark` 属性，以及 `user|groupquota|used@id` 形式的属性，但 id 必须为数字形式。

#### `zfs.sync` 子模块

`zfs.sync` 子模块包含修改磁盘状态的函数。它们在“同步上下文”（syncing context）中执行。

sync 子模块的可用函数如下：

##### `zfs.sync.clone(snapshot, newdataset)`

从快照创建新的文件系统。如果文件系统创建成功则返回 0，否则返回非零错误码。

**注意**：由于通道程序的一般性限制，以这种方式创建的文件系统不会被挂载，无论 `mountpoint` 与 `canmount` 属性的值是什么。这一限制将来可能会被移除，因此建议你设置 `mountpoint=none`、`canmount=off` 或 `noauto`，以避免出现意外情况。

* `snapshot (string)` — 要克隆的源快照的名称。
* `newdataset (string)` — 要创建的目标数据集的名称。

##### `zfs.sync.destroy(dataset[, defer=true|false])`

销毁给定的数据集。销毁成功则返回 0；如果数据集无法销毁（例如数据集存在处于活动状态的子数据集或克隆），则返回非零错误码。

* `dataset (string)` — 要销毁的文件系统或快照。
* `defer (boolean)`（可选） — 仅对销毁快照有效。如果设置为 `true`，并且该快照存在保留（hold）或克隆，则允许把该快照标记为延迟删除，而不是直接失败。

##### `zfs.sync.inherit(dataset, property)`

清除给定数据集中的指定属性，使其从祖先数据集继承；如果没有祖先设置该属性，则恢复为默认值。`zfs inherit -S` 选项尚未实现。成功则返回 0；如果属性无法清除，则返回非零错误码。

* `dataset (string)` — 包含要清除的属性的文件系统或快照。
* `property (string)` — 要清除的属性。允许的属性与 `zfs inherit` 命令相同。

##### `zfs.sync.promote(dataset)`

把给定的克隆提升为文件系统。提升成功则返回 0，否则返回非零错误码。如果返回 EEXIST，第二个返回值将是一个数组，其中包含该克隆的快照中与父文件系统的快照名称冲突的快照。

* `dataset (string)` — 要提升的克隆。

##### `zfs.sync.rollback(filesystem)`

把数据集回滚到上一个快照。回滚成功则返回 0，否则返回非零错误码。可以对文件系统或 zvol 执行回滚，但不能对快照或已挂载的数据集执行回滚。文件系统处于挂载状态时返回 EBUSY。

* `filesystem (string)` — 要回滚的文件系统。

##### `zfs.sync.set_prop(dataset, property, value)`

在数据集上设置给定的属性。目前仅支持用户属性。设置成功则返回 0，否则返回非零错误码。

* `dataset (string)` — 要设置属性的数据集。
* `property (string)` — 要设置的属性。
* `value (string)` — 要设置的属性值。

##### `zfs.sync.snapshot(dataset)`

为文件系统创建快照。如果快照创建成功则返回 0，否则返回非零错误码。

**注意**：在任何早于旧式（legacy）版本 27 的池上，创建快照都会失败。要允许从 ZCP 脚本创建快照，必须升级池。

* `dataset (string)` — 要创建的快照的名称。

##### `zfs.sync.rename_snapshot(dataset, oldsnapname, newsnapname)`

重命名文件系统或卷的快照。如果快照重命名成功则返回 0，否则返回非零错误码。

* `dataset (string)` — 快照的父数据集的名称。
* `oldsnapname (string)` — 快照的原名称。
* `newsnapname (string)` — 快照的新名称。

##### `zfs.sync.bookmark(source, newbookmark)`

为现有的源快照或书签创建书签。如果新书签创建成功则返回 0，否则返回非零错误码。

**注意**：创建书签要求启用相应的池特性标志。

* `source (string)` — 现有快照或书签的完整名称。
* `newbookmark (string)` — 新书签的完整名称。

#### `zfs.check` 子模块

`zfs.sync` 子模块中的每个函数，在 `zfs.check` 中都有一个对应的函数，用于对同一操作执行“空运行”（dry run）。每个函数接受的参数与其对应的 `zfs.sync` 函数相同：如果操作将会成功则返回 0；如果将会失败则返回非零错误码，以及其他错误细节。也就是说，除了不实际执行所请求的更改之外，每个函数的行为都与对应的 sync 函数相同。例如，如果 `zfs.sync.destroy("fs")` 能够成功销毁该数据集，`zfs.check.destroy("fs")` 就会返回 0。

可用的 `zfs.check` 函数如下：

* `zfs.check.clone(snapshot, newdataset)`
* `zfs.check.destroy(dataset[, defer=true|false])`
* `zfs.check.promote(dataset)`
* `zfs.check.rollback(filesystem)`
* `zfs.check.set_property(dataset, property, value)`
* `zfs.check.snapshot(dataset)`

#### `zfs.list` 子模块

`zfs.list` 子模块提供用于遍历数据集与属性的函数。这些函数不返回表，而是充当 Lua 迭代器，通常按如下方式使用：

```lua
for child in zfs.list.children("rpool") do
    ...
end
```

可用的 `zfs.list` 函数如下：

##### `zfs.list.clones(snapshot)`

遍历给定快照的所有克隆。

* `snapshot (string)` — 必须是当前池中的有效快照路径。

##### `zfs.list.snapshots(dataset)`

遍历给定数据集的所有快照。每个快照都以包含完整数据集名称的字符串形式返回，例如 `pool/fs@snap`。

* `dataset (string)` — 必须是有效的文件系统或卷。

##### `zfs.list.children(dataset)`

遍历给定数据集的所有直接子数据集。每个子数据集都以包含完整数据集名称的字符串形式返回，例如 `pool/fs/child`。

* `dataset (string)` — 必须是有效的文件系统或卷。

##### `zfs.list.bookmarks(dataset)`

遍历给定数据集的所有书签。每个书签都以包含完整数据集名称的字符串形式返回，例如 `pool/fs#bookmark`。

* `dataset (string)` — 必须是有效的文件系统或卷。

##### `zfs.list.holds(snapshot)`

遍历给定快照上的所有用户保留。每个保留以一对值的形式返回：保留的标签，以及创建该保留时的时间戳（自纪元起的秒数）。

* `snapshot (string)` — 必须是有效的快照。

##### `zfs.list.properties(dataset)`

是 `zfs.list.user_properties` 的别名（参见相应条目）。

* `dataset (string)` — 必须是有效的文件系统、快照或卷。

##### `zfs.list.user_properties(dataset)`

遍历给定数据集的所有用户属性。迭代的每一步都会输出属性名、属性值及其来源。如果数据集无效，将抛出 Lua 错误。

* `dataset (string)` — 必须是有效的文件系统、快照或卷。

##### `zfs.list.system_properties(dataset)`

返回一个字符串数组，其中是给定数据集的有效系统属性（非用户定义属性）的名称。如果数据集无效，将抛出 Lua 错误。

* `dataset (string)` — 必须是有效的文件系统、快照或卷。

## 示例

### 示例 1

以下通道程序以简单直接的方式递归销毁一个文件系统及其所有快照和子数据集。注意，其中不涉及任何错误处理或报告。

```lua
function destroy_recursive(root)
    for child in zfs.list.children(root) do
        destroy_recursive(child)
    end
    for snap in zfs.list.snapshots(root) do
        zfs.sync.destroy(snap)
    end
    zfs.sync.destroy(root)
end
destroy_recursive("pool/somefs")
```

### 示例 2

同一个通道程序还有一个更详细、更健壮的版本，它会正确地检测并报告错误，并且把要销毁的数据集作为命令行参数传入，如下所示：

```lua
succeeded = {}
failed = {}

function destroy_recursive(root)
    for child in zfs.list.children(root) do
        destroy_recursive(child)
    end
    for snap in zfs.list.snapshots(root) do
        err = zfs.sync.destroy(snap)
        if (err ~= 0) then
            failed[snap] = err
        else
            succeeded[snap] = err
        end
    end
    err = zfs.sync.destroy(root)
    if (err ~= 0) then
        failed[root] = err
    else
        succeeded[root] = err
    end
end

args = ...
argv = args["argv"]

destroy_recursive(argv[1])

results = {}
results["succeeded"] = succeeded
results["failed"] = failed
return results
```

### 示例 3

以下函数执行一次强制的 promote 操作：尝试提升给定的克隆，并销毁所有与之冲突的快照。

```lua
function force_promote(ds)
   errno, details = zfs.check.promote(ds)
   if (errno == EEXIST) then
       assert(details ~= Nil)
       for i, snap in ipairs(details) do
           zfs.sync.destroy(ds .. "@" .. snap)
       end
   elseif (errno ~= 0) then
       return errno
   end
   return zfs.sync.promote(ds)
end
```

2025 年 6 月 5 日
