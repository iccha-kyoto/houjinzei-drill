# 法人税法ドリル

相続税の直前演習と同じ「墨消しタップ」方式。ただし**積み上げ型**に設計を変えてある。

- 理論は `START`（既定 2026-09-07）から**毎週月曜に2題ずつ解禁**される
- 今週の新規2題は毎日出る。それ以前の既習分から4題をローテーション（間隔反復）
- 別表四・計算・改正論点は**最初から全部回る**（教材が届く前でも使える）
- 開講前は「助走期間」表示になり、理論タブは出ない

## ファイル

| ファイル | 役割 |
|---|---|
| `content.py` | **中身。編集するのはここだけ。** `【 】` で囲むと墨消しになる |
| `build.py` | `content.py` → `site/index.html` を生成 |
| `schedule.py` | 本日の範囲を決めるロジック。`build.py` の JS と一対一で対応 |
| `post_to_slack.py` | 本日の範囲を Slack Incoming Webhook で投稿 |

`schedule.py`（Python）と `build.py` 内の JS は同じ範囲を返すことを検証済み。
**片方を変えたらもう片方も変えること。**

## 使い方

中身を足す・直す:

```bash
cd ~/Projects/houjinzei-drill && python3 build.py
```

Slack投稿の下書き確認（POSTしない）:

```bash
python3 ~/Projects/houjinzei-drill/post_to_slack.py --dry-run
```

## 設定値

`schedule.py` と `build.py` の両方にある。

| 値 | 既定 | 意味 |
|---|---|---|
| `START` | 2026-09-07（月） | 理論の解禁開始日。教材着手日に合わせる |
| `EXAM` | 2027-08-04 | 第77回2日目（法人税法）の**予想日**。官報公告（2027年4月頃）で確定させる |
| `PER_WEEK` | 2 | 週に解禁する理論の題数 |
| `N_REVIEW` | 4 | 既習分から毎日回す題数 |

## 公開・配信

| | 状態 |
|---|---|
| GitHubリポジトリ | `iccha-kyoto/houjinzei-drill`（public）作成済 |
| ローカル配信リポジトリ | `~/houjinzei-drill-pages`（初回コミット済・**push未了**） |
| 公開URL | https://iccha-kyoto.github.io/houjinzei-drill/ （初回push＋Pages有効化の後に生きる） |
| Slackチャンネル | #法人税ー試験対策（非公開・`C0BNFL4NA2D`）作成済 |
| 定期タスク | `houjinzei-daily-drill`（毎朝6時） |
| Webhook | **未設定**。`~/.claude/secrets/slack_houjin_webhook.txt` に置くと安定する |

再デプロイ:

```bash
bash ~/Projects/houjinzei-drill/deploy.sh
```

## 中身についての注意

`content.py` の内容は**法令の条文構造をもとに書き起こした草案**であり、
理論マスター等の市販教材から転記したものではない。数値・限度額は毎年の税制改正で動くため、
**年度版教材が届いたら必ず突き合わせること**。特に次は改正頻度が高い:

- 賃上げ促進税制の要件・控除率
- 交際費の飲食費基準額（現行 1万円／令和6年4月1日以後）
- 少額減価償却資産の特例（適用期限が延長され続けている）
- 法人税率・特別税率
