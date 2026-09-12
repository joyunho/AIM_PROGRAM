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
for f in (TMP / "기록").glob("*.txt") if (TMP / "기록").is_dir() else (): f.unlink()
(TMP / "aim_desk_data.json").write_text(json.dumps({
    "stats_dir": str(STATS), "auto_delay": 1, "seeded": False, "pb": {}, "days": {}, "next_key": "f10",
    "win": {"geo": "1000x700+30+40"}, "seq_popup": True}), encoding="utf-8")     # 테스트는 순서창을 띄운 채로 (기본은 숨김)

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
check("verdict band and live strip visible at minsize", D["band_cv"].winfo_ismapped() and D["live"].winfo_ismapped() and len([i for i in D["band_cv"].find_all() if D["band_cv"].type(i) == "text"]) >= 8, str(len(D["band_cv"].find_all())))
D["set_routine_open"](True); pump(300)
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
check("install label points at the 4th tab", D["pl_lbl"].cget("text").startswith("플레이리스트 3개 설치 ✓ → 코박스 샌드박스 브라우저 네 번째 탭"), D["pl_lbl"].cget("text")[:80])
def shot0(name):
    if os.environ.get("AIMDESK_SHOTS"):
        import subprocess; Path(os.environ["AIMDESK_SHOTS"]).mkdir(parents=True, exist_ok=True)
        pump(120); subprocess.run(["import", "-window", "root", f"{os.environ['AIMDESK_SHOTS']}/{name}.png"], timeout=20)
top.geometry("+1180+60"); shot0("0_seq_fresh")
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
tx = texts(top); check("row shows the score, no misleading ▲▼ delta", "3000" in tx and not any(x.startswith(("▲", "▼")) for x in tx), str([x for x in tx if x.startswith(("▲", "▼"))]))
csv("VT Raw Control Novice S5", "10.01.00", 3300); scan(); wait_fired(2)      # v4 웜업: ground → raw → frog → float
check("after CSV#2: NEXT pressed again", fired == ["KEY:F10"] * 2, str(fired))
check("new personal best labelled 최고", "최고" in texts(top))
check("PB toast rendered with bench context", D["toast"].winfo_ismapped() and any("Control" in t or "Gold" in t or "Silver" in t for t in texts(D["toast"])), str(texts(D["toast"]))[:160])
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
check("link mode → deeplink for Popcorn (next probe)", len(fired) == 6 and fired[-1] == ad.scenario_uri("VT Popcorn Novice S5"), str(fired[-1:]))
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
sess = D["day_state"]["sess_lbl"].cget("text"); check("session line shows the session time", "분 (" in sess and "–" in sess, sess)
rib = D["day_state"]["rib_lbl"].cget("text"); check("ribbon line counts today's plays", rib.startswith("오늘 5/") and ("최고" in rib or "평소" in rib), rib)
check("ribbon cells match the plan", len(D["day_state"]["rib_cells"]) == D["today_plan_n"]() == 27, str(len(D["day_state"]["rib_cells"])))
check("training level shown in header", D["hdr_lv"].cget("text").startswith("Lv."), D["hdr_lv"].cget("text"))
_tt = texts(root)
check("week theme line lists five weekday themes", any(x.startswith("이번 주 · 월 ") and x.count("·") == 5 for x in _tt), str([x for x in _tt if x.startswith("이번 주")])[:120])
_V = D["verdicts"](); check("hero verdict is honest with 5 plays (측정 중, hollow)", _V["day"]["state"] == "wait" and _V["day"]["word"] == "측정 중" and D["band_cv"].itemcget("hero", "fill") == ad.C["card2"], str(_V["day"]))
check("live strip shows the last score and its scenario", D["cur_score"].cget("text") == "700" and "Pasu" in D["cur_word"].cget("text"), D["cur_score"].cget("text") + " " + D["cur_word"].cget("text"))
check("live strip mirrors the auto-progress hint", "코박스" in D["auto_mini"].cget("text") or "다음" in D["auto_mini"].cget("text") or D["auto_mini"].cget("text") == "", D["auto_mini"].cget("text")[:80])
_cl = D["day_state"].get("chal_lbl")
check("daily challenge is either a real rank target or absent", _cl is None or ("넘으면" in _cl.cget("text") and "칸" in _cl.cget("text")), _cl.cget("text") if _cl else "none")
D["open_card"](); pump(250)
cw = D["card_win"]["win"]
check("session card opens with real content", cw is not None and cw.winfo_exists() and len(D["card_win"]["cv"].find_all()) > 5, str(len(D["card_win"]["cv"].find_all())))
_ct = [D["card_win"]["cv"].itemcget(i, "text") for i in D["card_win"]["cv"].find_all() if D["card_win"]["cv"].type(i) == "text"]
check("card names the day, theme and play count", any("발로 데이" in x for x in _ct) and any(x.startswith("5판") for x in _ct), str(_ct[:4]))
cw.destroy(); pump(80)
# ── 방송 화면: 창을 키우면 글씨도 커져야 한다 (시청자 쪽에서 읽히도록) ──
import tkinter.font as _tkfont
def big_px(cv):
    b = 0
    for i in cv.find_all():
        if cv.type(i) != "text": continue
        try: b = max(b, abs(_tkfont.Font(font=cv.itemcget(i, "font")).cget("size")))
        except Exception: pass
    return b
D["open_broadcast"](); pump(300)
bw = D["bcast"]["win"]; bcv = D["bcast"]["cv"]
check("broadcast view opens with content", bw is not None and bw.winfo_exists() and len(bcv.find_all()) > 5, str(len(bcv.find_all())))
bw.geometry("900x200"); pump(350); small = big_px(bcv)
bw.geometry("900x420"); pump(350); large = big_px(bcv)
check("broadcast text grows with the window", large > small * 1.5 > 0, f"{small} -> {large}")
_bt = [bcv.itemcget(i, "text") for i in bcv.find_all() if bcv.type(i) == "text"]
check("broadcast shows theme and play count", any(ad.main_theme(TODAY.isoformat(), data["pb"])[1] in x for x in _bt) and any(x.endswith("판") for x in _bt), str(_bt[:4]))
check("broadcast carries the three verdicts", (any(x == "오늘" for x in _bt) and any(x.startswith("요즘") for x in _bt) and any(x.startswith("성장") for x in _bt)) or any("요즘" in x and "성장" in x for x in _bt), str(_bt)[:200])   # 좁은 창(<620px)은 한 줄 요약
bw.destroy(); pump(80)
# 글씨 크기 설정은 저장되고 다시 켤 때 쓰인다 (테스트에선 프로세스를 띄우지 않는다)
D["set_scale"](1.5); pump(60)
check("scale setting saved for next launch", data.get("ui_scale") == 1.5 and "geo" not in data["win"], str(data.get("ui_scale")))
check("current scale button highlighted", D["scale_btns"][1.5].bgc == ad.C["gold"], D["scale_btns"][1.5].bgc)
D["set_scale"](None); pump(60)
check("auto scale restores", data.get("ui_scale") is None and D["scale_btns"][None].bgc == ad.C["gold"])
coach = [l.cget("text") for l in D["day_state"]["coach"]]; check("coach card has lines", any(coach), str(coach)[:160])
D["show"]("tools"); pump(200); check("tools tab holds the stats folder and trainer cards", D["pl_lbl"].winfo_ismapped() and D["trainer_txt"].winfo_ismapped()); D["show"]("today"); pump(150)
D["set_drawer"](True); pump(80); check("rank feedback drawer opens with steppers", D["steppers"][0].winfo_ismapped())
D["tier_var"].set("실버 2"); D["rr_var"].set("+18"); D["commit_rank"](); check("rank tier / RR saved", data["days"][TODAY.isoformat()]["rank"] == {"tier": "실버 2", "rr": 18}, str(data["days"][TODAY.isoformat()].get("rank")))
plus = btn(D["steppers"][0], "＋"); plus.cmd(); pump(50)
check("deaths trend after +1", "1회" in D["dth_lbl"].cget("text"), D["dth_lbl"].cget("text"))
shot("1_today")
D["show"]("bench"); pump(200)
check("bench advice names the weakest link", D["advice_lbl"].cget("text").startswith("약한 고리"), D["advice_lbl"].cget("text")[:120])
wk = [k for k, (_, _, cardf) in D["ben_rows"].items() if cardf.cget("highlightbackground") == ad.C["gold"]]
check("weakest card highlighted (one)", len(wk) == 1, str(wk))
gaps = [c[3].cget("text") for c in D["ben_rows"]["react"][1]]; check("gap label for today's Ground", any(g.startswith("Gold") for g in gaps), str(gaps))
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
D["set_routine_open"](True); pump(150)
D["routine_rows"][0][8].event_generate("<Button-1>"); pump(150)
dw = D["detail"]; check("detail popup opened for ground", dw["win"] is not None and dw["win"].winfo_exists() and dw["key"] == "ground")
check("detail summary has PB and today count", "오늘 1판" in dw["sum"].cget("text") and "베스트 3000" in dw["sum"].cget("text"), dw["sum"].cget("text"))
dw["win"].geometry("+1180+560"); pump(120); shot("7_detail")
check("UI scale applied to daych", D["daych"].winfo_reqwidth() == ad.px(70), f"{D['daych'].winfo_reqwidth()} vs {ad.px(70)}")
check("window fits screen", root.winfo_width() <= root.winfo_screenwidth())
# ── v3.4 트레이너: 답장 붙여넣기 → 목표·도전·테마·메모 · 하루 기록 텍스트 저장 ──
D["show"]("today"); pump(100)
D["trainer_txt"].insert("1.0", "목표 Ground 3000\n도전 Pasu 900\n테마 내일 트래킹\n메모 첫 판 전에 손 풀기\n이상한 줄")
D["apply_trainer"](); pump(450)
check("trainer reply applied: targets + challenge + theme saved", data["trainer"]["targets"] == {"ground": 3000, "pasu": 900} and data["trainer"]["challenge"] == "pasu" and data["trainer"]["themes"] == {"2026-09-04": "trk"}, str(data.get("trainer")))
_cl = D["day_state"]["chal_lbl"]; check("challenge box shows the trainer target", _cl is not None and "Pasu 900점" in _cl.cget("text") and "트레이너 목표" in _cl.cget("text") and "200 남음" in _cl.cget("text"), _cl.cget("text") if _cl else "none")
_gr = next(r for r in D["routine_rows"] if r[1] == "ground"); check("ground row: 3000 meets 목표 3000 ✓ (green)", _gr[5].cget("text").endswith("목표 3000 ✓") and _gr[5].cget("fg") in (ad.C["ok"], ad.C["gold"]), _gr[5].cget("text"))
_pr = next(r for r in D["routine_rows"] if r[1] == "pasu"); check("pasu row: 700 vs 목표 900 not met", _pr[5].cget("text").startswith("700") and _pr[5].cget("text").endswith("목표 900"), _pr[5].cget("text"))
_st = D["trainer_lbl"].cget("text"); check("trainer status lists targets, theme, memo and the unread line", "목표 2개" in _st and "09/04 트래킹 집중" in _st and "손 풀기" in _st and "읽지 못한 줄 1" in _st, _st)
check("paste box cleared after apply", D["trainer_txt"].get("1.0", "end").strip() == "")
check("routine card shows the trainer memo", any(x.startswith("트레이너 메모 · 첫 판 전에 손 풀기") for x in texts(root)))
ke4 = KE(); ke4.widget = D["trainer_txt"]; ke4.keysym = "2"; ke4.state = 0
D["on_key"](ke4); pump(50); check("'2' typed in the paste box does not switch tab", D["cur_tab"][0] == "today")
_rp = D["save_report_today"](True); pump(100)
check("report saved as 기록/에임데스크_<date>.txt", _rp is not None and _rp.exists() and _rp == TMP / "기록" / "에임데스크_2026-09-03.txt", str(_rp))
_rt = _rp.read_text(encoding="utf-8-sig") if _rp else ""
check("report has every section and today's numbers", all(x in _rt for x in ("[요약]", "[판정]", "[판별 기록]", "[시나리오별]", "[트레이너 목표 현황]", "[트레이너에게]", "[데이터]")) and "판 5/27" in _rt and "랭크 실버 2 RR +18" in _rt and "Ground" in _rt and "목표  3000 · 오늘  3000  ✓ 넘음" in _rt and "메모: 첫 판 전에 손 풀기" in _rt, _rt[:300])
check("status line shows today's report saved", "에임데스크_2026-09-03.txt ✓" in D["trainer_lbl"].cget("text"), D["trainer_lbl"].cget("text")[-80:])
shot("9_trainer")
# 오늘 테마를 바꾸는 답장 → 열려 있는 순서창도 새 계획으로 다시 열린다 (자동 진행 상태는 유지)
_nf = len(fired); _old_seq = list(D["seq_win"]["seq"])
D["trainer_txt"].insert("1.0", "테마 오늘 트래킹"); D["apply_trainer"](); pump(500)
top = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel) and w.title().startswith("오늘 순서")][0]
check("today's theme override rebuilds the plan and reopens the sequence window", data["trainer"]["themes"].get("2026-09-03") == "trk" and D["seq_win"]["seq"] != _old_seq and D["seq_win"]["seq"].count("raw") >= 5 and len(D["seq_win"]["rows"]) == 27 and top.winfo_exists(), str(D["seq_win"]["seq"][10:16]))
check("theme override keeps auto mode and sends nothing by itself", D["auto"]["on"] and len(fired) == _nf, f"{D['auto']['on']} {len(fired) - _nf}")
_pl = json.loads((TMP / "FPSAimTrainer" / "Saved" / "SaveGames" / "Playlists" / "AIMDESK Day.json").read_bytes().decode("utf-16"))
check("installed AIMDESK Day.json follows the new theme", sum(1 for x in _pl["scenarioList"] if x["scenario_Name"] == "VT Raw Control Novice S5") >= 1 and len(_pl["scenarioList"]) == len(D["seq_win"]["rows"]) or sum(x.get("play_Count", 1) for x in _pl["scenarioList"]) == 27, str([x["scenario_Name"] for x in _pl["scenarioList"]][-4:]))
(TMP / "기록" / "에임데스크_2026-09-03.txt").unlink()          # 아래 자정 통과 검사: 켜 둔 채 날이 바뀌면 어제 기록이 다시 저장돼야 한다
# ── 토요일(벤치 데이)로 날짜가 넘어감 → AIMDESK Bench 플레이리스트 · 줄 18개 ──
btn(top, "딥링크 방식").cmd(); pump(50)
os.environ["AIMDESK_TODAY"] = "2026-09-05"; scan(); pump(700)
check("day change → bench day with AIMDESK Bench", D["day_state"]["dt"] == "b" and D["day_state"]["pl"] == "AIMDESK Bench", str(D["day_state"]["dt"]))
check("day change wrote yesterday's report first", (TMP / "기록" / "에임데스크_2026-09-03.txt").exists() and "판 5/27" in (TMP / "기록" / "에임데스크_2026-09-03.txt").read_text(encoding="utf-8-sig"))
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
check("on_close wrote the bench-day report", (TMP / "기록" / "에임데스크_2026-09-05.txt").exists() and "벤치마크" in (TMP / "기록" / "에임데스크_2026-09-05.txt").read_text(encoding="utf-8-sig"))
check("trainer targets survive in the saved file", saved.get("trainer", {}).get("targets") == {"ground": 3000, "pasu": 900})
log = (TMP / "aim_desk.log").read_text() if (TMP / "aim_desk.log").exists() else ""
check("no exceptions logged", log.strip() == "", log[-600:])
n_ok = sum(1 for _, ok in results if ok)
print(f"SUMMARY: {n_ok} / {len(results)} passed")
sys.exit(0 if n_ok == len(results) else 1)
