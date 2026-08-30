#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""content.py から site/index.html を生成する。

  python3 build.py

生成物は単一HTML（外部依存なし）。そのまま GitHub Pages に置ける。
本日の範囲を決めるロジックは schedule.py と一対一で対応させてある。
どちらかを変えたらもう一方も変えること。
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content import THEORY, BT4, KEISAN, KAISEI  # noqa: E402
import schedule  # noqa: E402

BASE = os.path.dirname(os.path.abspath(__file__))
MARK = re.compile(r"【(.+?)】")


def seg(text):
    """【】マークアップを {t:地の文} / {b:墨消し} の配列に変換する。"""
    out, pos = [], 0
    for m in MARK.finditer(text):
        if m.start() > pos:
            out.append({"t": text[pos:m.start()]})
        out.append({"b": m.group(1)})
        pos = m.end()
    if pos < len(text):
        out.append({"t": text[pos:]})
    return out


def pack_pillars(items):
    return [{"l": lab, "seg": seg(txt)} for lab, txt in items]


DATA = {
    "theory": [{"title": t, "art": a, "pillars": pack_pillars(p)} for t, a, p in THEORY],
    "bt4": [{"title": t, "seg": seg(s)} for t, s in BT4],
    "keisan": [{"title": t, "seg": seg(s)} for t, s in KEISAN],
    "kaisei": [{"title": t, "art": a, "pillars": pack_pillars(p)} for t, a, p in KAISEI],
}

STYLE = """
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Hiragino Sans","Noto Sans JP",sans-serif;
 background:#f6f7f9;color:#1b1f24;line-height:1.75;-webkit-text-size-adjust:100%}
header{background:#12324f;color:#fff;padding:14px 16px 12px;position:sticky;top:0;z-index:20}
header h1{margin:0;font-size:16px;font-weight:700;letter-spacing:.02em}
header .meta{margin-top:4px;font-size:12px;opacity:.85}
.tabs{display:flex;gap:4px;margin-top:10px;overflow-x:auto;-webkit-overflow-scrolling:touch}
.tabs button{flex:0 0 auto;border:0;border-radius:999px;padding:7px 14px;font-size:13px;font-weight:600;
 background:rgba(255,255,255,.14);color:#fff;cursor:pointer}
.tabs button[aria-selected="true"]{background:#fff;color:#12324f}
.bar{display:flex;gap:8px;align-items:center;padding:10px 16px;background:#fff;border-bottom:1px solid #e3e7ec;
 position:sticky;top:104px;z-index:15;font-size:12px;flex-wrap:wrap}
.bar button{border:1px solid #c9d2dc;background:#fff;border-radius:8px;padding:5px 10px;font-size:12px;cursor:pointer}
main{padding:14px 12px 60px;max-width:760px;margin:0 auto}
.card{background:#fff;border:1px solid #e3e7ec;border-radius:12px;padding:14px 15px;margin-bottom:12px}
.card.new{border-color:#c8892a;border-width:2px}
.tag{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;margin-right:6px;vertical-align:2px}
.tag.n{background:#fdf1dd;color:#96631a}
.tag.r{background:#e8f0f8;color:#2b5b86}
.card h2{margin:0 0 2px;font-size:15px;font-weight:700}
.card .art{font-size:11.5px;color:#6b7684;margin-bottom:9px}
.p{margin:9px 0;padding-left:10px;border-left:3px solid #dde3ea}
.p .l{font-size:11.5px;font-weight:700;color:#2b5b86;display:block;margin-bottom:1px}
.p .x{font-size:14.5px}
.b{background:#1b1f24;color:transparent;border-radius:3px;padding:0 3px;cursor:pointer;
 transition:background .12s;user-select:none}
.b.on{background:#fff3c9;color:#1b1f24}
.sec{font-size:12px;font-weight:700;color:#6b7684;margin:18px 2px 8px}
.sec:first-child{margin-top:0}
.note{font-size:12px;color:#6b7684;padding:10px 14px;background:#eef1f4;border-radius:10px;margin-bottom:14px}
.empty{font-size:13px;color:#6b7684;padding:18px;text-align:center}
"""

HTML = """<!doctype html>
<html lang="ja"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>法人税法ドリル</title>
<style>__STYLE__</style>
</head><body>
<header>
  <h1>法人税法ドリル</h1>
  <div class="meta" id="meta"></div>
  <nav class="tabs" role="tablist">
    <button role="tab" data-t="theory" aria-selected="true">理論</button>
    <button role="tab" data-t="bt4" aria-selected="false">別表四</button>
    <button role="tab" data-t="keisan" aria-selected="false">計算</button>
    <button role="tab" data-t="kaisei" aria-selected="false">改正・新論点</button>
  </nav>
</header>
<div class="bar">
  <button id="revealAll">全部めくる</button>
  <button id="hideAll">全部隠す</button>
  <button id="scope">全範囲を表示</button>
  <span id="scopeLabel" style="color:#6b7684"></span>
</div>
<main id="app"></main>
<script>
var DATA=__DATA__;
var START=Date.UTC(2026,7,31)/86400000, EXAM=Date.UTC(2027,7,4)/86400000;
var PER_WEEK=2, N_REVIEW=4, N_BT4=6, N_KEISAN=2, N_KAISEI=1;
var showAll=false, tab='theory';

function ordToday(){var d=new Date();return Math.floor(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())/86400000);}
var ORD=ordToday();
var WEEK=Math.floor((ORD-START)/7)+1; if(WEEK<1)WEEK=0;
var UNLOCKED=WEEK?Math.min(WEEK*PER_WEEK,DATA.theory.length):0;

function win(a,off,n){if(!a.length)return[];var r=[],L=a.length;
  for(var i=0;i<Math.min(n,L);i++)r.push(a[((off+i)%L+L)%L]);return r;}
function mod(n,L){return L?((n%L)+L)%L:0;}

function esc(s){return s.replace(/[&<>]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;'}[c];});}
function segHTML(sg){return sg.map(function(s){
  return s.b!==undefined?'<span class="b">'+esc(s.b)+'</span>':esc(s.t);}).join('');}
function pillarsHTML(ps){return ps.map(function(p){
  return '<div class="p"><span class="l">'+esc(p.l)+'</span><span class="x">'+segHTML(p.seg)+'</span></div>';}).join('');}
function card(o,cls,tag){
  return '<div class="card'+(cls?' '+cls:'')+'">'+(tag||'')+'<h2>'+esc(o.title)+'</h2>'
    +(o.art?'<div class="art">'+esc(o.art)+'</div>':'')
    +(o.pillars?pillarsHTML(o.pillars):'<div class="p"><span class="x">'+segHTML(o.seg)+'</span></div>')+'</div>';}

function render(){
  var h='', d=DATA;
  if(tab==='theory'){
    if(showAll){ h=d.theory.map(function(o){return card(o);}).join(''); }
    else if(!WEEK){
      h='<div class="note">開講前の助走期間です。理論は '+new Date(START*86400000).toLocaleDateString('ja-JP')
        +' から週'+PER_WEEK+'題ずつ解禁されます。それまでは「別表四」「改正・新論点」タブが使えます。</div>';
    } else {
      var nw=d.theory.slice((WEEK-1)*PER_WEEK,UNLOCKED);
      var older=d.theory.slice(0,Math.max(0,(WEEK-1)*PER_WEEK));
      var rv=win(older,mod(ORD*N_REVIEW,older.length),N_REVIEW);
      h=nw.length?('<div class="sec">今週の新規（毎日やる）</div>'
        +nw.map(function(o){return card(o,'new','<span class="tag n">NEW</span>');}).join(''))
        :'<div class="note">収録済みの理論をすべて解禁しました。content.py に題を追加すると、この先の週に自動で割り当てられます。</div>';
      if(rv.length) h+='<div class="sec">復習（既習分から巡回）</div>'
        +rv.map(function(o){return card(o,'','<span class="tag r">復習</span>');}).join('');
    }
  } else {
    var arr=d[tab], n={bt4:N_BT4,keisan:N_KEISAN,kaisei:N_KAISEI}[tab];
    var pick=showAll?arr:win(arr,mod(ORD*n,arr.length),n);
    h=pick.map(function(o){return card(o);}).join('');
  }
  document.getElementById('app').innerHTML=h||'<div class="empty">項目がありません</div>';
}

document.getElementById('meta').textContent=
  (WEEK?('第'+WEEK+'週／理論 '+UNLOCKED+'／'+DATA.theory.length+'題 解禁'):'助走期間')
  +'　本試験まであと '+(EXAM-ORD)+' 日';

document.querySelectorAll('.tabs button').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.tabs button').forEach(function(x){x.setAttribute('aria-selected','false');});
    b.setAttribute('aria-selected','true'); tab=b.dataset.t; render();});
});
document.getElementById('app').addEventListener('click',function(e){
  if(e.target.classList.contains('b')) e.target.classList.toggle('on');});
document.getElementById('revealAll').addEventListener('click',function(){
  document.querySelectorAll('.b').forEach(function(x){x.classList.add('on');});});
document.getElementById('hideAll').addEventListener('click',function(){
  document.querySelectorAll('.b').forEach(function(x){x.classList.remove('on');});});
document.getElementById('scope').addEventListener('click',function(){
  showAll=!showAll; this.textContent=showAll?'本日の範囲に戻す':'全範囲を表示';
  document.getElementById('scopeLabel').textContent=showAll?'全範囲':''; render();});
render();
</script>
</body></html>
"""


def main():
    out_dir = os.path.join(BASE, "site")
    os.makedirs(out_dir, exist_ok=True)
    page = HTML.replace("__STYLE__", STYLE).replace(
        "__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")))
    path = os.path.join(out_dir, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
    d = schedule.main()
    n_black = page.count('"b":')
    print(f"[ok] {path}")
    print(f"     理論{len(THEORY)}題 / 別表四{len(BT4)}枚 / 計算{len(KEISAN)}件 / 改正{len(KAISEI)}件"
          f" / 墨消し{n_black}箇所")
    print(f"     本日: {d['set_label']}　本試験まで{d['days_left']}日")


if __name__ == "__main__":
    main()
