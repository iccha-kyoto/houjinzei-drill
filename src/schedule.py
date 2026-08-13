#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""本日の出題範囲を決める。site/index.html の JS 巡回ロジックと完全に一致させること。

設計（相続税の直前演習との違い）
--------------------------------
相続税版は「完成した範囲を毎日1つずつ回す」直前型だった。
法人税は12ヶ月かけて積み上げるので、こちらは積み上げ型にする:

  ・週2題ずつ理論が「解禁」される（START からの経過週で決まる）
  ・今週の新規2題は毎日出る（＝叩き込む）
  ・それ以前の既習分から4題をローテーション（＝間隔反復で忘却を防ぐ）
  ・別表四・計算・改正論点は最初から全部回す（教材が無くても回せる）

START 前（助走期間）は理論を出さず、別表四と改正論点だけを回す。
"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import THEORY, BT4, KEISAN, KAISEI  # noqa: E402

EPOCH = datetime.date(1970, 1, 1)
START = datetime.date(2026, 8, 31)  # 学習開始（月曜）。教材2027年度版は8/29入手、9/1着手予定
EXAM = datetime.date(2027, 8, 4)    # 第77回 2日目（法人税法）の予想日。官報公告後に確定させる

PER_WEEK = 2      # 週に解禁する理論の題数
N_REVIEW = 4      # 既習分から毎日回す題数
N_BT4 = 6         # 別表四カードの1日あたり枚数
N_KEISAN = 2
N_KAISEI = 1


def win(arr, off, n):
    """arr の off 番目から n 個を巡回で取る。"""
    if not arr:
        return []
    return [arr[(off + i) % len(arr)] for i in range(min(n, len(arr)))]


def main(today=None):
    today = today or datetime.date.today()
    ordn = (today - EPOCH).days
    days_to_start = (START - today).days

    # 経過週（START の週を第1週とする）
    week = (today - START).days // 7 + 1
    if week < 1:
        week = 0  # 助走期間

    unlocked = min(week * PER_WEEK, len(THEORY)) if week else 0
    new_items = THEORY[(week - 1) * PER_WEEK:unlocked] if week else []
    older = THEORY[:max(0, (week - 1) * PER_WEEK)]
    review = win(older, ordn % len(older), N_REVIEW) if older else []

    bt4 = win(BT4, ordn % len(BT4), N_BT4)
    keisan = win(KEISAN, ordn % len(KEISAN), N_KEISAN)
    kaisei = win(KAISEI, ordn % len(KAISEI), N_KAISEI)

    if week:
        label = f"第{week}週・理論{unlocked}/{len(THEORY)}題"
    else:
        label = f"助走期間（開講まであと{days_to_start}日）"

    return {
        "date": today.strftime("%Y/%m/%d"),
        "days_left": (EXAM - today).days,
        "week": week,
        "unlocked": unlocked,
        "total_theory": len(THEORY),
        "set_label": label,
        "new_titles": [t[0] for t in new_items],
        "new_arts": [t[1] for t in new_items],
        "review_titles": [t[0] for t in review],
        "bt4_titles": [b[0] for b in bt4],
        "keisan_titles": [k[0] for k in keisan],
        "kaisei_titles": [k[0] for k in kaisei],
    }


if __name__ == "__main__":
    d = datetime.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else None
    print(json.dumps(main(d), ensure_ascii=False))
