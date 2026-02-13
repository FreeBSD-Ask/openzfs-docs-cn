# 分布式 RAID（dRAID）

>**注意**
>
>本页所述功能是 OpenZFS 2.1.0 版本新增的，OpenZFS 2.0.0 版本并不适用。

## 介绍

[dRAID](https://docs.google.com/presentation/d/1uo0nBfY84HIhEqGWEx-Tbm8fPbJKtIP3ICo4toOPcJo/edit) 是 raidz 的一种变体，提供集成的分布式热备盘，使重建（resilvering）更快，同时保留 raidz 的优势。dRAID vdev 由多个内部 raidz 组构成，每组包含 D 个数据设备和 P 个校验设备。这些组分布在所有子设备上，以充分利用可用的磁盘性能。这被称为校验去聚类（parity declustering），一直是研究的活跃领域。下图是简化示意，但有助于说明 dRAID 与 raidz 的关键区别。


![](../.gitbook/assets/raidz_draid.png)
