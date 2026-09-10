#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
에임 데스크 v3.2 — 코박스 자동 기록 + 성장 시각화 + 루틴 자동 진행 + 코치
· stats 폴더 2초 감시: 판 수/점수/신기록 실시간 자동
· 프로브(첫 판) 지수, 볼테익 동일 수식 에너지·랭크
· 루틴 실행 시 오늘 칠 시나리오 전체 순서창 (진행 자동 체크)
· 자동 진행(기본): 코박스 자체 플레이리스트로 돌리고, 판이 끝나 CSV가 생기면 앱이 PlaylistNext 키를 대신 눌러 다음 판으로
· 자동 진행(선택): 코박스 공식 딥링크(steam://run/824270/?action=jump-to-scenario)로 다음 시나리오를 직접 전송
· 순서창/루틴 줄에 판별 점수 + 최근 7일 평균 대비 ▲▼ + 역대 최고 경신(PB!) 표시
· 보낸 시나리오가 60초를 훌쩍 넘겨도 기록이 없으면 FREEPLAY(타이머 없음) 의심 경고
· 기록 보호: 원자적 저장 · 손상 파일 백업 · 스캔 실패 시 기록 보존 · 오류 로그
· 본훈련 테마가 요일마다 다르고(클리킹/트래킹/스위칭/전체 순회, 기록이 쌓이면 약점 집중), 프로브 6판은 측정 도구라 고정
· 한 판 점수는 흔들리므로 '평소 범위(중앙값±1.4826·MAD)' 기준 판정(최고/잘 나옴/평소/낮음) — ▲▼ 도배 금지
· 오늘의 띠 · 오늘 세션 곡선 · 훈련 레벨 · 오늘 한 장: 하루치 기록만 있어도 보이는 것들
· 실행: python aim_desk.py  (파이썬 3.9+, 추가 설치 없음)
"""
from __future__ import annotations
import json, math, os, re, sys, time, traceback, unicodedata
from datetime import date, datetime, timedelta
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
MAIN   = [("ww5", 3), ("popcorn", 3), ("dot", 6), ("drift", 3), ("cts", 2)]   # v3.1 까지의 고정 본훈련 (호환용)
FRIDAY = [("raw", 12), ("csphere", 12)]

# 본훈련 테마 — 매일 같은 17판을 치는 게 지겨워지지 않도록 월~목이 서로 다른 결을 갖는다.
# 판 수는 모두 17로 맞춰 세션 길이(약 45분)를 유지한다. 프로브 6판은 '측정 도구'라 절대 바뀌지 않는다.
MAIN_THEMES = [
    ("clk", "클리킹 집중", "한 번에 정확히 찍는 손", [("ww5", 4), ("w4", 4), ("pasu", 3), ("popcorn", 3), ("frog", 3)]),
    ("trk", "트래킹 집중", "붙어서 따라가는 손",     [("raw", 5), ("csphere", 4), ("ground", 4), ("aether", 4)]),
    ("swt", "스위칭 집중", "표적을 옮겨 다니는 손",   [("dot", 5), ("eddie", 4), ("drift", 4), ("cts", 4)]),
    ("mix", "전체 순회", "9개 갈래를 한 판씩 훑는 날", [("pasu", 2), ("ww5", 2), ("frog", 2), ("snake", 2), ("ground", 2),
                                                    ("raw", 2), ("dot", 2), ("drift", 2), ("penta", 1)]),
]

def weak_theme(pb: dict):
    """약점 집중 — 지금 가장 약한 서브카테고리 두 개에서 17판. 기록이 모자라면 None"""
    subs = [(s_, subE(s_, pb or {})) for s_ in SUBS]
    subs = [(s_, e) for s_, e in subs if e is not None]
    if len(subs) < 2: return None
    subs.sort(key=lambda x: x[1])
    a, b = subs[0][0], subs[1][0]
    items = [(a[3][0][0], 5), (a[3][1][0], 4), (b[3][0][0], 4), (b[3][1][0], 4)]
    return ("weak", "약점 집중", f"가장 낮은 {a[1]}·{a[2]} · {b[1]}·{b[2]} 를 파는 날", items)

def theme_line(dkey: str, pb: dict = None) -> str:
    """루틴 카드 맨 위 한 줄 — 오늘 무엇이 다른지와 내일 무엇이 오는지. 매일 같은 걸 친다는 느낌을 없애기 위한 것"""
    d = date.fromisoformat(dkey)
    dt = ["v", "v", "v", "v", "w", "b", "r"][d.weekday()]
    if dt != "v": return ""
    mt = main_theme(dkey, pb)
    out = f"오늘 본훈련 · {mt[1]} — {mt[2]}"
    for i in range(1, 5):                                    # 다음 발로 데이 예고 (금·토·일은 고정 루틴이라 건너뛴다 — 목요일이면 +4일)
        nd = d + timedelta(days=i)
        if ["v", "v", "v", "v", "w", "b", "r"][nd.weekday()] == "v":
            nm = main_theme(nd.isoformat(), pb)[1]
            out += (f" · 내일은 {nm}" if i == 1 else f" · {i}일 뒤는 {nm}")
            break
    return out

def week_themes(dkey: str, pb: dict = None) -> str:
    """이번 주 월~목 본훈련 테마 한 줄. '매일 같은 걸 친다'는 느낌을 눈으로 반박하는 용도"""
    d = date.fromisoformat(dkey)
    if d.weekday() > 3: return ""
    mon = d - timedelta(days=d.weekday())
    out = []
    for i in range(4):
        dd = mon + timedelta(days=i)
        out.append(("▶" if dd == d else "") + f"{'월화수목'[i]} {main_theme(dd.isoformat(), pb)[1]}")
    return "이번 주 · " + " · ".join(out)

def daily_challenge(data: dict, dkey: str, pb: dict = None):
    """오늘의 도전 — 오늘 칠 시나리오 중 '다음 등급 칸'이 가장 가까운 하나.
    목표를 앱이 지어내지 않고 볼테익 등급 임계값을 그대로 쓴다. 손이 닿는 거리가 아니면 (2.5 표준편차 밖) 내지 않는다."""
    d = date.fromisoformat(dkey)
    dt = ["v", "v", "v", "v", "w", "b", "r"][d.weekday()]
    if dt == "r": return None
    if dt == "v":   items = [k for k, _n in main_theme(dkey, pb)[3]]
    elif dt == "w": items = [k for k, _n in FRIDAY]
    else:           items = [k for k, _n in BENCH]
    pb = pb if pb is not None else data.get("pb", {})
    best = None
    for k in dict.fromkeys(items):
        th = th_of(k); cur = pb.get(k)
        if not th or cur is None: continue
        rank, t, gap = next_rank_gap(cur, th)
        if rank is None: continue                      # 이미 Gold 칸
        band = scen_band(data, k, dkey) or scen_day_band(data, k, dkey)
        sd = band["sd"] if band else max(1.0, cur * 0.03)
        sig = gap / sd
        if sig > 2.5: continue                         # 오늘 손이 닿는 거리가 아니면 도전으로 내지 않는다
        if best is None or sig < best["sigma"]:
            best = {"key": k, "target": t, "cur": cur, "rank": rank, "gap": gap, "sigma": sig}
    return best

def fmt_challenge(ch, today_best=None) -> str:
    if not ch: return ""
    s_ = f"오늘의 도전 · {sname(ch['key'])} {ch['target']}점 — 넘으면 {ch['rank']} 칸 (지금 최고 {ch['cur']})"
    if today_best is not None:
        s_ += f" · 오늘 {today_best}" + (" ✓ 달성" if today_best >= ch["target"] else f" · {ch['target'] - today_best} 남음")
    return s_

def main_theme(dkey: str, pb: dict = None):
    """그날의 본훈련 테마 (id, 이름, 설명, [(시나리오, 판수)]).
    날짜만으로 정해진다 — 앱을 껐다 켜도, 코박스에 설치된 플레이리스트와도 늘 같은 것을 가리키게.
    (주차 + 요일) % 4 라서 월~목이 한 주 안에서 모두 다르고, 다음 주에는 요일마다 한 칸씩 밀린다."""
    d = date.fromisoformat(dkey)
    i = (d.isocalendar()[1] + d.weekday()) % 4
    if i == 3:
        return weak_theme(pb or {}) or MAIN_THEMES[3]   # 기록이 쌓이면 '전체 순회' 자리가 '약점 집중'으로 바뀐다
    return MAIN_THEMES[i]

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

def today_date() -> date:
    """오늘. 환경변수 AIMDESK_TODAY=YYYY-MM-DD 가 있으면 그 날 (테스트가 요일·날짜에 좌우되지 않게)"""
    t = os.environ.get("AIMDESK_TODAY")
    if t:
        try: return date.fromisoformat(t)
        except ValueError: pass
    return date.today()

def _data_dir():
    """기본은 exe 옆. 쓰기 불가(Program Files 등)이거나 임시폴더 실행(zip 안에서 더블클릭)이면
    %LOCALAPPDATA%\\AimDesk 로 — 이때 exe 옆에 기존 기록이 있으면 1회 복사해 온다.
    환경변수 AIMDESK_DATA_DIR 이 있으면 무조건 그곳(테스트가 실제 기록을 건드리지 않게)."""
    env = os.environ.get("AIMDESK_DATA_DIR")
    if env:
        p = Path(env); p.mkdir(parents=True, exist_ok=True); return p
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

def log_line(msg: str):
    try:
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {msg}\n")
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
    d.setdefault("win", {}); d.setdefault("seq_compact", False)
    if not d.get("seeded"):
        d["days"].setdefault(SEED_DATE, blank_day())["best"] = dict(SEED)
        for k, v in SEED.items():
            d["pb"][k] = max(d["pb"].get(k, 0), v)
        d["seeded"] = True
    return d

def blank_day() -> dict:
    return {"first": {}, "best": {}, "count": {},
            "plays": [],                                   # [key, 'HH.MM.SS', score] 판별 기록 (시간순)
            "sess": {"start": None, "end": None},          # 오늘 루틴 시나리오의 첫/마지막 판 시각
            "deaths": {"aim":0,"pos":0,"dec":0,"trade":0},
            "cond": {"sleep":None,"caf":0,"feel":5},
            "checks": {"miyagi":False,"ranked":False}}

def merge_plays(existing, plays):
    """판별 기록 합치기: (key, 시각) 이 같으면 새 점수가 이긴다. 시간순 정렬된 [key, t, score] 목록"""
    m = {}
    for e in list(existing or []) + [list(x) for x in plays]:
        k, t, sc = e[0], e[1], int(round(e[2]))
        m[(k, t)] = [k, t, sc]
    return [m[kt] for kt in sorted(m, key=lambda kt: (kt[1], kt[0]))]

def day_plays(data: dict, dkey: str):
    return [tuple(x) for x in data["days"].get(dkey, {}).get("plays", [])]

def pb_days(data: dict) -> dict:
    """시나리오별로 PB 점수를 처음 낸 날짜"""
    out = {}
    for d in sorted(data["days"]):
        for k, v in data["days"][d]["best"].items():
            if k not in out and v == data["pb"].get(k): out[k] = d
    return out

def t_min(t: str) -> int:
    """'HH.MM.SS' → 분"""
    hh, mm = t.split(".")[:2]
    return int(hh) * 60 + int(mm)

DATA_VER = [0]                  # 기록이 바뀔 때마다 +1 — 계산 캐시(프로브 지수·최근 평균·memo)의 키
SAVE_COUNT = [0]
# 불변식: data 를 바꾸는 모든 곳은 곧바로 save_data() 를 부른다(= bump). 저장을 미루는 코드는 넣지 않는다.
def bump_ver(): DATA_VER[0] += 1

_MEMO: dict = {}
def memo(key: tuple, fn):
    """기록 버전이 그대로면 지난 결과 재사용. 오늘 날짜에 의존하는 계산은 key 에 dkey 를 넣는다"""
    v = DATA_VER[0]; hit = _MEMO.get(key)
    if hit is not None and hit[0] == v: return hit[1]
    r = fn(); _MEMO[key] = (v, r)
    return r

def save_data(d: dict):
    """임시 파일에 다 쓴 뒤 교체 — 쓰는 도중 꺼져도 잘린 파일이 남지 않는다"""
    bump_ver(); SAVE_COUNT[0] += 1
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

_MISS_SEEN: dict = {}     # 점수를 못 읽은 파일의 (mtime, size) — 같은 모습으로 다시 보이면 '쓰다 만 파일'이 아니라 영구 미인식

def read_score_cached(fp: Path, entry=None):
    """점수 읽기 — (mtime, size) 가 같으면 캐시. 못 읽은 파일은 한 번은 다시 읽어 보고(아직 쓰는 중일 수 있음),
    같은 모습이면 None 으로 캐시해 2초마다 다시 읽지 않는다. 반환 (점수, 불안정 여부)"""
    try: st = entry.stat() if entry is not None else fp.stat()
    except OSError: return None, True
    sig = (st.st_mtime_ns, st.st_size)
    hit = _SCORE_CACHE.get(fp.name)
    if hit and hit[0] == sig: return hit[1], False
    s = read_score(fp)
    if s is not None:
        _SCORE_CACHE[fp.name] = (sig, s); _MISS_SEEN.pop(fp.name, None); return s, False
    if _MISS_SEEN.get(fp.name) == sig:
        _SCORE_CACHE[fp.name] = (sig, None); return None, False           # 두 번째도 그대로 → 영구 미인식
    _MISS_SEEN[fp.name] = sig
    return None, True

SCAN_FORCE_EVERY = 15                                   # 15틱(30초)마다 한 번은 캐시를 무시하고 다시 훑는다
_SCAN_STATE = {"sig": None, "plays": [], "info": {}, "n": 0, "hits": 0}   # 폴더 mtime이 그대로면 지난 결과를 그대로 쓴다

def scan_day(stats: Path, day: date, force: bool = False):
    """해당 날짜의 (key, 'HH.MM.SS', score) 목록 + 진단 집계. 폴더를 못 읽으면 None(그 턴은 건너뜀).
    파일이 생기거나 지워지면 폴더의 mtime이 바뀌므로, 안 바뀌었으면 수만 개 파일을 다시 훑지 않는다.
    force=True(자동 진행 중)면 캐시를 건너뛴다 — 폴더 mtime 이 안 바뀌는 드라이브(exFAT·네트워크)에서도 2초 안에 감지."""
    tag = day.strftime("%Y.%m.%d")
    try: sig = (str(stats), stats.stat().st_mtime_ns, tag)
    except OSError: return None
    _SCAN_STATE["n"] += 1
    forced = force or _SCAN_STATE["n"] % SCAN_FORCE_EVERY == 0      # mtime 해상도가 거친 드라이브 대비 안전장치
    if not forced and _SCAN_STATE["sig"] == sig:
        _SCAN_STATE["hits"] += 1
        SCAN_INFO.update(_SCAN_STATE["info"], t=datetime.now().strftime("%H:%M:%S"))
        return list(_SCAN_STATE["plays"])
    out = []; miss = 0; other = 0; unstable = 0
    try:
        with os.scandir(stats) as it:
            for e in it:
                name = e.name
                if tag not in name: continue              # 정규식 전에 싼 문자열 검사 (수만 개 중 오늘 것만)
                m = FNAME_RE.match(name)
                if not m or m.group("d") != tag: continue
                key = NAME2KEY.get(m.group("scen"))
                if key is None:
                    other += 1; continue                  # 루틴 밖 시나리오 — 인식 실패가 아님
                sc, uns = read_score_cached(Path(e.path), e)   # DirEntry 의 stat 재사용
                if sc is None:
                    miss += 1; unstable += uns; continue
                out.append((key, m.group("t"), round(sc)))
    except OSError: return None
    info = dict(plays=len(out), miss=miss, other=other)
    SCAN_INFO.update(info, t=datetime.now().strftime("%H:%M:%S"))
    # 아직 쓰는 중일 수 있는 파일이 있으면 캐시하지 않고 다음 틱에 다시 본다 (영구 미인식 파일은 캐시를 막지 않는다)
    if unstable == 0: _SCAN_STATE.update(sig=sig, plays=list(out), info=info)
    else: _SCAN_STATE["sig"] = None
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
    merged = merge_plays(day.get("plays", []), plays)
    sess = day.setdefault("sess", {"start": None, "end": None})
    ns, ne = sess.get("start"), sess.get("end")
    if plays:                                    # 세션 시각은 넓어지기만 한다 (루틴 시나리오 기준)
        ts = sorted(t for _, t, _ in plays)
        ns = ts[0] if ns is None or ts[0] < ns else ns
        ne = ts[-1] if ne is None or ts[-1] > ne else ne
    changed = (first != day["first"] or best != day["best"] or count != day["count"]
               or merged != day.get("plays", []) or (ns, ne) != (sess.get("start"), sess.get("end")))
    if changed: bump_ver()
    day["first"], day["best"], day["count"] = first, best, count
    day["plays"] = merged; sess["start"], sess["end"] = ns, ne
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

RANK_NAMES = ("Iron", "Bronze", "Silver", "Gold")      # 임계값 인덱스 순

def rank_of(e):
    if e is None: return ("—", C["dim"])
    for t, n, c in RANKS:
        if e >= t: return (n, c)
    return ("Unranked", C["dim"])

def sub_of(key):
    """key 가 속한 SUBS 항목 (없으면 None)"""
    for sub in SUBS:
        if any(k == key for k, _ in sub[3]): return sub
    return None

def th_of(key):
    sub = sub_of(key)
    if sub is None: return None
    return next(th for k, th in sub[3] if k == key)

def next_rank_gap(score, th):
    """(다음 랭크 이름, 그 임계값, 부족 점수). 골드 이상이면 (None, th[3], 0)"""
    for i, t in enumerate(th):
        if score < t: return (RANK_NAMES[i], t, t - score)
    return (None, th[3], 0)

# ══════════════════ 프로브 지수 ══════════════════
_PS_CACHE = {"ver": None, "n": None, "out": None}

def probe_series(data: dict):
    """일별 프로브 지수(z 평균)와 7일 이동평균. 기록 버전이 그대로면 지난 결과 재사용"""
    n = sum(len(e["first"]) for e in data["days"].values())
    if _PS_CACHE["ver"] == DATA_VER[0] and _PS_CACHE["n"] == n and _PS_CACHE["out"] is not None:
        return _PS_CACHE["out"]
    out = _probe_series(data)
    _PS_CACHE.update(ver=DATA_VER[0], n=n, out=out)
    return out

def _probe_series(data: dict):
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

TODAY_PLAYS: list = []      # 오늘 판 (key, 'HH.MM.SS', score) 시간순 — 순서창에 판별 점수를 붙이기 위해

_RS_CACHE = {"ver": None, "m": {}}

def recent_stats(data: dict, key: str, before_day: str, field: str = "best", n: int = 7):
    """before_day 이전 기록의 (최근 n일 평균 of field, 역대 최고 of best). 기록이 없으면 (None, None).
    같은 기록 버전 안에서는 (key, day, field)별로 한 번만 계산한다 — 순서창 27줄이 2초마다 갱신돼도 가볍게."""
    if _RS_CACHE["ver"] != DATA_VER[0]:
        _RS_CACHE.update(ver=DATA_VER[0], m={})
    ck = (key, before_day, field, n)
    hit = _RS_CACHE["m"].get(ck)
    if hit is not None: return hit
    r = _recent_stats(data, key, before_day, field, n)
    _RS_CACHE["m"][ck] = r
    return r

def _recent_stats(data: dict, key: str, before_day: str, field: str = "best", n: int = 7):
    days = [data["days"][d] for d in sorted(data["days"]) if d < before_day]
    vals = [e[field].get(key) for e in days if e[field].get(key) is not None]
    bests = [e["best"].get(key) for e in days if e["best"].get(key) is not None]
    if not vals and not bests: return None, None
    recent = vals[-n:]
    return (sum(recent) / len(recent) if recent else None), (max(bests) if bests else None)

def bench_days(data: dict):
    out = []
    for k in sorted(data["days"]):
        e, n = totalE(data["days"][k]["best"])
        if e is not None and n == 9:
            out.append((k, e))
    return out



# ══════════════════ UI 계산용 순수 함수 (테스트 가능) ══════════════════
UI_SCALE = [1.0]
def px(n): return int(round(n * UI_SCALE[0]))

SCALE_STEPS = [1.0, 1.25, 1.5, 1.75, 2.0]      # 녹화하면 100% 글씨는 시청자 화면에서 뭉갠다

def scale_label(v) -> str:
    return "자동" if not v else f"{int(round(float(v) * 100))}%"

def pick_scale(saved, env, auto) -> float:
    """실제로 쓸 배율. 환경변수(테스트) > 사용자가 고른 값 > 모니터 DPI"""
    if env: return float(env)
    if saved: return max(0.8, min(3.0, float(saved)))
    return max(1.0, float(auto or 1.0))

TOAST_MS = 10000
HDR_STATE = {"vi": None, "oi": None}
COACH_STATE = {"brief": [], "validity": None, "fat_sig": None, "fat_len": 0, "toasts": []}
_DBG: dict = {}                       # 테스트 훅: main() 이 위젯·클로저를 채운다

def shade(hexc: str, d: int) -> str:
    h = hexc.lstrip("#"); r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    cl = lambda v: max(0, min(255, v + d))
    return "#%02x%02x%02x" % (cl(r), cl(g), cl(b))

def contrast_ratio(fg: str, bg: str) -> float:
    def lum(hexc):
        h = hexc.lstrip("#")
        out = []
        for i in (0, 2, 4):
            c = int(h[i:i+2], 16) / 255
            out.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
        return 0.2126 * out[0] + 0.7152 * out[1] + 0.0722 * out[2]
    a, b = lum(fg), lum(bg)
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)

def status_line(info: dict, stats_ok: bool, scan_err: bool, save_err, auto_on: bool):
    """하단 상태줄 (문구, 단계 'ok'|'warn'|'err')"""
    if save_err: r = (f"● 저장 실패 — {str(save_err)[:60]}", "err")
    elif not stats_ok: r = ("● stats 폴더를 찾을 수 없음 — 오늘 탭 우측 카드에서 폴더 선택", "err")
    elif scan_err: r = ("● 폴더 읽기 실패 — 기록은 보존, 자동 복구 대기", "warn")
    elif not info.get("plays"): r = ("● 오늘 0판 — 판이 끝나면 여기에 쌓입니다 (안 늘면 코박스 상단 토글 '도전 과제' 확인)", "warn")
    else:
        t = f"● 감시 중 · 오늘 {info['plays']}판 · {info.get('t', '')}"
        if info.get("other"): t += f" · 루틴 외 {info['other']}판"
        if info.get("miss"): t += f" · 점수 인식실패 {info['miss']}"
        r = (t, "ok")
    if auto_on: r = (r[0] + " · 자동 진행 ▶", r[1])
    return r

def mask_user_path(p: str) -> str:
    r"""C:\Users\홍길동\... → C:\Users\…\... — 화면을 녹화하면 윈도우 계정명이 그대로 나간다"""
    if not p: return ""
    parts = re.split(r"([\\/])", str(p))
    for i, seg in enumerate(parts):
        if seg.lower() in ("users", "home") and i + 2 < len(parts) and parts[i + 2]:
            parts[i + 2] = "…"
            break
    return "".join(parts)

def bench_src_label(src, n: int) -> str:
    if not src: return ""
    if src == SEED_DATE: return f"기준값 · {int(SEED_DATE[5:7])}/{int(SEED_DATE[8:10])} · 9/9"
    return f"{src} · {n}/9"

def seq_rows_apply(seq, done, nxt, scores, rs, vf=None):
    """순서창 각 줄의 표시값. rs(key) -> (최근 평균, 역대 최고). vf(key, 점수) -> (판정, 문구, 색키).
    vf 를 주면 '▲12/▼12' 대신 '평소·잘 나옴·낮음·최고' 로 적는다 — 한 판 점수는 평균과 몇 점 차이인지가
    의미 없을 만큼 흔들리기 때문. 반환: (rows, 신기록 수, 평균 대비 비율 목록)
    row = (num_fg, nm_fg, st_text, st_fg, sc_text, sc_fg, dl_text, dl_fg) — 색은 팔레트 키 이름"""
    rows, pb_keys, rel = [], set(), []
    for i, k in enumerate(seq):
        s_ = scores[i]
        if done[i]:
            if s_ is None:
                rows.append(("dim", "dim", "–", "dim", "", "txt", "건너뜀", "dim")); continue
            avg, pmax = rs(k)
            if avg: rel.append(s_ / avg - 1)
            if vf is not None:
                kind, label, colk = vf(k, s_)
                new_pb = kind == "pb"
                dl = (label, colk)
            else:
                new_pb = pmax is not None and s_ > pmax
                if new_pb: dl = ("PB!", "gold")
                elif avg is not None:
                    d_ = s_ - avg; dl = (f"{'▲' if d_ >= 0 else '▼'}{abs(d_):.0f}", "ok" if d_ >= 0 else "val")
                else: dl = ("", "dim")
            if new_pb: pb_keys.add(k)
            rows.append(("dim", "dim", "✓", "ok", str(s_), "gold" if new_pb else "txt", dl[0], dl[1]))
        elif i == nxt:
            avg, _ = rs(k)
            rows.append(("gold", "txt", "▶", "gold", f"{avg:.0f}" if avg is not None else "", "hint",
                         "평균" if avg is not None else "", "hint"))
        else:
            rows.append(("dim", "sub", "", "dim", "", "txt", "", "dim"))
    return rows, len(pb_keys), rel

class ToastQueue:
    """최대 max_n 개, 각각 ttl 초 뒤 사라짐. 시계는 바깥에서 준다(테스트용)"""
    def __init__(self, max_n=3, ttl=TOAST_MS / 1000):
        self.max_n, self.ttl, self.items = max_n, ttl, []
    def push(self, msg, kind, now):
        self.items.append((msg, kind, now + self.ttl))
        while len(self.items) > self.max_n: self.items.pop(0)
    def expire(self, now) -> bool:
        n = len(self.items); self.items = [it for it in self.items if it[2] > now]
        return len(self.items) != n
    def dismiss(self, i):
        if 0 <= i < len(self.items): self.items.pop(i)
    def clear(self): self.items = []

def pb_context(key, score, old, pb_after: dict) -> str:
    """신기록 토스트 문구: 서브카테고리 에너지 변화와 다음 랭크까지 남은 점수"""
    head = f"🏆 {sname(key)} {score} (+{score - old})"
    sub = sub_of(key)
    if sub is None: return head
    pb_before = dict(pb_after)
    if old > 0: pb_before[key] = old
    else: pb_before.pop(key, None)
    e_old, e_new = subE(sub, pb_before), subE(sub, pb_after)
    mid = f"{sub[2]} {e_old}→{e_new}" if e_old != e_new else f"{sub[2]} {e_new}"
    rank, _, gap = next_rank_gap(score, th_of(key))
    tail = f"{rank}까지 {gap}점" if rank else "Gold 칸 ✓"
    return f"{head} · {mid} · {tail}"

def pb_toast_lines(events, pb: dict, max_n: int = 2):
    """events = [(key, score, diff)] → 토스트 줄들 (많으면 한 줄 요약)"""
    if not events: return []
    if len(events) <= max_n:
        return [pb_context(k, s_, s_ - diff, pb) for k, s_, diff in events]
    body = ", ".join(f"{sname(k)} {s_}" for k, s_, _ in events)
    line = f"🏆 신기록 {len(events)}개 — {body}"
    return [line if len(line) <= 60 else line[:59] + "…"]

def wheel_units(delta, num) -> int:
    if num == 4: return -1
    if num == 5: return 1
    if not delta: return 0
    u = -int(delta / 120)
    return u if u else (-1 if delta > 0 else 1)          # 정밀 터치패드의 작은 델타도 한 칸

def needs_scroll(content_h: int, view_h: int) -> bool:
    return content_h > view_h + 2

_GEO_RE = re.compile(r"^(\d+)x(\d+)([+-]\d+)([+-]\d+)$")
_POS_RE = re.compile(r"^([+-]\d+)([+-]\d+)$")
def _overlaps(x, y, w, h, vx, vy, vw, vh, need=120):
    ox = min(x + w, vx + vw) - max(x, vx); oy = min(y + h, vy + vh) - max(y, vy)
    return ox >= need and oy >= need

def clamp_geometry(geo, vx, vy, vw, vh, minw, minh):
    """저장된 'WxH+X+Y' 가 지금 화면에 보이면 (크기 보정해서) 돌려주고, 아니면 None"""
    m = _GEO_RE.match(geo or "")
    if not m: return None
    w, h, x, y = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    w = max(minw, min(w, vw)); h = max(minh, min(h, vh))
    if not _overlaps(x, y, w, h, vx, vy, vw, vh): return None
    return f"{w}x{h}{x:+d}{y:+d}"

def clamp_pos(pos, w, h, vx, vy, vw, vh):
    m = _POS_RE.match(pos or "")
    if not m: return None
    x, y = int(m.group(1)), int(m.group(2))
    return pos if _overlaps(x, y, w, h, vx, vy, vw, vh) else None

# ── 오늘 세션 요약 · 훈련 스트릭 · 이번 주 ──
def session_summary(plays, rc: dict) -> dict:
    """plays = [(key, 'HH.MM.SS', score)], rc[key] = (최근 평균, 역대 최고)"""
    if not plays: return {"n": 0, "start": None, "end": None, "minutes": None, "n_pb": 0, "rel": None}
    ts = sorted(t for _, t, _ in plays)
    best_by, rel = {}, []
    for k, t, sc in plays:
        best_by[k] = max(best_by.get(k, sc), sc)
        avg = rc.get(k, (None, None))[0]
        if avg: rel.append(sc / avg - 1)
    n_pb = sum(1 for k, b in best_by.items() if rc.get(k, (None, None))[1] is not None and b > rc[k][1])
    return {"n": len(plays), "start": ts[0], "end": ts[-1], "minutes": t_min(ts[-1]) - t_min(ts[0]),
            "n_pb": n_pb, "rel": (sum(rel) / len(rel) if rel else None)}

def fmt_session(s: dict) -> str:
    if not s["n"]: return ""
    hm = lambda t: t[:5].replace(".", ":")
    # 신기록 수는 띠 줄이 말한다 (판별 판정 기준) — 여기서 다른 기준으로 또 세면 같은 화면에 다른 숫자가 뜬다
    return f"{s['minutes']}분 ({hm(s['start'])}–{hm(s['end'])})"

def training_days(data: dict) -> set:
    return {d for d, e in data["days"].items() if d != SEED_DATE and (e.get("first") or e.get("count"))}

def streak(days: set, today: date, rest_wd=(6,)):
    """(현재 연속 훈련일, 최고 기록). 휴식 요일은 끊지도 더하지도 않는다"""
    cur = 0; d = today
    if d.isoformat() not in days: d -= timedelta(days=1)
    for _ in range(4000):
        if d.weekday() in rest_wd and d.isoformat() not in days:
            d -= timedelta(days=1); continue
        if d.isoformat() in days: cur += 1; d -= timedelta(days=1)
        else: break
    best = run = 0; prev = None
    for ds in sorted(days):
        dd = date.fromisoformat(ds)
        if prev is None: run = 1
        else:
            gap = [prev + timedelta(days=i) for i in range(1, (dd - prev).days)]
            run = run + 1 if all(g.weekday() in rest_wd for g in gap) else 1
        best = max(best, run); prev = dd
    return cur, max(best, cur)

def week_strip(days: set, today: date, rest_wd=(6,)):
    """이번 주 월~일 각 칸의 상태: done / rest / today / future / miss"""
    mon = today - timedelta(days=today.weekday()); out = []
    for i in range(7):
        d = mon + timedelta(days=i); ds = d.isoformat()
        if ds in days: st = "done"
        elif d.weekday() in rest_wd: st = "rest"
        elif d == today: st = "today"
        elif d > today: st = "future"
        else: st = "miss"
        out.append((DOWK[i], st))
    return out

# ── 루틴 줄: 분절 진행바 · 섹션 진행 · 다음 판 ──
def segment_geometry(width: int, n: int, gap: int = 3, cap: int = 12):
    n = max(1, min(n, cap)); w = (width - gap * (n - 1)) / n
    return [(int(round(i * (w + gap))), int(round(i * (w + gap) + w))) for i in range(n)]

def section_progress(rows, day: dict):
    """rows = [(kind, key, target)] → (완료, 전체)"""
    d = t = 0
    for kind, key, target in rows:
        if kind == "probe": d += 1 if day["first"].get(key) is not None else 0; t += 1
        elif kind == "check": d += 1 if day["checks"].get(key) else 0; t += 1
        else: d += min(day["count"].get(key, 0), target); t += target
    return d, t

def next_routine_key(rows, day: dict, seq_next):
    if seq_next: return seq_next
    for kind, key, target in rows:
        done = (day["first"].get(key) is not None) if kind == "probe" else \
               bool(day["checks"].get(key)) if kind == "check" else day["count"].get(key, 0) >= target
        if not done: return key
    return None

# ── 벤치: 약한 고리 · 다음 등급까지 ──
def score_for_energy(e: float, th) -> float:
    """scenE 의 역함수 (구간별 선형)"""
    a, b, c, d = th
    if e < 100: return a * e / 100
    if e < 200: return a + (b - a) * (e - 100) / 100
    if e < 300: return b + (c - b) * (e - 200) / 100
    if e < 400: return c + (d - c) * (e - 300) / 100
    return d + (d - c) * (e - 400) / 100

def fmt_gap(score, th):
    if score is None: return ("", C["dim"])
    rank, t, gap = next_rank_gap(score, th)
    if rank is None: return (f"Gold +{score - th[3]}", C["gold"])
    return (f"{rank}까지 {gap}", RANKC[RANK_NAMES.index(rank)])

def weakest_link(scores: dict):
    """조화평균을 가장 끌어내리는 서브카테고리와, 다음 100 단위 에너지까지 필요한 점수"""
    subs = [(sub, subE(sub, scores)) for sub in SUBS]
    subs = [(sub, e) for sub, e in subs if e is not None]
    if not subs: return None
    sub, e = min(subs, key=lambda x: x[1])
    target = (e // 100 + 1) * 100
    needs = []
    for k, th in sub[3]:
        need = math.ceil(score_for_energy(target, th)); cur = scores.get(k)
        needs.append((k, need, need - (cur if cur is not None else 0)))
    total_now, _ = totalE(scores)
    kb = min(needs, key=lambda x: x[2])
    after = dict(scores); after[kb[0]] = max(after.get(kb[0], 0), kb[1])
    total_after, _ = totalE(after)
    others = sorted([(s2, e2) for s2, e2 in subs if s2 is not sub], key=lambda x: x[1])
    runner = (others[0][0][2], others[0][1]) if others and others[0][1] - e <= 10 else None
    tn = None
    for t, n, _c in sorted(RANKS):
        if total_now is not None and total_now < t: tn = (n, t - total_now); break
    return {"sub": sub[0], "cat": sub[1], "name": sub[2], "e": e, "target": target, "needs": needs,
            "total_now": total_now, "total_after": total_after, "runner_up": runner, "total_next": tn}

def fmt_weakest(w) -> str:
    if not w: return ""
    (k1, n1, g1), (k2, n2, g2) = w["needs"]
    t = (f"약한 고리 (PB 기준) · {w['cat']} {w['name']} {w['e']} — {sname(k1)} {n1}(+{g1}) 또는 {sname(k2)} {n2}(+{g2}) 이면 "
         f"{w['target']} → 총 {w['total_now']}→{w['total_after']}")
    if w["total_next"]: t += f"   ·   {w['total_next'][0]}까지 총 +{w['total_next'][1]}"
    if w["runner_up"]: t += f"   ({w['runner_up'][0]} {w['runner_up'][1]}도 비슷)"
    return t

# ── 죽음 원인 추세 ──
DEATH_NAMES = {"aim": "에임", "pos": "위치", "dec": "판단", "trade": "트레이드"}
def deaths_window(data: dict, end_day: str, n: int = 7, offset: int = 0) -> dict:
    end = date.fromisoformat(end_day)
    out = {"aim": 0, "pos": 0, "dec": 0, "trade": 0, "total": 0, "days": 0}
    for i in range(n):
        e = data["days"].get((end - timedelta(days=offset + i)).isoformat())
        if not e: continue
        dd = e.get("deaths", {}); tot = 0
        for c in DEATH_NAMES:
            v = int(dd.get(c, 0) or 0); out[c] += v; tot += v
        out["total"] += tot
        if tot: out["days"] += 1
    return out

def deaths_trend(data: dict, end_day: str) -> dict:
    cur = deaths_window(data, end_day); prev = deaths_window(data, end_day, offset=7)
    order = list(DEATH_NAMES)
    dom = max(order, key=lambda c: (cur[c], -order.index(c))) if cur["total"] else None
    share = round(100 * cur[dom] / cur["total"]) if dom else None
    pshare = round(100 * prev[dom] / prev["total"]) if (dom and prev["total"]) else None
    delta = (share - pshare) if (share is not None and pshare is not None) else None
    return {"cur": cur, "prev": prev, "dom": dom, "dom_share": share, "prev_share": pshare, "delta": delta}

def fmt_deaths_trend(t: dict):
    if not t["cur"]["total"]: return ("이번 주 태그 없음", C["dim"])
    txt = f"이번 주 {t['cur']['total']}회 · {DEATH_NAMES[t['dom']]} {t['dom_share']}%"
    if t["prev_share"] is not None:
        txt += f" (지난주 {t['prev_share']}% {'▲' if t['delta'] > 0 else '▼' if t['delta'] < 0 else '='})"
    col = C["ok"] if (t["delta"] is not None and t["delta"] < 0) else C["val"] if (t["delta"] is not None and t["delta"] > 0) else C["hint"]
    return (txt, col)

# ── 순서창 코치: 블록 추세 · 피로 신호 · 남은 시간 ──
BLOCK_TREND_PCT = 1.5
WARM_KEYS = frozenset(k for k, _ in WARMUP)

def _slope_pct(pts):
    """[(index, value)] 최소제곱 기울기를 평균 대비 %/판 으로. 3점 미만·평균 0 이면 None"""
    if len(pts) < 3: return None
    n = len(pts); mx = sum(i for i, _ in pts) / n; my = sum(v for _, v in pts) / n
    sxx = sum((i - mx) ** 2 for i, _ in pts)
    if my == 0 or sxx == 0: return None
    return sum((i - mx) * (v - my) for i, v in pts) / sxx / my * 100

def blocks_of(seq):
    """같은 시나리오가 3판 이상 이어지는 구간 [(key, start, end)]"""
    out = []; i = 0
    while i < len(seq):
        j = i
        while j < len(seq) and seq[j] == seq[i]: j += 1
        if j - i >= 3: out.append((seq[i], i, j))
        i = j
    return out

def block_trend(pts):
    pct = _slope_pct(pts)
    if pct is None: return None
    return ("↗" if pct >= BLOCK_TREND_PCT else "↘" if pct <= -BLOCK_TREND_PCT else "→", pct)

def sessions_of(plays, gap_min: int = 20):
    out = []
    for p in sorted(plays, key=lambda x: x[1]):
        if out and t_min(p[1]) - t_min(out[-1][-1][1]) > gap_min: out.append([p])
        elif out: out[-1].append(p)
        else: out.append([p])
    return out

def fatigue_signal(plays, avg: dict, warm=WARM_KEYS):
    """피로 신호: 같은 판 3연속 하락(4%↑) → 3판 연속 평균의 92% 아래 → 한 세션 75분 이상"""
    ps = [p for p in plays if p[0] not in warm]
    if len(ps) >= 3:
        a, b, c = ps[-3:]
        if a[0] == b[0] == c[0] and a[2] > b[2] > c[2] and a[2] > 0:
            drop = (a[2] - c[2]) / a[2] * 100
            if drop >= 4: return {"kind": "streak", "key": a[0], "drop": drop}
        if all(avg.get(p[0]) and p[2] <= 0.92 * avg[p[0]] for p in (a, b, c)): return {"kind": "under"}
    if ps:
        cur = sessions_of(ps)[-1]
        span = t_min(cur[-1][1]) - t_min(cur[0][1])
        if span >= 75: return {"kind": "long", "min": span}
    return None

def fatigue_msg(sig) -> str:
    if sig["kind"] == "streak": return f"{sname(sig['key'])} 3판 연속 ↓(−{sig['drop']:.0f}%) — 여기서 끊어도 좋아요. 남은 판은 내일 첫판이 더 값집니다"
    if sig["kind"] == "under": return "3판 연속 평균 아래 — 손목·집중 신호. 워밍업 1판 넣거나 오늘은 여기까지"
    return f"{sig['min']}분째 — 오늘 몫은 충분. 내일 이어서"

def probe_status(day: dict):
    return sum(1 for k in PROBE if day["first"].get(k) is not None), len(PROBE)

def remaining_estimate(plays, remaining: int):
    if remaining <= 0: return None
    ts = sorted(t_min(t) for _, t, _ in plays)
    gaps = [b - a for a, b in zip(ts, ts[1:]) if 0 < b - a <= 6]
    gap = sorted(gaps)[len(gaps) // 2] if len(gaps) >= 3 else 1.5
    return round(remaining * gap)

def fmt_seq_summary(played, total, n_pb, rel, probe, idx, est_min, block_txt=None) -> str:
    parts = []
    if block_txt: parts.append(block_txt)
    parts.append(f"오늘 {played}/{total}판")
    if n_pb: parts.append(f"PB {n_pb} 🏆")
    if rel:
        m = sum(rel) / len(rel) * 100; parts.append(f"{'▲' if m >= 0 else '▼'}{abs(m):.1f}%")
    if probe:
        pr = f"프로브 {probe[0]}/{probe[1]}"
        vi, oi = idx
        if vi is not None: pr += f" 발로 {vi:+.1f}"
        if oi is not None: pr += f" 옵치 {oi:+.1f}"
        parts.append(pr)
    remaining = total - played
    if remaining > 0:
        parts.append(f"남은 {remaining}판" + (f" ≈ {est_min}분" if est_min is not None else ""))
    return " · ".join(parts)

# ── 코치 카드: 어제 지수 · 오늘 초점 · 컨디션 · 프로브 유효성 ──
def last_probe_day(data: dict, before: str):
    for d in sorted(data["days"], reverse=True):
        if d < before and d != SEED_DATE and any(data["days"][d]["first"].get(k) is not None for k in PROBE): return d
    return None

def focus_pick(data: dict, dkey: str):
    """마지막 프로브 날의 첫판이 최근 평균보다 3% 이상 낮았던 시나리오 (가장 처진 것)"""
    lp = last_probe_day(data, dkey)
    if lp is None: return None
    best = None
    for k in PROBE:
        x = data["days"][lp]["first"].get(k)
        if x is None: continue
        priors = [data["days"][d]["first"].get(k) for d in sorted(data["days"]) if d < lp]
        priors = [v for v in priors if v is not None]
        if len(priors) < 3: continue
        avg = sum(priors[-7:]) / len(priors[-7:])
        ratio = x / avg - 1
        if ratio < -0.03 and (best is None or ratio < best[0]): best = (ratio, k, x, avg)
    if best is None: return None
    return (best[1], best[2], best[3], data["pb"].get(best[1]))

def nearest_rankup(pb: dict):
    """PB 기준으로 다음 랭크 칸까지 가장 적게 남은 시나리오 → (서브 이름, key, 목표 점수, 랭크)"""
    cand = None
    for sub in SUBS:
        for k, th in sub[3]:
            x = pb.get(k)
            if x is None: continue
            rank, t, gap = next_rank_gap(x, th)
            if rank is None: continue
            if cand is None or gap < cand[0]: cand = (gap, sub[2], k, t, rank)
    return None if cand is None else cand[1:]

def cond_adjust(cond: dict):
    sl_, fe = cond.get("sleep"), cond.get("feel")
    if sl_ is not None and sl_ < 6: return f"수면 {sl_:g}h — 프로브는 그대로, 본훈련은 블록당 반만"
    if fe is not None and fe <= 3: return f"체감 {fe} — 프로브는 그대로, 본훈련은 블록당 반만"
    return None

def probe_validity(plays, warm=WARM_KEYS, probe=PROBE, max_rep: int = 3):
    """프로브 첫판이 웜업 전이면 ('key','cold'), 프로브를 너무 많이 쳤으면 ('key','extra')"""
    seen_warm = False; counts = {}
    for k, _, _ in plays:
        if k in warm: seen_warm = True
        if k in probe:
            counts[k] = counts.get(k, 0) + 1
            if counts[k] == 1 and not seen_warm: return (k, "cold")
    for k in probe:
        if counts.get(k, 0) > max_rep: return (k, "extra")
    return None

def validity_msg(v, plays) -> str:
    k, kind = v
    if kind == "cold": return f"{sname(k)} 첫판이 웜업 전 — 오늘 측정값은 낮게 나올 수 있어요"
    n = sum(1 for p in plays if p[0] == k)
    return f"{sname(k)} {n}판 — 프로브는 첫 판만 측정, 나머지는 본훈련으로 봅니다"

def session_brief(data: dict, dkey: str, dt: str, plays, extra=None, alt=None):
    """코치 카드 최대 3줄 [(문구, 색 토큰)]. alt 가 있으면(휴식·벤치 요약) 그대로 쓴다"""
    if alt: return alt[:3]
    lines = []
    lp = last_probe_day(data, dkey)
    if lp:
        ser = {p["date"]: p for p in probe_series(data)}.get(lp)
        vi, oi = (ser["vi"], ser["oi"]) if ser else (None, None)
        if vi is not None or oi is not None:
            t = f"어제({int(lp[5:7])}/{int(lp[8:10])}) 지수"
            if vi is not None: t += f" 발로 {vi:+.1f}"
            if oi is not None: t += f" · 옵치 {oi:+.1f}"
            lines.append((t, "sub"))
        else: lines.append(("지수 준비 중 — 프로브 첫판이 4일 쌓이면 어제 컨디션이 여기 뜹니다", "hint"))
    else: lines.append(("첫 프로브를 치면 내일부터 어제 컨디션이 여기 뜹니다", "hint"))
    fp = focus_pick(data, dkey)
    if fp:
        k, x, avg, pb = fp
        lines.append((f"오늘 초점: {sname(k)} — 최근 첫판 평균 {avg:.0f}, 첫판 {avg:.0f} 넘기면 회복 (지난 첫판 {x})", "gold"))
    else:
        nr = nearest_rankup(data["pb"])
        if nr: lines.append((f"가까운 랭크업: {nr[0]} — {sname(nr[1])} {nr[2]}점이면 {nr[3]} 칸", "sub"))
    day = data["days"].get(dkey, {})
    ca = cond_adjust(day.get("cond", {})) if day else None
    if ca: lines.append((ca, "val"))
    elif extra: lines.append((extra, "gold"))
    elif COACH_STATE.get("validity") and dt != "b": lines.append((validity_msg(COACH_STATE["validity"], plays), "hint"))
    return lines[:3]

# ── 기록 탭: 최근 14일 표 · 날짜 상세 · 시작 대비 성장 ──
HIST_COLS = ["날짜", "유형", "판", "분", "프로브", "지수 발/옵", "PB", "죽음", "수면", "체감", "에너지", "✓"]
HIST_W = (9, 4, 4, 4, 5, 11, 3, 8, 5, 3, 5, 3)
DTYPE_SHORT = {"v": "발로", "w": "약점", "b": "벤치", "r": "휴식", "seed": "기준"}

def history_rows(data: dict, upto: str, series, pbd: dict, n: int = 14):
    """upto 부터 거꾸로 n 일 (없는 날도 한 줄, trained=False)"""
    end = date.fromisoformat(upto); ser = {p_["date"]: p_ for p_ in series}
    out = []
    for i in range(n):
        d = end - timedelta(days=i); ds = d.isoformat(); e = data["days"].get(ds)
        seed = ds == SEED_DATE
        dtype = "seed" if seed else ["v", "v", "v", "v", "w", "b", "r"][d.weekday()]
        trained = bool(e) and not seed and bool(e.get("first") or e.get("count"))
        row = {"date": ds, "dow": DOWK[d.weekday()], "dtype": dtype, "trained": trained,
               "plays": sum(e["count"].values()) if e else 0, "minutes": None, "probe": 0, "vi": None, "oi": None,
               "pbs": [] if seed else [k for k, dd in pbd.items() if dd == ds], "deaths": 0, "dom": None, "sleep": None, "feel": None,
               "energy": None, "miyagi": False, "ranked": False}
        if e:
            ss = e.get("sess", {})
            if ss.get("start") and ss.get("end"): row["minutes"] = t_min(ss["end"]) - t_min(ss["start"])
            row["probe"] = sum(1 for k in PROBE if e["first"].get(k) is not None)
            sp = ser.get(ds)
            if sp: row["vi"], row["oi"] = sp["vi"], sp["oi"]
            dd_ = e.get("deaths", {}); tot = sum(int(dd_.get(c, 0) or 0) for c in DEATH_NAMES)
            row["deaths"] = tot
            if tot: row["dom"] = DEATH_NAMES[max(DEATH_NAMES, key=lambda c: int(dd_.get(c, 0) or 0))]
            row["sleep"] = e.get("cond", {}).get("sleep"); row["feel"] = e.get("cond", {}).get("feel") if trained else None
            en, cnt = totalE(e.get("best", {}))
            if cnt == 9: row["energy"] = en
            row["miyagi"] = bool(e.get("checks", {}).get("miyagi")); row["ranked"] = bool(e.get("checks", {}).get("ranked"))
        out.append(row)
    return out

def fmt_history_row(r: dict):
    idx = "—"
    if r["vi"] is not None or r["oi"] is not None:
        idx = (f"{r['vi']:+.1f}" if r["vi"] is not None else "—") + "/" + (f"{r['oi']:+.1f}" if r["oi"] is not None else "—")
    tr = r["trained"] or r["dtype"] == "seed"
    return [f"{r['date'][5:7]}-{r['date'][8:10]} {r['dow']}", DTYPE_SHORT[r["dtype"]],
            str(r["plays"]) if r["trained"] else "·", str(r["minutes"]) if (r["trained"] and r["minutes"] is not None) else ("—" if r["trained"] else "·"),
            f"{r['probe']}/{len(PROBE)}" if r["trained"] else "", idx if r["trained"] else "",
            str(len(r["pbs"])) if r["pbs"] else "", (f"{r['deaths']} {r['dom']}" if r["deaths"] else ""),
            f"{r['sleep']:g}" if r["sleep"] is not None else "—", str(r["feel"]) if r["feel"] is not None else "—",
            str(r["energy"]) if r["energy"] is not None else "", ("M" if r["miyagi"] else "") + ("R" if r["ranked"] else "")]

def day_detail(data: dict, dkey: str):
    e = data["days"].get(dkey, {}); out = []
    for sub in SUBS:
        for k, _ in sub[3]:
            b = e.get("best", {}).get(k)
            out.append((k, e.get("first", {}).get(k), b, e.get("count", {}).get(k, 0), b is not None and b == data["pb"].get(k)))
    return out

def growth_since_seed(data: dict):
    out = []
    for si, sub in enumerate(SUBS):
        for k, th in sub[3]:
            sd_ = SEED[k]; pb = data["pb"].get(k, sd_); gain = pb - sd_
            out.append({"key": k, "seed": sd_, "pb": pb, "gain": gain, "pct": gain / sd_ * 100,
                        "band_seed": rank_of(scenE(sd_, th))[0], "band_pb": rank_of(scenE(pb, th))[0],
                        "stalled": gain <= 0, "idx": si})
    return sorted(out, key=lambda r: (r["stalled"], -r["pct"], r["idx"]))

def energy_delta(data: dict):
    return (totalE(SEED)[0], totalE(data["pb"])[0])

def fmt_growth_row(r: dict):
    return (sname(r["key"]), f"{r['seed']} → {r['pb']}", "정체" if r["stalled"] else f"+{r['pct']:.1f}%",
            f"{r['band_seed']}→{r['band_pb']}" if r["band_seed"] != r["band_pb"] else "")

# ══════════════════ 성장 가시화 (v3.2) ══════════════════
# 왜 필요한가: 한 판 점수는 같은 날 반복 사이에도 2~3%, 날마다 5% 안팎으로 흔들린다.
# 그래서 '7일 평균보다 1점 낮음'을 ▼로 적으면 정상 변동을 하락으로 오해하게 된다.
# 아래는 '평소 범위'를 먼저 구하고, 그 범위를 벗어난 판만 좋음/낮음으로 부르기 위한 계산이다.

def robust_band(vals, k: float = 1.0):
    """반복 점수의 '평소 범위'. 중앙값 ± k·(1.4826·MAD). 판이 4개 미만이면 None(판단 보류).
    표준편차 대신 MAD 를 쓰는 이유: 한 판 크게 튀어도 범위가 흔들리지 않게."""
    v = sorted(x for x in vals if x is not None)
    n = len(v)
    if n < 4: return None
    def med(a):
        m = len(a)
        return a[m // 2] if m % 2 else (a[m // 2 - 1] + a[m // 2]) / 2
    mid = med(v)
    sd = 1.4826 * med(sorted(abs(x - mid) for x in v))
    if sd <= 0: sd = max(1.0, mid * 0.02)          # 전부 같은 값이면 2% 를 폭으로
    return {"mid": mid, "sd": sd, "lo": mid - k * sd, "hi": mid + k * sd, "n": n}

def play_verdict(score, band, pb=None):
    """한 판 판정 → (종류, 문구, 팔레트키). 종류: pb·high·normal·low·new(비교 대상 부족)"""
    if score is None: return ("new", "", "dim")
    if pb is not None and score > pb: return ("pb", "최고", "gold")
    if not band: return ("new", "", "dim")
    if score >= band["hi"]: return ("high", "잘 나옴", "ok")
    if score <= band["lo"]: return ("low", "낮음", "dim")
    return ("normal", "평소", "sub")

def band_z(score, band):
    """평소 범위 기준 위치. 0 = 평소 한가운데, +1 = 범위 위끝. 범위가 없으면 None"""
    if score is None or not band or not band["sd"]: return None
    return (score - band["mid"]) / band["sd"]

def scen_play_pool(data: dict, key: str, end_day: str, n_days: int = 10, include_today: bool = False):
    """최근 n_days 일간 그 시나리오의 '모든 판' 점수 (평소 범위 계산용). 오늘은 기본 제외 —
    오늘 판을 넣으면 오늘이 좋은 날일 때 범위가 같이 올라가 판정이 무뎌진다."""
    end = date.fromisoformat(end_day)
    out = []
    for i in range(0 if include_today else 1, n_days + 1):
        dk = (end - timedelta(days=i)).isoformat()
        if dk == SEED_DATE: continue
        out += [p[2] for p in day_plays(data, dk) if p[0] == key]
    return out

def scen_day_band(data: dict, key: str, end_day: str, field: str = "best", n_days: int = 14):
    """어제까지 '그날 베스트'(또는 그날 첫 판)들의 평소 범위. 줄에 뜨는 값은 하루치 대표값이라
    판 단위 범위(scen_band)로 재면 좁아서 늘 벗어난다."""
    def calc():
        end = date.fromisoformat(end_day); vals = []
        for i in range(1, n_days + 1):
            dk = (end - timedelta(days=i)).isoformat()
            if dk == SEED_DATE: continue
            v = data["days"].get(dk, {}).get(field, {}).get(key)
            if v is not None: vals.append(v)
        return robust_band(vals)
    return memo(("dayband", key, end_day, field, n_days), calc)

def scen_band(data: dict, key: str, end_day: str):
    """그 시나리오의 평소 범위 (기록 버전 안에서 한 번만 계산)"""
    return memo(("band", key, end_day), lambda: robust_band(scen_play_pool(data, key, end_day)))

def day_dots(data: dict, key: str, end_day: str, n_days: int = 14):
    """점 하나 = 한 판. [(날짜순번 0..n-1, 그날 판 순번, 점수)] — 첫날부터 그릴 수 있는 조밀한 그림용"""
    end = date.fromisoformat(end_day); out = []
    for i in range(n_days):
        dk = (end - timedelta(days=n_days - 1 - i)).isoformat()
        if dk == SEED_DATE: continue
        for j, p in enumerate(x for x in day_plays(data, dk) if x[0] == key):
            out.append((i, j, p[2]))
    return out

def sub_shape(scores: dict, base: dict = None):
    """9개 서브카테고리 에너지와 기준 대비 차이 — 총점 하나가 아니라 '어디가 어떻게'를 보여주기 위한 것"""
    out = []
    for s_ in SUBS:
        e = subE(s_, scores or {}); b = subE(s_, base) if base else None
        out.append({"id": s_[0], "cat": s_[1], "sub": s_[2], "e": e, "base": b,
                    "delta": (e - b) if (e is not None and b is not None) else None})
    return out

def within_day_gain(plays):
    """오늘 3판 이상 친 시나리오에서 (뒤 절반 평균 - 앞 절반 평균) / 앞 절반 평균 × 100 의 중앙값.
    웜업이 실제로 먹혔는지를 그날 안에서만 보는 값 — 날짜 간 노이즈를 타지 않는다. 대상 없으면 None"""
    by = {}
    for k, _t, sc in plays: by.setdefault(k, []).append(sc)
    rates = []
    for k, v in by.items():
        if len(v) < 3: continue
        h = len(v) // 2
        a = sum(v[:h]) / h; b = sum(v[-h:]) / h
        if a > 0: rates.append((b - a) / a * 100)
    if not rates: return None
    rates.sort(); m = len(rates)
    return rates[m // 2] if m % 2 else (rates[m // 2 - 1] + rates[m // 2]) / 2

# ── 훈련 레벨: 실력이 제자리인 날에도 '한 일'은 남는다는 걸 보이게 하는 값 ──
#    점수가 아니라 '친 판 수 + 신기록'에서만 오른다. 앱을 켜 두는 것만으로는 1점도 오르지 않는다.
LEVELS = [(0, "입문"), (30, "수련"), (80, "훈련병"), (160, "정조준"), (280, "견습 사수"), (440, "숙련 사수"),
          (660, "정예 사수"), (950, "저격수"), (1320, "명사수"), (1800, "달인"), (2400, "장인")]

def total_pbs(data: dict) -> int:
    """누적 신기록 횟수. 기준값(SEED)은 출발선이라 세지 않는다"""
    best = dict(data["days"].get(SEED_DATE, {}).get("best", {})); n = 0
    for d in sorted(data["days"]):
        if d == SEED_DATE: continue
        for k, v in sorted(data["days"][d].get("best", {}).items()):
            if v is not None and v > best.get(k, 0): n += 1; best[k] = v
    return n

def total_xp(data: dict) -> int:
    """친 판 1점 + 신기록 5점"""
    plays = sum(len(e.get("plays") or []) for d, e in data["days"].items() if d != SEED_DATE)
    if not plays:                                    # 옛 파일엔 판별 기록이 없다 — 그날 판 수 합으로
        plays = sum(sum((e.get("count") or {}).values()) for d, e in data["days"].items() if d != SEED_DATE)
    return plays + 5 * total_pbs(data)

def level_of(xp: int):
    """(레벨, 이름, 이번 레벨 시작 xp, 다음 레벨 xp 또는 None)"""
    i = 0
    for j, (t, _) in enumerate(LEVELS):
        if xp >= t: i = j
    return (i + 1, LEVELS[i][1], LEVELS[i][0], LEVELS[i + 1][0] if i + 1 < len(LEVELS) else None)

def fmt_level(xp: int) -> str:
    lv, name, lo, hi = level_of(xp)
    return f"Lv.{lv} {name}" + (f"  {xp - lo}/{hi - lo}" if hi else f"  {xp}")

def level_frac(xp: int) -> float:
    _lv, _n, lo, hi = level_of(xp)
    return 1.0 if not hi else max(0.0, min(1.0, (xp - lo) / (hi - lo)))

def play_base(data: dict, key: str, dkey: str):
    """그 시나리오의 '평소 값' 기준선. 판 단위 평소 범위 → 어제까지 베스트 평균 → 기준값(SEED) 순으로 물러난다.
    1일차에도 반드시 하나는 나오게 (그래야 첫날부터 그릴 게 생긴다)"""
    b = scen_band(data, key, dkey)
    if b: return b["mid"]
    avg, _ = recent_stats(data, key, dkey, "best")
    if avg: return avg
    return SEED.get(key)

def session_points(data: dict, dkey: str, plays=None):
    """오늘 판마다 (순번, 시나리오, 점수, 평소 대비 %, 판정). 첫날부터 27개 점이 찍힌다"""
    plays = day_plays(data, dkey) if plays is None else plays
    pb = pb_before_day(data, dkey); out = []
    for i, (k, _t, sc) in enumerate(plays):
        base = play_base(data, k, dkey)
        pct = ((sc - base) / base * 100) if base else None
        kind = play_verdict(sc, scen_band(data, k, dkey), pb.get(k))[0]
        out.append((i, k, sc, pct, kind))
        if sc > pb.get(k, 0): pb[k] = sc
    return out

def session_caption(pts, gain) -> str:
    """세션 곡선 밑 한 줄 — 오늘 안에서만 확인되는 사실만 적는다 (날짜 간 노이즈를 타지 않게)"""
    have = [p[3] for p in pts if p[3] is not None]
    if not have: return "판이 들어오면 여기에 한 판씩 점이 찍힙니다"
    parts = [f"{len(pts)}판"]
    m = sorted(have)[len(have) // 2]
    parts.append(f"평소 대비 중앙 {m:+.1f}%")
    if gain is not None: parts.append(f"세션 중 상승 {gain:+.1f}% (앞 절반 → 뒤 절반)")
    n_pb = sum(1 for p in pts if p[4] == "pb")
    if n_pb: parts.append(f"신기록 {n_pb}")
    return " · ".join(parts)

def day_changes(data: dict, dkey: str, max_n: int = 6):
    """오늘 실제로 달라진 것만. 전부 기록 파일에서 확인되는 사실이고, 없으면 빈 목록을 돌려준다
    (없는 날 억지로 문장을 만들면 있는 날의 말이 같이 싸구려가 된다)"""
    day = data["days"].get(dkey) or blank_day()
    prev = pb_before_day(data, dkey)
    best = day.get("best") or {}
    out = []
    for k, v in sorted(best.items(), key=lambda kv: -(kv[1] - prev.get(kv[0], 0))):
        old = prev.get(k)
        if v is None or old is None or v <= old: continue
        line = f"{sname(k)} {v} 신기록 (+{v - old})"
        th = th_of(k)
        if th:
            r_old = sum(1 for t in th if old >= t); r_new = sum(1 for t in th if v >= t)
            if r_new > r_old: line += f" · {RANK_NAMES[r_new - 1]} 칸 진입"
        out.append(line)
    if len(out) < max_n:                       # 신기록은 아니지만 최근 14일 중 가장 높은 값
        for k, v in sorted(best.items()):
            if v is None or (prev.get(k) is not None and v > prev[k]): continue
            b = scen_day_band(data, k, dkey)
            hi = max((data["days"].get((date.fromisoformat(dkey) - timedelta(days=i)).isoformat(), {}).get("best", {}).get(k)
                      for i in range(1, 15)), key=lambda x: (x is not None, x), default=None)
            if hi is not None and v > hi:
                out.append(f"{sname(k)} {v} — 최근 14일 중 가장 높음")
            if len(out) >= max_n: break
    e_now, _ = totalE(data["pb"]); e_old, _ = totalE(prev)
    if e_now is not None and e_old is not None and e_now > e_old:
        out.append(f"총 에너지 {e_old} → {e_now} (+{e_now - e_old})")
    return out[:max_n]

def session_card(data: dict, dkey: str, day_name: str, theme_name: str = "", plays=None):
    """마감 카드 내용. 그리는 쪽은 이 값만 받아 쓴다 (테스트가 화면 없이 돌게)"""
    plays = day_plays(data, dkey) if plays is None else plays
    d = date.fromisoformat(dkey)
    kinds = [k for _, _, k in day_verdicts(data, dkey, plays)]
    ss = session_summary(plays, {})
    stat = [f"{len(plays)}판"]
    if ss["n"] and ss["minutes"] is not None: stat.append(f"{ss['minutes']}분")
    c = ribbon_counts(kinds)
    for kk in ("pb", "high", "normal", "low"):
        if c[kk]: stat.append(f"{VERDICT_NAME[kk]} {c[kk]}")
    head = f"{d.month}월 {d.day}일 {DOWK[d.weekday()]} · {day_name}" + (f" · {theme_name}" if theme_name else "")
    g = within_day_gain(plays)
    return {"title": head, "kinds": kinds, "stat": " · ".join(stat),
            "changed": day_changes(data, dkey), "gain": (f"세션 중 {g:+.1f}% (앞 절반 → 뒤 절반)" if g is not None else ""),
            "next": theme_line(dkey, data.get("pb")).split(" · ")[-1] if theme_line(dkey, data.get("pb")) else ""}

# ── 오늘의 띠: 계획한 판을 칸으로 깔고, 끝난 판을 판정 색으로 채운다 ──
VERDICT_FILL = {"pb": "gold", "high": "ok", "normal": "sub", "low": "dim", "new": "sub"}
# 색만으로 구분하면 영상 압축(4:2:0)에서 뭉갠다. 칸 높이로도 같은 정보를 실어 밝기·모양 둘 다로 읽히게 한다.
RIBBON_H = {"gold": 1.0, "ok": 0.78, "sub": 0.56, "dim": 0.36, "todo": 0.20}
VERDICT_NAME = {"pb": "최고", "high": "잘 나옴", "normal": "평소", "low": "낮음", "new": "첫 기록"}

def pb_before_day(data: dict, dkey: str) -> dict:
    """그날 이전까지의 시나리오별 최고 기록. '그 판이 칠 때 신기록이었나'를 보려면 오늘이 빠진 값이 필요하다"""
    out = {}
    for d in sorted(data["days"]):
        if d >= dkey: continue
        for k, v in data["days"][d]["best"].items():
            if v is not None and v > out.get(k, 0): out[k] = v
    return out

def day_verdicts(data: dict, dkey: str, plays=None):
    """오늘 친 판마다 (시나리오, 점수, 판정) — 시간순.
    신기록은 '그 판 직전'까지의 최고와 견주고, 평소 범위는 어제까지의 판들로 잡는다."""
    plays = day_plays(data, dkey) if plays is None else plays
    pb = pb_before_day(data, dkey); out = []
    for k, _t, sc in plays:
        kind = play_verdict(sc, scen_band(data, k, dkey), pb.get(k))[0]
        out.append((k, sc, kind))
        if sc > pb.get(k, 0): pb[k] = sc
    return out

def ribbon_cells(plan_n: int, kinds):
    """띠 각 칸의 팔레트 키. 계획보다 더 치면 칸이 늘어난다 ('todo' = 아직 안 친 칸)"""
    n = max(int(plan_n or 0), len(kinds))
    return [(VERDICT_FILL.get(kinds[i], "sub") if i < len(kinds) else "todo") for i in range(n)]

def ribbon_counts(kinds) -> dict:
    out = {k: 0 for k in VERDICT_NAME}
    for k in kinds: out[k] = out.get(k, 0) + 1
    return out

def fmt_ribbon(plan_n: int, kinds) -> str:
    """띠 밑 한 줄. 판정 개수만 적는다 — '7일 평균 대비 ▼5%' 같은 표현은 정상 변동을 하락으로 읽게 만든다"""
    n = len(kinds)
    if not n: return f"오늘 0/{plan_n}판 — 한 판만 쳐도 여기가 채워집니다" if plan_n else "오늘 0판"
    c = ribbon_counts(kinds)
    parts = [f"오늘 {n}/{max(plan_n, n)}판"]
    for k in ("pb", "high", "normal", "low"):
        if c[k]: parts.append(f"{VERDICT_NAME[k]} {c[k]}")
    return " · ".join(parts)

# ── 단축키 ──
def shortcut_action(keysym: str, state: int, in_entry: bool):
    ctrl = bool(state & 0x4)
    if keysym == "F5": return "rescan"
    if keysym == "Escape": return "dismiss"
    if in_entry and not ctrl: return None
    if ctrl and keysym.lower() == "o": return "folder"
    if ctrl and keysym.lower() == "r": return "run"
    if in_entry: return None
    return {"1": "tab:today", "2": "tab:grow", "3": "tab:bench", "4": "tab:log"}.get(keysym)

def seq_shortcut_action(keysym: str, state: int, in_entry: bool):
    ctrl = bool(state & 0x4)
    if keysym == "Escape": return "blur" if in_entry else "close"
    if ctrl and keysym.lower() == "n": return "skip"
    if ctrl and keysym.lower() == "r": return "resend"
    if in_entry or ctrl: return None
    return "auto" if keysym == "space" else None

# ── 정체 감지 (성장 탭 스파크 태그) ──
def trend_pct(vals):
    return _slope_pct(list(enumerate(vals))) if len(vals) >= 4 else None

def plateau(vals, n: int = 10, flat_pct: float = 0.3, range_pct: float = 6.0) -> bool:
    v = list(vals)[-n:]
    if len(v) < n: return False
    tp = trend_pct(v); m = sum(v) / len(v)
    return tp is not None and abs(tp) < flat_pct and m > 0 and (max(v) - min(v)) / m * 100 < range_pct

def spark_tag(vals) -> str:
    if plateau(vals): return "최근 10판 제자리"
    tp = trend_pct(vals)
    if tp is None: return ""
    return "↗" if tp >= 0.5 else "↘" if tp <= -0.5 else ""

# ── 세션 마무리: 다음 한 걸음 ──
def routine_complete(day: dict, dt: str) -> bool:
    if dt == "b": return all(day.get("best", {}).get(k) is not None for k in SCEN)
    if dt not in ("v", "w"): return False
    main = MAIN if dt == "v" else FRIDAY
    return (all(day.get("count", {}).get(k, 0) >= n for k, n in WARMUP + main)
            and all(day.get("first", {}).get(k) is not None for k in PROBE))

def next_step(data: dict, dkey: str, plays, avg: dict) -> str:
    day = data["days"].get(dkey, {})
    worst = None
    for k in PROBE:
        x = day.get("first", {}).get(k)
        a = avg.get(k)
        if x is None or not a: continue
        r = x / a - 1
        if r <= -0.03 and (worst is None or r < worst[0]): worst = (r, k, x, a)
    if worst: return f"내일: {sname(worst[1])} 첫판 {worst[3]:.0f} 넘기기 (오늘 {worst[2]})"
    seq = [p[0] for p in plays]
    for k, s_, e_ in blocks_of(seq):
        if e_ - s_ >= 4 and k not in WARM_KEYS:
            bt = block_trend([(i, plays[i][2]) for i in range(s_, e_)])
            if bt and bt[0] == "↘": return f"내일: {sname(k)} {e_ - s_}→{e_ - s_ - 2}판, 4판째 '다음 판 ▶'"
    nr = nearest_rankup(data["pb"])
    if nr: return f"다음: {nr[0]} — {sname(nr[1])} {nr[2]}점이면 {nr[3]}"
    return "내일도 프로브부터"

# ── 벤치마크 준비도 (금요일 예고 · 토요일 라이브) ──
def week_of(dkey: str):
    d = date.fromisoformat(dkey); mon = d - timedelta(days=d.weekday())
    return [(mon + timedelta(days=i)).isoformat() for i in range((d - mon).days + 1)]

def week_pbs(data: dict, dkey: str):
    wk = week_of(dkey); out = []
    for k in SCEN:
        vals = [data["days"].get(d, {}).get("best", {}).get(k) for d in wk]
        vals = [v for v in vals if v is not None]
        if not vals: continue
        _, pmax = recent_stats(data, k, wk[0])
        if pmax is None or max(vals) > pmax: out.append(k)
    return out

def projected_energy(pb: dict, today_best: dict):
    return totalE({**pb, **today_best})

def bench_readiness(data: dict, dkey: str) -> dict:
    e_pb, _ = totalE(data["pb"]); bd = bench_days(data)
    tb = data["days"].get(dkey, {}).get("best", {})
    return {"e_pb": e_pb, "rank": rank_of(e_pb)[0], "last_run": bd[-1] if bd else None,
            "week_pbs": week_pbs(data, dkey), "closest": nearest_rankup(data["pb"]),
            "projected": projected_energy(data["pb"], tb)[0], "n_today": sum(1 for k in SCEN if tb.get(k) is not None)}

def bench_lines(r: dict, dt: str):
    out = []
    if dt == "w":
        lr = f"지난 풀런 {r['last_run'][1]} ({r['last_run'][0][5:7]}-{r['last_run'][0][8:10]})" if r["last_run"] else "지난 풀런 없음"
        names = ", ".join(sname(k) for k in r["week_pbs"][:4]) + ("…" if len(r["week_pbs"]) > 4 else "")
        out.append((f"내일 벤치: {lr} · 이번 주 PB {len(r['week_pbs'])}개" + (f": {names}" if names else ""), "sub"))
        if r["closest"]: out.append((f"가까운 랭크업: {r['closest'][0]} — {sname(r['closest'][1])} {r['closest'][2]}점이면 {r['closest'][3]} 칸", "gold"))
    elif dt == "b":
        t = f"{r['n_today']}/18 · 예상 {r['projected']} (빈 칸은 PB)"
        nxt = next((n for th_, n, _ in sorted(RANKS) if r["projected"] is not None and r["projected"] < th_), None)
        if nxt:
            need = next(th_ for th_, n, _ in sorted(RANKS) if n == nxt) - r["projected"]
            t += f" · {nxt}까지 {need}"
        out.append((t, "gold" if r["n_today"] else "sub"))
    return out

# ── 주간 리캡 (일요일) ──
def sleep_effect(data: dict, min_n: int = 5):
    hi, lo = [], []
    for p_ in probe_series(data):
        e = data["days"].get(p_["date"], {}); sl_ = e.get("cond", {}).get("sleep")
        vals = [v for v in (p_["vi"], p_["oi"]) if v is not None]
        if sl_ is None or not vals: continue
        (hi if sl_ >= 7 else lo).append(sum(vals) / len(vals))
    a = sum(hi) / len(hi) if hi else None; b = sum(lo) / len(lo) if lo else None
    return (a, b, len(hi), len(lo)) if (len(hi) >= min_n and len(lo) >= min_n) else (None, None, len(hi), len(lo))

def weekly_recap(data: dict, dkey: str):
    wk = [d for d in week_of(dkey) if d < dkey]
    days = [data["days"][d] for d in wk if d in data["days"] and (data["days"][d].get("first") or data["days"][d].get("count"))]
    if not days: return [("이번 주 기록 없음", "sub")]
    plays = sum(sum(e["count"].values()) for e in days)
    out = [(f"이번 주 {len(days)}일 · {plays}판 · PB {len(week_pbs(data, dkey))}개", "sub")]
    ser = probe_series(data)
    if len(ser) >= 2:
        last = ser[-1]; prev = next((p_ for p_ in reversed(ser) if p_["date"] <= (date.fromisoformat(last["date"]) - timedelta(days=7)).isoformat()), None)
        f = lambda v: "—" if v is None else f"{v:+.1f}"
        if prev: out.append((f"지수 7일선 발로 {f(prev['maV'])}→{f(last['maV'])} · 옵치 {f(prev['maO'])}→{f(last['maO'])}", "sub"))
    a, b, n1, n2 = sleep_effect(data)
    if a is not None: out.append((f"수면 7h 이상 {n1}일 지수 {a:+.1f} · 미만 {n2}일 {b:+.1f}", "gold" if a > b else "sub"))
    else: out.append((f"수면 입력 {n1 + n2}일 — 10일부터 관계가 보입니다", "hint"))
    return out[:3]

# ── 순서창: 높이 · 자동 스크롤 · 간단히 보기 ──
def seq_window_height(req_h: int, avail_h: int) -> int:
    return max(px(120), min(req_h, int(avail_h * 0.75)))

def scroll_to_show(row_y: int, row_h: int, content_h: int, view_h: int, cur_frac: float, context_rows: int = 2) -> float:
    """현재 줄이 보이는 띠 안이면 그대로, 아니면 위에 두 줄 여유를 두고 보이게 하는 yview 비율"""
    if content_h <= view_h or content_h <= 0: return 0.0
    top = cur_frac * content_h
    if top <= row_y and row_y + row_h <= top + view_h: return cur_frac
    want = max(0, row_y - context_rows * row_h)
    return min(want / content_h, (content_h - view_h) / content_h)

def visible_rows(done, nxt, skipped, compact: bool, keep_done: int = 2, ahead: int = 4):
    """간단히 모드: 끝난 줄은 마지막 keep_done 개만, 앞으로 칠 줄은 ahead 개만 보인다 → (보이는 인덱스, 숨긴 완료 수, 숨긴 남은 수)"""
    n = len(done)
    if not compact: return list(range(n)), 0, 0
    cur = nxt if nxt is not None else n
    done_idx = [i for i in range(cur) if done[i]]
    show = set(done_idx[-keep_done:]) if keep_done else set()
    hidden_done = len(done_idx) - len(show) + sum(1 for i in range(cur, n) if done[i])   # 커서 뒤에 끝난 줄도 숨김으로 센다
    upcoming = [i for i in range(cur, n) if not done[i]]
    show.update(upcoming[:ahead + 1]); hidden_ahead = max(0, len(upcoming) - ahead - 1)     # 현재 판 + 다음 ahead 판
    return sorted(show), hidden_done, hidden_ahead

# ── 시나리오 상세 ──
def scen_history(data: dict, key: str, end_day: str, n: int = 30):
    out = []
    for d in sorted(data["days"]):
        if d > end_day: continue
        e = data["days"][d]
        b, f, c = e.get("best", {}).get(key), e.get("first", {}).get(key), e.get("count", {}).get(key, 0)
        if b is None and f is None: continue
        out.append({"date": d, "first": f, "best": b, "count": c})
    return out[-n:]

def scen_summary(data: dict, key: str, dkey: str) -> dict:
    hist = scen_history(data, key, dkey)
    e = data["days"].get(dkey, {})
    avg7b, _ = recent_stats(data, key, dkey); avg7f, _ = recent_stats(data, key, dkey, "first")
    th = th_of(key); pb = data["pb"].get(key)
    bests = [h["best"] for h in hist if h["best"] is not None and h["date"] != dkey]
    trend = None
    if len(bests) >= 6:
        a, b = bests[-7:], bests[-14:-7]
        if len(a) >= 3 and len(b) >= 3: trend = sum(a) / len(a) - sum(b) / len(b)
    return {"pb": pb, "pb_date": pb_days(data).get(key), "avg7_best": avg7b, "avg7_first": avg7f,
            "today_first": e.get("first", {}).get(key), "today_best": e.get("best", {}).get(key), "today_count": e.get("count", {}).get(key, 0),
            "gap": next_rank_gap(pb, th) if (pb is not None and th) else None, "trend": trend, "hist": hist}

def fmt_scen_summary(sm: dict) -> str:
    parts = []
    if sm["pb"] is not None: parts.append(f"PB {sm['pb']}" + (f" ({sm['pb_date'][5:].replace('-', '/')})" if sm["pb_date"] else ""))
    if sm["avg7_best"] is not None: parts.append(f"7일 평균 {sm['avg7_best']:.0f}")
    if sm["today_count"]: parts.append(f"오늘 {sm['today_count']}판 · 베스트 {sm['today_best']}")
    if sm["gap"]: parts.append(f"{sm['gap'][0]}까지 +{sm['gap'][2]}" if sm["gap"][0] else "Gold 칸 ✓")
    if sm["trend"] is not None: parts.append(f"최근 7일 {'▲' if sm['trend'] >= 0 else '▼'}{abs(sm['trend']):.0f}")
    return " · ".join(parts)

# ══════════════════ 플레이리스트 자동 설치 / 실행 ══════════════════
def _pl(name, items, tpl=None):
    """플레이리스트 JSON 객체. tpl(코박스가 만든 다른 플레이리스트)이 있으면 그 키 구성을 그대로 두고 이름·목록만 바꾼다"""
    obj = dict(tpl) if isinstance(tpl, dict) else {}
    obj.update({"playlistName": name, "playlistId": 0, "authorSteamId": "",
                "authorName": "aimdesk", "scenarioList":
                [{"scenario_Name": SCEN[k][0], "play_Count": c} for k, c in items],
                "description": "", "hasOfflineScenarios": False,
                "hasEdited": True, "shareCode": ""})
    return obj

def _pl_template(d: Path):
    """폴더에 코박스가 만든 다른 플레이리스트가 있으면 (그 객체, 인코딩, CRLF 여부) — 게임 버전별 파일 형식 차이를 그대로 따라가기 위해. 없으면 (None, 'utf-16', True)"""
    for fp in sorted(d.glob("*.json")):
        if fp.stem.startswith("AIMDESK"): continue
        try:
            raw = fp.read_bytes()
            enc = "utf-16" if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else ("utf-8-sig" if raw[:3] == b"\xef\xbb\xbf" else "utf-8")
            txt = raw.decode(enc); obj = json.loads(txt)
            if isinstance(obj, dict) and "scenarioList" in obj: return obj, enc, ("\r\n" in txt)
        except Exception:
            continue
    return None, "utf-16", True

def _pl_bytes(obj, enc="utf-16", crlf=True) -> bytes:
    txt = json.dumps(obj, ensure_ascii=False, indent="\t")
    if crlf: txt = txt.replace("\n", "\r\n")
    return (txt + ("\r\n" if crlf else "\n")).encode(enc)

PL_STATE = {"n": 0, "dir": None, "wrote": 0, "tpl": None, "enc": "utf-16"}

BENCH = [(k, 1) for s in SUBS for k, _ in s[3]]          # 토요일 벤치 18개 — 볼테익 표 순서 그대로
def playlists_for(dkey: str, pb: dict = None):
    """그날 설치할 플레이리스트 4개. 'AIMDESK Day' 의 본훈련만 날마다 달라진다."""
    return [("AIMDESK Day",    WARMUP + [(k, 1) for k in PROBE] + list(main_theme(dkey, pb)[3])),
            ("AIMDESK Friday", WARMUP + [(k, 1) for k in PROBE] + FRIDAY),
            ("AIMDESK Probe",  [(k, 1) for k in PROBE]),
            ("AIMDESK Bench",  BENCH)]

def playlists_dir(stats_dir):
    r"""...\FPSAimTrainer\stats -> ...\FPSAimTrainer\Saved\SaveGames\Playlists"""
    p = Path(stats_dir)
    return p.parent / "Saved" / "SaveGames" / "Playlists"

def ensure_playlists(stats_dir, dkey: str = None, pb: dict = None):
    """플레이리스트 JSON 을 코박스 폴더(…\\Saved\\SaveGames\\Playlists)에 설치. (성공 개수, 폴더, 이번에 새로 쓴 개수) 반환.
    폴더에 코박스가 만든 플레이리스트가 있으면 그 파일의 인코딩·키 구성을 그대로 따른다 (없으면 UTF-16 BOM + CRLF)"""
    try:
        d = playlists_dir(stats_dir)
        if not d.is_dir():
            try: d.mkdir(parents=True)      # 로컬 플레이리스트를 한 번도 안 만든 설치본
            except OSError: return 0, d, 0
        tpl, enc, crlf = _pl_template(d)
        ok = wrote = 0
        for name, items in playlists_for(dkey or today_date().isoformat(), pb):
            payload = _pl_bytes(_pl(name, items, tpl), enc, crlf)
            fp = d / (name + ".json")
            try:
                if not fp.exists() or fp.read_bytes() != payload:
                    fp.write_bytes(payload); wrote += 1
                ok += 1
            except OSError: pass
        PL_STATE.update(n=ok, dir=d, wrote=wrote, tpl=(tpl or {}).get("playlistName"), enc=enc)
        return ok, d, wrote
    except Exception:
        log_exc("ensure_playlists"); return 0, None, 0

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
STALL_SEC = 100          # 60초 시나리오를 보낸 뒤 이 시간이 지나도 기록이 없으면 FREEPLAY 의심 (게임이 이미 켜져 있던 경우)
STALL_SEC_LAUNCH = 240   # 딥링크로 게임을 새로 켠 경우 — 스팀·로딩 시간까지 감안

def scenario_uri(name: str) -> str:
    """코박스 공식 딥링크(3.0.0+, 공백은 %20): 게임이 꺼져 있으면 켜서, 켜져 있으면 그 자리에서 해당 시나리오를 바로 시작"""
    return "steam://run/824270/?action=jump-to-scenario;name=" + name.replace(" ", "%20")

def launch_scenario(key: str) -> bool:
    return open_uri(scenario_uri(SCEN[key][0]))

# ── 플레이리스트 NEXT 키 자동 입력 (렉 없는 진행 방식) ──
KOVAAKS_INPUT_INI = Path(os.environ.get("LOCALAPPDATA", "")) / "FPSAimTrainer" / "Saved" / "Config" / "WindowsNoEditor" / "Input.ini"
_NEXT_RE = re.compile(r'^\s*([+-]?)ActionMappings=\(ActionName="PlaylistNext"([^)]*)\)', re.M)
_KEY_RE = re.compile(r'Key=(\w+)'); _MOD_RE = re.compile(r'b(Shift|Ctrl|Alt|Cmd)=True')

def parse_next_key(txt: str):
    """Input.ini 본문 → (PlaylistNext 키, 이유). 언리얼 Saved/Config 의 Input.ini 는 '-줄'로 기본값을 지우고 '+줄'로 새 키를 넣는다 —
    그래서 '-줄'은 무시하고 '+줄'(또는 부호 없는 줄) 중 마지막 것을 쓴다. 이유: None(찾음) · 'removed'(지워졌거나 None) · 'none'(항목 없음)"""
    ents = []
    for m in _NEXT_RE.finditer(txt or ""):
        km = _KEY_RE.search(m.group(2))
        ents.append((m.group(1), km.group(1) if km else "None", bool(_MOD_RE.search(m.group(2)))))
    adds = [(k, mod) for sign, k, mod in ents if sign != "-" and k != "None"]
    if adds:
        k, mod = adds[-1]
        return (None, "chord") if mod else (k, None)
    return None, ("removed" if ents else "none")

_INI_CACHE = {"sig": None, "key": None, "why": "nofile"}

def playlist_next_key():
    """코박스 Input.ini에서 PlaylistNext에 묶인 키 이름. 미지정/파일 없음이면 None (파일이 안 바뀌면 캐시). 이유는 _INI_CACHE['why']"""
    try:
        st = KOVAAKS_INPUT_INI.stat(); sig = (st.st_mtime_ns, st.st_size)
    except OSError:
        _INI_CACHE.update(sig=None, key=None, why="nofile"); return None
    if _INI_CACHE["sig"] == sig: return _INI_CACHE["key"]
    try:
        raw = KOVAAKS_INPUT_INI.read_bytes()
    except OSError:
        _INI_CACHE.update(sig=None, key=None, why="unreadable"); return None
    txt = None
    for enc in ("utf-8-sig", "utf-16", "cp1252"):
        try: txt = raw.decode(enc); break
        except UnicodeDecodeError: pass
    key, why = parse_next_key(txt or "")
    _INI_CACHE.update(sig=sig, key=key, why=why)
    return key

def ini_why():
    return _INI_CACHE.get("why")

_VK = {"SpaceBar":0x20,"Enter":0x0D,"Tab":0x09,"Escape":0x1B,"BackSpace":0x08,"Insert":0x2D,"Delete":0x2E,"Home":0x24,"End":0x23,
       "PageUp":0x21,"PageDown":0x22,"Left":0x25,"Up":0x26,"Right":0x27,"Down":0x28,"CapsLock":0x14,"Pause":0x13,"ScrollLock":0x91,
       "NumLock":0x90,"Multiply":0x6A,"Add":0x6B,"Subtract":0x6D,"Decimal":0x6E,"Divide":0x6F,"Tilde":0xC0,"Semicolon":0xBA,
       "Equals":0xBB,"Comma":0xBC,"Hyphen":0xBD,"Period":0xBE,"Slash":0xBF,"LeftBracket":0xDB,"Backslash":0xDC,"RightBracket":0xDD,
       "Apostrophe":0xDE}
_DIGITS = ["Zero","One","Two","Three","Four","Five","Six","Seven","Eight","Nine"]
_EXTENDED = {"Insert","Delete","Home","End","PageUp","PageDown","Left","Up","Right","Down","Divide","NumLock"}
# 마우스 버튼: (누름 플래그, 뗌 플래그, XBUTTON 번호) — SendInput MOUSEINPUT
_MOUSE = {"LeftMouseButton": (0x0002, 0x0004, 0), "RightMouseButton": (0x0008, 0x0010, 0), "MiddleMouseButton": (0x0020, 0x0040, 0),
          "ThumbMouseButton": (0x0080, 0x0100, 1), "ThumbMouseButton2": (0x0080, 0x0100, 2)}
_KEY_KO = {"Add": "넘패드 +", "Subtract": "넘패드 -", "Multiply": "넘패드 *", "Divide": "넘패드 /", "Decimal": "넘패드 .",
           "SpaceBar": "스페이스", "Enter": "엔터", "Escape": "Esc", "BackSpace": "백스페이스", "Tilde": "` 물결", "Hyphen": "- 빼기",
           "Equals": "= 등호", "Semicolon": "; 세미콜론", "Apostrophe": "' 따옴표", "Comma": ", 쉼표", "Period": ". 마침표", "Slash": "/ 슬래시",
           "Backslash": "\\ 역슬래시", "LeftBracket": "[ 대괄호", "RightBracket": "] 대괄호", "PageUp": "Page Up", "PageDown": "Page Down",
           "CapsLock": "Caps Lock", "NumLock": "Num Lock", "ScrollLock": "Scroll Lock",
           "LeftMouseButton": "마우스 왼쪽", "RightMouseButton": "마우스 오른쪽", "MiddleMouseButton": "마우스 휠 클릭",
           "ThumbMouseButton": "마우스 엄지 1", "ThumbMouseButton2": "마우스 엄지 2"}

def key_label(name):
    """언리얼 키 이름을 사람이 읽는 표기로: Add → 'Add (넘패드 +)', NumPadFive → 'NumPadFive (넘패드 5)'"""
    if not name: return ""
    ko = _KEY_KO.get(name)
    if ko is None and name.startswith("NumPad") and name[6:] in _DIGITS: ko = f"넘패드 {_DIGITS.index(name[6:])}"
    elif ko is None and name in _DIGITS: ko = f"숫자 {_DIGITS.index(name)}"
    return f"{name} ({ko})" if ko else name

_KEY_ALIAS = {"space": "SpaceBar", "spacebar": "SpaceBar", "스페이스": "SpaceBar", "enter": "Enter", "return": "Enter", "엔터": "Enter",
              "tab": "Tab", "탭": "Tab", "esc": "Escape", "escape": "Escape", "backspace": "BackSpace", "bs": "BackSpace",
              "ins": "Insert", "insert": "Insert", "del": "Delete", "delete": "Delete", "home": "Home", "end": "End",
              "pgup": "PageUp", "pageup": "PageUp", "pgdn": "PageDown", "pagedown": "PageDown",
              "left": "Left", "up": "Up", "right": "Right", "down": "Down", "←": "Left", "↑": "Up", "→": "Right", "↓": "Down",
              "capslock": "CapsLock", "caps": "CapsLock", "pause": "Pause", "scrolllock": "ScrollLock", "numlock": "NumLock",
              "+": "Add", "plus": "Add", "num+": "Add", "numpad+": "Add", "numpadplus": "Add", "넘패드+": "Add",
              "*": "Multiply", "num*": "Multiply", "numpad*": "Multiply", "num-": "Subtract", "numpad-": "Subtract", "넘패드-": "Subtract",
              "num.": "Decimal", "numpad.": "Decimal", "num/": "Divide", "numpad/": "Divide",
              "-": "Hyphen", "minus": "Hyphen", "=": "Equals", ",": "Comma", ".": "Period", "/": "Slash",
              "`": "Tilde", "~": "Tilde", ";": "Semicolon", "[": "LeftBracket", "]": "RightBracket", "\\": "Backslash", "'": "Apostrophe",
              "numpadenter": "Enter", "numenter": "Enter", "kpenter": "Enter", "pagedn": "PageDown", "pgdown": "PageDown", "pageup": "PageUp",
              "numpadadd": "Add", "kp+": "Add", "numpadsubtract": "Subtract", "kp-": "Subtract", "numpadmultiply": "Multiply", "numpaddivide": "Divide", "numpaddecimal": "Decimal",
              "lmb": "LeftMouseButton", "mouse1": "LeftMouseButton", "rmb": "RightMouseButton", "mouse2": "RightMouseButton",
              "mmb": "MiddleMouseButton", "mouse3": "MiddleMouseButton", "mouse4": "ThumbMouseButton", "mouse5": "ThumbMouseButton2",
              "마우스4": "ThumbMouseButton", "마우스5": "ThumbMouseButton2"}

def norm_key(text):
    """사용자가 적은 키 이름 → 언리얼 키 이름 (f5→F5, num+→Add, numpad 5→NumPadFive, space→SpaceBar). 모르면 None"""
    if not text: return None
    t = re.sub(r"[\s\u200b-\u200d\ufeff]+", "", unicodedata.normalize("NFKC", str(text))); low = t.lower()    # 전각 'ｆ５' 도 F5
    if not t: return None
    if low in _KEY_ALIAS: return _KEY_ALIAS[low]
    for n in list(_VK) + list(_MOUSE):
        if n.lower() == low: return n
    m = re.fullmatch(r"f([1-9]|1[0-2])", low)                                              # 언리얼은 F1~F12 까지
    if m: return "F" + m.group(1)
    if len(t) == 1 and t.isascii() and t.isalpha(): return t.upper()
    if len(t) == 1 and t.isascii() and t.isdigit(): return _DIGITS[int(t)]
    for d in _DIGITS:
        if low == d.lower(): return d
    m = re.fullmatch(r"(?:numpad|num|np|kp|keypad|넘패드|숫자패드|키패드)_?([0-9]|zero|one|two|three|four|five|six|seven|eight|nine)", low)
    if m:
        g = m.group(1); return "NumPad" + (_DIGITS[int(g)] if g.isdigit() else next(d for d in _DIGITS if d.lower() == g))
    return None

def key_status(override, ini, why=None) -> dict:
    """앱이 누를 NEXT 키 정리. override = 순서창 'NEXT 키' 칸, ini = 코박스 Input.ini 의 PlaylistNext.
    → key: 보낼 키(정규화, 못 보내면 None) · src: 'override'|'ini'|None · unknown: 모르는 이름이면 그 문자열 ·
      mismatch: 칸의 키와 코박스 설정이 다르면 (앱 키, 코박스 키) · ini: 코박스 설정 키"""
    ov = (override or "").strip(); ini = (ini or "").strip() or None
    ini_n = norm_key(ini) if ini else None
    if ov:
        ov_n = norm_key(ov)
        if ov_n is None: return {"key": None, "src": "override", "unknown": ov, "mismatch": None, "ini": ini_n or ini, "why": why}
        mm = (ov_n, ini_n or ini) if (ini and ini_n != ov_n) else None
        return {"key": ov_n, "src": "override", "unknown": None, "mismatch": mm, "ini": ini_n or ini, "why": why}
    if ini:
        return {"key": ini_n, "src": "ini", "unknown": None if ini_n else ini, "mismatch": None, "ini": ini_n or ini, "why": why}
    return {"key": None, "src": None, "unknown": None, "mismatch": None, "ini": None, "why": why}

def can_send(name) -> bool:
    n = norm_key(name)
    return bool(n) and (vk_of(n) is not None or n in _MOUSE)

def key_line(st: dict):
    """순서창 NEXT 키 안내 한 줄 → (문구, 팔레트 키)"""
    mouse_note = " · 마우스 버튼은 커서 아래 것을 누를 수 있어 키보드 키를 권장" if (st["key"] in _MOUSE) else ""
    if st["src"] == "override":
        if st["unknown"]:
            return (f"'{st['unknown']}' 는 모르는 키 이름 — F5, Add(넘패드 +), NumPad5, Space 처럼 적어 주세요"
                    + (f" (칸을 비우면 코박스 설정의 {key_label(st['ini'])} 를 씁니다)" if st["ini"] and can_send(st["ini"]) else ""), "val")
        if st["mismatch"]:
            return (f"⚠ 코박스 설정의 PlaylistNext 는 {key_label(st['mismatch'][1])} 인데 앱은 {key_label(st['key'])} 를 누릅니다 — "
                    f"코박스 설정 → 키 설정에서 {st['key']} 로 바꾸" + ("거나 이 칸을 비우세요" if can_send(st["mismatch"][1]) else "세요"), "val")
        if st["ini"]: return (f"직접 지정 {key_label(st['key'])} ✓ 코박스 설정과 일치{mouse_note}", "ok")
        return (f"직접 지정 {key_label(st['key'])} ✓ — 코박스 설정 → 키 설정 → PlaylistNext 도 {st['key']} 여야 합니다{mouse_note}", "ok")
    if st["src"] == "ini":
        if st["unknown"]: return (f"코박스 설정의 PlaylistNext 는 {st['unknown']} — 앱이 보낼 수 없는 키라 F5 같은 키로 바꿔 주세요", "val")
        return (f"코박스 설정에서 읽음: PlaylistNext = {key_label(st['key'])} ✓ (칸은 비워 두면 됩니다){mouse_note}", "ok")
    why = st.get("why")
    if why == "nofile":
        return ("코박스 설정 파일(Input.ini)을 못 찾았습니다 — 코박스 설정 → 키 설정 → PlaylistNext 에 지정한 키를 위 칸에 적어 주세요 (예: F10)", "val")
    if why == "removed":
        return ("코박스 설정에서 PlaylistNext 키가 해제되어 있습니다 — 코박스 설정 → 키 설정 → PlaylistNext 에 F10 같은 키를 지정하세요 (앱이 자동으로 읽습니다)", "val")
    if why == "chord":
        return ("코박스 설정의 PlaylistNext 가 조합키(Ctrl/Shift/Alt + 키)입니다 — 앱은 조합키를 못 보내니 F10 같은 단일 키로 바꿔 주세요", "val")
    return ("코박스 설정 파일에 PlaylistNext 가 없습니다 (한 번도 안 바꿨을 수 있음) — 코박스 설정 → 키 설정 → PlaylistNext 에 F10 을 지정하면 앱이 자동으로 읽습니다. "
            "이미 지정돼 있다면 그 키를 위 칸에 적어 주세요", "val")

def vk_of(name: str):
    """키 이름(사용자 표기 허용) → Windows 가상 키 코드 (모르면 None)"""
    name = norm_key(name)
    if not name: return None
    if name in _VK: return _VK[name]
    if re.fullmatch(r"F([1-9]|1\d|2[0-4])", name): return 0x70 + int(name[1:]) - 1
    if len(name) == 1 and name.isalpha(): return ord(name.upper())
    if name in _DIGITS: return ord("0") + _DIGITS.index(name)
    if name.startswith("NumPad") and name[6:] in _DIGITS: return 0x60 + _DIGITS.index(name[6:])
    return None

def send_key(name: str) -> bool:
    """키(또는 마우스 버튼) 한 번 누르기 — SendInput. 가상 키 + 스캔코드를 같이 보내 게임(언리얼)이 정확한 키로 받게 한다. Windows 전용"""
    name = norm_key(name) or name
    vk = vk_of(name); mouse = _MOUSE.get(name)
    if (vk is None and mouse is None) or sys.platform != "win32": return False
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                        ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]
        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [("dx", wintypes.LONG), ("dy", wintypes.LONG), ("mouseData", wintypes.DWORD), ("dwFlags", wintypes.DWORD),
                        ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]
        class _U(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT), ("mi", MOUSEINPUT), ("pad", ctypes.c_byte * 32)]
        class INPUT(ctypes.Structure):
            _anonymous_ = ("u",)
            _fields_ = [("type", wintypes.DWORD), ("u", _U)]
        if mouse:
            fdown, fup, xbtn = mouse
            down = INPUT(type=0); down.mi = MOUSEINPUT(0, 0, xbtn, fdown, 0, 0)
            up = INPUT(type=0);   up.mi = MOUSEINPUT(0, 0, xbtn, fup, 0, 0)
        else:
            scan = user32.MapVirtualKeyW(vk, 0)
            ext = 0x0001 if name in _EXTENDED else 0
            down = INPUT(type=1); down.ki = KEYBDINPUT(vk, scan, ext, 0, 0)
            up = INPUT(type=1);   up.ki = KEYBDINPUT(vk, scan, ext | 0x0002, 0, 0)
        arr = (INPUT * 2)(down, up)
        n = user32.SendInput(2, arr, ctypes.sizeof(INPUT))
        if n != 2:
            log_line(f"send_key {name}: SendInput {n}/2, GetLastError={ctypes.GetLastError()}, 앞 창={foreground_exe() or '?'}")
        return n == 2
    except Exception:
        log_exc("send_key"); return False

def exe_of_hwnd(hwnd) -> str:
    """창 핸들 → 그 창을 가진 프로세스의 실행 파일 이름 (Windows). 모르면 빈 문자열"""
    try:
        import ctypes
        user32, k32 = ctypes.windll.user32, ctypes.windll.kernel32
        pid = ctypes.c_ulong(); user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h = k32.OpenProcess(0x1000, False, pid.value)          # PROCESS_QUERY_LIMITED_INFORMATION
        if not h: return ""
        buf = ctypes.create_unicode_buffer(1024); n = ctypes.c_ulong(1024)
        ok = k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)); k32.CloseHandle(h)
        return os.path.basename(buf.value) if ok else ""
    except Exception:
        return ""

def foreground_exe() -> str:
    """지금 앞에 있는 창의 실행 파일 이름 (Windows). 모르면 빈 문자열"""
    if sys.platform != "win32": return ""
    try:
        import ctypes
        return exe_of_hwnd(ctypes.windll.user32.GetForegroundWindow())
    except Exception:
        return ""

def kovaaks_foreground() -> bool:
    if sys.platform != "win32": return True
    return foreground_exe().lower() == KOVAAKS_EXE.lower()

def kovaaks_hwnd():
    """코박스 메인 창 핸들 (보이는 최상위 창 중 실행 파일이 코박스인 것). 없으면 None"""
    if sys.platform != "win32": return None
    try:
        import ctypes
        from ctypes import wintypes
        user32 = ctypes.windll.user32
        found = []
        @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        def cb(hwnd, _):
            if user32.IsWindowVisible(hwnd) and exe_of_hwnd(hwnd).lower() == KOVAAKS_EXE.lower():
                found.append(hwnd); return False
            return True
        user32.EnumWindows(cb, 0)
        return found[0] if found else None
    except Exception:
        log_exc("kovaaks_hwnd"); return None

def focus_kovaaks() -> bool:
    """코박스 창을 앞으로 가져온다 (순서창 버튼을 눌러 우리 창이 앞에 있을 때 — 그 경우 Windows 가 포커스 넘기기를 허용한다).
    안 되면 Alt 를 한 번 눌렀다 떼고 다시 시도(잘 알려진 우회). 성공 여부 반환"""
    if sys.platform != "win32": return True
    hwnd = kovaaks_hwnd()
    if not hwnd: return False
    try:
        import ctypes
        user32 = ctypes.windll.user32
        if user32.IsIconic(hwnd): user32.ShowWindow(hwnd, 9)          # SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        for _ in range(2):
            time.sleep(0.12)
            if user32.GetForegroundWindow() == hwnd: return True
            user32.keybd_event(0x12, 0, 0, 0); user32.keybd_event(0x12, 0, 2, 0)     # Alt 톡
            user32.SetForegroundWindow(hwnd)
        time.sleep(0.12)
        return user32.GetForegroundWindow() == hwnd
    except Exception:
        log_exc("focus_kovaaks"); return False

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
     "txt":"#EDF1F5","sub":"#8CA0B3","dim":"#5C6C7C","hint":"#7A8B9C",
     "val":"#E8453A","ow":"#3B87F7","ok":"#4ED490","gold":"#F5C24B"}
RANKC = ["#98A2AC", "#E08A3C", "#C9D6E2", "#F5C24B"]

# 방송 모드 팔레트 — 녹화·스트리밍에서 가장 먼저 사라지는 것은 어두운 회색 글씨(dim 3.27:1)와
# 진한 빨강이다(4:2:0 색 서브샘플링이 채도 높은 빨강 테두리를 뭉갠다). 밝기를 올리고 빨강을 연하게 한다.
C_BROADCAST = {"txt": "#FFFFFF", "sub": "#C2D0DC", "hint": "#A9BACA", "dim": "#93A4B4",
               "line": "#3D4B59", "card2": "#252E38", "c3": "#2F3A46",
               "val": "#FF7A6E", "ow": "#6FAEFF", "ok": "#63E6A6", "gold": "#FFD36B"}
RANKC_BROADCAST = ["#B6C0CA", "#F0A257", "#DCE6F0", "#FFD36B"]

def apply_broadcast(on: bool):
    """팔레트를 바꾼다. 위젯은 만들 때 색이 정해지므로 창을 만들기 전에 불러야 한다"""
    if not on: return False
    C.update(C_BROADCAST)
    RANKC[:] = RANKC_BROADCAST
    return True
DAY_TYPE = {"v": ("발로 데이", C["val"]), "w": ("약점 데이", "#8A94A2"), "b": ("벤치마크", C["gold"]), "r": ("휴식", C["dim"])}

def single_instance_lock(tries: int = 1):
    """두 개가 동시에 떠서 서로 기록을 덮어쓰는 것 방지. 소켓 하나를 점유(참조를 유지해야 함).
    글씨 크기를 바꿔 다시 켜는 중이면 앞 창이 닫히기를 잠깐 기다린다"""
    import socket
    for i in range(max(1, tries)):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", 47653)); s.listen(1)
            return s
        except OSError:
            s.close()
            if i + 1 < tries: time.sleep(0.4)
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

    lock = single_instance_lock(tries=12 if os.environ.get("AIMDESK_RESTART") else 1)
    if lock is None:
        r0 = tk.Tk(); r0.withdraw()
        messagebox.showwarning("에임 데스크", "에임 데스크가 이미 실행 중입니다.\n두 개를 동시에 켜면 기록이 서로 덮어써집니다.")
        r0.destroy(); return

    data = load_data(); bump_ver()
    apply_broadcast(bool(data.get("broadcast")))      # 색은 위젯을 만들기 전에 정해야 한다
    if sys.platform == "win32":                      # 125~150% 배율 모니터에서 흐릿하지 않게 (시스템 DPI 인식)
        try:
            import ctypes
            try: ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except Exception: ctypes.windll.user32.SetProcessDPIAware()
        except Exception: pass
    root = tk.Tk(); root.withdraw()
    root._aimdesk_lock = lock
    root.report_callback_exception = lambda t, v, tb: _hook(t, v, tb)
    root.title("에임 데스크"); root.configure(bg=C["bg"])
    env_scale = float(os.environ.get("AIMDESK_SCALE") or 0)
    try: auto_scale = max(1.0, round(root.winfo_fpixels("1i") / 96, 2))
    except Exception: auto_scale = 1.0
    UI_SCALE[0] = pick_scale(data.get("ui_scale"), env_scale, auto_scale)
    root.tk.call("tk", "scaling", UI_SCALE[0] * 96 / 72)      # 글꼴 크기(포인트)도 같이 커지게
    vroot = (root.winfo_vrootx(), root.winfo_vrooty(), root.winfo_vrootwidth(), root.winfo_vrootheight())
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    MINW, MINH = min(px(960), sw - 80), min(px(660), sh - 120)
    root.minsize(MINW, MINH)
    if abs(float(data["win"].get("geo_scale") or UI_SCALE[0]) - UI_SCALE[0]) > 1e-6:
        data["win"].pop("geo", None); data["win"].pop("seq", None)   # 다른 배율에서 잰 크기는 지금 화면에 안 맞는다
    root.geometry(clamp_geometry(data["win"].get("geo"), *vroot, MINW, MINH) or f"{min(px(1060), sw - 80)}x{min(px(760), sh - 120)}")
    try: root.iconphoto(True, tk.PhotoImage(data=ICON_B64))
    except Exception: pass

    fams = set(tkfont.families())                      # 한 번만 (수백 개 폰트 나열이 느림)
    FAM = "Malgun Gothic" if "Malgun Gothic" in fams else "TkDefaultFont"
    MONO = "Consolas" if "Consolas" in fams else "TkFixedFont"
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
        """둥근 플랫 버튼 (호버·눌림·비활성 지원)"""
        def __init__(self, parent, text, command=None, bg=C["card2"], fg=C["txt"],
                     hover=None, font=FB, padx=14, pady=7, r=9, w=None):
            self.f = tkfont.Font(font=font)
            padx, pady, r = px(padx), px(pady), px(r)
            tw = w if w else self.f.measure(text) + padx*2
            th = self.f.metrics("linespace") + pady*2
            super().__init__(parent, width=tw, height=th, bg=parent["bg"],
                             highlightthickness=0, cursor="hand2")
            self.bgc, self.fgc, self.r = bg, fg, r
            self.hv = hover or self._lift(bg)
            self.shape = rrect(self, 1, 1, tw-1, th-1, r, fill=bg, outline="")
            self.lbl = self.create_text(tw//2, th//2, text=text, fill=fg, font=font)
            self.cmd = command; self.enabled = True
            self.bind("<Button-1>", self._press)
            self.bind("<ButtonRelease-1>", self._release)
            self.bind("<Enter>", lambda e: self.enabled and self.itemconfig(self.shape, fill=self.hv))
            self.bind("<Leave>", lambda e: self.enabled and self.itemconfig(self.shape, fill=self.bgc))
            self.bind("<Return>", lambda e: self._press(e)); self.bind("<space>", lambda e: self._press(e))
            self.bind("<FocusIn>", lambda e: self.itemconfig(self.shape, outline=C["sub"], width=1))
            self.bind("<FocusOut>", lambda e: self.itemconfig(self.shape, outline=""))
        def _press(self, e=None):
            if not self.enabled: return
            self.itemconfig(self.shape, fill=shade(self.bgc, -10))
            if self.cmd: self.cmd()
        def _release(self, e):
            if not self.enabled or not self.winfo_exists(): return
            try: inside = self.winfo_containing(e.x_root, e.y_root) is self
            except Exception: inside = False
            self.itemconfig(self.shape, fill=self.hv if inside else self.bgc)
        @staticmethod
        def _lift(hexc): return shade(hexc, 16)
        def restyle(self, bg=None, fg=None, text=None):
            if bg: self.bgc = bg; self.hv = self._lift(bg); self.itemconfig(self.shape, fill=bg)
            if fg: self.fgc = fg; self.itemconfig(self.lbl, fill=fg)
            if text is not None: self.itemconfig(self.lbl, text=text)
        def set_enabled(self, b: bool):
            if self.enabled == bool(b): return
            self.enabled = bool(b)
            self.itemconfig(self.shape, fill=self.bgc if b else C["card"])
            self.itemconfig(self.lbl, fill=self.fgc if b else C["dim"])
            self.configure(cursor="hand2" if b else "arrow")

    class Toggle(RBtn):
        """● 켜짐 / ○ 꺼짐 — 글리프까지 포함한 폭으로 만들어 상태가 바뀌어도 크기가 안 변한다"""
        def __init__(self, parent, text, getter, setter):
            self.getter, self.setter, self.base = getter, setter, text
            f = tkfont.Font(font=FB)
            super().__init__(parent, "● " + text, command=self.flip, w=max(f.measure("● " + text), f.measure("○ " + text)) + px(14) * 2)
            self.sync()
        def flip(self):
            self.setter(not self.getter()); self.sync()
        def sync(self):
            on = self.getter()
            self.restyle(bg="#173226" if on else C["card2"], fg=C["ok"] if on else C["sub"],
                         text=("● " if on else "○ ") + self.base)

    class Stepper(tk.Frame):
        def __init__(self, parent, get, set_):
            super().__init__(parent, bg=parent["bg"])
            self.get, self.set_ = get, set_
            self.minus = RBtn(self, "−", lambda: self.mod(-1), padx=11, pady=4); self.minus.pack(side="left")
            self.v = tk.Label(self, text="0", font=FN, width=3, bg=parent["bg"], fg=C["txt"])
            self.v.pack(side="left", padx=2)
            self.plus = RBtn(self, "＋", lambda: self.mod(+1), padx=10, pady=4); self.plus.pack(side="left")
            self.sync()
        def mod(self, d): self.set_(max(0, self.get()+d)); self.sync()
        def sync(self):
            self.v.configure(text=str(self.get())); self.minus.set_enabled(self.get() > 0)

    class Segmented(tk.Canvas):
        """체감 1~10 선택"""
        def __init__(self, parent, get, set_, n=10, cw=17, h=20):
            cw, h = px(cw), px(h)
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

    class VScroll(tk.Frame):
        """세로 스크롤 컨테이너 — 내용이 넘칠 때만 얇은 썸이 보인다. 휠은 main() 의 전역 바인딩이 처리"""
        def __init__(self, parent, bg=None):
            bg = bg or parent["bg"]
            super().__init__(parent, bg=bg)
            self.cv = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, width=px(80), height=px(80))
            self.thumb = tk.Canvas(self, width=px(6), bg=bg, highlightthickness=0, bd=0)
            self.cv.pack(side="left", fill="both", expand=True)
            self.body = tk.Frame(self.cv, bg=bg)
            self.win = self.cv.create_window((0, 0), window=self.body, anchor="nw")
            self.body.bind("<Configure>", self._on_body)
            self.cv.bind("<Configure>", self._on_cv)
            self.cv.configure(yscrollcommand=self._on_yview)
            self.shown = False
        def _on_body(self, e):
            self.cv.configure(scrollregion=(0, 0, e.width, e.height)); self._on_yview(*self.cv.yview())
        def _on_cv(self, e):
            self.cv.itemconfigure(self.win, width=e.width); self._on_yview(*self.cv.yview())
        def _on_yview(self, lo, hi):
            lo, hi = float(lo), float(hi)
            need = needs_scroll(self.body.winfo_reqheight(), self.cv.winfo_height())
            if need != self.shown:
                self.shown = need
                if need: self.thumb.pack(side="right", fill="y")
                else: self.thumb.pack_forget()
            if need:
                h = max(self.thumb.winfo_height(), 10)
                y1 = int(lo * h); y2 = max(int(hi * h), y1 + px(12))
                self.thumb.delete("all")
                rrect(self.thumb, 1, y1, px(5), y2, 3, fill=C["c3"], outline="")

    def cfg(widget, **kw):
        """바뀐 옵션만 configure — 2초마다 수십 개 라벨을 건드려도 Tk 호출은 실제 변경분만"""
        last = getattr(widget, "_last", None)
        if last is None: last = widget._last = {}
        changed = {k: v for k, v in kw.items() if last.get(k) != v}
        if changed:
            widget.configure(**changed); last.update(changed)

    def card(parent, pad=(14, 12)):
        f = tk.Frame(parent, bg=C["card"], padx=pad[0], pady=pad[1],
                     highlightbackground=C["line"], highlightthickness=1)
        return f

    def cap(parent, text, fg=None):
        return tk.Label(parent, text=text, font=FCAP, bg=parent["bg"],
                        fg=fg or C["dim"])

    # ── 상태 ──
    today_key = [today_date().isoformat()]
    def dget(): return data["days"].setdefault(today_key[0], blank_day())

    # ══ 헤더 ══  (날짜·요일 칩은 build_day_ui()가 채운다 — 자정을 넘기면 다시 그림)
    head = tk.Frame(root, bg=C["bg"]); head.pack(fill="x", padx=18, pady=(14, 2))
    lf = tk.Frame(head, bg=C["bg"]); lf.pack(side="left")
    tk.Label(lf, text="에임 데스크", font=(FAM, 16, "bold"), bg=C["bg"], fg=C["txt"]).pack(anchor="w")
    sub = tk.Frame(lf, bg=C["bg"]); sub.pack(anchor="w")
    date_lbl = tk.Label(sub, text="", font=FS, bg=C["bg"], fg=C["sub"]); date_lbl.pack(side="left")
    daych = tk.Canvas(sub, width=px(70), height=px(18), bg=C["bg"], highlightthickness=0); daych.pack(side="left", padx=8)
    wk_cv = tk.Canvas(sub, width=px(7*15), height=px(18), bg=C["bg"], highlightthickness=0); wk_cv.pack(side="left")
    WEEK_FILL = {"done": C["ok"], "miss": "#3A1F1D", "rest": C["card2"], "future": C["card"], "today": C["bg"]}
    def draw_week(strip):
        wk_cv.delete("all")
        for i, (dow, st) in enumerate(strip):
            x = i * px(15); sz = px(11)
            rrect(wk_cv, x, px(3), x + sz, px(3) + sz, 3, fill=WEEK_FILL[st],
                  outline=C["gold"] if st == "today" else "", width=1)
            wk_cv.create_text(x + sz / 2, px(3) + sz / 2, text=dow, font=(FAM, 7),
                              fill="#0B0E11" if st == "done" else C["dim"])

    rf = tk.Frame(head, bg=C["bg"]); rf.pack(side="right")
    hdr_e = tk.Label(rf, text="", font=(MONO, 15, "bold"), bg=C["bg"], fg=C["gold"])
    hdr_e.pack(side="right")
    hdr_idx = tk.Label(rf, text="", font=FN, bg=C["bg"], fg=C["txt"])
    hdr_idx.pack(side="right", padx=(0, 16))
    hdr_mi = tk.Label(rf, text="", font=FNS, bg=C["bg"], fg=C["sub"])
    hdr_mi.pack(side="right", padx=(0, 16))
    hdr_streak = tk.Label(rf, text="", font=FNS, bg=C["bg"], fg=C["sub"])
    hdr_streak.pack(side="right", padx=(0, 16))
    hdr_lv = tk.Label(rf, text="", font=FNS, bg=C["bg"], fg=C["sub"])
    hdr_lv.pack(side="right", padx=(0, 6))
    lv_cv = tk.Canvas(rf, width=px(22), height=px(22), bg=C["bg"], highlightthickness=0)
    lv_cv.pack(side="right", padx=(0, 16))

    # 토스트 — 최대 3개 쌓이고, 클릭하면 닫히고, 각각 10초 뒤 사라진다
    toast = tk.Frame(root, bg=C["bg"])
    tq = ToastQueue()
    TOAST_STYLE = {"pb": ("#241E0E", C["gold"]), "info": (C["card2"], C["txt"]), "warn": ("#2A1512", C["val"])}
    toast_after = [None]
    def render_toasts():
        for w_ in toast.winfo_children(): w_.destroy()
        if not tq.items:
            toast.pack_forget(); return
        for i, (msg, kind, _) in enumerate(tq.items):
            bg_, fg_ = TOAST_STYLE.get(kind, TOAST_STYLE["info"])
            row = tk.Frame(toast, bg=bg_, highlightbackground=fg_, highlightthickness=1, padx=12, pady=6, cursor="hand2")
            row.pack(fill="x", pady=(0, 4))
            lb = tk.Label(row, text=msg, font=FB, bg=bg_, fg=fg_, anchor="w", justify="left",
                          wraplength=max(px(600), root.winfo_width() - px(80)))
            lb.pack(side="left", fill="x", expand=True)
            for w_ in (row, lb): w_.bind("<Button-1>", lambda e, i=i: (tq.dismiss(i), render_toasts()))
        if not toast.winfo_ismapped():
            toast.pack(fill="x", padx=18, pady=(6, 0), after=head)
    def toast_tick():
        toast_after[0] = None
        if tq.expire(time.monotonic()): render_toasts()
        if tq.items: toast_after[0] = root.after(1000, toast_tick)
    def show_toast(msg, kind="info"):
        tq.push(msg, kind, time.monotonic()); COACH_STATE["toasts"].append(msg)
        render_toasts()
        if toast_after[0] is None: toast_after[0] = root.after(1000, toast_tick)

    # ══ 탭바 · 하단 상태줄 · 본문 ══
    tabbar = tk.Frame(root, bg=C["bg"]); tabbar.pack(fill="x", padx=18, pady=(10, 6))
    status = tk.Frame(root, bg=C["card"], highlightbackground=C["line"], highlightthickness=1)
    status.pack(side="bottom", fill="x")
    status_dot = tk.Canvas(status, width=px(10), height=px(10), bg=C["card"], highlightthickness=0)
    status_dot.pack(side="left", padx=(12, 6), pady=5)
    status_oval = status_dot.create_oval(px(1), px(1), px(9), px(9), fill=C["dim"], outline="")
    status_lbl = tk.Label(status, text="", font=FS, bg=C["card"], fg=C["hint"], anchor="w")
    status_lbl.pack(side="left", fill="x", expand=True)
    legend_lbl = tk.Label(status, text="", font=FS, bg=C["card"], fg=C["dim"])
    legend_lbl.pack(side="right", padx=12)
    LEVEL_COL = {"ok": C["ok"], "warn": C["gold"], "err": C["val"]}
    def set_status(text, level):
        col = LEVEL_COL.get(level, C["hint"])
        cfg(status_lbl, text=text.lstrip("● ").strip(), fg=col)
        status_dot.itemconfig(status_oval, fill=col)
    body = tk.Frame(root, bg=C["bg"]); body.pack(fill="both", expand=True, padx=18, pady=(0, 10))
    frames, tabbtns, underls = {}, {}, {}
    dirty = {"today": True, "grow": True, "bench": True, "log": True}
    cur_tab = ["today"]
    tab_fn = {}                                    # 탭 이름 -> 그 탭만 다시 그리는 함수 (아래에서 채움)
    def refresh_tab(t):
        if dirty.get(t) and t in tab_fn:
            dirty[t] = False; tab_fn[t]()
            _DBG.setdefault("counters", {}).setdefault("refresh_tab", 0)
            _DBG["counters"]["refresh_tab"] += 1
    def show(tab):
        for f in frames.values(): f.pack_forget()
        frames[tab].pack(fill="both", expand=True)
        for n, b in tabbtns.items():
            b.configure(fg=C["txt"] if n == tab else C["dim"])
            underls[n].configure(bg=C["val"] if n == tab else C["bg"])
        cur_tab[0] = tab
        refresh_tab(tab)
    for name, label in (("today","오늘"),("grow","성장"),("bench","벤치"),("log","기록")):
        holder = tk.Frame(tabbar, bg=C["bg"]); holder.pack(side="left", padx=(0, 22))
        b = tk.Label(holder, text=label, font=(FAM, 11, "bold"), bg=C["bg"],
                     fg=C["dim"], cursor="hand2")
        b.pack(); b.bind("<Button-1>", lambda e, n=name: show(n))
        u = tk.Frame(holder, bg=C["bg"], height=3, width=30); u.pack(fill="x", pady=(3, 0))
        tabbtns[name], underls[name] = b, u

    # ══ 오늘 탭 ══
    ft = tk.Frame(body, bg=C["bg"]); frames["today"] = ft
    left = card(ft); left.pack(side="left", fill="both", expand=True)
    left_scroll = VScroll(left); left_scroll.pack(fill="both", expand=True)
    right = tk.Frame(ft, bg=C["bg"], width=px(310)); right.pack(side="left", fill="y", padx=(14, 0))
    right.pack_propagate(False)
    right_scroll = VScroll(right); right_scroll.pack(fill="both", expand=True)
    rbody = right_scroll.body

    # 날짜에 묶인 UI 상태 — 자정을 넘기면 build_day_ui()가 헤더와 루틴 카드를 다시 그린다
    day_state = {"dt": "v", "pl": None, "sess_lbl": None, "coach": []}
    routine_rows = []; section_labels = []; routine_next = [None]

    # ── 순서창 + 자동 진행 ──
    #   오늘 칠 시나리오를 순서대로 나열하고, 코박스 딥링크로 한 판씩 전송한다.
    #   판이 끝나 stats CSV가 생기면(2초 감시) 대기 시간 뒤 다음 시나리오 딥링크를 보낸다 → 결과창에서 NEXT를 누를 필요가 없다.
    seq_win = {"win": None, "rows": [], "prog": None, "auto_lbl": None, "auto_btn": None, "sum": None,
               "seq": [], "base": {}, "skipped": set()}      # skipped: 건너뛴 줄 번호
    auto = {"on": False, "fired": None, "due": None,      # fired/due: 넘겼거나 넘기기로 예약된 순서창 인덱스
            "fired_at": None, "fired_running": True, "warned": False, "pending": None,   # pending: 전송 실패 → 다시 시도 (key 방식 True, link 방식 인덱스)
            "seen": None, "start_played": 0,               # key 방식: seen = NEXT 를 눌러 준 판 수, start_played = 자동 진행을 시작할 때 이미 있던 판 수
            "mode": data.get("auto_mode", "key")}         # "key" = 코박스 플레이리스트 + NEXT 키 자동 입력, "link" = 딥링크
    def key_st(): return key_status(data.get("next_key"), playlist_next_key(), ini_why())
    if data.get("next_key") and playlist_next_key() and norm_key(data["next_key"]) == norm_key(playlist_next_key()):
        data["next_key"] = None      # 이전 버전이 코박스 설정 키를 칸에 채워 저장해 둔 것 — 비워서 앞으로 코박스 설정을 따라가게
    def next_key(): return key_st()["key"]
    def auto_delay(): return int(data.get("auto_delay", 4))
    def cur_plays():
        """오늘 판 (key, 시각, 점수) — 보존된 기록(폴더를 정리해도 남음)이 스캔 목록을 포함하므로 그것을 쓴다"""
        dp = day_plays(data, today_key[0])
        return dp if len(dp) >= len(TODAY_PLAYS) else list(TODAY_PLAYS)

    def sequence_for(plname):
        """플레이리스트(또는 토요일 벤치 18개)를 실제 치는 순서대로 펼친 key 목록"""
        if plname:
            return [k for k, n in dict(playlists_for(today_key[0], data["pb"]))[plname] for _ in range(n)]
        if day_state["dt"] == "b":
            return [k for s in SUBS for k, _ in s[3]]
        return []

    def today_plays_by_key():
        by = {}
        for k, _, s_ in cur_plays(): by.setdefault(k, []).append(s_)
        return by

    def seq_status():
        """(각 줄 완료 여부, 다음에 칠 인덱스(None이면 전부 완료), 각 줄의 점수(없으면 None)).
        오늘 친 판을 시간순으로 같은 시나리오의 줄에 차례로 배정한다 — '처음부터' 기준 판 수 이후부터."""
        by = today_plays_by_key()
        used, done, scores, nxt = {}, [], [], None
        for i, k in enumerate(seq_win["seq"]):
            idx = seq_win["base"].get(k, 0) + used.get(k, 0)
            lst = by.get(k, [])
            if i in seq_win["skipped"]:
                if idx < len(lst): seq_win["skipped"].discard(i)      # 건너뛰었다고 표시했는데 그 판이 들어옴 = 게임은 안 건너뜀 → 되살린다
                else: done.append(True); scores.append(None); continue
            if idx < len(lst):
                used[k] = used.get(k, 0) + 1
                done.append(True); scores.append(lst[idx])
            else:
                done.append(False); scores.append(None)
                if nxt is None: nxt = i
        seq_win["used"] = used
        return done, nxt, scores

    def played_count():
        done, _, scores = seq_status()
        return sum(1 for i in range(len(done)) if done[i] and scores[i] is not None)

    def seq_alive():
        w = seq_win["win"]
        return w is not None and w.winfo_exists()

    def open_sequence(plname):
        seq = sequence_for(plname)
        if not seq: return
        if seq_alive(): remember_seq_pos(); seq_win["win"].destroy()
        w = tk.Toplevel(root)
        seq_win.update(win=w, rows=[], seq=seq, base={}, skipped=set(), used={})
        auto.update(pending=None, fired_at=None, due=None)
        auto.update(seen=played_count(), start_played=auto["seen"])
        title = plname or "AIMDESK Bench"; seq_win["title"] = title
        w.title("오늘 순서 — " + title); w.configure(bg=C["bg"])
        w.attributes("-topmost", bool(data.get("seq_topmost", True))); w.resizable(False, False)
        def close_seq():
            if seq_win.get("commit_key"): seq_win["commit_key"]()     # 칸에 적다 만 키도 저장
            stop_auto(); remember_seq_pos(); w.destroy()
        w.protocol("WM_DELETE_WINDOW", close_seq)
        hd = tk.Frame(w, bg=C["bg"]); hd.pack(fill="x", padx=12, pady=(10, 2))
        tk.Label(hd, text=title, font=FB, bg=C["bg"], fg=C["txt"]).pack(side="left")
        seq_win["prog"] = tk.Label(hd, text="", font=FNS, bg=C["bg"], fg=C["sub"])
        seq_win["prog"].pack(side="right")
        seq_win["auto_lbl"] = tk.Label(w, text="", font=FS, bg=C["bg"], fg=C["hint"],
                                       wraplength=px(470), justify="left")
        seq_win["auto_lbl"].pack(anchor="w", padx=12)
        seq_win["guide"] = tk.Canvas(w, width=px(470), height=px(54), bg=C["bg"], highlightthickness=0)   # 코박스 탭 그림 — 첫 판 전에만 보인다
        bottom = tk.Frame(w, bg=C["bg"]); bottom.pack(side="bottom", fill="x")       # 조작부: 창을 줄여도 안 잘리게 먼저 자리를 잡는다
        box = tk.Frame(w, bg=C["card"], padx=10, pady=8,
                       highlightbackground=C["line"], highlightthickness=1)
        box.pack(fill="both", expand=True, padx=12, pady=(6, 8))
        vs = VScroll(box, bg=C["card"]); vs.pack(fill="both", expand=True); seq_win["vs"] = vs
        seq_win["top_lbl"] = tk.Label(vs.body, text="", font=FNS, bg=C["card"], fg=C["dim"], anchor="w")
        seq_win["bot_lbl"] = tk.Label(vs.body, text="", font=FNS, bg=C["card"], fg=C["dim"], anchor="w")
        seq_win.update(cur_row=None, last_nxt=None, vis=None, btn_enabled=None)
        nmw = max(16, math.ceil(tkfont.Font(font=FB).measure("Floating Heads") / max(1, tkfont.Font(font=F).measure("0"))) + 1)
        for i, k in enumerate(seq, 1):
            row = tk.Frame(vs.body, bg=C["card"]); row.pack(fill="x", pady=1)
            num = tk.Label(row, text=f"{i:02d}", font=FNS, width=3, anchor="e", bg=C["card"], fg=C["dim"])
            num.pack(side="left")
            tk.Frame(row, bg=C["val"] if SCEN[k][1] == "v" else C["ow"], width=px(3), height=px(14)).pack(side="left", padx=(6, 8))
            nm = tk.Label(row, text=sname(k), font=F, width=nmw, anchor="w", bg=C["card"], fg=C["sub"], cursor="hand2")
            nm.pack(side="left"); nm.bind("<Button-1>", lambda e, k=k: open_detail(k))
            st = tk.Label(row, text="", font=FN, width=2, bg=C["card"], fg=C["dim"])
            st.pack(side="right"); st.bind("<Button-1>", lambda e, i=i - 1: unskip(i))
            sc = tk.Label(row, text="", font=FN, width=6, anchor="e", bg=C["card"], fg=C["txt"])
            sc.pack(side="right", padx=(6, 4))
            dl = tk.Label(row, text="", font=FNS, width=8, anchor="e", bg=C["card"], fg=C["dim"])
            dl.pack(side="right")
            seq_win["rows"].append((k, num, nm, st, sc, dl))
        seq_win["sum"] = tk.Label(bottom, text="", font=FS, bg=C["bg"], fg=C["sub"], wraplength=px(470), justify="left")
        seq_win["sum"].pack(anchor="w", padx=12, pady=(0, 6))
        # 조작 줄: 자동 진행 토글 · 건너뛰기 · 다시 보내기 · 처음부터 · 판 사이 대기
        ctl = tk.Frame(bottom, bg=C["bg"]); ctl.pack(fill="x", padx=12, pady=(0, 6))
        seq_win["auto_btn"] = Toggle(ctl, "자동 진행", lambda: auto["on"], set_auto)
        seq_win["auto_btn"].pack(side="left")
        seq_win["skip_btn"] = RBtn(ctl, "건너뛰기 ▶", skip_current, padx=10, pady=5); seq_win["skip_btn"].pack(side="left", padx=(6, 0))
        seq_win["resend_btn"] = RBtn(ctl, "다시 보내기", resend_current, padx=10, pady=5); seq_win["resend_btn"].pack(side="left", padx=(6, 0))
        RBtn(ctl, "처음부터", restart_sequence, padx=10, pady=5).pack(side="left", padx=(6, 0))
        seq_win["hint"] = tk.Label(bottom, text="", font=FS, bg=C["bg"], fg=C["hint"], wraplength=px(470), justify="left")
        seq_win["hint"].pack(anchor="w", padx=12, pady=(0, 4))
        dl = tk.Frame(bottom, bg=C["bg"]); dl.pack(fill="x", padx=12, pady=(0, 4))
        tk.Label(dl, text="판 끝난 뒤 대기(초)", font=FS, bg=C["bg"], fg=C["sub"]).pack(side="left")
        Stepper(dl, auto_delay,
                lambda v: (data.__setitem__("auto_delay", max(1, min(30, v))), save_data(data), update_sequence())
                ).pack(side="left", padx=(8, 12))
        tk.Label(dl, text="NEXT 키", font=FS, bg=C["bg"], fg=C["sub"]).pack(side="left")
        key_var = tk.StringVar(value=data.get("next_key") or "")        # 칸에는 '직접 지정'만 — 비워 두면 코박스 설정에서 읽은 키를 쓴다
        key_ent = tk.Entry(dl, textvariable=key_var, width=9, font=FNS, bg=C["card2"], fg=C["txt"],
                           insertbackground=C["txt"], bd=0, justify="center")
        key_ent.pack(side="left", padx=(6, 0), ipady=3)
        def commit_key(*_):
            v = key_var.get().strip(); n = norm_key(v)
            if n and n != v: key_var.set(n)                                  # f5 → F5, num+ → Add
            new = (n or v) or None
            if (data.get("next_key") or None) == new: return
            data["next_key"] = new; save_data(data)
            set_hint(""); update_sequence()
        key_ent.bind("<Return>", commit_key); key_ent.bind("<FocusOut>", commit_key); seq_win["commit_key"] = commit_key
        seq_win["key_lbl"] = tk.Label(bottom, text="", font=FS, bg=C["bg"], fg=C["hint"], wraplength=px(470), justify="left")
        seq_win["key_lbl"].pack(anchor="w", padx=12, pady=(0, 4))
        opt = tk.Frame(bottom, bg=C["bg"]); opt.pack(fill="x", padx=12, pady=(0, 4))
        Toggle(opt, "항상 위", lambda: bool(data.get("seq_topmost", True)), set_topmost).pack(side="left")
        Toggle(opt, "딥링크 방식", lambda: auto["mode"] == "link", set_mode_link).pack(side="left", padx=(6, 0))
        Toggle(opt, "간단히", lambda: bool(data.get("seq_compact", False)), set_compact).pack(side="left", padx=(6, 0))
        tk.Label(bottom, text="Space 자동 · Ctrl+N 건너뛰기 · Ctrl+R 다시 · Esc 닫기 · 이름 클릭 = 상세", font=FS, bg=C["bg"], fg=C["dim"]).pack(anchor="w", padx=12, pady=(0, 10))
        def on_seq_key(e):
            if isinstance(e.widget, RBtn) and e.keysym in ("space", "Return"): return   # 버튼 자체가 처리
            act = seq_shortcut_action(e.keysym, e.state, isinstance(e.widget, tk.Entry))
            if not act: return
            if act == "auto": seq_win["auto_btn"].flip()
            elif act == "skip": skip_current()
            elif act == "resend": resend_current()
            elif act == "close": close_seq()
            elif act == "blur": w.focus_set()                      # 칸에서 Esc = 칸 나가기(저장). 창은 그대로
            return "break"
        w.bind("<Key>", on_seq_key)
        # 목록 높이: 화면의 3/4 를 넘지 않게 (넘치면 스크롤). 창을 세로로 줄이면 목록만 줄어든다
        root.update_idletasks(); w.update_idletasks()
        other_h = sum(c.winfo_reqheight() for c in w.winfo_children() if c is not box) + px(90)
        seq_win["max_list_h"] = w.winfo_screenheight() - other_h
        vs.cv.configure(height=seq_window_height(vs.body.winfo_reqheight(), seq_win["max_list_h"]))
        w.resizable(False, True); w.update_idletasks()
        # 지난번 위치가 화면 안이면 거기, 아니면 본창 오른쪽(화면 밖이면 본창 위에 겹쳐서)
        pos = clamp_pos(data["win"].get("seq"), w.winfo_reqwidth(), w.winfo_reqheight(), *vroot)
        if pos is None:
            x = root.winfo_x() + root.winfo_width() + 8
            if x + w.winfo_reqwidth() > vroot[0] + vroot[2]: x = root.winfo_x() + 40   # 가상 화면(모든 모니터) 기준
            pos = f"+{x}+{root.winfo_y()}"
        w.geometry(pos)
        update_sequence()

    def draw_tab_guide(cv):
        """코박스 샌드박스 브라우저의 탭 4개를 그려 '로컬 재생 목록'(네 번째)을 가리킨다"""
        cv.delete("all"); names = ["온라인 시나리오", "로컬 시나리오", "온라인 재생 목록", "로컬 재생 목록"]
        wbox, h, gap, x, y = px(108), px(24), px(6), px(2), px(2)
        for i, nm in enumerate(names):
            on = i == 3
            rrect(cv, x, y, x + wbox, y + h, 5, fill=("#E8702A" if on else C["bg"]), outline="#E8702A", width=1)
            cv.create_text(x + wbox / 2, y + h / 2, text=nm, fill=("#0B0E11" if on else "#E8702A"), font=(FAM, 8, "bold" if on else "normal"))
            x += wbox + gap
        cv.create_text(x - gap - wbox / 2, y + h + px(13), text="▲ 이 탭(네 번째)에서 AIMDESK 를 고르세요 · 시나리오 탭이 아닙니다", fill=C["gold"], font=(FAM, 8, "bold"), anchor="e")

    def remember_seq_pos():
        if seq_alive():
            w = seq_win["win"]; data["win"]["seq"] = "%+d%+d" % (w.winfo_x(), w.winfo_y())

    def update_sequence():
        if not seq_alive(): return
        done, nxt, scores = seq_status()
        dkey = today_key[0]
        _pbb = pb_before_day(data, dkey); _seen_pb = {}
        def _vf(k_, sc_):
            base = max(_pbb.get(k_, 0), _seen_pb.get(k_, 0)) or None
            r_ = play_verdict(sc_, scen_band(data, k_, dkey), base)
            _seen_pb[k_] = max(_seen_pb.get(k_, 0), sc_)
            return r_
        rows, n_pb, rel = seq_rows_apply(seq_win["seq"], done, nxt, scores, lambda k: recent_stats(data, k, dkey), _vf)
        block_txt = None
        for bk, bs_, be_ in blocks_of(seq_win["seq"]):
            pts = [(i, scores[i]) for i in range(bs_, be_) if scores[i] is not None]
            bt = block_trend(pts)
            if bt and all(scores[i] is not None for i in range(bs_, be_)):
                r_ = rows[be_ - 1]; rows[be_ - 1] = r_[:6] + ((r_[6] + " " + bt[0]).strip(), r_[7])
            if bt and nxt is not None and bs_ <= nxt < be_ and len(pts) >= 3:
                block_txt = f"{sname(bk)} {len(pts)}/{be_ - bs_} {bt[0]} {bt[1]:+.1f}%/판 · 베스트 {max(v for _, v in pts)}"
        for (k, num, nm, st, sc, dl), r in zip(seq_win["rows"], rows):
            cfg(num, fg=C[r[0]]); cfg(nm, fg=C[r[1]]); cfg(st, text=r[2], fg=C[r[3]])
            cfg(sc, text=r[4], fg=C[r[5]]); cfg(dl, text=r[6], fg=C[r[7]])
        # 현재 줄 강조 (바뀔 때만)
        if seq_win.get("cur_row") != nxt:
            for idx_ in (seq_win.get("cur_row"), nxt):
                if idx_ is None or idx_ >= len(seq_win["rows"]): continue
                on = idx_ == nxt; k_, num_, nm_, st_, sc_, dl_ = seq_win["rows"][idx_]
                for w_ in (num_.master, num_, nm_, st_, sc_, dl_): w_.configure(bg=C["card2"] if on else C["card"])
                nm_.configure(font=FB if on else F); num_.master.pack_configure(pady=3 if on else 1)
            seq_win["cur_row"] = nxt
            if routine_rows: set_next_marker(seq_win["seq"][nxt] if nxt is not None else next_routine_key(
                [(r[0], r[1], r[2]) for r in routine_rows], data["days"].get(dkey, blank_day()), None))
        # 간단히 보기: 보이는 줄 집합이 바뀔 때만 다시 pack
        vis, hd_, ha_ = visible_rows(done, nxt, seq_win["skipped"], bool(data.get("seq_compact", False)))
        if tuple(vis) != seq_win.get("vis"):
            vs = seq_win.get("vs")
            for r_ in seq_win["rows"]: r_[1].master.pack_forget()
            seq_win["top_lbl"].pack_forget(); seq_win["bot_lbl"].pack_forget()
            if hd_: cfg(seq_win["top_lbl"], text=f"  ✓ {hd_}판 완료"); seq_win["top_lbl"].pack(fill="x", pady=(0, 2))
            for i in vis:
                seq_win["rows"][i][1].master.pack(fill="x", pady=3 if i == nxt else 1)
            if ha_: cfg(seq_win["bot_lbl"], text=f"  … {ha_}판 남음"); seq_win["bot_lbl"].pack(fill="x", pady=(2, 0))
            seq_win["vis"] = tuple(vis)
            vs_ = seq_win.get("vs")
            if vs_ is not None and seq_win.get("max_list_h"):                  # 보이는 줄 수에 맞춰 목록 높이도 조정
                root.after_idle(lambda: vs_.cv.configure(height=seq_window_height(vs_.body.winfo_reqheight(), seq_win["max_list_h"])) if vs_.winfo_exists() else None)
        # 현재 줄이 보이도록 스크롤 (차례가 바뀔 때만)
        if nxt != seq_win.get("last_nxt") and nxt is not None and seq_win.get("vs") is not None:
            vs = seq_win["vs"]; row_ = seq_win["rows"][nxt][1].master
            root.after_idle(lambda: (vs.cv.yview_moveto(scroll_to_show(row_.winfo_y(), max(1, row_.winfo_height()), vs.body.winfo_reqheight(),
                                                                          max(1, vs.cv.winfo_height()), float(vs.cv.yview()[0])))
                                     if row_.winfo_exists() else None))
            seq_win["last_nxt"] = nxt
        en = nxt is not None
        if seq_win.get("btn_enabled") != en:
            for b_ in (seq_win.get("skip_btn"), seq_win.get("resend_btn")):
                if b_ is not None: b_.set_enabled(en)
            seq_win["btn_enabled"] = en
        total, done_n = len(done), sum(done)
        played = sum(1 for i in range(total) if done[i] and scores[i] is not None)
        cfg(seq_win["prog"], text=f"{played}/{total}" + (f" · 건너뜀 {done_n - played}" if done_n - played else "") + ("  완료 ✓" if done_n >= total else ""),
            fg=C["ok"] if done_n >= total else C["sub"])
        if played == 0:
            summ = "점수 옆 ▲▼ = 최근 7일 평균 대비 · PB! = 역대 최고 경신"
        else:
            remaining = sum(1 for i in range(total) if not done[i]); cp = cur_plays()
            est = remaining_estimate(cp, remaining) if (len(cp) >= 2 or remaining <= 15) else None
            summ = fmt_seq_summary(played, total - (done_n - played), n_pb, rel, probe_status(data["days"].get(dkey, blank_day())) if day_state["dt"] in ("v", "w") else None,
                                   (HDR_STATE["vi"], HDR_STATE["oi"]), est, block_txt)
            if done_n - played: summ += f" · 건너뜀 {done_n - played}"
            if nxt is None:
                avg_ = {k_: recent_stats(data, k_, dkey, "first")[0] for k_ in PROBE}
                summ += "\n" + next_step(data, dkey, cur_plays(), avg_)
        cfg(seq_win["sum"], text=summ, fg=C["gold"] if n_pb else C["sub"])
        col = C["ok"] if (auto["on"] and nxt is not None) else C["dim"]
        kst = key_st()
        mode_txt = "딥링크" if auto["mode"] == "link" else f"NEXT 키 {kst['key'] or '미지정'}" + (" ⚠" if (kst["mismatch"] or kst["unknown"]) else "")
        fresh = auto["mode"] == "key" and played == auto["start_played"]   # 자동 진행을 켠 뒤 아직 한 판도 안 들어옴 (건너뛰기·다시 보내기를 눌렀어도 마찬가지)
        if nxt is None:
            msg = "오늘 순서 전부 완료 🎉  ·  한 번 더 돌리려면 '처음부터'"
        elif auto["on"] and fresh:
            # 코박스에서 플레이리스트를 아직 안 켰을 가능성이 크다 → 할 일을 크게. 첫 판이 들어오면 자동 진행 상태로 바뀐다
            key_ok = bool(kst["key"]) and can_send(kst["key"])
            msg = (f"코박스에서 시작하세요: ESC → 샌드박스 브라우저 → 네 번째 탭 '로컬 재생 목록'(시나리오 탭 아님) → 목록에서 {seq_win['title']} 선택 → ▶ 플레이 (상단 토글 '도전 과제'). "
                   + (f"첫 판({sname(seq_win['seq'][0])})이 끝나면 앱이 {kst['key']} 키로 이어갑니다" if key_ok
                      else "⚠ 아래 NEXT 키를 먼저 설정하세요 — 없으면 판이 끝나도 앱이 다음 판으로 넘기지 못합니다")
                   + " · 목록에 AIMDESK 가 없으면 코박스를 껐다 켜세요. 그래도 없으면 '딥링크 방식' 토글을 켜면 앱이 시나리오를 직접 보냅니다")
            if played > 0 and nxt > 0:
                msg += f" · 오늘 이미 {played}판: 이어서 치는 중이면 다음은 {sname(seq_win['seq'][nxt])}, 플레이리스트를 새로 시작하면 자동으로 1번부터 다시 셉니다"
            col = C["gold"] if key_ok else C["val"]
        elif auto["on"] and auto["fired"] == nxt and auto["fired_at"] is not None:
            nm_ = sname(seq_win["seq"][nxt]); el = int(time.monotonic() - auto["fired_at"])
            if el > (STALL_SEC if auto["fired_running"] else STALL_SEC_LAUNCH):
                # 60초 시나리오가 끝났어야 할 시간인데 CSV가 없다 = 무료 플레이(FREEPLAY, 타이머 없음)로 열렸을 가능성
                msg = (f"⚠ {nm_} 시작 후 {el}초 — 기록이 없습니다. "
                       + (f"① 코박스에 새 판이 안 떴으면: NEXT 키 {kst['key'] or '미지정'} 가 코박스 설정의 PlaylistNext({kst['ini'] or '없음'})와 같은지, 플레이리스트가 돌고 있는지 확인 · "
                          if auto["mode"] == "key" else "")
                       + "② 타이머가 안 보이면 무료 플레이(FREEPLAY) 상태: ESC → 상단 '플레이' 왼쪽 토글을 '도전 과제'(CHALLENGE)로 바꾸고 플레이리스트를 다시 시작 · ③ 쉬는 중이면 무시")
                col = C["val"]
                if not auto["warned"]:
                    auto["warned"] = True
                    show_toast("⚠ 기록이 안 들어옵니다 — NEXT 키가 코박스 설정과 같은지, 상단 토글이 '도전 과제'인지 확인하세요", "warn")
            else:
                msg = f"자동 진행 중 ({mode_txt}) · {nm_} 시작 후 {el}초 · 끝나면 {auto_delay()}초 뒤 다음 판"
        elif auto["on"] and auto["fired"] == nxt:
            msg = f"자동 진행 중 ({mode_txt}) · {sname(seq_win['seq'][nxt])} 차례 · 판이 끝나면 {auto_delay()}초 뒤 다음 판"
        elif auto["on"] and auto["pending"]:
            msg = f"{sname(seq_win['seq'][nxt])} 넘기는 중… (키 전송 실패 — 코박스 창을 앞으로 두면 잠시 뒤 다시 보냅니다)"; col = C["gold"]
        elif auto["on"]:
            msg = f"{sname(seq_win['seq'][nxt])} 넘기는 중…"
        else:
            msg = f"자동 진행 꺼짐 ({mode_txt}) — 코박스에서 직접 넘기거나 '건너뛰기 ▶'"
        cfg(seq_win["auto_lbl"], text=msg, fg=col)
        g = seq_win.get("guide"); show_guide = bool(auto["on"] and fresh and nxt is not None)
        if g is not None and g.winfo_exists():
            if show_guide and not g.winfo_manager():
                g.pack(anchor="w", padx=12, pady=(2, 4), after=seq_win["auto_lbl"]); draw_tab_guide(g)
            elif not show_guide and g.winfo_manager(): g.pack_forget()
        if seq_win.get("key_lbl") is not None and seq_win["key_lbl"].winfo_exists():
            kl = key_line(kst) if auto["mode"] == "key" else ("딥링크 방식 — 키를 누르지 않고 매 판 steam:// 링크를 보냅니다", "hint")
            cfg(seq_win["key_lbl"], text=kl[0], fg=C[kl[1]])
        if seq_win["auto_btn"] is not None and seq_win["auto_btn"].winfo_exists():
            seq_win["auto_btn"].sync()

    # ── 자동 진행 엔진 ──
    #   key  방식(기본): 코박스가 자체 플레이리스트로 판을 잇고, 판이 끝나 CSV가 생기면 앱이 PlaylistNext 키를 대신 누른다 (Steam 개입 없음 → 렉 없음)
    #   link 방식      : 판이 끝나면 다음 시나리오 딥링크를 보낸다 (매 판 Steam이 끼어들어 렉·포커스 문제가 날 수 있음)
    def set_hint(text, col=None):
        if seq_alive() and seq_win.get("hint") is not None and seq_win["hint"].winfo_exists():
            seq_win["hint"].configure(text=text, fg=col or C["dim"])

    def press_next():
        """코박스 결과창에서 PlaylistNext 키를 대신 누른다"""
        st = key_st(); key = st["key"]
        if st["unknown"]:
            set_hint(f"'{st['unknown']}' 키는 앱이 보낼 수 없습니다 — 코박스 PlaylistNext 를 F5 같은 키로 바꾸거나 'NEXT 키' 칸에 F5 처럼 적어 주세요", C["val"]); return False
        if not key:
            set_hint("PlaylistNext 키가 없습니다 — 코박스 설정 → 키 설정 → PlaylistNext 에 F10 같은 키를 지정하세요 (앱이 자동으로 읽습니다)", C["val"]); return False
        if not can_send(key):
            set_hint(f"'{key}' 는 앱이 보낼 수 없는 키입니다 — F1~F12·문자·넘패드 키로 바꾸세요", C["val"]); return False
        if not kovaaks_foreground() and not focus_kovaaks():
            set_hint(f"코박스 창이 앞에 있어야 {key} 키를 보낼 수 있습니다 — 게임 창을 클릭하세요 (잠시 뒤 다시 시도)", C["gold"]); return False
        if not send_key(key):
            set_hint(f"{key} 키 전송 실패 — aim_desk.log 확인", C["val"]); return False
        if st["mismatch"]:
            set_hint(f"{key} 키 전송 — ⚠ 코박스 설정의 PlaylistNext 는 {st['mismatch'][1]} 라 게임이 반응하지 않을 수 있습니다. 둘을 같은 키로 맞추세요", C["val"])
        else:
            set_hint(f"{key} 키 전송 ✓")
        return True

    def advance(idx):
        """순서창 idx번 판으로 넘긴다: key 방식은 NEXT 키, link 방식은 딥링크"""
        seq = seq_win["seq"]
        if idx is None or idx >= len(seq): return False
        if auto["mode"] == "link":
            auto["fired_running"] = kovaaks_running()      # 이미 켜져 있었으면 60초+여유, 새로 켜는 거면 로딩까지 감안
            ok = launch_scenario(seq[idx])
            if not ok: show_toast("스팀 실행 실패 — Steam이 켜져 있는지 확인하세요", "warn")
        else:
            auto["fired_running"] = True
            ok = press_next()
        if ok:
            auto.update(fired=idx, due=None, fired_at=time.monotonic(), warned=False, pending=None)
            if auto["mode"] == "key": auto["seen"] = played_count()   # 지금까지 들어온 판은 처리한 것으로 (예약된 자동 전송과 겹치지 않게)
        else: auto.update(due=None, fired=None, pending=(True if auto["mode"] == "key" else idx))   # 다음 틱에 auto_step 이 다시 예약한다
        update_sequence()
        return ok

    def fire_due(idx):
        auto["due"] = None
        if not auto["on"] or not seq_alive(): return
        _, nxt, _ = seq_status()
        if nxt != idx: return                          # 그 사이 상황이 바뀜(다른 판을 쳤거나 건너뜀)
        if auto["fired"] is not None and not kovaaks_running():
            stop_auto("코박스가 꺼져 있어 자동 진행을 멈췄습니다"); return
        advance(idx)

    def detect_restart():
        """key 방식: 순서에 자리가 없는 판이 들어오면(같은 시나리오를 남은 줄 수보다 많이 침) 코박스 플레이리스트를 새로 시작한 것으로 보고 1번부터 다시 센다"""
        by = today_plays_by_key(); seq = seq_win["seq"]; base = seq_win["base"]
        if not any(len(by.get(k, [])) - base.get(k, 0) > seq.count(k) for k in set(seq)): return False
        restart_sequence(detected=True)
        show_toast("코박스 플레이리스트를 새로 시작한 것으로 보여 순서를 1번부터 다시 셉니다 (친 판은 그대로 기록)")
        return True

    def auto_step():
        """스캔 후 호출. key 방식: 새 판(CSV)이 들어왔으면 대기 시간 뒤 NEXT 키 — 포인터가 아니라 '판이 끝났다'는 사실이 기준 (실패했으면 다시 시도).
        link 방식: 다음 차례로 아직 안 넘겼으면 딥링크 예약"""
        if not auto["on"]: return
        if not seq_alive(): auto["on"] = False; return
        if auto["mode"] == "key": detect_restart()
        done, nxt, scores = seq_status()
        if nxt is None:
            stop_auto("오늘 순서 전부 완료 🎉 수고했어요"); return
        if auto["mode"] == "link":
            if auto["fired"] == nxt or auto["due"] == nxt: return
            auto["due"] = nxt
            root.after(auto_delay() * 1000, lambda: fire_due(nxt)); return
        played = sum(1 for i in range(len(done)) if done[i] and scores[i] is not None)
        if auto["seen"] is None: auto["seen"] = played
        if auto["due"] is not None: return
        if played > auto["seen"] or auto["pending"]:
            auto["due"] = played
            root.after(auto_delay() * 1000, lambda: fire_key(played))

    def fire_key(p):
        """key 방식: 판이 끝났으니(CSV) 결과창에서 NEXT 키. 그 사이 수동으로 넘겼으면(seen 이 이미 p) 안 누른다"""
        auto["due"] = None
        if not auto["on"] or not seq_alive(): return
        if not kovaaks_running(): stop_auto("코박스가 꺼져 있어 자동 진행을 멈췄습니다"); return
        if p <= (auto["seen"] or 0) and not auto["pending"]: return
        _, nxt, _ = seq_status()
        if nxt is None: stop_auto("오늘 순서 전부 완료 🎉 수고했어요"); return
        if press_next(): auto.update(seen=max(p, auto["seen"] or 0), fired=nxt, fired_at=time.monotonic(), warned=False, pending=None)
        else: auto.update(fired=None, pending=True)
        update_sequence()

    def stop_auto(msg=None):
        auto["on"] = False; auto["due"] = None
        if msg: show_toast(msg)
        update_sequence()

    def set_auto(v):
        auto["on"] = bool(v)
        if auto["on"]:
            _, nxt, _ = seq_status()
            if auto["mode"] == "link":
                if nxt is not None and auto["fired"] != nxt: advance(nxt)     # 켜는 즉시 현재 차례를 보낸다
            elif auto["pending"]: auto.update(fired=None, due=None)          # 전송에 실패해 기다리는 판이면 다시 시도하게 둔다
            else: auto.update(fired=nxt, due=None, fired_at=None, seen=played_count())   # 지금 치고 있는 판이 현재 차례라고 본다
        update_sequence()

    def set_mode_link(v):
        auto["mode"] = "link" if v else "key"
        data["auto_mode"] = auto["mode"]; save_data(data)
        if auto["on"] and auto["mode"] == "key":
            _, nxt, _ = seq_status()
            if auto["pending"]: auto.update(fired=None, due=None, pending=True)
            else: auto.update(fired=nxt, due=None, fired_at=None, seen=played_count())
        update_sequence()

    def set_topmost(v):
        data["seq_topmost"] = bool(v); save_data(data)
        if seq_alive(): seq_win["win"].attributes("-topmost", bool(v))

    def set_compact(v):
        data["seq_compact"] = bool(v); save_data(data); update_sequence()

    def skip_current():
        """지금 차례를 건너뛰고 다음 판으로 바로 넘긴다"""
        _, nxt, _ = seq_status()
        if nxt is None: return
        seq_win["skipped"].add(nxt)
        _, nxt2, _ = seq_status()
        if nxt2 is None: stop_auto("오늘 순서 전부 완료 🎉"); return
        if not advance(nxt2) and not auto["on"]:
            seq_win["skipped"].discard(nxt); update_sequence()          # 자동 진행이 꺼져 있으면 재시도가 없으니 표시를 되돌린다

    def unskip(i):
        """건너뜀 표시를 되돌린다 (줄의 '–' 클릭)"""
        if i in seq_win["skipped"]:
            seq_win["skipped"].discard(i); update_sequence()

    def resend_current():
        _, nxt, _ = seq_status()
        if nxt is not None: advance(nxt)

    def restart_sequence(detected=False):
        """지금까지 친 판은 그대로 두고 순서를 1번부터 다시 (오늘 두 번째 세션용).
        detected=True 는 자동 감지(자리 없는 판이 들어옴): 이전 순서가 쓴 판까지만 제외하고, 방금 들어온 판은 새 순서의 1번부터 배정"""
        if detected:
            seq_status(); used = seq_win.get("used", {}); base = seq_win["base"]
            seq_win["base"] = {k: base.get(k, 0) + used.get(k, 0) for k in set(base) | set(used)}
        else:
            seq_win["base"] = {k: len(v) for k, v in today_plays_by_key().items()}
        seq_win["skipped"] = set()
        auto.update(fired=None, due=None, fired_at=None, pending=None, seen=0, start_played=0, warned=False)
        if auto["on"] and auto["mode"] == "link": advance(0)
        elif auto["on"] and not detected:
            auto["fired"] = 0
            set_hint("코박스에서 플레이리스트를 처음부터 다시 시작하세요 — 판이 끝나면 앱이 NEXT 키로 넘깁니다", C["gold"])
        update_sequence()

    def run_playlist(plname):
        sd = data.get("stats_dir"); wrote = 0
        if sd: _, _, wrote = ensure_playlists(sd, today_key[0], data["pb"])   # 오늘 테마로 로컬 플레이리스트 설치
        was_running = kovaaks_running()
        if wrote and was_running:                      # 코박스는 시작할 때 Playlists 폴더를 읽는다 — 켜진 채로 새로 쓴 파일은 재시작해야 보인다
            show_toast("⚠ 플레이리스트를 새로 설치했습니다 — 코박스가 켜져 있었다면 껐다 켜야 '로컬 재생 목록'에 보입니다", "warn")
        open_sequence(plname)
        if not seq_win["seq"] or not seq_alive():
            if not launch_kovaaks(): show_toast("스팀 실행 실패 — Steam이 켜져 있는지 확인하고 코박스를 직접 실행하세요", "warn")
            return
        _, nxt, _ = seq_status()
        if auto["mode"] == "link":
            auto.update(on=True, fired=None, due=None)
            if nxt is None: restart_sequence()         # 오늘 이미 다 쳤으면 1번부터 한 번 더
            else: advance(nxt)
            show_toast(f"▶ 딥링크 자동 진행 — 한 판이 끝나면 {auto_delay()}초 뒤 다음 시나리오를 보냅니다. 결과창에선 아무것도 누르지 마세요")
            return
        if not kovaaks_running():
            launch_kovaaks()                            # 게임만 켠다 (딥링크 없음)
        if nxt is None: restart_sequence()
        auto.update(on=True, fired=(0 if nxt is None else nxt), due=None, fired_at=None, warned=False, pending=None,
                    seen=played_count(), start_played=played_count())
        st = key_st(); key = st["key"]
        target = plname or "AIMDESK Bench"
        if key and not st["mismatch"]:
            set_hint(f"판이 끝나면 앱이 {auto_delay()}초 뒤 {key} 키로 다음 판을 넘깁니다 — 결과창에선 아무것도 누르지 말고 기다리세요", C["ok"])
            show_toast(f"▶ 코박스에서 '로컬 재생 목록' → {target} 를 재생하세요 — 판이 끝날 때마다 앱이 {key} 키로 다음 판을 넘깁니다")
        elif key:
            set_hint(f"⚠ 코박스 설정의 PlaylistNext 는 {st['mismatch'][1]} 인데 앱은 {key} 를 누릅니다 — 둘을 같은 키로 맞추세요", C["val"])
            show_toast(f"⚠ NEXT 키가 코박스 설정({st['mismatch'][1]})과 다릅니다 — 순서창 아래 안내를 보세요", "warn")
        else:
            set_hint("NEXT 키가 아직 없습니다: 코박스 설정 → 키 설정 → PlaylistNext 에 F10 지정 (앱이 자동으로 읽음 · 못 읽으면 위 칸에 F10). "
                     f"그 다음 '로컬 재생 목록' → {target} ▶ 플레이", C["val"])
            show_toast("코박스 설정 → 키 설정 → PlaylistNext 에 F10 을 지정하세요 — 앱이 자동으로 읽습니다", "warn")
        update_sequence()

    # ── 시나리오 상세 팝업 (루틴 줄·순서창·스파크·벤치 이름 클릭) ──
    detail = {"win": None, "key": None, "cv": None, "title": None, "sum": None}
    def draw_scen_detail(cv, hist, th, pb, col):
        cv.delete("all"); W = max(cv.winfo_width(), px(400)); H = px(220)
        L, R, T, B = px(50), px(86), px(14), px(22)
        pts_b = [(i, h["best"]) for i, h in enumerate(hist) if h["best"] is not None]
        pts_f = [(i, h["first"]) for i, h in enumerate(hist) if h["first"] is not None]
        vals = [v for _, v in pts_b + pts_f]
        if not vals:
            cv.create_text(W / 2, H / 2, text="아직 기록이 없습니다", fill=C["hint"], font=F); return
        lo, hi = min(vals), max(vals)
        if th:
            below = [t for t in th if t <= lo]; above = [t for t in th if t > hi]
            lo = min(lo, below[-1]) if below else lo * 0.9
            hi = max(hi, above[0]) if above else hi
        span = max(1, hi - lo); lo -= span * 0.06; hi += span * 0.06
        n = len(hist)
        X = lambda i: L + (W - L - R) * (0.5 if n < 2 else i / (n - 1))
        Y = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))
        if th:
            for i, t in enumerate(th):
                if lo <= t <= hi:
                    cv.create_line(L, Y(t), W - R, Y(t), fill=RANKC[i], dash=(3, 4))
                    cv.create_text(W - R + px(6), Y(t), text=f"{RANK_NAMES[i]} {t}", anchor="w", fill=RANKC[i], font=FNS)
        if len(pts_b) > 1:
            cv.create_line(*[c for i, v in pts_b for c in (X(i), Y(v))], fill=col, width=2, smooth=True)
        for i, v in pts_f: cv.create_oval(X(i) - 2, Y(v) - 2, X(i) + 2, Y(v) + 2, fill=C["dim"], outline="")
        for i, v in pts_b:
            r_ = 4 if v == pb else 3
            cv.create_oval(X(i) - r_, Y(v) - r_, X(i) + r_, Y(v) + r_, fill=C["gold"] if v == pb else col, outline="")
        cv.create_text(L, H - px(8), text=hist[0]["date"][5:], anchor="w", fill=C["dim"], font=FNS)
        cv.create_text(W - R, H - px(8), text=hist[-1]["date"][5:], anchor="e", fill=C["dim"], font=FNS)
        cv.create_text(L - px(6), Y(vals[-1]), text="", anchor="e")
        cv.create_text(px(6), T + px(6), text="선 = 일별 베스트 · 점 = 첫 판 · 금색 = PB", anchor="nw", fill=C["dim"], font=FS)

    def update_detail():
        w = detail["win"]
        if w is None or not w.winfo_exists() or not detail["key"]: return
        k = detail["key"]; sub = sub_of(k)
        sm = scen_summary(data, k, today_key[0])
        cfg(detail["title"], text=f"{sname(k)} · {sub[1]} {sub[2]}" if sub else sname(k))
        cfg(detail["sum"], text=fmt_scen_summary(sm) or "아직 기록이 없습니다")
        draw_scen_detail(detail["cv"], sm["hist"], th_of(k), sm["pb"], C["val"] if SCEN[k][1] == "v" else C["ow"])

    def open_detail(key):
        detail["key"] = key
        w = detail["win"]
        if w is None or not w.winfo_exists():
            w = tk.Toplevel(root); detail["win"] = w
            w.title("시나리오 상세"); w.configure(bg=C["bg"]); w.resizable(False, False)
            w.geometry(f"{px(560)}x{px(300)}+{root.winfo_x() + px(120)}+{root.winfo_y() + px(120)}")
            if seq_alive() and bool(data.get("seq_topmost", True)): w.attributes("-topmost", True)   # 항상 위 순서창 밑에 깔리지 않게
            hd = tk.Frame(w, bg=C["bg"]); hd.pack(fill="x", padx=12, pady=(10, 2))
            detail["title"] = tk.Label(hd, text="", font=FH, bg=C["bg"], fg=C["txt"]); detail["title"].pack(side="left")
            detail["sum"] = tk.Label(w, text="", font=FNS, bg=C["bg"], fg=C["sub"], wraplength=px(540), justify="left")
            detail["sum"].pack(anchor="w", padx=12)
            detail["cv"] = tk.Canvas(w, width=px(540), height=px(220), bg=C["card"], highlightthickness=0)
            detail["cv"].pack(padx=12, pady=(8, 12))
            detail["cv"].bind("<Configure>", lambda e: update_detail())
            w.bind("<Escape>", lambda e: w.destroy())
        else:
            w.lift()
        update_detail()

    def draw_ribbon(cv, cells, pop=None):
        """한 칸 = 한 판. 아직 안 친 칸은 어둡게, 끝난 칸은 판정 색으로. pop 은 방금 채워진 칸(살짝 크게)"""
        cv.delete("all")
        n = len(cells)
        if not n: return
        W = max(cv.winfo_width(), px(240)); H = max(cv.winfo_height(), px(24))
        gap = px(2) if n <= 40 else 1
        tw = (W - gap * (n - 1)) / n
        base = H - px(4)                                   # 바닥을 맞추고 위로 자란다
        full = H - px(8)
        for i, key in enumerate(cells):
            x1 = i * (tw + gap); x2 = x1 + tw
            grow = px(3) if (pop is not None and i == pop) else 0
            h = full * RIBBON_H.get(key, 0.56) + grow
            y1, y2 = base - h, base
            fill = C["card2"] if key == "todo" else C[key]
            if tw >= px(5): rrect(cv, x1, y1, x2, y2, min(px(3), tw / 2, h / 2), fill=fill, outline="")
            else: cv.create_rectangle(x1, y1, x2, y2, fill=fill, outline="", width=0)

    def ribbon_pop(cv, cells, i, frame=0):
        """방금 채워진 칸이 커졌다 돌아온다 — 6프레임 240ms 로 끝나고 타이머를 남기지 않는다"""
        if not cv.winfo_exists(): return
        if frame >= 6: draw_ribbon(cv, cells); return
        draw_ribbon(cv, cells, pop=i if frame < 3 else None)
        root.after(40, lambda: ribbon_pop(cv, cells, i, frame + 1))

    def today_plan_n():
        """오늘 계획된 판 수 (띠 칸 수)"""
        pl = day_state.get("pl")
        if pl: return sum(n for _, n in dict(playlists_for(today_key[0], data["pb"]))[pl])
        return 18 if day_state.get("dt") == "b" else 0

    # ── 방송 화면: 시청자가 3초 안에 알아야 할 것만. 글씨 크기를 창 높이에 비례시켜(음수 = 픽셀)
    #    OBS 창 캡처로 키우면 그대로 커진다 — 본창 배율과 따로 논다.
    bcast = {"win": None, "cv": None}

    def draw_broadcast(cv):
        cv.delete("all")
        W = max(cv.winfo_width(), 320); H = max(cv.winfo_height(), 120)
        fam = lambda fr, b=True: tkfont.Font(family=FAM, size=-max(11, int(H * fr)), weight="bold" if b else "normal")
        mon = lambda fr: tkfont.Font(family=MONO, size=-max(11, int(H * fr)), weight="bold")
        dkey = today_key[0]; cp = cur_plays()
        kinds = [k_ for _, _, k_ in day_verdicts(data, dkey, cp)]
        plan = today_plan_n(); pad = int(W * 0.025)
        dt = day_state.get("dt", "v")
        top = main_theme(dkey, data["pb"])[1] if dt == "v" else DAY_TYPE.get(dt, ("훈련", ""))[0]
        cv.create_text(pad, int(H * 0.14), text=top, anchor="w", fill=C["gold"], font=fam(0.135))
        cv.create_text(W - pad, int(H * 0.14), text=f"{len(kinds)}/{max(plan, len(kinds))}판",
                       anchor="e", fill=C["sub"], font=mon(0.135))
        cur_k = None                                  # 진행 중이면 '지금 치는 판', 아니면 방금 끝난 판
        if seq_alive():
            _dn, _nx, _sc = seq_status()
            if _nx is not None: cur_k = seq_win["seq"][_nx]
        if cp:
            k_, _t_, sc_ = cp[-1]
            kind = kinds[-1] if kinds else "new"
            col = C[VERDICT_FILL.get(kind, "sub")]
            live = cur_k is not None
            cv.create_text(pad, int(H * 0.46), text=("▶ " if live else "") + sname(cur_k or k_),
                           anchor="w", fill=C["txt"] if live else C["sub"], font=fam(0.21))
            cv.create_text(W - pad, int(H * 0.44), text=str(sc_), anchor="e", fill=col, font=mon(0.30))
            nm = VERDICT_NAME.get(kind, "")
            sub_ = (f"직전 {sname(k_)} · {nm}" if live else nm)
            if sub_: cv.create_text(pad, int(H * 0.66), text=sub_, anchor="w", fill=col, font=fam(0.13))
        elif cur_k:
            cv.create_text(pad, int(H * 0.46), text="▶ " + sname(cur_k), anchor="w", fill=C["txt"], font=fam(0.21))
            cv.create_text(W - pad, int(H * 0.46), text="첫 판", anchor="e", fill=C["hint"], font=fam(0.14, False))
        else:
            cv.create_text(W / 2, int(H * 0.48), text="첫 판을 치면 여기에 뜹니다",
                           fill=C["hint"], font=fam(0.13, False))
        cells = ribbon_cells(plan, kinds)
        n = max(1, len(cells)); y1, y2 = int(H * 0.73), int(H * 0.95)
        gap = max(1, int(W * 0.0022)); tw = (W - 2 * pad - gap * (n - 1)) / n
        for i, ck in enumerate(cells):
            x1 = pad + i * (tw + gap); h = (y2 - y1) * RIBBON_H.get(ck, 0.56)
            cv.create_rectangle(x1, y2 - h, x1 + tw, y2,
                                fill=C["card2"] if ck == "todo" else C[ck], outline="", width=0)

    def remember_bcast():
        w = bcast["win"]
        if w is not None and w.winfo_exists(): data["win"]["bcast"] = w.winfo_geometry()

    def update_broadcast():
        if bcast["win"] is not None and bcast["win"].winfo_exists() and bcast["cv"].winfo_exists():
            draw_broadcast(bcast["cv"])

    def open_broadcast():
        w = bcast["win"]
        if w is None or not w.winfo_exists():
            w = tk.Toplevel(root); bcast["win"] = w
            w.title("에임 데스크 — 방송 화면"); w.configure(bg=C["bg"])
            w.minsize(px(360), px(120))
            cv = tk.Canvas(w, bg=C["bg"], highlightthickness=0, width=px(880), height=px(220))
            cv.pack(fill="both", expand=True); bcast["cv"] = cv
            cv.bind("<Configure>", lambda e: draw_broadcast(cv))
            w.bind("<Escape>", lambda e: (remember_bcast(), w.destroy()))
            w.protocol("WM_DELETE_WINDOW", lambda: (remember_bcast(), w.destroy()))
            g = data["win"].get("bcast")
            if g: w.geometry(g)                       # 지난번 크기·위치 그대로 (OBS 소스가 어긋나지 않게)
        else:
            w.lift()
        update_broadcast()

    card_win = {"win": None, "cv": None}

    def draw_card(cv, sc):
        cv.delete("all")
        W = max(cv.winfo_width(), px(600)); H = max(cv.winfo_height(), px(220))
        x0 = px(22); y = px(28)
        cv.create_text(x0, y, text=sc["title"], anchor="w", fill=C["txt"], font=FH); y += px(28)
        cv.create_text(x0, y, text=sc["stat"], anchor="w", fill=C["sub"], font=F); y += px(24)
        cells = ribbon_cells(len(sc["kinds"]), sc["kinds"])
        n = max(1, len(cells)); gap = px(2); bw = W - 2 * x0; tw = (bw - gap * (n - 1)) / n
        rh = px(22)
        for i, ck in enumerate(cells):
            x1 = x0 + i * (tw + gap); h = rh * RIBBON_H.get(ck, 0.56)
            fill = C["card2"] if ck == "todo" else C[ck]
            if tw >= px(5): rrect(cv, x1, y + rh - h, x1 + tw, y + rh, min(px(3), tw / 2, h / 2), fill=fill, outline="")
            else: cv.create_rectangle(x1, y + rh - h, x1 + tw, y + rh, fill=fill, outline="", width=0)
        y += px(43)
        cv.create_text(x0, y, text="오늘 바뀐 것", anchor="w", fill=C["gold"], font=FCAP); y += px(22)
        if sc["changed"]:
            for line in sc["changed"]:
                cv.create_text(x0 + px(6), y, text="· " + line, anchor="w", fill=C["txt"], font=F); y += px(21)
        else:
            cv.create_text(x0 + px(6), y, text="기록이 바뀐 건 없습니다 — 판을 쌓은 것도 그대로 남습니다",
                           anchor="w", fill=C["hint"], font=FS); y += px(21)
        if sc["gain"]:
            y += px(8); cv.create_text(x0, y, text=sc["gain"], anchor="w", fill=C["ok"], font=FS)
        if sc["next"]: cv.create_text(x0, H - px(22), text=sc["next"], anchor="w", fill=C["sub"], font=FS)
        cv.create_text(W - x0, H - px(22), text="아무 곳이나 누르면 닫힘", anchor="e", fill=C["dim"], font=FS)

    def open_card():
        dkey = today_key[0]; dt = day_state.get("dt", "v")
        sc = session_card(data, dkey, DAY_TYPE[dt][0],
                          main_theme(dkey, data["pb"])[1] if dt == "v" else "", cur_plays())
        CH = px(150) + px(21) * max(1, len(sc["changed"])) + px(56)      # 내용만큼만 — 빈 카드가 커 보이지 않게
        w = card_win["win"]
        if w is None or not w.winfo_exists():
            w = tk.Toplevel(root); card_win["win"] = w
            w.title("오늘 한 장"); w.configure(bg=C["bg"]); w.resizable(False, False)
            cv = tk.Canvas(w, width=px(620), height=CH, bg=C["card"], highlightthickness=0)
            cv.pack(padx=px(10), pady=px(10)); card_win["cv"] = cv
            cv.bind("<Button-1>", lambda e: w.destroy())
            w.bind("<Escape>", lambda e: w.destroy())
            w.geometry(clamp_pos("+%d+%d" % (root.winfo_x() + px(80), root.winfo_y() + px(70)),
                                 px(640), px(450), *vroot) or "")
            if seq_alive() and bool(data.get("seq_topmost", True)): w.attributes("-topmost", True)
        else:
            w.lift()
        if int(card_win["cv"].cget("height")) != CH: card_win["cv"].configure(height=CH)
        card_win["cv"].update_idletasks()
        draw_card(card_win["cv"], sc)

    def add_section(title, extra=None):
        f = tk.Frame(left_scroll.body, bg=C["card"]); f.pack(fill="x", pady=(10, 3))
        lb = tk.Label(f, text=title, font=FCAP, bg=C["card"], fg=C["gold"]); lb.pack(side="left")
        tk.Frame(f, bg=C["line"], height=1).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=1)
        section_labels.append((lb, title, len(routine_rows), extra))

    def add_row(kind, key, target):
        row = tk.Frame(left_scroll.body, bg=C["card"]); row.pack(fill="x", pady=2)
        grp = SCEN[key][1]
        gc = C["val"] if grp == "v" else C["ow"]
        mark = tk.Label(row, text="", font=FNS, width=2, bg=C["card"], fg=C["gold"]); mark.pack(side="left")
        tk.Frame(row, bg=gc, width=px(3), height=px(16)).pack(side="left", padx=(0, 9))
        nml = tk.Label(row, text=sname(key), font=F, width=13, anchor="w", bg=C["card"], fg=C["txt"], cursor="hand2"); nml.pack(side="left")
        nml.bind("<Button-1>", lambda e, k=key: open_detail(k))
        bar = tk.Canvas(row, width=px(60), height=px(8), bg=C["card"], highlightthickness=0)   # 기본 요청폭(378px)이면 오른쪽 점수 칸이 잘린다
        bar.pack(side="left", fill="x", expand=True, padx=(4, 10))
        cl = tk.Label(row, text="", font=FNS, width=7, anchor="e", bg=C["card"], fg=C["sub"])
        cl.pack(side="left")
        sl = tk.Label(row, text="", font=FNS, width=24 if kind == "bench" else 12, anchor="e", bg=C["card"], fg=C["dim"])
        sl.pack(side="left")
        routine_rows.append((kind, key, target, bar, cl, sl, gc, mark, nml, row))

    def build_day_ui():
        """헤더의 날짜·요일 칩과 좌측 루틴 카드를 '오늘' 기준으로 (다시) 만든다"""
        d = today_date()
        dt = ["v","v","v","v","w","b","r"][d.weekday()]
        day_state["dt"] = dt
        day_state["pl"] = {"v": "AIMDESK Day", "w": "AIMDESK Friday", "b": "AIMDESK Bench"}.get(dt)
        dt_name, dt_col = DAY_TYPE[dt]
        date_lbl.configure(text=f"{d.month}월 {d.day}일 {DOWK[d.weekday()]}")
        daych.delete("all")
        rrect(daych, 0, 1, px(68), px(17), 8, fill=dt_col, outline="")
        daych.create_text(px(34), px(9), text=dt_name, fill="#0B0E11", font=(FAM, 8, "bold"))

        for w_ in left_scroll.body.winfo_children(): w_.destroy()
        routine_rows.clear(); section_labels.clear(); routine_next[0] = None
        lh = tk.Frame(left_scroll.body, bg=C["card"]); lh.pack(fill="x")
        lt = tk.Frame(lh, bg=C["card"]); lt.pack(side="left")
        tk.Label(lt, text="오늘 루틴", font=FH, bg=C["card"], fg=C["txt"]).pack(anchor="w")
        pl = day_state["pl"]
        tk.Label(lt, text=(f"▶ 실행 → 코박스 ESC → 샌드박스 브라우저 → 네 번째 탭 '로컬 재생 목록' → {pl} ▶ 플레이 ('도전 과제' 토글). "
                           "판이 끝나면 앱이 NEXT 키를 대신 눌러 다음 판으로 — 결과창에선 기다리기") if pl else "오늘은 휴식 — 컨디션만 적어도 됩니다",
                 font=FS, bg=C["card"], fg=C["hint"], wraplength=px(250), justify="left").pack(anchor="w", pady=(0, 2))   # 250: 최소 폭에서도 오른쪽 버튼 3개가 잘리지 않게
        _tl = theme_line(today_key[0], data["pb"])
        if _tl:
            tk.Label(lt, text=_tl, font=FB, bg=C["card"], fg=C["gold"], wraplength=px(250),
                     justify="left").pack(anchor="w", pady=(2, 0))
        _wt = week_themes(today_key[0], data["pb"])
        if _wt:
            tk.Label(lt, text=_wt, font=FS, bg=C["card"], fg=C["dim"], wraplength=px(250),
                     justify="left").pack(anchor="w", pady=(0, 2))
        day_state["sess_lbl"] = tk.Label(lt, text="", font=FNS, bg=C["card"], fg=C["sub"], wraplength=px(250), justify="left")
        day_state["sess_lbl"].pack(anchor="w", pady=(0, 4))
        day_state["coach"] = []
        for _i in range(3):
            cl_ = tk.Label(lt, text="", font=FS, bg=C["card"], fg=C["sub"], wraplength=px(520), justify="left")
            cl_.pack(anchor="w"); day_state["coach"].append(cl_)
        if pl:
            RBtn(lh, "▶ 벤치 18개 실행" if dt == "b" else "▶ 오늘 루틴 실행", lambda: run_playlist(pl),
                 bg="#2A1512", fg=C["val"], padx=14, pady=8).pack(side="right", padx=(8, 0))
            if dt != "b":
                RBtn(lh, "프로브만", lambda: run_playlist("AIMDESK Probe"),
                     padx=12, pady=8).pack(side="right", padx=(8, 0))
            RBtn(lh, "순서 보기", lambda: open_sequence(pl), padx=12, pady=8).pack(side="right")

        day_state["chal"] = daily_challenge(data, today_key[0], data["pb"])
        day_state["chal_lbl"] = None
        if day_state["chal"]:
            cf = tk.Frame(left_scroll.body, bg=C["card2"], highlightbackground=C["gold"], highlightthickness=1)
            cf.pack(fill="x", pady=(8, 0), ipady=px(5), ipadx=px(8))
            day_state["chal_lbl"] = tk.Label(cf, text="", font=FB, bg=C["card2"], fg=C["gold"],
                                             wraplength=px(520), justify="left", anchor="w")
            day_state["chal_lbl"].pack(fill="x", padx=px(8))
        rib = tk.Frame(left_scroll.body, bg=C["card"]); rib.pack(fill="x", pady=(8, 0))
        day_state["rib_cv"] = tk.Canvas(rib, height=px(34), bg=C["card"], highlightthickness=0)
        day_state["rib_cv"].pack(fill="x")
        rl = tk.Frame(rib, bg=C["card"]); rl.pack(fill="x", pady=(4, 0))
        day_state["rib_lbl"] = tk.Label(rl, text="", font=FNS, bg=C["card"], fg=C["sub"], anchor="w")
        day_state["rib_lbl"].pack(side="left")
        RBtn(rl, "오늘 한 장", open_card, padx=10, pady=3).pack(side="right")
        day_state["rib_cells"] = []

        if dt in ("v", "w"):
            add_section("① 워밍업 · 트래킹 → 정확 → 속도 (점수 무시)")
            for k, n in WARMUP: add_row("warm", k, n)
            add_section("② 프로브 · 그날 첫 판이 측정값")
            for k in PROBE: add_row("probe", k, 1)
            if dt == "v":
                mt = main_theme(today_key[0], data["pb"])
                add_section(f"③ 본훈련 · {mt[1]}")
                for k, n in mt[3]: add_row("main", k, n)
            else:
                add_section("③ 금요일 약점 · 컨트롤")
                for k, n in FRIDAY: add_row("main", k, n)
            add_section("④ 게임 · 미야기 → 랭크 2판 → 죽음 태그", extra=[("check", "miyagi", 1), ("check", "ranked", 1)])
            tk.Label(left_scroll.body, text="미야기: DM에서 안 쏘고 머리만 따라가기 · 녹화 켜기",
                     font=FS, bg=C["card"], fg=C["hint"]).pack(anchor="w", padx=14)
        elif dt == "b":
            tk.Label(left_scroll.body, text="벤치마크 18개 풀런 · 오늘 베스트 기준 · 점수 옆은 다음 등급까지 남은 점수 · 벤치 탭에 실시간 반영",
                     font=FS, bg=C["card"], fg=C["hint"], wraplength=px(520), justify="left").pack(anchor="w", pady=(6, 0))
            for i, (sid, cat, sub, items) in enumerate(SUBS):
                add_section(f"{'①②③④⑤⑥⑦⑧⑨'[i]} {cat} · {sub}")
                for k, _th in items: add_row("bench", k, 1)
        else:
            add_section("휴식")
            tk.Label(left_scroll.body, text="손목도 데이터의 일부입니다. 오늘은 컨디션만 적어도 됩니다.",
                     font=F, bg=C["card"], fg=C["sub"]).pack(anchor="w", pady=6)

    # 우측 카드들 (스크롤 본체 안)
    ck = card(rbody); ck.pack(fill="x", pady=(0, 10))
    tk.Label(ck, text="했나요", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 7))
    tr = tk.Frame(ck, bg=C["card"]); tr.pack(anchor="w")
    tg1 = Toggle(tr, "미야기 완료", lambda: dget()["checks"]["miyagi"],
                 lambda v: (dget()["checks"].__setitem__("miyagi", v), save_data(data), refresh()))
    tg1.pack(side="left", padx=(0, 8))
    tg2 = Toggle(tr, "랭크 2판", lambda: dget()["checks"]["ranked"],
                 lambda v: (dget()["checks"].__setitem__("ranked", v), save_data(data), refresh()))
    tg2.pack(side="left")

    dk = card(rbody); dk.pack(fill="x", pady=(0, 10))
    tk.Label(dk, text="오늘 죽은 이유", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w")
    tk.Label(dk, text="랭크 리뷰하며 + 누르기", font=FS, bg=C["card"], fg=C["dim"]).pack(anchor="w", pady=(0, 6))
    steppers = []
    for key, name in (("aim","에임"),("pos","위치"),("dec","판단"),("trade","트레이드")):
        row = tk.Frame(dk, bg=C["card"]); row.pack(fill="x", pady=2)
        tk.Label(row, text=name, font=F, width=8, anchor="w", bg=C["card"], fg=C["txt"]).pack(side="left")
        st_ = Stepper(row,
                      lambda k=key: dget()["deaths"][k],
                      lambda v, k=key: (dget()["deaths"].__setitem__(k, v), save_data(data), sync_deaths_lbl(), dirty.__setitem__("log", True)))
        st_.pack(side="right"); steppers.append(st_)
    dth_lbl = tk.Label(dk, text="", font=FS, bg=C["card"], fg=C["hint"], wraplength=px(270), justify="left")
    dth_lbl.pack(anchor="w", pady=(6, 0))
    def sync_deaths_lbl():
        t_, c_ = fmt_deaths_trend(deaths_trend(data, today_key[0])); cfg(dth_lbl, text=t_, fg=c_)

    cd = card(rbody); cd.pack(fill="x", pady=(0, 10))
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
            save_data(data); ent.configure(fg=C["txt"]); refresh()
        except ValueError:
            ent.configure(fg=C["val"])          # 잘못된 값은 빨갛게 표시, 저장 안 됨
    ent.bind("<Return>", commit_sleep); ent.bind("<FocusOut>", commit_sleep)
    sync_sleep_entry()
    rowf = tk.Frame(cd, bg=C["card"]); rowf.pack(fill="x", pady=(8, 0))
    tk.Label(rowf, text="체감", font=FS, bg=C["card"], fg=C["sub"]).pack(side="left")
    seg = Segmented(rowf, lambda: dget()["cond"]["feel"],
                    lambda v: (dget()["cond"].__setitem__("feel", v), save_data(data), refresh()))
    seg.pack(side="left", padx=(8, 0))

    stc = card(rbody); stc.pack(fill="x")
    tk.Label(stc, text="코박스 stats 폴더", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w")
    stats_lbl = tk.Label(stc, text="", font=(MONO, 8), bg=C["card"], fg=C["hint"],
                         wraplength=px(270), justify="left")
    stats_lbl.pack(anchor="w", pady=(4, 6))
    def pick_stats():
        p = filedialog.askdirectory(title="…\\FPSAimTrainer\\FPSAimTrainer\\stats 선택")
        if p: data["stats_dir"] = p; save_data(data); sync_stats_lbl()
    plrow = tk.Frame(stc, bg=C["card"]); plrow.pack(fill="x", pady=(0, 2))
    RBtn(plrow, "폴더 선택", pick_stats, padx=12, pady=5).pack(side="left")
    RBtn(plrow, "플레이리스트 재설치", lambda: (install_playlists(), None),
         padx=12, pady=5).pack(side="left", padx=(8, 0))
    plrow2 = tk.Frame(stc, bg=C["card"]); plrow2.pack(fill="x", pady=(6, 0))
    RBtn(plrow2, "플레이리스트 폴더 열기", lambda: (PL_STATE["dir"] and open_uri(str(PL_STATE["dir"])), None),
         padx=12, pady=5).pack(side="left")
    pl_lbl = tk.Label(stc, text="", font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left"); pl_lbl.pack(anchor="w", pady=(5, 0))

    # ── 화면 (녹화·방송) ──
    vc = card(rbody); vc.pack(fill="x", pady=(10, 0))
    tk.Label(vc, text="화면 · 녹화", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 4))
    tk.Label(vc, text="녹화하면 시청자 쪽에서 글씨가 뭉갭니다. 크기를 올리면 저장하고 앱을 다시 켜서 적용합니다.",
             font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left").pack(anchor="w", pady=(0, 7))
    srow = tk.Frame(vc, bg=C["card"]); srow.pack(anchor="w")
    srow2 = tk.Frame(vc, bg=C["card"]); srow2.pack(anchor="w", pady=(4, 0))
    scale_btns = {}

    def restart_app() -> bool:
        """새 창으로 다시 켠다 — 창 크기·글씨는 시작할 때 한 번 정해지기 때문"""
        if os.environ.get("AIMDESK_NO_MAINLOOP"): return False        # 테스트에선 프로세스를 띄우지 않는다
        try:
            import subprocess
            args = ([sys.executable] if getattr(sys, "frozen", False)
                    else [sys.executable, os.path.abspath(sys.argv[0])]) + list(sys.argv[1:])
            env = dict(os.environ); env["AIMDESK_RESTART"] = "1"
            kw = {"creationflags": getattr(subprocess, "DETACHED_PROCESS", 0)} if sys.platform == "win32" else {}
            subprocess.Popen(args, env=env, **kw)
        except Exception:
            log_exc("restart_app"); return False
        try: root._aimdesk_lock.close()                               # 새 창이 잠금을 잡을 수 있게 먼저 놓아준다
        except Exception: pass
        root.after(200, root.destroy)
        return True

    def sync_scale_btns():
        cur = data.get("ui_scale")
        for v, b in scale_btns.items():
            on = (v == cur) or (v is None and not cur)
            b.restyle(bg=C["gold"] if on else C["card2"], fg="#10141A" if on else C["txt"])

    def set_scale(v):
        if (data.get("ui_scale") or None) == (v or None): return
        data["win"].pop("geo", None); data["win"].pop("seq", None)    # 새 배율에 맞는 기본 크기로 열리게
        data["ui_scale"] = v
        data["win"].update(zoomed=False, tab=cur_tab[0])
        save_data(data); sync_scale_btns()
        if SAVE_ERROR[0]:
            show_toast("저장에 실패해 크기를 바꾸지 못했습니다", "warn"); return
        if not restart_app():
            show_toast(f"글씨 크기 {scale_label(v)} — 앱을 껐다 켜면 적용됩니다")

    for _i, _v in enumerate([None] + SCALE_STEPS):          # 두 줄로 — 배율을 올리면 한 줄에 안 들어간다
        _b = RBtn(srow if _i < 3 else srow2, scale_label(_v), (lambda v=_v: set_scale(v)), padx=7, pady=4)
        _b.pack(side="left", padx=(0, 4)); scale_btns[_v] = _b
    sync_scale_btns()
    RBtn(vc, "방송 화면 열기", open_broadcast, bg="#1B2A22", fg=C["ok"], padx=12, pady=6).pack(anchor="w", pady=(8, 0))
    brow = tk.Frame(vc, bg=C["card"]); brow.pack(anchor="w", pady=(8, 0))
    def set_broadcast(v):
        if bool(data.get("broadcast")) == bool(v): return
        data["broadcast"] = bool(v); save_data(data)
        if SAVE_ERROR[0]:
            show_toast("저장에 실패해 바꾸지 못했습니다", "warn"); return
        if not restart_app():
            show_toast("방송 모드 — 앱을 껐다 켜면 적용됩니다")
    bc_tg = Toggle(brow, "방송 모드 (고대비)", lambda: bool(data.get("broadcast")), set_broadcast)
    bc_tg.pack(side="left")
    tk.Label(vc, text="방송 모드: 흐린 회색 글씨를 밝히고 빨강을 연하게 — 영상으로 넘어가면 어두운 색부터 뭉갭니다.\n"
                      "OBS 는 '창 캡처'로 이 창만 담으면 게임 화면과 따로 크기를 맞출 수 있습니다.",
             font=FS, bg=C["card"], fg=C["dim"], wraplength=px(268), justify="left").pack(anchor="w", pady=(7, 0))
    def install_playlists():
        sd = data.get("stats_dir")
        if not sd:
            pl_lbl.configure(text="stats 폴더를 먼저 지정하세요", fg=C["val"]); return
        n, d_, wrote = ensure_playlists(sd, today_key[0], data["pb"])
        if n:
            msg = f"플레이리스트 {n}개 설치 ✓ → 코박스 샌드박스 브라우저 네 번째 탭 '로컬 재생 목록'에 AIMDESK Day · Friday · Probe · Bench"
            if PL_STATE["tpl"]: msg += f" (파일 형식은 코박스가 만든 '{PL_STATE['tpl']}' 을 따름)"
            col = C["ok"]
            if wrote and kovaaks_running():
                msg += "\n⚠ 코박스가 켜진 채로 설치됨 — 목록에 안 보이면 코박스를 껐다 켜세요"; col = C["gold"]
            pl_lbl.configure(text=msg, fg=col)
        else: pl_lbl.configure(text="설치 실패 — Playlists 폴더를 못 찾았습니다 (stats 폴더가 …\\FPSAimTrainer\\FPSAimTrainer\\stats 인지 확인)", fg=C["val"])
    def sync_stats_lbl():
        ok = data.get("stats_dir") and Path(data["stats_dir"]).is_dir()
        p = mask_user_path(data["stats_dir"]) if ok else ""
        if len(p) > 44: p = "…" + p[-43:]          # 공백 없는 긴 경로가 카드 밖으로 넘치지 않게 꼬리만
        stats_lbl.configure(text=(p if ok else "자동 탐지 실패 — 폴더를 선택해 주세요"),
                            fg=C["hint"] if ok else C["val"])

    # ══ 성장 탭 ══
    fg_ = tk.Frame(body, bg=C["bg"]); frames["grow"] = fg_
    grow_scroll = VScroll(fg_); grow_scroll.pack(fill="both", expand=True); gbody = grow_scroll.body
    sess_card = card(gbody, pad=(0, 0)); sess_card.pack(fill="x", pady=(0, 12))
    cv_sess = tk.Canvas(sess_card, height=px(214), bg=C["card"], highlightthickness=0); cv_sess.pack(fill="x")
    idx_card = card(gbody, pad=(0, 0)); idx_card.pack(fill="x", pady=(0, 12))
    cv_idx = tk.Canvas(idx_card, height=px(236), bg=C["card"], highlightthickness=0); cv_idx.pack(fill="x")
    ben_card = card(gbody, pad=(0, 0)); ben_card.pack(fill="x", pady=(0, 12))
    cv_ben = tk.Canvas(ben_card, height=px(196), bg=C["card"], highlightthickness=0); cv_ben.pack(fill="x")
    spark = tk.Frame(gbody, bg=C["bg"]); spark.pack(fill="both", expand=True)
    spark_cvs = {}
    for i, k in enumerate(PROBE):
        cell = card(spark, pad=(10, 8))
        cell.grid(row=i//3, column=i % 3, sticky="nsew", padx=(0, 12), pady=(0, 12))
        spark.grid_columnconfigure(i % 3, weight=1)
        top = tk.Frame(cell, bg=C["card"]); top.pack(fill="x")
        nl_ = tk.Label(top, text=sname(k), font=FB, cursor="hand2",
                       bg=C["card"], fg=C["val"] if SCEN[k][1] == "v" else C["ow"]); nl_.pack(side="left")
        nl_.bind("<Button-1>", lambda e, k=k: open_detail(k))
        pbl = tk.Label(top, text="", font=FNS, bg=C["card"], fg=C["sub"]); pbl.pack(side="right")
        cv = tk.Canvas(cell, height=px(48), bg=C["card"], highlightthickness=0); cv.pack(fill="x")
        spark_cvs[k] = (cv, pbl)

    # ══ 벤치 탭 ══
    fb_ = tk.Frame(body, bg=C["bg"]); frames["bench"] = fb_
    bench_scroll = VScroll(fb_); bench_scroll.pack(fill="both", expand=True); bbody = bench_scroll.body
    ben_head = card(bbody); ben_head.pack(fill="x", pady=(0, 12))
    ben_total = tk.Label(ben_head, text="—", font=FBIG, bg=C["card"], fg=C["gold"])
    ben_total.pack(side="left")
    ben_rankcv = tk.Canvas(ben_head, width=px(76), height=px(26), bg=C["card"], highlightthickness=0)
    ben_rankcv.pack(side="left", padx=14)
    tk.Label(ben_head, text="총 에너지 · Novice S5 · 볼테익 동일 수식", font=FS,
             bg=C["card"], fg=C["hint"]).pack(side="left")
    ben_src = tk.Label(ben_head, text="", font=FNS, bg=C["card"], fg=C["dim"])
    ben_src.pack(side="right")
    RBtn(ben_head, "내 볼테익 프로필", lambda: open_uri("https://app.voltaic.gg/j0y0nho"),
         padx=12, pady=5).pack(side="right", padx=(0, 12))
    RBtn(ben_head, "볼테익 벤치 페이지", lambda: open_uri("https://app.voltaic.gg/benchmarks"),
         padx=12, pady=5).pack(side="right", padx=(0, 8))

    advice_lbl = tk.Label(bbody, text="", font=FS, bg=C["bg"], fg=C["hint"], wraplength=px(900), justify="left", anchor="w")
    advice_lbl.pack(fill="x", pady=(0, 10))
    ben_body = tk.Frame(bbody, bg=C["bg"]); ben_body.pack(fill="both", expand=True)
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
        tk.Frame(hd, bg=CATC[sub_[1]], width=px(8), height=px(8)).pack(side="left", pady=3)
        tk.Label(hd, text=f" {sub_[1]} · {sub_[2]}", font=FB, bg=C["card"], fg=C["txt"]).pack(side="left")
        se_lbl = tk.Label(hd, text="—", font=FN, bg=C["card"], fg=C["dim"]); se_lbl.pack(side="right")
        cells = []
        for k, th in sub_[3]:
            r1 = tk.Frame(sc, bg=C["card"]); r1.pack(fill="x", pady=(7, 1))
            bl_ = tk.Label(r1, text=sname(k), font=FS, bg=C["card"], fg=C["sub"], cursor="hand2"); bl_.pack(side="left")
            bl_.bind("<Button-1>", lambda e, k=k: open_detail(k))
            sc_lbl = tk.Label(r1, text="—", font=FN, bg=C["card"], fg=C["txt"]); sc_lbl.pack(side="right")
            gap_lbl = tk.Label(r1, text="", font=FNS, bg=C["card"], fg=C["dim"]); gap_lbl.pack(side="right", padx=(0, 8))
            cvth = tk.Canvas(sc, height=px(22), bg=C["card"], highlightthickness=0)
            cvth.pack(fill="x")
            cells.append((k, th, sc_lbl, gap_lbl, cvth))
        ben_rows[sub_[0]] = (se_lbl, cells, sc)

    # ══ 기록 탭 ══
    fl_ = tk.Frame(body, bg=C["bg"]); frames["log"] = fl_
    log_scroll = VScroll(fl_); log_scroll.pack(fill="both", expand=True); lbody = log_scroll.body
    log_left = tk.Frame(lbody, bg=C["bg"]); log_left.pack(side="left", fill="both", expand=True)
    log_right = tk.Frame(lbody, bg=C["bg"], width=px(300)); log_right.pack(side="left", fill="y", padx=(14, 0)); log_right.pack_propagate(False)
    hist_card = card(log_left, pad=(12, 10)); hist_card.pack(fill="x", pady=(0, 12))
    hh = tk.Frame(hist_card, bg=C["card"]); hh.pack(fill="x")
    tk.Label(hh, text="최근 14일", font=FH, bg=C["card"], fg=C["txt"]).pack(side="left")
    tk.Label(hh, text="줄을 누르면 그날 시나리오별 기록 · ✓ M=미야기 R=랭크", font=FS, bg=C["card"], fg=C["hint"]).pack(side="right")
    hist_empty = tk.Label(hist_card, text="첫 훈련일이 지나면 여기에 하루씩 쌓입니다", font=F, bg=C["card"], fg=C["hint"])
    hist_grid = tk.Frame(hist_card, bg=C["card"]); hist_grid.pack(fill="x", pady=(8, 0))
    for ci, (cn, cw) in enumerate(zip(HIST_COLS, HIST_W)):
        tk.Label(hist_grid, text=cn, font=FCAP, width=cw, anchor="w", bg=C["card"], fg=C["dim"]).grid(row=0, column=ci, sticky="w", padx=(0, 6))
    hist_cells = []; hist_rows_f = []; hist_sel = [None]; hist_dates = []
    for ri in range(14):
        cells_r = []
        for ci, cw in enumerate(HIST_W):
            lb = tk.Label(hist_grid, text="", font=FNS, width=cw, anchor="w", bg=C["card"], fg=C["sub"], cursor="hand2")
            lb.grid(row=ri + 1, column=ci, sticky="w", padx=(0, 6), pady=1)
            lb.bind("<Button-1>", lambda e, i=ri: select_day(i))
            cells_r.append(lb)
        hist_cells.append(cells_r)
    grow_card = card(log_left, pad=(12, 10)); grow_card.pack(fill="x")
    grow_title = tk.Label(grow_card, text="", font=FB, bg=C["card"], fg=C["txt"]); grow_title.pack(anchor="w")
    grow_grid = tk.Frame(grow_card, bg=C["card"]); grow_grid.pack(fill="x", pady=(6, 0))
    grow_cells = []
    for ri in range(len(SCEN)):
        r_ = []
        for ci, cw in enumerate((14, 12, 8, 14)):
            lb = tk.Label(grow_grid, text="", font=FNS, width=cw, anchor="w", bg=C["card"], fg=C["sub"])
            lb.grid(row=ri, column=ci, sticky="w", padx=(0, 8)); r_.append(lb)
        grow_cells.append(r_)
    det_card = card(log_right, pad=(12, 10)); det_card.pack(fill="x")
    det_title = tk.Label(det_card, text="날짜를 고르세요", font=FB, bg=C["card"], fg=C["txt"]); det_title.pack(anchor="w", pady=(0, 6))
    det_lines = []
    for _i in range(len(SCEN)):
        lb = tk.Label(det_card, text="", font=FNS, bg=C["card"], fg=C["sub"], anchor="w"); lb.pack(anchor="w"); det_lines.append(lb)

    def select_day(i):
        if i < len(hist_dates): hist_sel[0] = hist_dates[i]; fill_detail()
    def fill_detail():
        dk = hist_sel[0]
        for ri, rf_ in enumerate(hist_cells):
            on = ri < len(hist_dates) and hist_dates[ri] == dk
            for lb in rf_: cfg(lb, bg=C["card2"] if on else C["card"])
        if not dk:
            cfg(det_title, text="날짜를 고르세요")
            for lb in det_lines: cfg(lb, text="")
            return
        e = data["days"].get(dk, {})
        cfg(det_title, text=f"{dk[5:7]}-{dk[8:10]} {DOWK[date.fromisoformat(dk).weekday()]} · {sum(e.get('count', {}).values())}판")
        for lb, (k, first, best, cnt, is_pb) in zip(det_lines, day_detail(data, dk)):
            if best is None: cfg(lb, text=f"{sname(k)}  —", fg=C["dim"]); continue
            t = f"{sname(k)}  {best}" + (f" · 첫 {first}" if first is not None else "") + (f" · {cnt}판" if cnt else "") + (" · PB" if is_pb else "")
            cfg(lb, text=t, fg=C["gold"] if is_pb else C["sub"])

    def refresh_log():
        dkey = today_key[0]
        tdays = memo(("tdays",), lambda: training_days(data))
        if not tdays:
            hist_grid.pack_forget(); hist_empty.pack(anchor="w", pady=8)
        else:
            hist_empty.pack_forget()
            if not hist_grid.winfo_ismapped(): hist_grid.pack(fill="x", pady=(8, 0))
        rows = memo(("hist", dkey), lambda: history_rows(data, dkey, probe_series(data), memo(("pbd",), lambda: pb_days(data))))
        hist_dates[:] = [r["date"] for r in rows]
        for ri, r in enumerate(rows):
            vals = fmt_history_row(r)
            base = C["txt"] if r["date"] == dkey else (C["sub"] if (r["trained"] or r["dtype"] == "seed") else C["dim"])
            if r["dtype"] == "r" and not r["trained"]: base = C["dim"]
            for ci, (lb, v) in enumerate(zip(hist_cells[ri], vals)):
                col = base
                if ci == 1: col = DAY_TYPE.get(r["dtype"], ("", C["dim"]))[1] if r["dtype"] != "seed" else C["gold"]
                elif ci == 6 and r["pbs"]: col = C["gold"]
                elif ci == 5 and r["vi"] is not None: col = C["ok"] if r["vi"] >= 0 else C["val"]
                cfg(lb, text=v, fg=col)
        if hist_sel[0] not in hist_dates:
            hist_sel[0] = next((r["date"] for r in rows if r["trained"]), None)
        fill_detail()
        e0, e1 = energy_delta(data)
        cfg(grow_title, text=f"시작 대비 · 총 에너지 {e0} → {e1} ({e1 - e0:+d})", fg=C["gold"] if e1 > e0 else C["dim"])
        for r_, g in zip(grow_cells, memo(("growth",), lambda: growth_since_seed(data))):
            vals = fmt_growth_row(g)
            col = C["dim"] if g["stalled"] else C["sub"]
            cfg(r_[0], text=vals[0], fg=C["val"] if SCEN[g["key"]][1] == "v" else C["ow"])
            cfg(r_[1], text=vals[1], fg=col); cfg(r_[2], text=vals[2], fg=C["ok"] if not g["stalled"] else C["dim"])
            cfg(r_[3], text=vals[3], fg=C["gold"] if vals[3] else col)
    tab_fn["log"] = refresh_log

    def draw_thcells(cv, th, score):
        cv.delete("all")
        W = max(cv.winfo_width(), px(200)); h = px(22); skew = px(7); gap = px(5)
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

    def rank_pill(cv, name, color, w=None):
        cv.delete("all"); w = w or px(76)
        if not name or name == "—": return
        rrect(cv, 0, px(2), w, px(24), px(10), fill=color, outline="")
        cv.create_text(w/2, px(13), text=name, font=(FAM, 9, "bold"), fill="#0B0E11")

    # ── 차트 ──
    def draw_idx(cv, series):
        cv.delete("all"); W = max(cv.winfo_width(), px(400))
        _has = [p for p in series if p["vi"] is not None or p["oi"] is not None]
        H = px(236) if _has else px(74)                     # 그릴 게 없으면 자리를 덜 차지한다
        if int(cv.cget("height")) != H: cv.configure(height=H)
        if not _has:
            cv.create_text(px(16), px(20), text="프로브 지수", anchor="w", fill=C["txt"], font=FB)
            cv.create_text(px(16), px(46), anchor="w", fill=C["hint"], font=FS,
                           text="그날 첫 판만 모아 컨디션을 뺀 실력 곡선을 그립니다 — 프로브 4일치가 쌓이면 여기에 나타납니다")
            return
        H = px(236)
        cv.create_text(px(16), px(16), text="프로브 지수", anchor="w", fill=C["txt"], font=FB)
        cv.create_text(W-px(16), px(16), text="점 = 일별 · 선 = 7일 평균", anchor="e", fill=C["hint"], font=FS)
        cv.create_rectangle(px(96), px(11), px(108), px(14), fill=C["val"], outline="")
        cv.create_text(px(112), px(13), text="발로", anchor="w", fill=C["sub"], font=FS)
        cv.create_rectangle(px(146), px(11), px(158), px(14), fill=C["ow"], outline="")
        cv.create_text(px(162), px(13), text="옵치", anchor="w", fill=C["sub"], font=FS)
        pts = [p for p in series if p["vi"] is not None or p["oi"] is not None][-30:]
        L, R, T, B = px(46), px(18), px(38), px(24)
        def X(i): return L + (W-L-R) * (0.5 if len(pts) < 2 else i/(len(pts)-1))
        def Y(v): return T + (H-T-B) * (1 - (v+3)/6)
        for v in (-2, 0, 2):
            cv.create_line(L, Y(v), W-R, Y(v), fill="#222A32" if v else "#39434E")
            cv.create_text(L-px(9), Y(v), text=f"{v:+d}" if v else "0", anchor="e",
                           fill=C["dim"], font=FNS)
        if not pts:
            cv.create_text((L+W-R)/2, (T+H-B)/2,
                           text="프로브를 시작하면 여기서 성장 곡선이 자랍니다  ·  지수는 4일차부터",
                           fill=C["hint"], font=F)
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
        cv.create_text(L, H-px(10), text=pts[0]["date"][5:], anchor="w", fill=C["dim"], font=FNS)
        cv.create_text(W-R, H-px(10), text=pts[-1]["date"][5:], anchor="e", fill=C["dim"], font=FNS)

    def draw_bench_chart(cv, bd):
        cv.delete("all"); W = max(cv.winfo_width(), px(400)); H = px(196)
        cv.create_text(px(16), px(16), text="벤치마크 총 에너지", anchor="w", fill=C["txt"], font=FB)
        cv.create_text(W-px(16), px(16), text="랭크 선을 넘는 순간이 보입니다", anchor="e", fill=C["hint"], font=FS)
        L, R, T, B = px(70), px(18), px(38), px(22)
        top = max([520] + [e_ + 60 for _, e_ in bd])   # 골드 위로 외삽돼도 점이 차트 밖으로 나가지 않게
        def Y(v): return T + (H-T-B) * (1 - v/top)
        for (t, n, c) in RANKS:
            cv.create_line(L, Y(t), W-R, Y(t), fill="#2A333D", dash=(3, 4))
            cv.create_text(L-px(10), Y(t), text=n, anchor="e", fill=c, font=FNS)
        if not bd:
            cv.create_text((L+W-R)/2, (T+H-B)/2, text="토요일 풀런이 쌓이면 계단이 생깁니다",
                           fill=C["hint"], font=F)
            return
        def X(i): return L + (W-L-R) * (0.5 if len(bd) < 2 else i/(len(bd)-1))
        seq = [(X(i), Y(e)) for i, (k, e) in enumerate(bd)]
        if len(seq) > 1:
            cv.create_line(*[c for xy in seq for c in xy], fill=C["gold"], width=3)
        for i, (k, e) in enumerate(bd):
            x, y = X(i), Y(e)
            cv.create_oval(x-px(4), y-px(4), x+px(4), y+px(4), fill=C["gold"], outline="")
            cv.create_text(x, y-px(14), text=str(e), fill=C["txt"], font=FNS)
            cv.create_text(x, H-px(10), text=k[5:], fill=C["dim"], font=FNS)

    def draw_session(cv, pts, gain):
        """오늘 친 판을 점으로. 세로는 '그 시나리오 평소 대비 %' — 시나리오마다 점수 단위가 달라 그대로 겹쳐 그릴 수 없다.
        점을 선으로 잇지 않는 이유: 옆 점은 다른 시나리오라 이으면 없는 추세가 보인다."""
        cv.delete("all")
        W = max(cv.winfo_width(), px(420)); H = px(214)
        L, R, T, B = px(52), px(16), px(34), px(38)
        cv.create_text(px(14), px(17), text="오늘 세션", anchor="w", fill=C["txt"], font=FB)
        cv.create_text(W - px(14), px(17), text="점 하나 = 한 판 · 세로 = 그 시나리오 평소 대비",
                       anchor="e", fill=C["hint"], font=FNS)
        vals = [p[3] for p in pts if p[3] is not None]
        if not vals:
            cv.create_text(W / 2, H / 2, text=session_caption(pts, gain), fill=C["hint"], font=FS); return
        rng = max(6.0, float(math.ceil(max(abs(min(vals)), abs(max(vals))))))
        Y = lambda v: T + (H - T - B) * (1 - (v + rng) / (2 * rng))
        for v, txt in ((rng, f"+{rng:.0f}%"), (0.0, "평소"), (-rng, f"-{rng:.0f}%")):
            y = Y(v)
            cv.create_line(L, y, W - R, y, fill=C["dim"] if v == 0 else C["line"], dash=() if v == 0 else (2, 3))
            cv.create_text(L - px(7), y, text=txt, anchor="e", fill=C["sub"] if v == 0 else C["dim"], font=FNS)
        n = len(pts)
        X = lambda i: L + (W - L - R) * (i / (n - 1) if n > 1 else 0.5)
        prev_k = None; last_lbl = -1e9
        for i, k, _sc, pct, kind in pts:
            if k != prev_k:                                   # 시나리오가 바뀌는 자리에 옅은 칸막이와 이름
                if prev_k is not None:
                    cv.create_line(X(i) - px(3), T, X(i) - px(3), H - B, fill=C["line"])
                if X(i) - last_lbl >= px(44):                 # 자리가 있을 때만 — 짧은 블록이 이어지면 이름이 겹친다
                    cv.create_text(X(i), H - B + px(11), text=sname(k)[:8], anchor="w", fill=C["dim"], font=(FAM, 7))
                    last_lbl = X(i)
                prev_k = k
            if pct is None: continue
            x, y = X(i), Y(max(-rng, min(rng, pct)))
            r = px(4) if kind == "pb" else px(3)
            cv.create_oval(x - r, y - r, x + r, y + r, fill=C[VERDICT_FILL.get(kind, "sub")], outline="")
        cv.create_text(px(14), H - px(12), text=session_caption(pts, gain), anchor="w", fill=C["sub"], font=FS)

    def draw_spark(k, cv, pbl):
        cv.delete("all"); W = max(cv.winfo_width(), px(200)); H = px(48)
        days = sorted(d_ for d_ in data["days"] if data["days"][d_]["first"].get(k) is not None)[-14:]
        vals = [data["days"][d_]["first"][k] for d_ in days]
        pb = data["pb"].get(k); delta = ""
        if len(vals) >= 2:
            base = sum(vals[:-1]) / len(vals[:-1]); df = vals[-1] - base
            delta = f"  {'▲' if df >= 0 else '▼'}{abs(df):.0f}"
        tag = spark_tag(vals)
        pbl.configure(text=(f"PB {pb}{delta}" if pb else "") + (f" · {tag}" if tag else ""))
        if len(vals) < 2:
            th = th_of(k); cur = pb
            if not th or cur is None:
                cv.create_text(W / 2, H / 2, text="첫 판을 치면 여기가 채워집니다", fill=C["hint"], font=FS); return
            # 첫날엔 이을 점이 없으니 '지금 어느 등급 칸에 있는지'를 보여준다 — 이건 한 판만 있어도 뜻이 있다
            bw = W - px(24); h = px(13); x0 = px(12); y0 = px(8)
            for i, t in enumerate(th):
                x1 = x0 + bw * i / 4; x2 = x0 + bw * (i + 1) / 4
                cv.create_rectangle(x1, y0, x2 - px(2), y0 + h, fill=RANKC[i] if cur >= t else C["card2"], outline="")
            rank, t_, gap = next_rank_gap(cur, th)
            cv.create_text(W / 2, y0 + h + px(13), font=FS, fill=C["sub"],
                           text=(f"{rank}까지 {gap}점" if rank else "Gold 칸 ✓"))
            return
        lo, hi = min(vals), max(vals)
        if hi == lo: hi += 1
        col = C["val"] if SCEN[k][1] == "v" else C["ow"]
        m6, m12, m7, m16 = px(6), px(12), px(7), px(16)
        seq = [(m6 + (W-m12)*i/(len(vals)-1), H-m7 - (H-m16)*(v-lo)/(hi-lo)) for i, v in enumerate(vals)]
        cv.create_line(*[c for xy in seq for c in xy], fill=col, width=2, smooth=True)
        x, y = seq[-1]
        cv.create_oval(x-3, y-3, x+3, y+3, fill=col, outline="")

    # ── 갱신 ──
    def bench_source():
        dkey = today_key[0]
        if data["days"].get(dkey, {}).get("best"): return dkey
        cands = [k for k in sorted(data["days"]) if data["days"][k]["best"]]
        return cands[-1] if cands else None

    def set_next_marker(nk):
        """다음에 칠 줄 하나만 강조. 같은 시나리오가 프로브와 본훈련에 같이 있을 수 있어(테마에 따라)
        '키'가 아니라 '줄 번호'로 고른다 — 아직 안 끝난 줄이 우선."""
        day = data["days"].get(today_key[0], blank_day())
        cands = [i for i, r in enumerate(routine_rows) if r[1] == nk] if nk is not None else []
        idx = None
        for i in cands:
            kind, key, target = routine_rows[i][0], routine_rows[i][1], routine_rows[i][2]
            done = (day["first"].get(key) is not None) if kind == "probe" else day["count"].get(key, 0) >= target
            if not done: idx = i; break
        if idx is None and cands: idx = cands[0]
        if idx == routine_next[0]: return
        for i in (routine_next[0], idx):
            if i is None or i >= len(routine_rows): continue
            kind, key, target, bar, cl, sl, gc, mark, nml, rowf = routine_rows[i]
            on = i == idx
            for w_ in (rowf, mark, nml, bar, cl, sl): w_.configure(bg=C["card2"] if on else C["card"])
            mark.configure(text="▶" if on else "")
        routine_next[0] = idx

    def refresh_today():
        dkey = today_key[0]; day = data["days"].get(dkey, blank_day())
        seq_next = None
        if seq_alive():
            _, nx_, _ = seq_status()
            if nx_ is not None: seq_next = seq_win["seq"][nx_]
        unmapped = False
        pb_prev = pb_before_day(data, dkey)
        for kind, key, target, bar, cl, sl, gc, mark, nml, rowf in routine_rows:
            c = day["count"].get(key, 0)
            done = (day["first"].get(key) is not None) if kind == "probe" else c >= target
            bar.delete("all")
            if bar.winfo_width() <= 1: unmapped = True
            bw = max(bar.winfo_width(), 60); h = px(8)
            segs = segment_geometry(bw, target)
            filled = min(len(segs), int(c * len(segs) / target)) if target > len(segs) else min(c, len(segs))
            for i, (x1, x2) in enumerate(segs):
                fill = (C["ok"] if done else gc) if i < filled else C["card2"]
                if x2 - x1 >= 8: rrect(bar, x1, 1, x2, h - 1, min(3, (x2 - x1) // 2), fill=fill, outline="", tags="seg")
                else: bar.create_rectangle(x1, 1, x2, h - 1, fill=fill, outline="", tags="seg")
            cfg(cl, text=f"{min(c,99)}/{target}" + (" ✓" if done else ""), fg=C["ok"] if done else C["sub"])
            # 점수 + 최근 7일 평균 대비 (프로브는 그날 첫 판, 나머지는 오늘 베스트 기준)
            val, field = (day["first"].get(key), "first") if kind == "probe" else (day["best"].get(key), "best")
            if val is None:
                sl.configure(text="", fg=C["dim"])
            else:
                kind_, label_, colk_ = play_verdict(val, scen_day_band(data, key, dkey, field), pb_prev.get(key))
                txt, col = f"{val} {label_}".strip(), C[colk_]
                if kind == "bench" and th_of(key):                                       # 벤치 데이: ▲▼ 대신 다음 등급까지 (순서창이 ▲▼를 보여 준다)
                    g_, gcol = fmt_gap(val, th_of(key)); is_pb = kind_ == "pb"
                    txt, col = f"{val}{' 최고' if is_pb else ''} · {g_}", (C["gold"] if is_pb else gcol)
                cfg(sl, text=txt, fg=col)
        if unmapped and not day_state.get("redraw_pending"):
            day_state["redraw_pending"] = True
            root.after(250, lambda: (day_state.__setitem__("redraw_pending", False), dirty.__setitem__("today", True), refresh_tab("today")))
        # 섹션별 진행 (③ 본훈련 · 12/17 처럼)
        for i, (lb, title, start, extra) in enumerate(section_labels):
            end = section_labels[i + 1][2] if i + 1 < len(section_labels) else len(routine_rows)
            rows = [(r[0], r[1], r[2]) for r in routine_rows[start:end]] + (extra or [])
            if rows:
                d_, t_ = section_progress(rows, day)
                cfg(lb, text=f"{title} · {d_}/{t_}", fg=C["ok"] if d_ >= t_ else C["gold"])
        # 다음에 칠 판 표시 (순서창이 열려 있으면 그 포인터, 아니면 첫 미완료 줄)
        set_next_marker(next_routine_key([(r[0], r[1], r[2]) for r in routine_rows], day, seq_next))
        # 오늘의 도전
        if day_state.get("chal_lbl") is not None and day_state["chal_lbl"].winfo_exists():
            ch = day_state["chal"]; tb = day.get("best", {}).get(ch["key"])
            done_ = tb is not None and tb >= ch["target"]
            cfg(day_state["chal_lbl"], text=fmt_challenge(ch, tb), fg=C["ok"] if done_ else C["gold"])
        # 오늘의 띠
        if day_state.get("rib_cv") is not None and day_state["rib_cv"].winfo_exists():
            kinds = [k_ for _, _, k_ in day_verdicts(data, dkey, cur_plays())]
            plan = today_plan_n(); cells = ribbon_cells(plan, kinds)
            prev = day_state.get("rib_cells") or []
            day_state["rib_cells"] = cells
            if len(kinds) and len(cells) == len(prev) and prev[len(kinds) - 1] == "todo":
                ribbon_pop(day_state["rib_cv"], cells, len(kinds) - 1)      # 방금 한 칸 찼다
            else:
                draw_ribbon(day_state["rib_cv"], cells)
            cfg(day_state["rib_lbl"], text=fmt_ribbon(plan, kinds),
                fg=C["gold"] if ribbon_counts(kinds)["pb"] else C["sub"])
        # 오늘 세션 요약 줄
        if day_state["sess_lbl"] is not None:
            cp = cur_plays(); keys_ = {p_[0] for p_ in cp}
            rc = {k_: recent_stats(data, k_, dkey) for k_ in keys_}
            ss = session_summary(cp, rc)
            cfg(day_state["sess_lbl"], text=fmt_session(ss), fg=C["gold"] if ss["n_pb"] else C["sub"])
        sync_deaths_lbl()
        # 코치 카드
        if day_state["coach"]:
            dt_ = day_state["dt"]
            cp = cur_plays()
            COACH_STATE["validity"] = probe_validity(cp)
            def _brief():
                alt = None
                if dt_ == "r": alt = weekly_recap(data, dkey)
                elif dt_ in ("w", "b"): alt = bench_lines(bench_readiness(data, dkey), dt_)
                extra = None
                if routine_complete(day, dt_):
                    avg_ = {k_: recent_stats(data, k_, dkey, "first")[0] for k_ in PROBE}
                    extra = "마무리 · " + next_step(data, dkey, cp, avg_)
                elif dt_ == "b" and alt: alt = alt + [("18개 다 치면 벤치 탭·성장 차트에 오늘 점이 찍힙니다", "hint")]
                return session_brief(data, dkey, dt_, cp, extra=extra, alt=alt)
            lines = memo(("brief", dkey, dt_, COACH_STATE.get("validity"), len(cp)), _brief)
            COACH_STATE["brief"] = lines
            for i, lb_ in enumerate(day_state["coach"]):
                if i < len(lines): cfg(lb_, text=lines[i][0], fg=C[lines[i][1]])
                else: cfg(lb_, text="")
        tg1.sync(); tg2.sync()
        for st_ in steppers: st_.sync()
        seg.draw()

    def refresh_header():
        dkey = today_key[0]
        s = probe_series(data)
        last = s[-1] if s and s[-1]["date"] == dkey else None
        vi = last["vi"] if last else None; oi = last["oi"] if last else None
        HDR_STATE.update(vi=vi, oi=oi)
        if vi is not None or oi is not None:
            parts = []
            if vi is not None: parts.append(f"발로 {vi:+.1f}")
            if oi is not None: parts.append(f"옵치 {oi:+.1f}")
            hdr_idx.configure(text=" · ".join(parts), fg=C["txt"])
        else:
            nprobe = memo(("nprobe",), lambda: len([1 for k_ in data["days"] if any(data["days"][k_]["first"].get(p) is not None for p in PROBE)]))
            hdr_idx.configure(text=f"지수 준비 {min(nprobe,4)}/4일", fg=C["dim"])
        xp = memo(("xp",), lambda: total_xp(data))
        cfg(hdr_lv, text=fmt_level(xp), fg=C["gold"] if level_frac(xp) >= 0.85 else C["sub"])
        lv_cv.delete("all"); _r = px(9); _c = px(11)
        lv_cv.create_oval(_c - _r, _c - _r, _c + _r, _c + _r, outline=C["line"], width=px(3))
        _f = level_frac(xp)
        if _f > 0:
            lv_cv.create_arc(_c - _r, _c - _r, _c + _r, _c + _r, start=90, extent=-359.9 * _f,
                             style="arc", outline=C["gold"] if _f >= 0.85 else C["ok"], width=px(3))
        mi = memo(("miyagi",), lambda: sum(1 for e in data["days"].values() if e["checks"].get("miyagi")))
        hdr_mi.configure(text=f"미야기 D+{min(mi, 30)}/30" + (" ✓" if mi >= 30 else ""))
        tdays = memo(("tdays",), lambda: training_days(data)); today_d = date.fromisoformat(dkey)
        cur, best = streak(tdays, today_d)
        cfg(hdr_streak, text=f"연속 {cur}일" + (f" · 최고 {best}" if best > cur else ""), fg=C["gold"] if cur >= 3 else C["sub"])
        draw_week(week_strip(tdays, today_d))
        # 헤더 에너지는 PB 기준(항상 9/9) — 오늘 친 몇 판의 부분 조화평균으로 흔들리지 않게
        e_pb, _ = totalE(data["pb"]); rn_pb, rc_pb = rank_of(e_pb)
        hdr_e.configure(text=f"PB {e_pb} {rn_pb}" if e_pb is not None else "", fg=rc_pb)

    def refresh_bench():
        # 벤치 탭은 오늘(없으면 마지막 기록일)의 베스트 — 토요일 풀런이 실시간으로 차오르는 용도, n/9 표기
        src = bench_source()
        scores = data["days"].get(src, {}).get("best", {}) if src else {}
        e, n = totalE(scores); rn, rc = rank_of(e)
        ben_total.configure(text=str(e) if e is not None else "—", fg=rc)
        rank_pill(ben_rankcv, rn if e is not None else "", rc)
        ben_src.configure(text=bench_src_label(src, n))
        wl = memo(("weakest",), lambda: weakest_link(data["pb"]))
        cfg(advice_lbl, text=fmt_weakest(wl))
        for sub_ in SUBS:
            se_lbl, cells, card_f = ben_rows[sub_[0]]
            se = subE(sub_, scores)
            cfg(se_lbl, text=str(se) if se is not None else "—", fg=rank_of(se)[1])
            cfg(card_f, highlightbackground=C["gold"] if (wl and wl["sub"] == sub_[0]) else C["line"])
            for k, th, sc_lbl, gap_lbl, cvth in cells:
                x = scores.get(k)
                cfg(sc_lbl, text=str(x) if x is not None else "—",
                    fg=rank_of(scenE(x, th))[1] if x is not None else C["dim"])
                gt, gcol = fmt_gap(x, th); cfg(gap_lbl, text=gt, fg=gcol)
                draw_thcells(cvth, th, x)

    def refresh_grow():
        _cp = cur_plays()
        draw_session(cv_sess, session_points(data, today_key[0], _cp), within_day_gain(_cp))
        draw_idx(cv_idx, probe_series(data))
        draw_bench_chart(cv_ben, memo(("bench_days",), lambda: bench_days(data)))
        for k, (cv, pbl) in spark_cvs.items(): draw_spark(k, cv, pbl)

    tab_fn.update(today=refresh_today, grow=refresh_grow, bench=refresh_bench)

    def refresh():
        """기록이 바뀌었을 때: 헤더 + 지금 보이는 탭만 그린다. 숨은 탭은 dirty 로 표시해 두고 열 때 그린다"""
        for t in dirty: dirty[t] = True
        refresh_header()
        refresh_tab(cur_tab[0])
        update_sequence()
        update_detail()
        update_broadcast()

    # 창 크기 변경: 캔버스마다 오는 <Configure> 폭풍을 80ms 로 묶어 한 번만, 보이는 탭만 다시 그린다
    tab_of = {}; last_w = {}; resize_job = [None]
    def _resize_flush():
        resize_job[0] = None; refresh_tab(cur_tab[0])
    def on_resize(e):
        w = e.widget
        if last_w.get(w) == e.width: return
        last_w[w] = e.width
        dirty[tab_of.get(w, cur_tab[0])] = True
        if resize_job[0]: root.after_cancel(resize_job[0])
        resize_job[0] = root.after(80, _resize_flush)
    for cv in [cv_sess, cv_idx, cv_ben] + [c for c, _ in spark_cvs.values()]:
        tab_of[cv] = "grow"; cv.bind("<Configure>", on_resize)
    for _, cells_, _card in ben_rows.values():
        for _k, _th, _l, _g, cvth in cells_:
            tab_of[cvth] = "bench"; cvth.bind("<Configure>", on_resize)
    tab_of[left_scroll.cv] = "today"; left_scroll.cv.bind("<Configure>", on_resize, add="+")

    def on_day_change(nk):
        """자정 통과: 데이터 키·스캔 캐시·날짜 UI·입력칸을 모두 오늘로 (켜 둔 채 밤을 넘겨도 어제 루틴이 남지 않게)"""
        today_key[0] = nk
        _SCORE_CACHE.clear(); _MISS_SEEN.clear(); TODAY_PLAYS.clear()
        auto.update(on=False, fired=None, due=None, fired_at=None, pending=None, warned=False, seen=None, start_played=0)
        HDR_STATE.update(vi=None, oi=None)
        COACH_STATE.update(brief=[], validity=None, fat_sig=None, fat_len=0)
        routine_next[0] = None
        if detail["win"] is not None and detail["win"].winfo_exists(): detail["win"].destroy()
        if card_win["win"] is not None and card_win["win"].winfo_exists(): card_win["win"].destroy()
        if seq_alive(): remember_seq_pos(); seq_win["win"].destroy()
        build_day_ui()
        install_playlists()                     # 오늘 테마로 다시 설치 — 코박스 목록이 어제 구성으로 남지 않게
        sync_sleep_entry()
        refresh()
        root.after(300, lambda: (dirty.__setitem__("today", True), refresh_tab("today")))   # 새 줄들이 자리를 잡은 뒤 진행바를 실제 폭으로

    def scan_once():
        """stats 폴더 한 번 확인 → 기록 반영 → 화면·자동 진행·상태줄 갱신 (tick 이 2초마다, F5 가 즉시 부른다)"""
        d_now = today_date(); nk = d_now.isoformat()   # 한 번만 읽는다 — 자정 경계에서 어제 키에 오늘 스캔이 섞이지 않게
        if nk != today_key[0]: on_day_change(nk)
        sd = data.get("stats_dir"); scan_err = False
        if sd:
            plays = scan_day(Path(sd), d_now, force=auto["on"])
            if plays is None:
                scan_err = True
            else:
                TODAY_PLAYS[:] = sorted(plays, key=lambda x: x[1])
                events, changed = apply_scan(data, plays, nk)
                for line in pb_toast_lines(events, data["pb"]): show_toast(line, "pb")
                if changed or events: save_data(data)                 # 버전을 먼저 확정해야 아래 계산 캐시가 refresh 에서 그대로 쓰인다
                if changed:
                    cp = cur_plays()
                    avg_ = {k_: recent_stats(data, k_, nk, "first" if k_ in PROBE else "best")[0] for k_ in {p_[0] for p_ in cp}}
                    sig = fatigue_signal(cp, avg_); kind = sig and sig["kind"]
                    if kind and kind != COACH_STATE["fat_sig"]:
                        msg_ = fatigue_msg(sig); show_toast(msg_, "warn"); set_hint(msg_, C["gold"])
                        COACH_STATE.update(fat_sig=kind, fat_len=len(cp))
                    elif kind is None: COACH_STATE["fat_sig"] = None
                    pn = today_plan_n()
                    if pn and len(cp) >= pn and data.get("card_day") != nk:
                        data["card_day"] = nk; save_data(data)
                        root.after(800, open_card)              # 오늘 계획을 다 친 순간 한 번만
                if changed or events: refresh()
                auto_step()
                if auto["on"] and seq_alive(): update_sequence()     # 보낸 지 n초 / FREEPLAY 경고 갱신
        set_status(*status_line(SCAN_INFO, bool(sd) and Path(sd).is_dir(), scan_err, SAVE_ERROR[0], auto["on"]))

    def tick():
        try:
            scan_once()
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
    root.after(1200, install_playlists)                 # 시작을 빠르게 — 플레이리스트 설치는 1.2초 뒤
    build_day_ui()

    # 마우스 휠: 포인터 아래의 스크롤 컨테이너로
    def on_wheel(e):
        try: w = root.winfo_containing(e.x_root, e.y_root) or e.widget
        except Exception: w = e.widget
        while w is not None and not isinstance(w, VScroll): w = getattr(w, "master", None)
        if w is None or not w.shown: return
        w.cv.yview_scroll(wheel_units(getattr(e, "delta", 0), getattr(e, "num", 0)), "units")
    root.bind_all("<MouseWheel>", on_wheel); root.bind_all("<Button-4>", on_wheel); root.bind_all("<Button-5>", on_wheel)

    def on_key(e):
        if e.widget.winfo_toplevel() is not root: return
        act = shortcut_action(e.keysym, e.state, isinstance(e.widget, tk.Entry))
        if not act: return
        if act.startswith("tab:"): show(act[4:])
        elif act == "rescan":
            _SCAN_STATE["sig"] = None; _SCORE_CACHE.clear(); _INI_CACHE["sig"] = None; scan_once()
            if seq_alive(): update_sequence()
        elif act == "dismiss": tq.clear(); render_toasts()
        elif act == "folder": pick_stats()
        elif act == "run" and day_state["pl"]: run_playlist(day_state["pl"])
        return "break"
    root.bind("<Key>", on_key)
    legend_lbl.configure(text="1·2·3·4 탭  F5 재스캔  Ctrl+R 실행")

    root.deiconify(); root.update_idletasks(); win_dark()
    if data["win"].get("zoomed") and sys.platform == "win32":
        try: root.state("zoomed")
        except tk.TclError: pass
    refresh_header()
    show(data["win"].get("tab") if data["win"].get("tab") in frames else "today")
    if LOAD_ERROR:
        root.after(500, lambda: messagebox.showwarning("에임 데스크 — 기록 파일", "\n\n".join(LOAD_ERROR)))
    root.after(300, tick)
    root.after(450, refresh)
    def on_close():
        remember_seq_pos(); remember_bcast()
        try: z = (root.state() == "zoomed")
        except tk.TclError: z = False
        data["win"].update(geo=(data["win"].get("geo") if z else root.winfo_geometry()), zoomed=z,
                           tab=cur_tab[0], geo_scale=UI_SCALE[0])
        save_data(data)
        if SAVE_ERROR[0] and not messagebox.askyesno(
                "에임 데스크", f"기록 저장에 실패했습니다:\n{SAVE_ERROR[0]}\n\n그래도 닫을까요? (아니오 = 열어 둠)"):
            return
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", on_close)
    _DBG.update(root=root, pl_lbl=pl_lbl, draw_ribbon=draw_ribbon, today_plan_n=today_plan_n, cv_sess=cv_sess, hdr_lv=hdr_lv, open_card=open_card, card_win=card_win, set_scale=set_scale, scale_btns=scale_btns, set_broadcast=set_broadcast, open_broadcast=open_broadcast, bcast=bcast, data=data, refresh=refresh, refresh_tab=refresh_tab, dirty=dirty, cur_tab=cur_tab, show=show,
                scan_once=scan_once, tick=tick, seq_win=seq_win, auto=auto, routine_rows=routine_rows, day_state=day_state,
                tq=tq, status_lbl=status_lbl, status_dot=status_dot, show_toast=show_toast, render_toasts=render_toasts,
                toast=toast, toast_tick=toast_tick, on_close=on_close, left_scroll=left_scroll, right_scroll=right_scroll,
                grow_scroll=grow_scroll, bench_scroll=bench_scroll, on_wheel=on_wheel, frames=frames, tabbtns=tabbtns,
                open_sequence=open_sequence, update_sequence=update_sequence, run_playlist=run_playlist,
                VScroll=VScroll, cv_idx=cv_idx, cv_ben=cv_ben, hdr_e=hdr_e, hdr_idx=hdr_idx, set_status=set_status,
                hist_cells=hist_cells, det_lines=det_lines, det_title=det_title, grow_title=grow_title, select_day=select_day,
                hdr_streak=hdr_streak, wk_cv=wk_cv, section_labels=section_labels, advice_lbl=advice_lbl, ben_rows=ben_rows,
                dth_lbl=dth_lbl, steppers=steppers, on_key=on_key, pick_stats=pick_stats,
                detail=detail, open_detail=open_detail, spark_cvs=spark_cvs, daych=daych, set_compact=set_compact)
    _DBG.setdefault("counters", {}).setdefault("refresh_tab", 0)
    if os.environ.get("AIMDESK_NO_MAINLOOP"): return
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
        assert sum(n for _, n in dict(playlists_for("2026-09-10"))["AIMDESK Day"]) == 27
        # 코박스 딥링크 형식 (3.0.0 패치노트: 공백은 %20)
        assert scenario_uri("VT Pasu Novice S5") == "steam://run/824270/?action=jump-to-scenario;name=VT%20Pasu%20Novice%20S5"
        t2 = {"days": {"2026-01-01": {"best": {"pasu": 700}, "first": {"pasu": 650}},
                       "2026-01-02": {"best": {"pasu": 800}, "first": {}},
                       "2026-01-03": {"best": {"pasu": 900}, "first": {"pasu": 850}}}}
        assert recent_stats(t2, "pasu", "2026-01-03") == (750.0, 800)
        assert recent_stats(t2, "pasu", "2026-01-03", "first") == (650.0, 800)
        assert recent_stats(t2, "zzz", "2026-01-03") == (None, None)
        # 폴더 mtime 캐시: 같은 폴더를 두 번 스캔하면 두 번째는 캐시(plays 동일), 파일이 추가되면 다시 읽음
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            sd_ = Path(td); dd = date(2026, 1, 5)
            (sd_ / "VT Pasu Novice S5 - Challenge - 2026.01.05-10.00.00 Stats.csv").write_text("Score:,600\n")
            a = scan_day(sd_, dd); b = scan_day(sd_, dd)
            assert a == b == [("pasu", "10.00.00", 600)], (a, b)
            assert _SCAN_STATE["sig"] is not None
            time.sleep(0.02)
            (sd_ / "VT Pasu Novice S5 - Challenge - 2026.01.05-10.01.00 Stats.csv").write_text("Score:,650\n")
            c = scan_day(sd_, dd)
            assert len(c) == 2 or _SCAN_STATE["sig"] is None, c      # 파일 추가 → mtime 변경 → 재스캔
        assert vk_of("F10") == 0x79 and vk_of("PageDown") == 0x22 and vk_of("N") == 0x4E and vk_of("Nine") == 0x39 and vk_of("Gamepad_X") is None
        assert parse_next_key('+ActionMappings=(ActionName="PlaylistNext",bShift=False,bCtrl=False,bAlt=False,bCmd=False,Key=F10)') == ("F10", None)
        ini_ = '[/Script/Engine.InputSettings]\r\n-ActionMappings=(ActionName="PlaylistNext",bShift=False,bCtrl=False,bAlt=False,bCmd=False,Key=Add)\r\n+ActionMappings=(ActionName="PlaylistNext",bShift=False,bCtrl=False,bAlt=False,bCmd=False,Key=F5)\r\n+ActionMappings=(ActionName="Restart",Key=R)\r\n'
        assert parse_next_key(ini_) == ("F5", None), parse_next_key(ini_)                      # '-' 줄(지운 기본값)은 무시
        assert parse_next_key('-ActionMappings=(ActionName="PlaylistNext",Key=Add)') == (None, "removed")
        assert parse_next_key('+ActionMappings=(ActionName="PlaylistNext",Key=None)') == (None, "removed")
        assert parse_next_key('+ActionMappings=(ActionName="Restart",Key=R)') == (None, "none") and parse_next_key("") == (None, "none")
        assert parse_next_key('+ActionMappings=(ActionName="PlaylistNext",Key=ThumbMouseButton)') == ("ThumbMouseButton", None)
        assert parse_next_key('+ActionMappings=(ActionName="PlaylistNext",bShift=False,bCtrl=True,bAlt=False,bCmd=False,Key=F5)') == (None, "chord")
        assert "조합키" in key_line(key_status(None, None, "chord"))[0]
        assert norm_key("\u0663") is None and norm_key("²") == "Two" and norm_key("pagedn") == "PageDown" and norm_key("numpad add") == "Add" and norm_key("F\u200b5") == "F5"
        assert "칸을 비우면" in key_line(key_status("xyz", "F10"))[0] and "칸을 비우면" not in key_line(key_status("xyz", "Gamepad_X"))[0]
        assert key_line(key_status("F5", "Gamepad_X"))[0].endswith("바꾸세요") and key_line(key_status("F5", "Add"))[0].endswith("비우세요")
        assert "프로브" not in fmt_seq_summary(3, 18, 0, [], None, (None, None), None) and "프로브 2/6" in fmt_seq_summary(3, 27, 0, [], (2, 6), (None, None), None)
        # v3 기반: 판별 기록 병합·세션 시각·memo·색 대비·창 위치·토스트·상태줄
        assert merge_plays([["pasu","10.00.00",500]], [("pasu","10.00.00",505),("dot","12.00.00",-5)]) == [["pasu","10.00.00",505],["dot","12.00.00",-5]]
        t3 = {"pb": {}, "days": {}}
        apply_scan(t3, [("pasu","10.00.00",500),("pasu","11.00.00",450),("dot","12.00.00",-5)], "2026-01-01")
        d3 = t3["days"]["2026-01-01"]
        assert d3["plays"] == [["pasu","10.00.00",500],["pasu","11.00.00",450],["dot","12.00.00",-5]] and d3["sess"] == {"start":"10.00.00","end":"12.00.00"}, d3
        assert apply_scan(t3, [], "2026-01-01")[1] is False and d3["sess"]["end"] == "12.00.00"
        apply_scan(t3, [("pasu","13.00.00",520)], "2026-01-01"); assert d3["sess"] == {"start":"10.00.00","end":"13.00.00"}
        assert pb_days({"pb":{"pasu":900},"days":{"2026-01-01":{"best":{"pasu":700}},"2026-01-03":{"best":{"pasu":900}},"2026-01-04":{"best":{"pasu":900}}}}) == {"pasu":"2026-01-03"}
        calls = [0]
        def _f(): calls[0] += 1; return 1
        memo(("x",), _f); memo(("x",), _f); assert calls[0] == 1; bump_ver(); memo(("x",), _f); assert calls[0] == 2
        UI_SCALE[0] = 1.5; assert px(70) == 105 and px(8) == 12; UI_SCALE[0] = 1.0
        assert scale_label(None) == "자동" and scale_label(1.25) == "125%" and scale_label(2.0) == "200%"
        assert pick_scale(None, 0, 1.0) == 1.0 and pick_scale(None, 0, 1.5) == 1.5      # 저장값 없으면 모니터
        assert pick_scale(1.5, 0, 1.0) == 1.5 and pick_scale(1.5, 2.0, 1.0) == 2.0      # 환경변수가 가장 셈
        assert pick_scale(9.9, 0, 1.0) == 3.0 and pick_scale(0.1, 0, 1.0) == 0.8        # 말도 안 되는 값은 자른다
        assert SCALE_STEPS[0] == 1.0 and SCALE_STEPS[-1] == 2.0
        _c0 = dict(C); _r0 = list(RANKC)
        assert apply_broadcast(False) is False and C == _c0
        assert apply_broadcast(True) is True and C["dim"] != _c0["dim"] and RANKC != _r0
        for _k in ("txt", "sub", "hint", "dim", "val", "ow", "ok", "gold"):     # 카드 위에서 전부 4.5:1 이상
            assert contrast_ratio(C[_k], C["card"]) >= 4.5, (_k, contrast_ratio(C[_k], C["card"]))
        assert contrast_ratio(_c0["dim"], _c0["card"]) < 4.5                    # 원래 팔레트는 dim 이 부족했다
        C.update(_c0); RANKC[:] = _r0
        assert contrast_ratio(C["hint"], C["card"]) >= 4.5 and contrast_ratio(C["txt"], C["card"]) >= 7 and contrast_ratio(C["dim"], C["card"]) >= 3.0
        assert shade("#14191F", 16) == "#24292f" and shade("#000000", -10) == "#000000"
        assert t_min("19.43.00") == 1183
        assert blank_day()["plays"] == [] and blank_day()["sess"] == {"start": None, "end": None}
        assert next_rank_gap(413, [290,340,390,445]) == ("Gold", 445, 32) and next_rank_gap(500, [290,340,390,445])[0] is None
        assert sub_of("zzz") is None and sub_of("dot")[0] == "speed" and th_of("dot") == [845,940,1030,1090]
        pc = pb_context("dot", 1002, 990, {"dot": 1002, "eddie": 780}); assert "Speed" in pc and "→268" in pc and "Silver까지 28점" in pc, pc
        assert "✓" in pb_context("dot", 1100, 990, {"dot": 1100})
        assert len(pb_toast_lines([("dot", 1002, 12)], {"dot": 1002})) == 1 and len(pb_toast_lines([("dot",1,1),("pasu",1,1)], {})) == 2
        assert len(pb_toast_lines([(k, 1, 1) for k in SCEN], {})) == 1 and len(pb_toast_lines([(k, 1, 1) for k in SCEN], {})[0]) <= 60
        q = ToastQueue(); [q.push(f"m{i}", "info", 0) for i in range(4)]; assert len(q.items) == 3
        assert q.expire(10.1) and q.items == []; q.push("a","info",0); q.push("b","info",0); q.dismiss(0); assert q.items[0][0] == "b"
        assert status_line({}, False, False, None, False)[1] == "err" and status_line({}, True, True, None, False)[1] == "warn"
        assert status_line({"plays": 0}, True, False, None, False)[1] == "warn" and status_line({}, True, False, "x", False)[0].startswith("● 저장 실패")
        okl = status_line({"plays": 3, "t": "10:00:00", "other": 1}, True, False, None, True); assert okl[1] == "ok" and "루틴 외 1판" in okl[0] and okl[0].endswith("자동 진행 ▶")
        rows_, npb_, rel_ = seq_rows_apply(["pasu","dot","frog"], [True, False, False], 1, [850, None, None],
                                            lambda k: (800.0, 806) if k == "pasu" else (900.0, 1000))
        assert rows_[0][2] == "✓" and rows_[0][6] == "PB!" and rows_[1][2] == "▶" and rows_[1][4] == "900" and rows_[2][2] == "" and npb_ == 1 and len(rel_) == 1, rows_
        assert bench_src_label(SEED_DATE, 9) == "기준값 · 8/29 · 9/9" and bench_src_label("2026-09-02", 5) == "2026-09-02 · 5/9" and bench_src_label(None, 0) == ""
        assert wheel_units(-120, 0) == 1 and wheel_units(240, 0) == -2 and wheel_units(0, 4) == -1 and wheel_units(0, 5) == 1 and wheel_units(30, 0) == -1 and wheel_units(0, 0) == 0
        assert needs_scroll(700, 600) and not needs_scroll(500, 600)
        assert clamp_geometry("1060x760+100+50", 0, 0, 1920, 1080, 960, 660) == "1060x760+100+50"
        assert clamp_geometry("1060x760+5000+50", 0, 0, 1920, 1080, 960, 660) is None
        assert clamp_geometry("1060x760-1900+80", -1920, 0, 3840, 1080, 960, 660) == "1060x760-1900+80"
        assert clamp_geometry("300x200+10+10", 0, 0, 1920, 1080, 960, 660) == "960x660+10+10" and clamp_geometry("garbage", 0, 0, 1920, 1080, 960, 660) is None
        assert clamp_pos("+1900+80", 300, 300, 0, 0, 1920, 1080) is None and clamp_pos("+1500+80", 300, 300, 0, 0, 1920, 1080) == "+1500+80"
        # 스캔 캐시: 강제 재스캔·점수 없는 파일은 캐시 안 함
        with tempfile.TemporaryDirectory() as td:
            sd_ = Path(td); dd = date(2026, 1, 6)
            for i in range(3): (sd_ / f"VT Pasu Novice S5 - Challenge - 2026.01.06-10.0{i}.00 Stats.csv").write_text(f"Score:,{600+i}\n")
            a = scan_day(sd_, dd); h0 = _SCAN_STATE["hits"]; b = scan_day(sd_, dd)
            assert a == b and len(a) == 3 and _SCAN_STATE["hits"] == h0 + 1
            _SCAN_STATE["n"] = SCAN_FORCE_EVERY - 1; c = scan_day(sd_, dd); assert c == a and _SCAN_STATE["hits"] == h0 + 1
            (sd_ / "VT Pasu Novice S5 - Challenge - 2026.01.06-10.09.00 Stats.csv").write_text("Kills:,1\n")
            _SCAN_STATE["sig"] = None; d_ = scan_day(sd_, dd)
            assert SCAN_INFO["miss"] == 1 and _SCAN_STATE["sig"] is None and "VT Pasu Novice S5 - Challenge - 2026.01.06-10.09.00 Stats.csv" not in _SCORE_CACHE
            _SCAN_STATE["sig"] = None; d_ = scan_day(sd_, dd)                      # 두 번째도 점수 없음 → 영구 미인식으로 캐시, 폴더 캐시 살아남
            assert SCAN_INFO["miss"] == 1 and _SCAN_STATE["sig"] is not None and _SCORE_CACHE["VT Pasu Novice S5 - Challenge - 2026.01.06-10.09.00 Stats.csv"][1] is None
        # v3 정보: 세션 요약·스트릭·주간·진행바·벤치 조언·죽음 추세
        ss = session_summary([("pasu","19.02.10",500),("dot","19.43.00",900)], {"pasu":(450,480),"dot":(1000,1100)})
        assert ss["n"] == 2 and ss["minutes"] == 41 and ss["n_pb"] == 1 and fmt_session(ss) == "41분 (19:02–19:43)", (ss, fmt_session(ss))
        assert session_summary([("pasu","10.00.00",500),("pasu","10.01.00",520),("pasu","10.02.00",530)], {"pasu":(450,480)})["n_pb"] == 1
        assert fmt_session(session_summary([], {})) == ""
        assert streak({"2026-09-01","2026-09-02","2026-09-03"}, date(2026,9,4)) == (3, 3)
        assert streak({"2026-09-05","2026-09-07"}, date(2026,9,7))[0] == 2           # 일요일(휴식) 건너뜀
        ws = week_strip({"2026-09-01"}, date(2026,9,3)); assert len(ws) == 7 and ws[6][1] == "rest" and ws[1][1] == "done" and ws[2][1] == "miss" and ws[3][1] == "today" and ws[4][1] == "future", ws
        assert SEED_DATE not in training_days({"days": {SEED_DATE: {"first": {}, "count": {}, "best": dict(SEED)}, "2026-09-01": {"first": {"pasu": 1}, "count": {"pasu": 1}}}})
        sg = segment_geometry(120, 6); assert len(sg) == 6 and sg[-1][1] <= 120 and max(b-a for a, b in sg) - min(b-a for a, b in sg) <= 1
        assert len(segment_geometry(60, 12)) == 12 and len(segment_geometry(100, 30)) == 12
        dsyn = {"first": {"pasu": 1}, "count": {"ground": 2, "dot": 3}, "checks": {"miyagi": True, "ranked": False}}
        assert section_progress([("probe","pasu",1),("probe","w4",1)], dsyn) == (1, 2) and section_progress([("warm","ground",2)], dsyn) == (2, 2)
        assert section_progress([("main","dot",6)], dsyn) == (3, 6) and section_progress([("check","miyagi",1),("check","ranked",1)], dsyn) == (1, 2)
        assert next_routine_key([("warm","ground",2),("main","dot",6)], dsyn, None) == "dot" and next_routine_key([], dsyn, "frog") == "frog"
        for sub_t in SUBS:
            for _k, th_t in sub_t[3]:
                for e_t in (200, 300, 400): assert scenE(math.ceil(score_for_energy(e_t, th_t)), th_t) >= e_t
        wl = weakest_link(SEED)
        assert wl["sub"] == "speed" and wl["total_now"] == 339 and wl["needs"] == [("dot", 1030, 60), ("eddie", 810, 30)] and wl["total_next"] == ("Gold", 61), wl
        assert wl["total_after"] > 339 and "Speed" in fmt_weakest(wl) and weakest_link({}) is None
        assert fmt_gap(413, [290,340,390,445]) == ("Gold까지 32", RANKC[3]) and fmt_gap(477, [290,340,390,445]) == ("Gold +32", C["gold"]) and fmt_gap(None, [1,2,3,4]) == ("", C["dim"])
        dth = {"days": {"2026-09-01": {"deaths": {"aim": 3, "pos": 1, "dec": 0, "trade": 0}}, "2026-09-03": {"deaths": {"aim": 1, "pos": 2, "dec": 0, "trade": 0}},
                        "2026-08-27": {"deaths": {"aim": 5, "pos": 0, "dec": 0, "trade": 0}}}}
        dw = deaths_window(dth, "2026-09-03"); assert dw["total"] == 7 and dw["days"] == 2 and dw["aim"] == 4
        dt_ = deaths_trend(dth, "2026-09-03"); assert dt_["dom"] == "aim" and dt_["dom_share"] == 57 and dt_["prev_share"] == 100 and dt_["delta"] == -43
        assert fmt_deaths_trend(dt_)[1] == C["ok"] and "에임 57%" in fmt_deaths_trend(dt_)[0]
        assert fmt_deaths_trend(deaths_trend({"days": {}}, "2026-09-03")) == ("이번 주 태그 없음", C["dim"])
        assert fmt_deaths_trend(deaths_trend({"days": {"2026-09-03": {"deaths": {"aim": 2, "pos": 0, "dec": 0, "trade": 0}}}}, "2026-09-03"))[1] == C["hint"]
        # v3 코치: 블록 추세·피로·남은 시간·요약·초점·유효성
        bt = block_trend([(0,900),(1,920),(2,940)]); assert bt[0] == "↗" and abs(bt[1] - 2.17) < 0.05, bt
        assert block_trend([(0,940),(1,920),(2,900)])[0] == "↘" and block_trend([(0,900),(1,905),(2,900)])[0] == "→" and block_trend([(0,1),(1,2)]) is None
        assert blocks_of(["ground","ground","frog","float"] + ["dot"]*6) == [("dot", 4, 10)]
        fs_ = fatigue_signal([("dot","10.00.00",1000),("dot","10.01.00",960),("dot","10.02.00",940)], {}); assert fs_["kind"] == "streak" and abs(fs_["drop"] - 6) < 0.01
        assert fatigue_signal([("dot","10.00.00",1000),("dot","10.01.00",980),("dot","10.02.00",990)], {}) is None
        assert fatigue_signal([("pasu","10.00.00",740),("pasu","10.01.00",750),("pasu","10.02.00",745)], {"pasu": 820})["kind"] == "under"
        assert fatigue_signal([("ground","10.00.00",1),("ground","10.01.00",1),("ground","10.02.00",1)], {}) is None
        longp = [("dot", f"{10 + m // 60}.{m % 60:02d}.00", 900) for m in range(0, 76, 15)]      # 10:00~11:15 한 세션 75분
        assert fatigue_signal(longp, {})["kind"] == "long" and len(sessions_of([("dot","10.00.00",1),("dot","10.40.00",1)])) == 2
        assert fatigue_signal([("dot","10.00.00",1),("dot","12.00.00",1),("dot","12.30.00",1)], {}) is None   # 마지막 세션만 30분
        assert remaining_estimate([("a","10.00.00",1),("b","10.01.30",1),("c","10.03.00",1),("d","10.40.00",1)], 10) == 15 and remaining_estimate([], 0) is None
        sm = fmt_seq_summary(14, 27, 1, [0.023], (6, 6), (0.4, -0.2), 18, None)
        assert sm == "오늘 14/27판 · PB 1 🏆 · ▲2.3% · 프로브 6/6 발로 +0.4 옵치 -0.2 · 남은 13판 ≈ 18분", sm
        fx = {"pb": {"eddie": 800}, "days": {SEED_DATE: {"first": {}, "best": dict(SEED)}}}
        for i, v in enumerate((740, 750, 745, 705)):
            fx["days"][f"2026-09-0{i+1}"] = {"first": {"eddie": v}, "best": {"eddie": v}}
        assert focus_pick(fx, "2026-09-05")[0] == "eddie"                                   # 705 는 평균 745 의 -5%
        fx["days"]["2026-09-04"]["first"]["eddie"] = 730; assert focus_pick(fx, "2026-09-05") is None   # -2%
        assert focus_pick({"pb": {}, "days": {"2026-09-01": {"first": {"eddie": 700}, "best": {}}}}, "2026-09-02") is None
        assert cond_adjust({"sleep": 5, "feel": 5}).startswith("수면 5h") and cond_adjust({"sleep": 8, "feel": 7}) is None and cond_adjust({"sleep": None, "feel": 2}).startswith("체감 2")
        assert probe_validity([("pasu","1",1),("ground","2",1),("ground","3",1)]) == ("pasu", "cold")
        assert probe_validity([("ground","1",1),("frog","2",1),("pasu","3",1)]) is None
        assert probe_validity([("ground","0",1)] + [("eddie", str(i), 1) for i in range(4)]) == ("eddie", "extra")
        nr = nearest_rankup(SEED); assert nr and nr[1] in SEED and nr[3] in RANK_NAMES
        sb = session_brief(fx, "2026-09-05", "v", []); assert 1 <= len(sb) <= 3 and "지수" in sb[0][0]
        assert session_brief(fx, "2026-09-05", "r", [], alt=[("x", "sub")]) == [("x", "sub")]
        # v3 기록 탭 · 단축키
        hx = {"pb": dict(SEED), "days": {SEED_DATE: dict(blank_day(), best=dict(SEED)),
              "2026-09-01": dict(blank_day(), first={"pasu": 800}, best={"pasu": 850}, count={"pasu": 2}, sess={"start": "10.00.00", "end": "10.41.00"},
                                 deaths={"aim": 2, "pos": 1, "dec": 0, "trade": 0}, cond={"sleep": 7, "caf": 0, "feel": 6}, checks={"miyagi": True, "ranked": False}),
              "2026-09-03": dict(blank_day(), first={"dot": 1}, best={"dot": 1}, count={"dot": 1})}}
        hx["pb"]["pasu"] = 850
        hr = history_rows(hx, "2026-09-03", probe_series(hx), pb_days(hx), n=6)
        assert len(hr) == 6 and hr[0]["date"] == "2026-09-03" and hr[1]["trained"] is False and hr[2]["trained"] is True
        assert hr[5]["dtype"] == "seed" and hr[5]["trained"] is False and hr[5]["energy"] == 339 and hr[2]["energy"] is None and hr[5]["pbs"] == []
        assert hr[2]["pbs"] == ["pasu"] and hr[2]["minutes"] == 41 and hr[2]["dom"] == "에임" and hr[2]["miyagi"]
        fr = fmt_history_row(hr[2]); assert fr[0] == "09-01 화" and fr[2] == "2" and fr[3] == "41" and fr[6] == "1" and fr[7] == "3 에임" and fr[11] == "M", fr
        assert fmt_history_row(hr[1])[2] == "·" and fmt_history_row(hr[5])[1] == "기준"
        dd_ = day_detail(hx, "2026-09-01"); assert [x[0] for x in dd_] == [k for sub in SUBS for k, _ in sub[3]] and dd_[0] == ("pasu", 800, 850, 2, True)
        g0 = growth_since_seed({"pb": dict(SEED), "days": {}}); assert all(r["stalled"] for r in g0) and energy_delta({"pb": dict(SEED)}) == (339, 339)
        g1 = growth_since_seed(hx); assert g1[0]["key"] == "pasu" and abs(g1[0]["pct"] - 5.46) < 0.01 and fmt_growth_row(g1[0])[3] == "" and g1[0]["band_pb"] == "Gold"
        assert fmt_growth_row(g1[-1])[2] == "정체"
        # v3.2 훈련 레벨
        assert level_of(0)[:2] == (1, "입문") and level_of(29)[0] == 1 and level_of(30)[:2] == (2, "수련")
        assert level_of(10 ** 6)[3] is None and level_frac(10 ** 6) == 1.0
        assert level_frac(0) == 0.0 and abs(level_frac(55) - 0.5) < 1e-9
        assert fmt_level(55) == "Lv.2 수련  25/50", fmt_level(55)
        _xd = {"days": {SEED_DATE: dict(blank_day(), best={"pasu": 800}),
                        "2026-09-09": dict(blank_day(), best={"pasu": 850}, plays=[["pasu", "10.00.00", 850]] * 3),
                        "2026-09-10": dict(blank_day(), best={"pasu": 840}, plays=[["pasu", "11.00.00", 840]] * 2)}}
        assert total_pbs(_xd) == 1 and total_xp(_xd) == 5 + 5 * 1           # 판 5 + 신기록 1
        assert total_xp({"days": {}}) == 0 and total_pbs({"days": {}}) == 0
        assert total_xp({"days": {"2026-09-09": dict(blank_day(), count={"pasu": 4})}}) == 4   # 옛 파일: count 합
        # v3.2 세션 곡선
        bump_ver()
        _sd = {"pb": {}, "days": {"2026-09-10": dict(blank_day(), plays=[["pasu", "10.00.00", 806], ["pasu", "10.02.00", 900]])}}
        assert play_base(_sd, "pasu", "2026-09-10") == SEED["pasu"]                  # 첫날: 기준값으로 물러난다
        _sp = session_points(_sd, "2026-09-10")
        assert len(_sp) == 2 and _sp[0][3] == 0.0 and _sp[1][3] > 0
        assert session_points({"pb": {}, "days": {}}, "2026-09-10") == []
        assert session_caption([], None) == "판이 들어오면 여기에 한 판씩 점이 찍힙니다"
        _cap = session_caption(_sp, 4.0)
        assert "2판" in _cap and "평소 대비 중앙" in _cap and "세션 중 상승 +4.0%" in _cap, _cap
        # v3.2 오늘 한 장
        bump_ver()
        _cd = {"pb": {"pasu": 900, "popcorn": 500}, "days": {
            "2026-09-09": dict(blank_day(), best={"pasu": 790, "popcorn": 500}),
            "2026-09-10": dict(blank_day(), best={"pasu": 900}, plays=[["pasu", "10.00.00", 870], ["pasu", "10.30.00", 900]])}}
        _ch = day_changes(_cd, "2026-09-10")
        assert _ch and _ch[0].startswith("Pasu 900 신기록 (+110)") and "Gold 칸 진입" in _ch[0], _ch
        assert any(x.startswith("총 에너지") for x in _ch), _ch
        assert day_changes(_cd, "2026-09-09") == []                     # 달라진 게 없으면 빈 목록
        _sc = session_card(_cd, "2026-09-10", "발로 데이", "클리킹 집중")
        assert _sc["title"] == "9월 10일 목 · 발로 데이 · 클리킹 집중" and _sc["kinds"] == ["pb", "pb"], _sc
        assert _sc["stat"].startswith("2판") and "최고 2" in _sc["stat"], _sc["stat"]
        assert session_card({"pb": {}, "days": {}}, "2026-09-10", "휴식")["changed"] == []
        # v3.2 오늘의 띠
        _dd = {"pb": {}, "days": {
            "2026-09-08": dict(blank_day(), best={"pasu": 820}, plays=[["pasu", "10.00.00", 800], ["pasu", "10.02.00", 820],
                                                                        ["pasu", "10.04.00", 790], ["pasu", "10.06.00", 810]]),
            "2026-09-10": dict(blank_day(), plays=[["pasu", "10.00.00", 900], ["pasu", "10.02.00", 805], ["pasu", "10.04.00", 700]])}}
        bump_ver()
        assert pb_before_day(_dd, "2026-09-10") == {"pasu": 820} and pb_before_day(_dd, "2026-09-08") == {}
        _v = [k for _, _, k in day_verdicts(_dd, "2026-09-10")]
        assert _v == ["pb", "normal", "low"], _v                       # 900 신기록 → 805 평소 → 700 낮음
        assert ribbon_cells(5, _v) == ["gold", "sub", "dim", "todo", "todo"]
        assert ribbon_cells(2, _v) == ["gold", "sub", "dim"]           # 계획보다 더 치면 칸이 늘어난다
        assert ribbon_cells(3, []) == ["todo"] * 3 and ribbon_cells(0, []) == []
        assert ribbon_counts(_v)["pb"] == 1 and ribbon_counts([])["low"] == 0
        assert set(RIBBON_H) == {"gold", "ok", "sub", "dim", "todo"} and RIBBON_H["gold"] == 1.0
        _hs = [RIBBON_H[k] for k in ("gold", "ok", "sub", "dim", "todo")]
        assert _hs == sorted(_hs, reverse=True) and min(_hs[i] - _hs[i + 1] for i in range(4)) >= 0.15   # 눈에 띄는 차이
        assert mask_user_path(r"C:\Users\hong\Steam\stats") == r"C:\Users\…\Steam\stats"
        assert mask_user_path("/home/joy/FPSAimTrainer/stats") == "/home/…/FPSAimTrainer/stats"
        assert mask_user_path("D:\\Games\\stats") == "D:\\Games\\stats" and mask_user_path("") == "" and mask_user_path(None) == ""
        assert fmt_ribbon(27, _v) == "오늘 3/27판 · 최고 1 · 평소 1 · 낮음 1", fmt_ribbon(27, _v)
        assert fmt_ribbon(27, []).endswith("여기가 채워집니다") and fmt_ribbon(0, []) == "오늘 0판"
        assert shortcut_action("2", 0, False) == "tab:grow" and shortcut_action("2", 0, True) is None and shortcut_action("F5", 0, True) == "rescan"
        assert shortcut_action("r", 0x4, False) == "run" and shortcut_action("r", 0, False) is None and shortcut_action("o", 0x4, True) == "folder"
        assert seq_shortcut_action("space", 0, False) == "auto" and seq_shortcut_action("space", 0, True) is None and seq_shortcut_action("n", 0x4, False) == "skip"
        assert seq_shortcut_action("Escape", 0, True) == "blur" and seq_shortcut_action("Escape", 0, False) == "close" and seq_shortcut_action("r", 0, False) is None
        # v3 권장: 정체·다음 한 걸음·벤치 준비도·주간 리캡
        assert plateau([800,802,799,801,800,803,798,800,801,799]) and not plateau([800,810,820,830,840,850,860,870,880,890]) and not plateau([800]*5)
        assert spark_tag([800,810,820,830,840,850,860,870,880,890]) == "↗" and spark_tag([]) == "" and spark_tag([900,880,860,840]) == "↘"
        nx = {"pb": dict(SEED), "days": {"2026-09-03": dict(blank_day(), first={"eddie": 720}, best={"eddie": 720}, count={"eddie": 1})}}
        assert "Eddie" in next_step(nx, "2026-09-03", [("eddie","10.00.00",720)], {"eddie": 745.0}) and "745" in next_step(nx, "2026-09-03", [], {"eddie": 745.0})
        dotp = [("dot", f"10.0{i}.00", v) for i, v in enumerate((1000, 990, 970, 950, 940, 930))]
        ns2 = next_step({"pb": dict(SEED), "days": {"2026-09-03": blank_day()}}, "2026-09-03", dotp, {}); assert "6→4판" in ns2, ns2
        ns3 = next_step({"pb": dict(SEED), "days": {"2026-09-03": blank_day()}}, "2026-09-03", [], {}); assert "다음:" in ns3 or "프로브부터" in ns3
        full = dict(blank_day(), count={k: n for k, n in WARMUP + MAIN}, first={k: 1 for k in PROBE})
        assert routine_complete(full, "v") and not routine_complete(dict(full, first={k: 1 for k in PROBE[1:]}), "v") and not routine_complete(full, "r")
        bx = {"pb": dict(SEED), "days": {SEED_DATE: dict(blank_day(), best=dict(SEED))}}
        br = bench_readiness(bx, "2026-09-04"); assert br["e_pb"] == 339 and br["week_pbs"] == [] and br["last_run"] == (SEED_DATE, 339), br
        bx["days"]["2026-09-01"] = dict(blank_day(), best={"pasu": 820}, count={"pasu": 1}); bump_ver()
        assert week_pbs(bx, "2026-09-04") == ["pasu"] and projected_energy(SEED, {"pasu": 500})[0] < 339
        assert bench_lines(bench_readiness(bx, "2026-09-04"), "w")[0][0].startswith("내일 벤치") and bench_lines(bench_readiness(bx, "2026-09-05"), "b")[0][0].startswith("0/18 · 예상")
        assert week_of("2026-09-03") == ["2026-08-31", "2026-09-01", "2026-09-02", "2026-09-03"]
        assert weekly_recap({"pb": {}, "days": {}}, "2026-09-06") == [("이번 주 기록 없음", "sub")]
        wr = weekly_recap(bx, "2026-09-06"); assert "판" in wr[0][0] and wr[-1][0].startswith("수면 입력")
        sx = {"pb": {}, "days": {}}
        for i in range(14):
            d_i = (date(2026, 8, 1) + timedelta(days=i)).isoformat()
            hi_ = i % 2 == 0
            sx["days"][d_i] = dict(blank_day(), first={k: (900 + (60 if hi_ else -60) + i) for k in PROBE}, cond={"sleep": 8 if hi_ else 5, "caf": 0, "feel": 5})
        bump_ver(); a_, b_, n1_, n2_ = sleep_effect(sx); assert n1_ >= 5 and n2_ >= 5 and a_ is not None and a_ > b_, (a_, b_, n1_, n2_)
        # v3 UI 순수 함수: 순서창 높이·스크롤·간단히·시나리오 상세
        assert seq_window_height(900, 700) == 525 and seq_window_height(300, 700) == 300
        assert scroll_to_show(100, 20, 1000, 300, 0.0) == 0.0 and scroll_to_show(500, 20, 1000, 300, 0.0) == 0.46 and scroll_to_show(990, 20, 1000, 300, 0.0) == 0.7
        assert scroll_to_show(100, 20, 200, 300, 0.3) == 0.0
        vr = visible_rows([True]*10 + [False]*17, 10, set(), True); assert vr[0] == list(range(8, 15)) and vr[1] == 8 and vr[2] == 12, vr
        assert visible_rows([True]*3 + [False]*2, 3, set(), False) == ([0, 1, 2, 3, 4], 0, 0)
        assert visible_rows([True]*5, None, set(), True) == ([3, 4], 3, 0)
        assert visible_rows([True, False, True, False], 1, set(), True) == ([0, 1, 3], 1, 0)
        r2, npb2, _ = seq_rows_apply(["pasu","pasu"], [True, True], None, [850, 860], lambda k: (800.0, 806)); assert npb2 == 1 and r2[1][6] == "PB!"
        _b = robust_band([790, 800, 810, 820])
        _vfn = lambda k_, sc_: play_verdict(sc_, _b, 820)
        _r3, _n3, _ = seq_rows_apply(["pasu", "pasu"], [True, True], None, [805, 900], lambda k: (800.0, 820), _vfn)
        assert _r3[0][6] == "평소" and _r3[0][7] == "sub" and _r3[1][6] == "최고" and _n3 == 1, (_r3[0], _r3[1])
        _dd2 = {"days": {"2026-09-06": dict(blank_day(), best={"pasu": 800}), "2026-09-07": dict(blank_day(), best={"pasu": 810}),
                         "2026-09-08": dict(blank_day(), best={"pasu": 790}), "2026-09-09": dict(blank_day(), best={"pasu": 820})}}
        bump_ver(); _db = scen_day_band(_dd2, "pasu", "2026-09-10"); assert _db and _db["n"] == 4 and _db["mid"] == 805
        assert scen_day_band(_dd2, "pasu", "2026-09-10", "first") is None            # first 기록이 없으면 판단 보류
        sh = scen_history(hx, "pasu", "2026-09-03"); assert [h["date"] for h in sh] == [SEED_DATE, "2026-09-01"] and sh[1]["first"] == 800
        ssm = scen_summary(hx, "pasu", "2026-09-03"); assert ssm["pb"] == 850 and ssm["pb_date"] == "2026-09-01" and ssm["trend"] is None and "PB 850" in fmt_scen_summary(ssm)
        # v3.1: 키 이름 정규화 · 키 상태 · 벤치 플레이리스트 · 날짜 재정의
        assert norm_key("f5") == "F5" and norm_key(" F10 ") == "F10" and norm_key("num+") == "Add" and norm_key("+") == "Add" and norm_key("Add") == "Add"
        assert norm_key("numpad 5") == "NumPadFive" and norm_key("num5") == "NumPadFive" and norm_key("NumPadFive") == "NumPadFive" and norm_key("5") == "Five"
        assert norm_key("space") == "SpaceBar" and norm_key("pagedown") == "PageDown" and norm_key("n") == "N" and norm_key("Nine") == "Nine"
        assert norm_key("Gamepad_X") is None and norm_key("") is None and norm_key(None) is None and norm_key("   ") is None and norm_key("xyz") is None
        assert vk_of("f5") == 0x74 and vk_of("num+") == 0x6B and vk_of("numpad5") == 0x65 and vk_of("space") == 0x20 and vk_of("f25") is None and vk_of("F13") is None
        assert norm_key("ｆ５") == "F5" and norm_key("kp5") == "NumPadFive" and norm_key("mouse4") == "ThumbMouseButton" and norm_key("thumbmousebutton") == "ThumbMouseButton"
        assert can_send("ThumbMouseButton") and can_send("f5") and not can_send("Gamepad_X") and not can_send("")
        assert key_label("Add") == "Add (넘패드 +)" and key_label("NumPadFive") == "NumPadFive (넘패드 5)" and key_label("F5") == "F5" and key_label("Five") == "Five (숫자 5)" and key_label(None) == ""
        ks = key_status(None, None, "nofile"); assert "Input.ini" in key_line(ks)[0]
        ks = key_status(None, None, "removed"); assert "해제" in key_line(ks)[0]
        ks = key_status(None, "ThumbMouseButton"); assert ks["key"] == "ThumbMouseButton" and "마우스" in key_line(ks)[0] and key_line(ks)[1] == "ok"
        ks = key_status("f5", "Add"); assert ks["key"] == "F5" and ks["src"] == "override" and ks["mismatch"] == ("F5", "Add") and key_line(ks)[1] == "val" and "Add" in key_line(ks)[0]
        ks = key_status("", "Add"); assert ks["key"] == "Add" and ks["src"] == "ini" and ks["mismatch"] is None and key_line(ks)[1] == "ok" and "Add" in key_line(ks)[0]
        ks = key_status("F10", "F10"); assert ks["mismatch"] is None and key_line(ks)[1] == "ok" and "일치" in key_line(ks)[0]
        ks = key_status("f10", "F10"); assert ks["key"] == "F10" and ks["mismatch"] is None
        ks = key_status("xyz", None); assert ks["key"] is None and ks["unknown"] == "xyz" and key_line(ks)[1] == "val"
        ks = key_status(None, None); assert ks["key"] is None and ks["src"] is None and "PlaylistNext" in key_line(ks)[0] and key_line(ks)[1] == "val"
        ks = key_status(None, "Gamepad_X"); assert ks["key"] is None and ks["unknown"] == "Gamepad_X" and key_line(ks)[1] == "val"
        ks = key_status("F5", None); assert ks["key"] == "F5" and ks["mismatch"] is None and "여야" in key_line(ks)[0]
        _pls = playlists_for("2026-09-10")
        assert dict(_pls)["AIMDESK Bench"] == [(k, 1) for s in SUBS for k, _ in s[3]] and len(dict(_pls)["AIMDESK Bench"]) == 18 and len(_pls) == 4
        # 요일 변주: 월~목이 한 주 안에서 모두 다르고, 판 수는 늘 17, 다음 주엔 밀린다
        _mon = date.fromisoformat("2026-09-07")
        _wk = [main_theme((_mon + timedelta(days=i)).isoformat())[0] for i in range(4)]
        assert len(set(_wk)) == 4, _wk
        _wk2 = [main_theme((_mon + timedelta(days=7 + i)).isoformat())[0] for i in range(4)]
        assert _wk2 != _wk and len(set(_wk2)) == 4, _wk2
        for _t in MAIN_THEMES: assert sum(n for _, n in _t[3]) == 17, _t[0]
        assert sum(n for _, n in main_theme("2026-09-10", SEED)[3]) == 17
        assert main_theme("2026-09-10")[0] != "weak"                      # 기록 없으면 약점 테마로 안 감
        assert {main_theme((_mon + timedelta(days=i)).isoformat(), SEED)[0] for i in range(4)} == {"clk", "trk", "swt", "weak"}
        _w = weak_theme(SEED); assert _w and _w[0] == "weak" and sum(n for _, n in _w[3]) == 17
        assert weak_theme({}) is None and weak_theme({"pasu": 700}) is None
        assert theme_line("2026-09-07", SEED).startswith("오늘 본훈련 · ") and "내일은 " in theme_line("2026-09-07", SEED)   # 월→화
        assert "4일 뒤는 " in theme_line("2026-09-10", SEED), theme_line("2026-09-10", SEED)             # 목→월
        assert theme_line("2026-09-11") == "" and theme_line("2026-09-12") == "" and theme_line("2026-09-13") == ""   # 금·토·일은 고정
        _wt = week_themes("2026-09-09", SEED)
        assert _wt.startswith("이번 주 · 월 ") and "▶수 " in _wt and _wt.count("·") == 4, _wt
        assert week_themes("2026-09-12") == ""                                   # 토요일엔 안 띄운다
        _ch = daily_challenge({"pb": dict(SEED), "days": {}}, "2026-09-10", dict(SEED))
        assert _ch is None or (_ch["target"] > _ch["cur"] and _ch["sigma"] <= 2.5 and _ch["key"] in dict(SCEN)), _ch
        _far = daily_challenge({"pb": {"ww5": 10}, "days": {}}, "2026-09-10", {"ww5": 10}); assert _far is None   # 너무 멀면 안 낸다
        _c2 = {"key": "dot", "target": 1030, "cur": 983, "rank": "Silver", "gap": 47, "sigma": 1.2}
        assert fmt_challenge(_c2).startswith("오늘의 도전 · DotTS 1030점 — 넘으면 Silver 칸")
        assert "17 남음" in fmt_challenge(_c2, 1013) and "✓ 달성" in fmt_challenge(_c2, 1030)
        assert fmt_challenge(None) == "" and daily_challenge({"pb": {}, "days": {}}, "2026-09-13") is None
        assert sum(n for _, n in dict(playlists_for("2026-09-10", SEED))["AIMDESK Day"]) == 27
        assert seq_rows_apply(["pasu"], [True], None, [None], lambda k: (None, None))[0][0][6] == "건너뜀"
        import tempfile as _tf
        with _tf.TemporaryDirectory() as _td:
            _st = Path(_td) / "FPSAimTrainer" / "stats"; _st.mkdir(parents=True)
            _n, _d, _w = ensure_playlists(_st); assert (_n, _w) == (4, 4) and _d == Path(_td) / "FPSAimTrainer" / "Saved" / "SaveGames" / "Playlists"
            _raw = (_d / "AIMDESK Bench.json").read_bytes(); assert _raw[:2] == b"\xff\xfe" and "\r\n" in _raw.decode("utf-16")        # 기본: UTF-16 BOM + CRLF
            _obj = json.loads(_raw.decode("utf-16")); assert _obj["playlistName"] == "AIMDESK Bench" and [x["scenario_Name"] for x in _obj["scenarioList"]] == [SCEN[k][0] for k, _ in BENCH]
            assert ensure_playlists(_st)[2] == 0                                                                    # 같은 내용이면 다시 쓰지 않는다
            (_d / "Mine.json").write_text(json.dumps({"playlistName": "Mine", "version": 3, "scenarioList": [{"scenario_Name": "x", "play_Count": 1}]}), encoding="utf-8")
            _n, _d, _w = ensure_playlists(_st); assert (_n, _w) == (4, 4) and PL_STATE["tpl"] == "Mine" and PL_STATE["enc"] == "utf-8"
            _raw = (_d / "AIMDESK Day.json").read_bytes(); assert _raw[:1] == b"{" and b"\r\n" not in _raw            # 코박스 파일 형식(UTF-8, LF)을 따라간다
            _obj = json.loads(_raw.decode("utf-8")); assert _obj["version"] == 3 and _obj["playlistName"] == "AIMDESK Day" and len(_obj["scenarioList"]) == len(dict(playlists_for(today_date().isoformat()))["AIMDESK Day"])
        os.environ["AIMDESK_TODAY"] = "2026-09-05"; assert today_date().weekday() == 5
        os.environ["AIMDESK_TODAY"] = "bad"; assert today_date() == date.today(); del os.environ["AIMDESK_TODAY"]
        # v3.2 성장 가시화
        assert robust_band([100, 100, 100]) is None                      # n<4 판단 보류
        b_ = robust_band([90, 95, 100, 105, 110]); assert b_["mid"] == 100 and b_["n"] == 5 and b_["lo"] < 100 < b_["hi"]
        assert abs(robust_band([100] * 6)["sd"] - 2.0) < 1e-9            # 전부 같으면 2%
        assert play_verdict(None, b_) == ("new", "", "dim") and play_verdict(500, None)[0] == "new"
        assert play_verdict(120, b_)[0] == "high" and play_verdict(80, b_) == ("low", "낮음", "dim") and play_verdict(100, b_)[0] == "normal"
        assert play_verdict(101, b_, pb=100)[0] == "pb" and play_verdict(99, b_, pb=100)[0] == "normal"
        assert abs(band_z(b_["mid"] + b_["sd"], b_) - 1.0) < 1e-9 and band_z(100, None) is None
        _d = {"days": {"2026-09-08": dict(blank_day(), plays=[["pasu", "10.00.00", 800], ["pasu", "10.02.00", 820]]),
                       "2026-09-09": dict(blank_day(), plays=[["pasu", "10.00.00", 810]]),
                       "2026-09-10": dict(blank_day(), plays=[["pasu", "10.00.00", 900]])}}
        assert scen_play_pool(_d, "pasu", "2026-09-10") == [810, 800, 820]                  # 오늘 제외
        assert 900 in scen_play_pool(_d, "pasu", "2026-09-10", include_today=True)
        assert day_dots(_d, "pasu", "2026-09-10", 3) == [(0, 0, 800), (0, 1, 820), (1, 0, 810), (2, 0, 900)]
        _sh = sub_shape({"pasu": 660, "popcorn": 500}, SEED)
        assert len(_sh) == 9 and _sh[0]["id"] == "dyn" and _sh[0]["e"] == 200 and _sh[0]["delta"] < 0 and _sh[1]["e"] is None
        assert within_day_gain([("a", "1", 100), ("a", "2", 100)]) is None                   # 3판 미만 제외
        assert within_day_gain([("a", "1", 100), ("a", "2", 110), ("a", "3", 120)]) == 20.0  # 앞1 뒤1: 100→120
        print("selftest OK: seed energy =", e, "Silver · scan merge OK · deeplink OK · recent_stats OK · v3 base OK · v3 info OK · v3 coach OK · v3 log OK · v3 should OK · v3 ui OK · v3.1 key OK · v3.2 growth OK")
        sys.exit(0)
    main()
