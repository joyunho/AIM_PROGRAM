#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
에임 데스크 v2.2 — 코박스 자동 기록 + 성장 시각화 + 루틴 자동 진행
· stats 폴더 2초 감시: 판 수/점수/신기록 실시간 자동
· 프로브(첫 판) 지수, 볼테익 동일 수식 에너지·랭크
· 루틴 실행 시 오늘 칠 시나리오 전체 순서창 (진행 자동 체크)
· 자동 진행: 코박스 공식 딥링크(steam://run/824270/?action=jump-to-scenario)로 한 판이 끝나면 다음 판을 자동 전송
· 기록 보호: 원자적 저장 · 손상 파일 백업 · 스캔 실패 시 기록 보존 · 오류 로그
· 실행: python aim_desk.py  (파이썬 3.9+, 추가 설치 없음)
"""
from __future__ import annotations
import json, os, re, sys, traceback
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
def sname(k):
    """화면용 짧은 이름: 'VT Pasu Novice S5' -> 'Pasu'"""
    return SCEN[k][0].replace("VT ", "").replace(" Novice S5", "")
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

def _data_dir():
    """기본은 exe 옆. 쓰기 불가(Program Files 등)이거나 임시폴더 실행(zip 안에서 더블클릭)이면
    %LOCALAPPDATA%\\AimDesk 로 — 이때 exe 옆에 기존 기록이 있으면 1회 복사해 온다."""
    base = _base_dir()
    import tempfile
    in_tmp = str(base).lower().startswith(str(Path(tempfile.gettempdir())).lower())
    writable = True
    try:
        probe = base / ".aimdesk_write_test"
        probe.write_text("x"); probe.unlink()
    except OSError:
        writable = False
    if writable and not in_tmp:
        return base
    appdir = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "AimDesk"
    try:
        appdir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return base
    old, new = base / "aim_desk_data.json", appdir / "aim_desk_data.json"
    if old.exists() and not new.exists():
        try: new.write_bytes(old.read_bytes())
        except OSError: pass
    return appdir

DATA_FILE = _data_dir() / "aim_desk_data.json"
BACKUP_FILE = DATA_FILE.with_name("aim_desk_data.backup.json")
LOG_FILE = DATA_FILE.with_name("aim_desk.log")
LOAD_ERROR: list[str] = []      # 시작 시 사용자에게 보여줄 경고
SAVE_ERROR = [None]             # 마지막 저장 실패 사유 (None이면 정상)
DOWK = ["월","화","수","목","금","토","일"]

def log_exc(where: str):
    """창 모드 exe에선 print/traceback이 아무 데도 안 가므로 파일에 남긴다"""
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] {where}\n")
            traceback.print_exc(file=f)
    except OSError:
        pass

# ══════════════════ 데이터 ══════════════════
def load_data() -> dict:
    d = {"stats_dir": None, "pb": {}, "days": {}, "seeded": False}
    if DATA_FILE.exists():
        try:
            raw = DATA_FILE.read_bytes()
            d.update(json.loads(raw.decode("utf-8-sig")))
            try: BACKUP_FILE.write_bytes(raw)     # 실행마다 정상본 1부 보관
            except OSError: pass
        except Exception:
            # 손상된 파일은 절대 덮어쓰지 않는다 — 이름을 바꿔 보관하고 사용자에게 알림
            log_exc("load_data")
            bad = DATA_FILE.with_name(f"aim_desk_data.corrupt-{datetime.now():%Y%m%d-%H%M%S}.json")
            try:
                DATA_FILE.replace(bad)
                LOAD_ERROR.append(f"기록 파일이 손상되어 읽지 못했습니다.\n원본은 {bad.name} 으로 보관했고, "
                                  f"직전 정상본은 {BACKUP_FILE.name} 입니다.\n"
                                  f"복구하려면 앱을 닫고 정상본을 {DATA_FILE.name} 으로 복사하세요.")
            except OSError:
                LOAD_ERROR.append("기록 파일이 손상되었고 백업 이름 변경도 실패했습니다. 파일을 직접 확인하세요.")
            d = {"stats_dir": None, "pb": {}, "days": {}, "seeded": False}
    for day in d["days"].values():          # 옛 버전/수정된 파일의 빠진 키 보정
        for k, v in blank_day().items():
            if k not in day: day[k] = v
            elif isinstance(v, dict):
                for kk, vv in v.items(): day[k].setdefault(kk, vv)
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
    """임시 파일에 다 쓴 뒤 교체 — 쓰는 도중 꺼져도 잘린 파일이 남지 않는다"""
    tmp = DATA_FILE.with_name(DATA_FILE.name + ".tmp")
    try:
        tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, DATA_FILE)
        SAVE_ERROR[0] = None
    except Exception as e:
        SAVE_ERROR[0] = f"{type(e).__name__}: {e}"
        log_exc("save_data")

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

SCAN_INFO = {"plays": 0, "miss": 0, "other": 0, "t": ""}
_SCORE_CACHE: dict = {}   # 파일명 -> ((mtime, size), score) — 2초마다 같은 파일을 다시 읽지 않기 위함

def read_score_cached(fp: Path):
    try: st = fp.stat()
    except OSError: return None
    sig = (st.st_mtime_ns, st.st_size)
    hit = _SCORE_CACHE.get(fp.name)
    if hit and hit[0] == sig: return hit[1]
    s = read_score(fp)
    _SCORE_CACHE[fp.name] = (sig, s)
    return s

def scan_day(stats: Path, day: date):
    """해당 날짜의 (key, 'HH.MM.SS', score) 목록 + 진단 집계. 폴더를 못 읽으면 None(그 턴은 건너뜀)"""
    tag = day.strftime("%Y.%m.%d"); out = []; miss = 0; other = 0
    try: it = list(stats.iterdir())
    except OSError: return None
    for fp in it:
        m = FNAME_RE.match(fp.name)
        if not m or m.group("d") != tag: continue
        key = NAME2KEY.get(m.group("scen"))
        if key is None:
            other += 1; continue          # 루틴 밖 시나리오 — 인식 실패가 아님
        sc = read_score_cached(fp)
        if sc is None:
            miss += 1; continue
        out.append((key, m.group("t"), round(sc)))
    SCAN_INFO.update(plays=len(out), miss=miss, other=other,
                     t=datetime.now().strftime("%H:%M:%S"))
    return out

def apply_scan(data: dict, plays, dkey: str):
    """오늘 판들을 반영. (신기록 이벤트 목록, 변경 여부) 반환.
    기존 기록은 절대 줄이지 않는다 — stats 폴더를 정리했거나 스캔이 비어도 오늘 기록이 남는다."""
    day = data["days"].setdefault(dkey, blank_day())
    first, best, count = {}, {}, {}
    for key, t, s in sorted(plays, key=lambda x: x[1]):
        count[key] = count.get(key, 0) + 1
        if key not in first: first[key] = s
        if key not in best or s > best[key]: best[key] = s
    for k, v in day["first"].items(): first[k] = v      # 첫 판은 먼저 기록된 값이 진짜 첫 판
    for k, v in day["best"].items():
        if k not in best or v > best[k]: best[k] = v
    for k, v in day["count"].items():
        if count.get(k, 0) < v: count[k] = v
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
        if not d.is_dir():
            try: d.mkdir(parents=True)      # 로컬 플레이리스트를 한 번도 안 만든 설치본
            except OSError: return 0, d
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

KOVAAKS_EXE = "FPSAimTrainer-Win64-Shipping.exe"

def scenario_uri(name: str) -> str:
    """코박스 공식 딥링크(3.0.0+, 공백은 %20): 게임이 꺼져 있으면 켜서, 켜져 있으면 그 자리에서 해당 시나리오를 바로 시작"""
    return "steam://run/824270/?action=jump-to-scenario;name=" + name.replace(" ", "%20")

def launch_scenario(key: str) -> bool:
    return open_uri(scenario_uri(SCEN[key][0]))

def kovaaks_running() -> bool:
    """코박스 프로세스가 떠 있는지 (Windows tasklist). 판단 불가면 True — 자동 진행을 괜히 막지 않기 위해"""
    if sys.platform != "win32": return True
    try:
        import subprocess
        r = subprocess.run(["tasklist", "/FI", f"IMAGENAME eq {KOVAAKS_EXE}", "/NH"],
                           capture_output=True, timeout=5,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return KOVAAKS_EXE.lower().encode() in r.stdout.lower()
    except Exception:
        return True

ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAACkUlEQVR4nO1bwWrDMAxNxo6Dwc6D0vYy9v/fMnppS2HnQCD37WQwiSVL1pPTpn6nrY4dvWfZsmyn6xqeG31Jpbf3jz+0IShM46DiJH74nklTkIghEsCL/OV6O4e/D/vd0eMdORFeucJH7PU5AgdKiJdcxa2A4pMUYGvkA1K8SA94FiwE2GrvB8z59VyhB+KZn4JXRIgRJsUqAkhIU/AOj24CWEhTQIqxEKAW+ZgEtRCS1rdiGoeeXQhpQRmuNZoTI/yPEgIWBlPkD/vd0Woo1QZqiEEEmBuDID5Hqk2ECOY5IEXealStd07j0JsEKDUEMckhRDAJoDWgxF21bWpFmMahh8wBHuQl9RDDrcgDpBsZJWHRWkcjSpEHSHuzNCxaw57W20xDgCKDCIuasGcZCu77AYiFEMqWFFQCSMaax0anJE+Q5hJzQD3AIwP0fg80GYqR6/3T9+fit6+fX7Y9D4HFHoB07RR57ncpSoaBSzbICZQjyZWXjnMOVXeFpT1s9QQNFnOARNk1MkCpLZKy2N52LrC2AWtjMQRqLnAQ4JbLEjuregAX50ueQwAmgDRE5chx5R5eKBYAGYMpktaeLxHIbSl8ud7OnBFasl55BnQOqDU5It+jEsAzLeXgmYa7RwGrCN4ptkkA6RbV5Xo7a4mk6ki34DRQCyB1L2pjM2cs9YzlvRwgByNe5wLatlc7GPE6wPAUNqCdDYZ/2umw4YoMwhNq9nyA2+FoSdjLQRMWNXDJBgMQQljDYg7QZCgYRV1sip/hUOuWWNe1e4Ltpmi7KzwvqHlbfK2N1vjrkUUU0H519WiY83v6c4GkAFv1ghQv0gO2JgLFh10IhUqP/BlNriPbl6MlDd+zGFsbuu74B4fxI3bL2IpFAAAAAElFTkSuQmCC"
# ══════════════════ GUI (v2 — 커스텀 위젯) ══════════════════
C = {"bg":"#0B0E11","card":"#14191F","card2":"#1D242C","c3":"#242C35","line":"#28313B",
     "txt":"#EDF1F5","sub":"#8CA0B3","dim":"#5C6C7C",
     "val":"#E8453A","ow":"#3B87F7","ok":"#4ED490","gold":"#F5C24B"}
RANKC = ["#98A2AC", "#E08A3C", "#C9D6E2", "#F5C24B"]

def single_instance_lock():
    """두 개가 동시에 떠서 서로 기록을 덮어쓰는 것 방지. 소켓 하나를 점유(참조를 유지해야 함)"""
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", 47653)); s.listen(1)
        return s
    except OSError:
        return None

def main():
    import tkinter as tk
    import tkinter.font as tkfont
    from tkinter import filedialog, messagebox

    # 창 모드 exe에서도 예외가 사라지지 않도록 파일 로그로
    def _hook(t, v, tb):
        try:
            with LOG_FILE.open("a", encoding="utf-8") as f:
                f.write(f"\n[{datetime.now():%Y-%m-%d %H:%M:%S}] uncaught\n")
                traceback.print_exception(t, v, tb, file=f)
        except OSError: pass
    sys.excepthook = _hook

    lock = single_instance_lock()
    if lock is None:
        r0 = tk.Tk(); r0.withdraw()
        messagebox.showwarning("에임 데스크", "에임 데스크가 이미 실행 중입니다.\n두 개를 동시에 켜면 기록이 서로 덮어써집니다.")
        r0.destroy(); return

    data = load_data()
    root = tk.Tk(); root.withdraw()
    root._aimdesk_lock = lock
    root.report_callback_exception = lambda t, v, tb: _hook(t, v, tb)
    root.title("에임 데스크"); root.configure(bg=C["bg"])
    root.geometry("1060x760"); root.minsize(960, 660)
    try: root.iconphoto(True, tk.PhotoImage(data=ICON_B64))
    except Exception: pass

    FAM = "Malgun Gothic" if "Malgun Gothic" in tkfont.families() else "TkDefaultFont"
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

    # ══ 헤더 ══  (날짜·요일 칩은 build_day_ui()가 채운다 — 자정을 넘기면 다시 그림)
    head = tk.Frame(root, bg=C["bg"]); head.pack(fill="x", padx=18, pady=(14, 2))
    lf = tk.Frame(head, bg=C["bg"]); lf.pack(side="left")
    tk.Label(lf, text="에임 데스크", font=(FAM, 16, "bold"), bg=C["bg"], fg=C["txt"]).pack(anchor="w")
    sub = tk.Frame(lf, bg=C["bg"]); sub.pack(anchor="w")
    date_lbl = tk.Label(sub, text="", font=FS, bg=C["bg"], fg=C["sub"]); date_lbl.pack(side="left")
    daych = tk.Canvas(sub, width=70, height=18, bg=C["bg"], highlightthickness=0); daych.pack(side="left", padx=8)

    rf = tk.Frame(head, bg=C["bg"]); rf.pack(side="right")
    hdr_e = tk.Label(rf, text="", font=(MONO, 15, "bold"), bg=C["bg"], fg=C["gold"])
    hdr_e.pack(side="right")
    hdr_idx = tk.Label(rf, text="", font=FN, bg=C["bg"], fg=C["txt"])
    hdr_idx.pack(side="right", padx=(0, 16))
    hdr_mi = tk.Label(rf, text="", font=FNS, bg=C["bg"], fg=C["sub"])
    hdr_mi.pack(side="right", padx=(0, 16))

    # PB 토스트
    toast = tk.Frame(root, bg=C["bg"]); toast_in = tk.Frame(toast, bg="#241E0E",
        highlightbackground=C["gold"], highlightthickness=1, padx=12, pady=6)
    toast_lbl = tk.Label(toast_in, text="", font=FB, bg="#241E0E", fg=C["gold"])
    toast_lbl.pack(side="left"); toast_in.pack(fill="x")
    toast_timer = [None]
    def show_toast(msg):
        toast_lbl.configure(text=msg)
        toast.pack(fill="x", padx=18, pady=(6, 0), after=head)
        if toast_timer[0]: root.after_cancel(toast_timer[0])   # 이전 토스트의 타이머가 새 토스트를 지우지 않도록
        toast_timer[0] = root.after(8000, toast.pack_forget)

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

    # 날짜에 묶인 UI 상태 — 자정을 넘기면 build_day_ui()가 헤더와 루틴 카드를 다시 그린다
    day_state = {"dt": "v", "pl": None}
    routine_rows = []

    # ── 순서창 + 자동 진행 ──
    #   오늘 칠 시나리오를 순서대로 나열하고, 코박스 딥링크로 한 판씩 전송한다.
    #   판이 끝나 stats CSV가 생기면(2초 감시) 대기 시간 뒤 다음 시나리오 딥링크를 보낸다 → 결과창에서 NEXT를 누를 필요가 없다.
    seq_win = {"win": None, "rows": [], "prog": None, "auto_lbl": None, "auto_btn": None,
               "seq": [], "base": {}, "skipped": {}}
    auto = {"on": False, "fired": None, "due": None}     # fired/due: 전송했거나 전송 예약된 순서창 인덱스
    def auto_delay(): return int(data.get("auto_delay", 4))

    def sequence_for(plname):
        """플레이리스트(또는 토요일 벤치 18개)를 실제 치는 순서대로 펼친 key 목록"""
        if plname:
            return [k for k, n in dict(PLAYLISTS)[plname] for _ in range(n)]
        if day_state["dt"] == "b":
            return [k for s in SUBS for k, _ in s[3]]
        return []

    def seq_status():
        """각 줄의 완료 여부 목록과 '다음에 칠' 인덱스(None이면 전부 완료).
        완료 = (오늘 판 수 − 처음부터 눌렀을 때의 기준 판 수 + 건너뛴 수) ≥ 그 시나리오의 n번째 줄"""
        day = data["days"].get(today_key[0], blank_day())
        seen, done, nxt = {}, [], None
        for i, k in enumerate(seq_win["seq"]):
            seen[k] = seen.get(k, 0) + 1
            played = day["count"].get(k, 0) - seq_win["base"].get(k, 0) + seq_win["skipped"].get(k, 0)
            d_ = played >= seen[k]
            done.append(d_)
            if not d_ and nxt is None: nxt = i
        return done, nxt

    def seq_alive():
        w = seq_win["win"]
        return w is not None and w.winfo_exists()

    def open_sequence(plname):
        seq = sequence_for(plname)
        if not seq: return
        if seq_alive(): seq_win["win"].destroy()
        w = tk.Toplevel(root)
        seq_win.update(win=w, rows=[], seq=seq, base={}, skipped={})
        title = plname or "볼테익 벤치마크 18"
        w.title("오늘 순서 — " + title); w.configure(bg=C["bg"])
        w.attributes("-topmost", True); w.resizable(False, False)
        w.protocol("WM_DELETE_WINDOW", lambda: (stop_auto(), w.destroy()))
        hd = tk.Frame(w, bg=C["bg"]); hd.pack(fill="x", padx=12, pady=(10, 2))
        tk.Label(hd, text=title, font=FB, bg=C["bg"], fg=C["txt"]).pack(side="left")
        seq_win["prog"] = tk.Label(hd, text="", font=FNS, bg=C["bg"], fg=C["sub"])
        seq_win["prog"].pack(side="right")
        seq_win["auto_lbl"] = tk.Label(w, text="", font=FS, bg=C["bg"], fg=C["dim"],
                                       wraplength=300, justify="left")
        seq_win["auto_lbl"].pack(anchor="w", padx=12)
        box = tk.Frame(w, bg=C["card"], padx=10, pady=8,
                       highlightbackground=C["line"], highlightthickness=1)
        box.pack(fill="both", expand=True, padx=12, pady=(6, 8))
        for i, k in enumerate(seq, 1):
            row = tk.Frame(box, bg=C["card"]); row.pack(fill="x", pady=1)
            num = tk.Label(row, text=f"{i:02d}", font=FNS, width=3, anchor="e", bg=C["card"], fg=C["dim"])
            num.pack(side="left")
            tk.Frame(row, bg=C["val"] if SCEN[k][1] == "v" else C["ow"], width=3, height=14).pack(side="left", padx=(6, 8))
            nm = tk.Label(row, text=sname(k), font=F, width=16, anchor="w", bg=C["card"], fg=C["sub"])
            nm.pack(side="left")
            st = tk.Label(row, text="", font=FN, width=2, bg=C["card"], fg=C["dim"])
            st.pack(side="right")
            seq_win["rows"].append((k, num, nm, st))
        # 조작 줄: 자동 진행 토글 · 다음 판(건너뛰기) · 다시 보내기 · 처음부터 · 판 사이 대기
        ctl = tk.Frame(w, bg=C["bg"]); ctl.pack(fill="x", padx=12, pady=(0, 6))
        seq_win["auto_btn"] = Toggle(ctl, "자동 진행", lambda: auto["on"], set_auto)
        seq_win["auto_btn"].pack(side="left")
        RBtn(ctl, "다음 판 ▶", skip_current, padx=10, pady=5).pack(side="left", padx=(6, 0))
        RBtn(ctl, "다시 보내기", resend_current, padx=10, pady=5).pack(side="left", padx=(6, 0))
        RBtn(ctl, "처음부터", restart_sequence, padx=10, pady=5).pack(side="left", padx=(6, 0))
        dl = tk.Frame(w, bg=C["bg"]); dl.pack(fill="x", padx=12, pady=(0, 10))
        tk.Label(dl, text="판 끝난 뒤 다음 판까지 대기(초)", font=FS, bg=C["bg"], fg=C["sub"]).pack(side="left")
        Stepper(dl, auto_delay,
                lambda v: (data.__setitem__("auto_delay", max(1, min(30, v))), save_data(data), update_sequence())
                ).pack(side="left", padx=(8, 0))
        # 본창 오른쪽에 붙이되 화면 밖으로 나가면 본창 위에 겹쳐서
        root.update_idletasks(); w.update_idletasks()
        x = root.winfo_x() + root.winfo_width() + 8
        if x + w.winfo_reqwidth() > root.winfo_screenwidth(): x = root.winfo_x() + 40
        w.geometry(f"+{x}+{root.winfo_y()}")
        update_sequence()

    def update_sequence():
        if not seq_alive(): return
        done, nxt = seq_status()
        for i, (k, num, nm, st) in enumerate(seq_win["rows"]):
            if done[i]:
                st.configure(text="✓", fg=C["ok"]); nm.configure(fg=C["dim"]); num.configure(fg=C["dim"])
            elif i == nxt:
                st.configure(text="▶", fg=C["gold"]); nm.configure(fg=C["txt"]); num.configure(fg=C["gold"])
            else:
                st.configure(text=""); nm.configure(fg=C["sub"]); num.configure(fg=C["dim"])
        total, done_n = len(done), sum(done)
        seq_win["prog"].configure(text=f"{done_n}/{total}" + ("  완료 ✓" if done_n >= total else ""),
                                  fg=C["ok"] if done_n >= total else C["sub"])
        if nxt is None:
            msg = "오늘 순서 전부 완료 🎉  ·  한 번 더 돌리려면 '처음부터'"
        elif auto["on"]:
            msg = (f"자동 진행 중 · 판이 끝나면 {auto_delay()}초 뒤 다음 판을 코박스로 보냅니다"
                   if auto["fired"] == nxt else f"{sname(seq_win['seq'][nxt])} 전송 대기…")
        else:
            msg = "자동 진행 꺼짐 — 코박스에서 직접 고르거나 '다음 판 ▶'로 보내세요"
        seq_win["auto_lbl"].configure(text=msg, fg=C["ok"] if (auto["on"] and nxt is not None) else C["dim"])
        if seq_win["auto_btn"] is not None and seq_win["auto_btn"].winfo_exists():
            seq_win["auto_btn"].sync()

    # ── 자동 진행 엔진 ──
    def fire(idx):
        """seq[idx] 시나리오 딥링크 전송 (코박스가 꺼져 있으면 스팀이 켜서 시작한다)"""
        seq = seq_win["seq"]
        if idx is None or idx >= len(seq): return False
        ok = launch_scenario(seq[idx])
        auto["fired"] = idx; auto["due"] = None
        if not ok: show_toast("스팀 실행 실패 — Steam이 켜져 있는지 확인하세요")
        update_sequence()
        return ok

    def fire_due(idx):
        auto["due"] = None
        if not auto["on"] or not seq_alive(): return
        _, nxt = seq_status()
        if nxt != idx: return                          # 그 사이 상황이 바뀜(다른 판을 쳤거나 건너뜀)
        if auto["fired"] is not None and not kovaaks_running():
            stop_auto("코박스가 꺼져 있어 자동 진행을 멈췄습니다"); return
        fire(idx)

    def auto_step():
        """스캔 후 호출: 다음 칠 판이 아직 전송 전이면 대기 시간 뒤 전송을 예약"""
        if not auto["on"]: return
        if not seq_alive(): auto["on"] = False; return
        _, nxt = seq_status()
        if nxt is None:
            stop_auto("오늘 순서 전부 완료 🎉 수고했어요"); return
        if auto["fired"] == nxt or auto["due"] == nxt: return
        auto["due"] = nxt
        root.after(auto_delay() * 1000, lambda: fire_due(nxt))

    def stop_auto(msg=None):
        auto["on"] = False; auto["due"] = None
        if msg: show_toast(msg)
        update_sequence()

    def set_auto(v):
        auto["on"] = bool(v)
        if auto["on"]:
            _, nxt = seq_status()
            if nxt is not None and auto["fired"] != nxt: fire(nxt)    # 켜는 즉시 현재 차례를 보낸다
        update_sequence()

    def skip_current():
        """지금 차례를 건너뛰고 다음 판을 바로 보낸다"""
        _, nxt = seq_status()
        if nxt is None: return
        k = seq_win["seq"][nxt]
        seq_win["skipped"][k] = seq_win["skipped"].get(k, 0) + 1
        _, nxt2 = seq_status()
        if nxt2 is None: stop_auto("오늘 순서 전부 완료 🎉"); return
        fire(nxt2)

    def resend_current():
        _, nxt = seq_status()
        if nxt is not None: fire(nxt)

    def restart_sequence():
        """지금까지 친 판은 그대로 두고 순서를 1번부터 다시 (오늘 두 번째 세션용)"""
        day = data["days"].get(today_key[0], blank_day())
        seq_win["base"] = dict(day["count"]); seq_win["skipped"] = {}
        auto["fired"] = None; auto["due"] = None
        update_sequence()
        if auto["on"]: fire(0)

    def run_playlist(plname):
        sd = data.get("stats_dir")
        if sd: ensure_playlists(sd)                    # 수동으로 돌릴 때를 위해 로컬 플레이리스트도 계속 설치
        open_sequence(plname)
        if not seq_win["seq"] or not seq_alive():
            if not launch_kovaaks(): show_toast("스팀 실행 실패 — Steam이 켜져 있는지 확인하고 코박스를 직접 실행하세요")
            return
        auto.update(on=True, fired=None, due=None)
        _, nxt = seq_status()
        if nxt is None: restart_sequence()             # 오늘 이미 다 쳤으면 1번부터 한 번 더
        else: fire(nxt)
        show_toast(f"▶ 자동 진행 시작 — 코박스가 꺼져 있으면 켜지고, 한 판이 끝날 때마다 {auto_delay()}초 뒤 다음 판이 자동으로 뜹니다"
                   "  ·  좌하단 토글이 FREEPLAY면 CHALLENGE로! (프리플레이는 기록이 안 남습니다)")

    def add_section(title):
        f = tk.Frame(left, bg=C["card"]); f.pack(fill="x", pady=(10, 3))
        tk.Label(f, text=title, font=FCAP, bg=C["card"], fg=C["gold"]).pack(side="left")
        tk.Frame(f, bg=C["line"], height=1).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=1)

    def add_row(kind, key, target):
        row = tk.Frame(left, bg=C["card"]); row.pack(fill="x", pady=2)
        grp = SCEN[key][1]
        gc = C["val"] if grp == "v" else C["ow"]
        tk.Frame(row, bg=gc, width=3, height=16).pack(side="left", padx=(2, 9))
        tk.Label(row, text=sname(key), font=F, width=13, anchor="w", bg=C["card"], fg=C["txt"]).pack(side="left")
        bar = tk.Canvas(row, height=8, bg=C["card"], highlightthickness=0)
        bar.pack(side="left", fill="x", expand=True, padx=(4, 10))
        cl = tk.Label(row, text="", font=FNS, width=5, anchor="e", bg=C["card"], fg=C["sub"])
        cl.pack(side="left")
        sl = tk.Label(row, text="", font=FNS, width=9, anchor="e", bg=C["card"], fg=C["dim"])
        sl.pack(side="left")
        routine_rows.append((kind, key, target, bar, cl, sl, gc))

    def build_day_ui():
        """헤더의 날짜·요일 칩과 좌측 루틴 카드를 '오늘' 기준으로 (다시) 만든다"""
        d = date.today()
        dt = ["v","v","v","v","w","b","r"][d.weekday()]
        day_state["dt"] = dt
        day_state["pl"] = {"v": "AIMDESK Day", "w": "AIMDESK Friday"}.get(dt)
        dt_name = {"v":"발로 데이","w":"약점 데이","b":"벤치마크","r":"휴식"}[dt]
        dt_col  = {"v":C["val"],"w":"#8A94A2","b":C["gold"],"r":C["dim"]}[dt]
        date_lbl.configure(text=f"{d.month}월 {d.day}일 {DOWK[d.weekday()]}")
        daych.delete("all")
        rrect(daych, 0, 1, 68, 17, 8, fill=dt_col, outline="")
        daych.create_text(34, 9, text=dt_name, fill="#0B0E11", font=(FAM, 8, "bold"))

        for w_ in left.winfo_children(): w_.destroy()
        routine_rows.clear()
        lh = tk.Frame(left, bg=C["card"]); lh.pack(fill="x")
        lt = tk.Frame(lh, bg=C["card"]); lt.pack(side="left")
        tk.Label(lt, text="오늘 루틴", font=FH, bg=C["card"], fg=C["txt"]).pack(anchor="w")
        tk.Label(lt, text="실행하면 코박스에 시나리오가 순서대로 자동 전송됩니다 · 한 판이 끝나면 다음 판이 저절로 뜸 · 판 수 자동 집계",
                 font=FS, bg=C["card"], fg=C["dim"], wraplength=300, justify="left").pack(anchor="w", pady=(0, 6))
        pl = day_state["pl"]
        if pl:
            RBtn(lh, "▶ 오늘 루틴 실행", lambda: run_playlist(pl),
                 bg="#2A1512", fg=C["val"], padx=14, pady=8).pack(side="right", padx=(8, 0))
            RBtn(lh, "프로브만", lambda: run_playlist("AIMDESK Probe"),
                 padx=12, pady=8).pack(side="right", padx=(8, 0))
            RBtn(lh, "순서 보기", lambda: open_sequence(pl), padx=12, pady=8).pack(side="right")
        elif dt == "b":
            RBtn(lh, "▶ 코박스 실행", lambda: run_playlist(None),
                 bg="#2A1512", fg=C["val"], padx=14, pady=8).pack(side="right", padx=(8, 0))
            RBtn(lh, "순서 보기", lambda: open_sequence(None), padx=12, pady=8).pack(side="right", padx=(8, 0))
            RBtn(lh, "볼테익 페이지", lambda: open_uri("https://app.voltaic.gg/benchmarks"),
                 padx=12, pady=8).pack(side="right")

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
            tk.Label(left, text="▶ 코박스 실행을 누르면 18개 시나리오가 순서대로 자동 진행됩니다 — 점수는 자동 수집, 벤치 탭에서 실시간으로 차오릅니다.",
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
    sleep_var = tk.StringVar()
    ent = tk.Entry(rowc, textvariable=sleep_var, width=5, font=FN, bg=C["card2"], fg=C["txt"],
                   insertbackground=C["txt"], bd=0, justify="center")
    ent.pack(side="left", padx=(8, 0), ipady=4)
    def sync_sleep_entry():
        v = dget()["cond"]["sleep"]
        try: txt = "" if v is None else f"{float(v):g}"
        except (TypeError, ValueError): txt = str(v)
        sleep_var.set(txt); ent.configure(fg=C["txt"])
    def commit_sleep(*_):
        # 키 입력마다가 아니라 엔터/포커스 이동 때 저장 — "10"을 치는 중에 1이 저장되지 않게
        v = sleep_var.get().strip().replace(",", ".")
        try:
            dget()["cond"]["sleep"] = float(v) if v else None
            save_data(data); ent.configure(fg=C["txt"])
        except ValueError:
            ent.configure(fg=C["val"])          # 잘못된 값은 빨갛게 표시, 저장 안 됨
    ent.bind("<Return>", commit_sleep); ent.bind("<FocusOut>", commit_sleep)
    sync_sleep_entry()
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
        p = data["stats_dir"] if ok else ""
        if len(p) > 44: p = "…" + p[-43:]          # 공백 없는 긴 경로가 카드 밖으로 넘치지 않게 꼬리만
        stats_lbl.configure(text=(p if ok else "자동 탐지 실패 — 폴더를 선택해 주세요"),
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
        tk.Label(top, text=sname(k), font=FB,
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
            tk.Label(r1, text=sname(k), font=FS,
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
        top = max([520] + [e_ + 60 for _, e_ in bd])   # 골드 위로 외삽돼도 점이 차트 밖으로 나가지 않게
        def Y(v): return T + (H-T-B) * (1 - v/top)
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
        for kind, key, target, bar, cl, sl, gc in routine_rows:
            c = day["count"].get(key, 0)
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
        mi = sum(1 for e in data["days"].values() if e["checks"].get("miyagi"))
        hdr_mi.configure(text=f"미야기 D+{min(mi, 30)}/30" + (" ✓" if mi >= 30 else ""))
        # 헤더 에너지는 PB 기준(항상 9/9) — 오늘 친 몇 판의 부분 조화평균으로 흔들리지 않게
        e_pb, _ = totalE(data["pb"]); rn_pb, rc_pb = rank_of(e_pb)
        hdr_e.configure(text=f"PB {e_pb} {rn_pb}" if e_pb is not None else "", fg=rc_pb)
        # 벤치 탭은 오늘(없으면 마지막 기록일)의 베스트 — 토요일 풀런이 실시간으로 차오르는 용도, n/9 표기
        src = bench_source()
        scores = data["days"].get(src, {}).get("best", {}) if src else {}
        e, n = totalE(scores); rn, rc = rank_of(e)
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
        update_sequence()

    def on_resize(_=None):
        root.after_idle(refresh)
    for cv in [cv_idx, cv_ben] + [c for c, _ in spark_cvs.values()]:
        cv.bind("<Configure>", on_resize)

    def on_day_change(nk):
        """자정 통과: 데이터 키·스캔 캐시·날짜 UI·입력칸을 모두 오늘로 (켜 둔 채 밤을 넘겨도 어제 루틴이 남지 않게)"""
        today_key[0] = nk
        _SCORE_CACHE.clear()
        auto.update(on=False, fired=None, due=None)
        w = seq_win["win"]
        if w is not None and w.winfo_exists(): w.destroy()
        build_day_ui()
        sync_sleep_entry()
        refresh()

    def tick():
        try:
            d_now = date.today(); nk = d_now.isoformat()   # 한 번만 읽는다 — 자정 경계에서 어제 키에 오늘 스캔이 섞이지 않게
            if nk != today_key[0]: on_day_change(nk)
            sd = data.get("stats_dir")
            if sd and Path(sd).is_dir():
                plays = scan_day(Path(sd), d_now)
                if plays is None:
                    scan_lbl.configure(fg=C["val"],
                        text="stats 폴더를 읽지 못했습니다 — 기록은 보존됩니다. 일시적이면 자동 복구")
                else:
                    events, changed = apply_scan(data, plays, nk)
                    if SCAN_INFO["plays"] == 0:
                        scan_lbl.configure(fg=C["gold"],
                            text="오늘 감지 0판 — 플레이 중인데도 0이면 코박스 토글이 FREEPLAY입니다. CHALLENGE로 바꾸세요.")
                    else:
                        extra = ((f" · 루틴 외 {SCAN_INFO['other']}판" if SCAN_INFO["other"] else "")
                                 + (f" · 점수 인식실패 {SCAN_INFO['miss']}" if SCAN_INFO["miss"] else ""))
                        scan_lbl.configure(fg=C["dim"],
                            text=f"오늘 감지 {SCAN_INFO['plays']}판 · 마지막 확인 {SCAN_INFO['t']}{extra}")
                    if events:
                        k, sc_, diff = events[-1]
                        show_toast(f"🏆 신기록 — {sname(k)}  {sc_}  (+{diff})")
                    if changed or events:
                        save_data(data); refresh()
                    auto_step()
            if SAVE_ERROR[0]:
                scan_lbl.configure(fg=C["val"],
                    text=f"⚠ 저장 실패 — 기록이 저장되지 않고 있습니다 ({SAVE_ERROR[0][:70]})")
        except Exception:
            log_exc("tick")
        finally:
            root.after(2000, tick)          # 무슨 일이 있어도 감시 루프는 계속 돈다

    if not data.get("stats_dir"):
        for c_ in DEFAULT_STATS:
            if Path(c_).is_dir():
                data["stats_dir"] = c_; break
        save_data(data)
    sync_stats_lbl()
    install_playlists()
    build_day_ui()

    root.deiconify(); root.update_idletasks(); win_dark()
    show("today")
    if LOAD_ERROR:
        root.after(500, lambda: messagebox.showwarning("에임 데스크 — 기록 파일", "\n\n".join(LOAD_ERROR)))
    root.after(300, tick)
    root.after(450, refresh)
    def on_close():
        save_data(data)
        if SAVE_ERROR[0] and not messagebox.askyesno(
                "에임 데스크", f"기록 저장에 실패했습니다:\n{SAVE_ERROR[0]}\n\n그래도 닫을까요? (아니오 = 열어 둠)"):
            return
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        e, n = totalE(SEED)
        assert (e, n) == (339, 9), (e, n)
        # 스캔 반영: 첫 판/베스트/판수, 그리고 빈 스캔·부분 스캔이 기록을 지우지 않는지
        t = {"pb": {}, "days": {}}
        ev, ch = apply_scan(t, [("pasu", "10.00.00", 500), ("pasu", "11.00.00", 450), ("dot", "12.00.00", -5)], "2026-01-01")
        d1 = t["days"]["2026-01-01"]
        assert d1["first"] == {"pasu": 500, "dot": -5} and d1["best"] == {"pasu": 500, "dot": -5} and d1["count"] == {"pasu": 2, "dot": 1}, d1
        assert t["pb"]["pasu"] == 500 and ch and ev == [("pasu", 500, 500)], (ev, t["pb"])   # 음수 점수는 PB가 아님
        ev, ch = apply_scan(t, [], "2026-01-01")
        assert not ch and d1["best"]["pasu"] == 500 and d1["count"]["pasu"] == 2, d1
        ev, ch = apply_scan(t, [("pasu", "13.00.00", 520)], "2026-01-01")
        assert d1["first"]["pasu"] == 500 and d1["best"]["pasu"] == 520 and d1["count"]["pasu"] == 2 and ev == [("pasu", 520, 20)], (d1, ev)
        # 플레이리스트 펼치기: Day = 웜업 4 + 프로브 6 + 본훈련 17
        assert sum(n for _, n in dict(PLAYLISTS)["AIMDESK Day"]) == 27
        # 코박스 딥링크 형식 (3.0.0 패치노트: 공백은 %20)
        assert scenario_uri("VT Pasu Novice S5") == "steam://run/824270/?action=jump-to-scenario;name=VT%20Pasu%20Novice%20S5"
        print("selftest OK: seed energy =", e, "Silver · scan merge OK · deeplink OK")
        sys.exit(0)
    main()
