# 词典生成数据来源

本目录保存本次 0.3.0 词库实际使用的源文件，确保无需联网即可重建运行时词典。许可见仓库根目录 `THIRD_PARTY_NOTICES.md` 与 `licenses/`。

| 文件 | 上游项目 | SHA-256 |
|---|---|---|
| `8105.dict.yaml` | iDvel/rime-ice | `1f9a42b91dea6982baee2551981780271aeffd78876662b9c9f324e56b37b120` |
| `base.dict.yaml` | iDvel/rime-ice | `19f6f96f5dfe553545f36c979001a12e3f3c0316f4e23f4382960a13e93e7550` |
| `hanzi-dictionary.txt` | skishore/makemeahanzi | `744bb05d5b0742e9ee35c37791f94d56a173349b3367569e7ca11e510364d203` |
| `cjkvi-ids.txt` | cjkvi/cjkvi-ids（ids.txt） | `bfc70a8c09f9f5616ebf0543bd6681e67314e9f7ae2307e5ae8c6f15bdc5c6a6` |

这些哈希固定的是本源码包内的快照，不代表上游仓库的最新版本。升级源数据必须重新评估词典行数、碰撞率、许可和回归用例。
