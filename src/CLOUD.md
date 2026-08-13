# クラウド定期実行（毎朝のSlack投稿）

このディレクトリは、ローカル `~/Projects/houjinzei-drill/` のミラー。
クラウドのルーティン（claude.ai の Routines）がこのリポジトリを clone して使う。

## クラウド側でやること

```bash
cd src
TZ=Asia/Tokyo python3 post_to_slack.py --dry-run
```

- クラウドは UTC で動くので **`TZ=Asia/Tokyo` を必ず付ける**。付け忘れると 6:00 JST の実行時に前日の範囲が出る。
- 出力された本文をそのまま Slack コネクタで `#法人税ー試験対策`（channel_id `C0BNFL4NA2D`）へ 1通だけ投稿する。
- `--date YYYY-MM-DD` で任意の日付の範囲を作れる（投稿漏れの後追い用）。

## ローカルからの同期

`bash ~/Projects/houjinzei-drill/deploy.sh` が index.html と src/ の両方を同期して push する。
`content.py` を直したら必ず deploy.sh を通すこと（src/ が古いとクラウドの出題が古くなる）。
