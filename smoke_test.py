#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""헤드리스 GUI 스모크 테스트 — Xvfb 에서 앱을 띄워 버튼을 누르고 가짜 CSV 를 넣어 본다.
   실행: AIMDESK_DATA_DIR=/tmp/x AIMDESK_NO_MAINLOOP=1 xvfb-run -a python3 smoke_test.py
   (exe 에는 포함되지 않음)"""
import os, sys, json, time, tempfile, importlib.util
from pathlib import Path
from datetime import date

TMP = Path(os.environ.get("AIMDESK_DATA_DIR") or tempfile.mkdtemp(prefix="aimdesk_smoke_"))
os.environ["AIMDESK_DATA_DIR"] = str(TMP); os.environ["AIMDESK_NO_MAINLOOP"] = "1"
STATS = TMP / "FPSAimTrainer" / "stats"; STATS.mkdir(parents=True, exist_ok=True)
for f in STATS.iterdir(): f.unlink()
for f in TMP.glob("*.json"): f.unlink()
for f in TMP.glob("*.log"): f.unlink()
(TMP / "aim_desk_data.json").write_text(json.dumps({
    "stats_dir": str(STATS), "auto_delay": 1, "seeded": False, "pb": {}, "days": {},
    "win": {"geo": "1000x700+30+40"}}), encoding="utf-8")

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ad", HERE / "aim_desk.py")
ad = importlib.util.module_from_spec(spec); spec.loader.exec_module(ad)
fired = []
ad.open_uri = lambda uri: (fired.append(uri), True)[1]
ad.kovaaks_running = lambda: True
ad.kovaaks_foreground = lambda: True
ad.playlist_next_key = lambda: "F10"
ad.send_key = lambda name: (fired.append("KEY:" + name), True)[1]
ad.STALL_SEC = 3
import tkinter as tk
from tkinter import messagebox
messagebox.showwarning = lambda *a, **k: None
messagebox.askyesno = lambda *a, **k: True

today = date.today().strftime("%Y.%m.%d")
results = []
def check(name, cond, extra=""):
    results.append((name, bool(cond))); print(("PASS " if cond else "FAIL ") + name, extra)
def csv(name, hhmmss, score):
    (STATS / f"{name} - Challenge - {today}-{hhmmss} Stats.csv").write_text(f"Kills:,5\nScore:,{score}\n")
def pump(ms=300):
    end = time.time() + ms / 1000
    while time.time() < end:
        root.update(); time.sleep(0.02)
def walk(w):
    yield w
    for c in w.winfo_children(): yield from walk(c)
def btn(top, label):
    for w in walk(top):
        if isinstance(w, tk.Canvas) and hasattr(w, "lbl") and hasattr(w, "cmd"):
            try:
                if w.itemcget(w.lbl, "text") == label: return w
            except tk.TclError: pass
    return None
def texts(top): return [w.cget("text") for w in walk(top) if isinstance(w, tk.Label)]
def scan():
    ad._SCAN_STATE["sig"] = None; D["scan_once"](); pump(150)

ad.main()
D = ad._DBG; root = D["root"]; data = D["data"]
pump(700)                                       # tick(300ms)·refresh(450ms) 가 돌도록

# ── 시작 상태 ──
check("window geometry remembered (1000x700)", root.winfo_width() == 1000 and abs(root.winfo_x() - 30) <= 2, f"{root.winfo_width()} {root.winfo_x()}")
check("today tab visible", D["frames"]["today"].winfo_ismapped())
check("status bar shows 0판 warn", "0판" in D["status_lbl"].cget("text"), D["status_lbl"].cget("text"))
b = btn(root, "▶ 오늘 루틴 실행"); check("routine button exists (v-day)", b is not None)
c0 = D["counters"]["refresh_tab"]
D["refresh"](); check("refresh() on today leaves grow dirty", D["dirty"]["grow"] is True and len(D["cv_idx"].find_all()) == 0)
D["tabbtns"]["grow"].event_generate("<Button-1>"); pump(100)
check("grow tab drawn on click", len(D["cv_idx"].find_all()) > 0 and D["dirty"]["grow"] is False)
c1 = D["counters"]["refresh_tab"]
D["tabbtns"]["grow"].event_generate("<Button-1>"); pump(100)
check("second click does not redraw", D["counters"]["refresh_tab"] == c1)
# 리사이즈 폭풍
for i in range(20):
    root.geometry(f"{960+i}x700"); root.update()
pump(300)
check("resize storm coalesced (<=3 redraws)", D["counters"]["refresh_tab"] - c1 <= 3, str(D["counters"]["refresh_tab"] - c1))
D["show"]("today"); pump(100)
# 스크롤
root.geometry("960x660"); pump(300)
ls = D["left_scroll"]
check("routine card overflows at minsize → thumb shown", ls.shown and ls.thumb.winfo_ismapped(), f"{ls.body.winfo_reqheight()} vs {ls.cv.winfo_height()}")
class Ev: pass
ev = Ev(); ev.widget = ls.cv; ev.delta = -120; ev.num = 0
ev.x_root = ls.cv.winfo_rootx() + 10; ev.y_root = ls.cv.winfo_rooty() + 10
D["on_wheel"](ev); pump(50)
check("wheel scrolls the routine card", ls.cv.yview()[0] > 0, str(ls.cv.yview()))
root.geometry("1000x760"); pump(200)

# ── 루틴 실행 + 자동 진행 (key 방식) ──
b.cmd(); pump(150)
check("key mode: no deeplink at start", fired == [], str(fired))
top = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)][0]
check("status shows NEXT key", any("NEXT 키 F10" in t for t in texts(top)))
csv("VT Ground Novice S5", "10.00.00", 3000); scan(); pump(1300); scan()
check("after CSV#1: NEXT pressed once", fired == ["KEY:F10"], str(fired))
check("status bar counts 1판 ok", "1판" in D["status_lbl"].cget("text") and D["status_dot"].itemcget(1, "fill") == ad.C["ok"], D["status_lbl"].cget("text"))
tx = texts(top); check("row shows 3000 ▼181", "3000" in tx and "▼181" in tx)
csv("VT Ground Novice S5", "10.01.00", 3300); scan(); pump(1300); scan()
check("after CSV#2: NEXT pressed again", fired == ["KEY:F10"] * 2, str(fired))
check("PB! shown", "PB!" in texts(top))
check("PB toast rendered with bench context", D["toast"].winfo_ismapped() and any("Reactive" in t or "Gold" in t for t in texts(D["toast"])), str(texts(D["toast"]))[:160])
check("plays persisted in day", len(data["days"][date.today().isoformat()]["plays"]) == 2 and data["days"][date.today().isoformat()]["sess"]["start"] == "10.00.00")
D["show_toast"]("a"); D["show_toast"]("b"); D["show_toast"]("c"); pump(50)
check("toast queue caps at 3", len(D["toast"].winfo_children()) == 3)
D["toast"].winfo_children()[0].event_generate("<Button-1>"); pump(50)
check("click dismisses a toast", len(D["toast"].winfo_children()) == 2)
_mono = ad.time.monotonic; ad.time.monotonic = lambda: _mono() + 11; D["toast_tick"](); ad.time.monotonic = _mono; pump(50)
check("toasts expire", not D["toast"].winfo_ismapped())
btn(top, "다음 판 ▶").cmd(); pump(50)
check("skip → NEXT pressed immediately", len(fired) == 3)
pump(6500)
check("stall → 프리 플레이 warning", any("⚠" in t and "도전 과제" in t for t in texts(top)))
csv("VT Floating Heads Novice S5", "10.03.00", 600); scan(); pump(1300); scan()
check("CSV → NEXT (4), warning cleared", len(fired) == 4 and not any("⚠" in t for t in texts(top)))
btn(top, "자동 진행").cmd(); csv("VT 1w4ts Novice S5", "10.05.00", 900); scan(); pump(1300); scan()
check("auto OFF: no key", len(fired) == 4)
btn(top, "자동 진행").cmd(); check("auto ON (key) presses nothing", len(fired) == 4)
btn(top, "딥링크 방식").cmd(); csv("VT Pasu Novice S5", "10.06.00", 700); scan(); pump(1300); scan()
check("link mode → deeplink for EddieTS", len(fired) == 5 and fired[-1] == ad.scenario_uri("VT EddieTS Novice S5"), str(fired[-1:]))
top.geometry("+120+90"); pump(100)
# ── 닫기: 창 정보 저장 ──
D["on_close"]()
saved = json.loads((TMP / "aim_desk_data.json").read_text(encoding="utf-8"))
check("on_close saved win.geo/tab/seq", saved["win"].get("tab") == "today" and "geo" in saved["win"] and saved["win"].get("seq", "").startswith("+"), str(saved["win"]))
check("auto_mode persisted", saved.get("auto_mode") == "link")
log = (TMP / "aim_desk.log").read_text() if (TMP / "aim_desk.log").exists() else ""
check("no exceptions logged", log.strip() == "", log[-600:])
n_ok = sum(1 for _, ok in results if ok)
print(f"SUMMARY: {n_ok} / {len(results)} passed")
sys.exit(0 if n_ok == len(results) else 1)
