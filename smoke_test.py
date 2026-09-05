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
os.environ.setdefault("AIMDESK_TODAY", "2026-09-03")          # 목요일(발로 데이)로 고정 — 주말에 돌려도 같은 화면
STATS = TMP / "FPSAimTrainer" / "stats"; STATS.mkdir(parents=True, exist_ok=True)
for f in STATS.iterdir(): f.unlink()
for f in TMP.glob("*.json"): f.unlink()
for f in TMP.glob("*.log"): f.unlink()
(TMP / "aim_desk_data.json").write_text(json.dumps({
    "stats_dir": str(STATS), "auto_delay": 1, "seeded": False, "pb": {}, "days": {}, "next_key": "f10",
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

TODAY = ad.today_date(); today = TODAY.strftime("%Y.%m.%d")
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
                txt = w.itemcget(w.lbl, "text")
                if txt == label or txt[2:] == label: return w          # 토글은 '● ' / '○ ' 글리프가 앞에 붙는다
            except tk.TclError: pass
    return None
def texts(top): return [w.cget("text") for w in walk(top) if isinstance(w, tk.Label)]
def scan():
    ad._SCAN_STATE["sig"] = None; D["scan_once"](); pump(150)
def wait_fired(n, ms=6000):
    """fired 가 n개가 될 때까지 (자동 전송 타이머 1초 + 여유)"""
    end = time.time() + ms / 1000
    while time.time() < end and len(fired) < n:
        root.update(); time.sleep(0.03)
    scan()

ad.main()
D = ad._DBG; root = D["root"]; data = D["data"]
pump(700)                                       # tick(300ms)·refresh(450ms) 가 돌도록

# ── 시작 상태 ──
check("window geometry remembered (1000x700, clamped to minsize)", root.winfo_width() == max(1000, ad.px(960)) and abs(root.winfo_x() - 30) <= 2, f"{root.winfo_width()} {root.winfo_x()}")
check("today tab visible", D["frames"]["today"].winfo_ismapped())
check("stale override equal to ini key cleared at startup", data.get("next_key") is None, str(data.get("next_key")))
check("status bar shows 0판 warn", "0판" in D["status_lbl"].cget("text"), D["status_lbl"].cget("text"))
b = btn(root, "▶ 오늘 루틴 실행"); check("routine button exists (v-day)", b is not None)
c0 = D["counters"]["refresh_tab"]
D["refresh"](); check("refresh() on today leaves grow dirty", D["dirty"]["grow"] is True and len(D["cv_idx"].find_all()) == 0)
D["tabbtns"]["grow"].event_generate("<Button-1>"); pump(400)        # 첫 표시 뒤 캔버스 <Configure> 디바운스(80ms)까지 기다린다
check("grow tab drawn on click", len(D["cv_idx"].find_all()) > 0 and D["dirty"]["grow"] is False)
c1 = D["counters"]["refresh_tab"]
D["tabbtns"]["grow"].event_generate("<Button-1>"); pump(400)
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
al_ = D["seq_win"]["auto_lbl"]; check("start instruction (auto_lbl, gold) names local playlist + key", "로컬 재생 목록" in al_.cget("text") and "AIMDESK Day" in al_.cget("text") and "F10" in al_.cget("text") and al_.cget("fg") == ad.C["gold"], al_.cget("text")[:160])
check("key line: read from KovaaK's ini", D["seq_win"]["key_lbl"].cget("text").startswith("코박스 설정에서 읽음") and "F10" in D["seq_win"]["key_lbl"].cget("text"))
check("tab guide drawn before first play", bool(D["seq_win"]["guide"].winfo_manager()) and len(D["seq_win"]["guide"].find_all()) >= 9)
check("install label points at the 4th tab", D["pl_lbl"].cget("text").startswith("플레이리스트 4개 설치 ✓ → 코박스 샌드박스 브라우저 네 번째 탭"), D["pl_lbl"].cget("text")[:80])
kent = next(w for w in walk(top) if isinstance(w, tk.Entry))
kent.insert(0, "f5"); D["seq_win"]["commit_key"](); pump(80)
check("typed 'f5' normalised to F5 and saved", kent.get() == "F5" and data.get("next_key") == "F5", f"{kent.get()} {data.get('next_key')}")
kl = D["seq_win"]["key_lbl"].cget("text"); check("mismatch warning F5 vs ini F10", kl.startswith("⚠") and "F10" in kl and "F5" in kl, kl)
kent.delete(0, "end"); D["seq_win"]["commit_key"](); pump(80)
check("cleared entry → back to ini key", data.get("next_key") is None and D["seq_win"]["key_lbl"].cget("text").startswith("코박스 설정에서 읽음"))
csv("VT Ground Novice S5", "10.00.00", 3000); scan(); wait_fired(1)
check("after CSV#1: NEXT pressed once", fired == ["KEY:F10"], str(fired))
check("start instruction gone after first play", "코박스에서 시작하세요" not in D["seq_win"]["auto_lbl"].cget("text"))
check("tab guide hidden after first play", not D["seq_win"]["guide"].winfo_manager())
check("status bar counts 1판 ok", "1판" in D["status_lbl"].cget("text") and D["status_dot"].itemcget(1, "fill") == ad.C["ok"], D["status_lbl"].cget("text"))
tx = texts(top); check("row shows 3000 ▼181", "3000" in tx and "▼181" in tx)
csv("VT Ground Novice S5", "10.01.00", 3300); scan(); wait_fired(2)
check("after CSV#2: NEXT pressed again", fired == ["KEY:F10"] * 2, str(fired))
check("PB! shown", "PB!" in texts(top))
check("PB toast rendered with bench context", D["toast"].winfo_ismapped() and any("Reactive" in t or "Gold" in t for t in texts(D["toast"])), str(texts(D["toast"]))[:160])
check("plays persisted in day", len(data["days"][TODAY.isoformat()]["plays"]) == 2 and data["days"][TODAY.isoformat()]["sess"]["start"] == "10.00.00")
D["show_toast"]("a"); D["show_toast"]("b"); D["show_toast"]("c"); pump(50)
check("toast queue caps at 3", len(D["toast"].winfo_children()) == 3)
D["toast"].winfo_children()[0].event_generate("<Button-1>"); pump(50)
check("click dismisses a toast", len(D["toast"].winfo_children()) == 2)
_mono = ad.time.monotonic; ad.time.monotonic = lambda: _mono() + 11; D["toast_tick"](); ad.time.monotonic = _mono; pump(50)
check("toasts expire", not D["toast"].winfo_ismapped())
btn(top, "건너뛰기 ▶").cmd(); pump(50)
check("skip → NEXT pressed immediately", len(fired) == 3)
check("skipped row labelled 건너뜀", any(r[5].cget("text") == "건너뜀" for r in D["seq_win"]["rows"]))
pump(6500)
check("stall → 프리 플레이 warning", any("⚠" in t and "도전 과제" in t for t in texts(top)))
csv("VT Floating Heads Novice S5", "10.03.00", 600); scan(); wait_fired(4)
check("CSV → NEXT (4), warning cleared", len(fired) == 4 and not any("⚠" in t for t in texts(top)))
# 게임 창이 앞에 없을 때: 건너뛰기 → 전송 실패 → 안내, 창을 되찾으면(focus 성공) 다시 시도해서 보냄. 그 사이 토글을 껐다 켜도 재시도가 살아 있어야 한다
ad.kovaaks_foreground = lambda: False; ad.focus_kovaaks = lambda: False
btn(top, "건너뛰기 ▶").cmd(); pump(100)
check("foreground lost: key not sent, hint asks to click game, pending set", len(fired) == 4 and any("앞에 있어야" in t for t in texts(top)) and D["auto"]["pending"] is not None, f"{len(fired)} {D['auto']['pending']}")
btn(top, "자동 진행").cmd(); btn(top, "자동 진행").cmd(); pump(50)
check("auto toggle keeps the pending retry", D["auto"]["on"] and D["auto"]["fired"] is None and D["auto"]["pending"] is not None)
ad.focus_kovaaks = lambda: True
scan(); wait_fired(5); pump(200)
check("retry after focus regained → key sent, pending cleared", len(fired) == 5 and fired[-1] == "KEY:F10" and D["auto"]["pending"] is None, str(fired[-2:]))
ad.kovaaks_foreground = lambda: True
btn(top, "자동 진행").cmd(); csv("VT 1w4ts Novice S5", "10.05.00", 900); scan(); pump(1300); scan()
check("auto OFF: no key", len(fired) == 5)
check("skipped 1w4ts row revived by its own CSV (Frogtagon stays skipped)", D["seq_win"]["skipped"] == {2}, str(D["seq_win"]["skipped"]))
D["seq_win"]["rows"][2][3].event_generate("<Button-1>"); pump(50)
check("click on '–' un-skips the row", D["seq_win"]["skipped"] == set() and "건너뜀" not in D["seq_win"]["prog"].cget("text"), D["seq_win"]["prog"].cget("text"))
D["seq_win"]["skipped"].add(2); D["update_sequence"]()          # 아래 검사들은 Frogtagon 이 건너뛴 상태를 전제로 한다
btn(top, "자동 진행").cmd(); check("auto ON (key) presses nothing", len(fired) == 5)
btn(top, "딥링크 방식").cmd(); csv("VT Pasu Novice S5", "10.06.00", 700); scan(); wait_fired(6)
check("link mode → deeplink for EddieTS", len(fired) == 6 and fired[-1] == ad.scenario_uri("VT EddieTS Novice S5"), str(fired[-1:]))
top.geometry("+1180+60"); pump(100)          # 스크린샷에서 본창을 가리지 않게 오른쪽으로

# ── v3: 정보·코치·기록 탭·단축키 ──
SHOTS = os.environ.get("AIMDESK_SHOTS")
def shot(name):
    if not SHOTS: return
    import subprocess; Path(SHOTS).mkdir(parents=True, exist_ok=True)
    pump(120); subprocess.run(["import", "-window", "root", f"{SHOTS}/{name}.png"], timeout=20)
D["show"]("today"); root.geometry("1100x780"); pump(300)
check("streak label", "연속" in D["hdr_streak"].cget("text"), D["hdr_streak"].cget("text"))
check("week strip drawn (7 cells)", len([i for i in D["wk_cv"].find_all() if D["wk_cv"].type(i) == "polygon"]) == 7)
sec0 = D["section_labels"][0][0].cget("text"); check("warmup section shows progress 3/4", sec0.endswith("3/4"), sec0)
hi = [r for r in D["routine_rows"] if r[9].cget("bg") == ad.C["card2"]]
check("exactly one routine row highlighted as next", len(hi) == 1, str(len(hi)))
sess = D["day_state"]["sess_lbl"].cget("text"); check("session line shows 5판 and PB", sess.startswith("오늘 5판") and "PB 1" in sess, sess)
coach = [l.cget("text") for l in D["day_state"]["coach"]]; check("coach card has lines", any(coach) and ("지수" in coach[0] or "프로브" in coach[0]), str(coach)[:160])
plus = btn(D["steppers"][0], "＋"); plus.cmd(); pump(50)
check("deaths trend after +1", "1회" in D["dth_lbl"].cget("text"), D["dth_lbl"].cget("text"))
shot("1_today")
D["show"]("bench"); pump(200)
check("bench advice names the weakest link", D["advice_lbl"].cget("text").startswith("약한 고리"), D["advice_lbl"].cget("text")[:120])
wk = [k for k, (_, _, cardf) in D["ben_rows"].items() if cardf.cget("highlightbackground") == ad.C["gold"]]
check("weakest card highlighted (one)", len(wk) == 1, str(wk))
gaps = [c[3].cget("text") for c in D["ben_rows"]["react"][1]]; check("gap label for today's Ground", any(g.startswith("Gold +") for g in gaps), str(gaps))
shot("2_bench")
D["show"]("grow"); pump(200); shot("3_grow")
D["show"]("log"); pump(200)
c00 = D["hist_cells"][0][0].cget("text"); check("log first row is today", c00.startswith(TODAY.strftime("%m-%d")), c00)
D["select_day"](0); pump(50)
check("detail shows today's Pasu", D["det_lines"][0].cget("text").startswith("Pasu") and "700" in D["det_lines"][0].cget("text"), D["det_lines"][0].cget("text"))
check("growth card title", "총 에너지" in D["grow_title"].cget("text"), D["grow_title"].cget("text"))
shot("4_log")
class KE: pass
ke = KE(); ke.widget = root; ke.keysym = "2"; ke.state = 0
D["on_key"](ke); pump(50); check("shortcut 2 → grow tab", D["cur_tab"][0] == "grow")
ent = next(w for w in walk(root) if isinstance(w, tk.Entry))
ke2 = KE(); ke2.widget = ent; ke2.keysym = "1"; ke2.state = 0
D["on_key"](ke2); pump(50); check("'1' typed in entry does not switch tab", D["cur_tab"][0] == "grow")
D["show_toast"]("x"); pump(30); ke3 = KE(); ke3.widget = root; ke3.keysym = "Escape"; ke3.state = 0
D["on_key"](ke3); pump(50); check("Escape dismisses toasts", not D["toast"].winfo_ismapped())
D["show"]("today"); pump(100); shot("5_seq")
# ── 순서창 간단히 · 현재 줄 강조 · 상세 팝업 · 배율 ──
rows_ = D["seq_win"]["rows"]; nxt_ = ad_status = None
done_, nxt_, _ = None, None, None
mapped_before = sum(1 for r in rows_ if r[1].master.winfo_ismapped())
D["set_compact"](True); pump(150)
mapped_after = sum(1 for r in rows_ if r[1].master.winfo_ismapped())
check("compact mode hides rows", mapped_before == 27 and 4 <= mapped_after <= 8, f"{mapped_before}->{mapped_after}")
cur = D["seq_win"]["cur_row"]; check("current row emphasized (bold, card2)", cur is not None and rows_[cur][2].cget("font") != rows_[0][2].cget("font") and rows_[cur][2].cget("bg") == ad.C["card2"])
check("skip/resend buttons enabled while rows remain", D["seq_win"]["skip_btn"].enabled)
shot("6_seq_compact")
D["set_compact"](False); pump(100)
D["routine_rows"][0][8].event_generate("<Button-1>"); pump(150)
dw = D["detail"]; check("detail popup opened for ground", dw["win"] is not None and dw["win"].winfo_exists() and dw["key"] == "ground")
check("detail summary has PB and today count", "PB 3300" in dw["sum"].cget("text") and "오늘 2판" in dw["sum"].cget("text"), dw["sum"].cget("text"))
dw["win"].geometry("+1180+560"); pump(120); shot("7_detail")
check("UI scale applied to daych", D["daych"].winfo_reqwidth() == ad.px(70), f"{D['daych'].winfo_reqwidth()} vs {ad.px(70)}")
check("window fits screen", root.winfo_width() <= root.winfo_screenwidth())
# ── 토요일(벤치 데이)로 날짜가 넘어감 → AIMDESK Bench 플레이리스트 · 줄 18개 ──
btn(top, "딥링크 방식").cmd(); pump(50)
os.environ["AIMDESK_TODAY"] = "2026-09-05"; scan(); pump(700)
check("day change → bench day with AIMDESK Bench", D["day_state"]["dt"] == "b" and D["day_state"]["pl"] == "AIMDESK Bench", str(D["day_state"]["dt"]))
check("day change resets auto engine", D["auto"]["on"] is False and D["auto"]["pending"] is None and D["auto"]["fired_at"] is None)
bb = btn(root, "▶ 벤치 18개 실행"); check("bench run button exists", bb is not None)
check("bench rows: 18 in Voltaic order", [r[1] for r in D["routine_rows"]] == [k for s_ in ad.SUBS for k, _ in s_[3]], str([r[1] for r in D["routine_rows"]])[:120])
check("bench sections 9", len(D["section_labels"]) == 9 and D["section_labels"][0][1].startswith("① 클리킹"), str([s_[1] for s_ in D["section_labels"]])[:120])
bb.cmd(); pump(250)
tops = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel) and "AIMDESK Bench" in w.title()]
check("bench sequence window 18 rows", len(tops) == 1 and len(D["seq_win"]["rows"]) == 18, f"{len(tops)} {len(D['seq_win']['rows'])}")
check("bench start instruction", bool(tops) and "로컬 재생 목록" in D["seq_win"]["auto_lbl"].cget("text") and "AIMDESK Bench" in D["seq_win"]["auto_lbl"].cget("text") and "Pasu" in D["seq_win"]["auto_lbl"].cget("text"))
check("seq rows follow BENCH order", [r[0] for r in D["seq_win"]["rows"]] == [k for k, _ in ad.BENCH])
pl_json = json.loads((TMP / "FPSAimTrainer" / "Saved" / "SaveGames" / "Playlists" / "AIMDESK Bench.json").read_bytes().decode("utf-16"))
check("installed AIMDESK Bench.json lists the 18 scenarios in order", [x["scenario_Name"] for x in pl_json["scenarioList"]] == [ad.SCEN[k][0] for k, _ in ad.BENCH])
# 시작 전에 건너뛰기를 눌러도(스크린샷 상황) 시작 안내는 남고, 그 판의 기록이 들어오면 줄이 되살아난다
btn(tops[0], "건너뛰기 ▶").cmd(); pump(100)
check("skip before first play keeps the start instruction", "코박스에서 시작하세요" in D["seq_win"]["auto_lbl"].cget("text") and 0 in D["seq_win"]["skipped"])
check("bench playlist file installed", (TMP / "FPSAimTrainer" / "Saved" / "SaveGames" / "Playlists" / "AIMDESK Bench.json").exists())
n0 = len(fired); today = "2026.09.05"; csv("VT Pasu Novice S5", "11.00.00", 700); scan(); wait_fired(n0 + 1)
check("bench: Pasu CSV → exactly one NEXT press, skipped Pasu row revived", fired[n0:] == ["KEY:F10"] and 0 not in D["seq_win"]["skipped"], f"{fired[n0:]} {D['seq_win']['skipped']}")
# 두 번째 세션 감지: 자리 없는 판(오늘 Pasu 를 두 번째로 침, 줄은 하나) → 1번부터 다시 세고 그 판을 1번에 배정 + NEXT
n1 = len(fired); csv("VT Pasu Novice S5", "11.30.00", 720); scan(); wait_fired(n1 + 1)
check("restart detected: new run starts at row 1 with the new Pasu, NEXT pressed", fired[n1:] == ["KEY:F10"] and D["seq_win"]["base"].get("pasu") == 1 and D["seq_win"]["rows"][0][4].cget("text") == "720", f"{fired[n1:]} base={D['seq_win']['base']} row0={D['seq_win']['rows'][0][4].cget('text')}")
prow = next(r for r in D["routine_rows"] if r[1] == "pasu"); check("bench row shows today's best + next rank gap", prow[5].cget("text").startswith("720") and "까지" in prow[5].cget("text"), prow[5].cget("text"))
shot("8_bench_day")
# ── 닫기: 창 정보 저장 ──
D["on_close"]()
saved = json.loads((TMP / "aim_desk_data.json").read_text(encoding="utf-8"))
check("on_close saved win.geo/tab/seq", saved["win"].get("tab") == "today" and "geo" in saved["win"] and saved["win"].get("seq", "").startswith("+"), str(saved["win"]))
check("auto_mode persisted", saved.get("auto_mode") == "key")
log = (TMP / "aim_desk.log").read_text() if (TMP / "aim_desk.log").exists() else ""
check("no exceptions logged", log.strip() == "", log[-600:])
n_ok = sum(1 for _, ok in results if ok)
print(f"SUMMARY: {n_ok} / {len(results)} passed")
sys.exit(0 if n_ok == len(results) else 1)
