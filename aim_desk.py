#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
에임 데스크 v2 — 코박스 자동 기록 + 성장 시각화
· stats 폴더 2초 감시: 판 수/점수/신기록 실시간 자동
· 프로브(첫 판) 지수, 볼테익 동일 수식 에너지·랭크
· 실행: python aim_desk.py  (파이썬 3.9+, 추가 설치 없음)
"""
from __future__ import annotations
import json, os, re, sys
from datetime import date, datetime
from pathlib import Path

# ══════════════════ 시나리오 정의 ══════════════════
SCEN = {
    "pasu":   ("VT Pasu Novice S5", "v"),      "popcorn": ("VT Popcorn Novice S5", "v"),
    "w4":     ("VT 1w4ts Novice S5", "v"),     "ww5":     ("VT ww5t Novice S5", "v"),
    "frog":   ("VT Frogtagon Novice S5", "v"), "float":   ("VT Floating Heads Novice S5", "v"),
    "pgt":    ("VT PGT Novice S5", "o"),       "snake":   ("VT Snake Track Novice S5", "o"),
    "aether": ("VT Aether Novice S5", "o"),    "ground":  ("VT Ground Novice S5", "o"),
    "raw":    ("VT Raw Control Novice S5","o"),"csphere": ("VT Controlsphere Novice S5","o"),
    "dot":    ("VT DotTS Novice S5", "v"),     "eddie":   ("VT EddieTS Novice S5", "v"),
    "drift":  ("VT DriftTS Novice S5", "v"),   "fly":     ("VT FlyTS Novice S5", "o"),
    "cts":    ("VT ControlTS Novice S5", "v"), "penta":   ("VT Penta Bounce Novice S5","v"),
}
NAME2KEY = {v[0]: k for k, v in SCEN.items()}
PROBE = ["w4", "pasu", "eddie", "snake", "aether", "fly"]          # 측정: 그날 '첫 판'
WARMUP = [("ground", 2), ("frog", 1), ("float", 1)]               # 트래킹 웜업→정확→속도 (중복 없음)
MAIN   = [("ww5", 3), ("popcorn", 3), ("dot", 6), ("drift", 3), ("cts", 2)]
FRIDAY = [("raw", 12), ("csphere", 12)]

SUBS = [
 ("dyn","클리킹","Dynamic",  [("pasu",[555,660,745,800]),("popcorn",[390,500,600,720])]),
 ("stat","클리킹","Static",  [("w4",[820,915,1010,1110]),("ww5",[990,1090,1190,1290])]),
 ("lin","클리킹","Linear",   [("frog",[620,740,850,980]),("float",[375,460,540,640])]),
 ("prec","트래킹","Precise", [("pgt",[1900,2325,2775,3050]),("snake",[2400,2750,3125,3425])]),
 ("react","트래킹","Reactive",[("aether",[1525,1900,2250,2650]),("ground",[2100,2500,2825,3100])]),
 ("ctrl","트래킹","Control", [("raw",[2125,2550,2975,3450]),("csphere",[1575,1950,2400,2900])]),
 ("speed","스위칭","Speed",  [("dot",[845,940,1030,1090]),("eddie",[640,730,810,890])]),
 ("evas","스위칭","Evasive", [("drift",[315,355,390,430]),("fly",[420,460,500,535])]),
 ("stab","스위칭","Stability",[("cts",[340,380,420,450]),("penta",[290,340,390,445])]),
]
RANKS = [(400,"Gold","#F5C24B"),(300,"Silver","#C9D6E2"),(200,"Bronze","#E08A3C"),(100,"Iron","#98A2AC")]
SEED_DATE = "2026-08-29"
SEED = {"pasu":806,"popcorn":660,"w4":1046,"ww5":1260,"frog":930,"float":613,
        "pgt":2744,"snake":3211,"aether":2477,"ground":3181,"raw":2664,"csphere":2238,
        "dot":970,"eddie":780,"drift":385,"fly":522,"cts":422,"penta":413}

FNAME_RE = re.compile(r"^(?P<scen>.+) - Challenge - (?P<d>\d{4}\.\d{2}\.\d{2})-(?P<t>\d{2}\.\d{2}\.\d{2}) Stats\.csv$")
SCORE_RE = re.compile(r"^\s*Score\s*:?\s*,\s*(?P<v>[-\d.,]+)", re.I)
DEFAULT_STATS = [
    r"C:\Program Files (x86)\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats",
    r"C:\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats",
    r"D:\Steam\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats",
    r"D:\SteamLibrary\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats",
    r"E:\SteamLibrary\steamapps\common\FPSAimTrainer\FPSAimTrainer\stats",
]
def _base_dir():
    # exe(PyInstaller)로 얼려진 경우 exe 옆에, 스크립트면 스크립트 옆에 저장
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent
DATA_FILE = _base_dir() / "aim_desk_data.json"
DOWK = ["월","화","수","목","금","토","일"]

# ══════════════════ 데이터 ══════════════════
def load_data() -> dict:
    d = {"stats_dir": None, "pb": {}, "days": {}, "seeded": False}
    if DATA_FILE.exists():
        try: d.update(json.loads(DATA_FILE.read_text(encoding="utf-8")))
        except Exception: pass
    if not d.get("seeded"):
        d["days"].setdefault(SEED_DATE, blank_day())["best"] = dict(SEED)
        for k, v in SEED.items():
            d["pb"][k] = max(d["pb"].get(k, 0), v)
        d["seeded"] = True
    return d

def blank_day() -> dict:
    return {"first": {}, "best": {}, "count": {},
            "deaths": {"aim":0,"pos":0,"dec":0,"trade":0},
            "cond": {"sleep":None,"caf":0,"feel":5},
            "checks": {"miyagi":False,"ranked":False}}

def save_data(d: dict):
    try: DATA_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception as e: print("save fail:", e)

# ══════════════════ 코박스 파싱 ══════════════════
def read_score(fp: Path):
    s = None
    try:
        with fp.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                m = SCORE_RE.match(line)
                if m:
                    try: s = float(m.group("v").replace(",", ""))
                    except ValueError: pass
    except OSError: return None
    return s

SCAN_INFO = {"plays": 0, "miss": 0, "t": ""}

def scan_day(stats: Path, day: date):
    """해당 날짜의 (key, 'HH.MM.SS', score) 목록 + 진단 집계"""
    tag = day.strftime("%Y.%m.%d"); out = []; miss = 0
    try: it = list(stats.iterdir())
    except OSError: return out
    for fp in it:
        m = FNAME_RE.match(fp.name)
        if not m or m.group("d") != tag: continue
        key = NAME2KEY.get(m.group("scen"))
        sc = read_score(fp)
        if key is None or sc is None:
            miss += 1; continue
        out.append((key, m.group("t"), round(sc)))
    SCAN_INFO.update(plays=len(out), miss=miss,
                     t=datetime.now().strftime("%H:%M:%S"))
    return out

def apply_scan(data: dict, plays, dkey: str):
    """오늘 판들을 반영. (신기록 이벤트 목록, 변경 여부) 반환"""
    day = data["days"].setdefault(dkey, blank_day())
    first, best, count = {}, {}, {}
    for key, t, s in sorted(plays, key=lambda x: x[1]):
        count[key] = count.get(key, 0) + 1
        if key not in first: first[key] = s
        best[key] = max(best.get(key, 0), s)
    changed = (first != day["first"] or best != day["best"] or count != day["count"])
    day["first"], day["best"], day["count"] = first, best, count
    events = []
    for k, s in best.items():
        if s > data["pb"].get(k, 0):
            events.append((k, s, s - data["pb"].get(k, 0)))
            data["pb"][k] = s
    return events, changed

# ══════════════════ 볼테익 에너지 (검증 완료 수식) ══════════════════
def scenE(x, th):
    if x is None: return None
    a,b,c,d = th
    if x < a: return max(0, int(100*x/a))
    if x < b: return int(100+100*(x-a)/(b-a))
    if x < c: return int(200+100*(x-b)/(c-b))
    if x < d: return int(300+100*(x-c)/(d-c))
    return int(400+100*(x-d)/(d-c))

def subE(sub, scores):
    es = [scenE(scores.get(k), th) for k, th in sub[3]]
    es = [e for e in es if e is not None]
    return max(es) if es else None

def totalE(scores):
    es = [subE(s, scores) for s in SUBS]
    es = [e for e in es if e is not None]
    if not es: return None, 0
    return int(len(es)/sum(1/max(e,1) for e in es)), len(es)

def rank_of(e):
    if e is None: return ("—", "#5C6C7C")
    for t, n, c in RANKS:
        if e >= t: return (n, c)
    return ("Unranked", "#5C6C7C")

# ══════════════════ 프로브 지수 ══════════════════
def probe_series(data: dict):
    keys = sorted(k for k in data["days"] if data["days"][k]["first"])
    out = []
    for i, k in enumerate(keys):
        e = data["days"][k]; prior = keys[max(0,i-30):i]
        zs = {"v": [], "o": []}
        for pk in PROBE:
            x = e["first"].get(pk)
            if x is None: continue
            base = [data["days"][p]["first"].get(pk) for p in prior]
            base = [b for b in base if b is not None]
            if len(base) < 3: continue
            m = sum(base)/len(base)
            sd = (sum((b-m)**2 for b in base)/len(base)) ** .5
            if sd < 1e-9: continue
            zs[SCEN[pk][1]].append(max(-3, min(3, (x-m)/sd)))
        vi = sum(zs["v"])/len(zs["v"]) if zs["v"] else None
        oi = sum(zs["o"])/len(zs["o"]) if zs["o"] else None
        out.append({"date": k, "vi": vi, "oi": oi})
    for i, p in enumerate(out):
        for a, b in (("vi","maV"), ("oi","maO")):
            w = [q[a] for q in out[max(0,i-6):i+1] if q[a] is not None]
            p[b] = sum(w)/len(w) if w else None
    return out

def bench_days(data: dict):
    out = []
    for k in sorted(data["days"]):
        e, n = totalE(data["days"][k]["best"])
        if e is not None and n == 9:
            out.append((k, e))
    return out



# ══════════════════ 플레이리스트 자동 설치 / 실행 ══════════════════
def _pl(name, items):
    return {"playlistName": name, "playlistId": 0, "authorSteamId": "",
            "authorName": "aimdesk", "scenarioList":
            [{"scenario_Name": SCEN[k][0], "play_Count": c} for k, c in items],
            "description": "", "hasOfflineScenarios": False,
            "hasEdited": True, "shareCode": ""}

PLAYLISTS = [
    ("AIMDESK Day",     WARMUP + [(k, 1) for k in PROBE] + MAIN),
    ("AIMDESK Friday",  WARMUP + [(k, 1) for k in PROBE] + FRIDAY),
    ("AIMDESK Probe",   [(k, 1) for k in PROBE]),
]

def playlists_dir(stats_dir):
    r"""...\FPSAimTrainer\stats -> ...\FPSAimTrainer\Saved\SaveGames\Playlists"""
    p = Path(stats_dir)
    return p.parent / "Saved" / "SaveGames" / "Playlists"

def ensure_playlists(stats_dir):
    """플레이리스트 JSON(UTF-16)을 코박스 폴더에 설치. (성공 개수, 폴더) 반환"""
    try:
        d = playlists_dir(stats_dir)
        if not d.is_dir(): return 0, d
        ok = 0
        for name, items in PLAYLISTS:
            txt = json.dumps(_pl(name, items), ensure_ascii=False, indent="\t")
            payload = (txt.replace("\n", "\r\n") + "\n").encode("utf-16")
            fp = d / (name + ".json")
            try:
                if not fp.exists() or fp.read_bytes() != payload:
                    fp.write_bytes(payload)
                ok += 1
            except OSError: pass
        return ok, d
    except Exception:
        return 0, None

def open_uri(uri):
    try:
        if sys.platform == "win32":
            os.startfile(uri)  # steam:// 포함
        else:
            import webbrowser; webbrowser.open(uri)
        return True
    except Exception:
        return False

def launch_kovaaks():
    return open_uri("steam://rungameid/824270")

ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACkUlEQVR4nO1bwWrDMAxNxo6Dwc6D0vYy9v/fMnppS2HnQCD37WQwiSVL1pPTpn6nrY4dvWfZsmyn6xqeG31Jpbf3jz+0IShM46DiJH74nklTkIghEsCL/OV6O4e/D/vd0eMdORFeucJH7PU5AgdKiJdcxa2A4pMUYGvkA1K8SA94FiwE2GrvB8z59VyhB+KZn4JXRIgRJsUqAkhIU/AOj24CWEhTQIqxEKAW+ZgEtRCS1rdiGoeeXQhpQRmuNZoTI/yPEgIWBlPkD/vd0Woo1QZqiEEEmBuDID5Hqk2ECOY5IEXealStd07j0JsEKDUEMckhRDAJoDWgxF21bWpFmMahh8wBHuQl9RDDrcgDpBsZJWHRWkcjSpEHSHuzNCxaw57W20xDgCKDCIuasGcZCu77AYiFEMqWFFQCSMaax0anJE+Q5hJzQD3AIwP0fg80GYqR6/3T9+fit6+fX7Y9D4HFHoB07RR57ncpSoaBSzbICZQjyZWXjnMOVXeFpT1s9QQNFnOARNk1MkCpLZKy2N52LrC2AWtjMQRqLnAQ4JbLEjuregAX50ueQwAmgDRE5chx5R5eKBYAGYMpktaeLxHIbSl8ud7OnBFasl55BnQOqDU5It+jEsAzLeXgmYa7RwGrCN4ptkkA6RbV5Xo7a4mk6ki34DRQCyB1L2pjM2cs9YzlvRwgByNe5wLatlc7GPE6wPAUNqCdDYZ/2umw4YoMwhNq9nyA2+FoSdjLQRMWNXDJBgMQQljDYg7QZCgYRV1sip/hUOuWWNe1e4Ltpmi7KzwvqHlbfK2N1vjrkUUU0H519WiY83v6c4GkAFv1ghQv0gO2JgLFh10IhUqP/BlNriPbl6MlDd+zGFsbuu74B4fxI3bL2IpFAAAAAElFTkSuQmCC"
# ══════════════════ GUI (v2 — 커스텀 위젯) ══════════════════
C = {"bg":"#0B0E11","card":"#14191F","card2":"#1D242C","c3":"#242C35","line":"#28313B",
     "txt":"#EDF1F5","sub":"#8CA0B3","dim":"#5C6C7C",
     "val":"#E8453A","ow":"#3B87F7","ok":"#4ED490","gold":"#F5C24B"}
RANKC = ["#98A2AC", "#E08A3C", "#C9D6E2", "#F5C24B"]

def main():
    import tkinter as tk
    import tkinter.font as tkfont
    from tkinter import filedialog

    data = load_data()
    root = tk.Tk(); root.withdraw()
    root.title("에임 데스크"); root.configure(bg=C["bg"])
    root.geometry("1060x760"); root.minsize(960, 660)
    try: root.iconphoto(True, tk.PhotoImage(data=ICON_B64))
    except Exception: pass

    FAM = "Malgun Gothic" if "Malgun Gothic" in tkfont.families() else "sans-serif"
    MONO = "Consolas" if "Consolas" in tkfont.families() else "TkFixedFont"
    F   = (FAM, 10);  FS  = (FAM, 9);   FB = (FAM, 10, "bold")
    FH  = (FAM, 12, "bold"); FCAP = (FAM, 9, "bold")
    FN  = (MONO, 11, "bold"); FNS = (MONO, 9, "bold"); FBIG = (MONO, 26, "bold")

    def win_dark():
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            for attr in (20, 19):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attr, ctypes.byref(ctypes.c_int(1)), 4)
        except Exception: pass

    # ── 커스텀 위젯 킷 ──────────────────────
    def rrect(cv, x1, y1, x2, y2, r=9, **kw):
        pts = [x1+r,y1, x2-r,y1, x2,y1, x2,y1+r, x2,y2-r, x2,y2,
               x2-r,y2, x1+r,y2, x1,y2, x1,y2-r, x1,y1+r, x1,y1]
        return cv.create_polygon(pts, smooth=True, **kw)

    class RBtn(tk.Canvas):
        """둥근 플랫 버튼 (호버 지원)"""
        def __init__(self, parent, text, command=None, bg=C["card2"], fg=C["txt"],
                     hover=None, font=FB, padx=14, pady=7, r=9, w=None):
            self.f = tkfont.Font(font=font)
            tw = w if w else self.f.measure(text) + padx*2
            th = self.f.metrics("linespace") + pady*2
            super().__init__(parent, width=tw, height=th, bg=parent["bg"],
                             highlightthickness=0, cursor="hand2")
            self.bgc, self.fgc = bg, fg
            self.hv = hover or self._lift(bg)
            self.shape = rrect(self, 1, 1, tw-1, th-1, r, fill=bg, outline="")
            self.lbl = self.create_text(tw//2, th//2, text=text, fill=fg, font=font)
            self.cmd = command
            self.bind("<Button-1>", lambda e: self.cmd and self.cmd())
            self.bind("<Enter>", lambda e: self.itemconfig(self.shape, fill=self.hv))
            self.bind("<Leave>", lambda e: self.itemconfig(self.shape, fill=self.bgc))
        @staticmethod
        def _lift(hexc):
            h = hexc.lstrip("#"); r,g,b = (int(h[i:i+2],16) for i in (0,2,4))
            return "#%02x%02x%02x" % (min(r+16,255), min(g+16,255), min(b+16,255))
        def restyle(self, bg=None, fg=None, text=None):
            if bg: self.bgc = bg; self.hv = self._lift(bg); self.itemconfig(self.shape, fill=bg)
            if fg: self.fgc = fg; self.itemconfig(self.lbl, fill=fg)
            if text is not None: self.itemconfig(self.lbl, text=text)

    class Toggle(RBtn):
        def __init__(self, parent, text, getter, setter):
            self.getter, self.setter = getter, setter
            super().__init__(parent, text, command=self.flip)
            self.sync()
        def flip(self):
            self.setter(not self.getter()); self.sync()
        def sync(self):
            on = self.getter()
            self.restyle(bg="#173226" if on else C["card2"],
                         fg=C["ok"] if on else C["sub"])

    class Stepper(tk.Frame):
        def __init__(self, parent, get, set_):
            super().__init__(parent, bg=parent["bg"])
            self.get, self.set_ = get, set_
            RBtn(self, "−", lambda: self.mod(-1), padx=11, pady=4).pack(side="left")
            self.v = tk.Label(self, text="0", font=FN, width=3, bg=parent["bg"], fg=C["txt"])
            self.v.pack(side="left", padx=2)
            RBtn(self, "＋", lambda: self.mod(+1), padx=10, pady=4).pack(side="left")
            self.sync()
        def mod(self, d): self.set_(max(0, self.get()+d)); self.sync()
        def sync(self): self.v.configure(text=str(self.get()))

    class Segmented(tk.Canvas):
        """체감 1~10 선택"""
        def __init__(self, parent, get, set_, n=10, cw=17, h=20):
            super().__init__(parent, width=n*(cw+3), height=h, bg=parent["bg"],
                             highlightthickness=0, cursor="hand2")
            self.n, self.cw, self.h, self.get, self.set_ = n, cw, h, get, set_
            self.bind("<Button-1>", self.click); self.draw()
        def click(self, e):
            self.set_(min(self.n, max(1, e.x // (self.cw+3) + 1))); self.draw()
        def draw(self):
            self.delete("all"); v = self.get()
            for i in range(self.n):
                x = i*(self.cw+3)
                on = i < v
                col = C["ok"] if v >= 7 else C["gold"] if v >= 4 else C["val"]
                rrect(self, x, 3, x+self.cw, self.h-1, 5,
                      fill=col if on else C["card2"], outline="")
            self.create_text(self.n*(self.cw+3)-2, 1, text=str(v), anchor="ne",
                             fill=C["txt"], font=FNS)

    def card(parent, pad=(14, 12)):
        f = tk.Frame(parent, bg=C["card"], padx=pad[0], pady=pad[1],
                     highlightbackground=C["line"], highlightthickness=1)
        return f

    def cap(parent, text, fg=None):
        return tk.Label(parent, text=text, font=FCAP, bg=parent["bg"],
                        fg=fg or C["dim"])

    # ── 상태 ──
    today_key = [date.today().isoformat()]
    def dget(): return data["days"].setdefault(today_key[0], blank_day())

    # ══ 헤더 ══
    head = tk.Frame(root, bg=C["bg"]); head.pack(fill="x", padx=18, pady=(14, 2))
    d = date.today()
    dt = ["v","v","v","v","w","b","r"][d.weekday()]
    dt_name = {"v":"발로 데이","w":"약점 데이","b":"벤치마크","r":"휴식"}[dt]
    dt_col  = {"v":C["val"],"w":"#8A94A2","b":C["gold"],"r":C["dim"]}[dt]
    lf = tk.Frame(head, bg=C["bg"]); lf.pack(side="left")
    tk.Label(lf, text="에임 데스크", font=(FAM, 16, "bold"), bg=C["bg"], fg=C["txt"]).pack(anchor="w")
    sub = tk.Frame(lf, bg=C["bg"]); sub.pack(anchor="w")
    tk.Label(sub, text=f"{d.month}월 {d.day}일 {DOWK[d.weekday()]}", font=FS,
             bg=C["bg"], fg=C["sub"]).pack(side="left")
    daych = tk.Canvas(sub, width=70, height=18, bg=C["bg"], highlightthickness=0); daych.pack(side="left", padx=8)
    rrect(daych, 0, 1, 68, 17, 8, fill=dt_col, outline="")
    daych.create_text(34, 9, text=dt_name, fill="#0B0E11", font=(FAM, 8, "bold"))

    rf = tk.Frame(head, bg=C["bg"]); rf.pack(side="right")
    hdr_e = tk.Label(rf, text="", font=(MONO, 15, "bold"), bg=C["bg"], fg=C["gold"])
    hdr_e.pack(side="right")
    hdr_r = tk.Canvas(rf, width=58, height=22, bg=C["bg"], highlightthickness=0)
    hdr_idx = tk.Label(rf, text="", font=FN, bg=C["bg"], fg=C["txt"])
    hdr_idx.pack(side="right", padx=(0, 16))
    hdr_mi = tk.Label(rf, text="", font=FNS, bg=C["bg"], fg=C["sub"])
    hdr_mi.pack(side="right", padx=(0, 16))

    # PB 토스트
    toast = tk.Frame(root, bg=C["bg"]); toast_in = tk.Frame(toast, bg="#241E0E",
        highlightbackground=C["gold"], highlightthickness=1, padx=12, pady=6)
    toast_lbl = tk.Label(toast_in, text="", font=FB, bg="#241E0E", fg=C["gold"])
    toast_lbl.pack(side="left"); toast_in.pack(fill="x")
    def show_toast(msg):
        toast_lbl.configure(text=msg)
        toast.pack(fill="x", padx=18, pady=(6, 0), after=head)
        root.after(8000, toast.pack_forget)

    # ══ 탭바 ══
    tabbar = tk.Frame(root, bg=C["bg"]); tabbar.pack(fill="x", padx=18, pady=(10, 6))
    body = tk.Frame(root, bg=C["bg"]); body.pack(fill="both", expand=True, padx=18, pady=(0, 14))
    frames, tabbtns, underls = {}, {}, {}
    def show(tab):
        for f in frames.values(): f.pack_forget()
        frames[tab].pack(fill="both", expand=True)
        for n, b in tabbtns.items():
            b.configure(fg=C["txt"] if n == tab else C["dim"])
            underls[n].configure(bg=C["val"] if n == tab else C["bg"])
        refresh()
    for name, label in (("today","오늘"),("grow","성장"),("bench","벤치")):
        holder = tk.Frame(tabbar, bg=C["bg"]); holder.pack(side="left", padx=(0, 22))
        b = tk.Label(holder, text=label, font=(FAM, 11, "bold"), bg=C["bg"],
                     fg=C["dim"], cursor="hand2")
        b.pack(); b.bind("<Button-1>", lambda e, n=name: show(n))
        u = tk.Frame(holder, bg=C["bg"], height=3, width=30); u.pack(fill="x", pady=(3, 0))
        tabbtns[name], underls[name] = b, u

    # ══ 오늘 탭 ══
    ft = tk.Frame(body, bg=C["bg"]); frames["today"] = ft
    left = card(ft); left.pack(side="left", fill="both", expand=True)
    right = tk.Frame(ft, bg=C["bg"], width=310); right.pack(side="left", fill="y", padx=(14, 0))
    right.pack_propagate(False)

    lh = tk.Frame(left, bg=C["card"]); lh.pack(fill="x")
    lt = tk.Frame(lh, bg=C["card"]); lt.pack(side="left")
    tk.Label(lt, text="오늘 루틴", font=FH, bg=C["card"], fg=C["txt"]).pack(anchor="w")
    tk.Label(lt, text="판 수는 자동으로 셉니다 · 시나리오 사이엔 결과창에서 NEXT 한 번이 정상 진행",
             font=FS, bg=C["card"], fg=C["dim"]).pack(anchor="w", pady=(0, 6))
    PL_TODAY = {"v": "AIMDESK Day", "w": "AIMDESK Friday"}.get(dt)
    def run_playlist(plname):
        sd = data.get("stats_dir")
        if sd: ensure_playlists(sd)
        launched = launch_kovaaks()
        if plname:
            show_toast(f"▶ LOCAL PLAYLISTS → \"{plname}\" 재생  ·  좌하단 토글이 FREEPLAY면 CHALLENGE로! (프리플레이는 기록이 안 남습니다)"
                       + ("" if launched else "  · 스팀 실행은 수동으로"))
    if PL_TODAY:
        RBtn(lh, "▶ 오늘 루틴 실행", lambda: run_playlist(PL_TODAY),
             bg="#2A1512", fg=C["val"], padx=14, pady=8).pack(side="right", padx=(8, 0))
        RBtn(lh, "프로브만", lambda: run_playlist("AIMDESK Probe"),
             padx=12, pady=8).pack(side="right")
    elif dt == "b":
        RBtn(lh, "▶ 코박스 실행", lambda: run_playlist(None),
             bg="#2A1512", fg=C["val"], padx=14, pady=8).pack(side="right", padx=(8, 0))
        RBtn(lh, "볼테익 벤치 페이지", lambda: open_uri("https://app.voltaic.gg/benchmarks"),
             padx=12, pady=8).pack(side="right")
    routine_rows = []

    def add_section(title):
        f = tk.Frame(left, bg=C["card"]); f.pack(fill="x", pady=(10, 3))
        tk.Label(f, text=title, font=FCAP, bg=C["card"], fg=C["gold"]).pack(side="left")
        tk.Frame(f, bg=C["line"], height=1).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=1)

    def add_row(kind, key, target):
        row = tk.Frame(left, bg=C["card"]); row.pack(fill="x", pady=2)
        grp = SCEN[key][1]
        gc = C["val"] if grp == "v" else C["ow"]
        tk.Frame(row, bg=gc, width=3, height=16).pack(side="left", padx=(2, 9))
        tk.Label(row, text=SCEN[key][0].replace("VT ", "").replace(" Novice S5", ""),
                 font=F, width=13, anchor="w", bg=C["card"], fg=C["txt"]).pack(side="left")
        bar = tk.Canvas(row, height=8, bg=C["card"], highlightthickness=0)
        bar.pack(side="left", fill="x", expand=True, padx=(4, 10))
        cl = tk.Label(row, text="", font=FNS, width=5, anchor="e", bg=C["card"], fg=C["sub"])
        cl.pack(side="left")
        sl = tk.Label(row, text="", font=FNS, width=9, anchor="e", bg=C["card"], fg=C["dim"])
        sl.pack(side="left")
        routine_rows.append((kind, key, target, bar, cl, sl, gc))

    if dt in ("v", "w"):
        add_section("① 워밍업 · 트래킹 → 정확 → 속도 (점수 무시)")
        for k, n in WARMUP: add_row("warm", k, n)
        add_section("② 프로브 · 그날 첫 판이 측정값")
        for k in PROBE: add_row("probe", k, 1)
        if dt == "v":
            add_section("③ 본훈련 · 과부하 블록")
            for k, n in MAIN: add_row("main", k, n)
        else:
            add_section("③ 금요일 약점 · 컨트롤")
            for k, n in FRIDAY: add_row("main", k, n)
        add_section("④ 게임 · 미야기 → 랭크 2판 → 죽음 태그")
        tk.Label(left, text="미야기: DM에서 안 쏘고 머리만 따라가기 · 녹화 켜기",
                 font=FS, bg=C["card"], fg=C["dim"]).pack(anchor="w", padx=14)
    elif dt == "b":
        add_section("벤치마크 18개 풀런")
        tk.Label(left, text="볼테익 Open playlist로 실행 — 점수는 자동 수집, 벤치 탭에서 실시간으로 차오릅니다.",
                 font=F, bg=C["card"], fg=C["sub"], wraplength=520, justify="left").pack(anchor="w", pady=6)
    else:
        add_section("휴식")
        tk.Label(left, text="손목도 데이터의 일부입니다. 오늘은 컨디션만 적어도 됩니다.",
                 font=F, bg=C["card"], fg=C["sub"]).pack(anchor="w", pady=6)

    # 우측 카드들
    ck = card(right); ck.pack(fill="x", pady=(0, 10))
    tk.Label(ck, text="했나요", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 7))
    tr = tk.Frame(ck, bg=C["card"]); tr.pack(anchor="w")
    tg1 = Toggle(tr, "미야기 완료", lambda: dget()["checks"]["miyagi"],
                 lambda v: (dget()["checks"].__setitem__("miyagi", v), save_data(data), refresh()))
    tg1.pack(side="left", padx=(0, 8))
    tg2 = Toggle(tr, "랭크 2판", lambda: dget()["checks"]["ranked"],
                 lambda v: (dget()["checks"].__setitem__("ranked", v), save_data(data)))
    tg2.pack(side="left")

    dk = card(right); dk.pack(fill="x", pady=(0, 10))
    tk.Label(dk, text="오늘 죽은 이유", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w")
    tk.Label(dk, text="랭크 리뷰하며 + 누르기", font=FS, bg=C["card"], fg=C["dim"]).pack(anchor="w", pady=(0, 6))
    steppers = []
    for key, name in (("aim","에임"),("pos","위치"),("dec","판단"),("trade","트레이드")):
        row = tk.Frame(dk, bg=C["card"]); row.pack(fill="x", pady=2)
        tk.Label(row, text=name, font=F, width=8, anchor="w", bg=C["card"], fg=C["txt"]).pack(side="left")
        st_ = Stepper(row,
                      lambda k=key: dget()["deaths"][k],
                      lambda v, k=key: (dget()["deaths"].__setitem__(k, v), save_data(data)))
        st_.pack(side="right"); steppers.append(st_)

    cd = card(right); cd.pack(fill="x", pady=(0, 10))
    tk.Label(cd, text="컨디션", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 6))
    rowc = tk.Frame(cd, bg=C["card"]); rowc.pack(fill="x")
    tk.Label(rowc, text="수면(h)", font=FS, bg=C["card"], fg=C["sub"]).pack(side="left")
    sleep_var = tk.StringVar(value="" if dget()["cond"]["sleep"] is None else str(dget()["cond"]["sleep"]))
    def on_sleep(*_):
        v = sleep_var.get().strip()
        try:
            dget()["cond"]["sleep"] = float(v) if v else None; save_data(data)
        except ValueError: pass
    sleep_var.trace_add("write", on_sleep)
    ent = tk.Entry(rowc, textvariable=sleep_var, width=5, font=FN, bg=C["card2"], fg=C["txt"],
                   insertbackground=C["txt"], bd=0, justify="center")
    ent.pack(side="left", padx=(8, 0), ipady=4)
    rowf = tk.Frame(cd, bg=C["card"]); rowf.pack(fill="x", pady=(8, 0))
    tk.Label(rowf, text="체감", font=FS, bg=C["card"], fg=C["sub"]).pack(side="left")
    seg = Segmented(rowf, lambda: dget()["cond"]["feel"],
                    lambda v: (dget()["cond"].__setitem__("feel", v), save_data(data)))
    seg.pack(side="left", padx=(8, 0))

    stc = card(right); stc.pack(fill="x")
    tk.Label(stc, text="코박스 stats 폴더", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w")
    stats_lbl = tk.Label(stc, text="", font=(MONO, 8), bg=C["card"], fg=C["dim"],
                         wraplength=270, justify="left")
    stats_lbl.pack(anchor="w", pady=(4, 6))
    def pick_stats():
        p = filedialog.askdirectory(title="…\\FPSAimTrainer\\FPSAimTrainer\\stats 선택")
        if p: data["stats_dir"] = p; save_data(data); sync_stats_lbl()
    plrow = tk.Frame(stc, bg=C["card"]); plrow.pack(fill="x", pady=(0, 2))
    RBtn(plrow, "폴더 선택", pick_stats, padx=12, pady=5).pack(side="left")
    RBtn(plrow, "플레이리스트 재설치", lambda: (install_playlists(), None),
         padx=12, pady=5).pack(side="left", padx=(8, 0))
    pl_lbl = tk.Label(stc, text="", font=FS, bg=C["card"], fg=C["dim"], wraplength=268, justify="left"); pl_lbl.pack(anchor="w", pady=(5, 0))
    scan_lbl = tk.Label(stc, text="", font=FS, bg=C["card"], fg=C["dim"], wraplength=268, justify="left"); scan_lbl.pack(anchor="w", pady=(3, 0))
    def install_playlists():
        sd = data.get("stats_dir")
        if not sd:
            pl_lbl.configure(text="stats 폴더를 먼저 지정하세요", fg=C["val"]); return
        n, d_ = ensure_playlists(sd)
        if n: pl_lbl.configure(text=f"플레이리스트 {n}개 설치 ✓ — 코박스 Local Playlists에 AIMDESK", fg=C["ok"])
        else: pl_lbl.configure(text="설치 실패 — Playlists 폴더를 못 찾았습니다", fg=C["val"])
    def sync_stats_lbl():
        ok = data.get("stats_dir") and Path(data["stats_dir"]).is_dir()
        stats_lbl.configure(text=(data["stats_dir"] if ok else "자동 탐지 실패 — 폴더를 선택해 주세요"),
                            fg=C["dim"] if ok else C["val"])

    # ══ 성장 탭 ══
    fg_ = tk.Frame(body, bg=C["bg"]); frames["grow"] = fg_
    idx_card = card(fg_, pad=(0, 0)); idx_card.pack(fill="x", pady=(0, 12))
    cv_idx = tk.Canvas(idx_card, height=236, bg=C["card"], highlightthickness=0); cv_idx.pack(fill="x")
    ben_card = card(fg_, pad=(0, 0)); ben_card.pack(fill="x", pady=(0, 12))
    cv_ben = tk.Canvas(ben_card, height=196, bg=C["card"], highlightthickness=0); cv_ben.pack(fill="x")
    spark = tk.Frame(fg_, bg=C["bg"]); spark.pack(fill="both", expand=True)
    spark_cvs = {}
    for i, k in enumerate(PROBE):
        cell = card(spark, pad=(10, 8))
        cell.grid(row=i//3, column=i % 3, sticky="nsew", padx=(0, 12), pady=(0, 12))
        spark.grid_columnconfigure(i % 3, weight=1)
        top = tk.Frame(cell, bg=C["card"]); top.pack(fill="x")
        tk.Label(top, text=SCEN[k][0].replace("VT ", "").replace(" Novice S5", ""), font=FB,
                 bg=C["card"], fg=C["val"] if SCEN[k][1] == "v" else C["ow"]).pack(side="left")
        pbl = tk.Label(top, text="", font=FNS, bg=C["card"], fg=C["sub"]); pbl.pack(side="right")
        cv = tk.Canvas(cell, height=48, bg=C["card"], highlightthickness=0); cv.pack(fill="x")
        spark_cvs[k] = (cv, pbl)

    # ══ 벤치 탭 ══
    fb_ = tk.Frame(body, bg=C["bg"]); frames["bench"] = fb_
    ben_head = card(fb_); ben_head.pack(fill="x", pady=(0, 12))
    ben_total = tk.Label(ben_head, text="—", font=FBIG, bg=C["card"], fg=C["gold"])
    ben_total.pack(side="left")
    ben_rankcv = tk.Canvas(ben_head, width=76, height=26, bg=C["card"], highlightthickness=0)
    ben_rankcv.pack(side="left", padx=14)
    tk.Label(ben_head, text="총 에너지 · Novice S5 · 볼테익 동일 수식", font=FS,
             bg=C["card"], fg=C["dim"]).pack(side="left")
    ben_src = tk.Label(ben_head, text="", font=FNS, bg=C["card"], fg=C["dim"])
    ben_src.pack(side="right")
    RBtn(ben_head, "내 볼테익 프로필", lambda: open_uri("https://app.voltaic.gg/j0y0nho"),
         padx=12, pady=5).pack(side="right", padx=(0, 12))

    ben_body = tk.Frame(fb_, bg=C["bg"]); ben_body.pack(fill="both", expand=True)
    ben_rows = {}
    colf = [tk.Frame(ben_body, bg=C["bg"]) for _ in range(3)]
    for i, f in enumerate(colf):
        f.grid(row=0, column=i, sticky="nsew", padx=(0, 12))
        ben_body.grid_columnconfigure(i, weight=1)
    CATC = {"클리킹": C["val"], "트래킹": C["ow"], "스위칭": "#B98CFF"}
    for si, sub_ in enumerate(SUBS):
        holder = colf[si // 3]
        sc = card(holder, pad=(12, 9)); sc.pack(fill="x", pady=(0, 10))
        hd = tk.Frame(sc, bg=C["card"]); hd.pack(fill="x")
        tk.Frame(hd, bg=CATC[sub_[1]], width=8, height=8).pack(side="left", pady=3)
        tk.Label(hd, text=f" {sub_[1]} · {sub_[2]}", font=FB, bg=C["card"], fg=C["txt"]).pack(side="left")
        se_lbl = tk.Label(hd, text="—", font=FN, bg=C["card"], fg=C["dim"]); se_lbl.pack(side="right")
        cells = []
        for k, th in sub_[3]:
            r1 = tk.Frame(sc, bg=C["card"]); r1.pack(fill="x", pady=(7, 1))
            tk.Label(r1, text=SCEN[k][0].replace("VT ", "").replace(" Novice S5", ""), font=FS,
                     bg=C["card"], fg=C["sub"]).pack(side="left")
            sc_lbl = tk.Label(r1, text="—", font=FN, bg=C["card"], fg=C["txt"]); sc_lbl.pack(side="right")
            cvth = tk.Canvas(sc, height=22, bg=C["card"], highlightthickness=0)
            cvth.pack(fill="x")
            cells.append((k, th, sc_lbl, cvth))
        ben_rows[sub_[0]] = (se_lbl, cells)

    def draw_thcells(cv, th, score):
        cv.delete("all")
        W = max(cv.winfo_width(), 200); h = 22; skew = 7; gap = 5
        cw = (W - gap*3 - skew) / 4
        p = -1
        if score is not None:
            for i, t in enumerate(th):
                if score >= t: p = i
        for i, t in enumerate(th):
            x = i * (cw + gap)
            hit = i <= p
            fill = RANKC[i] if hit else C["card2"]
            cv.create_polygon(x+skew, 1, x+cw+skew, 1, x+cw, h-1, x, h-1,
                              fill=fill, outline="")
            cv.create_text(x + (cw+skew)/2, h/2, text=str(t), font=FNS,
                           fill="#10141A" if hit else C["dim"])

    def rank_pill(cv, name, color, w=76):
        cv.delete("all")
        if not name or name == "—": return
        rrect(cv, 0, 2, w, 24, 10, fill=color, outline="")
        cv.create_text(w/2, 13, text=name, font=(FAM, 9, "bold"), fill="#0B0E11")

    # ── 차트 ──
    def draw_idx(cv, series):
        cv.delete("all"); W = max(cv.winfo_width(), 400); H = 236
        cv.create_text(16, 16, text="프로브 지수", anchor="w", fill=C["txt"], font=FB)
        cv.create_text(W-16, 16, text="점 = 일별 · 선 = 7일 평균", anchor="e", fill=C["dim"], font=FS)
        cv.create_rectangle(96, 11, 108, 14, fill=C["val"], outline="")
        cv.create_text(112, 13, text="발로", anchor="w", fill=C["sub"], font=FS)
        cv.create_rectangle(146, 11, 158, 14, fill=C["ow"], outline="")
        cv.create_text(162, 13, text="옵치", anchor="w", fill=C["sub"], font=FS)
        pts = [p for p in series if p["vi"] is not None or p["oi"] is not None][-30:]
        L, R, T, B = 46, 18, 38, 24
        def X(i): return L + (W-L-R) * (0.5 if len(pts) < 2 else i/(len(pts)-1))
        def Y(v): return T + (H-T-B) * (1 - (v+3)/6)
        for v in (-2, 0, 2):
            cv.create_line(L, Y(v), W-R, Y(v), fill="#222A32" if v else "#39434E")
            cv.create_text(L-9, Y(v), text=f"{v:+d}" if v else "0", anchor="e",
                           fill=C["dim"], font=FNS)
        if not pts:
            cv.create_text((L+W-R)/2, (T+H-B)/2,
                           text="프로브를 시작하면 여기서 성장 곡선이 자랍니다  ·  지수는 4일차부터",
                           fill=C["dim"], font=F)
            return
        for a, col in (("vi", C["val"]), ("oi", C["ow"])):
            for i, p in enumerate(pts):
                if p[a] is not None:
                    x, y = X(i), Y(p[a])
                    cv.create_oval(x-3, y-3, x+3, y+3, fill=col, outline="")
        for a, col in (("maV", C["val"]), ("maO", C["ow"])):
            seq = [(X(i), Y(p[a])) for i, p in enumerate(pts) if p[a] is not None]
            if len(seq) > 1:
                cv.create_line(*[c for xy in seq for c in xy], fill=col, width=3, smooth=True)
        cv.create_text(L, H-10, text=pts[0]["date"][5:], anchor="w", fill=C["dim"], font=FNS)
        cv.create_text(W-R, H-10, text=pts[-1]["date"][5:], anchor="e", fill=C["dim"], font=FNS)

    def draw_bench_chart(cv, bd):
        cv.delete("all"); W = max(cv.winfo_width(), 400); H = 196
        cv.create_text(16, 16, text="벤치마크 총 에너지", anchor="w", fill=C["txt"], font=FB)
        cv.create_text(W-16, 16, text="랭크 선을 넘는 순간이 보입니다", anchor="e", fill=C["dim"], font=FS)
        L, R, T, B = 70, 18, 38, 22
        def Y(v): return T + (H-T-B) * (1 - v/520)
        for (t, n, c) in RANKS:
            cv.create_line(L, Y(t), W-R, Y(t), fill="#2A333D", dash=(3, 4))
            cv.create_text(L-10, Y(t), text=n, anchor="e", fill=c, font=FNS)
        if not bd:
            cv.create_text((L+W-R)/2, (T+H-B)/2, text="토요일 풀런이 쌓이면 계단이 생깁니다",
                           fill=C["dim"], font=F)
            return
        def X(i): return L + (W-L-R) * (0.5 if len(bd) < 2 else i/(len(bd)-1))
        seq = [(X(i), Y(e)) for i, (k, e) in enumerate(bd)]
        if len(seq) > 1:
            cv.create_line(*[c for xy in seq for c in xy], fill=C["gold"], width=3)
        for i, (k, e) in enumerate(bd):
            x, y = X(i), Y(e)
            cv.create_oval(x-4, y-4, x+4, y+4, fill=C["gold"], outline="")
            cv.create_text(x, y-14, text=str(e), fill=C["txt"], font=FNS)
            cv.create_text(x, H-10, text=k[5:], fill=C["dim"], font=FNS)

    def draw_spark(k, cv, pbl):
        cv.delete("all"); W = max(cv.winfo_width(), 200); H = 48
        days = sorted(d_ for d_ in data["days"] if data["days"][d_]["first"].get(k) is not None)[-14:]
        vals = [data["days"][d_]["first"][k] for d_ in days]
        pb = data["pb"].get(k); delta = ""
        if len(vals) >= 2:
            base = sum(vals[:-1]) / len(vals[:-1]); df = vals[-1] - base
            delta = f"  {'▲' if df >= 0 else '▼'}{abs(df):.0f}"
        pbl.configure(text=f"PB {pb}{delta}" if pb else "")
        if len(vals) < 2:
            cv.create_text(W/2, H/2, text="첫 판 2개부터 선이 생깁니다", fill=C["dim"], font=FS)
            return
        lo, hi = min(vals), max(vals)
        if hi == lo: hi += 1
        col = C["val"] if SCEN[k][1] == "v" else C["ow"]
        seq = [(6 + (W-12)*i/(len(vals)-1), H-7 - (H-16)*(v-lo)/(hi-lo)) for i, v in enumerate(vals)]
        cv.create_line(*[c for xy in seq for c in xy], fill=col, width=2, smooth=True)
        x, y = seq[-1]
        cv.create_oval(x-3, y-3, x+3, y+3, fill=col, outline="")

    # ── 갱신 ──
    def bench_source():
        dkey = today_key[0]
        if data["days"].get(dkey, {}).get("best"): return dkey
        cands = [k for k in sorted(data["days"]) if data["days"][k]["best"]]
        return cands[-1] if cands else None

    def refresh():
        dkey = today_key[0]; day = data["days"].get(dkey, blank_day())
        warm_t = dict((k, n) for k, n in WARMUP)
        for kind, key, target, bar, cl, sl, gc in routine_rows:
            c = day["count"].get(key, 0)
            if kind == "main" and key in warm_t:
                c = max(0, c - warm_t[key])
            done = (day["first"].get(key) is not None) if kind == "probe" else c >= target
            bar.delete("all")
            bw = max(bar.winfo_width(), 60)
            rrect(bar, 0, 1, bw, 7, 4, fill=C["card2"], outline="")
            frac = min(1.0, c / max(target, 1))
            if frac > 0:
                rrect(bar, 0, 1, max(10, bw*frac), 7, 4,
                      fill=C["ok"] if done else gc, outline="")
            cl.configure(text=f"{min(c,99)}/{target}", fg=C["ok"] if done else C["sub"])
            if kind == "probe":
                fs = day["first"].get(key)
                sl.configure(text=f"{fs}" if fs is not None else "")
        # 헤더 지수 / 준비 카운트
        s = probe_series(data)
        last = s[-1] if s and s[-1]["date"] == dkey else None
        vi = last["vi"] if last else None; oi = last["oi"] if last else None
        if vi is not None or oi is not None:
            parts = []
            if vi is not None: parts.append(f"발로 {vi:+.1f}")
            if oi is not None: parts.append(f"옵치 {oi:+.1f}")
            hdr_idx.configure(text=" · ".join(parts), fg=C["txt"])
        else:
            nprobe = len([1 for k_ in data["days"] if any(data["days"][k_]["first"].get(p) is not None for p in PROBE)])
            hdr_idx.configure(text=f"지수 준비 {min(nprobe,4)}/4일", fg=C["dim"])
        hdr_mi.configure(text=f"미야기 D+{sum(1 for e in data['days'].values() if e['checks'].get('miyagi'))}/30")
        # 벤치
        src = bench_source()
        scores = data["days"].get(src, {}).get("best", {}) if src else {}
        e, n = totalE(scores); rn, rc = rank_of(e)
        hdr_e.configure(text=f"{e} {rn}" if e is not None else "", fg=rc)
        ben_total.configure(text=str(e) if e is not None else "—", fg=rc)
        rank_pill(ben_rankcv, rn if e is not None else "", rc)
        ben_src.configure(text=f"{src} · {n}/9" if src else "")
        for sub_ in SUBS:
            se_lbl, cells = ben_rows[sub_[0]]
            se = subE(sub_, scores)
            se_lbl.configure(text=str(se) if se is not None else "—", fg=rank_of(se)[1])
            for k, th, sc_lbl, cvth in cells:
                x = scores.get(k)
                sc_lbl.configure(text=str(x) if x is not None else "—",
                                 fg=rank_of(scenE(x, th))[1] if x is not None else C["dim"])
                draw_thcells(cvth, th, x)
        draw_idx(cv_idx, s)
        draw_bench_chart(cv_ben, bench_days(data))
        for k, (cv, pbl) in spark_cvs.items(): draw_spark(k, cv, pbl)
        tg1.sync(); tg2.sync()
        for st_ in steppers: st_.sync()
        seg.draw()

    def on_resize(_=None):
        root.after_idle(refresh)
    for cv in [cv_idx, cv_ben] + [c for c, _ in spark_cvs.values()]:
        cv.bind("<Configure>", on_resize)

    def tick():
        nk = date.today().isoformat()
        if nk != today_key[0]: today_key[0] = nk
        sd = data.get("stats_dir")
        if sd and Path(sd).is_dir():
            events, changed = apply_scan(data, scan_day(Path(sd), date.today()), today_key[0])
            if SCAN_INFO["plays"] == 0:
                scan_lbl.configure(fg=C["gold"],
                    text="오늘 감지 0판 — 플레이 중인데도 0이면 코박스 토글이 FREEPLAY입니다. CHALLENGE로 바꾸세요.")
            else:
                extra = f" · 인식실패 {SCAN_INFO['miss']}" if SCAN_INFO["miss"] else ""
                scan_lbl.configure(fg=C["dim"],
                    text=f"오늘 감지 {SCAN_INFO['plays']}판 · 마지막 확인 {SCAN_INFO['t']}{extra}")
            if events:
                k, sc_, diff = events[-1]
                show_toast(f"🏆 신기록 — {SCEN[k][0].replace('VT ','').replace(' Novice S5','')}  {sc_}  (+{diff})")
            if changed or events:
                save_data(data); refresh()
        root.after(2000, tick)

    if not data.get("stats_dir"):
        for c_ in DEFAULT_STATS:
            if Path(c_).is_dir():
                data["stats_dir"] = c_; break
        save_data(data)
    sync_stats_lbl()
    install_playlists()

    root.deiconify(); root.update_idletasks(); win_dark()
    show("today")
    root.after(300, tick)
    root.after(450, refresh)
    root.protocol("WM_DELETE_WINDOW", lambda: (save_data(data), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        e, n = totalE(SEED)
        assert (e, n) == (339, 9), (e, n)
        print("selftest OK: seed energy =", e, "Silver")
        sys.exit(0)
    main()
