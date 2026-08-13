#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""法人税法ドリル｜本日の範囲を Slack Incoming Webhook で投稿する。

標準ライブラリのみ／MCP 非依存。headless の自動実行でも動く。
--dry-run を付けると POST せず本文だけ出力する。
--date YYYY-MM-DD を付けるとその日の範囲で作る（投稿漏れの後追い用）。

Webhook URL は次のどちらかから読む（環境変数が優先）:
  1. 環境変数 HOUJIN_SLACK_WEBHOOK
  2. ファイル ~/.claude/secrets/slack_houjin_webhook.txt
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schedule  # noqa: E402

WEBHOOK_FILE = os.path.expanduser("~/.claude/secrets/slack_houjin_webhook.txt")
SITE_URL = "https://iccha-kyoto.github.io/houjinzei-drill/"


def load_webhook():
    url = os.environ.get("HOUJIN_SLACK_WEBHOOK", "").strip()
    if url:
        return url
    try:
        with open(WEBHOOK_FILE, encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        sys.exit(f"[error] webhook が見つかりません: env HOUJIN_SLACK_WEBHOOK か {WEBHOOK_FILE} を設定してください")


def build_message(d):
    def j(items):
        return "／".join(items) if items else "—"

    lines = [f"📗 *法人税法ドリル｜{d['set_label']}*　（{d['date']}）　本試験まであと *{d['days_left']}* 日"]

    if d["week"]:
        pairs = [f"{t}（{a}）" for t, a in zip(d["new_titles"], d["new_arts"])]
        lines.append(f"🆕 *今週の新規*：{j(pairs)}")
        if d["review_titles"]:
            lines.append(f"🔁 *復習*：{j(d['review_titles'])}")
    else:
        lines.append("🌱 *助走期間*：理論の解禁前。別表四と改正論点で足場を作る時期。")

    lines.append(f"📋 *別表四の判定*：{j(d['bt4_titles'])}")
    lines.append(f"🧮 *計算*：{j(d['keisan_titles'])}")
    lines.append(f"⚡ *改正・新論点*：{j(d['kaisei_titles'])}")
    lines.append("")
    lines.append("📱 ドリル（スマホ可・4タブ／墨消しタップ／「全範囲を表示」も可）")
    lines.append(SITE_URL)
    lines.append("")
    lines.append("_柱ラベルを見て中身を声に出す → 墨をタップして答え合わせ。理論は毎週月曜に2題ずつ増えます。_")
    return "\n".join(lines)


def post(webhook, text):
    payload = json.dumps({"text": text}).encode("utf-8")
    req = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        body = resp.read().decode("utf-8", "replace")
        if resp.status != 200 or body.strip() != "ok":
            sys.exit(f"[error] Slack 応答異常: HTTP {resp.status} body={body!r}")


def parse_date_arg():
    """--date YYYY-MM-DD / --date=YYYY-MM-DD を拾う。無ければ None（＝今日）。"""
    import datetime
    for i, a in enumerate(sys.argv):
        raw = None
        if a == "--date" and i + 1 < len(sys.argv):
            raw = sys.argv[i + 1]
        elif a.startswith("--date="):
            raw = a.split("=", 1)[1]
        if raw:
            try:
                return datetime.date.fromisoformat(raw)
            except ValueError:
                sys.exit(f"[error] --date の形式が不正です: {raw}（YYYY-MM-DD）")
    return None


def main():
    d = schedule.main(parse_date_arg())
    text = build_message(d)
    if "--dry-run" in sys.argv:
        print(text)
        return
    post(load_webhook(), text)
    print(f"[ok] posted to Slack ({d['date']} / {d['set_label']} / あと{d['days_left']}日)")


if __name__ == "__main__":
    main()
