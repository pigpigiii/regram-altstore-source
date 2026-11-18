# 白日梦的源

Regram（Telegram 版）、iPadn（精简版）、Erosion-CN 三个 App 的更新汇总源，自动跟各自 GitHub 最新正式版。只做汇总，不改包、不重新打包。

| App | 上游 | 包名 | 当前版 |
| --- | --- | --- | --- |
| Regram | RegramDev/Regram-ios | app.swiftgram.ios | 13.2.34663（原版 13.2 b34663） |
| iPadn | mengangs/ipadn | app.local.iPadn | 2.2.1（精简版 lite） |
| Erosion | Kianuni/Erosion-CN | com.jbdotparty.Erosion | 1.0.5 |

注意：这个 Regram 是 Telegram 第三方客户端，不是 Instagram 那个同名 Regram，别混了。Erosion 官方自己也有源（`https://raw.githubusercontent.com/Kianuni/Erosion-CN/main/apps.json`），这里只是汇总，方便在 LBox 里一次看三个。

## 怎么加

源地址（仓库建好后把下面换成实际地址）：

`https://raw.githubusercontent.com/OWNER/REPO/main/apps.json`

- **LBox**：打开 LBox → 加源 → 粘贴上面地址。有新版会提醒，点更新保留数据。
- **SideStore / AltStore**：源 → 右上角 + → 粘贴上面地址。

## Regram 在 LiveContainer 里怎么更新

SideStore 源装出来的是签名版真 App，和 LiveContainer 里那份是两份，数据不通。LiveContainer 里那份更新办法：

1. 在源里（或 LBox 里）看到新版，下载 IPA
2. LiveContainer → App 页 → 点 + → 选 IPA 导入覆盖
3. 别先删旧的，删了数据就没了

Regram 自带的内置更新走证书签名 / TrollStore，也不是给 LiveContainer 用的，别在里面点安装。

## 自动更新

`.github/workflows/update.yml` 每天 08:00 跑一次 `update.py`，查三个上游的最新正式版，有变化就更新 `apps.json` 并提交。Regram 的版本号写成 `13.2.34663` 这种形式，是因为它同一个 13.2 下面有很多构建号，不把构建号写进版本号，源就检测不到更新。
