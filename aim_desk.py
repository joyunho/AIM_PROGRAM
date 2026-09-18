#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
에임 데스크 v7.4 — 코박스 자동 기록 + 3초 판정 + 발로란트 루틴 + 자동 진행 + 트레이너 루프 + 매일 올리는 시리즈(업로드 팩 · 방송창 · 단계 사다리)
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
· 루틴을 마치면 그날 기록을 기록/에임데스크_YYYY-MM-DD.txt 로 저장 — 트레이너(사람·AI)에게 보내고 답장(목표·테마·메모)을 붙여넣으면 앱이 그 목표를 따른다
· v4.0: 오늘 탭 맨 위 판정 밴드 — 오늘은 어제보다? · 전체적으로 성장 중? · 요즘 부진? (면의 색 + 글리프 + 단어 + 숫자 하나, 확실치 않으면 비워 둠)
· v4.0: 발로란트 전용 루틴 — 클리킹·스위칭 위주 6개 테마가 10일 주기로 돌고(같은 테마가 이틀 연속 없음), 옵치·미야기·게임 항목 제거
· v5.0: 출발선을 직접 잰다 — 하드코딩 점수를 PB 로 주입하지 않는다. 첫날은 무슨 요일이든 '기준 측정일'(18종 1판씩)이고
  거기서 나온 점수가 data["base"] = 내 출발선. 성장·요즘은 전부 이 출발선 대비로 잰다 (첫날이 정확히 0)
· v5.0: 레벨선 이상치는 좁은 클램프가 아니라 프로브 6개의 '중앙값' 으로 막는다 — 좁은 클램프는 진짜 성장까지 잘라 성장 판정이 안 떴다
· v5.0: '판정까지 N일' 이 진짜 N일 — 두 조건(쌓인 날 수·기간)이 동시에 차는 첫 훈련일을 직접 찾는다
· v5.0: 기록이 갈라지는 걸 막는다 — 도구 탭에 지금 쓰는 파일 경로, 다른 폴더의 기록 탐지·합치기, 날짜별 백업, fsync 저장, 기록 새로 시작
· v6.0: 볼테익 3단계(노비스·인터미디어트·어드밴스드)와 졸업 — 풀런에서 9갈래 전부 최상위면 다음 단계, 출발선을 새로 잰다
· v6.0: 하루 20판(웜업 2 · 프로브 6 · 본훈련 12, 같은 판 3연속 없음) + 발로란트 블록 15분(숫자 4개) · 토 보스전 · 일 주간 결산
· v6.0: 매일 올리는 시리즈 — DAY N · 녹화 시작 시각 → 명장면·챕터(mm:ss) · 업로드 팩(제목·설명·태그·고정 댓글) · 썸네일 HTML · 16:9 오늘 한 장
· v6.0: 방송창(AimDesk Broadcast) — 원시 픽셀 프리셋 · 글자 하한 28px · 크로마 · 보스전/주간 보드 · 관문 미터 · 주인공 줄
· v6.0: 골드 2 → 불멸 다섯 단계 — 에임·게임·랭크 관문을 전부 숫자로, 두 주 연속 다 차야 다음 단계 · 발로란트 전적 연동(선택)
· v6.1: 눈에 들어오는 화면 — 회색 글씨 세 단계를 밝히고(dim 3.3:1 → 5.0:1) 기본 글꼴 한 단계 키움, 미룬 판정도 밝은 글씨('프로브 0/6'),
  라이브 줄에 큰 실행 버튼 하나, 루틴 줄은 굵은 막대, 발로 블록 설명은 접음, 옛 죽음 스텝퍼 제거, 방송창 좁은 타일은 두 줄(겹침 버그)
· v6.2: '계획' 탭 — 달력 하나로 오늘 뭘 하고 · 이번 주가 어떻게 가고 · 몇 달 뒤 어디에 있는지. 처음 켜면 이 탭부터. 화면 말을 쉬운 말로
· v6.3: 밝은 테마(기본) — 도구 탭에서 어두움으로. 방송창은 늘 어두운 고대비. 자동 코치(앱 규칙, 매일 목표·테마·메모) · AI 코치(Claude, 선택)
· v7.0: 오늘 탭을 '한 가지만'으로 — 헤드라인 하나(다음 판) · 숫자 하나(6/20) · 버튼 하나. 판정은 타일이 아니라 문장 한 줄,
  ①②③④ 는 히어로 안의 얇은 막대, 나머지(시나리오별 점수·곡선·코치·랭크·트레이너)는 '자세히' 뒤. 헤더는 네 가지, 탭은 다섯
· v7.1: 아이콘 — 금색 A 모노그램 + 조준점 (app.ico 6장 · 창 아이콘 ICON_B64 도 같은 그림. 32·16px 은 단순화한 그림)
· v7.2: 저장 위치 — 설정 탭 '기록 파일' 카드에서 기록·업로드 팩·썸네일·주간 결산이 갈 폴더를 고른다 (data["out_dir"], 기본은 기록 파일 옆 '기록')
· v7.2: 쉬는 날은 월요일 (REST_WD) — 화~금·일 훈련, 토 벤치. 주간 결산은 월요일에 지난 주(월~일)를 마감. 10일 테마 주기는 화~일 5일 × 2주
· v7.3: AI 코치 노트 — 오늘 한 줄 · 잘된 것 · 아쉬운 것 · 내일 이렇게 · 발로란트로 연결 · 이번 주 흐름 · 한마디 (COACH_SECTIONS) + === 앱 적용 === 줄.
  지난 노트·이번 주 결산·'코치에게' 를 같이 보내 이어서 코칭. 노트는 data["coach"]["notes"] 와 기록/EP###_날짜_코치.txt · 오늘 탭 '코치 노트' 링크 · 노트 창
· v7.4: 계획 탭에 코칭 — 달력 칸·이번 주 줄에 그날 코치 한 줄([오늘 한 줄] / 다음 계획일엔 [내일 이렇게] 첫 항목 / 오늘 메모), '이번 주' 아래 코치 노트 카드(내일 이렇게 · 이번 주 흐름)
· 실행: python aim_desk.py  (파이썬 3.9+, 추가 설치 없음)
"""
from __future__ import annotations
import json, math, os, re, sys, time, traceback, unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path

# 윈도우 기본 콘솔 코덱(cp949·cp1252)은 한글·특수문자를 못 찍고 UnicodeEncodeError 로 죽는다.
# 로그 한 줄 때문에 프로그램이 멈추면 안 되니 출력 스트림을 UTF-8 + 치환 모드로 돌려놓는다.
for _st in (sys.stdout, sys.stderr):
    try: _st.reconfigure(encoding="utf-8", errors="replace")   # 3.7+
    except (AttributeError, ValueError, OSError): pass

# ══════════════════ 시나리오 정의 ══════════════════
# 볼테익 S5 벤치마크 3단계 (2026-09 공식 시트 bit.ly/VTKovaaKsS5 에서 읽음 · Novice 값이 이전 하드코딩과 일치함을 확인).
# 키: Novice 는 옛 기록과 호환되게 그대로("pasu"), Intermediate/Advanced 는 "i.pasu"/"a.pasu" —
# 같은 이름의 시나리오라도 단계가 다르면 점수 척도가 달라서 한 키에 섞으면 PB·기준선이 망가진다.
TIERS = {"n": ("Novice", 0, ("Iron", "Bronze", "Silver", "Gold")),
         "i": ("Intermediate", 400, ("Platinum", "Diamond", "Jade", "Master")),
         "a": ("Advanced", 800, ("Grandmaster", "Nova", "Astra", "Celestial"))}
TIER_ORDER = ["n", "i", "a"]
TIER_KO = {"n": "노비스", "i": "인터미디어트", "a": "어드밴스드"}
SCEN = {
    # ── Novice ──
    "pasu": ("VT Pasu Novice S5", "v"),
    "popcorn": ("VT Popcorn Novice S5", "v"),
    "w4": ("VT 1w4ts Novice S5", "v"),
    "ww5": ("VT ww5t Novice S5", "v"),
    "frog": ("VT Frogtagon Novice S5", "v"),
    "float": ("VT Floating Heads Novice S5", "v"),
    "pgt": ("VT PGT Novice S5", "o"),
    "snake": ("VT Snake Track Novice S5", "o"),
    "aether": ("VT Aether Novice S5", "o"),
    "ground": ("VT Ground Novice S5", "o"),
    "raw": ("VT Raw Control Novice S5", "o"),
    "csphere": ("VT Controlsphere Novice S5", "o"),
    "dot": ("VT DotTS Novice S5", "v"),
    "eddie": ("VT EddieTS Novice S5", "v"),
    "drift": ("VT DriftTS Novice S5", "v"),
    "fly": ("VT FlyTS Novice S5", "o"),
    "cts": ("VT ControlTS Novice S5", "v"),
    "penta": ("VT Penta Bounce Novice S5", "v"),
    # ── Intermediate ──
    "i.pasu": ("VT Pasu Intermediate S5", "v"),
    "i.popcorn": ("VT Popcorn Intermediate S5", "v"),
    "i.w4": ("VT 1w3ts Intermediate S5", "v"),
    "i.ww5": ("VT ww5t Intermediate S5", "v"),
    "i.frog": ("VT Frogtagon Intermediate S5", "v"),
    "i.float": ("VT Floating Heads Intermediate S5", "v"),
    "i.pgt": ("VT PGT Intermediate S5", "o"),
    "i.snake": ("VT Snake Track Intermediate S5", "o"),
    "i.aether": ("VT Aether Intermediate S5", "o"),
    "i.ground": ("VT Ground Intermediate S5", "o"),
    "i.raw": ("VT Raw Control Intermediate S5", "o"),
    "i.csphere": ("VT Controlsphere Intermediate S5", "o"),
    "i.dot": ("VT DotTS Intermediate S5", "v"),
    "i.eddie": ("VT EddieTS Intermediate S5", "v"),
    "i.drift": ("VT DriftTS Intermediate S5", "v"),
    "i.fly": ("VT FlyTS Intermediate S5", "o"),
    "i.cts": ("VT ControlTS Intermediate S5", "v"),
    "i.penta": ("VT Penta Bounce Intermediate S5", "v"),
    # ── Advanced ──
    "a.pasu": ("VT Pasu Advanced S5", "v"),
    "a.popcorn": ("VT Popcorn Advanced S5", "v"),
    "a.w4": ("VT 1w2ts Advanced S5", "v"),
    "a.ww5": ("VT ww5t Advanced S5", "v"),
    "a.frog": ("VT Frogtagon Advanced S5", "v"),
    "a.float": ("VT Floating Heads Advanced S5", "v"),
    "a.pgt": ("VT PGT Advanced S5", "o"),
    "a.snake": ("VT Snake Track Advanced S5", "o"),
    "a.aether": ("VT Aether Advanced S5", "o"),
    "a.ground": ("VT Ground Advanced S5", "o"),
    "a.raw": ("VT Raw Control Advanced S5", "o"),
    "a.csphere": ("VT Controlsphere Advanced S5", "o"),
    "a.dot": ("VT DotTS Advanced S5", "v"),
    "a.eddie": ("VT EddieTS Advanced S5", "v"),
    "a.drift": ("VT DriftTS Advanced S5", "v"),
    "a.fly": ("VT FlyTS Advanced S5", "o"),
    "a.cts": ("VT ControlTS Advanced S5", "v"),
    "a.penta": ("VT Penta Bounce Advanced S5", "v"),
}
NAME2KEY = {v[0]: k for k, v in SCEN.items()}
def tier_of(k: str) -> str:
    """시나리오 키의 단계: 'pasu' → n · 'i.pasu' → i"""
    return k[0] if len(k) > 2 and k[1] == "." and k[0] in TIERS else "n"
def base_of(k: str) -> str:
    """단계를 뗀 몸통 키: 'i.pasu' → 'pasu'"""
    return k[2:] if tier_of(k) != "n" or (len(k) > 2 and k[1] == ".") else k
def tk(base: str, tier: str = None) -> str:
    """몸통 키 + 단계 → 실제 키. 루틴·프로브는 몸통 키로 적어 두고 현재 단계로 풀어 쓴다"""
    tier = tier or CUR_TIER[0]
    return base if tier == "n" else f"{tier}.{base}"
def sname(k, with_tier: bool = False):
    """화면용 짧은 이름: 'VT Pasu Novice S5' -> 'Pasu'. with_tier 면 단계가 다를 때 'Pasu·인터' 처럼 표시"""
    n = SCEN[k][0].replace("VT ", "")
    for t, (en, _o, _r) in TIERS.items(): n = n.replace(f" {en} S5", "")
    t = tier_of(k)
    return n + (f"·{TIER_KO[t][:2]}" if with_tier and t != "n" else "")
CUR_TIER = ["n"]                # 지금 훈련 중인 단계 — data["tier"]. 승급하면 다음 단계에서 기준 측정을 다시 한다
# 루틴 상수는 '몸통 키'(단계 없음)로 적어 둔다. set_tier() 가 현재 단계의 실제 키로 제자리 갱신한다 —
# 그래서 아래 PROBE/WARMUP/MAIN_THEMES 를 읽는 40여 곳은 단계를 몰라도 된다.
PROBE_BASE = ["w4", "pasu", "popcorn", "eddie", "drift", "cts"]   # 측정: 그날 '첫 판' — 발로란트에 닿는 클리킹 3 + 스위칭 3 (매일 고정)
WARMUP_BASE = [("ground", 1), ("float", 1)]                     # 손 깨우기 2판: 트래킹 1 → 리니어 클리킹 1 (점수 무시)
PROBE = list(PROBE_BASE); WARMUP = list(WARMUP_BASE)
MAIN   = [("ww5", 3), ("popcorn", 3), ("dot", 6), ("drift", 3), ("cts", 2)]   # v3.1 까지의 고정 본훈련 (호환용)
FRIDAY = [("raw", 12), ("csphere", 12)]                            # v3 의 금요일 컨트롤 데이 (호환용 — v4 부터 금요일도 테마 루틴)
REST_WD, BENCH_WD = 0, 5                                          # 쉬는 날 = 월요일 (v7.2 — "쉬는 요일은 무조건 월요일") · 실력 재는 날 = 토요일
DAYTYPES = ["r", "v", "v", "v", "v", "b", "v"]                     # 월 휴식 · 화~금 발로 데이 · 토 벤치마크 · 일 발로 데이
_TRAIN_CUM = [sum(1 for t in DAYTYPES[:i + 1] if t == "v") for i in range(7)]   # 요일별 '그 주 훈련일 누적' (월 0 · 화 1 … 금 4 · 토 4 · 일 5)
TRAIN_PER_WEEK = _TRAIN_CUM[6]

# 본훈련 테마 — 발로란트에 닿는 결(클리킹·스위칭·플릭)을 위주로, 같은 걸 이틀 연속 치지 않게 10일 주기로 돈다.
# 본훈련 12판. 같은 시나리오가 3판 연속 오지 않게 (2,2,2,2,1,1,1,1) 로 섞는다 — '같은 걸 5판 연속' 이 지루함의 원인이었다.
# 플레이리스트 항목도 (키, ≤2) 로 쪼개 코박스가 그 순서 그대로 돌린다. 프로브 6판은 '측정 도구'라 절대 바뀌지 않는다.
# 코박스 20판 ≈ 33분 + 발로란트 블록 15분 = 48분. 트래킹은 발로에 덜 닿아 트레이너 지정 때만.
MAIN_THEMES_BASE = [
    ("clk", "클리킹 정확",   "한 번에 정확히 찍는 손 — 크로스헤어 배치",      [("w4",2),("ww5",2),("float",2),("frog",2),("w4",1),("ww5",1),("float",1),("frog",1)]),
    ("spd", "클리킹 스피드", "빠르게 찍고 다음으로 — 연속 원탭",            [("pasu",2),("popcorn",2),("ww5",1),("eddie",1),("pasu",2),("popcorn",2),("ww5",1),("eddie",1)]),
    ("swt", "스위칭 집중",   "표적을 옮겨 다니는 손 — 멀티 킬",             [("dot",2),("eddie",2),("drift",2),("cts",2),("dot",1),("eddie",1),("drift",1),("cts",1)]),
    ("flk", "플릭 & 컨트롤", "먼 플릭과 손 안정 — 스트레이프 뒤 한 발",      [("penta",2),("fly",2),("popcorn",1),("raw",1),("csphere",1),("penta",1),("fly",1),("popcorn",1),("raw",1),("csphere",1)]),
    ("trk", "트래킹 집중",   "붙어서 따라가는 손 (트레이너가 지정할 때만)",   [("raw",2),("csphere",2),("ground",2),("aether",2),("raw",1),("csphere",1),("ground",1),("aether",1)]),
    ("mix", "전체 순회",     "9개 갈래를 한 판씩 훑는 날",                  [("pasu",1),("ww5",1),("frog",1),("snake",1),("ground",1),("raw",1),("dot",1),("drift",1),("penta",1),("w4",1),("popcorn",1),("cts",1)]),
]
MAIN_PLAYS = 12                 # 본훈련 판 수 (테마 전부 같아야 세션 길이가 일정하다)
# 10 훈련일(2주) 주기. 세 가지를 동시에 만족하게 짠 순서다 — ① 같은 테마가 이틀 연속 오지 않고,
# ② 같은 요일에 2주 연속 같은 테마가 오지 않고, ③ 달력 한 주(월~금) 안에서 5일이 전부 다른 테마다.
# ③ 때문에 순서가 CYCLE_EPOCH 요일에 묶인다 — 시작 요일이나 쉬는 요일을 바꾸면 5칸 창이 달라져 이 순서를 다시 짜야 한다 (v7.2: 창 = 화~금·일).
# 구성: 클리킹 4 (정확 2 · 스피드 2) · 스위칭 2 · 약점 2 · 플릭 1 · 순회 1
CYCLE = ["clk", "swt", "spd", "mix", "weak", "spd", "clk", "weak", "flk", "swt"]   # 5칸 창(화~일) 둘 다 서로 다른 테마 · 이틀 연속 없음 · 같은 요일 2주 연속 없음
CYCLE_EPOCH = "2026-09-15"                                          # 화요일 — 주기의 1번 날 (여기부터 CYCLE[0]). 월요일이 쉬는 날이라 화~일 5일 = 주기 절반

def _train_ord(d: date) -> int:
    """훈련일(DAYTYPES 의 v)만 세는 일련번호. 쉬는 날·벤치 날은 직전 훈련일과 같은 번호(훈련일이 아니라 쓸 일이 없다).
    기준일이 무슨 요일이든 주기가 맞게 돌도록 — 날짜 차이를 7로 나누는 방식은 기준일이 월요일일 때만 맞다."""
    n = d.toordinal() - 1                            # 0 = 0001-01-01 (월요일)
    return (n // 7) * TRAIN_PER_WEEK + _TRAIN_CUM[n % 7]

def weak_theme(pb: dict):
    """약점 집중 — 발로란트에 닿는 클리킹·스위칭 서브카테고리 중 가장 약한 둘에서 12판. 기록이 모자라면 None"""
    subs = [(s_, subE(s_, pb or {})) for s_ in SUBS if s_[1] in ("클리킹", "스위칭")]
    subs = [(s_, e) for s_, e in subs if e is not None]
    if len(subs) < 2: return None
    subs.sort(key=lambda x: x[1])
    a, b = subs[0][0], subs[1][0]
    ks = [a[3][0][0], a[3][1][0], b[3][0][0], b[3][1][0]]
    items = [(k, 2) for k in ks] + [(k, 1) for k in ks]              # 12판 · 같은 시나리오 3연속 없음
    return ("weak", "약점 집중", f"가장 낮은 {a[1]}·{a[2]} · {b[1]}·{b[2]} 를 파는 날", items)

def theme_line(dkey: str, pb: dict = None) -> str:
    """루틴 카드 맨 위 한 줄 — 오늘 무엇이 다른지와 내일 무엇이 오는지. 매일 같은 걸 친다는 느낌을 없애기 위한 것"""
    d = date.fromisoformat(dkey)
    if day_type_of(dkey) != "v": return ""
    mt = main_theme(dkey, pb)
    out = f"오늘 본훈련 · {mt[1]}" + (" (트레이너 지정)" if TRAINER["themes"].get(dkey) else "") + f" — {mt[2]}"
    for i in range(1, 4):                                    # 다음 발로 데이 예고 (토·일은 건너뛴다 — 금요일이면 +3일)
        nd = d + timedelta(days=i)
        if day_type_of(nd.isoformat()) == "v":
            nm = main_theme(nd.isoformat(), pb)[1]
            out += (f" · 내일은 {nm}" if i == 1 else f" · {i}일 뒤는 {nm}")
            break
    return out

def week_themes(dkey: str, pb: dict = None) -> str:
    """이번 주 훈련일(화~금·일) 본훈련 테마 한 줄. '매일 같은 걸 친다'는 느낌을 눈으로 반박하는 용도. 쉬는 날·벤치 날엔 비움"""
    d = date.fromisoformat(dkey)
    if DAYTYPES[d.weekday()] != "v": return ""
    mon = d - timedelta(days=d.weekday())
    out = []
    for i in range(7):
        if DAYTYPES[i] != "v": continue
        dd = mon + timedelta(days=i)
        out.append(("▶" if dd == d else "") + f"{DOWK[i]} {main_theme(dd.isoformat(), pb)[1]}")
    return "이번 주 · " + " · ".join(out)

def daily_challenge(data: dict, dkey: str, pb: dict = None):
    """오늘의 도전 — 오늘 칠 시나리오 중 '다음 등급 칸'이 가장 가까운 하나.
    목표를 앱이 지어내지 않고 볼테익 등급 임계값을 그대로 쓴다. 손이 닿는 거리가 아니면 (2.5 표준편차 밖) 내지 않는다."""
    dt = day_type_of(dkey)
    if dt == "r": return None
    if dt == "v":   items = [k for k, _n in main_theme(dkey, pb)[3]]
    else:           items = [k for k, _n in BENCH]
    pb = pb if pb is not None else data.get("pb", {})
    tset = TRAINER["targets"]
    if tset:                                           # 트레이너가 준 목표가 오늘 칠 시나리오에 있으면 그것이 도전 — 앱 임계값보다 먼저
        _pi = plan_items(dkey, pb)
        plan = [k for k, _n in (_pi[len(WARMUP):] if dt == "v" else _pi)]     # 오늘 실제로 칠 것(프로브 포함, 웜업 4판은 자리로 제외) — 여기 없는 목표는 오늘 도전이 아니다
        cands = [TRAINER["challenge"]] if (TRAINER["challenge"] in tset and TRAINER["challenge"] in plan) else [k for k in dict.fromkeys(plan) if k in tset]
        best = None
        for k in cands:
            t = tset[k]; cur = pb.get(k)
            band = scen_band(data, k, dkey) or scen_day_band(data, k, dkey)
            sd = band["sd"] if band else max(1.0, (cur or t) * 0.03)
            gap = (t - cur) if cur is not None else t
            ch = {"key": k, "target": t, "cur": cur, "rank": "", "gap": gap, "sigma": gap / sd, "src": "trainer"}
            if best is None or (gap > 0 and (best["gap"] <= 0 or ch["sigma"] < best["sigma"])): best = ch
        if best: return best
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
    if ch.get("src") == "trainer":
        s_ = f"오늘의 도전 · {sname(ch['key'])} {ch['target']}점 — 트레이너 목표" + (f" (지금 최고 {ch['cur']})" if ch["cur"] is not None else "")
    else:
        s_ = f"오늘의 도전 · {sname(ch['key'])} {ch['target']}점 — 넘으면 {ch['rank']} 칸 (지금 최고 {ch['cur']})"
    if today_best is not None:
        s_ += f" · 오늘 {today_best}" + (" ✓ 달성" if today_best >= ch["target"] else f" · {ch['target'] - today_best} 남음")
    return s_

def main_theme(dkey: str, pb: dict = None):
    """그날의 본훈련 테마 (id, 이름, 설명, [(시나리오, 판수)]).
    날짜만으로 정해진다 — 앱을 껐다 켜도, 코박스에 설치된 플레이리스트와도 늘 같은 것을 가리키게.
    CYCLE_EPOCH(화요일)부터 훈련일(월~금)을 세어 10일 주기로 돌린다 — 10 훈련일 = 딱 2주."""
    d = date.fromisoformat(dkey)
    tid = TRAINER["themes"].get(dkey)                    # 트레이너가 그날 테마를 지정했으면 그것이 먼저
    if tid is None:
        tid = CYCLE[(_train_ord(d) - _train_ord(date.fromisoformat(CYCLE_EPOCH))) % len(CYCLE)]
    if tid == "weak": return weak_theme(pb or {}) or THEME_BY_ID["mix"]   # 기록이 모자라면 '약점' 자리는 '전체 순회'
    return THEME_BY_ID.get(tid, MAIN_THEMES[0])

# ══════════════════ 트레이너 루프 (v3.4) ══════════════════
# 하루 루틴이 끝나면 그날 기록을 텍스트 한 장으로 저장한다. 사용자는 그 파일을 트레이너(사람이든 AI든)에게 보내고,
# 답장(목표 점수 · 내일 테마 · 메모)을 앱에 붙여넣으면 '오늘의 도전'과 루틴 줄이 그 목표를 따른다.
# 앱은 목표를 지어내지 않는다 — 트레이너 목표가 없으면 볼테익 등급 임계값(daily_challenge)이 그대로 쓰인다.
REPORT_VER = "v6.0"
TRAINER = {"targets": {}, "themes": {}, "note": "", "challenge": None, "set_on": None}
MAIN_THEMES = [tuple(t) for t in MAIN_THEMES_BASE]
THEME_BY_ID = {t[0]: t for t in MAIN_THEMES}

def tier_keys(tier: str = None):
    """그 단계의 벤치 18개 키 (SUBS_T 순서)"""
    return [k for sub in SUBS_T[tier or CUR_TIER[0]] for k, _th in sub[3]]

def set_tier(tier: str):
    """현재 단계를 바꾸고 루틴 상수를 그 단계의 키로 다시 푼다. load_data 와 졸업에서만 부른다"""
    if tier not in TIERS: tier = "n"
    CUR_TIER[0] = tier
    PROBE[:] = [tk(b, tier) for b in PROBE_BASE]
    WARMUP[:] = [(tk(b, tier), n) for b, n in WARMUP_BASE]
    WARM_KEYS.clear(); WARM_KEYS.update(k for k, _ in WARMUP)
    MAIN_THEMES[:] = [(t[0], t[1], t[2], [(tk(b, tier), n) for b, n in t[3]]) for t in MAIN_THEMES_BASE]
    THEME_BY_ID.clear(); THEME_BY_ID.update({t[0]: t for t in MAIN_THEMES})
    SUBS[:] = SUBS_T[tier]
    BENCH[:] = [(k, 1) for sub in SUBS_T[tier] for k, _th in sub[3]]       # 벤치 18개도 그 단계로
THEME_NAME = {"clk": "클리킹 정확", "spd": "클리킹 스피드", "swt": "스위칭 집중", "flk": "플릭 & 컨트롤", "trk": "트래킹 집중", "mix": "전체 순회", "weak": "약점 집중"}
THEME_ALIAS = [("클리킹스피드", "spd"), ("스피드", "spd"), ("speed", "spd"), ("spd", "spd"),
               ("플릭", "flk"), ("flick", "flk"), ("컨트롤", "flk"), ("control", "flk"), ("flk", "flk"),
               ("클리킹정확", "clk"), ("정확", "clk"), ("클리킹", "clk"), ("클릭", "clk"), ("clicking", "clk"), ("click", "clk"), ("clk", "clk"),
               ("트래킹", "trk"), ("트랙", "trk"), ("tracking", "trk"), ("track", "trk"), ("trk", "trk"),
               ("스위칭", "swt"), ("스위치", "swt"), ("switching", "swt"), ("switch", "swt"), ("swt", "swt"), ("ts", "swt"),
               ("전체", "mix"), ("순회", "mix"), ("mix", "mix"), ("all", "mix"),
               ("약점", "weak"), ("weak", "weak")]

def _norm_txt(s) -> str:
    """비교용: 전각→반각, 공백·밑줄·하이픈 제거, 소문자"""
    return re.sub(r"[\s_\-·.]+", "", unicodedata.normalize("NFKC", str(s or ""))).lower()

def scen_lookup(name):
    """'Pasu' · 'pasu' · 'VT Pasu Novice S5' · '1w4ts' · 'floating' → key. 모르거나 애매하면 None"""
    q = _norm_txt(name)
    if not q: return None
    t = next((tt for tt, (en, _o, _r) in TIERS.items() if _norm_txt(en) in q), None)   # 'pasu intermediate' → 그 단계
    pool = tier_keys(t or CUR_TIER[0])                                             # 단계를 안 적으면 지금 훈련 중인 단계
    sn = {k: _norm_txt(sname(k)) for k in pool}
    for k in pool:
        if q in (k, base_of(k), sn[k], _norm_txt(SCEN[k][0])): return k
    if len(q) < 3: return None
    q2 = re.sub(r"^vt", "", re.sub(r"(novice|intermediate|advanced)?(s5)?$", "", q))   # 'pasu novice s5' → 'pasu'
    hits = [k for k in pool if sn[k].startswith(q2)                               # 'floating' → float
            or (q2.startswith(sn[k]) and re.fullmatch(r"(은|는|이|가|을|를|의|도|만|에|로|으로|에서|목표|target|goal)?", q2[len(sn[k]):]))]   # 'pasu는' → pasu · 'popcorn 오늘'·'ground pb'·'pasu 861 / 861 /' → 아님
    return hits[0] if len(hits) == 1 else None

def theme_lookup(name):
    q = _norm_txt(name)
    if not q: return None
    for a, tid in THEME_ALIAS:
        if q == a or q.startswith(a): return tid                                 # '트래킹 집중' → trk
    return None

def bench_label(dkey: str) -> str:
    """벤치 날의 이름 — 출발선을 재는 날은 '기준 측정', 그 뒤 풀런은 '벤치마크'"""
    return "기준 측정" if (BASE_DATE[0] is None or dkey == BASE_DATE[0]) else "벤치마크"

def day_type_of(dkey: str) -> str:
    """v 발로 데이 · b 벤치(기준 측정/풀런) · r 휴식.
    출발선을 아직 안 쟀으면 어느 요일이든 '기준 측정일' — 18종 한 판씩 쳐서 내 출발선을 만든다"""
    if BASE_DATE[0] is None: return "b"
    if dkey == BASE_DATE[0]: return "b"                   # 기준 측정일은 나중에도 벤치로 기억한다
    return DAYTYPES[date.fromisoformat(dkey).weekday()]

def parse_trainer(text: str, today: str) -> dict:
    """트레이너 답장 → {"targets": {key: 점수}, "remove": [key], "themes": {날짜: 테마id}, "note", "challenge", "errors": [줄]}.
    형식을 엄격히 하지 않는다 — '목표: Pasu 850점 (지금 806)', '- Pasu 850', 'target pasu 850' 모두 받는다.
    못 읽은 줄은 버리지 않고 errors 로 돌려준다(사용자에게 보여 주기 위해). 답장 전체를 붙여넣어도 문장 줄은 그냥 넘어간다."""
    out = {"targets": {}, "remove": [], "themes": {}, "note": "", "challenge": None, "errors": []}
    td = date.fromisoformat(today)
    KW_T, KW_C, KW_M, KW_TH = ("목표", "target", "goal"), ("도전", "challenge"), ("메모", "memo", "note", "노트"), ("테마", "theme")
    for raw in (text or "").splitlines():
        line = raw.strip().lstrip("-•*·>").strip()
        if not line or line.startswith("#"): continue
        norm = unicodedata.normalize("NFKC", line); low = norm.lower()
        head = re.split(r"[\s:：]+", low, 1)
        kw, rest = head[0].rstrip(":："), (head[1] if len(head) > 1 else "")
        if kw in KW_M:                                                            # 메모는 자유 글 — 대소문자 그대로
            rest_raw = re.split(r"[\s:：]+", norm, 1)
            out["note"] = (out["note"] + " " + (rest_raw[1] if len(rest_raw) > 1 else "").strip()).strip(); continue
        if kw in KW_TH:
            m = re.match(r"(내일|오늘|모레|\d{4}-\d{2}-\d{2})\s*[:：]?\s*(.+)", rest.strip())
            tid = theme_lookup(m.group(2)) if m else None
            if not tid: out["errors"].append(raw.strip()); continue
            dk = {"오늘": td, "내일": td + timedelta(days=1), "모레": td + timedelta(days=2)}.get(m.group(1))
            if dk is None:
                try: dk = date.fromisoformat(m.group(1))
                except ValueError: out["errors"].append(raw.strip()); continue      # '2026-09-31' 처럼 달력에 없는 날은 받지 않는다
            out["themes"][dk.isoformat()] = tid; continue
        body = rest if kw in KW_T + KW_C else low
        body = re.sub(r"\(.*?\)|（.*?）", " ", body)                            # '(지금 806)' 같은 괄호 설명은 무시
        body = re.split(r"\s[—–]\s|\s//|\s·\s", body)[0].strip()
        m = re.match(r"(.+?)\s*[:：=→]?\s*(없음|삭제|해제|none|remove|\d[\d,]*)\s*(점|pts?|points?)?\s*$", body)
        key = scen_lookup(m.group(1)) if m else None
        if not key: out["errors"].append(raw.strip()); continue
        v = m.group(2)
        if v in ("없음", "삭제", "해제", "none", "remove", "0"):
            out["remove"].append(key); out["targets"].pop(key, None)
            if out["challenge"] == key: out["challenge"] = None
            continue
        out["targets"][key] = int(v.replace(",", ""))
        if kw in KW_C: out["challenge"] = key
    return out

def _blank_trainer() -> dict:
    return {"targets": {}, "themes": {}, "note": "", "challenge": None, "set_on": None}

def _is_dkey(k) -> bool:
    try: date.fromisoformat(str(k)); return True
    except ValueError: return False

def trainer_load(data: dict):
    """기록 파일의 트레이너 항목 → 전역 TRAINER (main_theme·daily_challenge 가 인자 없이 보게)"""
    tr = data.get("trainer") or {}
    TRAINER.update(targets={k: int(v) for k, v in (tr.get("targets") or {}).items() if k in SCEN},
                   themes={k: v for k, v in (tr.get("themes") or {}).items() if v in THEME_NAME and _is_dkey(k)},   # 손으로 고친 파일의 이상한 키가 시작을 막지 않게
                   note=str(tr.get("note") or ""), challenge=tr.get("challenge"), set_on=tr.get("set_on"))
    if TRAINER["challenge"] not in TRAINER["targets"]: TRAINER["challenge"] = None

def trainer_apply(data: dict, text: str, today: str) -> dict:
    """답장을 기록에 합친다 — 같은 시나리오는 새 목표가 이기고, 언급 없는 목표는 그대로 남는다. 파싱 결과를 돌려준다"""
    p = parse_trainer(text, today)
    tr = data.setdefault("trainer", _blank_trainer())
    for k, v in _blank_trainer().items(): tr.setdefault(k, v)
    if p["targets"] or p["remove"] or p["themes"] or p["note"] or p["challenge"]:
        for k in p["remove"]: tr["targets"].pop(k, None)
        tr["targets"].update(p["targets"]); tr["themes"].update(p["themes"])
        if p["note"]: tr["note"] = p["note"]
        if p["challenge"]: tr["challenge"] = p["challenge"]
        if tr.get("challenge") not in tr["targets"]: tr["challenge"] = None
        tr["set_on"] = today
    trainer_load(data)
    return p

def trainer_clear(data: dict):
    data["trainer"] = _blank_trainer(); trainer_load(data)

def suggest_target(target, today_best, band, pb=None):
    """트레이너가 다음 목표를 정할 때 참고할 값. 넘었으면 '직전 목표 ×1.02'와 '평소 범위 위끝' 중 큰 쪽, 못 넘었으면 유지.
    목표가 없던 시나리오는 (PB · 오늘 베스트 · 범위 위끝) 중 최대 ×1.02. 제안일 뿐 — 최종 숫자는 답장이 정한다"""
    hi = band["hi"] if band else None
    if target is None:
        base = [x for x in (pb, today_best, hi) if x is not None]
        return int(math.ceil(max(base) * 1.02)) if base else None
    if today_best is None or today_best < target: return int(target)
    return int(math.ceil(max(target * 1.02, hi or 0)))

OUT_DIR = [None]                       # 설정 탭에서 고른 저장 폴더 (None = 기록 파일 옆 '기록'). load_data 가 채운다
OUT_PATTERNS = ("에임데스크_*.txt", "EP*_업로드.txt", "EP*_썸네일.html", "EP*_코치.txt", "WEEK_*_결산.txt")   # 앱이 만드는 파일만 — 폴더의 다른 파일은 건드리지 않는다
def default_report_dir() -> Path: return DATA_FILE.parent / "기록"
def report_dir() -> Path:
    """기록 · 업로드 팩 · 썸네일 · 주간 결산이 저장되는 폴더 — 설정 탭 '저장 위치' 로 바꿀 수 있다 (data["out_dir"])"""
    return Path(OUT_DIR[0]) if OUT_DIR[0] else default_report_dir()
def dir_writable(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True); probe = p / ".aimdesk_write_test"; probe.write_text("x"); probe.unlink(); return True
    except OSError: return False
def set_out_dir(d: dict, path):
    """저장 위치를 바꾼다 — 만들 수 있고 써 볼 수 있는 폴더만 받는다. (성공, 이유)"""
    if not path:
        d["out_dir"] = None; OUT_DIR[0] = None; return True, "기본 위치"
    p = Path(str(path)).expanduser()
    if not dir_writable(p): return False, "쓸 수 없는 폴더"
    d["out_dir"] = str(p); OUT_DIR[0] = str(p); return True, str(p)
def load_out_dir(d: dict):
    """켤 때 — 저장해 둔 폴더가 지금도 쓸 수 있으면 그곳, 아니면(USB 뽑힘 등) 기본 폴더. 설정값은 지우지 않는다. 쓸 수 있는지 돌려준다"""
    od = d.get("out_dir")
    OUT_DIR[0] = str(od) if od and dir_writable(Path(str(od))) else None
    return not od or OUT_DIR[0] is not None
def out_dir_files(src: Path) -> list:
    """폴더 안의 앱 파일들 (기록 · 업로드 팩 · 썸네일 · 주간 결산)"""
    if not src.is_dir(): return []
    return sorted({f for pat in OUT_PATTERNS for f in src.glob(pat) if f.is_file()})
def move_out_files(src: Path, dst: Path):
    """앱 파일만 옮긴다. 같은 이름이 이미 있으면 건너뛴다 → (옮긴 수, 건너뛴 수)"""
    import shutil
    moved = skipped = 0
    dst.mkdir(parents=True, exist_ok=True)
    for f in out_dir_files(src):
        if (dst / f.name).exists(): skipped += 1; continue
        try: shutil.move(str(f), str(dst / f.name)); moved += 1
        except OSError: skipped += 1
    return moved, skipped
def report_path(dkey: str, dir_=None) -> Path: return (Path(dir_) if dir_ else report_dir()) / f"에임데스크_{dkey}.txt"

def plan_items(dkey: str, pb: dict = None):
    """그날 계획된 (시나리오, 판수) — 발로/약점 데이는 플레이리스트, 토요일은 벤치 18개, 휴식은 없음"""
    dt = day_type_of(dkey)
    pl = {"v": "AIMDESK Day", "b": "AIMDESK Bench"}.get(dt)
    return list(dict(playlists_for(dkey, pb))[pl]) if pl else []

def plan_count(dkey: str, pb: dict = None) -> int:
    return sum(n for _, n in plan_items(dkey, pb))

def off_plan_plays(data: dict, dkey: str, plays=None, pb: dict = None):
    """오늘 친 판 중 '오늘 계획에 없는 시나리오' 의 판 → (판 수, 시나리오 목록).
    코박스가 예전 플레이리스트를 들고 있으면 여기에 쌓인다 — 기록에는 남지만 오늘 진행률에는 안 잡힌다."""
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    plan = {k for k, _n in plan_items(dkey, pb if pb is not None else data.get("pb"))}
    if not plan or not plays: return (0, [])
    off = [k for k, _t, _s in plays if k not in plan]
    return (len(off), sorted(dict.fromkeys(off)))

def stale_playlist(data: dict, dkey: str, plays=None):
    """오늘 계획엔 없고 '직전 훈련일' 계획엔 있는 시나리오를 쳤는가 → (판 수, 그날 테마 이름).
    웜업·프로브는 매일 같아서 신호가 안 되고, 본훈련 첫 판에서 잡힌다"""
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    pb = data.get("pb")
    today = {k for k, _n in plan_items(dkey, pb)}
    d = date.fromisoformat(dkey); prev = None
    for i in range(1, 8):
        pk = (d - timedelta(days=i)).isoformat()
        if day_type_of(pk) == "v": prev = pk; break
    if prev is None or not plays: return (0, "")
    yday = {k for k, _n in plan_items(prev, pb)}
    hits = [k for k, _t, _s in plays if k not in today and k in yday]
    return (len(hits), main_theme(prev, pb)[1] if hits else "")

def fmt_off_plan(n: int, keys) -> str:
    if not n: return ""
    nm = " · ".join(sname(k) for k in keys[:4]) + ("…" if len(keys) > 4 else "")
    return (f"⚠ 계획 밖 {n}판 ({nm}) — 기록에는 남지만 오늘 진행률에는 안 잡힙니다. "
            "코박스가 예전 플레이리스트를 들고 있으면 껐다 켜세요")

def _cell(x, w=5):
    return f"{'—' if x is None else x:>{w}}"

def daily_report(data: dict, dkey: str, plays=None, dt: str = None) -> str:
    """그날 기록 한 장(텍스트). 사람이 읽고, 트레이너(AI 포함)에게 그대로 보낼 수 있게 — 화면과 같은 함수로 같은 숫자를 낸다"""
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    d = date.fromisoformat(dkey); dt = dt or day_type_of(dkey)
    day = data["days"].get(dkey) or blank_day()
    pb = data.get("pb", {}); prev = pb_before_day(data, dkey)
    theme = main_theme(dkey, pb) if dt == "v" else None
    tset = TRAINER["targets"]
    L = []
    head = f"에임 데스크 기록 · {dkey} ({DOWK[d.weekday()]}) · {bench_label(dkey) if dt == 'b' else DAY_TYPE[dt][0]}"
    if theme: head += f" · {theme[1]}" + (" (트레이너 지정)" if TRAINER["themes"].get(dkey) else "")
    L.append(head)
    tdays = training_days(data); cur_st, _best_st = streak(tdays, d)
    e_pb, _n = totalE(pb)
    L.append(f"형식 {REPORT_VER} · 훈련 {len(tdays)}일째 · 연속 {cur_st}일 · {fmt_level(total_xp(data))}"
             + (f" · PB 에너지 {e_pb} {rank_of(e_pb)[0]}" if e_pb is not None else ""))
    # ── 요약 ──
    L += ["", "[요약]"]
    plan = plan_count(dkey, pb)
    ss = session_summary(plays, {})
    verd = day_verdicts(data, dkey, plays); kinds = [k for _, _, k in verd]; c = ribbon_counts(kinds)
    line = f"판 {len(plays)}/{plan}" if plan else f"판 {len(plays)}"
    if ss["n"] and ss["minutes"] is not None: line += f" · {fmt_session(ss)}"
    for kk in ("pb", "high", "normal", "low", "new"):
        if c.get(kk): line += f" · {VERDICT_NAME[kk]} {c[kk]}"
    L.append(line)
    have = sorted(p[3] for p in session_points(data, dkey, plays) if p[3] is not None)
    g = within_day_gain(plays)
    if dkey == BASE_DATE[0]: have = []                 # 출발선을 만드는 날 — '평소' 가 곧 오늘이라 비교가 무의미
    if have:
        line = f"평소 대비 중앙 {have[len(have) // 2]:+.1f}%"
        if g is not None: line += f" · 세션 중 상승 {g:+.1f}% (앞 절반 → 뒤 절반)"
        L.append(line)
    ch = daily_challenge(data, dkey, pb)
    if ch: L.append(fmt_challenge(ch, day.get("best", {}).get(ch["key"])))
    e_old, _ = totalE(prev); e_day, n_day = totalE(day.get("best") or {})
    if dkey == BASE_DATE[0] and e_day is not None:
        line = f"출발선 에너지 {e_day} {rank_of(e_day)[0]} ({n_day}/9) — 앞으로 이 값과 비교합니다"
    else:
        line = f"총 에너지 PB {'—' if e_old is None else e_old} → {'—' if e_pb is None else e_pb}"
        if e_pb is not None and e_old is not None and e_pb > e_old: line += f" (+{e_pb - e_old})"
        if e_day is not None: line += f" · 오늘 베스트 기준 {e_day} ({n_day}/9)"
    L.append(line)
    _vl = fmt_val(day)
    if _vl: L.append("발로란트 블록: " + _vl)
    cond = day.get("cond") or {}; chk = day.get("checks") or {}; dth = day.get("deaths") or {}
    sl = cond.get("sleep")
    try: sl_txt = f"{float(sl):g}h" if sl is not None else "미입력"
    except (TypeError, ValueError): sl_txt = str(sl)
    line = f"컨디션: 수면 {sl_txt} · 체감 {cond.get('feel', '—')}/10"
    rk = day.get("rank") or {}
    if chk.get("ranked") or rk.get("tier") or rk.get("rr") is not None or any(dth.values()):
        line += " · 랭크" + (f" {rk['tier']}" if rk.get("tier") else "") + (f" RR {int(rk['rr']):+d}" if rk.get("rr") is not None else "")
        if any(dth.values()): line += " · 죽음 " + " ".join(f"{n} {dth.get(k, 0)}" for k, n in (("aim", "에임"), ("pos", "위치"), ("dec", "판단"), ("trade", "트레이드")))
    L.append(line)
    V = verdicts(data, dkey, dt, plays)
    L += ["", "[판정]  (앱이 계산한 판정 — 다시 판정하지 말고 근거로만)",
          "  " + fmt_verdict_line("오늘", V["day"]) + (f" · {V['day']['cap2']}" if V["day"].get("cap2") else ""),
          "  " + fmt_verdict_line("성장", V["grow"]) + (f" · {V['grow']['cap2']}" if V["grow"].get("cap2") else ""),
          "  " + fmt_verdict_line("요즘", V["recent"])]
    chg = day_changes(data, dkey)
    if chg: L.append("오늘 바뀐 것:"); L += [f"  - {x}" for x in chg]
    L += ["", "[단계]  (골드 2 → 불멸 다섯 단계 — 관문은 앱이 읽는 숫자. 두 주 연속 다 차면 다음 단계)"] + ["  " + x for x in stage_lines(data, dkey)]
    # ── 판별 기록 ──
    L += ["", "[판별 기록]  시각 · 시나리오 · 점수 · 판정 · 어제까지 평소 범위(판 단위)"]
    if not plays: L.append("  (오늘 판 없음)")
    for (k, t, sc), (_k, _s, kind) in zip(plays, verd):
        b = scen_band(data, k, dkey)
        rng = f"{b['lo']:.0f}–{b['hi']:.0f}" if b else "범위 없음"
        L.append(f"  {t[:5].replace('.', ':')}  {sname(k):<15} {_cell(sc)}  {VERDICT_NAME.get(kind, ''):<4} {rng}")
    # ── 시나리오별 ──
    L += ["", "[시나리오별]  오늘 베스트 / 첫 판 / 판 수 · PB(날짜) · 7일 평균 · 어제까지 범위(그날 베스트) · 다음 등급 · 트레이너 목표"]
    keys = list(dict.fromkeys([k for k, _n in plan_items(dkey, pb)] + [p[0] for p in plays] + list(tset)))
    for k in keys:
        sm = scen_summary(data, k, dkey)
        tb, tf, tc = sm["today_best"], sm["today_first"], sm["today_count"]
        parts = [f"{sname(k):<15} {_cell(tb)} / {_cell(tf)} / {_cell(tc, 2)}"]
        if sm["pb"] is not None: parts.append(f"PB {sm['pb']}" + (f" ({sm['pb_date'][5:]})" if sm["pb_date"] else ""))
        if sm["avg7_best"] is not None: parts.append(f"7일 {sm['avg7_best']:.0f}")
        db = scen_day_band(data, k, dkey)
        if db: parts.append(f"범위 {db['lo']:.0f}–{db['hi']:.0f}")
        if sm["gap"]: parts.append(f"{sm['gap'][0]}까지 +{sm['gap'][2]}" if sm["gap"][0] else "Gold ✓")
        tg = tset.get(k)
        if tg is not None:
            parts.append(f"목표 {tg} " + ("✓" if (tb is not None and tb >= tg) else (f"({tg - tb} 남음)" if tb is not None else "(오늘 안 침)")))
        L.append("  " + " · ".join(parts))
    # ── 서브카테고리 ──
    L += ["", "[서브카테고리 에너지]  PB 기준 / 오늘 베스트 기준"]
    for a, b_ in zip(sub_shape(pb), sub_shape(day.get("best") or {})):
        L.append(f"  {a['cat']} {a['sub']:<10} {_cell(a['e'], 4)} / {_cell(b_['e'], 4)}")
    # ── 프로브 ──
    L += ["", "[프로브 첫 판 · 최근 7일]  날짜 · " + " ".join(sname(k) for k in PROBE) + " · 지수"]
    ps = {p["date"]: p for p in probe_series(data)}
    n_pr = 0
    for i in range(6, -1, -1):
        dk = (d - timedelta(days=i)).isoformat(); e = data["days"].get(dk)
        if not e or not e.get("first"): continue
        vals = " ".join(_cell(e["first"].get(k)) for k in PROBE)
        p = ps.get(dk); idx = []
        if p and p.get("vi") is not None: idx.append(f"발로 {p['vi']:+.1f}")

        L.append(f"  {dk[5:]} {DOWK[date.fromisoformat(dk).weekday()]}  {vals}" + (" · " + " ".join(idx) if idx else "")); n_pr += 1
    if not n_pr: L.append("  (기록 없음)")
    # ── 다음 계획 ──
    L += ["", "[다음 계획]"]
    for i in range(1, 8):
        nd = d + timedelta(days=i); ndk = nd.isoformat(); ndt = day_type_of(ndk)
        if ndt == "v":
            mt = main_theme(ndk, pb)
            what = (f"{DAY_TYPE['v'][0]} · {mt[1]}" + (" (트레이너 지정)" if TRAINER["themes"].get(ndk) else "")
                    + " · " + " ".join(f"{sname(k)}×{n}" for k, n in mt[3]))
        elif ndt == "b": what = f"{DAY_TYPE['b'][0]} 18개"
        else: what = DAY_TYPE["r"][0]
        L.append(f"  {ndk[5:]} {DOWK[nd.weekday()]}  {what}")
    # ── 트레이너 목표 현황 ──
    L += ["", "[트레이너 목표 현황]" + (f"  ({TRAINER['set_on']} 받은 답장)" if TRAINER["set_on"] else "  (아직 받은 목표 없음)")]
    for k, tg in tset.items():
        tb = day.get("best", {}).get(k); b = scen_band(data, k, dkey) or scen_day_band(data, k, dkey)
        st = "✓ 넘음" if (tb is not None and tb >= tg) else (f"✗ {tg - tb} 남음" if tb is not None else "— 오늘 안 침")
        L.append(f"  {sname(k):<15} 목표 {_cell(tg)} · 오늘 {_cell(tb)}  {st} · 다음 제안 {suggest_target(tg, tb, b, pb.get(k))}"
                 + (" (도전)" if TRAINER["challenge"] == k else ""))
    sug = []
    for k in [k for k in keys if k not in tset and (day.get("best") or {}).get(k) is not None][:9]:
        s_ = suggest_target(None, day["best"].get(k), scen_band(data, k, dkey) or scen_day_band(data, k, dkey), pb.get(k))
        if s_: sug.append(f"{sname(k)} {s_}")
    if sug: L.append("  목표 없는 시나리오 제안(기록 기준 ×1.02): " + " · ".join(sug))
    if TRAINER["note"]: L.append(f"  메모: {TRAINER['note']}")
    # ── 트레이너에게 ──
    L += ["", "[트레이너에게]",
          "이 파일을 그대로 보내면 됩니다. 답장 중 아래 형식의 줄만 앱 '트레이너' 카드에 붙여넣으면 바로 적용됩니다 (다른 문장은 무시 — 코칭 글은 얼마든지 길게 써도 됩니다).",
          "  목표 Pasu 870            ← 그 시나리오의 목표 점수 (여러 줄 가능, 같은 이름은 새 값이 이김)",
          "  도전 Pasu 870            ← '오늘의 도전' 칸에 올릴 하나 (목표도 함께 잡힘)",
          "  테마 내일 트래킹         ← 본훈련 테마 지정: 클리킹 · 트래킹 · 스위칭 · 전체 · 약점 (내일 / 오늘 / 모레 / 2026-09-14)",
          "  메모 첫 판 전에 손목 풀기   ← 루틴 카드 맨 위에 그대로 보이는 한 줄",
          "  목표 Pasu 없음           ← 그 목표 지우기",
          "역치 올리는 기준(제안): 넘은 날은 '직전 목표 ×1.02'와 '평소 범위 위끝' 중 큰 쪽, 못 넘은 날은 유지. 한 판 점수는 2~5% 흔들리니 한 번에 3% 넘게 올리지 않기."]
    # ── 데이터 ──
    dat = {"date": dkey, "dt": dt, "theme": theme[0] if theme else None, "plan": plan, "plays": len(plays),
           "pb": {k: pb.get(k) for k in keys}, "today_best": {k: day.get("best", {}).get(k) for k in keys},
           "today_first": {k: day.get("first", {}).get(k) for k in keys}, "count": {k: day.get("count", {}).get(k, 0) for k in keys},
           "band_hi": {k: (lambda b: int(b["hi"]) if b else None)(scen_band(data, k, dkey) or scen_day_band(data, k, dkey)) for k in keys},
           "targets": dict(tset), "challenge": TRAINER["challenge"], "energy_pb": e_pb}
    L += ["", "[데이터]  (앱·트레이너용 숫자 — 읽지 않아도 됩니다)", json.dumps(dat, ensure_ascii=False, separators=(",", ":"))]
    return "\n".join(L) + "\n"

def save_report(data: dict, dkey: str, plays=None, dt: str = None, dir_=None) -> Path:
    """그날 기록을 기록/에임데스크_YYYY-MM-DD.txt 로 (UTF-8 BOM — 메모장·카톡 첨부에서 그대로 읽히게). 임시 파일 뒤 교체"""
    p = report_path(dkey, dir_)
    p.parent.mkdir(parents=True, exist_ok=True)
    txt = daily_report(data, dkey, plays, dt)
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_text(txt, encoding="utf-8-sig"); os.replace(tmp, p)
    return p


SUBS_T = {
 "n": [
  ("dyn","\ud074\ub9ac\ud0b9","Dynamic", [("pasu",[555, 660, 745, 800]),("popcorn",[390, 500, 600, 720])]),
  ("stat","\ud074\ub9ac\ud0b9","Static", [("w4",[820, 915, 1010, 1110]),("ww5",[990, 1090, 1190, 1290])]),
  ("lin","\ud074\ub9ac\ud0b9","Linear", [("frog",[620, 740, 850, 980]),("float",[375, 460, 540, 640])]),
  ("prec","\ud2b8\ub798\ud0b9","Precise", [("pgt",[1900, 2325, 2775, 3050]),("snake",[2400, 2750, 3125, 3425])]),
  ("react","\ud2b8\ub798\ud0b9","Reactive", [("aether",[1525, 1900, 2250, 2650]),("ground",[2100, 2500, 2825, 3100])]),
  ("ctrl","\ud2b8\ub798\ud0b9","Control", [("raw",[2125, 2550, 2975, 3450]),("csphere",[1575, 1950, 2400, 2900])]),
  ("speed","\uc2a4\uc704\uce6d","Speed", [("dot",[845, 940, 1030, 1090]),("eddie",[640, 730, 810, 890])]),
  ("evas","\uc2a4\uc704\uce6d","Evasive", [("drift",[315, 355, 390, 430]),("fly",[420, 460, 500, 535])]),
  ("stab","\uc2a4\uc704\uce6d","Stability", [("cts",[340, 380, 420, 450]),("penta",[290, 340, 390, 445])]),
 ],
 "i": [
  ("dyn","\ud074\ub9ac\ud0b9","Dynamic", [("i.pasu",[770, 850, 930, 980]),("i.popcorn",[600, 690, 780, 860])]),
  ("stat","\ud074\ub9ac\ud0b9","Static", [("i.w4",[1120, 1220, 1300, 1380]),("i.ww5",[1310, 1400, 1490, 1560])]),
  ("lin","\ud074\ub9ac\ud0b9","Linear", [("i.frog",[940, 1040, 1140, 1230]),("i.float",[610, 690, 770, 860])]),
  ("prec","\ud2b8\ub798\ud0b9","Precise", [("i.pgt",[2275, 2675, 3050, 3325]),("i.snake",[2800, 3175, 3500, 3750])]),
  ("react","\ud2b8\ub798\ud0b9","Reactive", [("i.aether",[2175, 2550, 2900, 3175]),("i.ground",[2550, 2850, 3100, 3350])]),
  ("ctrl","\ud2b8\ub798\ud0b9","Control", [("i.raw",[2775, 3200, 3550, 3875]),("i.csphere",[2750, 3175, 3525, 3825])]),
  ("speed","\uc2a4\uc704\uce6d","Speed", [("i.dot",[1110, 1180, 1230, 1280]),("i.eddie",[880, 950, 1020, 1080])]),
  ("evas","\uc2a4\uc704\uce6d","Evasive", [("i.drift",[390, 430, 460, 490]),("i.fly",[520, 570, 610, 650])]),
  ("stab","\uc2a4\uc704\uce6d","Stability", [("i.cts",[420, 460, 485, 520]),("i.penta",[450, 490, 540, 580])]),
 ],
 "a": [
  ("dyn","\ud074\ub9ac\ud0b9","Dynamic", [("a.pasu",[910, 1020, 1110, 1240]),("a.popcorn",[680, 800, 910, 1020])]),
  ("stat","\ud074\ub9ac\ud0b9","Static", [("a.w4",[1320, 1420, 1520, 1620]),("a.ww5",[1510, 1610, 1720, 1860])]),
  ("lin","\ud074\ub9ac\ud0b9","Linear", [("a.frog",[1090, 1220, 1360, 1490]),("a.float",[740, 830, 920, 1050])]),
  ("prec","\ud2b8\ub798\ud0b9","Precise", [("a.pgt",[2750, 3175, 3625, 4050]),("a.snake",[3050, 3425, 3725, 4050])]),
  ("react","\ud2b8\ub798\ud0b9","Reactive", [("a.aether",[2750, 3175, 3525, 3825]),("a.ground",[2875, 3200, 3500, 3725])]),
  ("ctrl","\ud2b8\ub798\ud0b9","Control", [("a.raw",[3150, 3550, 3875, 4250]),("a.csphere",[3100, 3475, 3800, 4125])]),
  ("speed","\uc2a4\uc704\uce6d","Speed", [("a.dot",[1280, 1360, 1420, 1500]),("a.eddie",[1020, 1120, 1200, 1280])]),
  ("evas","\uc2a4\uc704\uce6d","Evasive", [("a.drift",[430, 470, 510, 540]),("a.fly",[540, 600, 660, 720])]),
  ("stab","\uc2a4\uc704\uce6d","Stability", [("a.cts",[450, 490, 520, 550]),("a.penta",[530, 580, 630, 670])]),
 ],
}
SUBS = list(SUBS_T["n"])          # 현재 단계의 표 — set_tier() 가 제자리 갱신. 과거 날은 totalE 가 키로 단계를 알아낸다
# 12개 랭크가 에너지 100~1200 한 줄로 이어진다 (단계 오프셋 0/400/800). 색은 단계 안에서 4개를 돌려 쓴다
RANKS = [(TIERS[t][1] + 100 * (i + 1), n, c)
         for t in reversed(TIER_ORDER) for i, n, c in reversed(list(zip(range(4), TIERS[t][2], ["#98A2AC", "#E08A3C", "#C9D6E2", "#F5C24B"])))]
RANK_E = {n: e for e, n, _c in RANKS}
EPOCH_DATE = "2026-01-01"       # 레벨선 x축의 고정 원점. 차이만 쓰므로 날짜 자체엔 의미가 없다
LVL_CLAMP = 150.0               # 레벨선 항목별 한계(%). 망가진 값(다른 시나리오 점수 등)만 막으면 되므로 넉넉하게 —
                                # 이상치는 중앙값이 막는다. 좁게 잡으면 진짜 성장이 천장에 걸린다

# 선택 검사(--selftest)용 예시 점수 18개 — 제품 동작에는 절대 쓰지 않는다.
# 예전에는 이 값이 새 기록 파일마다 PB 로 주입됐다: 한 판도 치기 전에 에너지 339 Silver 가
# '내 실력'으로 떴고, 성장은 남의 점수 대비로 계산됐다. 게다가 실력이 이 값보다 낮으면
# 레벨선이 ±30% 클램프에 붙어 납작해져서, 매일 늘어도 '성장' 판정이 영원히 안 떴다.
# 이제 출발선은 하드코딩이 아니라 사용자가 '기준 측정일'에 직접 친 점수 — data["base"] 다.
SAMPLE_DATE = "2026-08-29"
SAMPLE = {"pasu":806,"popcorn":660,"w4":1046,"ww5":1260,"frog":930,"float":613,
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

DAY_CUTOFF_H = [5]          # 훈련일이 바뀌는 시각 (기본 새벽 5시). 0 이면 자정 — 옛 동작
# 왜 자정이 아닌가: 밤 11시에 시작해 새벽 1시에 끝난 세션이 자정에서 이틀로 쪼개지면
# 한 루틴이 반씩 나뉘어 진행률·첫 판·세션 길이가 전부 어긋난다. 게다가 자정을 넘기는 순간
# 앱은 다음 날 테마로 갈아타는데 코박스는 켤 때 읽은 어제 플레이리스트를 그대로 들고 있다.

BASELINE = [None]               # {시나리오: 점수} — 기준 측정일에 실제로 친 점수. None 이면 아직 측정 전
BASE_DATE = [None]              # 기준 측정일 (YYYY-MM-DD)
BASE_MIN = 4                    # 레벨선을 그리려면 프로브 6개 중 최소 이만큼은 측정돼 있어야 한다

def base_ok(scores) -> bool:
    """기준선으로 쓸 수 있는가 — 프로브 6개 중 BASE_MIN 개 이상 있어야 한다"""
    return bool(scores) and sum(1 for k in PROBE if scores.get(k)) >= BASE_MIN

def set_baseline(data: dict, dkey: str, scores: dict) -> bool:
    """그날 친 점수를 출발선으로 박는다. 여기서부터 성장을 잰다"""
    sc = {k: int(v) for k, v in (scores or {}).items() if v}
    if not base_ok(sc): return False
    data["base"] = {"date": dkey, "scores": sc}
    BASELINE[0], BASE_DATE[0] = sc, dkey
    bump_ver(); return True

def tier_ready(data: dict):
    """졸업 조건: 현재 단계 벤치 풀런에서 9갈래 전부 최상위 랭크(노비스면 골드) — (충족 여부, 못 채운 갈래 수, 판정한 풀런 날짜)"""
    t = CUR_TIER[0]; top = TIERS[t][1] + 400
    bd = [(dk, e) for dk, e in bench_days(data) if tier_of_scores(data["days"][dk].get("best") or {}) == t]
    if not bd: return (False, 9, None)
    dk = bd[-1][0]; best = data["days"][dk]["best"]
    short = sum(1 for sub in SUBS_T[t] if (subE(sub, best) or 0) < top)
    return (short == 0, short, dk)

def graduate(data: dict) -> str:
    """다음 단계로. 지금 출발선은 base_hist 에 보관하고 비운다 — 다음 훈련일이 새 단계의 기준 측정일이 된다"""
    t = CUR_TIER[0]; i = TIER_ORDER.index(t)
    if i + 1 >= len(TIER_ORDER): return t
    nt = TIER_ORDER[i + 1]
    if data.get("base"): data.setdefault("base_hist", []).append(dict(data["base"], tier=t))
    data.pop("base", None); BASELINE[0] = BASE_DATE[0] = None
    data["tier"] = nt; set_tier(nt); bump_ver()
    return nt

def derive_baseline(data: dict) -> bool:
    """이미 기록이 있는데 기준선만 없는 경우(옛 파일) — 프로브가 가장 먼저 갖춰진 날을 출발선으로 삼는다"""
    for dk in sorted(data.get("days") or {}):
        e = data["days"][dk]
        sc = dict(e.get("best") or {})
        for k, v in (e.get("first") or {}).items(): sc.setdefault(k, v)
        if base_ok(sc): return set_baseline(data, dk, sc)
    return False

def desynth_legacy(data: dict) -> int:
    """옛(v4 이하) 파일에서 주입돼 있던 가짜 출발선을 걷어낸다.
    반드시 가짜 날을 먼저 지우고 PB 를 판정해야 한다 — 순서가 바뀌면 그 날이 '근거' 노릇을 해서
    가짜 PB 가 전부 살아남고 마이그레이션이 통째로 무효가 된다"""
    if not data.pop("seeded", None): return 0
    (data.get("days") or {}).pop(SAMPLE_DATE, None)
    return drop_synthetic_pb(data)

def drop_synthetic_pb(data: dict) -> int:
    """옛 파일 청소: 실제로 친 날이 하나도 없는데 PB 로만 남아 있는 값(=주입된 가짜)을 지운다.
    기록에 근거가 있는 PB 는 절대 건드리지 않는다"""
    real = {}
    for e in (data.get("days") or {}).values():
        for k, v in (e.get("best") or {}).items():
            if v is not None and v > real.get(k, 0): real[k] = v
    n = 0
    for k, v in list((data.get("pb") or {}).items()):
        if real.get(k) is None: data["pb"].pop(k, None); n += 1
        elif v > real[k]: data["pb"][k] = real[k]; n += 1
    return n

def today_date() -> date:
    """오늘 훈련일. 자정이 아니라 DAY_CUTOFF_H 에 날이 바뀐다 — 자정을 넘긴 세션도 한 날로 모이게.
    환경변수 AIMDESK_TODAY=YYYY-MM-DD 가 있으면 그 날 (테스트가 요일·날짜에 좌우되지 않게)"""
    t = os.environ.get("AIMDESK_TODAY")
    if t:
        try: return date.fromisoformat(t)
        except ValueError: pass
    n = datetime.now()
    return (n.date() - timedelta(days=1)) if n.hour < DAY_CUTOFF_H[0] else n.date()

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
    try:                                              # 폴더를 열어 봤을 때 어디로 갔는지 알 수 있게
        (base / "aim_desk_기록위치.txt").write_text(
            "에임 데스크 기록은 이 폴더가 아니라 아래에 저장됩니다.\n(이 폴더에 쓸 수 없거나 임시 폴더에서 실행됐기 때문입니다)\n\n"
            f"{appdir}\n\n앱의 도구 탭에서도 같은 경로를 볼 수 있고, '폴더 열기' 로 바로 열 수 있습니다.\n",
            encoding="utf-8-sig")
    except OSError: pass
    return appdir

DATA_FILE = _data_dir() / "aim_desk_data.json"
BACKUP_FILE = DATA_FILE.with_name("aim_desk_data.backup.json")
LOG_FILE = DATA_FILE.with_name("aim_desk.log")
LOAD_ERROR: list[str] = []      # 시작 시 사용자에게 보여줄 경고
MIGRATED = [0]                  # 훈련일 경계로 합쳐 옮긴 판 수 (시작할 때 알림)
DESYNTH = [0]                   # 옛 파일에서 걷어낸 가짜 PB 개수
BASED = [None]                  # 이번 실행에서 기준선이 처음 정해졌으면 그 날짜 (한 번 알려주려고)
SAVE_ERROR = [None]             # 마지막 저장 실패 사유 (None이면 정상)
DOWK = ["월","화","수","목","금","토","일"]

def data_candidates():
    """기록 파일이 있을 수 있는 자리 전부 (지금 쓰는 곳 포함, 중복 제거)"""
    out = [DATA_FILE.parent]
    try: out.append(_base_dir())
    except Exception: pass
    la = os.environ.get("LOCALAPPDATA")
    if la: out.append(Path(la) / "AimDesk")
    try: home = Path.home()
    except Exception: home = None
    if home is not None:
        out += [home / "AimDesk", home / "Desktop" / "AimDesk", home / "Downloads" / "AimDesk",
                home / "바탕화면" / "AimDesk"]
    seen, uniq = set(), []
    for d in out:
        try: r = d.resolve()
        except (OSError, RuntimeError): continue
        if r not in seen: seen.add(r); uniq.append(r)
    return uniq

def peek_data(fp: Path):
    """기록 파일을 열어보지 않고도 비교할 수 있게 (훈련일 수, 판 수, 마지막 날)"""
    try: d = json.loads(fp.read_bytes().decode("utf-8-sig"))
    except Exception: return None
    days = d.get("days") or {}
    if not isinstance(days, dict): return None
    real = {k: v for k, v in days.items() if isinstance(v, dict) and (v.get("first") or v.get("count"))}
    plays = sum(len(v.get("plays") or []) or sum((v.get("count") or {}).values()) for v in real.values())
    return {"path": fp, "days": len(real), "plays": plays, "last": max(real) if real else None}

def stray_data_files():
    """지금 쓰는 파일 말고 다른 자리에 남아 있는 기록 — 여기 있는 걸 모르면 기록을 잃는다"""
    out = []
    for d in data_candidates():
        fp = d / DATA_FILE.name
        if fp == DATA_FILE or not fp.is_file(): continue
        info = peek_data(fp)
        if info and (info["days"] or info["plays"]): out.append(info)
    return sorted(out, key=lambda i: (-i["plays"], -i["days"]))

def fmt_stray(info: dict) -> str:
    return f"{mask_user_path(str(info['path'].parent))} — 훈련 {info['days']}일 · {info['plays']}판" + \
           (f" · 마지막 {info['last'][5:].replace('-', '/')}" if info["last"] else "")

def merge_data(cur: dict, other: dict) -> dict:
    """다른 자리의 기록을 지금 기록에 합친다 — 판은 합집합(같은 시각은 높은 점수), 집계는 다시 계산,
    PB 는 큰 쪽. 어느 쪽도 잃지 않는다"""
    days = cur.setdefault("days", {})
    for dk, oe in (other.get("days") or {}).items():
        if not isinstance(oe, dict): continue
        ce = days.get(dk)
        if ce is None:
            days[dk] = oe; continue
        ce["plays"] = merge_plays(ce.get("plays") or [], [tuple(x) for x in (oe.get("plays") or [])])
        if ce["plays"]: _reagg(ce)
        else:
            for f in ("first", "best", "count"):
                for k, v in (oe.get(f) or {}).items():
                    cv = (ce.setdefault(f, {})).get(k)
                    ce[f][k] = v if cv is None else (max(cv, v) if f != "first" else cv)
    pb = cur.setdefault("pb", {})
    for k, v in (other.get("pb") or {}).items():
        if v is not None and v > pb.get(k, 0): pb[k] = v
    ob = other.get("base") or {}
    if not (cur.get("base") or {}).get("scores") and ob.get("scores"): cur["base"] = ob
    bump_ver(); return cur

def archive_data() -> Path:
    """지금 기록을 날짜 붙여 보관하고 그 경로를 돌려준다 (지우지 않는다 — 되돌릴 수 있게)"""
    dst = DATA_FILE.with_name(f"aim_desk_data.{datetime.now():%Y%m%d-%H%M%S}.json")
    if DATA_FILE.exists(): dst.write_bytes(DATA_FILE.read_bytes())
    return dst

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
BACKUP_KEEP = 8                 # 날짜별 백업 보관 개수

def _n_days(raw: bytes) -> int:
    try: d = json.loads(raw.decode("utf-8-sig"))
    except Exception: return -1
    days = d.get("days")
    if not isinstance(days, dict): return -1
    return sum(1 for v in days.values() if isinstance(v, dict) and (v.get("first") or v.get("count")))

def keep_backup(raw: bytes):
    """정상본을 날짜별로 보관한다.
    한 칸짜리 백업을 실행마다 덮어쓰면, 파일이 손상됐을 때 '직전 정상본을 복사하세요' 안내가
    가리키는 파일이 이미 손상본으로 덮여 있다. 게다가 기록이 줄어든 파일(다른 폴더에서 새로 생긴
    빈 파일 등)로 멀쩡한 백업을 지워버리면 그걸로 끝이다 — 그래서 '더 빈약하면 안 쓴다'."""
    n = _n_days(raw)
    if n < 0: return                                   # 읽을 수 없는 내용은 백업하지 않는다
    if BACKUP_FILE.exists():
        try:
            if n < _n_days(BACKUP_FILE.read_bytes()): return    # 지금 것이 더 빈약하면 그대로 둔다
        except OSError: pass
    for fp in (BACKUP_FILE, BACKUP_FILE.with_name(f"aim_desk_data.bak-{date.today():%Y%m%d}.json")):
        tmp = fp.with_name(fp.name + ".tmp")
        try:
            tmp.write_bytes(raw); os.replace(tmp, fp)
        except OSError:
            try: tmp.unlink()
            except OSError: pass
    old = sorted(BACKUP_FILE.parent.glob("aim_desk_data.bak-*.json"))
    for fp in old[:-BACKUP_KEEP]:
        try: fp.unlink()
        except OSError: pass

def load_data() -> dict:
    d = {"stats_dir": None, "pb": {}, "days": {}, "seeded": False}
    if DATA_FILE.exists():
        try:
            raw = DATA_FILE.read_bytes()
            d.update(json.loads(raw.decode("utf-8-sig")))
            try: keep_backup(raw)                 # 정상본 보관 (날짜별 · 빈약한 파일로 덮어쓰지 않음)
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
    try: DAY_CUTOFF_H[0] = max(0, min(12, int(d.setdefault("day_cutoff", 5))))
    except (TypeError, ValueError): DAY_CUTOFF_H[0] = 5; d["day_cutoff"] = 5
    MIGRATED[0] = migrate_cutoff(d)                       # 자정에 쪼개졌던 옛 기록 합치기 (한 번만)
    trainer_load(d); load_out_dir(d)
    set_tier(d.setdefault("tier", "n"))                  # 지금 훈련 중인 벤치 단계 (n/i/a)
    d.setdefault("series", {}).setdefault("ep_offset", 0)   # DAY N 시작 오프셋 (새로 시작할 때 이어 셀 수 있게)
    d.setdefault("valo_cfg", {"rid": "", "region": "ap", "key": ""})
    _bc = d.setdefault("bcast", {}); _bc.setdefault("preset", "card"); _bc.setdefault("frameless", False); _bc.setdefault("chroma", False); _bc.setdefault("open", True)
    d.setdefault("theme", "light")                       # v6.3: 기본 밝은 테마 (도구 탭에서 어두움으로)
    # 출발선: 하드코딩이 아니라 사용자가 직접 측정한 점수. 없으면 첫 훈련일이 '기준 측정일'이 된다
    b = d.get("base") or {}
    BASELINE[0] = dict(b.get("scores") or {}) or None
    BASE_DATE[0] = b.get("date")
    if not base_ok(BASELINE[0]):
        BASELINE[0] = BASE_DATE[0] = None; d.pop("base", None)
    DESYNTH[0] = desynth_legacy(d)                        # 옛 파일: 주입돼 있던 가짜 PB 를 걷어낸다
    if BASELINE[0] is None: derive_baseline(d)            # 기록은 있는데 기준선만 없으면 뽑아낸다
    return d

def blank_day() -> dict:
    return {"first": {}, "best": {}, "count": {},
            "plays": [],                                   # [key, 'HH.MM.SS', score] 판별 기록 (시간순)
            "sess": {"start": None, "end": None},          # 오늘 루틴 시나리오의 첫/마지막 판 시각
            "deaths": {"aim":0,"pos":0,"dec":0,"trade":0},
            "cond": {"sleep":None,"feel":5},
            "rank": {"tier": "", "rr": None},                  # 랭크 피드백(선택): 오늘 티어·RR 변화 — 실제 게임에서 어떻게 변하는지 보려고
            "rec": {"start": None, "src": None},               # 녹화 시작 시각 (routine=루틴 실행 · manual=버튼) — 명장면·챕터의 0:00
            "val": {"range": None, "dm_k": None, "dm_d": None, "dm_hs": None, "skip": False},   # 발로란트 블록 15분 — 숫자만 (v6.0)
            "checks": {}}                                       # v4 에서 미야기·랭크 체크 제거 — 옛 파일 호환용 빈 칸

def merge_plays(existing, plays):
    """판별 기록 합치기: (key, 시각) 이 같으면 새 점수가 이긴다. 시간순 정렬된 [key, t, score] 목록"""
    m = {}
    for e in list(existing or []) + [list(x) for x in plays]:
        k, t, sc = e[0], e[1], int(round(e[2]))
        m[(k, t)] = [k, t, sc]
    return [m[kt] for kt in sorted(m, key=lambda kt: (t_key(kt[1]), kt[0]))]

def day_plays(data: dict, dkey: str):
    return [tuple(x) for x in data["days"].get(dkey, {}).get("plays", [])]

def pb_days(data: dict) -> dict:
    """시나리오별로 PB 점수를 처음 낸 날짜"""
    out = {}
    for d in sorted(data["days"]):
        for k, v in data["days"][d]["best"].items():
            if k not in out and v == data["pb"].get(k): out[k] = d
    return out

def _hh(t) -> int:
    try: return int(str(t).split(".")[0])
    except (ValueError, IndexError): return 0

def t_key(t: str) -> int:
    """'HH.MM.SS' → 그 훈련일 안에서의 초. 경계 시각 이전(새벽)은 +24시간으로 쳐서
    자정을 넘긴 세션도 순서·길이가 맞는다 (01:10 이 23:50 보다 뒤로 간다)"""
    p = (str(t).split(".") + ["0", "0", "0"])[:3]
    try: h, m_, s_ = int(p[0]), int(p[1]), int(p[2])
    except ValueError: return 0
    return (h + (24 if h < DAY_CUTOFF_H[0] else 0)) * 3600 + m_ * 60 + s_

def t_min(t: str) -> int:
    """'HH.MM.SS' → 분 (훈련일 기준)"""
    return t_key(t) // 60

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
    """임시 파일에 다 쓰고 디스크까지 내려보낸 뒤 교체 — 쓰는 도중 전원이 나가도 잘린 파일이 남지 않는다.
    fsync 없이 이름만 바꾸면 순서가 뒤집혀 '이름은 새 파일, 내용은 빈 파일' 이 될 수 있다"""
    bump_ver(); SAVE_COUNT[0] += 1
    tmp = DATA_FILE.with_name(DATA_FILE.name + ".tmp")
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=False, indent=1))
            f.flush(); os.fsync(f.fileno())
        os.replace(tmp, DATA_FILE)
        if os.name != "nt":                          # POSIX 는 디렉터리 항목도 내려보내야 확실하다
            try:
                fd = os.open(str(DATA_FILE.parent), os.O_RDONLY)
                try: os.fsync(fd)
                finally: os.close(fd)
            except OSError: pass
        SAVE_ERROR[0] = None
    except Exception as e:
        SAVE_ERROR[0] = f"{type(e).__name__}: {e}"
        log_exc("save_data")
        try: tmp.unlink()                            # 실패한 임시 파일을 남겨두지 않는다
        except OSError: pass

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
    훈련일은 자정이 아니라 DAY_CUTOFF_H 에 바뀌므로 달력 날짜 두 개를 본다 — 당일의 경계 이후 + 다음 날의 경계 이전.
    파일이 생기거나 지워지면 폴더의 mtime이 바뀌므로, 안 바뀌었으면 수만 개 파일을 다시 훑지 않는다.
    force=True(자동 진행 중)면 캐시를 건너뛴다 — 폴더 mtime 이 안 바뀌는 드라이브(exFAT·네트워크)에서도 2초 안에 감지."""
    cut = DAY_CUTOFF_H[0]
    tag = day.strftime("%Y.%m.%d"); tag_n = (day + timedelta(days=1)).strftime("%Y.%m.%d")
    try: sig = (str(stats), stats.stat().st_mtime_ns, tag, cut)
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
                if tag not in name and (cut <= 0 or tag_n not in name): continue   # 정규식 전에 싼 문자열 검사
                m = FNAME_RE.match(name)
                if not m: continue
                d_ = m.group("d")
                if d_ == tag:
                    if _hh(m.group("t")) < cut: continue      # 그 날 경계 이전 = 어제 훈련일 몫
                elif d_ == tag_n and cut > 0:
                    if _hh(m.group("t")) >= cut: continue     # 다음 날 경계 이후 = 내일 훈련일 몫
                else: continue
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

def _reagg(day: dict):
    """판별 기록(plays)에서 그날 집계(first/best/count/sess)를 다시 만든다"""
    ps = sorted((tuple(p) for p in (day.get("plays") or [])), key=lambda x: t_key(x[1]))
    first, best, count = {}, {}, {}
    for k, _t, sc in ps:
        count[k] = count.get(k, 0) + 1
        if k not in first: first[k] = sc
        if k not in best or sc > best[k]: best[k] = sc
    day["first"], day["best"], day["count"] = first, best, count
    day["sess"] = {"start": ps[0][1] if ps else None, "end": ps[-1][1] if ps else None}

def migrate_cutoff(data: dict) -> int:
    """자정에서 이틀로 쪼개졌던 옛 기록을 훈련일(경계 시각) 기준으로 합친다 — 한 번만 돈다.
    판별 기록과 집계가 서로 맞는 날만 건드린다(옛 버전 파일은 그대로 둔다). 옮긴 판 수를 돌려준다."""
    cut = DAY_CUTOFF_H[0]
    if cut <= 0 or data.get("cutoff_migrated"): return 0
    days = data.get("days") or {}
    moved = 0
    for dk in sorted(days):
        if dk == SAMPLE_DATE: continue
        e = days[dk]; ps = [tuple(p) for p in (e.get("plays") or [])]
        if not ps or sum((e.get("count") or {}).values()) != len(ps): continue
        early = [p for p in ps if _hh(p[1]) < cut]
        if not early: continue
        prev = (date.fromisoformat(dk) - timedelta(days=1)).isoformat()
        if prev == SAMPLE_DATE: continue
        tgt = days.get(prev)
        if tgt is not None and sum((tgt.get("count") or {}).values()) != len(tgt.get("plays") or []): continue
        tgt = days.setdefault(prev, blank_day())
        tgt["plays"] = merge_plays(tgt.get("plays") or [], early); _reagg(tgt)
        rest = [p for p in ps if _hh(p[1]) >= cut]
        moved += len(early)
        if rest: e["plays"] = [list(p) for p in rest]; _reagg(e)
        else: days.pop(dk, None)
    if moved:
        for k, v in list(data.get("pb", {}).items()):      # PB 는 줄이지 않는다 — 합치기는 날짜만 옮긴다
            data["pb"][k] = v
        bump_ver()
    data["cutoff_migrated"] = True
    return moved

def apply_scan(data: dict, plays, dkey: str):
    """오늘 판들을 반영. (신기록 이벤트 목록, 변경 여부) 반환.
    기존 기록은 절대 줄이지 않는다 — stats 폴더를 정리했거나 스캔이 비어도 오늘 기록이 남는다."""
    day = data["days"].setdefault(dkey, blank_day())
    first, best, count = {}, {}, {}
    for key, t, s in sorted(plays, key=lambda x: t_key(x[1])):
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
        ts = sorted((t for _, t, _ in plays), key=t_key)
        ns = ts[0] if ns is None or t_key(ts[0]) < t_key(ns) else ns
        ne = ts[-1] if ne is None or t_key(ts[-1]) > t_key(ne) else ne
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
    if merged and not day.get("ep"): day["ep"] = episode_no(data, dkey)   # DAY N 고정 — 올린 편 번호는 안 바뀐다
    if BASE_DATE[0] in (None, dkey) and base_ok(best):    # 기준 측정일 → 출발선 확정(당일엔 계속 갱신)
        if set_baseline(data, dkey, best) and BASED[0] is None: BASED[0] = dkey
    return events, changed

# ══════════════════ 볼테익 에너지 (검증 완료 수식) ══════════════════
def scenE(x, th, off: int = 0):
    """볼테익 공식. off 는 단계 오프셋 — Intermediate 플래티넘 임계값이 정확히 500 이 되게"""
    if x is None: return None
    a,b,c,d = th
    if off: return (lambda e: None if e is None else e + off)(scenE(x, th))
    if x < a: return max(0, int(100*x/a))
    if x < b: return int(100+100*(x-a)/(b-a))
    if x < c: return int(200+100*(x-b)/(c-b))
    if x < d: return int(300+100*(x-c)/(d-c))
    return int(400+100*(x-d)/(d-c))

def E_of(key: str, x):
    """키 하나의 에너지 (단계 오프셋 포함)"""
    th = th_of(key)
    return None if (x is None or th is None) else scenE(x, th, TIERS[tier_of(key)][1])

def subE(sub, scores, off: int = None):
    if off is None: off = TIERS[tier_of(sub[3][0][0])][1]
    es = [scenE(scores.get(k), th, off) for k, th in sub[3]]
    es = [e for e in es if e is not None]
    return max(es) if es else None

def tier_of_scores(scores) -> str:
    """점수 묶음이 어느 단계인가 — 키 다수결 (한 날은 한 단계다). 비어 있으면 현재 단계"""
    if not scores: return CUR_TIER[0]
    cnt = {}
    for k in scores: cnt[tier_of(k)] = cnt.get(tier_of(k), 0) + 1
    return max(cnt, key=cnt.get)

def totalE(scores):
    """벤치 에너지 = 9갈래의 조화평균. 어느 단계의 표를 쓸지는 키로 알아낸다 (과거 날도 맞게)"""
    t = tier_of_scores(scores); off = TIERS[t][1]
    es = [subE(s, scores, off) for s in SUBS_T[t]]
    es = [e for e in es if e is not None]
    if not es: return None, 0
    return int(len(es)/sum(1/max(e,1) for e in es) + 1e-9), len(es)   # 1e-9: 같은 값 9개의 조화평균이 499.999… 로 잘리지 않게

RANK_NAMES = ("Iron", "Bronze", "Silver", "Gold")      # Novice 임계값 인덱스 순 (호환용) — 단계별은 TIERS[t][2]
RANK_IDX = {n: i for t in TIERS for i, n in enumerate(TIERS[t][2])}      # 랭크 이름 → 단계 안 순번(0~3, RANKC 색 인덱스)
RANK_TIER = {n: t for t in TIERS for n in TIERS[t][2]}

def rank_of(e):
    if e is None: return ("—", C["dim"])
    for t, n, _c in RANKS:
        if e >= t: return (n, RANKC[RANK_IDX[n]])
    return ("Unranked", C["dim"])

def sub_of(key):
    """key 가 속한 하위분류 항목 — 어느 단계든 (없으면 None)"""
    for sub in SUBS_T.get(tier_of(key), ()):
        if any(k == key for k, _ in sub[3]): return sub
    return None

def th_of(key):
    sub = sub_of(key)
    if sub is None: return None
    return next(th for k, th in sub[3] if k == key)

def next_rank_gap(score, th, key: str = None):
    """(다음 랭크 이름, 그 임계값, 부족 점수). 단계 최상위 이상이면 (None, th[3], 0). key 가 있으면 그 단계의 랭크 이름"""
    names = TIERS[tier_of(key)][2] if key else RANK_NAMES
    for i, t in enumerate(th):
        if score < t: return (names[i], t, t - score)
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

BENCH_MIN = 14                  # 풀런으로 인정할 최소 시나리오 수 (벤치는 18개)

def bench_days(data: dict):
    """벤치마크 '풀런' 을 한 날들. 9개 하위분류를 다 덮는 것만으로는 부족하다 —
    '전체 순회' 날도 9/9 를 덮어서, 그것까지 세면 평범한 훈련일이 지난 풀런으로 둔갑하고
    에너지를 엉뚱한 날과 비교하게 된다 (항목 수가 같아도 친 시나리오가 다르다)"""
    out = []
    for k in sorted(data["days"]):
        best = data["days"][k]["best"]
        e, n = totalE(best)
        if e is None or n != 9: continue
        if day_type_of(k) != "b" and sum(1 for s_ in tier_keys(tier_of_scores(best)) if best.get(s_) is not None) < BENCH_MIN: continue
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
    elif not stats_ok: r = ("● stats 폴더를 찾을 수 없음 — 도구 탭 → 코박스 stats 폴더 → 폴더 선택", "err")
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
    if src == BASE_DATE[0]: return f"기준 측정 · {int(src[5:7])}/{int(src[8:10])} · {n}/9"
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
    ts = sorted((t for _, t, _ in plays), key=t_key)
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
    return {d for d, e in data["days"].items() if e.get("first") or e.get("count")}

def streak(days: set, today: date, rest_wd=(REST_WD,)):
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

def week_strip(days: set, today: date, rest_wd=(REST_WD,)):
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
    return (f"{rank}까지 {gap}", RANKC[RANK_IDX.get(rank, 3)])

def weakest_link(scores: dict):
    """조화평균을 가장 끌어내리는 서브카테고리와, 다음 100 단위 에너지까지 필요한 점수"""
    t_ = tier_of_scores(scores); off = TIERS[t_][1]
    subs = [(sub, subE(sub, scores, off)) for sub in SUBS_T[t_]]
    subs = [(sub, e) for sub, e in subs if e is not None]
    if not subs: return None
    sub, e = min(subs, key=lambda x: x[1])
    target = (e // 100 + 1) * 100
    needs = []
    for k, th in sub[3]:
        need = math.ceil(score_for_energy(target - off, th)); cur = scores.get(k)
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
WARM_KEYS = set(k for k, _ in WARMUP)           # set_tier() 가 갱신한다

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
    for p in sorted(plays, key=lambda x: t_key(x[1])):
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

def fmt_seq_summary(played, total, n_pb, rel, probe, idx, est_min, block_txt=None, counts=None) -> str:
    """counts 를 주면 '평균 대비 ▼4.8%' 대신 판정 개수를 적는다 — 그 정도 차이는 정상 변동이라
    하락으로 읽히면 안 된다 (줄마다 이미 판정이 붙어 있어 뜻도 겹친다)"""
    parts = []
    if block_txt: parts.append(block_txt)
    parts.append(f"오늘 {played}/{total}판")
    if counts is not None:
        for kk in ("pb", "high", "normal", "low"):
            if counts.get(kk): parts.append(f"{VERDICT_NAME[kk]} {counts[kk]}")
    else:
        if n_pb: parts.append(f"PB {n_pb} 🏆")
        if rel:
            m = sum(rel) / len(rel) * 100; parts.append(f"{'▲' if m >= 0 else '▼'}{abs(m):.1f}%")
    if probe:
        pr = f"프로브 {probe[0]}/{probe[1]}"
        vi, oi = idx
        if vi is not None: pr += f" 발로 {vi:+.1f}"

        parts.append(pr)
    remaining = total - played
    if remaining > 0:
        parts.append(f"남은 {remaining}판" + (f" ≈ {est_min}분" if est_min is not None else ""))
    return " · ".join(parts)

# ── 코치 카드: 어제 지수 · 오늘 초점 · 컨디션 · 프로브 유효성 ──
def last_probe_day(data: dict, before: str):
    for d in sorted(data["days"], reverse=True):
        if d < before and any(data["days"][d]["first"].get(k) is not None for k in PROBE): return d
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
            rank, t, gap = next_rank_gap(x, th, k)
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
    lines = []                                   # v4: '어제 지수' 줄은 판정 밴드가 대신한다
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
DTYPE_SHORT = {"v": "발로", "w": "약점", "b": "벤치", "r": "휴식", "base": "기준"}

def history_rows(data: dict, upto: str, series, pbd: dict, n: int = 14):
    """upto 부터 거꾸로 n 일 (없는 날도 한 줄, trained=False)"""
    end = date.fromisoformat(upto); ser = {p_["date"]: p_ for p_ in series}
    out = []
    for i in range(n):
        d = end - timedelta(days=i); ds = d.isoformat(); e = data["days"].get(ds)
        # 가짜 '기준값 날' 은 없앴다. 기준 측정일은 실제로 친 벤치 날이라 한 줄을 정상적으로 차지한다
        dtype = "base" if ds == BASE_DATE[0] else day_type_of(ds)
        trained = bool(e) and bool(e.get("first") or e.get("count"))
        row = {"date": ds, "dow": DOWK[d.weekday()], "dtype": dtype, "trained": trained,
               "plays": sum(e["count"].values()) if e else 0, "minutes": None, "probe": 0, "vi": None, "oi": None,
               "pbs": [] if dtype == "base" else [k for k, dd in pbd.items() if dd == ds], "deaths": 0, "dom": None, "sleep": None, "feel": None,
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
    if r["vi"] is not None:
        idx = f"{r['vi']:+.1f}"
    return [f"{r['date'][5:7]}-{r['date'][8:10]} {r['dow']}", DTYPE_SHORT[r["dtype"]],
            str(r["plays"]) if r["trained"] else "·", str(r["minutes"]) if (r["trained"] and r["minutes"] is not None) else ("—" if r["trained"] else "·"),
            f"{r['probe']}/{len(PROBE)}" if r["trained"] else "", idx if r["trained"] else "",
            str(len(r["pbs"])) if r["pbs"] else "", (f"{r['deaths']} {r['dom']}" if r["deaths"] else ""),
            f"{r['sleep']:g}" if r["sleep"] is not None else "—", str(r["feel"]) if r["feel"] is not None else "—",
            str(r["energy"]) if r["energy"] is not None else "", ""]

def day_detail(data: dict, dkey: str):
    e = data["days"].get(dkey, {}); out = []
    for sub in SUBS:
        for k, _ in sub[3]:
            b = e.get("best", {}).get(k)
            out.append((k, e.get("first", {}).get(k), b, e.get("count", {}).get(k, 0), b is not None and b == data["pb"].get(k)))
    return out

def growth_since_base(data: dict):
    """기준 측정일 대비 시나리오별 성장. 기준선이 없으면 빈 표 — 아직 잴 게 없다"""
    base = BASELINE[0] or {}
    out = []
    for si, sub in enumerate(SUBS):
        for k, th in sub[3]:
            sd_ = base.get(k)
            if sd_ is None: continue
            pb = data["pb"].get(k, sd_); gain = pb - sd_
            out.append({"key": k, "seed": sd_, "pb": pb, "gain": gain, "pct": gain / sd_ * 100,
                        "band_seed": rank_of(scenE(sd_, th))[0], "band_pb": rank_of(scenE(pb, th))[0],
                        "stalled": gain <= 0, "idx": si})
    return sorted(out, key=lambda r: (r["stalled"], -r["pct"], r["idx"]))

def energy_delta(data: dict):
    return (totalE(BASELINE[0])[0] if BASELINE[0] else None, totalE(data["pb"])[0])

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
        out += [p[2] for p in day_plays(data, dk) if p[0] == key]
    return out

def scen_day_band(data: dict, key: str, end_day: str, field: str = "best", n_days: int = 14):
    """어제까지 '그날 베스트'(또는 그날 첫 판)들의 평소 범위. 줄에 뜨는 값은 하루치 대표값이라
    판 단위 범위(scen_band)로 재면 좁아서 늘 벗어난다."""
    def calc():
        end = date.fromisoformat(end_day); vals = []
        for i in range(1, n_days + 1):
            dk = (end - timedelta(days=i)).isoformat()
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

# ══════════════════ 판정 (v4.0): 오늘은 어제보다? · 전체적으로 성장 중? · 요즘 부진? ══════════════════
# 시청자가 3초 안에 답해야 할 세 질문. 판정은 '면의 색 + 글리프 + 단어 + 숫자 하나'로 나가고,
# 확실하지 않으면 '측정 중 / 판정까지 N일' 로 솔직하게 비워 둔다. 튜닝 상수는 VERDICT 한 곳에.
#   오늘  = 오늘 친 시나리오와 지난 훈련일의 같은 시나리오를 짝지어(프로브는 첫 판, 나머지는 그날 중앙값) 비교 — 평소 범위 폭으로 나눈 z 의 평균 + 다수결
#   성장  = 프로브 첫 판 6개를 '내 기준선' 으로 정규화한 '레벨선' 8주 창에서 Mann–Kendall 추세 + Theil–Sen 기울기
#   요즘  = 같은 레벨선에서 최근 ≤5일 중앙값 − [30일 전, 10일 전] 기준 블록 중앙값 (기준 창과 판정 창이 겹치지 않는다)
VERDICT = {"Z_ON": 0.8, "Z_OFF": 0.65, "DEAD": 0.35, "PAIR_MIN": 4, "PAIR_SOLID": 6,
           "MK_Z": 2.3, "MK_DMIN": 2.0, "MK_N": 10, "MK_SPAN": 21, "MK_WIN": 56,
           "FORM_TH": 3.0, "FORM_REC": 5, "FORM_DOT": 1.5}
VERDICT_GLYPH = {"up": "▲", "flat": "▬", "down": "▼", "hold": "○", "none": "○", "wait": "○", "rest": "○"}

def _median(vals):
    v = sorted(x for x in vals if x is not None); m = len(v)
    if not m: return None
    return v[m // 2] if m % 2 else (v[m // 2 - 1] + v[m // 2]) / 2

def _wa(word: str) -> str:
    """'와/과' 조사: 받침 있으면 과"""
    ch = word[-1]
    return "과" if ("가" <= ch <= "힣" and (ord(ch) - 0xAC00) % 28) else "와"

def _iga(word: str) -> str:
    """'이/가' 조사: 받침 있으면 이"""
    ch = word[-1]
    return "이" if ("가" <= ch <= "힣" and (ord(ch) - 0xAC00) % 28) else "가"

def day_value(data: dict, dkey: str, plays=None) -> dict:
    """그날 시나리오별 대표값: 프로브 = 첫 판, 나머지 = 그날 판들의 중앙값. 웜업은 뺀다(벤치 데이는 전부 단발이라 포함).
    판별 기록이 없는 옛 날은 first(프로브)/best 로 대체"""
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    dt = day_type_of(dkey); e = data["days"].get(dkey) or {}
    by = {}; seen = set()
    for k, _t, sc in plays:
        if k in WARM_KEYS and dt != "b" and k not in seen: seen.add(k); continue   # 웜업 = 그 시나리오의 '첫 판'(손 깨우기)만 뺀다 — 본훈련의 frog/float/raw/ground 블록은 남긴다
        seen.add(k); by.setdefault(k, []).append(sc)
    out = {k: (v[0] if k in PROBE else _median(v)) for k, v in by.items()}
    if not plays:
        for k, v in (e.get("first") or {}).items():
            if k in PROBE and v is not None: out[k] = v
        for k, v in (e.get("best") or {}).items():
            if k not in out and v is not None and (k not in WARM_KEYS or dt == "b"): out[k] = v
    return out

def prev_day_candidates(data: dict, dkey: str, dt: str = None):
    """비교할 지난 훈련일 후보 — 벤치 데이는 지난 벤치 풀런부터, 그 외는 어제부터 7일 안의 훈련일"""
    dt = dt or day_type_of(dkey); out = []
    if dt == "b":
        out += [d for d, _e in bench_days(data) if d < dkey][-3:][::-1]
    td = training_days(data); d = date.fromisoformat(dkey)
    for i in range(1, 8):
        k = (d - timedelta(days=i)).isoformat()
        if k in td and k not in out: out.append(k)
    return out

def pair_scale(data: dict, k: str, dkey: str, v_prev) -> float:
    """짝 비교의 눈금: 그날 대표값의 평소 범위 폭 → 판 단위 범위 → 5% 일간 노이즈 prior(첫 며칠만)"""
    b = scen_day_band(data, k, dkey, "first" if k in PROBE else "best", 14) or scen_band(data, k, dkey)
    if b and b.get("sd"): return b["sd"]
    return max(1.0, 0.05 * abs(v_prev or 1.0))

def verdict_state(Z, up_ok: bool, dn_ok: bool, prev=None, on=None, off=None) -> str:
    """히스테리시스: 올라갈 땐 Z≥on, 이미 그 상태면 Z≥off 까지 유지 — 판 하나 들어올 때마다 경계에서 깜빡이지 않게"""
    on = VERDICT["Z_ON"] if on is None else on; off = VERDICT["Z_OFF"] if off is None else off
    if up_ok and (Z >= on or (prev == "up" and Z >= off)): return "up"
    if dn_ok and (Z <= -on or (prev == "down" and Z <= -off)): return "down"
    return "flat"

def _V(state, conf, word, glyph, num, cap="", cap2="", colk="dim", fill="none", ev=None, n=0, **kw):
    d = {"state": state, "conf": conf, "word": word, "glyph": glyph, "num": num, "cap": cap, "cap2": cap2,
         "colk": colk, "fill": fill, "ev": ev, "n": n}
    d.update(kw); return d

def verdict_day(data: dict, dkey: str, plays=None, dt: str = None, prev_state=None) -> dict:
    """【오늘】 — 지난 훈련일의 같은 시나리오와 짝지어 비교. 같은 유형의 날이면 '루틴의 같은 지점'까지만(세션 중 상승이 아침 판정을 기울이지 않게)"""
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    dt = dt or day_type_of(dkey); d = date.fromisoformat(dkey); day = data["days"].get(dkey) or {}
    if dt == "r" and not plays:                       # 실제로 친 날이면 아래 정상 판정으로 내려간다
        wk = [k for k in recap_week(dkey) if k < dkey and k in training_days(data)]
        return _V("rest", "solid", "휴식일", "○", f"{recap_label(dkey)} {len(wk)}일", cap=f"오늘 · {d.month}/{d.day} {DOWK[d.weekday()]}",
                  cap2="손목도 데이터의 일부 — 내일 다시", colk="flat", fill="solid")
    n_pb = sum(1 for _k, _s, kind in day_verdicts(data, dkey, plays) if kind == "pb")
    t = day_value(data, dkey, plays)
    if dt == "b":
        br = bench_readiness(data, dkey); proj = br["projected"]; n_t = br["n_today"]
        _bd = [(d_, e_) for d_, e_ in bench_days(data) if d_ < dkey]      # bench_days 는 9/9 풀런만 준다
        last, e_last = (_bd[-1] if _bd else (None, None))
        if n_t == 0 or proj is None:
            bl = bench_label(dkey)
            return _V("wait", "wait", f"{bl} 시작 전", "○", "0/18", cap=f"오늘 · {d.month}/{d.day} {DOWK[d.weekday()]} · {bl}",
                      cap2=("18개를 한 판씩 — 여기서 나온 점수가 내 출발선이 됩니다" if bl == "기준 측정" else "18개 다 치면 에너지가 확정됩니다"),
                      colk="dim", n_pb=n_pb)
        rn = rank_of(proj)[0]; nxt = next((n_ for th_, n_, _c in sorted(RANKS) if proj < th_), None)
        need = (next(th_ for th_, n_, _c in sorted(RANKS) if n_ == nxt) - proj) if nxt else 0
        done = n_t >= 18
        word = (f"확정 {proj} {rn}" if done else f"예상 {rn}") + (f" · {nxt}까지 {need}" if nxt and not done else "")
        cap2 = (f"PB 에너지 {br['e_pb']} · " if br["e_pb"] is not None and bench_label(dkey) != "기준 측정" else "") + f"{n_t}/18판" \
               + (f" · 지난 벤치 {last[5:].replace('-', '/')}" if last else (" · 출발선을 만드는 중" if bench_label(dkey) == "기준 측정" else " · 첫 벤치"))
        state = "flat"
        if last and e_last is not None and done:       # 풀런끼리만 비교한다
            state = "up" if proj > e_last + 5 else ("down" if proj < e_last - 5 else "flat"); cap2 += f" ({e_last} → {proj})"
        return _V(state if done else "bench", "solid" if done else "prov", word, VERDICT_GLYPH.get(state, "○") if done else "○", str(proj),
                  cap=f"오늘 · {d.month}/{d.day} {DOWK[d.weekday()]} · {bench_label(dkey)}", cap2=cap2, colk="rank", fill="solid" if done else "hollow", rank=rn, n=n_t, n_pb=n_pb)
    if len(t) < VERDICT["PAIR_MIN"]:
        return _V("wait", "wait", "워밍업 중" if (plays and not t) else "측정 중", "○", f"{len(t)}/{VERDICT['PAIR_MIN']}쌍",
                  cap=f"오늘 · {d.month}/{d.day} {DOWK[d.weekday()]}", cap2=f"오늘 {len(plays)}판 — 프로브가 끝나면 판정이 섭니다", colk="dim", n=len(t), n_pb=n_pb)
    best = None
    for prev in prev_day_candidates(data, dkey, dt):
        pp = day_plays(data, prev)
        if day_type_of(prev) == dt and len(pp) > len(plays):     # 같은 지점 = 웜업 뺀 판 수 (프로브만 치거나 웜업을 더 쳐도 어제와 짝이 맞게)
            n_t = sum(1 for k_, _t_, _s_ in plays if k_ not in WARM_KEYS or dt == "b"); i_ = n_ = 0
            while i_ < len(pp) and n_ < n_t: n_ += (pp[i_][0] not in WARM_KEYS or dt == "b"); i_ += 1
            pp = pp[:i_]
        p = day_value(data, prev, pp); K = sorted(set(t) & set(p))
        if len(K) >= VERDICT["PAIR_MIN"]: best = (prev, p, K, pp); break
    # 평소(어제까지 범위) 대비 — 캡션과 폴백에 쓴다
    u = {}
    for k, v in t.items():
        b = scen_band(data, k, dkey) or scen_day_band(data, k, dkey, "first" if k in PROBE else "best")
        if b and b.get("sd"): u[k] = (max(-3.0, min(3.0, (v - b["mid"]) / b["sd"])), (v / b["mid"] - 1) * 100 if b["mid"] else 0.0)
    Zu = (sum(z for z, _p in u.values()) / len(u)) if u else None
    pct_u = _median([p_ for _z, p_ in u.values()]) if u else None
    cap1 = f"오늘 · {d.month}/{d.day} {DOWK[d.weekday()]}"
    cap2 = f"오늘 {len(plays)}판" + (f" · 평소보다 {pct_u:+.1f}%" if pct_u is not None else "")
    if best is None:
        if not any(k < dkey for k in training_days(data)):                    # 진짜 첫 훈련일 (7일 넘게 쉰 건 첫날이 아니다 → 아래 평소 기준)
            return _V("none", "solid", "오늘이 기준선", "○", f"{len(plays)}판", cap=cap1 + " · 첫 훈련일", cap2="내일부터 어제와 비교합니다", colk="gold", fill="hollow", n=len(t), n_pb=n_pb)
        if not u:
            return _V("wait", "wait", "측정 중", "○", f"{len(t)}/{VERDICT['PAIR_MIN']}쌍", cap=cap1 + " · 비교할 어제 없음", cap2=cap2, colk="dim", n=len(t), n_pb=n_pb)
        n = len(u); zs = [z for z, _p in u.values()]
        n_up = sum(1 for z in zs if z > VERDICT["DEAD"]); n_dn = sum(1 for z in zs if z < -VERDICT["DEAD"])
        state = verdict_state(Zu, n_up >= math.ceil(n / 2) and n_dn <= n // 4, n_dn >= math.ceil(n / 2) and n_up <= n // 4, prev_state)
        conf = "solid" if n >= VERDICT["PAIR_SOLID"] else "prov"
        word = {"up": "평소보다 좋음", "down": "평소보다 별로", "flat": "평소와 비슷"}[state]
        return _V(state, conf, word, VERDICT_GLYPH[state], f"{pct_u:+.1f}%", cap=cap1 + " · 비교할 어제 없음 · 평소 기준", cap2=cap2,
                  colk=state, fill="solid" if conf == "solid" else "hollow", n=n, n_pb=n_pb, pct=pct_u, zu=Zu)
    prev, p, K, pp = best
    n = len(K); zs = []; pcts = []
    for k in K:
        sd = pair_scale(data, k, dkey, p[k])
        zs.append(max(-3.0, min(3.0, (t[k] - p[k]) / (math.sqrt(2) * sd))))
        if p[k]: pcts.append((t[k] / p[k] - 1) * 100)
    Z = sum(zs) / n; n_up = sum(1 for z in zs if z > VERDICT["DEAD"]); n_dn = sum(1 for z in zs if z < -VERDICT["DEAD"])
    up_ok = n_up >= math.ceil(n / 2) and n_dn <= n // 4; dn_ok = n_dn >= math.ceil(n / 2) and n_up <= n // 4
    state = verdict_state(Z, up_ok, dn_ok, prev_state)
    conf = "solid" if n >= VERDICT["PAIR_SOLID"] else "prov"
    pd = date.fromisoformat(prev)
    prevlbl = "어제" if (d - pd).days == 1 else ("지난 " if (d - pd).days >= 7 else "") + f"{DOWK[pd.weekday()]}요일"
    btag = "(벤치)" if (day_type_of(prev) == "b" and dt != "b") else ""
    word = {"up": f"{prevlbl}보다 좋음", "down": f"{prevlbl}보다 별로", "flat": f"{prevlbl}{_wa(prevlbl)} 비슷"}[state]
    pct = _median(pcts) if pcts else 0.0
    sub = ""
    if state == "up" and Zu is not None and Zu < 0.3: sub = f" · {prevlbl}{_iga(prevlbl)} 낮았던 날 — 오늘은 평소 수준"
    elif state == "down" and Zu is not None and Zu > -0.3: sub = f" · {prevlbl}{_iga(prevlbl)} 유난히 좋았던 날 — 오늘은 평소 수준"
    ca = cond_adjust(day.get("cond") or {}) if isinstance(day, dict) else None
    cap = cap1 + f" · {prevlbl}{btag}보다 · {n}쌍" + (f" · 잠정 {n}/{VERDICT['PAIR_SOLID']}쌍" if conf == "prov" else "")
    n_pp = len(pp) or sum((data["days"].get(prev) or {}).get("count", {}).values())   # 판별 기록 없는 옛 날은 count 합
    cap2 += f" · {prevlbl}{btag} {n_pp}판" + sub + (" · 컨디션 참작" if ca else "")
    return _V(state, conf, word, VERDICT_GLYPH[state], f"{pct:+.1f}%", cap=cap, cap2=cap2, colk=state,
              fill="solid" if conf == "solid" else "hollow", n=n, n_pb=n_pb, pct=pct, zu=Zu, prev=prev, z=Z)

def probe_level_series(data: dict):
    """레벨선: 날마다 프로브 첫 판 6개를 '내 기준선' 대비 (first/base − 1)·100 평균 (항목별 ±30 클램프, ≥4개 필요).
    눈금이 내 출발선이라 첫날이 정확히 0 이고 위아래로 고르게 움직인다.
    하드코딩 눈금을 쓰면 실력이 그보다 낮을 때 값이 전부 −30 클램프에 붙어 레벨선이 납작해지고,
    매일 늘어도 성장 판정이 영영 안 뜬다 (35% 아래면 156칸 중 129칸이 클램프에 걸렸다).
    기준선의 개별 오차는 날마다 같은 값으로 나누므로 추세·차이 계산에서 상쇄된다.
    이상치는 좁은 클램프가 아니라 '6개의 중앙값' 으로 막는다 — 좁은 클램프(±30)는 이상치도 막지만
    진짜 성장까지 같이 잘라서(초보는 3주면 천장) 성장 판정이 다시 납작해진다. 중앙값은 튀는 값
    한둘을 무시하면서 성장 폭은 그대로 둔다 (같은 조건에서 이상치 흡수 6.9 · 추세 Z 9.54 로 둘 다 최고)"""
    def calc():
        base = BASELINE[0]
        if not base: return []                          # 기준 측정 전 — 그릴 선이 없다
        out = []; d0 = date.fromisoformat(EPOCH_DATE)
        for dk in sorted(data["days"]):
            fr = data["days"][dk].get("first") or {}
            vals = [max(-LVL_CLAMP, min(LVL_CLAMP, (fr[k] / base[k] - 1) * 100)) for k in PROBE if fr.get(k) is not None and base.get(k)]
            if len(vals) < BASE_MIN: continue
            out.append({"date": dk, "cal": (date.fromisoformat(dk) - d0).days, "lvl": _median(vals), "n": len(vals)})
        return out
    return memo(("plvl",), calc)

def mann_kendall(pts):
    """(Z, S) — pts = [(x, y)] 시간순. 단조 추세 검정 (분포 가정 없음)"""
    n = len(pts)
    if n < 3: return (0.0, 0)
    S = 0
    for i in range(n):
        for j in range(i + 1, n):
            dy = pts[j][1] - pts[i][1]; S += (dy > 0) - (dy < 0)
    var = n * (n - 1) * (2 * n + 5) / 18.0
    return ((S - (1 if S > 0 else -1 if S < 0 else 0)) / math.sqrt(var), S)

def theil_sen(pts):
    """쌍별 기울기의 중앙값 (y 단위 / x 단위)"""
    sl = [(pts[j][1] - pts[i][1]) / (pts[j][0] - pts[i][0]) for i in range(len(pts)) for j in range(i + 1, len(pts)) if pts[j][0] != pts[i][0]]
    return _median(sl) if sl else 0.0

def _energy_line(data: dict) -> str:
    e0, e1 = energy_delta(data); r0, r1 = rank_of(e0)[0], rank_of(e1)[0]
    if e1 is None: return "기준 측정 전"
    if e0 is None: return f"에너지 {e1} {r1}"
    return f"에너지 {e0} → {e1} · {r0} → {r1}" if (e0 != e1 or r0 != r1) else f"에너지 {e1} {r1}"

def _future_days(cal_d: int, dkey: str, ahead: int):
    """오늘 이후 ahead 일 안의 훈련일들의 cal 좌표 (일요일 휴식은 뺀다)"""
    d0 = date.fromisoformat(dkey)
    return [cal_d + j for j in range(1, ahead + 1) if DAYTYPES[(d0 + timedelta(days=j)).weekday()] != "r"]

def eta_days(have, cal_d: int, dkey: str, ok, horizon: int = 120) -> int:
    """지금부터 훈련일마다 친다고 할 때 ok(관측일들, 그날) 이 참이 되는 첫 '훈련일' 까지 며칠. 못 찾으면 -1.
    쉬는 날에 조건이 차더라도 그날을 답으로 주지 않는다 — 실제로 보게 되는 건 다음 훈련일이다"""
    have = sorted(set(have)); d0 = date.fromisoformat(dkey)
    for ahead in range(0, horizon + 1):
        if ahead and DAYTYPES[(d0 + timedelta(days=ahead)).weekday()] == "r": continue
        if ok(sorted(set(have + _future_days(cal_d, dkey, ahead))), cal_d + ahead): return ahead
    return -1

def _eta_txt(n: int) -> str:
    return "판정까지 " + ("오늘" if n == 0 else f"{n}일" if n > 0 else "더 필요")

def _grow_ok(pts, cd):
    w = [c for c in pts if c > cd - VERDICT["MK_WIN"]]
    return len(w) >= VERDICT["MK_N"] and (w[-1] - w[0]) >= VERDICT["MK_SPAN"]

def _recent_ok(pts, cd):
    rec = [c for c in pts if c >= cd - 7][-VERDICT["FORM_REC"]:]
    base = [c for c in pts if cd - 30 <= c <= cd - 10]
    if len(base) < 4: base = [c for c in pts if cd - 21 <= c <= cd - 8]
    return len(rec) >= 3 and len(base) >= 4

HYST = {"MK": 0.3, "FORM": 0.5}     # 경계 완충 — 이 폭 안에서는 어제 상태를 유지한다

def _sticky(new: str, prev, strong: bool) -> str:
    """이전 상태가 있고 지금 신호가 경계 완충 안(약함)이면 이전 상태를 지킨다"""
    return prev if (prev in ("up", "flat", "down") and not strong and new != prev) else new

def verdict_growth(data: dict, dkey: str, prev=None, npr: int = None) -> dict:
    """【성장】 — 레벨선 8주 창의 Mann–Kendall 추세. 숫자는 Theil–Sen 기울기 × 창 길이 (%).
    prev 가 있으면 히스테리시스(경계 ±0.3), 오늘 점은 프로브가 다 들어왔을 때만"""
    ser = probe_level_series(data); cal_d = (date.fromisoformat(dkey) - date.fromisoformat(EPOCH_DATE)).days
    full_today = npr is None or npr >= len(PROBE)
    pts = [(p["cal"], p["lvl"]) for p in ser if (p["date"] < dkey or (p["date"] == dkey and full_today)) and p["cal"] > cal_d - VERDICT["MK_WIN"]]
    n = len(pts); span = (pts[-1][0] - pts[0][0]) if n >= 2 else 0
    cap2 = _energy_line(data)
    if n < VERDICT["MK_N"] or span < VERDICT["MK_SPAN"]:
        if not BASELINE[0]:
            return _V("hold", "wait", "기준 측정 전", "○", "0/18", cap="18개를 한 판씩 치면 여기부터 잽니다", cap2=cap2,
                      colk="dim", ev={"pts": pts}, n=0)
        eta = eta_days([p["cal"] for p in ser if p["cal"] <= cal_d], cal_d, dkey, _grow_ok)
        return _V("hold", "wait", _eta_txt(eta), "○", f"{n}/{VERDICT['MK_N']}일",
                  cap="프로브 10일 이상 · 3주 이상 쌓이면 판정", cap2=cap2, colk="dim", ev={"pts": pts}, n=n)
    Z, S = mann_kendall(pts); slope = theil_sen(pts); delta = slope * span
    if Z >= VERDICT["MK_Z"] and delta >= VERDICT["MK_DMIN"]: state = "up"
    elif Z <= -VERDICT["MK_Z"] and delta <= -VERDICT["MK_DMIN"]: state = "down"
    else: state = "flat"
    strong = abs(abs(Z) - VERDICT["MK_Z"]) >= HYST["MK"]            # 경계에서 충분히 떨어져야 상태를 바꾼다
    state = _sticky(state, prev, strong)
    word, gl = {"up": ("꾸준히 오르는 중", "↗"), "down": ("최근 내려가는 중", "↘"), "flat": ("큰 변화 없음", "→")}[state]
    ev = {"pts": pts, "slope": slope, "mid": (_median([x for x, _y in pts]), _median([y for _x, y in pts])), "Z": Z}
    return _V(state, "solid", word, gl, f"{delta:+.1f}%", cap=f"{max(1, round(span / 7))}주 프로브 추세", cap2=cap2, colk=state, fill="solid", ev=ev, n=n, z=Z)

def verdict_recent(data: dict, dkey: str, prev=None, npr: int = None) -> dict:
    """【요즘】 — 최근 ≤5 훈련일 레벨 중앙값 − [30일 전, 10일 전] 기준 블록 중앙값. 75% 다수결.
    prev 가 있으면 히스테리시스(경계 ±0.5%), 오늘 점은 프로브가 다 들어왔을 때만"""
    ser = probe_level_series(data); cal_d = (date.fromisoformat(dkey) - date.fromisoformat(EPOCH_DATE)).days
    full_today = npr is None or npr >= len(PROBE)
    rec = [p for p in ser if (p["date"] < dkey or (p["date"] == dkey and full_today)) and p["cal"] >= cal_d - 7][-VERDICT["FORM_REC"]:]
    base = [p for p in ser if cal_d - 30 <= p["cal"] <= cal_d - 10]; short = False
    if len(base) < 4: base = [p for p in ser if cal_d - 21 <= p["cal"] <= cal_d - 8]; short = True
    m, nb = len(rec), len(base)
    if m < 3 or nb < 4:
        if not BASELINE[0]:
            return _V("hold", "wait", "기준 측정 전", "○", "0/18", cap="18개를 한 판씩 치면 여기부터 잽니다",
                      cap2="첫 판 기준", colk="dim", ev={"dots": []}, n=0)
        eta = eta_days([p["cal"] for p in ser if p["cal"] <= cal_d], cal_d, dkey, _recent_ok)
        return _V("hold", "wait", _eta_txt(eta), "○", (f"최근 {m}/3일" if m < 3 else f"기준 {nb}/4일"),
                  cap="최근 5일 vs 3주 전", cap2="첫 판 기준", colk="dim", ev={"dots": [(p["date"], None) for p in rec]}, n=m)
    b = _median([p["lvl"] for p in base]); R = _median([p["lvl"] for p in rec]) - b
    n_neg = sum(1 for p in rec if p["lvl"] < b); n_pos = sum(1 for p in rec if p["lvl"] > b)
    if R <= -VERDICT["FORM_TH"] and n_neg >= math.ceil(0.75 * m): state = "down"
    elif R >= VERDICT["FORM_TH"] and n_pos >= math.ceil(0.75 * m): state = "up"
    else: state = "flat"
    state = _sticky(state, prev, abs(abs(R) - VERDICT["FORM_TH"]) >= HYST["FORM"])
    word = {"down": "요즘 부진", "up": "요즘 상승세", "flat": "요즘 평소 흐름"}[state]
    dots = [(p["date"], p["lvl"] - b) for p in rec]
    cap = f"최근 {m}일 vs 3주 전 · {m}일 중 {n_neg}일 아래" + (" · 기준 짧음" if short else "")
    sl = (data["days"].get(dkey) or {}).get("cond", {}).get("sleep")
    cap2 = f"수면 {float(sl):g}h" if isinstance(sl, (int, float)) and sl < 6 else "첫 판 기준"
    return _V(state, "solid", word, VERDICT_GLYPH[state], f"{R:+.1f}%", cap=cap, cap2=cap2, colk=state, fill="solid", ev={"dots": dots, "base": b}, n=m)

def verdicts(data: dict, dkey: str, dt: str = None, plays=None, prev_state=None) -> dict:
    """세 판정을 한 번에 — 오늘 탭·방송 화면·오늘 한 장·기록 파일이 전부 이것만 읽는다 (UI 는 통계를 다시 계산하지 않는다)"""
    dt = dt or day_type_of(dkey)
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    if prev_state is None and (data.get("hero") or {}).get("date") == dkey: prev_state = data["hero"].get("state")   # 카드·기록 파일도 밴드와 같은 히스테리시스 상태로
    npr = sum(1 for k in PROBE if (data["days"].get(dkey) or {}).get("first", {}).get(k) is not None)
    h = data.get("hero") or {}; pg, pr = h.get("grow"), h.get("recent")     # 어제까지의 성장·요즘 상태 (히스테리시스)
    return memo(("verdicts", dkey, dt, len(plays), prev_state, npr, pg, pr),
                lambda: {"day": verdict_day(data, dkey, plays, dt, prev_state), "grow": verdict_growth(data, dkey, pg, npr), "recent": verdict_recent(data, dkey, pr, npr)})

def fmt_verdict_line(name: str, V: dict) -> str:
    return f"{name} · {V['word']} {V['glyph']} {V['num']}" + (f" · {V['cap']}" if V.get("cap") else "")


# ── 훈련 레벨: 실력이 제자리인 날에도 '한 일'은 남는다는 걸 보이게 하는 값 ──
#    점수가 아니라 '친 판 수 + 신기록'에서만 오른다. 앱을 켜 두는 것만으로는 1점도 오르지 않는다.
LEVELS = [(0, "입문"), (30, "수련"), (80, "훈련병"), (160, "정조준"), (280, "견습 사수"), (440, "숙련 사수"),
          (660, "정예 사수"), (950, "저격수"), (1320, "명사수"), (1800, "달인"), (2400, "장인")]

def total_pbs(data: dict) -> int:
    """누적 신기록 횟수. 기준 측정일에 처음 찍은 점수는 출발선이라 신기록으로 세지 않는다"""
    best = dict(data["days"].get(BASE_DATE[0], {}).get("best", {})); n = 0
    for d in sorted(data["days"]):
        if d == BASE_DATE[0]: continue
        for k, v in sorted(data["days"][d].get("best", {}).items()):
            if v is not None and v > best.get(k, 0): n += 1; best[k] = v
    return n

def total_xp(data: dict) -> int:
    """친 판 1점 + 신기록 5점"""
    plays = sum(len(e.get("plays") or []) for e in data["days"].values())
    if not plays:                                    # 옛 파일엔 판별 기록이 없다 — 그날 판 수 합으로
        plays = sum(sum((e.get("count") or {}).values()) for e in data["days"].values())
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
    """그 시나리오의 '평소 값' 기준선. 판 단위 평소 범위 → 어제까지 베스트 평균 → 내 기준 측정값 순으로 물러난다.
    1일차에도 반드시 하나는 나오게 (그래야 첫날부터 그릴 게 생긴다)"""
    b = scen_band(data, key, dkey)
    if b: return b["mid"]
    avg, _ = recent_stats(data, key, dkey, "best")
    if avg: return avg
    return (BASELINE[0] or {}).get(key)

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

def baseline_changes(data: dict) -> list:
    """출발선을 만든 날의 요약 세 줄 — 총 에너지 · 갈래별 · 가장 약한 갈래와 첫 목표"""
    pb = data.get("pb") or {}; e, n = totalE(pb)
    if e is None: return []
    t = CUR_TIER[0]; off = TIERS[t][1]; top = off + 400
    cats = {}
    for sub in SUBS_T[t]:
        se = subE(sub, pb, off)
        if se is not None: cats.setdefault(sub[1], []).append(se)
    cat_txt = " · ".join(f"{c} {sum(v) // len(v)}" for c, v in cats.items())
    n_top = sum(1 for sub in SUBS_T[t] if (subE(sub, pb, off) or 0) >= top)
    out = [f"출발선 확정 · 총 에너지 {e} {rank_of(e)[0]} ({n}/9)", f"{cat_txt} — {TIERS[t][2][3]} 위 {n_top}갈래"]
    w = weakest_link(pb)
    if w and w.get("needs"):
        k, need, _gap = min(w["needs"], key=lambda x: x[2])
        out.append(f"가장 약한 갈래 {w['cat']} {w['name']} {w['e']} — 첫 목표 {sname(k)} {need}")
    return out

def day_changes(data: dict, dkey: str, max_n: int = 6):
    if dkey == BASE_DATE[0]: return baseline_changes(data)[:max_n]
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
            if r_new > r_old: line += f" · {TIERS[tier_of(k)][2][r_new - 1]} 칸 진입"
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
    V = verdicts(data, dkey, None, plays)["day"]
    gw, gn, _gc = fmt_gate(gate_status(data.get("pb") or {}))
    return {"title": head, "kinds": kinds, "stat": " · ".join(stat), "verdict": (f"{V['word']} {V['glyph']}", V["num"], V["colk"]),
            "changed": day_changes(data, dkey), "gain": (f"세션 중 {g:+.1f}% (앞 절반 → 뒤 절반)" if g is not None else ""),
            "next": theme_line(dkey, data.get("pb")).split(" · ")[-1] if theme_line(dkey, data.get("pb")) else "",
            "story": story_line(data, dkey), "stars": [m for _c, m in milestones(data, dkey, plays)][:3],
            "gate": f"{gw} · {gn}" if BASE_DATE[0] else ""}

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
    if ctrl and keysym.lower() == "b": return "cast"
    if ctrl and keysym.lower() == "o": return "folder"
    if ctrl and keysym.lower() == "r": return "run"
    if in_entry: return None
    return {"1": "tab:today", "2": "tab:grow", "3": "tab:bench", "4": "tab:log", "5": "tab:tools", "6": "tab:cal"}.get(keysym)

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
# ══════════════════ 발로란트 전적 (v6.0 · 선택) ══════════════════
# HenrikDev 커뮤니티 API. 키는 사용자가 https://api.henrikdev.xyz/dashboard/ 에서 직접 받는다.
# 이게 없어도 앱은 전부 돌고, 있으면 티어·RR·최근 경쟁전 ACS/HS%/승률이 자동으로 들어온다 —
# '에임은 올랐는데 랭크가 안 오르는' 구간을 숫자로 보이게 하는 재료.
import urllib.request, urllib.parse, urllib.error

VAL_API = "https://api.henrikdev.xyz"
VAL_REGIONS = ("ap", "kr", "na", "eu", "latam", "br")

def riot_id(s: str):
    """'YouKnowJo#YK1' → ('YouKnowJo', 'YK1'). 모양이 아니면 None"""
    s = (s or "").strip()
    if "#" not in s: return None
    name, tag = s.rsplit("#", 1)
    return (name.strip(), tag.strip()) if name.strip() and tag.strip() else None

def val_get(path: str, key: str, timeout: float = 8.0, header: str = "Authorization"):
    """GET → (json | None, 오류 문구 | None). 키·네트워크·형식 오류를 전부 문구로 돌려준다"""
    if not key: return None, "API 키 없음"
    req = urllib.request.Request(VAL_API + path, headers={header: key, "User-Agent": "AimDesk"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: return json.loads(r.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        try: msg = (json.loads(e.read().decode("utf-8")).get("errors") or [{}])[0].get("message") or ""
        except Exception: msg = ""
        return None, {401: "API 키가 틀렸습니다", 403: "API 키 권한 없음", 404: "계정을 찾을 수 없습니다 (이름#태그·지역 확인)", 429: "요청이 너무 잦습니다 — 잠시 뒤"}.get(e.code, f"HTTP {e.code} {msg}".strip())
    except (urllib.error.URLError, TimeoutError, OSError) as e: return None, f"연결 실패 — {getattr(e, 'reason', e)}"
    except ValueError: return None, "응답 형식 오류"

def parse_mmr(j: dict):
    """v3 MMR → {'tier','rr','elo','last','peak'} (문서 경로: data.current.tier.name · data.current.rr · data.current.elo · data.current.last_change · data.peak.tier.name)"""
    try:
        cur = j["data"]["current"]; pk = (j["data"].get("peak") or {})
        return {"tier": cur["tier"]["name"], "rr": int(cur.get("rr") or 0), "elo": cur.get("elo"), "last": cur.get("last_change"),
                "peak": (pk.get("tier") or {}).get("name")}
    except (KeyError, TypeError, ValueError): return None

def parse_matches(j: dict):
    """v1 stored-matches → [{'id','date','map','mode','k','d','a','acs','hs','won'}] 최신순.
    hs = 머리/(머리+몸+다리) %. won = 내 팀 점수 > 상대 점수"""
    out = []
    for m in (j or {}).get("data") or []:
        try:
            meta, st, tm = m.get("meta") or {}, m.get("stats") or {}, m.get("teams") or {}
            if not st: continue
            sh = st.get("shots") or {}; h, b, l = int(sh.get("head") or 0), int(sh.get("body") or 0), int(sh.get("leg") or 0)
            mine = (st.get("team") or "").lower(); mine_s, other_s = tm.get(mine), tm.get("blue" if mine == "red" else "red")
            out.append({"id": meta.get("id"), "date": (meta.get("started_at") or "")[:10], "map": (meta.get("map") or {}).get("name"),
                        "mode": meta.get("mode"), "k": int(st.get("kills") or 0), "d": int(st.get("deaths") or 0), "a": int(st.get("assists") or 0),
                        "acs": int(st.get("score") or 0), "hs": (100.0 * h / (h + b + l)) if (h + b + l) else None,
                        "won": (None if mine_s is None or other_s is None else mine_s > other_s)})
        except (KeyError, TypeError, ValueError, AttributeError): continue
    return out

def val_mmr(rid: str, region: str, key: str):
    p = riot_id(rid)
    if not p: return None, "라이엇 ID 는 이름#태그 꼴이어야 합니다"
    n, t = (urllib.parse.quote(x, safe="") for x in p)
    j, err = val_get(f"/valorant/v3/mmr/{region}/pc/{n}/{t}", key)
    return (parse_mmr(j) if j else None), err

def val_matches(rid: str, region: str, key: str, n: int = 20):
    p = riot_id(rid)
    if not p: return None, "라이엇 ID 는 이름#태그 꼴이어야 합니다"
    nm, t = (urllib.parse.quote(x, safe="") for x in p)
    j, err = val_get(f"/valorant/v1/stored-matches/{region}/{nm}/{t}?mode=competitive&size={int(n)}", key)
    return (parse_matches(j) if j else None), err

def week_stats(matches, n: int = 20):
    """최근 n판 요약 — 판 · 승률 · ACS 평균 · HS% 평균 · K/D (단계 관문이 읽는 숫자)"""
    ms = [m for m in (matches or [])][:n]
    if not ms: return None
    won = [m["won"] for m in ms if m["won"] is not None]; hs = [m["hs"] for m in ms if m["hs"] is not None]
    k, d = sum(m["k"] for m in ms), sum(m["d"] for m in ms)
    return {"n": len(ms), "win": (100.0 * sum(won) / len(won)) if won else None, "acs": sum(m["acs"] for m in ms) / len(ms),
            "hs": (sum(hs) / len(hs)) if hs else None, "kd": (k / d) if d else None}


def val_sync(data: dict):
    """설정대로 불러와 data["valo"] 에 넣는다. (성공 여부, 안내 문구). 네트워크를 타므로 GUI 는 스레드로 부른다"""
    cfg = data.get("valo_cfg") or {}
    rid, region, key = (cfg.get("rid") or "").strip(), (cfg.get("region") or "ap"), (cfg.get("key") or "").strip()
    if not rid or not key: return False, "도구 탭에서 라이엇 ID 와 API 키를 넣으세요"
    mmr, e1 = val_mmr(rid, region, key)
    if mmr is None: return False, e1 or "전적을 못 받았습니다"
    ms, e2 = val_matches(rid, region, key, 60)                 # 단계 3·4 관문이 최근 40·60판 승률을 읽는다
    data["valo"] = {"at": datetime.now().strftime("%Y-%m-%d %H:%M"), "mmr": mmr, "recent": week_stats(ms or []), "matches": (ms or [])[:60]}
    data.setdefault("days", {}).setdefault(today_date().isoformat(), blank_day())["valo"] = {"tier": mmr["tier"], "rr": mmr["rr"]}
    rc = data["valo"].get("recent") or {}
    return True, f"{mmr['tier']} {mmr['rr']}RR" + (f" · 최근 {rc['n']}판 승률 {rc['win']:.0f}%" if rc.get("win") is not None else "")

# ══════════════════ 에피소드 · 녹화 오프셋 · 명장면 · 챕터 (v6.0) ══════════════════
# 매일 올리는 시리즈의 한 편 = 훈련 하루. 앱은 세션 시작 시각과 판마다 끝난 시각을 이미 알고 있으니,
# 녹화 시작 시각 하나만 있으면 신기록·최대 상승·마지막 판이 영상 안 어디인지(mm:ss) 바로 나온다.
PLAY_SEC = 60                      # VT S5 시나리오는 전부 60초. CSV 시각은 '끝난' 시각이라 시작 = 끝 − 60

def episode_no(data, dkey):
    """DAY N — 한 번 붙은 번호는 day['ep'] 에 얼려 두어 합치기·경계 이동으로 바뀌지 않는다.
    번호는 '친 날'만 먹는다: 휴식일·안 친 날은 번호를 쓰지 않는다. 기준 측정일 = DAY 1"""
    e = (data.get("days") or {}).get(dkey) or {}
    if e.get("ep"): return e["ep"]
    off = int((data.get("series") or {}).get("ep_offset") or 0)
    lo = BASE_DATE[0] or ""
    n = sum(1 for dk, d in (data.get("days") or {}).items() if lo <= dk < dkey and (d.get("plays") or d.get("count")))
    return off + n + 1

def rec_start(day):
    """녹화 시작 시각과 출처. 표시가 없으면 첫 판 시작(끝−60초)을 0:00 으로 잡는다"""
    r = (day.get("rec") or {})
    if r.get("start"): return r["start"], r.get("src", "manual")
    ss = (day.get("sess") or {}).get("start")
    if ss: return _sec2t(t_key(ss) - PLAY_SEC), "first_play"
    return None, None

def _sec2t(sec):
    sec %= 24 * 3600
    return f"{sec // 3600:02d}.{sec % 3600 // 60:02d}.{sec % 60:02d}"

def fmt_mmss(sec):
    sec = max(0, int(sec)); return f"{sec // 60:02d}:{sec % 60:02d}"

def play_offsets(day, plays):
    """[(offset_sec, key, t, score)] — 영상 안 위치(판 시작 기준)"""
    rs, _src = rec_start(day)
    if rs is None: return []
    r0 = t_key(rs)
    return [(t_key(t) - PLAY_SEC - r0, k, t, sc) for k, t, sc in plays]

def highlights(data, dkey, plays, max_n=8):
    """편집할 때 바로 갈 수 있는 순간들 — PB 는 절대 빠지지 않는다"""
    day = (data.get("days") or {}).get(dkey) or {}
    offs = play_offsets(day, plays)
    if not offs: return []
    kinds = [k for _, _, k in day_verdicts(data, dkey, plays)]
    pts = {i: p[3] for i, p in enumerate(session_points(data, dkey, plays)) if p[3] is not None}   # i → 평소 대비 %
    pbb = pb_before_day(data, dkey)
    out = []; pb_streak = 0; probe_seen = False
    for i, (off, k, t, sc) in enumerate(offs):
        kind = kinds[i] if i < len(kinds) else "new"
        if kind == "pb":
            pb_streak += 1; old = pbb.get(k)
            txt = f"★ {sname(k)} {sc} 신기록" + (f" (+{sc - old})" if old else "") + (f" · 연속 {pb_streak}번째" if pb_streak > 1 else "")
            out.append({"off": off, "kind": "pb", "text": txt, "i": i})
        else: pb_streak = 0
        if not probe_seen and k in PROBE:
            probe_seen = True; out.append({"off": off, "kind": "probe", "text": f"프로브 첫 판 {sname(k)} {sc} — 오늘의 측정", "i": i})
    non_pb = [(pts[i], i) for i in pts if kinds[i] != "pb"]
    if non_pb:
        hi = max(non_pb); off, k, t, sc = offs[hi[1]]
        if hi[0] > 0: out.append({"off": off, "kind": "high", "text": f"최대 상승 {sname(k)} {sc} ({hi[0]:+.1f}%)", "i": hi[1]})
        lo = min(non_pb); off, k, t, sc = offs[lo[1]]
        if kinds[lo[1]] == "low": out.append({"off": off, "kind": "low", "text": f"낮음 {sname(k)} {sc} ({lo[0]:+.1f}%) — 실패 컷", "i": lo[1]})
    off, k, t, sc = offs[-1]
    out.append({"off": off, "kind": "last", "text": "마지막 판 · 오늘 한 장 뜸", "i": len(offs) - 1, "tail": 15})
    # 중복 제거(같은 판) · 시간순 · 상한 — PB 와 마지막은 지키고 나머지부터 뺀다.
    # 마지막 판이 신기록이면 '★ … 신기록 · 마지막 판' 으로 합친다 (꼬리 15초는 카드가 뜨는 시간)
    seen = {}
    for h in out:
        if h["i"] in seen:
            if h["kind"] == "last": seen[h["i"]]["text"] += " · 마지막 판"; seen[h["i"]]["tail"] = h["tail"]; seen[h["i"]]["last"] = True
            continue
        seen[h["i"]] = h
    out = sorted(seen.values(), key=lambda h: h["off"])
    while len(out) > max_n:
        drop = next((h for h in out if h["kind"] not in ("pb", "last")), None)
        if drop is None: break
        out.remove(drop)
    for h in out: h["in"], h["out"] = max(0, h["off"] - 3), h["off"] + PLAY_SEC + 3 + h.get("tail", 0)
    return out

def chapters(data, dkey, plays):
    """유튜브 챕터: 00:00 부터 오름차순, 10초 이상 간격, 3개 이상 아니면 빈 목록"""
    day = (data.get("days") or {}).get(dkey) or {}
    offs = play_offsets(day, plays)
    if not offs: return []
    ep = episode_no(data, dkey); dt = day_type_of(dkey)
    theme = main_theme(dkey, data.get("pb"))[1] if dt == "v" else bench_label(dkey)
    ch = [(0, f"오늘의 루틴 — DAY {ep} {theme}")]
    def first(pred, title):
        o = next((off for off, k, _t, _s in offs if pred(k)), None)
        if o is None: return
        if o < 10: ch[0] = (0, ch[0][1] + " · " + title)              # 녹화 직후 시작한 구간은 첫 챕터 제목에 붙인다
        else: ch.append((o, title))
    if dt == "v":
        first(lambda k: k in WARM_KEYS, f"워밍업 {len(WARMUP)}판")
        first(lambda k: k in PROBE, f"프로브 {len(PROBE)}판 — 오늘의 측정")
        first(lambda k: k not in WARM_KEYS and k not in PROBE, f"본훈련 — {theme}")   # 계획 밖 판이어도 본훈련 구간
    else:
        for sub in SUBS:
            ks = {k for k, _th in sub[3]}; first(lambda k, ks=ks: k in ks, f"{sub[1]} · {sub[2]}")
    ch.append((offs[-1][0] + PLAY_SEC, "오늘 한 장"))
    ok = []
    for o, t in sorted(ch):
        if o < 0: continue
        if ok and o - ok[-1][0] < 10: continue
        ok.append((o, t))
    return ok if len(ok) >= 3 and ok[0][0] == 0 else []


# ══════════════════ 업로드 팩 (v6.0) — 한 편 올리는 데 5분 ══════════════════
SERIES = {"title": "Road to Immortal", "who": "YouKnowJo#YK1", "channel": "@YouKnow-ky9oh"}
VAL_ORDER = ["Iron", "Bronze", "Silver", "Gold", "Platinum", "Diamond", "Ascendant", "Immortal", "Radiant"]
VAL_TIER_KO = {"Iron": "아이언", "Bronze": "브론즈", "Silver": "실버", "Gold": "골드", "Platinum": "플래티넘", "Diamond": "다이아몬드",
               "Ascendant": "어센던트", "Immortal": "불멸", "Radiant": "레디언트", "Unrated": "언레이티드", "Unranked": "언랭"}

def ko_tier(t: str) -> str:
    """'Gold 2' → '골드 2'. 모르는 이름은 그대로"""
    if not t: return ""
    n = norm_val_tier(t); parts = (n or str(t).strip()).split()
    return " ".join([VAL_TIER_KO.get(parts[0], parts[0])] + parts[1:])

VAL_KO_REV = {v: k for k, v in VAL_TIER_KO.items()}
VAL_KO_REV.update({"플래": "Platinum", "다이아": "Diamond", "어센": "Ascendant", "이모탈": "Immortal", "레디": "Radiant", "언랭": "Unranked"})

def norm_val_tier(t):
    """랭크 카드에 손으로 적은 티어를 영어 표준형으로 — '골드 2' · '골드2' · '플래 1' · 'gold 2' → 'Gold 2'. 모르면 None"""
    if not t: return None
    m = re.match(r"^([A-Za-z가-힣]+)\s*(\d)?$", unicodedata.normalize("NFKC", str(t)).strip())
    if not m: return None
    name, div = m.group(1), m.group(2)
    en = next((k for k in VAL_ORDER if k.lower() == name.lower()), None) or VAL_KO_REV.get(name)
    if en not in VAL_ORDER: return None
    return en + (f" {div}" if div else "")

def val_rank_ord(t: str):
    """티어 문자열의 순서값 (비교용). 'Gold 2' → 32 · '골드 2' → 32 · 'Immortal 1' → 71 · 모르면 None"""
    n = norm_val_tier(t)
    if not n: return None
    parts = n.split()
    return VAL_ORDER.index(parts[0]) * 10 + (int(parts[1]) if len(parts) > 1 else 0)

def day_val_tier(data: dict, dkey: str):
    """그날의 발로란트 티어·RR — 손으로 적은 값이 먼저, 없으면 그날 불러온 스냅샷"""
    e = (data.get("days") or {}).get(dkey) or {}
    r = e.get("rank") or {}
    if r.get("tier"): return (r["tier"], r.get("rr"))
    v = e.get("valo") or {}
    return (v.get("tier"), v.get("rr")) if v.get("tier") else (None, None)

def prev_val_tier(data: dict, dkey: str):
    for dk in sorted(data.get("days") or {}, reverse=True):
        if dk >= dkey: continue
        t, _rr = day_val_tier(data, dk)
        if t: return t
    return None

def milestones(data: dict, dkey: str, plays=None):
    """특별편 감지 — [(코드, 문구)]. 강등한 날도 특별편이다 (규칙 01: 못한 날도 올린다)"""
    out = []
    ep = episode_no(data, dkey)
    if ep in (10, 30, 50, 100, 200, 365): out.append(("DAY", f"★ DAY {ep}"))
    t, _rr = day_val_tier(data, dkey); pt = prev_val_tier(data, dkey)
    if t and pt and t != pt:
        a, b = val_rank_ord(pt), val_rank_ord(t)
        if a is not None and b is not None and b > a: out.append(("VAL_UP", f"★ 랭크업 {ko_tier(pt)} → {ko_tier(t)}"))
        elif a is not None and b is not None and b < a: out.append(("VAL_DOWN", f"강등 {ko_tier(pt)} → {ko_tier(t)}"))
    e0, _n0 = totalE(pb_before_day(data, dkey)); e1, _n1 = totalE(data.get("pb") or {})
    if e0 is not None and e1 is not None and rank_of(e1)[0] != rank_of(e0)[0] and e1 > e0:
        out.append(("VT_UP", f"★ 볼테익 {rank_of(e0)[0]} → {rank_of(e1)[0]}"))
    t_ = CUR_TIER[0]; top = TIERS[t_][1] + 400
    pb = data.get("pb") or {}; pbb = pb_before_day(data, dkey)
    if pb and all((subE(sub, pb) or 0) >= top for sub in SUBS_T[t_]) and not all((subE(sub, pbb) or 0) >= top for sub in SUBS_T[t_]):
        out.append(("SUB_TOP", f"★ 9갈래 전부 {TIERS[t_][2][3]}"))
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    n_today = sum(1 for _k, _s, kind in day_verdicts(data, dkey, plays) if kind == "pb")
    tot = total_pbs(data)
    for T in (10, 50, 100, 250, 500):
        if tot - n_today < T <= tot: out.append(("PB", f"★ 누적 신기록 {T}개"))
    cur, _best = streak(training_days(data), date.fromisoformat(dkey))
    if cur in (10, 30, 100): out.append(("STREAK", f"★ 연속 {cur}일"))
    st = data.get("stage") or {}
    if st.get("since") == dkey and st.get("idx", 0) > 0: out.append(("STAGE_UP", f"★ 단계 {st['idx']} 진입 — {STAGES[st['idx']]['name']}"))
    return out

SUB_KO = {"Dynamic": "다이내믹", "Static": "스태틱", "Linear": "리니어", "Precise": "프리시전", "Reactive": "리액티브",
          "Control": "컨트롤", "Speed": "스피드", "Evasive": "이배시브", "Stability": "스태빌리티"}

def gate_status(pb: dict, tier: str = None) -> dict:
    """관문 미터 — 현재 단계에서 9갈래 중 몇 개가 최상위(노비스면 골드)인가, 못 넘은 갈래는 어느 시나리오 몇 점이 모자란가.
    1일차부터 답이 나오는 유일한 '남은 거리' 지표 — 성장 판정이 3주 걸리는 동안 시청자가 볼 숫자"""
    t = tier or CUR_TIER[0]; off = TIERS[t][1]; top = off + 400; pb = pb or {}
    n = 0; left = []
    for sub in SUBS_T[t]:
        e = subE(sub, pb, off)
        if e is not None and e >= top: n += 1; continue
        best = None
        for k, th in sub[3]:
            need = math.ceil(score_for_energy(400, th)); cur = pb.get(k)
            gap = need - (cur if cur is not None else 0)
            if cur is not None and (best is None or gap < best[2]): best = (k, need, gap)
        if best is None:                                   # 아직 한 판도 없는 갈래 — 첫 시나리오 기준
            k, th = sub[3][0]; best = (k, math.ceil(score_for_energy(400, th)), None)
        left.append((SUB_KO.get(sub[2], sub[2]), best[0], best[1], best[2]))
    left.sort(key=lambda x: (x[3] is None, x[3] if x[3] is not None else 0))
    e0 = totalE(BASELINE[0])[0] if BASELINE[0] else None; e1 = totalE(pb)[0] if pb else None
    return {"n": n, "total": 9, "left": left, "e0": e0, "e1": e1, "top": TIERS[t][2][3], "tier": t}

def fmt_gate(g: dict):
    """(문구, 숫자, 설명줄). 남은 갈래는 3개까지 '시나리오 +N' 으로"""
    if g["n"] >= g["total"]:
        nxt = TIER_ORDER.index(g["tier"]) + 1
        cap = (f"에너지 {g['e0']} → {g['e1']}" if g["e0"] is not None and g["e1"] is not None else "") + \
              (f" · 다음은 {TIER_KO[TIER_ORDER[nxt]]}" if nxt < len(TIER_ORDER) else "")
        return (f"{TIER_KO[g['tier']]} 졸업 ✓", (f"{g['e1'] - g['e0']:+d}" if g["e0"] is not None and g["e1"] is not None else "9/9"), cap.strip(" ·"))
    items = [f"{sname(k)} +{gap}" if gap is not None else f"{sname(k)} {need}" for _sub, k, need, gap in g["left"][:3]]
    return (f"{TIER_KO[g['tier']]} 졸업 {g['n']}/{g['total']}", f"남은 {g['total'] - g['n']}", " · ".join(items) + ("…" if len(g["left"]) > 3 else ""))

def rr_net(data: dict, dkey: str) -> int:
    """출발선 이후 손으로 적은 RR 변화의 합"""
    lo = BASE_DATE[0] or ""; tot = 0
    for dk, e in (data.get("days") or {}).items():
        if lo <= dk <= dkey:
            try: tot += int((e.get("rank") or {}).get("rr") or 0)
            except (TypeError, ValueError): pass
    return tot

def story_line(data: dict, dkey: str) -> str:
    """주인공 줄 — 누구·어디·얼마나 꾸준히. 시청자용 모든 화면의 첫 줄.
    'DAY 14 · 골드 2 → 불멸 · 연속 12일'  (기준 측정 전엔 'DAY 0 · 기준 측정')"""
    if BASE_DATE[0] is None and not ((data.get("days") or {}).get(dkey) or {}).get("plays"): return "DAY 0 · 기준 측정"
    ep = episode_no(data, dkey)
    t, rr = None, None
    for dk in sorted(data.get("days") or {}, reverse=True):
        if dk > dkey: continue
        t, rr = day_val_tier(data, dk)
        if t: break
    tier = ko_tier(t) if t else ((data.get("series") or {}).get("tier") or "골드 2")
    cur, _b = streak(training_days(data), date.fromisoformat(dkey))
    goal = (data.get("series") or {}).get("goal") or "불멸"
    return f"DAY {ep} · {tier} → {goal}" + (f" · 연속 {cur}일" if cur >= 2 else "")

def _best_pb_line(data: dict, dkey: str, plays):
    pbb = pb_before_day(data, dkey); best = None
    for k, _s, kind in day_verdicts(data, dkey, plays):
        if kind != "pb": continue
        old = pbb.get(k); d_ = (_s - old) if old else None
        if best is None or (d_ or 0) > (best[2] or 0): best = (k, _s, d_)
    if best is None: return ""
    k, sc, d_ = best
    return f"{sname(k)} {sc} 신기록" + (f" (+{d_})" if d_ else "")

def _cut(t: str, n: int = 100) -> str:
    return t if len(t) <= n else t[:n - 1] + "…"

def upload_pack(data: dict, dkey: str, plays=None, dt: str = None) -> str:
    """유튜브 업로드에 필요한 글 전부 — 제목 후보 3 · 설명 · 명장면(영상 안 위치) · 챕터 · 태그 · 고정 댓글"""
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    dt = dt or day_type_of(dkey); d = date.fromisoformat(dkey); ep = episode_no(data, dkey)
    V = verdicts(data, dkey, dt, plays); Vd, Vr, Vg = V["day"], V["recent"], V["grow"]
    theme = main_theme(dkey, data.get("pb"))[1] if dt == "v" else bench_label(dkey)
    ms = milestones(data, dkey, plays); pbl = _best_pb_line(data, dkey, plays)
    n_pb = sum(1 for _k, _s, kind in day_verdicts(data, dkey, plays) if kind == "pb")
    ss = session_summary(plays, {}); mins = ss.get("minutes")
    vt, vrr = day_val_tier(data, dkey); vline = (ko_tier(vt) + (f" · {vrr}RR" if vrr is not None else "")) if vt else "골드 2"
    e_pb, _ = totalE(data.get("pb") or {}); eline = f"총 에너지 {e_pb} {rank_of(e_pb)[0]}" if e_pb is not None else "기준 측정 전"
    # 오늘 가장 큰 일: 특별편 > 랭크 변동 > 신기록 > 에너지 > 테마
    big = ms[0][1] if ms else (pbl or eline)
    who = (data.get("valo_cfg") or {}).get("rid") or SERIES["who"]
    t1 = _cut(f"[{SERIES['title']}] DAY {ep} · {vline.split(' · ')[0]} 에임 훈련 — {Vd['word']} {Vd['glyph']} {Vd['num']}" + (f" · 신기록 {n_pb}개" if n_pb else ""))
    t2 = _cut(f"{vline.split(' · ')[0]}가 불멸 갈 때까지 매일 코박스 DAY {ep} | {big}")
    t3 = _cut(f"DAY {ep} | {theme} {len(plays)}판" + (f" {mins}분" if mins else "") + f" · {Vr['word']}")
    if dt == "b" and e_pb is not None: t1 = _cut(f"[{SERIES['title']}] DAY {ep} {theme} — 볼테익 {e_pb} {rank_of(e_pb)[0]}")
    L = [f"[제목 후보]  (100자 이내 · 하나 골라 복사)", f"1. {t1}", f"2. {t2}", f"3. {t3}", ""]
    gw, gn, gc = fmt_gate(gate_status(data.get("pb") or {}))
    L += ["[설명]", f"{SERIES['title']} · {story_line(data, dkey)} · {dkey} ({DOWK[d.weekday()]})" + (f" · {ms[0][1]}" if ms else ""),
          f"발로란트 {vline} · 목표 불멸", f"오늘 {Vd['word']} {Vd['glyph']} {Vd['num']} · 요즘 {Vr['word']} · 성장 {Vg['word']}",
          f"루틴 {theme} · {len(plays)}판" + (f" · {mins}분" if mins else "") + (f" · 신기록 {n_pb}개" if n_pb else ""), eline + f" · {TIER_KO[CUR_TIER[0]]} 벤치마크",
          f"{gw} — {gc}" if gc else gw]
    ch_ = day_changes(data, dkey)
    if ch_: L += ["오늘 바뀐 것: " + " · ".join(str(x) for x in ch_[:4])]
    L += ["", "매일 올립니다 — 못한 날도. 점수는 코박스가 저장한 파일에서 앱이 직접 읽습니다.", f"{who} · 에임 데스크", ""]
    day = (data.get("days") or {}).get(dkey) or {}; rs, src = rec_start(day)
    hl = highlights(data, dkey, plays)
    L += ["[명장면]  " + (f"녹화 시작 {rs.replace('.', ':')} ({'루틴 실행 시각' if src == 'routine' else '버튼' if src == 'manual' else '첫 판 시작'}) · 시각 = 영상 안 위치" if rs else "녹화 시작 표시 없음")]
    L += [f"{fmt_mmss(h['off'])}  {h['text']:<40} [{fmt_mmss(h['in'])}–{fmt_mmss(h['out'])}]" for h in hl] or ["(판이 없습니다)"]
    ch = chapters(data, dkey, plays)
    L += ["", "[챕터]  (설명 맨 아래에 그대로)"] + ([f"{fmt_mmss(o)} {t}" for o, t in ch] or ["(챕터 3개를 못 만들었습니다 — 판이 더 있어야 합니다)"])
    L += ["", "[태그]", "에임 훈련, 코박스, KovaaK's, 발로란트, Valorant, 골드, 불멸, Road to Immortal, 볼테익, Voltaic, aim training, 에임 연습, 매일 훈련"]
    nxt = nearest_rankup(data.get("pb") or {})
    L += ["", "[고정 댓글]", f"DAY {ep} · {Vd['word']} {Vd['num']}" + (f" · 신기록 {n_pb}개" if n_pb else "") +
          (f" · 다음 목표: {sname(nxt[1])} {nxt[2]}점이면 {nxt[3]}" if nxt else "") + " · 기록 파일은 앱이 자동 저장합니다"]
    return "\n".join(L) + "\n"

def thumb_data(data: dict, dkey: str, plays=None, dt: str = None) -> dict:
    """썸네일에 들어갈 세 가지 — 큰 숫자/단어 · 짧은 단어 · 부제. 고르는 순서: 특별편 > 랭크 변동 > 신기록 > 오늘 판정 > 에너지"""
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    dt = dt or day_type_of(dkey); ep = episode_no(data, dkey)
    V = verdicts(data, dkey, dt, plays); Vd = V["day"]
    theme = main_theme(dkey, data.get("pb"))[1] if dt == "v" else bench_label(dkey)
    vt, _rr = day_val_tier(data, dkey); sub = f"{ko_tier(vt) if vt else '골드 2'} · {theme}"
    ms = milestones(data, dkey, plays); pbl = _best_pb_line(data, dkey, plays)
    e_pb, _ = totalE(data.get("pb") or {})
    if ms: big, word, colk = ms[0][1].replace("★ ", ""), "특별편", "gold"
    elif pbl: big, word, colk = pbl.split(" 신기록")[0], "신기록" + (pbl.split("신기록")[1].strip() or ""), "gold"
    elif Vd["state"] in ("up", "flat", "down"): big, word, colk = Vd["num"], Vd["word"], Vd["state"]
    elif e_pb is not None: big, word, colk = f"{e_pb} E", "볼테익", "sub"
    else: big, word, colk = "DAY 1", "출발선", "gold"
    if dt == "b" and e_pb is not None: big, word, colk = f"{e_pb} E", "보스전", "gold"
    return {"day": f"DAY {ep}", "big": big, "word": word, "sub": sub, "colk": colk, "story": story_line(data, dkey), "who": SERIES["channel"]}

THUMB_COL = {"up": "#4ADE80", "flat": "#C9D6E2", "down": "#FF6B6B", "gold": "#FFC531", "sub": "#948CC8"}

def thumb_html(td: dict) -> str:
    """혼자 도는 HTML — CDN 없음, 엣지에서 오프라인으로 열려 'PNG 저장' 을 누르면 1280×720 PNG 가 내려온다"""
    payload = json.dumps(dict(td, col=THUMB_COL.get(td.get("colk"), "#FFC531")), ensure_ascii=False)
    return """<!doctype html><html lang="ko"><head><meta charset="utf-8"><title>썸네일 · %s</title>
<style>body{margin:0;background:#0A0821;color:#ECEAFB;font-family:"Malgun Gothic","Pretendard",sans-serif;padding:20px}
.row{display:flex;flex-wrap:wrap;gap:20px}.c{display:flex;flex-direction:column;gap:8px}canvas{width:640px;height:360px;border:1px solid #2E2870;border-radius:8px}
button{font:600 14px "Malgun Gothic",sans-serif;padding:8px 14px;border-radius:6px;border:1px solid #2E2870;background:#16123A;color:#ECEAFB;cursor:pointer}
h1{font-size:18px;font-weight:600;margin:0 0 14px}</style></head><body>
<h1>%s · 썸네일 3장 — 하나 골라 PNG 저장 (1280×720)</h1><div class="row" id="row"></div>
<script>
var D=%s;
function rr(g,x,y,w,h,r){g.beginPath();g.moveTo(x+r,y);g.arcTo(x+w,y,x+w,y+h,r);g.arcTo(x+w,y+h,x,y+h,r);g.arcTo(x,y+h,x,y,r);g.arcTo(x,y,x+w,y,r);g.closePath();g.fill();}
function fit(g,t,max,px,bold){for(var s=px;s>24;s-=4){g.font=(bold?"900 ":"700 ")+s+"px 'Malgun Gothic','Pretendard',sans-serif";if(g.measureText(t).width<=max)return s;}return 24;}
function draw(kind,cv){var g=cv.getContext("2d");g.fillStyle="#0A0821";g.fillRect(0,0,1280,720);
 var grd=g.createRadialGradient(1120,-80,40,1120,-80,900);grd.addColorStop(0,"#2A1F6E");grd.addColorStop(1,"rgba(10,8,33,0)");g.fillStyle=grd;g.fillRect(0,0,1280,720);
 g.textBaseline="middle";
 if(kind==="A"){g.fillStyle="#5FE8FF";fit(g,D.day,600,140,true);g.textAlign="left";g.fillText(D.day,60,120);
  g.fillStyle=D.col;var s=fit(g,D.big,1160,260,true);g.textAlign="center";g.fillText(D.big,640,360);
  g.fillStyle=D.col;fit(g,D.word,1160,96,true);g.fillText(D.word,640,520);
  g.fillStyle="#948CC8";g.textAlign="left";fit(g,D.sub,800,44,false);g.fillText(D.sub,60,660);g.textAlign="right";g.fillStyle="#5B5490";g.fillText(D.who,1220,660);}
 else if(kind==="B"){g.fillStyle=D.col;var s2=fit(g,D.word,1160,180,true);g.textAlign="center";g.fillText(D.word,640,300);
  g.fillStyle="#ECEAFB";fit(g,D.big,1160,120,true);g.fillText(D.big,640,470);
  g.fillStyle="#5FE8FF";g.textAlign="left";fit(g,D.day,600,72,true);g.fillText(D.day,60,90);
  g.fillStyle="#948CC8";fit(g,D.sub,1100,44,false);g.fillText(D.sub,60,660);}
 else{g.fillStyle="#5FE8FF";g.textAlign="left";fit(g,D.day,600,110,true);g.fillText(D.day,60,110);
  g.fillStyle="#ECEAFB";fit(g,D.story,1160,56,false);g.fillText(D.story,60,210);
  g.fillStyle=D.col;rr(g,60,300,1160,300,28);g.fillStyle="#10141A";fit(g,D.big,1000,150,true);g.textAlign="center";g.fillText(D.big,640,410);
  fit(g,D.word,1000,72,true);g.fillText(D.word,640,540);
  g.fillStyle="#948CC8";g.textAlign="left";fit(g,D.sub,800,40,false);g.fillText(D.sub,60,670);}}
["A","B","C"].forEach(function(k){var c=document.createElement("div");c.className="c";var cv=document.createElement("canvas");cv.width=1280;cv.height=720;draw(k,cv);
 var b=document.createElement("button");b.textContent={A:"A 숫자 — PNG 저장",B:"B 단어 — PNG 저장",C:"C 밴드 — PNG 저장"}[k];
 b.onclick=function(){cv.toBlob(function(bl){var a=document.createElement("a");a.href=URL.createObjectURL(bl);a.download=D.day.replace(" ","")+"_"+k+".png";a.click();},"image/png");};
 c.appendChild(cv);c.appendChild(b);document.getElementById("row").appendChild(c);});
</script></body></html>""" % (td["day"], td["day"], payload)

def save_thumb_page(data: dict, dkey: str, plays=None, dt: str = None, dir_=None) -> Path:
    ep = episode_no(data, dkey)
    p = (Path(dir_) if dir_ else report_dir()) / f"EP{ep:03d}_{dkey}_썸네일.html"
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp"); tmp.write_text(thumb_html(thumb_data(data, dkey, plays, dt)), encoding="utf-8"); os.replace(tmp, p)
    return p

def save_upload_pack(data: dict, dkey: str, plays=None, dt: str = None, dir_=None) -> Path:
    ep = episode_no(data, dkey)
    p = (Path(dir_) if dir_ else report_dir()) / f"EP{ep:03d}_{dkey}_업로드.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    txt = upload_pack(data, dkey, plays, dt)
    tmp = p.with_name(p.name + ".tmp"); tmp.write_text(txt, encoding="utf-8-sig"); os.replace(tmp, p)
    e = (data.get("days") or {}).get(dkey)
    if e is not None: e["ms"] = [t for _c, t in milestones(data, dkey, plays)]
    return p

# ══════════════════ 단계 사다리 · 주간 결산 (v6.0) ══════════════════
# 골드 2 → 불멸까지 다섯 단계. 관문은 전부 앱이 읽는 숫자다 — 에임(볼테익) · 게임(발로 블록·전적) · 랭크(유지).
# 단계는 '두 일요일 연속' 관문이 다 찰 때만 오른다. 한 주 잘된 걸로 올리지 않고, 한 주 못했다고 내리지도 않는다.
# 에임은 엔진이 아니라 관문이다 — 에임 관문은 파란데 게임 관문이 빨간 채면 답은 코박스가 아니다. 그래서 세 갈래를 따로 보여 준다.
STAGES = [
    {"name": "출발선",               "motto": "재고 시작한다",          "span": "2주"},
    {"name": "골드 2 → 플래티넘 1",   "motto": "크로스헤어가 곧 랭크",     "span": "2~4개월"},
    {"name": "플래티넘 → 다이아 1",   "motto": "에임이 아니라 타이밍",     "span": "3~6개월"},
    {"name": "다이아 1 → 어센던트 1", "motto": "복기가 실력을 만든다",     "span": "4~8개월"},
    {"name": "어센던트 1 → 불멸 1",   "motto": "RR 은 승리에서만 나온다",  "span": "6~18개월 · 미도달 가능"},
]
GATE_KO = {"aim": "에임", "game": "게임", "rank": "랭크"}
WHY_KO = {"aim": "에임", "pos": "피크·위치", "dec": "정보·판단", "util": "유틸"}

def iso_week_id(dkey: str) -> str:
    y, w, _d = date.fromisoformat(dkey).isocalendar()
    return f"{y}-W{w:02d}"

def _week_after(wid: str) -> str:
    y, w = wid.split("-W")
    return iso_week_id((date.fromisocalendar(int(y), int(w), 1) + timedelta(days=7)).isoformat())

def week_range(dkey: str):
    """dkey 가 속한 주의 월~일 7일"""
    d = date.fromisoformat(dkey); mon = d - timedelta(days=d.weekday())
    return [(mon + timedelta(days=i)).isoformat() for i in range(7)]

def _val_field_med(data: dict, dkey: str, field: str, days: int = 14):
    """최근 days 일 발로 블록 항목의 중앙값 → (값, 개수). 한두 판의 요행이 관문을 열지 않게 중앙값"""
    d0 = (date.fromisoformat(dkey) - timedelta(days=days - 1)).isoformat(); vals = []
    for dk, e in (data.get("days") or {}).items():
        if d0 <= dk <= dkey:
            v = (e.get("val") or {}).get(field)
            if v is not None: vals.append(float(v))
    return _median(vals), len(vals)

def _aim_death_ratio(data: dict, dkey: str, days: int = 14):
    """랭크 카드에서 '가장 많이 죽은 이유 = 에임' 인 날의 비율(%) → (값, 적은 날 수)"""
    d0 = (date.fromisoformat(dkey) - timedelta(days=days - 1)).isoformat(); n = a = 0
    for dk, e in (data.get("days") or {}).items():
        if d0 <= dk <= dkey:
            w = (e.get("rank") or {}).get("why")
            if w: n += 1; a += (w == "aim")
    return (100.0 * a / n if n else None), n

def _val_records(data: dict, dkey: str):
    out = []
    for dk in sorted(data.get("days") or {}):
        if dk > dkey: continue
        o = val_rank_ord(day_val_tier(data, dk)[0])
        if o is not None: out.append((dk, o))
    return out

def held_days(data: dict, dkey: str, min_ord: int) -> int:
    """지금 티어가 min_ord 이상이고, 마지막으로 그 아래였던 기록 이후 며칠째인가. 미달이면 0"""
    rec = _val_records(data, dkey)
    if not rec or rec[-1][1] < min_ord: return 0
    since = rec[-1][0]
    for dk, o in reversed(rec):
        if o < min_ord: break
        since = dk
    return (date.fromisoformat(dkey) - date.fromisoformat(since)).days + 1

def _recap_streak(data: dict, dkey: str) -> int:
    """주간 결산이 연속 몇 주 저장됐나 (이번 주가 아직 안 닫혔으면 지난 주부터)"""
    wks = data.get("weeks") or {}; d = date.fromisoformat(dkey); sun = d + timedelta(days=6 - d.weekday()); n = 0
    for i in range(104):
        if (wks.get(iso_week_id((sun - timedelta(days=7 * i)).isoformat())) or {}).get("pack"): n += 1
        elif i == 0: continue
        else: break
    return n

def _api_recent(data: dict, n: int):
    ms = (data.get("valo") or {}).get("matches") or []
    return week_stats(ms, n) if ms else None

def _hs_pct(data: dict, dkey: str):
    """HS% — 발로 블록 DM 14일 중앙값이 먼저, 없으면 전적 최근 20판"""
    v, n = _val_field_med(data, dkey, "dm_hs")
    if v is not None: return v, f"DM {n}일"
    rc = _api_recent(data, 20)
    if rc and rc.get("hs") is not None: return rc["hs"], f"전적 {rc['n']}판"
    return None, ""

def tier_energy(scores: dict, tier: str):
    """특정 단계 표로만 계산한 총 에너지 (PB 에 두 단계 키가 섞여 있어도 그 단계만) → (에너지, 갈래 수)"""
    off = TIERS[tier][1]
    es = [subE(s, scores, off) for s in SUBS_T[tier]]; es = [e for e in es if e is not None]
    return (int(len(es) / sum(1 / max(e, 1) for e in es) + 1e-9), len(es)) if es else (None, 0)

def stage_idx(data: dict) -> int: return int((data.get("stage") or {}).get("idx", 0))

def _gate_item(kind, label, ok, val): return {"k": kind, "label": label, "ok": ok, "val": val}

def stage_gates(data: dict, dkey: str, idx: int = None):
    """현재 단계의 관문 목록 — ok 는 True/False, 자료가 아직 없으면 None (닫힌 것으로 세되 '자료 없음'으로 보인다)"""
    idx = stage_idx(data) if idx is None else idx
    pb = data.get("pb") or {}; days = data.get("days") or {}
    ge = lambda v, th: (None if v is None else v >= th); le = lambda v, th: (None if v is None else v <= th)
    fv = lambda v, u="", nd=0: "자료 없음" if v is None else f"{v:.{nd}f}{u}"
    G = []
    if idx == 0:
        tds = sorted(d for d in training_days(data) if d <= dkey and (BASE_DATE[0] is None or d >= BASE_DATE[0]))
        G.append(_gate_item("aim", "출발선 측정 18판", BASE_DATE[0] is not None, BASE_DATE[0] or "아직"))
        G.append(_gate_item("aim", "훈련 10일", len(tds) >= 10, f"{len(tds)}/10일"))
        last10 = [d for d in tds if d != BASE_DATE[0]][-10:]; nv = sum(1 for d in last10 if val_done(days[d]))
        G.append(_gate_item("game", "발로 블록 8/10일", nv >= 8, f"{nv}/10일"))
        d0 = (date.fromisoformat(dkey) - timedelta(days=13)).isoformat()
        nr = sum(1 for d in days if d0 <= d <= dkey and day_val_tier(data, d)[0])
        G.append(_gate_item("rank", "랭크 카드 5일 (14일 안)", nr >= 5, f"{nr}/5일"))
    elif idx == 1:
        g = gate_status(pb, "n"); grad = CUR_TIER[0] != "n" or g["n"] >= 9
        G.append(_gate_item("aim", "노비스 졸업 (9갈래 골드)", grad, "졸업 ✓" if CUR_TIER[0] != "n" else f"{g['n']}/9"))
        hs, src = _hs_pct(data, dkey); G.append(_gate_item("game", "DM HS% 14일 중앙 ≥ 25", ge(hs, 25), fv(hs, "%") + (f" ({src})" if src else "")))
        rg, _n = _val_field_med(data, dkey, "range"); G.append(_gate_item("game", "사격 ≥ 24/30", ge(rg, 24), fv(rg, "/30")))
        ar, n = _aim_death_ratio(data, dkey); G.append(_gate_item("game", "'에임' 죽음 ≤ 40%", le(ar, 40), fv(ar, "%") + (f" ({n}일)" if n else "")))
        hd = held_days(data, dkey, val_rank_ord("Platinum 1")); G.append(_gate_item("rank", "플래티넘 1 · 14일 강등 없음", hd >= 14, f"{hd}/14일"))
    elif idx == 2:
        ok6 = sum(1 for s in SUBS_T["i"] if (subE(s, pb) or 0) >= 500)
        G.append(_gate_item("aim", "인터미디어트 500 · 6갈래", ok6 >= 6, f"{ok6}/6갈래"))
        hs, src = _hs_pct(data, dkey); G.append(_gate_item("game", "HS% ≥ 30", ge(hs, 30), fv(hs, "%")))
        rg, _n = _val_field_med(data, dkey, "range"); G.append(_gate_item("game", "사격 ≥ 27/30", ge(rg, 27), fv(rg, "/30")))
        rc = _api_recent(data, 20); acs = rc["acs"] if rc else None; G.append(_gate_item("game", "최근 20판 ACS ≥ 220", ge(acs, 220), fv(acs)))
        hd = held_days(data, dkey, val_rank_ord("Diamond 1")); G.append(_gate_item("rank", "다이아 1 · 14일 유지", hd >= 14, f"{hd}/14일"))
        rs = _recap_streak(data, dkey); G.append(_gate_item("rank", "주간 결산 8주 연속", rs >= 8, f"{rs}/8주"))
    elif idx == 3:
        e_i, _n = tier_energy(pb, "i"); all600 = bool(_n == 9 and all((subE(s, pb) or 0) >= 600 for s in SUBS_T["i"]))
        G.append(_gate_item("aim", "인터 650 · 9갈래 600", (e_i or 0) >= 650 and all600, fv(e_i) + (" · 9갈래 ✓" if all600 else f" · {sum(1 for s in SUBS_T['i'] if (subE(s, pb) or 0) >= 600)}/9")))
        hs, src = _hs_pct(data, dkey); G.append(_gate_item("game", "HS% ≥ 27", ge(hs, 27), fv(hs, "%")))
        rc = _api_recent(data, 20); acs = rc["acs"] if rc else None; G.append(_gate_item("game", "ACS ≥ 230", ge(acs, 230), fv(acs)))
        r4 = _api_recent(data, 40); win = r4["win"] if r4 else None; G.append(_gate_item("game", "최근 40판 승률 ≥ 53%", ge(win, 53), fv(win, "%")))
        hd = held_days(data, dkey, val_rank_ord("Ascendant 1")); G.append(_gate_item("rank", "어센던트 1 · 30일 유지", hd >= 30, f"{hd}/30일"))
    else:
        e_i, _n = tier_energy(pb, "i"); G.append(_gate_item("aim", "인터 700", (e_i or 0) >= 700, fv(e_i)))
        hs, src = _hs_pct(data, dkey); G.append(_gate_item("game", "HS% ≥ 28", ge(hs, 28), fv(hs, "%")))
        rc = _api_recent(data, 20); acs = rc["acs"] if rc else None; G.append(_gate_item("game", "ACS ≥ 240", ge(acs, 240), fv(acs)))
        r6 = _api_recent(data, 60); win = r6["win"] if r6 else None; G.append(_gate_item("game", "최근 60판 승률 ≥ 55%", ge(win, 55), fv(win, "%")))
        hd = held_days(data, dkey, val_rank_ord("Immortal 1")); G.append(_gate_item("rank", "불멸 1 · 30일 강등 없음", hd >= 30, f"{hd}/30일"))
    return G

def stage_status(data: dict, dkey: str) -> dict:
    idx = min(stage_idx(data), len(STAGES) - 1); G = stage_gates(data, dkey, idx); st = data.get("stage") or {}
    by = {k: (sum(1 for g in G if g["k"] == k and g["ok"]), sum(1 for g in G if g["k"] == k)) for k in GATE_KO}
    return {"idx": idx, "name": STAGES[idx]["name"], "motto": STAGES[idx]["motto"], "span": STAGES[idx]["span"], "gates": G,
            "n_ok": sum(1 for g in G if g["ok"]), "total": len(G), "by": by,
            "weeks_ok": list(st.get("ok_weeks") or []), "since": st.get("since"), "final": idx >= len(STAGES) - 1}

def fmt_stage_chip(s: dict) -> str: return f"단계 {s['idx']} · 관문 {s['n_ok']}/{s['total']}"

def stage_lines(data: dict, dkey: str):
    """기록 파일 [단계] 절 · 주간 결산 [관문] 절"""
    s = stage_status(data, dkey)
    L = [f"단계 {s['idx']} · {s['name']} — {s['motto']} ({s['span']}) · 관문 {s['n_ok']}/{s['total']}"]
    for g in s["gates"]:
        L.append(f"  {'✓' if g['ok'] else ('·' if g['ok'] is None else '✗')} [{GATE_KO[g['k']]}] {g['label']}: {g['val']}")
    if s["weeks_ok"]: L.append(f"  관문이 다 찬 주: {', '.join(s['weeks_ok'])} — 두 주 연속이면 다음 단계")
    if s["since"] == dkey and s["idx"] > 0: L.append(f"  ★ 오늘 단계 {s['idx']} 진입")
    return L

def stage_check(data: dict, dkey: str):
    """쉬는 날 결산 때 부른다. 관문이 다 찼으면 그 주를 적고, 두 주 연속이면 다음 단계로 → (올랐는가, 지금 단계)"""
    st = data.setdefault("stage", {"idx": 0, "since": None, "ok_weeks": []})
    s = stage_status(data, dkey); wid = iso_week_id(dkey)
    if s["n_ok"] < s["total"] or s["final"]: return False, st["idx"]
    if wid not in st["ok_weeks"]: st["ok_weeks"].append(wid)
    ok = st["ok_weeks"]
    if len(ok) >= 2 and _week_after(ok[-2]) == ok[-1]:
        st["idx"] = min(st["idx"] + 1, len(STAGES) - 1); st["since"] = dkey; st["ok_weeks"] = []; bump_ver()
        return True, st["idx"]
    bump_ver(); return False, st["idx"]

def week_pack(data: dict, dkey: str) -> str:
    """주간 결산 한 장 — 그 주 숫자 · 관문 · 특별편 · 다음 주 · 주간 영상 제목 후보 (dkey 가 속한 월~일 주). 매일 편의 '이번 주 한 장' 재료"""
    wk = week_range(dkey); wid = iso_week_id(dkey); days_ = data.get("days") or {}
    days = [d for d in wk if d <= dkey and d in days_ and (days_[d].get("first") or days_[d].get("count"))]
    head = f"[{SERIES['title']}] {wid} 결산 · {wk[0][5:].replace('-', '/')} ~ {wk[6][5:].replace('-', '/')}"
    eps = [episode_no(data, d) for d in days]
    if eps: head += f" · DAY {min(eps)}~{max(eps)}" if len(eps) > 1 else f" · DAY {eps[0]}"
    L = [head, story_line(data, dkey), "", "[이번 주]"]
    stars = []
    if not days: L.append("  훈련 기록 없음")
    else:
        plays = sum(len(day_plays(data, d)) for d in days)
        pbs = sum(1 for d in days for _k, _s, kind in day_verdicts(data, d) if kind == "pb")
        cur, _b = streak(training_days(data), date.fromisoformat(dkey))
        L.append(f"  훈련 {len(days)}일 · {plays}판 · 신기록 {pbs} · 연속 {cur}일")
        e0 = totalE(pb_before_day(data, wk[0]))[0]; e1 = totalE(data.get("pb") or {})[0]; eb = totalE(BASELINE[0])[0] if BASELINE[0] else None
        if e1 is not None:
            L.append(f"  볼테익 {'—' if e0 is None else e0} → {e1}" + (f" ({e1 - e0:+d})" if e0 is not None else "") + (f" · 출발선 {e1 - eb:+d}" if eb is not None else ""))
        L += ["  " + t for t, _st in weekly_recap(data, dkey)[1:]]
        nv = sum(1 for d in days if val_done(days_[d])); rg, _n = _val_field_med(data, dkey, "range", 7); hs, _n2 = _val_field_med(data, dkey, "dm_hs", 7)
        L.append(f"  발로 블록 {nv}/{len(days)}일" + (f" · 사격 중앙 {rg:.0f}/30" if rg is not None else "") + (f" · DM HS% {hs:.0f}" if hs is not None else ""))
        t0 = prev_val_tier(data, wk[0]); t1 = None; rrs = games = 0; whys = {}
        for d in wk:
            if d > dkey: continue
            t, _rr = day_val_tier(data, d)
            if t: t1 = t
            rk = days_.get(d, {}).get("rank") or {}
            if rk.get("rr") is not None: rrs += int(rk["rr"])
            games += int(rk.get("games") or 0)
            if rk.get("why"): whys[rk["why"]] = whys.get(rk["why"], 0) + 1
        if t1 or games:
            L.append("  랭크 " + (f"{ko_tier(t0)} → " if t0 and t0 != t1 else "") + (ko_tier(t1) if t1 else "미기록") + f" · RR {rrs:+d} · 판 {games}"
                     + (" · 죽은 이유 " + " ".join(f"{WHY_KO.get(k, k)} {v}" for k, v in sorted(whys.items(), key=lambda kv: -kv[1])) if whys else ""))
        for d in days: stars += [m for _c, m in milestones(data, d)]
    L += ["", "[관문]"] + stage_lines(data, dkey)
    if stars: L += ["", "[특별편]"] + [f"  {m}" for m in stars]
    nmon = date.fromisoformat(wk[6]) + timedelta(days=1)
    L += ["", "[다음 주]", "  " + " · ".join(f"{DOWK[i]} " + ("쉼 · 결산" if DAYTYPES[i] == "r" else "보스전 18판" if DAYTYPES[i] == "b" else main_theme((nmon + timedelta(days=i)).isoformat(), data.get('pb'))[1]) for i in range(7))]
    s = stage_status(data, dkey); vt = None
    for d in reversed(wk):
        if d <= dkey and day_val_tier(data, d)[0]: vt = day_val_tier(data, d)[0]; break
    tier = ko_tier(vt) if vt else "골드 2"
    L += ["", "[제목 후보]  (주간 영상)",
          _cut(f"[{SERIES['title']}] {wid[-3:]} 결산 — {tier} · 관문 {s['n_ok']}/{s['total']}" + (f" · {stars[0]}" if stars else "")),
          _cut(f"{tier}가 불멸 갈 때까지 · 이번 주 {len(days)}일 {sum(len(day_plays(data, d)) for d in days)}판 · 신기록 {sum(1 for d in days for _k, _s, kd in day_verdicts(data, d) if kd == 'pb')}") if days else _cut(f"{tier}가 불멸 갈 때까지 · 쉬어 간 주")]
    return "\n".join(L)

def save_week_pack(data: dict, dkey: str, dir_=None) -> Path:
    """기록/WEEK_YYYY-Www_결산.txt. 저장한 사실도 기록에 남긴다 (관문 '주간 결산 N주 연속' 이 이걸 센다)"""
    wid = iso_week_id(dkey)
    p = (Path(dir_) if dir_ else report_dir()) / f"WEEK_{wid}_결산.txt"
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_name(p.name + ".tmp"); tmp.write_text(week_pack(data, dkey), encoding="utf-8-sig"); os.replace(tmp, p)
    data.setdefault("weeks", {}).setdefault(wid, {})["pack"] = dkey
    return p

def week_close(data: dict, dkey: str, dir_=None):
    """쉬는 날 하루 한 번 — 방금 끝난 주(월요일이면 어제까지의 지난 주)를 마감: 관문 검사(두 주 연속이면 단계 상승) → 결산 파일. (파일, 올랐는가, 단계)"""
    ck = close_key(dkey)
    adv, idx = stage_check(data, ck)
    p = save_week_pack(data, ck, dir_)
    return p, adv, idx



# ══════════════════ 자동 코치 · AI 코치 (v6.3) ══════════════════
# "너가 기록을 보고 내 훈련을 조절해 줄 순 없어?" — 두 가지 길, 둘 다 트레이너 답장과 같은 형식의 글을 만들어 같은 길(trainer_apply)로 적용한다.
#  ① 자동 코치: 앱 안의 규칙. 네트워크 없음. 매일 시작 때와 루틴이 끝났을 때 한 번씩.
#     목표 = 평소 범위 위끝 · 넘은 날은 ×1.02 와 위끝 중 큰 쪽 · 못 넘으면 유지 · PB+5% 까지.
#     테마 = 가장 약한 갈래가 두 풀런 연속 같으면 다음 '전체 순회' 자리에 '약점'. 메모 = 부진 신호 · 3일 연속 미완 · 12일 연속.
#  ② AI 코치(선택): 오늘 기록 파일을 그대로 Claude 에 보내 답장을 받아 적용. API 키가 있어야 하고 요청마다 요금이 든다.
CLAUDE_API = "https://api.anthropic.com/v1/messages"
CLAUDE_MODEL = "claude-opus-5"
COACH_MARK = "=== 앱 적용 ==="                         # 답장에서 이 줄 뒤가 앱이 읽는 줄 (앞은 사람이 읽는 코치 노트)
COACH_SECTIONS = ("[오늘 한 줄]", "[잘된 것]", "[아쉬운 것]", "[내일 이렇게]", "[발로란트로 연결]", "[이번 주 흐름]", "[한마디]")
COACH_SYSTEM = ("당신은 발로란트 에임 코치다. 선수는 골드 2에서 불멸을 목표로 매일 코박스(KovaaK's) 20판 + 발로란트 15분을 치고 그 과정을 유튜브에 매일 올린다. "
                "아래 [오늘 기록]은 훈련 앱이 만든 것이다. 기록에 있는 숫자만 근거로 쓰고 없는 숫자는 지어내지 않는다. 앱이 계산한 판정·범위는 다시 판정하지 말고 근거로만 쓴다.\n"
                "선수에게 직접 말하듯 존댓말로. 빈말·과장 없이 구체적으로 — 시나리오 이름과 숫자를 인용한다. 판 수·순서·요일 계획은 앱이 정하니 바꾸라고 하지 않는다.\n\n"
                "답은 두 부분이다.\n"
                "1) 코치 노트 — 아래 제목 7개를 이 순서로 그대로 쓰고, 제목마다 2~4문장 (전체 700~1200자):\n"
                "[오늘 한 줄]  오늘 세션을 한 문장으로 (판 수 · 판정 · 가장 눈에 띈 숫자). 지난 코치 노트가 있으면 그 조언대로 됐는지 먼저 짚는다\n"
                "[잘된 것]  2~3개 — 어떤 시나리오가 왜 좋았는지, 평소 범위·PB 대비 숫자로\n"
                "[아쉬운 것]  2~3개 — 원인 가설까지 (첫 판이 낮으면 손 풀기 부족, 후반 하락은 피로, 특정 갈래만 낮으면 그 손놀림)\n"
                "[내일 이렇게]  3~5개 — 시나리오별로 '무엇을 의식할지' (크로스헤어 배치 · 오버플릭 · 감도 · 호흡 · 판 사이 쉬기 · 첫 판 루틴)\n"
                "[발로란트로 연결]  1~2개 — 사격장 /30 · 데스매치 K/D · 헤드샷 % 와 코박스 숫자를 잇는 조언. 발로 블록 숫자가 없으면 그렇다고 말한다\n"
                "[이번 주 흐름]  주간 결산·관문(단계) 대비 어디쯤인지, 이번 주 남은 날에 집중할 것\n"
                "[한마디]  격려 한 줄\n"
                "선수가 [선수가 코치에게] 에 쓴 말이 있으면 해당 제목 안에서 반드시 답한다.\n\n"
                f"2) 그 다음 줄에 {COACH_MARK} 를 쓰고, 그 뒤에는 앱이 읽는 줄만 쓴다 (다른 문장 금지):\n"
                "목표 <시나리오> <점수>   ← 측정 6개(1w4ts·Pasu·Popcorn·EddieTS·DriftTS·ControlTS) 중 바꿀 것만. 한 번에 3% 넘게 올리지 말고, 못 넘은 목표는 유지\n"
                "도전 <시나리오> <점수>   ← 오늘의 도전 하나 (선택)\n"
                "테마 내일 <클리킹|트래킹|스위칭|전체|약점>   ← 바꿀 이유가 있을 때만\n"
                "메모 <한 줄>   ← 내일 가장 중요한 한 가지, 30자 안팎")

def ai_coach_context(data: dict, dkey: str, ask: str = "") -> str:
    """보고서 뒤에 붙이는 맥락 — 지난 코치 노트(이어서 코칭) · 이번 주 결산(지금까지) · 선수가 코치에게 쓴 말"""
    parts = []
    notes = (data.get("coach") or {}).get("notes") or {}
    prev = [k for k in sorted(notes) if k < dkey and (notes[k] or {}).get("text")]
    if prev:
        k = prev[-1]; parts += ["", f"[지난 코치 노트 · {k}]", str(notes[k].get("text") or "")[:1500]]
    try: parts += ["", "[이번 주 결산 (지금까지)]", week_pack(data, dkey)]
    except Exception: pass
    if (ask or "").strip(): parts += ["", "[선수가 코치에게]", ask.strip()[:1500]]
    return "\n".join(parts)

def ai_coach_split(text: str):
    """답장 → (코치 노트, 앱 적용 줄). 표식이 없으면(옛 형식) 전체를 둘 다로 쓴다 — parse_trainer 는 모르는 줄을 그냥 넘긴다"""
    text = text or ""
    for m in (COACH_MARK, "=== 앱 적용", "[앱 적용]", "앱 적용 ==="):
        i = text.find(m)
        if i >= 0:
            j = text.find("\n", i)
            return text[:i].strip(), (text[j + 1:] if j >= 0 else "").strip()
    return text.strip(), text.strip()

def note_section(text: str, title: str) -> str:
    """코치 노트에서 [제목] 절의 본문 (다음 [제목] 전까지)"""
    out = []; on = False
    for ln in (text or "").splitlines():
        s_ = ln.strip()
        if s_.startswith("[") and s_.endswith("]"):
            if on: break
            on = (s_ == title); continue
        if on and s_: out.append(s_)
    return "\n".join(out).strip()

def note_items(section: str) -> list:
    """'1) … 2) …' 또는 줄 단위를 항목으로 (번호·불릿 제거)"""
    txt = (section or "").strip()
    if not txt: return []
    parts = re.split(r"(?:^|\s)(?:\d+[)\.]|[-•·▸])\s+", txt)
    items = [p_.strip(" .") for p_ in parts if p_.strip(" .")]
    if len(items) <= 1: items = [l_.strip(" -•·") for l_ in txt.splitlines() if l_.strip(" -•·")]
    return items

def first_sentence(text: str, n: int = 44) -> str:
    """첫 문장 하나 (…다. / …요. 까지), n자에서 자름"""
    t = (text or "").strip().replace("\n", " ")
    m = re.search(r"^(.+?(?:다|요|죠|니다|습니다|세요|네요)\.)", t)
    return _cut((m.group(1) if m else t).strip(), n)

def _next_plan_day(dkey: str):
    """다음 '계획이 있는 날' (쉬는 날만 건너뜀 — 벤치 날도 코칭 대상)"""
    d = date.fromisoformat(dkey)
    for i in range(1, 8):
        nd = (d + timedelta(days=i)).isoformat()
        if day_type_of(nd) != "r": return nd
    return None

def coach_for_day(data: dict, dkey: str, today: str = None):
    """달력 칸·이번 주 줄에 적을 코치 한 줄 → (표식, 글) 또는 None.
    그날 노트가 있으면 [오늘 한 줄], 직전 노트의 다음 계획일이 그날이면 [내일 이렇게] 첫 항목, 오늘이면 트레이너 메모"""
    notes = (data.get("coach") or {}).get("notes") or {}
    n = notes.get(dkey)
    if n and n.get("text"):
        s_ = first_sentence(note_section(n["text"], "[오늘 한 줄]") or n["text"])
        if s_: return ("코치", s_)
    prev = [k for k in sorted(notes) if k < dkey and (notes[k] or {}).get("text")]
    if prev and _next_plan_day(prev[-1]) == dkey:
        its = note_items(note_section(notes[prev[-1]]["text"], "[내일 이렇게]"))
        if its: return ("내일 이렇게", _cut(its[0], 44))
    if today and dkey == today and TRAINER.get("note"): return ("메모", _cut(TRAINER["note"], 44))
    return None

def latest_note(data: dict, upto: str = None):
    """가장 최근 코치 노트 → (날짜, 노트) 또는 (None, None)"""
    notes = (data.get("coach") or {}).get("notes") or {}
    ks = [k for k in sorted(notes) if (notes[k] or {}).get("text") and (upto is None or k <= upto)]
    return (ks[-1], notes[ks[-1]]) if ks else (None, None)

def coach_note_path(data: dict, dkey: str, dir_=None) -> Path:
    return (Path(dir_) if dir_ else report_dir()) / f"EP{episode_no(data, dkey):03d}_{dkey}_코치.txt"

def save_coach_note(data: dict, dkey: str, note: str, apply: str = "", dir_=None) -> Path:
    """코치 노트를 기록 폴더에 한 파일로 (업로드 팩·썸네일과 같은 자리)"""
    p = coach_note_path(data, dkey, dir_); p.parent.mkdir(parents=True, exist_ok=True)
    body = f"AI 코치 노트 · {dkey} · {story_line(data, dkey)}\n\n{note.rstrip()}\n"
    if apply.strip() and apply.strip() != note.strip(): body += f"\n{COACH_MARK}\n{apply.strip()}\n"
    tmp = p.with_name(p.name + ".tmp"); tmp.write_text(body, encoding="utf-8-sig"); os.replace(tmp, p)
    return p

def _cycle_theme_id(dkey: str) -> str:
    d = date.fromisoformat(dkey)
    return CYCLE[(_train_ord(d) - _train_ord(date.fromisoformat(CYCLE_EPOCH))) % len(CYCLE)]

def _next_vday(dkey: str):
    d = date.fromisoformat(dkey)
    for i in range(1, 8):
        nd = (d + timedelta(days=i)).isoformat()
        if day_type_of(nd) == "v": return nd
    return None

def auto_coach(data: dict, dkey: str, plays=None, dt: str = None) -> str:
    """규칙 코치 — 트레이너 답장 형식의 글. 정할 게 없으면 빈 문자열"""
    if BASE_DATE[0] is None or dkey == BASE_DATE[0]: return ""
    plays = day_plays(data, dkey) if plays is None else [tuple(p) for p in plays]
    dt = dt or day_type_of(dkey)
    day = (data.get("days") or {}).get(dkey) or {}; best = day.get("best") or {}; pb = data.get("pb") or {}
    L = []
    for k in PROBE:                                                     # 목표: 측정 6개
        band = scen_band(data, k, dkey)
        if not band: continue
        cur = TRAINER["targets"].get(k); b = best.get(k)
        if cur is None: t = int(round(band["hi"]))
        elif b is not None and b >= cur: t = max(int(round(cur * 1.02)), int(round(band["hi"])))
        else: t = int(cur)
        if pb.get(k): t = min(t, int(round(pb[k] * 1.05)))
        if t > 0 and t != cur: L.append(f"목표 {sname(k)} {t}")
    nd = _next_vday(dkey); bd = bench_days(data)                          # 테마: 약점이 두 풀런 연속 같으면
    if nd and len(bd) >= 2 and TRAINER["themes"].get(nd) is None and _cycle_theme_id(nd) == "mix":
        w1 = weakest_link(data["days"][bd[-1][0]].get("best") or {}); w2 = weakest_link(data["days"][bd[-2][0]].get("best") or {})
        if w1 and w2 and w1["sub"] == w2["sub"]: L.append("테마 내일 약점")
    memo = []                                                           # 메모: 신호가 있을 때만
    V = verdicts(data, dkey, dt, plays)
    if V["recent"]["state"] == "down": memo.append("요즘 부진 신호 — 내일은 워밍업을 두 배로, 본훈련은 점수를 보지 말고 감각만")
    tds = sorted(d for d in training_days(data) if d < dkey and day_type_of(d) == "v")[-3:]
    if len(tds) == 3 and all(len((data["days"][d].get("plays") or [])) < 20 for d in tds): memo.append("3일 연속 20판을 못 채웠습니다 — 오늘은 측정 6판만이라도")
    cur_st, _b = streak(training_days(data), date.fromisoformat(dkey))
    if cur_st >= 12: memo.append(f"{cur_st}일 연속 — 이번 {DOWK[REST_WD]}요일은 꼭 쉬기")
    if memo: L.append("메모 " + " · ".join(memo))
    return "\n".join(L)

def ai_coach_request(report: str, key: str):
    """(url, headers, body) — Messages API 원형 HTTP. 거절 시 서버가 다른 모델로 이어 답하게(fallbacks) 둔다"""
    body = {"model": CLAUDE_MODEL, "max_tokens": 8000, "system": COACH_SYSTEM, "fallbacks": "default",
            "messages": [{"role": "user", "content": report}]}
    hdr = {"content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01",
           "anthropic-beta": "server-side-fallback-2026-07-01", "User-Agent": "AimDesk"}
    return CLAUDE_API, hdr, body

def ai_coach_parse(j: dict):
    """응답 → (답장 글, 오류). 거절이면 (None, 이유)"""
    if j.get("stop_reason") == "refusal":
        return None, "코치가 답을 거절했습니다" + (f" ({(j.get('stop_details') or {}).get('category')})" if (j.get("stop_details") or {}).get("category") else "")
    text = "\n".join((b.get("text") or "") for b in (j.get("content") or []) if b.get("type") == "text").strip()
    return (text, None) if text else (None, "빈 답장")

def ai_coach(data: dict, dkey: str, plays=None, dt: str = None, key: str = None, timeout: float = 180.0, ask: str = ""):
    """오늘 기록 + 맥락(지난 노트 · 이번 주 · 코치에게)을 보내고 답장을 받는다 → (성공, 답장 또는 오류 문구, usage). 네트워크를 타므로 GUI 는 스레드로 부른다"""
    key = (key or "").strip()
    if not key: return False, "API 키 없음", None
    url, hdr, body = ai_coach_request("[오늘 기록]\n" + daily_report(data, dkey, plays, dt) + "\n" + ai_coach_context(data, dkey, ask), key)
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=hdr, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r: j = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try: msg = ((json.loads(e.read().decode("utf-8")).get("error") or {}).get("message") or "")
        except Exception: msg = ""
        return False, {401: "API 키가 틀렸습니다", 403: "API 키 권한 없음", 429: "요청 한도 — 잠시 뒤 다시", 529: "서버 혼잡 — 잠시 뒤 다시"}.get(e.code, f"오류 {e.code}") + (f" · {msg[:80]}" if msg else ""), None
    except (urllib.error.URLError, TimeoutError, OSError) as e: return False, f"연결 실패 — {getattr(e, 'reason', e)}", None
    except ValueError: return False, "응답 형식 오류", None
    text, err = ai_coach_parse(j)
    return (True, text, j.get("usage")) if text is not None else (False, err, j.get("usage"))

DAY_WORD = {"v": "훈련하는 날", "w": "훈련하는 날 · 약점 집중", "b": "실력 재는 날", "r": "쉬는 날"}

def verdict_sentence(V: dict, pd: int = None):
    """오늘 탭의 판정 — 타일이 아니라 문장 하나 → (문장, 풀이). 자료가 모자라면 '판정까지 N일' 대신 무엇을 치면 되는지"""
    Vd = V["day"]; st = Vd.get("state"); num = Vd.get("num", "") or ""
    cap = "어제 같은 판들과 비교한 평균 차이"
    if st == "up": sent = f"● 오늘은 어제보다 잘 나와요 · {num}"
    elif st == "flat": sent = f"● 오늘은 어제와 비슷해요 · {num}"
    elif st == "down": sent = f"● 오늘은 어제보다 낮아요 · {num}"; cap += " · 하루 오르내림은 정상이에요"
    elif st == "wait":
        pd = pd if pd is not None else 0
        sent = (f"○ 재는 중 · 오늘 점수 재기 {pd}/{len(PROBE)} — 다 치면 어제와 비교해요" if pd
                else f"○ 아직 안 쳤어요 — 손 풀고 점수 재기 {len(PROBE)}판 치면 어제와 비교해요"); cap = "첫 판 점수끼리 비교해요"
    elif Vd.get("colk") == "rank": sent = f"● {Vd['word']}" + (f" · {num}" if num else ""); cap = "코박스 종합 점수 기준 예상 등급"
    else:
        sent = ("● " if Vd.get("colk") in ("up", "flat", "down", "gold", "rank") else "○ ") + str(Vd.get("word", "")) + (f" · {num}" if num else "")
        cap = Vd.get("cap2") or Vd.get("cap") or ""
    r = V.get("recent") or {}
    if r.get("state") in ("up", "flat", "down"): cap = (cap + " · " if cap else "") + f"{r['word']} {r.get('glyph', '')}".strip()
    return sent, cap

def routine_complete(day: dict, dt: str, dkey: str = None, pb: dict = None) -> bool:
    if dt == "b": return all(day.get("best", {}).get(k) is not None for k in tier_keys())
    if dt != "v": return False
    main = main_theme(dkey, pb)[3] if dkey else MAIN
    need = {}
    for k, n in WARMUP + list(main): need[k] = need.get(k, 0) + n
    return (all(day.get("count", {}).get(k, 0) >= n for k, n in need.items())
            and all(day.get("first", {}).get(k) is not None for k in PROBE))

def val_done(day: dict) -> bool:
    """발로란트 블록 숫자가 적혔는가 (사격 + DM). 루틴 완료 조건은 아니다 — 리본 칸과 주인공 줄의 '발로 ✓' 에만 쓴다"""
    v = day.get("val") or {}
    return bool(v.get("skip")) or (v.get("range") is not None and v.get("dm_k") is not None)

def fmt_val(day: dict) -> str:
    """'사격 27/30 · 드릴 ✓ · DM 24/18 (K/D 1.33) · HS 31%' — 적힌 것만"""
    v = day.get("val") or {}
    if v.get("skip"): return "발로 블록 건너뜀"
    parts = []
    if v.get("range") is not None: parts.append(f"사격 {v['range']}/30")
    if v.get("dm_k") is not None:
        kd = f" (K/D {v['dm_k'] / v['dm_d']:.2f})" if v.get("dm_d") else ""
        parts.append(f"DM {v['dm_k']}/{v.get('dm_d') if v.get('dm_d') is not None else '—'}{kd}")
    if v.get("dm_hs") is not None: parts.append(f"HS {v['dm_hs']:.0f}%")
    return " · ".join(parts)

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

def close_key(dkey: str) -> str:
    """쉬는 날이 마감하는 주 — 마지막으로 '다 지난' 주의 일요일. 쉬는 날이 월요일이면 어제(일요일), 일요일이면 그날"""
    d = date.fromisoformat(dkey)
    return dkey if d.weekday() == 6 else (d - timedelta(days=d.weekday() + 1)).isoformat()

def recap_week(dkey: str):
    """리캡이 보는 주 — 쉬는 날엔 방금 끝난 주(월~일 전부), 훈련일엔 이번 주 오늘까지"""
    return week_range(close_key(dkey)) if day_type_of(dkey) == "r" else week_of(dkey)

def recap_label(dkey: str) -> str:
    return "지난 주" if day_type_of(dkey) == "r" and date.fromisoformat(dkey).weekday() != 6 else "이번 주"

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
            "projected": projected_energy(data["pb"], tb)[0], "n_today": sum(1 for k in tier_keys() if tb.get(k) is not None)}

def bench_lines(r: dict, dt: str):
    out = []
    if dt == "w":
        lr = f"지난 풀런 {r['last_run'][1]} ({r['last_run'][0][5:7]}-{r['last_run'][0][8:10]})" if r["last_run"] else "지난 풀런 없음"
        names = ", ".join(sname(k) for k in r["week_pbs"][:4]) + ("…" if len(r["week_pbs"]) > 4 else "")
        out.append((f"내일 벤치: {lr} · 이번 주 PB {len(r['week_pbs'])}개" + (f": {names}" if names else ""), "sub"))
        if r["closest"]: out.append((f"가까운 랭크업: {r['closest'][0]} — {sname(r['closest'][1])} {r['closest'][2]}점이면 {r['closest'][3]} 칸", "gold"))
    elif dt == "b":
        t = f"{r['n_today']}/18" + (f" · 예상 {r['projected']} (빈 칸은 PB)" if r["projected"] is not None else " · 18개를 다 치면 에너지가 나옵니다")
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
    wk = [d for d in recap_week(dkey) if d < dkey]; lbl = recap_label(dkey)
    days = [data["days"][d] for d in wk if d in data["days"] and (data["days"][d].get("first") or data["days"][d].get("count"))]
    if not days: return [(f"{lbl} 기록 없음", "sub")]
    plays = sum(sum(e["count"].values()) for e in days)
    out = [(f"{lbl} {len(days)}일 · {plays}판 · PB {len(week_pbs(data, wk[-1] if wk else dkey))}개", "sub")]
    ser = probe_series(data)
    if len(ser) >= 2:
        last = ser[-1]; prev = next((p_ for p_ in reversed(ser) if p_["date"] <= (date.fromisoformat(last["date"]) - timedelta(days=7)).isoformat()), None)
        f = lambda v: "—" if v is None else f"{v:+.1f}"
        if prev: out.append((f"지수 7일선 발로 {f(prev['maV'])}→{f(last['maV'])}", "sub"))
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
    """그날 설치할 플레이리스트 3개. 'AIMDESK Day' 의 본훈련만 날마다 달라진다."""
    return [("AIMDESK Day",    WARMUP + [(k, 1) for k in PROBE] + list(main_theme(dkey, pb)[3])),
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

ICON_B64 = "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAIGNIUk0AAHomAACAhAAA+gAAAIDoAAB1MAAA6mAAADqYAAAXcJy6UTwAAAAGYktHRAAAAAAAAPlDu38AAAAHdElNRQfqCRIPHiqIrd4VAAAbtElEQVR42s2baawc15Xff/dWVVdvb+V73HdS4iqRkkiKi0iRIjVyJBvRjGKP4nhiZCaTzEyAAEESJIN8GCCDQZDB5EMyS+A4M1m8BmPZsrzJFmVai2lbkmnT2riai7i9fel+3VV1t3y41f36kSIlSwSSCxRes9lV955z/mc/JbjJeu7b3+bhRx/lIx97sm9odHynNvZh59xOYLm1ZtA5V+D/oyUQRgZyHMRlIfiZlOJwT1f1xX/1+5++8rPXT9g/+qM/vMl9Hcs5xxvHj3PX1gf4h7/96d4TZ859NM3Up40xO6zR3UZrrNFYa3Hu/zXJNxIipEQGAUEYEgRhIoPgrSgMv7x44eCXn/nK/7703PcOu4d/7RBCiDn3tYkXQuCck4987Ml7hscm/p3W+lGVJnGWJCiVdRDu4AMy4P3cJt7Hb979Rn+nlJIwConjIlFctEEYvdZdLf/J7/32J5/91D/4zaxFa3uvDuLDvYcef3S6PvMfVZauT2ZmSNMUa+1tk5SUAnkTCp0D6/x5bsteQhAVIkqVKlFcHC3G8X948jce+8y//Bf/bKZFc+ic40//7D/jnJMPHHr80ela/S9UmiybqdXQSrUl1gmbX3W1NosjQSESiFswQBtHkoG17kPtCWCdI00ztJ6iXNEDzrl//6Wnvhl+/gv/578IIRLnHCJJEorFIoce+8R9w6Pjn8+S5vr69DRa6w9NeIsocBQLkmJBIIVAyvb/0gl4ax3WgdKORupwDj7k9m00SSmpVKsUK9XJarn8B0ePPPPlb37rWSfu2/0wG9fd0fv622f+Ok2bv1GfmkIpdVuIbx0gkIJKSRJIqMQQF4IbKHPOkSnLTGIxxtHMHErfnjO0zxFIql3dxOXKW4P9fX/v+R+8/Hb406PPIWT4UW30Y8nMDPq2Eu//FkKv96F0DN61mU/+2l0MFgUO1/5RMpPx8tMvcfjMMA3tiALQZlZ9PvQSAmMszcYMQVTYOD459Y//+s//5N+Ej3z0E31XRyY+rdIkTtPUg/I2cR289KNIIIC4u8qmT3yCxx8oUs2ugNFeC8IqmBKr3jrH2+dHOJ1ZAikIpGfC7VgCv5VSmixpEITRE5/9/FNfkEOjEzutNduzJLmt1r4l/agtfUvP3Vs5ePdiKslVbDKFVQrrihjtMNKwcvty9nSXiQKHwxGFXlNul1fIPR1pkmKNXt5spo9LY+3D1ugepbL2j24TC5BSUAi99AvVMhsfPsD20ihkMzjZjQt7cQgwGWhFedNCHlq/iMVRgEcPBPLDnuPGZYxGq0xYx0ekc9xvtL6t0m+tQugtfiAsXZvv4uF7l9GvR3BRPwRdYBWYFJzzul4NWbd3VY4CEHhbcDtRAP5ZWimcc5slghXWmNsa2jrnpR/l0o+rRdY/fJD7uxMgxBGA1WAUzrkcBSnojMrmhRy6Yz4LI4nDEQQQ3C5Q0lIDsEYjBCXprJ1vreEDx7ZzCJ+r+2EAkbR0bdzEwe13MGAmsEaDTnLCAWc8M5z2KOgpsH73cnZ3lYlCkNfZgs49Psyy1qNO4lzk3Aen37UIxx9SCkcYCEoFQSAgrsTccfAgu3sakE2BzTzROLAKZ7OceRpnFc4oqlvmc3DVAAuiACGhEEIYgBR+D8+MD8eIlguWHyL18JFaB+FS5IYvEoSBIAwc1TvX8dD9d7JAXcUZlR/cwx9nEXns73SCs9ofqidi445BdlSKnnAJceTtiWeCy69Z5n/Q9YFsbIv7Ij+MFOQhriAIBMWCj/qKpYhVBw6wpy9B6Bl/UKtzw2dz9JiccO/wnW5ikzG6NpY4uKyHgYJEiBYKWkzwe7WYIPgAaHA+V/iVGdAivC3xPLZvXYXQu75IOsqr17Bv12YWmWGsUWAzL33n2oQ7qwHnVSCbxiXjYDJEX8ime/u4rxwTBp7JceT3aLlHKUQHIt6bCc45jDForUjTlDTNfjUGzJG6FPlF+28ghU94JMTFkGX7H2LvoEKmE173rZkl3iT5iYU3is1RyKZxzmKNRauMyvqIhxZW6YskQjgKoSBsMbuT8UIgb8KEFtFZluVEp2SZwhiDc47wfaIFOiQv8s09/ETOFNGWfiAcxZUr2bNnC0vVeaxOQPjY3+UWH+Erak7VcKoBxofhxmisyrCmCV0pmzYV2Xot5gWT4BwUIkGqnLdcApzz0Z21AglYnM8qrcVa2yb0ZnHEezLg5sTPcl3kNqBYkEgpiAuCxXv3s39QETYmMADWeCuP9Sc3KU7NgK4DYJ3FaIXVKU4nWJNijaK8Dvb/oszP05SpzFEIJcb4wglO4MA/UbTgbdDGtt1ca3VGuJ3fvzcC5ui8QOSQa0ld5n+j0F+hcMRLl7Nrz1ZWmMtYq3DWeKm3OKpncFmt/U+rFUYlOJ3iTILRGcYonLOIPti0rsDmkZgfmRRaKMi8JbbGoI1Ba5tL3n/vESLes6ZwSxvgbkG8FLSJlxKKBZ+9FQqC+bv38eBCCNIxrMnaxDurcekkZJMEwvjSmNWgm6BnsHoGrTwDWv5Na015rWFff5FqANZqcAqtU1SWorXCGoPAo1G2zygQ78NBhu+HePEuxHfagZb0A+EoLFrMjr3bWGUuYdRMW4UwTVw2jbCKa2MJvzg9hdIWZw3ONFg+IFi1QHgDicAZg1HaE9dr2bzCsfaq48cqBTtbV/REC6wDmdsCIR3SgkW0XeTNUCBvRby4TuevJ17mm/sgxef983buZf8SSdQc8rpmDS6bmnVvwnH81ATfODrO5XHD2YsjHHltgsOvTfrYwIHNMnTSxOoEZ1O0nqG0aoYHuwtUAiD3CEFHdDj3XKLDNt3aRd4UAQJ3na67WSbI2Y2jAAqRJBCOeP4C7tt3P3fYS1ibeb+fTrUtvLMWqxUqS9m6cZB/8uvLSUcc331lmrfP17FGobMUqxXgLbnRGc4Y6Ictq0psmIz4qcmQwmeKmQOJwOKDGuvErOBwOQq8u303JNyAgFnpd3LWtQ3eHKZIQRxJZB6p9e7Yzf5lBQrNIWw2jUvG5rg3nSVeLXQzd11eBbTOyJImKqljVYpzFqP97632SZJBU1zVYF93kXLoqYjCFjrdHKlfj1pxi3D/XVXAG5RZQjt9/awt8ElPS/ejefPYsncX68x5zMwVyKbBGqyzaJVisgZW1XCqjsqaGK18PcB5L2Fy3+acw6gMo3y4DKCVJksUujdhyzJYG0UI4QsmrXpBKyTuhH3ndzeLFm9gQKf0O2+cfZBoc7yQJyhRAD333s+BFSHFqbfbEm5J3WY1bDaJzaaxWc37eTu32OeNmsEo7//9/ZYszfISvUNLS2F5g73VmDj01rVVcutE6Q1CuwUKbmRAp/QRcx/asVEQ+KhP4oj6etm0bw8bzFlMNu2lniXotIZNx70RzGaYnGrw6okGL7/RROmWzvnr9XMpLx6fYWTKF0qt0WRphs0juUxbmomm2dNgyyJYHUWQoyAMZm3TrLA66ZgrzJsawZbUPSP8Da10eVYdfJDRKndF0lHdsp0HV5cpTZ9BqaaXok7ANMFmDI8nPPdajeePzTBRd/R2xxxcKLEqQRSqLFkEpUqDzx6eIURz72p4aDMs7QfjIFU+ugMw0hAtqbPnSpVfKkVmPApa1eMWQgUC4TrOnQdH1zuDNgM6ezSixbI5sJ/9HOS6j7WI7gpr9z3AZnOKrD7kIzrTxJkUozN+/Ead//HsBPVU8pE9y3hoz2pWrVxIuVL2EWTfKnYtcdy7K+HKlVGOvnqOr3//HD/+ao3H7hXsvtMSSO8ejXWkypB017l7sMKKRsQpowikrz8o42ah73KJd6o1NxqBuQiAG2HTwQScwzqHkA6tAKEpbNzDg2urFMffRKV1sAnWZKg046svTfGl56fYu20hv/Ob97JyzXIEYJJp7MwwTqeAQwQFokKZNWuWsnbdKh59eJi//foxPvfMac5eNXx8F0SBIVPW7x8KelYm7B4ucV4plHFEgUeBa1EiHDjRId5Z4XbyIOwkfo6d6PhsjcFoC1ikcBQDibMQ9lZYt38/W81JdP2SL2boDKMVX32pxucPT/O7T6zjySd2EpdKqOmrmPowTicIrD8neUcYgQoKBKV++vuX8k9/5xDr1wzwx3/1Kp97cYaP77QUQkcQBpTLRWQXbLsY8EIj5JzRyEAQSIE1ue634P8uavDuCBCzdtI5hzUWY03bFUnpLX8c+4wvFJbypns4sKGP6th3ybIaRmuEM7xyoskXn5/id59Yx2/9/X1gNcnQW7h0CikE2jomphRT0xprHdVqSH9vRElkmPpVbDJJ2LeSAwe3EYaSf/tnRznyZoOPbQ8ol0sEYYATMHCnZdfVmHeURnfYAtep6aKjZpYbAXEjA/L82Vmcs75W10qCOvr5rYqPEI6wWmLtQw9xjz2Jmr6EVhnCOcZqhr/5ziT77lvAk0/sBKvJRk7gdANr4fjJaZ4/MszJk1M0pn2NMC6HLF9R4cF989l5Xx8lmqjR0+DW8sDerfz+5Un+4vO/YNv6Aut6AkBQLMWU1kXsPg0vNhIuGdNup1mTm7DriG1zQXSkw0pr0jQjTRMEs/G9N4Rzb21FXgGW0oa7eXDTfKoj3yNLG+0dv/dajZlU8DtPbqNYKtEcegunG6TK8bVvX+UbT79DOqUoB5KS9PW+rJHx5rUmb/x8nGP7FvDpT65goAfUxDlkVOLxx7bxg1eu8OyxCdYtK9BVLRJGIUIKlm6S7LwU8zXVQBtHGAq0cW2j3qpWX0d3e0mlZstDt6qv+kaHDxuicpFVDx1imzuBmn7H5/TGMDbR5PljMzyycx4rFpXJpi7j0imsha99+ypf+dJ5grphZTlmc28XuxYNsmfxfLb097CmWqLHSl4+fJX//r/OUWtYMClq8iKVInz80CLODgnGGjFxHOXeKKC8IWLfkhLzg7yRkpfJbkrJreKAW60w8PAKhCVet5kDW5fQP36ELK/1CaM5eyVjcgYe3NqFmjiLNd5uHD85zTeefoeygeXlItsWz2f7soX0l4tIGVDPFK9fHebo+SvImQavvDTMuju7+PW/swjbHCdJp9iyKmJ+X5Hjv1RsWhUjg5AgDBElWLslZselIs/oGYxxhAGom3WVr+PMezCgFQv4qA8gKhZYuu8AxbM/5ftvnkCnTaw1SCF44fWE3q6IZfOLOOvtiLbw/A+GSacUK8sx2xbP5yP33UVx2SrSsQnUqRNUooAHVi0lDkO+ffIc9VqD739/iAd3D9LfE+KMprssWbe8xJGfTzHYVyAIdJuWsgrZ1l/kh80mQ9q35KWAfMbFo/sm/YNZBuRKM+dH+Xe+OSGQWOK167h/01K+85dfYfG8Xnq7F+ZdFli5XrBFjnHx7Cmq1QqVapl6GnHy7SkqgWSwGLN96QJKG+5G7tpPsdEk+5vP0DhziqK13LVokDevjjCSpFy73ODU6VE2ry2Qpd617rurSP+iZUwImRcFBdpYXjv+Dr+3tMD2sSLfyhreRQctW3C9GZzLiTmRYNtwOOerrfm9hcibkygOWbb/IDuiC7ytx3nyka2sXlqh1VgWUnDx5AynXx9mbMRHjEPjIVPjlu4goC8MKU7PUH/lVaLUYptNzPA1QJBN1giTjEEpKQYBJk05f3aYZb0xJq/zbV4xyMGDK+dEqc3UcuXKKJVNIQeGHUdnEkaNJWwZcuvmCvQ6LQivZ851o5N5NyaX/sp17Nm2lnnDXyRt1miOnCWLY2weWgkhUPWhdgXWz/1onMuHo4BmvYE6c4b4/PlZ9ywFWaZI0gyZq47ANzDJgxgH2KxOOnpyTr6SJJasUUf2D7Dx7jL3XKrxnPLZaNgas2kJlVvkAm0U5BHkbJdXeukXQhYdOMSu0mX0+GmSzPLK2zNcHs3yEnUeZqaGqOOB5SKEBchmLOOZ4uTkNN1hwIruLqJAIgpF6Oll6Pw5JhpNLmeKzDoIBN3dss1IIeDisOYnv5yaQ0SmHGPTGiGgd0uJQ8eqvNpIGTPOo+B6kb+3EXR5vd0RSN/jk85RWL6KPTs3MHjty0ynk9y3Cn55YZxzFyzGeKmduOxIM80/fzQmkgZrNYG0VLok09OWca25ogIC53inVqevGBMYR00ZJpoJo9owpDR1bYirgnLJ5vOCkjCK+M6rdX50usn+rV1I2UIZ3LeuSn93TNATcffdVbZcrvF9lYCjnSTNomBuTjgnF2h1Wl2r3pdb/jCSLNp3gD2ly6SnXkdieWxbgNEGrX0tPpBw9ITlM885GvSysKqZmRojU4aBQcPI1QJjmeK8lATAfOeoZ34izTjHpHWcVYqRTFE3hhWLpW+U2JgojjFhF2eu1XhkRy9/8PhgG6FCSqSUgLdZvVtKHDxW5bVmyoTxHmE237hxhTfKX+SzfZJQgnCWeMlKdu/ezIJrf0uS1nDOoTLty1j44cY0NSzusxQjwfEzCSv29NCoT9JdcaxeqhgZNYxd8oxOnWMkDOiREgHUnWNUG0YyxXCqqAwI7lovWTgQ+3Z7scxbF5sMTTq2b6jQymqlDHJ74wuezoIcDLhnc5XNV2u8rJLcjvkJVJy4oSR2IwOcw+WdHoAwFCzYu58HesbQF97EGINSszNFxjoyZTDW0VtxbF0JL72Rsm+LpVTpxpkJlgyG3L1B8XMLI1ehYSxjYUAx8AxIraOuDXVjqAwI7t8u2biqSE81IohinCzw7CujLF9YYuOKIjgfBbbGXeYMS0hB710FDv6szM+aKVN5XAC+He4N1Sy971oUDSSE0rM5XrSY+/fdx6Lhl2nWxsgy37ICyLQlSTXaWD94pC071iiSBnzn6DRxuYcoLlEtS9YsDdi+JWP1BoWpaoaM4mKSciFJuaoyGrFm8VrLgb2SbRtKLBosIYOQYqWXH71V54UzIU/s76OrEiHkuxNvrSVppCRdinvWldgYFyAfpgiDtoRvjQAxR/owuHc/e/snSX/6KkophBBtqWvj2s/0ZSvD4krIR+aV+Z9HGyxbNM3eu+czNT5EFwlrl0n6uzUjywxjk4JG0xNRjB19PY75fYI7VlZZOOCJL3X1c+Fawp9/ZQi39RArtwVILmNakHezfltrQ9pM0NqAgK71kkNvljneyKgZ784z7eOb6xlgfbF7VvpRIMBZ4gULuX//DpZcfYZGfQwQZNqSKeN9NKCNbasAEsoTFVxNMJ1q/uu3GhRCwY6NC2jUJpGNGosGBAO9jjSz+YGgEEoKkaQQATZDBH2Ue/q5cDXhjz93jbNXFMt2hLxQ3sWaxlN+xoCW7juyVPnhx1wtVaZQXSlbV0dsHI34cZb60fhAtIuxrVhFCinHRF5O9aMoIvcAMLB7Lw8O1jFXfoqxliQzpJlpwy5VhiTzxEspqUZlmpcqHJ6YplR0TDYkf/rUDE+9MAlRD72DiyhVuikWC3RXI+b1RAz0RnRXQ8qliGK5SrGrHyUrvHx8in/9mSsc+6WhvzfG/eLHvHgh5lK0pA1jYwzNmSZJM2nPACTNhKTRJLMasTRjf0/JN1JcPnPYgXQhJCGOS0EQDAIds32OeHCAHQd3sXzkMLXpEdKc0JbhS5XB5JXaMAopV4pUR6p8/VzK+UxRiGOKsaTWFHz2exmvnBrlse0l7l7bTc9Ar+8I5eLwr7gENFJ440KTw8cucfSEo6kk/d2Rz+4mJ7n8wg858lv38SkukWWKtJnmnsh3kfMRWNLMMjGV0nApGxd1s24i4pjKkML3E7UBGQSAM6Fz9lgQRvdIKSmELu/3OQZ27ubBxYrmKz+imWS0tCTTFqWML04KQVyMKZViIkImT4U8NzqOFRIpAoyBUiHAuoBfXHC8fqHJkv4G65YG/N0HF7JlTYxJprk0avnaS5O8eVFzfhgSLSnHId0VibG+NI6VZK/9kCMPPcADXf3MmzmPbatAhsoyjLHUG5qJySZJkuKco7Kgyf7LJd5OFM3MN1WNhTCKcI7T0hhzWAZhMy5Es9Kf18e9h/aybOhl6hPXcOSj5qkmUxrrfHGyWi1TqZSQoSQcifjRmYQzaUYYhFgn0DYfBg8k3ZWQUqnA1amIZ3/meKexgLWbtrByxXzquswzr1pOD4UEYYGeakQhktj8DRKlfatbjY1x8cWf8FLh3tzraJqNBlmakmWGsYmE4ZEazaYfpLDWMRJNs3nQsjb2jRQpHHEUEEYFrLWHZZYkLyDEG5VqyY+2B46BnQ9wcKXAXjwKGKy1ZFrjnB9jL5djenuqlMsxYSAohwWa5wp8d7iGFgIpA5QBa2ffA/LhvaBcDKgUJc5BZiDJPCSLsaRaDAhD0e4BWOufkSr/ObOC5Ccv8eLEYq6FA6jmDNYYmolmZGyGqakZnDEEwvnOUjMhNSkM1DnYU6SUe7dyuYCQwajW6qlw0YqVVydGhr9YLpa2CZOIMAzoGuxn9Iff5cIbl2kmqu3uAKJCSDEOEEIDmrAQUspC3ni9xokkJQwjL33jszzrRD7E08rMfd/um0fOcfyta2TNGhM1gzHg5Ow+PixvFTIcmRAEUpIND3Pu2SM8vbrC6qEajcxRq2VkmW+pAxhtUUq1X9c5ZWpURUx3KEgNxMUiqTHPTYxce0UsWbMVY+zCef3Vp9DJbpVMU4wFRqVMTdVJ0sx3VDpy8HbMwGz11TqBkyGFQoyxEuP8gYWUyM5X1PLfG2vx2a7PfQPZar7MBmrtAMf5OcFSAZyzFGOBtZbJySmfiN0wDHPdv5wjCkIKxTJBoUpUqg5PTtU/NfTOqSOBDCusWTlYT5rplagQPWKMrTTqTZqJJskM2oB1Euu8NI297mp97yRBECJEgDLCB5lC0u4mtgjLfbhvuuazPGLWp9s8yLG55PNaSKsA5KvImUVrg9LePrTOMHvJGy5tQYYxxXJFp2n6V5fPn3wa0EHamMA5yfDl8+cq3X1ZEEX7rHVRmvo8XwbhrS+ZX0EABGTGz+61GnKtyKslzc7Q1XVctiOsbdUlZr/zjDCtyBP/Zpl13t681xmDIKRYrlAsVVym1NNDV975S6N1DcgCgNr0JGvuesBdPPvW62FcTWRU3A5BUWubI+Ddudp5GStRJidYyLZUWyduDzW7uTH8jZdrG88bGGIh0w5lHMY6jH3vcwkZUihViYpdOlP6qyPXLv2nLGkOAwmQXl8xlDKIK4OLVz9eKJb+EGc3ZEmTNE0xRrerq7dcogVvOafd3hl+tu3BzbV2LmI6DWPOlc43zm48gkAGkkIhJi6WEEE4nKXN/zY+dOELKm1MAynQeDcG5MpLOG/h6jvLXb3/KAjCJ5yzS43KpFIqf3m6NYXpbrhdiNZfccODW1TfbGLHdXy4OZ9d27pfPwkqpCSQAUEUEUYFpAzGrLXPJY3aZ0cunznmnLEtDQIywL7bWVrYdaXqvLB3YPHGKC4+HgTBo0KIu4QQJefsrdHwPl+8urF5/Sus66TfYoBzzjjnTltrn9cqe6o+Nf7K1OjFBtBOiPGO2QH8X7EURtTNAAP1AAAAAElFTkSuQmCC"
# ══════════════════ GUI (v2 — 커스텀 위젯) ══════════════════
# 판정 색 — up/flat/down 은 히어로 '면'에 깔리고 글자는 onfill. 빨강(val)과 온도를 달리해 '발로 그룹색 ≠ 별로'.
VERDICT_C = {"up": "#4ED490", "flat": "#8CA0B3", "down": "#F0654F", "onfill": "#0B0E11", "up_bg": "#122A1E", "flat_bg": "#1D242C", "down_bg": "#2A1512"}
VERDICT_C_BROADCAST = {"up": "#63E6A6", "flat": "#B7C6D3", "down": "#FF8A70", "onfill": "#0B0E11", "up_bg": "#17392A", "flat_bg": "#252E38", "down_bg": "#3A1E1A"}
VERDICT_C_LIGHT = {"up": "#177A48", "flat": "#5F6C79", "down": "#C9372C", "onfill": "#FFFFFF", "up_bg": "#DDF3E6", "flat_bg": "#E9EDF2", "down_bg": "#FBE3E0"}
C_HC_LIGHT = {"sub": "#3C4854", "hint": "#4A5765", "dim": "#55626F", "wait": "#2B3540", "line": "#B9C3CE", "card2": "#E1E6EC", "c3": "#D0D7DF",
              "val": "#B0262E", "ow": "#2451B8", "ok": "#1E7A46", "gold": "#8F5E0F"}
RANKC_HC_LIGHT = ["#5C6470", "#8F4A16", "#4F5F6F", "#8F5E0F"]
VERDICT_C_HC_LIGHT = {"up": "#1E7A46", "flat": "#4A5765", "down": "#B0262E", "onfill": "#FFFFFF", "up_bg": "#D2EEDD", "flat_bg": "#E1E6EC", "down_bg": "#F8D9D5"}
# v6.1 — 회색 글씨 세 단계를 전부 밝혔다 (sub 4.9:1 → 7.4:1, dim 3.3:1 → 5.0:1). 어두운 회색은 1080p 모니터에서 '없는 글씨'였다.
# wait = 판정을 미루는 동안의 큰 글씨 — 판정색은 아니지만 '비어 있음'이 아니라 '읽으라는 글'이라 밝게
# v6.3 — 테마 두 벌. 위젯은 만들 때 색이 정해지므로 apply_theme() 는 창을 만들기 전에 한 번. 방송창은 테마와 무관하게 늘 어두운 고대비(BC).
# 색은 전부 키로만 쓴다 (onfill = 색 채움 위의 글자, flash = 판정이 바뀌는 순간, gold_bg = 금색 배경 칸, ok_bg = 초록 버튼 배경 …)
THEME_DARK = {"bg":"#0B0E11","card":"#14191F","card2":"#1D242C","c3":"#242C35","line":"#2B3540",
              "txt":"#EDF1F5","sub":"#A7B6C6","dim":"#7A8A9A","hint":"#93A3B3","wait":"#C9D3DD",
              "val":"#E8453A","ow":"#3B87F7","ok":"#4ED490","gold":"#F5C24B",
              "onfill":"#0B0E11","flash":"#FFFFFF","pb_bg":"#241E0E","warn_bg":"#2A1512","ok_bg":"#1B2A22","ok_bg2":"#173226",
              "gold_bg":"#2A2410","gold_bg2":"#221E12","miss":"#3A1F1D","grid":"#222A32","grid2":"#39434E","chart_line":"#2A333D","swt":"#B98CFF","sel":"#E8702A"}
THEME_LIGHT = {"bg":"#F3F5F8","card":"#FFFFFF","card2":"#E9EDF2","c3":"#DCE2E9","line":"#D3DAE2",
               "txt":"#17202B","sub":"#4B5866","dim":"#69768A","hint":"#5F6C79","wait":"#3D4955",
               "val":"#C93030","ow":"#2F5FD0","ok":"#177A48","gold":"#9C6A12",
               "onfill":"#FFFFFF","flash":"#FFE9A8","pb_bg":"#FFF3D6","warn_bg":"#FBE3E0","ok_bg":"#DDF3E6","ok_bg2":"#CFEBDB",
               "gold_bg":"#FBEFD6","gold_bg2":"#FDF6E7","miss":"#F6D9D6","grid":"#E4E9EF","grid2":"#D3DAE2","chart_line":"#D3DAE2","swt":"#6E43C9","sel":"#D2691E"}
RANKC_DARK = ["#98A2AC", "#E08A3C", "#C9D6E2", "#F5C24B"]
RANKC_LIGHT = ["#6B7480", "#A8571A", "#5E6F80", "#9C6A12"]
C = dict(THEME_DARK)
RANKC = list(RANKC_DARK)
THEME = ["dark"]

# 방송 모드 팔레트 — 녹화·스트리밍에서 가장 먼저 사라지는 것은 어두운 회색 글씨(dim 3.27:1)와
# 진한 빨강이다(4:2:0 색 서브샘플링이 채도 높은 빨강 테두리를 뭉갠다). 밝기를 올리고 빨강을 연하게 한다.
C_BROADCAST = {"txt": "#FFFFFF", "sub": "#C2D0DC", "hint": "#A9BACA", "dim": "#93A4B4", "wait": "#E1E8EF",
               "line": "#3D4B59", "card2": "#252E38", "c3": "#2F3A46",
               "val": "#FF7A6E", "ow": "#6FAEFF", "ok": "#63E6A6", "gold": "#FFD36B"}
RANKC_BROADCAST = ["#B6C0CA", "#F0A257", "#DCE6F0", "#FFD36B"]
C.update(VERDICT_C)                                   # 기본 팔레트에 판정 색 (방송 모드는 apply_broadcast 가 덮어씀)
BC = dict(THEME_DARK); BC.update(VERDICT_C); BC.update(C_BROADCAST); BC.update(VERDICT_C_BROADCAST)   # 방송창 — 테마와 무관하게 늘 어두운 고대비 (OBS 캡처 대상)
RANKC_BC = list(RANKC_BROADCAST)
DAY_TYPE = {"v": ("발로 데이", C["val"]), "w": ("약점 데이", "#8A94A2"), "b": ("벤치마크", C["gold"]), "r": ("휴식", C["dim"])}

def apply_theme(name: str):
    """테마를 고른다 — 창을 만들기 전에. 색을 직접 들고 있는 표(DAY_TYPE)도 같이 갱신"""
    light = name == "light"
    C.update(THEME_LIGHT if light else THEME_DARK); C.update(VERDICT_C_LIGHT if light else VERDICT_C)
    RANKC[:] = RANKC_LIGHT if light else RANKC_DARK; THEME[0] = "light" if light else "dark"
    DAY_TYPE.update({"v": ("발로 데이", C["val"]), "b": ("벤치마크", C["gold"]), "r": ("휴식", C["dim"])})
    return THEME[0]

def apply_broadcast(on: bool):
    """고대비(방송 모드) 팔레트 — 지금 테마 위에 덮는다. 위젯은 만들 때 색이 정해지므로 창을 만들기 전에 불러야 한다"""
    if not on: return False
    if THEME[0] == "light": C.update(C_HC_LIGHT); C.update(VERDICT_C_HC_LIGHT); RANKC[:] = RANKC_HC_LIGHT
    else: C.update(C_BROADCAST); C.update(VERDICT_C_BROADCAST); RANKC[:] = RANKC_BROADCAST
    DAY_TYPE.update({"v": ("발로 데이", C["val"]), "b": ("벤치마크", C["gold"]), "r": ("휴식", C["dim"])})
    return True

def single_instance_lock(tries: int = 1):
    """두 개가 동시에 떠서 서로 기록을 덮어쓰는 것 방지. 소켓 하나를 점유(참조를 유지해야 함).
    글씨 크기를 바꿔 다시 켜는 중이면 앞 창이 닫히기를 잠깐 기다린다"""
    import socket
    for i in range(max(1, tries)):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.bind(("127.0.0.1", int(os.environ.get("AIMDESK_LOCK_PORT") or 47653))); s.listen(1)   # 테스트가 여러 개 동시에 뜰 때 포트를 달리한다
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
    apply_theme(os.environ.get("AIMDESK_THEME") or data.get("theme") or "light")   # 색은 위젯을 만들기 전에 정해야 한다
    apply_broadcast(bool(data.get("broadcast")))
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
    # v6.1 — 기본 글꼴을 한 단계 키웠다 (본문 10 → 11, 캡션 9 → 10). 1080p 100% 에서 9pt 는 12px — 읽는 게 아니라 알아보는 크기였다
    F   = (FAM, 11);  FS  = (FAM, 10);   FB = (FAM, 11, "bold")
    FH  = (FAM, 14, "bold"); FCAP = (FAM, 10, "bold")
    FN  = (MONO, 12, "bold"); FNS = (MONO, 10, "bold"); FBIG = (MONO, 30, "bold")
    # 판정 밴드·라이브 스트립 (시청자용 크기: T0~T2). 배율은 tk scaling 이 같이 키운다
    FV0 = (MONO, 44, "bold"); FV1 = (FAM, 30, "bold"); FV2 = (FAM, 20, "bold"); FVN2 = (MONO, 26, "bold")
    FLIVE = (FAM, 20, "bold"); FSCORE = (MONO, 30, "bold")
    # v7 오늘 탭 — 헤드라인 하나 · 숫자 하나 · 문장 하나. 나머지는 12~13pt regular
    FHERO = (FAM, 34, "bold"); FCNT = (MONO, 44, "bold"); FM = (FAM, 13); FROW = (FAM, 12); FRCNT = (MONO, 14, "bold")
    FLAST = (MONO, 18, "bold"); FBTN = (FAM, 16, "bold"); FLINK = (FAM, 12); FS11 = (FAM, 11)

    def win_dark():
        try:
            import ctypes
            hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
            for attr in (20, 19):
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, attr, ctypes.byref(ctypes.c_int(1 if THEME[0] == "dark" else 0)), 4)
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
        def _lift(hexc): return shade(hexc, 16 if THEME[0] == "dark" else -12)
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
            self.restyle(bg=C["ok_bg2"] if on else C["card2"], fg=C["ok"] if on else C["sub"],
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

    # ══ 헤더 ══ (v7) — 네 가지만: 제목·오늘이 어떤 날 | DAY n · 연속 | 방송 화면 | ⚙ 설정.
    # 예전 상태 위젯(레벨 링·요일 띠·볼테익 필·단계 칩·주인공 줄)은 hdr_hidden 에 산다 — 값은 계속 갱신되고(순서창 요약·검사·기록 탭이 읽는다) 화면엔 없다
    head = tk.Frame(root, bg=C["bg"]); head.pack(fill="x", padx=px(24), pady=(px(12), 0))
    hdr_hidden = tk.Frame(root, bg=C["bg"])                                   # 절대 pack 하지 않는다
    tk.Label(head, text="에임 데스크", font=(FAM, 14, "bold"), bg=C["bg"], fg=C["txt"]).pack(side="left")
    date_lbl = tk.Label(head, text="", font=FLINK, bg=C["bg"], fg=C["sub"]); date_lbl.pack(side="left", padx=(px(12), 0))
    settings_lbl = tk.Label(head, text="⚙ 설정", font=FLINK, bg=C["bg"], fg=C["hint"], cursor="hand2"); settings_lbl.pack(side="right")
    settings_lbl.bind("<Button-1>", lambda e: show("tools"))
    cast_lbl = tk.Label(head, text="방송 화면", font=FLINK, bg=C["bg"], fg=C["hint"], cursor="hand2"); cast_lbl.pack(side="right", padx=(0, px(18)))
    cast_lbl.bind("<Button-1>", lambda e: open_broadcast())
    hdr_day = tk.Label(head, text="", font=FLINK, bg=C["bg"], fg=C["sub"]); hdr_day.pack(side="right", padx=(0, px(18)))
    ttl = sub = rf = hdr_hidden
    daych = tk.Canvas(sub, width=px(70), height=px(18), bg=C["bg"], highlightthickness=0)
    wk_cv = tk.Canvas(sub, width=px(7*15), height=px(18), bg=C["bg"], highlightthickness=0)
    WEEK_FILL = {"done": C["ok"], "miss": C["miss"], "rest": C["card2"], "future": C["card"], "today": C["bg"]}
    def draw_week(strip):
        wk_cv.delete("all")
        for i, (dow, st) in enumerate(strip):
            x = i * px(15); sz = px(11)
            rrect(wk_cv, x, px(3), x + sz, px(3) + sz, 3, fill=WEEK_FILL[st],
                  outline=C["gold"] if st == "today" else "", width=1)
            wk_cv.create_text(x + sz / 2, px(3) + sz / 2, text=dow, font=(FAM, 7),
                              fill=C["onfill"] if st == "done" else C["dim"])
    hdr_e = tk.Label(rf, text="", font=(MONO, 13, "bold"), bg=C["card2"], fg=C["gold"], padx=px(10), pady=px(3))
    hdr_idx = tk.Label(rf, text="", font=FN, bg=C["bg"], fg=C["txt"])          # 순서창 요약이 HDR_STATE 를 읽는다
    hdr_mi = tk.Label(rf, text="", font=FNS, bg=C["bg"], fg=C["sub"])
    hdr_story = tk.Label(sub, text="", font=FH, bg=C["bg"], fg=C["gold"])      # DAY N · 골드 2 → 불멸 · 연속 N일 (기록 파일·검사용)
    hdr_stage = tk.Label(sub, text="", font=FNS, bg=C["card2"], fg=C["sub"], padx=px(8), pady=px(1))
    lv_cv = tk.Canvas(ttl, width=px(22), height=px(22), bg=C["bg"], highlightthickness=0)
    hdr_lv = tk.Label(ttl, text="", font=FNS, bg=C["bg"], fg=C["sub"])
    hdr_streak = tk.Label(ttl, text="", font=FNS, bg=C["bg"], fg=C["sub"])

    # 토스트 — 최대 3개 쌓이고, 클릭하면 닫히고, 각각 10초 뒤 사라진다
    toast = tk.Frame(root, bg=C["bg"])
    tq = ToastQueue()
    TOAST_STYLE = {"pb": (C["pb_bg"], C["gold"]), "info": (C["card2"], C["txt"]), "warn": (C["warn_bg"], C["val"])}
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
    dirty = {"cal": True, "today": True, "grow": True, "bench": True, "log": True, "tools": True}
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
            b.configure(fg=C["txt"] if n == tab else (C["hint"] if n == "tools" else C["sub"]))
            underls[n].configure(bg=C["gold"] if n == tab else C["bg"])
        cur_tab[0] = tab
        refresh_tab(tab)
    for name, label in (("today","오늘"),("cal","계획"),("grow","성장"),("bench","벤치"),("log","기록")):
        holder = tk.Frame(tabbar, bg=C["bg"]); holder.pack(side="left", padx=(0, 22))
        b = tk.Label(holder, text=label, font=(FAM, 13, "bold"), bg=C["bg"],
                     fg=C["sub"], cursor="hand2")
        b.pack(); b.bind("<Button-1>", lambda e, n=name: show(n))
        u = tk.Frame(holder, bg=C["bg"], height=3, width=30); u.pack(fill="x", pady=(3, 0))
        tabbtns[name], underls[name] = b, u
    tabbtns["tools"], underls["tools"] = settings_lbl, tk.Frame(hdr_hidden, bg=C["bg"], height=0)   # 설정은 탭이 아니라 헤더 링크 (frames['tools'] 는 그대로)


    # ══ 계획 탭 (v6.2) ══ — 달력 하나로 '오늘 뭘 하고 · 이번 주가 어떻게 가고 · 몇 달 뒤 어디에 있는지'. 숫자보다 말이 먼저인 유일한 탭
    fcal = tk.Frame(body, bg=C["bg"]); frames["cal"] = fcal
    cal_scroll = VScroll(fcal); cal_scroll.pack(fill="both", expand=True); cbody = cal_scroll.body
    cal_state = {"ym": None}
    CAL_KIND = {"measure": ("출발선 재기 18판", C["gold"]), "boss": ("보스전 18판", C["gold"]), "rest": ("쉼 · 주간 결산", C["dim"]), "before": ("—", C["dim"])}
    def cal_kind(dk: str, tdays: set):
        """달력 한 칸의 종류 — (종류, 칩 글, 색). 종류: measure · boss · train · rest · before"""
        base = BASE_DATE[0]; today = today_key[0]; wd = date.fromisoformat(dk).weekday()
        if base is None:
            if dk < today: return ("before", *CAL_KIND["before"]) if dk not in tdays else ("train", "훈련", C["sub"])
            if dk == today: return ("measure", *CAL_KIND["measure"])
        elif dk < base: return ("before", *CAL_KIND["before"]) if dk not in tdays else ("train", "시작 전 훈련", C["sub"])
        elif dk == base: return ("measure", *CAL_KIND["measure"])
        dt = DAYTYPES[wd] if base is None else day_type_of(dk)
        if dt == "b": return ("boss", *CAL_KIND["boss"])
        if dt == "r": return ("rest", *CAL_KIND["rest"])
        return ("train", main_theme(dk, data.get("pb"))[1], C["ow"])
    def cal_ep(dk: str, tdays: set):
        """DAY 번호 — 친 날은 실제 번호, 앞으로의 날은 오늘부터 쉬는 날을 빼고 센 예정 번호"""
        today = today_key[0]
        if dk in tdays and dk <= today: return episode_no(data, dk)
        if dk < today: return None
        ep = episode_no(data, today); d = date.fromisoformat(today); end = date.fromisoformat(dk)
        while d < end:
            d += timedelta(days=1)
            if cal_kind(d.isoformat(), tdays)[0] in ("measure", "boss", "train"): ep += 1
        return ep
    def cal_move(dm):
        y, m = cal_state["ym"]; m += dm
        if m < 1: y, m = y - 1, 12
        if m > 12: y, m = y + 1, 1
        cal_state["ym"] = (y, m); dirty["cal"] = True; refresh_tab("cal")
    def refresh_cal():
        for w_ in cbody.winfo_children(): w_.destroy()
        today = today_key[0]; td = date.fromisoformat(today); tdays = training_days(data)
        if cal_state["ym"] is None: cal_state["ym"] = (td.year, td.month)
        y, m = cal_state["ym"]
        # 머리: 달 이동 · 범례
        hd = tk.Frame(cbody, bg=C["bg"]); hd.pack(fill="x", pady=(0, px(8)))
        RBtn(hd, "‹", lambda: cal_move(-1), padx=10, pady=3).pack(side="left")
        tk.Label(hd, text=f"{y}년 {m}월", font=FH, bg=C["bg"], fg=C["txt"]).pack(side="left", padx=px(10))
        RBtn(hd, "›", lambda: cal_move(+1), padx=10, pady=3).pack(side="left")
        if (y, m) != (td.year, td.month): RBtn(hd, "오늘 달", lambda: (cal_state.__setitem__("ym", (td.year, td.month)), cal_move(0)), padx=10, pady=3).pack(side="left", padx=(px(8), 0))
        lg = tk.Frame(hd, bg=C["bg"]); lg.pack(side="right")
        for txt, col in (("■ 출발선 · 보스전 18판 (27분)", C["gold"]), ("■ 훈련 20판 + 발로란트 15분 (48분)", C["ow"]), ("■ 쉼 — 앱이 주간 결산 저장", C["dim"])):
            tk.Label(lg, text=txt, font=FS, bg=C["bg"], fg=col).pack(side="left", padx=(px(12), 0))
        # 달력
        grid = tk.Frame(cbody, bg=C["bg"]); grid.pack(fill="x")
        for i, dow in enumerate("월화수목금토일"):
            tk.Label(grid, text=dow, font=FCAP, bg=C["bg"], fg=C["gold"] if i == BENCH_WD else (C["dim"] if i == REST_WD else C["sub"])).grid(row=0, column=i, sticky="w", padx=(px(6), 0), pady=(0, px(2)))
            grid.grid_columnconfigure(i, weight=1, uniform="cal")
        first = date(y, m, 1); start = first - timedelta(days=first.weekday())
        n_rows = ((date(y + (m == 12), (m % 12) + 1, 1) - timedelta(days=1)) - start).days // 7 + 1
        for r in range(n_rows):
            for c in range(7):
                d = start + timedelta(days=r * 7 + c); dk = d.isoformat(); in_m = d.month == m
                kind, chip, col = cal_kind(dk, tdays)
                bg_ = {"measure": C["gold_bg"], "boss": C["gold_bg2"], "rest": C["bg"]}.get(kind, C["card"])
                cell = tk.Frame(grid, bg=bg_, highlightbackground=C["gold"] if dk == today else (C["line"] if kind != "rest" else C["bg"]), highlightthickness=px(2) if dk == today else 1, padx=px(8), pady=px(6))
                cell.grid(row=r + 1, column=c, sticky="nsew", padx=(0, px(4)), pady=(0, px(4)))
                top_ = tk.Frame(cell, bg=bg_); top_.pack(fill="x")
                tk.Label(top_, text=str(d.day), font=FB, bg=bg_, fg=(C["txt"] if in_m else C["dim"])).pack(side="left")
                if dk == today: tk.Label(top_, text="오늘", font=FCAP, bg=C["gold"], fg=C["onfill"], padx=px(5)).pack(side="left", padx=(px(6), 0))
                ep = cal_ep(dk, tdays) if kind in ("measure", "boss", "train") else None
                if ep: tk.Label(top_, text=f"DAY {ep}", font=FNS, bg=bg_, fg=C["gold"] if dk in tdays else C["dim"]).pack(side="right")
                tk.Label(cell, text=chip, font=FB, bg=bg_, fg=(col if in_m else C["dim"]), anchor="w", wraplength=px(150), justify="left").pack(fill="x", pady=(px(2), 0))
                if dk in tdays:
                    e_ = data["days"][dk]; n_ = sum((e_.get("count") or {}).values()) or len(e_.get("plays") or [])
                    st, sc = f"✓ {n_}판", C["ok"]
                elif kind in ("measure", "boss"): st, sc = ("오늘 · 27분" if dk == today else "27분"), C["sub"]
                elif kind == "train": st, sc = ("오늘 · 48분" if dk == today else "48분"), C["sub"]
                elif kind == "rest": st, sc = "", C["dim"]
                else: st, sc = ("안 침" if dk < today and BASE_DATE[0] and dk > BASE_DATE[0] else ""), C["dim"]
                if kind == "train" and dk < today and dk not in tdays and BASE_DATE[0] and dk > BASE_DATE[0]: st, sc = "안 침", C["val"]
                tk.Label(cell, text=st, font=FS, bg=bg_, fg=sc, anchor="w").pack(fill="x")
                cl_ = coach_for_day(data, dk, today) if in_m and kind != "before" else None
                if cl_: tk.Label(cell, text=f"{cl_[0]} · {cl_[1]}", font=FS, bg=bg_, fg=C["gold"] if cl_[0] == "내일 이렇게" else C["txt"], anchor="w", wraplength=px(150), justify="left").pack(fill="x", pady=(px(3), 0))
        # 아래: 이번 주 · 다섯 단계 · 이 앱이 하는 일
        cols_ = tk.Frame(cbody, bg=C["bg"]); cols_.pack(fill="x", pady=(px(12), 0))
        left_ = tk.Frame(cols_, bg=C["bg"]); left_.pack(side="left", fill="both", expand=True, anchor="n")
        wk = card(left_); wk.pack(fill="x")
        tk.Label(wk, text="이번 주", font=FH, bg=C["card"], fg=C["txt"]).pack(anchor="w")
        mon = td - timedelta(days=td.weekday())
        for i in range(7):
            d = mon + timedelta(days=i); dk = d.isoformat(); kind, chip, col = cal_kind(dk, tdays)
            what = {"measure": "18개를 한 판씩 — 이 점수가 앞으로의 0점", "boss": "18판 시험 — 출발선과 비교, 방송창은 에너지 보드",
                    "rest": "쉬는 날 — 앱을 켜면 주간 결산이 저장됩니다", "before": ""}.get(kind, "워밍업 2 → 측정 6 → 본훈련 12 → 발로란트 15분")
            row = tk.Frame(wk, bg=C["card"]); row.pack(fill="x", pady=(px(5), 0))
            tk.Label(row, text=f"{'월화수목금토일'[i]} {d.month}/{d.day}", font=FB, bg=C["card"], fg=C["gold"] if dk == today else C["sub"], width=8, anchor="w").pack(side="left")
            tk.Label(row, text=chip, font=FB, bg=C["card"], fg=col, width=14, anchor="w").pack(side="left")
            cl_ = coach_for_day(data, dk, today) if kind != "before" else None
            done_ = f"✓ {sum((data['days'][dk].get('count') or {}).values())}판 · " if dk in tdays else ""
            tk.Label(row, text=done_ + (f"{cl_[0]} · {cl_[1]}" if cl_ else what), font=FS, bg=C["card"], fg=(C["gold"] if cl_ and cl_[0] == "내일 이렇게" else C["txt"]) if cl_ else C["sub"], anchor="w").pack(side="left", fill="x", expand=True)
        # 코치 노트 — 내일 이렇게 · 이번 주 흐름 (계획 탭에서 바로 읽는다)
        cc = card(left_); cc.pack(fill="x", pady=(px(12), 0))
        nk_, nn_ = latest_note(data)
        tk.Label(cc, text="코치 노트" + (f" · {nk_[5:].replace('-', '/')}" + (f" {nn_.get('at')}" if nn_.get("at") else "") if nk_ else ""), font=FH, bg=C["card"], fg=C["txt"]).pack(anchor="w")
        if not nk_:
            tk.Label(cc, text="AI 코치 노트를 받으면 여기에 '내일 이렇게'와 '이번 주 흐름'이 적히고, 달력 칸마다 코치 한 줄이 붙습니다 — 설정 탭 → 트레이너 → 지금 답장 받기",
                     font=FS, bg=C["card"], fg=C["hint"], wraplength=px(560), justify="left").pack(anchor="w", pady=(px(4), 0))
        else:
            _nt = nn_.get("text") or ""
            for _ttl, _key in (("오늘 한 줄", "[오늘 한 줄]"), ("내일 이렇게", "[내일 이렇게]"), ("이번 주 흐름", "[이번 주 흐름]")):
                _sec = note_section(_nt, _key)
                if not _sec: continue
                if _ttl == "오늘 한 줄" and nk_ != today: _ttl = f"{nk_[5:].replace('-', '/')} 한 줄"
                tk.Label(cc, text=_ttl, font=FB, bg=C["card"], fg=C["gold"]).pack(anchor="w", pady=(px(8), px(2)))
                _lines = note_items(_sec) if _key == "[내일 이렇게]" else [_sec.replace("\n", " ")]
                for _it in _lines[:6]:
                    tk.Label(cc, text=("• " if _key == "[내일 이렇게]" else "") + _it, font=FS, bg=C["card"], fg=C["txt"], wraplength=px(560), justify="left", anchor="w").pack(fill="x", pady=(0, px(2)))
            if TRAINER.get("note"): tk.Label(cc, text=f"메모 · {TRAINER['note']}", font=FS, bg=C["card"], fg=C["sub"], wraplength=px(560), justify="left", anchor="w").pack(fill="x", pady=(px(6), 0))
            _more = tk.Label(cc, text="전체 노트 보기 →", font=FLINK, bg=C["card"], fg=C["hint"], cursor="hand2"); _more.pack(anchor="w", pady=(px(6), 0))
            _more.bind("<Button-1>", lambda e, k_=nk_: open_coach_note(k_))
        rt = tk.Frame(cols_, bg=C["bg"]); rt.pack(side="left", anchor="n", padx=(px(12), 0))
        sg = card(rt); sg.pack(fill="x")
        ss = stage_status(data, today)
        tk.Label(sg, text="골드 2 → 불멸 · 다섯 단계", font=FH, bg=C["card"], fg=C["txt"]).pack(anchor="w")
        tk.Label(sg, text="관문은 전부 앱이 읽는 숫자. 두 주 연속 다 차야 다음 단계 (쉬는 날인 월요일에 지난 주를 마감)", font=FS, bg=C["card"], fg=C["hint"], wraplength=px(390), justify="left").pack(anchor="w", pady=(0, px(4)))
        STAGE_PLAIN = ["첫날 18판 · 훈련 10일 · 발로 블록 8번 · 랭크 카드 5번", "코박스 9갈래 골드 · 헤드샷 25% · 사격 24/30 · 플래 1 2주",
                       "인터 500 · 헤드샷 30% · ACS 220 · 다이아 1 2주 · 결산 8주", "인터 650 · ACS 230 · 40판 승률 53% · 어센 1 30일", "인터 700 · ACS 240 · 60판 승률 55% · 불멸 1 30일"]
        for i, st_ in enumerate(STAGES):
            here = i == ss["idx"]
            row = tk.Frame(sg, bg=C["card2"] if here else C["card"], padx=px(8), pady=px(4)); row.pack(fill="x", pady=(px(3), 0))
            tk.Label(row, text=str(i), font=FBIG if False else (MONO, 16, "bold"), bg=row["bg"], fg=C["gold"] if here else C["dim"], width=2).pack(side="left")
            bx = tk.Frame(row, bg=row["bg"]); bx.pack(side="left", fill="x", expand=True)
            tk.Label(bx, text=st_["name"] + f" · {st_['span']}" + ("  ← 지금 여기" if here else ""), font=FB, bg=row["bg"], fg=C["txt"] if here else C["sub"], anchor="w").pack(fill="x")
            if here:
                for g in ss["gates"]:
                    tk.Label(bx, text=f"{'✓' if g['ok'] else '✗'} {g['label']} — {g['val']}", font=FS, bg=row["bg"], fg=C["ok"] if g["ok"] else C["sub"], anchor="w").pack(fill="x")
            else: tk.Label(bx, text=STAGE_PLAIN[i], font=FS, bg=row["bg"], fg=C["dim"], anchor="w", wraplength=px(360), justify="left").pack(fill="x")
        hp = card(rt); hp.pack(fill="x", pady=(px(10), 0))
        tk.Label(hp, text="이 앱이 하는 일", font=FH, bg=C["card"], fg=C["txt"]).pack(anchor="w")
        for ln in ("코박스(에임 연습 게임)가 저장하는 점수 파일을 2초마다 읽어 자동으로 기록합니다 — 직접 적는 건 하루 숫자 몇 개뿐",
                   "노란 버튼 → 코박스에서 AIMDESK 재생 목록 ▶. 한 판 끝나면 앱이 다음 판을 넘깁니다",
                   "판정 세 개 — 오늘(어제보다?) · 요즘(흐름) · 성장(몇 주 추세). 자료가 모자라면 꾸미지 않고 비워 둡니다",
                   "루틴이 끝나면 오늘 한 장 · 유튜브 제목·설명·챕터 · 썸네일 페이지가 기록 폴더에 저장됩니다",
                   "볼테익 점수의 Iron·Bronze·Silver·Gold 는 코박스 랭크입니다 — 발로란트 랭크가 아닙니다"):
            tk.Label(hp, text="· " + ln, font=FS, bg=C["card"], fg=C["sub"], wraplength=px(390), justify="left", anchor="w").pack(fill="x", pady=(px(3), 0))

    # ══ 오늘 탭 ══ (v7) — 한 가지만: 헤드라인 하나 · 숫자 하나 · 버튼 하나. 세부는 '자세히' 뒤로. 방송창은 별개(draw_broadcast)
    ft = tk.Frame(body, bg=C["bg"]); frames["today"] = ft
    page_pad = [px(24), 0]
    page = tk.Frame(ft, bg=C["bg"]); page.pack(fill="both", expand=True, padx=page_pad[0])
    hero = tk.Frame(page, bg=C["card"], highlightbackground=C["line"], highlightthickness=1, padx=px(28), pady=px(22)); hero.pack(fill="x")
    live = hero
    h_top = tk.Frame(hero, bg=C["card"]); h_top.pack(fill="x")
    cnt_box = tk.Frame(h_top, bg=C["card"]); cnt_box.pack(side="right", anchor="s")
    cnt_unit = tk.Label(cnt_box, text="판", font=FM, bg=C["card"], fg=C["sub"]); cnt_unit.pack(side="right", anchor="s", pady=(0, px(9)))
    cnt_lbl = tk.Label(cnt_box, text="0/20", font=FCNT, bg=C["card"], fg=C["dim"]); cnt_lbl.pack(side="right", anchor="s", padx=(0, px(6)))
    cur_lbl = tk.Label(h_top, text="오늘 할 일", font=FHERO, bg=C["card"], fg=C["txt"], anchor="w"); cur_lbl.pack(side="left", anchor="sw", fill="x", expand=True)
    est_lbl = tk.Label(hero, text="", font=FM, bg=C["card"], fg=C["sub"], anchor="w", justify="left"); est_lbl.pack(fill="x", pady=(px(2), 0))
    day_state = {"dt": "v", "pl": None, "sess_lbl": None, "coach": [], "summary": None, "detail": None, "toggle": None,
                 "hero_state": None, "last_hero": None, "anim": None}
    routine_rows = []; section_labels = []; routine_next = [None]
    if (data.get("hero") or {}).get("date") == today_key[0]: day_state["hero_state"] = data["hero"].get("state")   # 히스테리시스 상태 복원
    day_state["rib_cv"] = tk.Canvas(hero, height=px(34), bg=C["card"], highlightthickness=0); day_state["rib_cv"].pack(fill="x", pady=(px(12), 0))
    todo_host = tk.Frame(hero, bg=C["card"]); todo_host.pack(fill="x", pady=(px(10), 0))     # ①②③④ 줄 — build_day_ui 가 날마다 다시 채운다
    day_state["summary"] = todo_host
    last_row = tk.Frame(hero, bg=C["card"])                                                    # 방금 친 판 — 판이 있을 때만 보인다
    tk.Label(last_row, text="방금", font=FM, bg=C["card"], fg=C["sub"]).pack(side="left")
    cur_score = tk.Label(last_row, text="—", font=FLAST, bg=C["card"], fg=C["dim"]); cur_score.pack(side="left", padx=(px(8), 0))
    cur_word = tk.Label(last_row, text="", font=FM, bg=C["card"], fg=C["hint"]); cur_word.pack(side="left", padx=(px(8), 0))
    band_cv = tk.Canvas(hero, height=px(66), bg=C["card"], highlightthickness=0); band_cv.pack(fill="x", pady=(px(12), 0))   # 판정 한 문장
    run_row = tk.Frame(hero, bg=C["card"]); run_row.pack(fill="x", pady=(px(14), 0))
    def run_cta():
        """큰 버튼 — 안 돌고 있으면 실행, 돌고 있으면 순서창, 끝났으면 오늘 한 장"""
        pl_ = day_state.get("pl")
        if not pl_: return
        if seq_alive(): show_sequence(pl_)
        else: run_playlist(pl_)
    run_btn = RBtn(run_row, "▶ 오늘 루틴 실행", run_cta, bg=C["gold"], fg=C["onfill"], font=FBTN, padx=28, pady=12, r=12, w=px(320)); run_btn.pack(side="left")
    def rec_now():
        """OBS 녹화를 누른 순간에 같이 누른다 — 명장면·챕터의 0:00 이 정확해진다 (루틴 실행 시각을 덮어쓴다)"""
        _dy = data["days"].setdefault(today_key[0], blank_day())
        _dy["rec"] = {"start": datetime.now().strftime("%H.%M.%S"), "src": "manual"}; save_data(data)
        show_toast(f"녹화 시작 {_dy['rec']['start'].replace('.', ':')} — 여기가 영상의 0:00 입니다")
    links = tk.Frame(run_row, bg=C["card"]); links.pack(side="left", padx=(px(18), 0), anchor="s", pady=(0, px(6)))
    def _link(text, cmd):
        l_ = tk.Label(links, text=text, font=FLINK, bg=C["card"], fg=C["hint"], cursor="hand2"); l_.pack(side="left", padx=(0, px(14)))
        l_.bind("<Button-1>", lambda e: cmd()); return l_
    rec_lnk = _link("● 녹화 시작", rec_now)
    seq_lnk = _link("순서 보기", lambda: (day_state.get("pl") and show_sequence(day_state["pl"])))
    card_lnk = _link("오늘 한 장", lambda: open_card())
    note_lnk = _link("코치 노트", lambda: open_coach_note()); note_lnk.pack_forget()      # 오늘 AI 코치 노트가 있을 때만 (sync_live)
    auto_mini = tk.Label(hero, text="", font=FS, bg=C["card"], fg=C["hint"], anchor="w", justify="left", wraplength=px(900))   # 내용이 있을 때만 pack
    # 발밑 줄 — 왼쪽 자세히 · 오른쪽 컨디션
    foot = tk.Frame(page, bg=C["bg"]); foot.pack(fill="x", pady=(px(8), 0))
    toggle_lbl = tk.Label(foot, text="", font=FLINK, bg=C["bg"], fg=C["hint"], cursor="hand2"); toggle_lbl.pack(side="left")
    toggle_lbl.bind("<Button-1>", lambda e: set_routine_open(not data["win"].get("routine_open")))
    day_state["toggle"] = toggle_lbl
    cond_row = tk.Frame(foot, bg=C["bg"]); cond_row.pack(side="right")
    cond_chip = tk.Label(cond_row, text="", font=FCAP, bg=C["down_bg"], fg=C["down"], padx=px(6))
    # 자세히 — 왼쪽: 도전 · 시나리오별 점수 · 코치 · 오늘 곡선 / 오른쪽: 발로란트 랭크 · 트레이너. set_routine_open 이 pack/forget
    cols = tk.Frame(page, bg=C["bg"])
    left = card(cols); left.pack(side="left", fill="both", expand=True)
    left_scroll = VScroll(left); left_scroll.pack(fill="both", expand=True)
    right = tk.Frame(cols, bg=C["bg"], width=px(360)); right.pack(side="left", fill="y", padx=(14, 0))
    right.pack_propagate(False)
    right_scroll = VScroll(right); right_scroll.pack(fill="both", expand=True)
    rbody = right_scroll.body
    day_state["rib_lbl"] = tk.Label(hdr_hidden, text="", font=FNS, bg=C["bg"], fg=C["sub"])        # 옛 형식 그대로 (순서창 요약·검사가 읽는다)
    day_state["sess_lbl"] = tk.Label(hdr_hidden, text="", font=FNS, bg=C["bg"], fg=C["sub"])
    day_state["rib_cells"] = []
    # 도구 탭 — 시청자가 볼 필요 없는 것(폴더·글씨 크기·방송 모드·트레이너 답장)
    ftool = tk.Frame(body, bg=C["bg"]); frames["tools"] = ftool
    tools_scroll = VScroll(ftool, bg=C["bg"]); tools_scroll.pack(fill="both", expand=True); tbody = tools_scroll.body
    tcols = tk.Frame(tbody, bg=C["bg"]); tcols.pack(anchor="nw")
    tcol1 = tk.Frame(tcols, bg=C["bg"]); tcol1.pack(side="left", anchor="n")
    tcol2 = tk.Frame(tcols, bg=C["bg"]); tcol2.pack(side="left", anchor="n", padx=(px(14), 0))
    _fcache = {}
    def fit_font(base, text, maxw, floor=12, step=4):
        """글자가 칸을 넘치면 step pt 씩 줄인다 (최소 floor pt). Font 객체는 크기별로 한 번만 만든다"""
        fam_, size, *rest = base; size = abs(size)
        while True:
            key = (fam_, size, tuple(rest)); f_ = _fcache.get(key)
            if f_ is None: f_ = _fcache[key] = tkfont.Font(family=fam_, size=size, weight=(rest[0] if rest else "normal"))
            if f_.measure(text) <= maxw or size <= floor: return f_
            size -= step
    def vcol(V):
        """판정 → (채움색, 이 색이 판정색인가)"""
        colk = V.get("colk")
        if colk == "rank":
            rk = V.get("rank"); return (RANKC[RANK_IDX[rk]] if rk in RANK_IDX else C["gold"]), True
        if colk in ("up", "flat", "down"): return C[colk], True
        if colk == "gold": return C["gold"], True
        return C["dim"], False
    def draw_band(cv, V, flash=None):
        """오늘 탭의 판정 — 색 판 위에 문장 하나 + 풀이 한 줄. 타일·점·추세선 없음 (그건 성장 탭 draw_trend)"""
        cv.delete("all")
        W = max(cv.winfo_width(), px(400)); H = px(66)
        if int(cv.cget("height")) != H: cv.configure(height=H)
        dk0 = today_key[0]; Vd = V["day"]; fc, isv = vcol(Vd)
        if BASE_DATE[0] is None or dk0 == BASE_DATE[0]:                            # 기준 측정일
            br_ = bench_readiness(data, dk0); n_t = br_["n_today"]; proj = br_["projected"]
            if n_t < 18: sent, cap = "○ 오늘 18판이 앞으로의 0점이에요", "내일부터 하루 20판 루틴" + (f" · 예상 {proj}" if proj is not None else "")
            else: sent, cap = "● 출발선 완성 ✓", (f"출발선 {proj} · " if proj is not None else "") + "내일부터 하루 20판 루틴"
            bg, fg = C["card2"], C["wait"]
        else:
            _pd = len({k_ for k_, _t_, _s_ in cur_plays() if k_ in PROBE})
            sent, cap = verdict_sentence(V, _pd)
            colk = Vd.get("colk")
            bg = C[colk + "_bg"] if colk in ("up", "flat", "down") else C["card2"]; fg = fc if isv else C["wait"]
        if flash: bg = flash
        rrect(cv, 0, 0, W, H, px(10), fill=bg, outline="", tags="hero")
        rx = px(160) if Vd.get("n_pb") else px(24)
        f1 = fit_font(FLIVE, sent, W - px(32) - rx, floor=14, step=2)
        cv.create_text(px(16), int(H * 0.34), text=sent, anchor="w", fill=fg, font=f1, tags="hero")
        cv.create_text(px(16), int(H * 0.76), text=cap, anchor="w", fill=C["sub"], font=fit_font(FS11, cap, W - px(32) - rx, floor=9, step=1), tags="hero")
        if Vd.get("n_pb"): cv.create_text(W - px(16), int(H * 0.5), text=f"★ 오늘 신기록 {Vd['n_pb']}", anchor="e", fill=C["gold"], font=FS11, tags="hero")
    def draw_trend(cv, V):
        """성장 탭 맨 위 — 【요즘】【성장】 두 타일 (v6 오늘 탭에서 옮겨 옴). 자료가 모자라면 '판정까지 N일' · 성장 자리는 관문 미터"""
        cv.delete("all"); W = max(cv.winfo_width(), px(400)); H = px(170)
        gap = px(12); sw = (W - gap) // 2
        for j, (key, title) in enumerate((("recent", "요즘"), ("grow", "성장"))):
            Vt = V[key]; x = j * (sw + gap); fc, isv = vcol(Vt)
            if key == "grow" and Vt["state"] == "hold" and BASELINE[0]:
                gw_, gn_, gc_ = fmt_gate(gate_status(data.get("pb") or {}))
                Vt = dict(Vt, word=gw_, glyph="", num=gn_, cap=("먼저 " + _cut(gc_.split(" · ")[0], 22)) if gc_ and not gw_.endswith("✓") else _cut(gc_, 24), cap2=f"추세 판정은 {Vt['word'].replace('판정까지 ', '')} 뒤")
            bgk = Vt["colk"] + "_bg" if Vt["colk"] in ("up", "flat", "down") else None
            rrect(cv, x, 0, x + sw, H, px(14), fill=C[bgk] if bgk else C["card2"], outline=fc if isv else C["line"], width=1)
            if isv: rrect(cv, x, 0, x + sw, px(7), px(3), fill=fc, outline="")
            fg2 = fc if isv else C["wait"]
            top_r, bottom = (Vt.get("cap2", ""), Vt.get("cap", "")) if key == "recent" else (Vt.get("cap", ""), Vt.get("cap2", ""))
            cv.create_text(x + px(12), px(24), text=title, anchor="w", fill=C["txt"], font=FB)
            capf = fit_font(FS, top_r, sw - px(64)); cv.create_text(x + sw - px(12), px(24), text=top_r, anchor="e", fill=C["dim"], font=capf)
            wf = fit_font((FAM, 16, "bold"), f"{Vt['word']} {Vt['glyph']}", sw - px(24)); cv.create_text(x + px(12), int(H * 0.33), text=f"{Vt['word']} {Vt['glyph']}", anchor="w", fill=fg2, font=wf)
            nf = fit_font((MONO, 20, "bold"), Vt.get("num", ""), sw - px(24)); cv.create_text(x + px(12), int(H * 0.52), text=Vt.get("num", ""), anchor="w", fill=fg2, font=nf)
            ev = Vt.get("ev") or {}; y1, y2 = int(H * 0.66), int(H * 0.76)
            if key == "recent":
                dots = ev.get("dots") or []
                for i_, (dk_, dv) in enumerate(dots[-5:]):
                    cx_ = x + px(12) + i_ * px(28); col_ = C["card"] if dv is None else (C["up"] if dv >= VERDICT["FORM_DOT"] else C["down"] if dv <= -VERDICT["FORM_DOT"] else C["flat"])
                    rrect(cv, cx_, y1, cx_ + px(22), y2, px(4), fill=col_, outline=C["gold"] if dk_ == today_key[0] else "", width=1)
                    cv.create_text(cx_ + px(11), y2 + px(7), text=DOWK[date.fromisoformat(dk_).weekday()], fill=C["dim"], font=FS)
            else:
                pts = ev.get("pts") or []
                if len(pts) >= 2:
                    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]; x0_, x1_ = min(xs), max(xs); lo, hi = min(ys + [0]), max(ys + [0])
                    if hi - lo < 4: hi, lo = (hi + lo) / 2 + 2, (hi + lo) / 2 - 2
                    X_ = lambda v: x + px(12) + (sw - px(24)) * ((v - x0_) / max(1, x1_ - x0_))
                    Y_ = lambda v: y2 - (y2 - y1) * ((v - lo) / (hi - lo))
                    cv.create_line(x + px(12), Y_(0), x + sw - px(12), Y_(0), fill=C["line"], dash=(3, 3))
                    for px_, py_ in pts: cv.create_oval(X_(px_) - 2, Y_(py_) - 2, X_(px_) + 2, Y_(py_) + 2, fill=C["sub"], outline="")
                    if ev.get("slope") is not None and ev.get("mid"):
                        mx, my = ev["mid"]; sl_ = ev["slope"]
                        cv.create_line(X_(x0_), Y_(my + sl_ * (x0_ - mx)), X_(x1_), Y_(my + sl_ * (x1_ - mx)), fill=fg2, width=px(3))
            cv.create_text(x + px(12), H - px(11), text=bottom, anchor="w", fill=C["dim"], font=fit_font(FS, bottom, sw - px(24)))
    def flash_hero(V):
        """판정이 바뀐 순간 한 번 하얗게 → 제 색으로 (숫자 트윈 없음)"""
        if day_state.get("anim"):
            try: root.after_cancel(day_state["anim"])
            except Exception: pass
        draw_band(band_cv, V, flash=C["flash"])
        day_state["anim"] = root.after(140, lambda: (day_state.__setitem__("anim", None), band_cv.winfo_exists() and draw_band(band_cv, V)))

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
            dirty["today"] = True; refresh_tab(cur_tab[0])          # 창이 사라진 뒤 라이브 줄(자동 진행 안내·지금 판)을 다시 맞춘다
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
        w.geometry(pos); w.update_idletasks()   # 'wm geometry' 는 idle 때 적용된다 — 숨기기(withdraw) 전에 먼저 반영해야 위치가 남는다
        update_sequence()

    def draw_tab_guide(cv):
        """코박스 샌드박스 브라우저의 탭 4개를 그려 '로컬 재생 목록'(네 번째)을 가리킨다"""
        cv.delete("all"); names = ["온라인 시나리오", "로컬 시나리오", "온라인 재생 목록", "로컬 재생 목록"]
        wbox, h, gap, x, y = px(108), px(24), px(6), px(2), px(2)
        for i, nm in enumerate(names):
            on = i == 3
            rrect(cv, x, y, x + wbox, y + h, 5, fill=(C["sel"] if on else C["bg"]), outline=C["sel"], width=1)
            cv.create_text(x + wbox / 2, y + h / 2, text=nm, fill=(C["onfill"] if on else C["sel"]), font=(FAM, 8, "bold" if on else "normal"))
            x += wbox + gap
        cv.create_text(x - gap - wbox / 2, y + h + px(13), text="▲ 이 탭(네 번째)에서 AIMDESK 를 고르세요 · 시나리오 탭이 아닙니다", fill=C["gold"], font=(FAM, 8, "bold"), anchor="e")

    def remember_seq_pos():
        if seq_alive():
            w = seq_win["win"]
            if w.state() == "withdrawn": return       # 숨긴 창의 winfo_x/y 는 마지막으로 보였던 자리 — 덮어쓰지 않는다
            data["win"]["seq"] = "%+d%+d" % (w.winfo_x(), w.winfo_y())

    def update_sequence():
        if not seq_alive(): return
        done, nxt, scores = seq_status()
        dkey = today_key[0]
        _pbb = pb_before_day(data, dkey); _seen_pb = {}; _kinds = []
        def _vf(k_, sc_):
            base = max(_pbb.get(k_, 0), _seen_pb.get(k_, 0)) or None
            r_ = play_verdict(sc_, scen_band(data, k_, dkey), base)
            _seen_pb[k_] = max(_seen_pb.get(k_, 0), sc_)
            _kinds.append(r_[0])
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
                                   (HDR_STATE["vi"], HDR_STATE["oi"]), est, block_txt, ribbon_counts(_kinds))
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
        cfg(seq_win["auto_lbl"], text=msg, fg=col); sync_auto_mini()
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
        if auto["mode"] != "link": return               # 키 방식으로 바뀐 뒤 도착한 예약
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
        """key 방식: 판이 끝났으니(CSV) 결과창에서 NEXT 키. 그 사이 수동으로 넘겼으면(seen 이 이미 p) 안 누른다.
        root.after 로 예약된 뒤 딥링크 방식으로 바뀌었으면 누르지 않는다 (예약은 모드 전환을 모른다)"""
        if auto["mode"] != "key": return
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
        if auto["mode"] == "link": auto.update(fired=None, due=None, pending=None)   # 키로 넘긴 표시(fired)는 딥링크가 아니다 — 남기면 첫 딥링크가 막힌다
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

    def show_sequence(plname):
        """순서창 보기 — 숨겨 둔 채 돌고 있으면 다시 띄우고, 없으면 연다"""
        if seq_alive():
            w = seq_win["win"]; w.deiconify(); w.lift(); return
        open_sequence(plname)

    def sync_auto_mini():
        """순서창의 자동 진행 안내를 라이브 줄에 그대로 비춘다 (창을 숨겨도 상태가 보이게)"""
        al = seq_win.get("auto_lbl")
        if seq_alive() and al is not None and al.winfo_exists(): cfg(auto_mini, text=al.cget("text"), fg=al.cget("fg"))
        else: cfg(auto_mini, text="")

    def run_playlist(plname):
        sd = data.get("stats_dir"); wrote = 0
        if not sd:                                     # 폴더 없이 시작하면 친 판이 하나도 안 잡힌다 — 먼저 잡게 한다
            show_toast("⚠ 먼저 코박스 stats 폴더를 지정하세요 — 폴더를 모르면 플레이리스트도 설치되지 않고 친 판도 기록되지 않습니다", "warn")
            show("tools")
            return
        _dy = data["days"].setdefault(today_key[0], blank_day())
        if not (_dy.get("rec") or {}).get("start"):           # 루틴 실행 시각 = 녹화 시작(기본). 명장면·챕터의 0:00
            _dy["rec"] = {"start": datetime.now().strftime("%H.%M.%S"), "src": "routine"}; save_data(data)
        if sd: _, _, wrote = ensure_playlists(sd, today_key[0], data["pb"])   # 오늘 테마로 로컬 플레이리스트 설치
        was_running = kovaaks_running()
        if wrote and was_running:                      # 코박스는 시작할 때 Playlists 폴더를 읽는다 — 켜진 채로 새로 쓴 파일은 재시작해야 보인다
            show_toast("⚠ 플레이리스트를 새로 설치했습니다 — 코박스가 켜져 있었다면 껐다 켜야 '로컬 재생 목록'에 보입니다", "warn")
        open_sequence(plname)
        if seq_alive() and not data.get("seq_popup"): seq_win["win"].withdraw()      # v4 기본: 창 없이 NEXT 만 — 진행은 라이브 줄에 (순서 보기로 열 수 있다)
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
                    cv.create_text(W - R + px(6), Y(t), text=f"{TIERS[CUR_TIER[0]][2][i]} {t}", anchor="w", fill=RANKC[i], font=FNS)
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

    BCAST_PRESETS = {"strip": (1920, 240), "card": (1280, 400), "full": (1920, 1080)}   # 원시 픽셀 — OBS 는 픽셀을 캡처한다
    def vcol_bc(V_):
        """방송창용 vcol — 테마와 무관하게 방송 팔레트에서"""
        colk = V_.get("colk")
        if colk == "rank":
            rk = V_.get("rank"); return (RANKC_BC[RANK_IDX[rk]] if rk in RANK_IDX else BC["gold"]), True
        if colk in ("up", "flat", "down"): return BC[colk], True
        if colk == "gold": return BC["gold"], True
        return BC["dim"], False
    def draw_broadcast(cv):
        """녹화되는 화면 그 자체. 폰에서 1080p 를 볼 때도 읽히게 글자 하한 28px, 텍스트 요소 7개 이하.
        테마가 밝아도 이 창은 어둡다 (C = BC) — OBS 가 잡는 화면은 늘 같아야 한다.
        첫 줄 = 주인공 줄(DAY N · 골드 2 → 불멸) + 티어/볼테익 필. 발로 데이 = 오늘 판정 · 요즘 · 관문 + 지금 판 · 남은 시간 · 띠.
        토요일 = 보스전 보드(에너지 카운터 · 9갈래 막대) · 일요일 = 이번 주 점수판. 크로마 모드면 글자 묶음마다 판을 깐다"""
        C = BC                                             # 이 함수 안의 C 는 방송 팔레트
        cv.delete("all")
        W = max(cv.winfo_width(), 320); H = max(cv.winfo_height(), 120)
        chroma = bool((data.get("bcast") or {}).get("chroma"))
        fam = lambda fr, b=True: tkfont.Font(family=FAM, size=-max(28, int(H * fr)), weight="bold" if b else "normal")
        mon = lambda fr: tkfont.Font(family=MONO, size=-max(28, int(H * fr)), weight="bold")
        def fit(f, text, maxw):
            while f.measure(text) > maxw and abs(f.cget("size")) > 28: f.configure(size=-(abs(f.cget("size")) - 2))
            return f
        def plate(x1, y1, x2, y2, fill=None):
            if chroma or fill: rrect(cv, x1, y1, x2, y2, int(H * 0.04), fill=fill or C["card"], outline="")
        dkey = today_key[0]; cp = cur_plays(); dt = day_state.get("dt", "v")
        kinds = [k_ for _, _, k_ in day_verdicts(data, dkey, cp)]
        plan = today_plan_n(); pad = int(W * 0.02)
        V = verdicts(data, dkey, dt, cp, day_state.get("hero_state"))
        strip = H < 300
        # ── 첫 줄: 주인공 · 티어 · 볼테익 ──
        y0 = int(H * (0.17 if strip else 0.08))
        sl = story_line(data, dkey); f_sl = fit(fam(0.11 if strip else 0.06), sl, int(W * 0.55))
        plate(pad - 8, y0 - int(H * 0.07), pad + f_sl.measure(sl) + 8, y0 + int(H * 0.07))
        cv.create_text(pad, y0, text=sl, anchor="w", fill=C["gold"], font=f_sl)
        vt, vrr = day_val_tier(data, dkey); e_pb, _ = totalE(data.get("pb") or {}); e0 = totalE(BASELINE[0])[0] if BASELINE[0] else None
        pills = []
        if vt: pills.append((ko_tier(vt) + (f" · {int(vrr):+d}RR" if vrr is not None else ""), C["val"]))
        pills.append(((f"볼테익 {e_pb}" + (f" · 출발선 {e_pb - e0:+d}" if e0 is not None else "")) if e_pb is not None else "기준 측정 전", C["sub"]))
        xr = W - pad; f_p = fam(0.10 if strip else 0.05)
        for txt, col in reversed(pills):
            w_ = f_p.measure(txt) + int(H * 0.06)
            rrect(cv, xr - w_, y0 - int(H * 0.06), xr, y0 + int(H * 0.06), int(H * 0.03), fill=C["card2"] if not chroma else C["card"], outline=col, width=2)
            cv.create_text(xr - w_ // 2, y0, text=txt, fill=col, font=f_p); xr -= w_ + int(W * 0.008)
        y1 = int(H * (0.32 if strip else 0.18))
        # ── 토요일: 보스전 보드 ──
        if dt == "b":
            br = bench_readiness(data, dkey); n_t, proj = br["n_today"], br["projected"]
            bl = bench_label(dkey); done = n_t >= 18
            bd = [(d_, e_) for d_, e_ in bench_days(data) if d_ < dkey]
            head = f"{bl} · {n_t}/18"; cv.create_text(pad, y1, text=head, anchor="w", fill=C["sub"], font=fam(0.06))
            big = str(proj) if proj is not None else "—"; f_big = mon(0.30 if not strip else 0.5)
            plate(pad - 8, y1 + int(H * 0.06), pad + f_big.measure(big) + 8, y1 + int(H * 0.06) + int(H * 0.32))
            cv.create_text(pad, y1 + int(H * 0.22), text=big, anchor="w", fill=C["gold"] if done else C["txt"], font=f_big)
            lab = ("확정" if done else "예상") if proj is not None else "첫 판을 치면"
            cv.create_text(pad + f_big.measure(big) + int(W * 0.012), y1 + int(H * 0.22), text=lab, anchor="w", fill=C["sub"], font=fam(0.05))
            if bd and proj is not None:
                d0, e_last = bd[-1]; dlt = proj - e_last; col = C["up"] if dlt > 5 else (C["down"] if dlt < -5 else C["flat"])
                cv.create_text(pad, y1 + int(H * 0.44), text=f"지난 {d0[5:].replace('-', '/')} {e_last} → {proj} ({dlt:+d})", anchor="w", fill=col, font=fam(0.05))
            elif bl == "기준 측정": cv.create_text(pad, y1 + int(H * 0.44), text="출발선을 만드는 중", anchor="w", fill=C["sub"], font=fam(0.05))
            if not strip:                                     # 9갈래 막대 (오른쪽 절반)
                t_ = CUR_TIER[0]; off = TIERS[t_][1]; top = off + 400
                tb = (data["days"].get(dkey) or {}).get("best") or {}; merged = dict(data.get("pb") or {}); merged.update(tb)
                bx = int(W * 0.50); bw = W - bx - pad; rows = SUBS_T[t_]; rh = int((H - y1 - int(H * 0.16)) / len(rows))
                f_b = fam(0.04, False)
                for i, sub in enumerate(rows):
                    y = y1 + i * rh; e = subE(sub, merged, off)
                    cv.create_text(bx, y + rh // 2, text=SUB_KO.get(sub[2], sub[2]), anchor="w", fill=C["sub"], font=f_b)
                    lx = bx + int(bw * 0.28); fill_w = 0 if e is None else int((bw - int(bw * 0.28)) * max(0, min(500, e - off)) / 500)
                    rrect(cv, lx, y + int(rh * 0.25), bx + bw, y + int(rh * 0.75), 4, fill=C["card2"], outline="")
                    if fill_w > 0: rrect(cv, lx, y + int(rh * 0.25), lx + fill_w, y + int(rh * 0.75), 4, fill=C["gold"] if (e or 0) >= top else C["val"], outline="")
                    gx = lx + int((bw - int(bw * 0.28)) * 0.8); cv.create_line(gx, y + int(rh * 0.15), gx, y + int(rh * 0.85), fill=C["gold"], width=2)
                gw_, gn_, _gc = fmt_gate(gate_status(merged)); cv.create_text(pad, H - int(H * 0.08), text=f"{gw_} · {gn_}", anchor="w", fill=C["txt"], font=fam(0.05))
            return
        # ── 일요일: 이번 주 점수판 ──
        if dt == "r":
            lines = [t for t, _st in weekly_recap(data, dkey)][:4]
            gw_, gn_, gc_ = fmt_gate(gate_status(data.get("pb") or {})); lines.append(f"{gw_} · {gn_}" + (f" — {gc_}" if gc_ else ""))
            rr_ = rr_net(data, dkey); lines.append(f"출발선 이후 RR {rr_:+d}" if rr_ else "휴식일 — 손 대신 눈: 랭크 1판 복기 30분")
            f_l = fam(0.07 if not strip else 0.16, False); yy = y1
            for ln in lines[:5 if not strip else 2]:
                fit(f_l, ln, W - 2 * pad); plate(pad - 8, yy - int(H * 0.05), pad + f_l.measure(ln) + 8, yy + int(H * 0.05))
                cv.create_text(pad, yy, text=ln, anchor="w", fill=C["txt"], font=f_l); yy += int(H * (0.13 if not strip else 0.3))
            return
        # ── 발로 데이: 판정 셋 (오늘 히어로 · 요즘 · 관문) ──
        Vd = V["day"]; fc, isv = vcol_bc(Vd)
        gw_, gn_, gc_ = fmt_gate(gate_status(data.get("pb") or {})) if BASELINE[0] else ("기준 측정 전", "", "")
        hero_num = Vd["num"]
        if Vd.get("state") == "wait": hero_num = f"프로브 {len({k_ for k_, _t_, _s_ in cp if k_ in PROBE})}/{len(PROBE)}"
        rc_ = vcol_bc(V["recent"])
        tiles = [("hero", Vd["word"] + (" " + Vd["glyph"] if Vd.get("glyph") else ""), hero_num, fc if isv else C["wait"], Vd["fill"], not isv),
                 ("recent", V["recent"]["word"] + (" " + V["recent"]["glyph"] if V["recent"].get("glyph") else ""), V["recent"]["num"], rc_[0] if rc_[1] else C["wait"], "chip", not rc_[1]),
                 ("gate", gw_, gn_, C["gold"], "chip", False)]
        y2 = int(H * (0.70 if strip else 0.44)); hw = int(W * 0.46); cw = int((W - 2 * pad - hw - 2 * int(W * 0.012)) / 2); x = pad
        for kind, word, num, col, fill_, hold_ in tiles:
            w_ = hw if kind == "hero" else cw; ol = C["line"] if hold_ else col
            if kind == "hero":
                bg = col if fill_ == "solid" else (C["card2"] if not chroma else C["card"]); fg = C["onfill"] if fill_ == "solid" else col
                rrect(cv, x, y1, x + w_, y2, int(H * 0.04), fill=bg, outline=ol if fill_ != "solid" else "", width=2)
            else:
                rrect(cv, x, y1, x + w_, y2, int(H * 0.04), fill=C["card2"] if not chroma else C["card"], outline=ol, width=2); fg = col
            inner = w_ - 2 * int(W * 0.012); cy = (y1 + y2) // 2
            f_n = fit(mon(0.16 if not strip else 0.30), num, int(w_ * 0.40)); f_w = fit(fam(0.11 if not strip else 0.22), word, inner - f_n.measure(num) - int(W * 0.01))
            if f_w.measure(word) + f_n.measure(num) + int(W * 0.01) <= inner:          # 한 줄에 들어가면 말 왼쪽 · 숫자 오른쪽
                cv.create_text(x + int(W * 0.012), cy, text=word, anchor="w", fill=fg, font=f_w)
                cv.create_text(x + w_ - int(W * 0.012), cy, text=num, anchor="e", fill=fg, font=f_n)
            else:                                                                        # 좁은 타일: 말 위 · 숫자 아래 (겹치지 않게)
                f_w2 = fit(fam(0.085 if not strip else 0.16), word, inner); f_n2 = fit(mon(0.11 if not strip else 0.20), num, inner)
                dy = int((y2 - y1) * 0.24)
                cv.create_text(x + int(W * 0.012), cy - dy, text=word, anchor="w", fill=fg, font=f_w2)
                cv.create_text(x + int(W * 0.012), cy + dy, text=num, anchor="w", fill=fg, font=f_n2)
            x += w_ + int(W * 0.012)
        if strip:                                              # 띠 프리셋은 여기까지 (아래 줄은 카드/전체에서만)
            return
        # ── 지금 판 · 직전 점수 · 남은 시간 (+ 신기록 플래시) ──
        ya = int(H * 0.50); yb = int(H * 0.72); ym = (ya + yb) // 2
        cur_k = None
        if seq_alive():
            _dn, _nx, _sc = seq_status()
            if _nx is not None: cur_k = seq_win["seq"][_nx]
        if cp:
            k_, _t_, sc_ = cp[-1]; kind = kinds[-1] if kinds else "new"; col = C[VERDICT_FILL.get(kind, "sub")]
            flash = kind == "pb" and time.monotonic() < bcast.get("flash_until", 0)
            head = ("▶ " + sname(cur_k)) if cur_k else sname(k_)
            f_h = fit(fam(0.14), head, int(W * 0.55)); plate(pad - 8, ym - int(H * 0.09), pad + f_h.measure(head) + 8, ym + int(H * 0.09))
            cv.create_text(pad, ym, text=head, anchor="w", fill=C["txt"], font=f_h)
            sub_ = (f"직전 {sname(k_)} · {VERDICT_NAME.get(kind, '')}" if cur_k else VERDICT_NAME.get(kind, ""))
            cv.create_text(pad, yb + int(H * 0.05), text=sub_, anchor="w", fill=col, font=fam(0.05, False))
            f_s = mon(0.24); sw_ = f_s.measure(str(sc_)) + int(W * 0.02)
            if flash:
                rrect(cv, W - pad - sw_ - int(W * 0.16), ym - int(H * 0.14), W - pad, ym + int(H * 0.14), int(H * 0.04), fill=C["gold"], outline="")
                cv.create_text(W - pad - sw_, ym, text="★ 신기록", anchor="e", fill=C["onfill"], font=fam(0.08))
                cv.create_text(W - pad - int(W * 0.01), ym, text=str(sc_), anchor="e", fill=C["onfill"], font=f_s)
            else:
                plate(W - pad - sw_, ym - int(H * 0.14), W - pad, ym + int(H * 0.14))
                cv.create_text(W - pad - int(W * 0.01), ym, text=str(sc_), anchor="e", fill=col, font=f_s)
        elif cur_k:
            cv.create_text(pad, ym, text="▶ " + sname(cur_k), anchor="w", fill=C["txt"], font=fam(0.14))
            cv.create_text(W - pad, ym, text="첫 판", anchor="e", fill=C["hint"], font=fam(0.12, False))
        else:
            cv.create_text(W / 2, ym, text="첫 판을 치면 여기에 뜹니다", fill=C["hint"], font=fam(0.10, False))
        rem = max(0, plan - len(cp)) if plan else 0; est = remaining_estimate(cp, rem) if rem else None
        tail = (f"남은 {rem}판" + (f" ≈ {est}분 · {(datetime.now() + timedelta(minutes=est)).strftime('%H:%M')}쯤 끝" if est else "")) if rem else ("오늘 계획 끝 ✓" if plan else "")
        top_ = main_theme(dkey, data["pb"])[1] if dt == "v" else DAY_TYPE.get(dt, ("훈련", ""))[0]
        cv.create_text(W - pad, yb + int(H * 0.05), text=f"{top_} · {len(kinds)}/{max(plan, len(kinds))}판", anchor="e", fill=C["sub"], font=fam(0.05, False))
        if tail: cv.create_text(W - pad, yb + int(H * 0.11), text=tail, anchor="e", fill=C["dim"], font=fam(0.045, False))
        # ── 오늘의 띠 ──
        cells = ribbon_cells(plan, kinds); n = max(1, len(cells)); y3, y4 = int(H * 0.86), int(H * 0.97)
        gap = max(1, int(W * 0.0022)); tw = (W - 2 * pad - gap * (n - 1)) / n
        for i, ck in enumerate(cells):
            x1 = pad + i * (tw + gap); h = (y4 - y3) * RIBBON_H.get(ck, 0.56)
            cv.create_rectangle(x1, y4 - h, x1 + tw, y4, fill=C["card2"] if ck == "todo" else C[ck], outline="", width=0)

    def remember_bcast():
        w = bcast["win"]
        if w is not None and w.winfo_exists(): data["win"]["bcast"] = w.winfo_geometry()

    def note_pb_flash(events):
        if events:
            bcast["flash_until"] = time.monotonic() + 1.5
            root.after(1600, update_broadcast)
    def update_broadcast():
        if bcast["win"] is not None and bcast["win"].winfo_exists() and bcast["cv"].winfo_exists():
            draw_broadcast(bcast["cv"])

    def bcast_cfg(): return data.setdefault("bcast", {"preset": "card", "frameless": False, "chroma": False, "open": True})
    def apply_bcast_geometry(w):
        pw, ph = BCAST_PRESETS.get(bcast_cfg().get("preset", "card"), BCAST_PRESETS["card"])
        pos = ""
        g = data["win"].get("bcast") or ""
        if "+" in g: pos = g[g.index("+"):]
        w.geometry(f"{pw}x{ph}{pos}")
    def _drag_start(e): bcast["drag"] = (e.x_root, e.y_root, bcast["win"].winfo_x(), bcast["win"].winfo_y())
    def _drag_move(e):
        d = bcast.get("drag")
        if d: bcast["win"].geometry(f"+{d[2] + e.x_root - d[0]}+{d[3] + e.y_root - d[1]}")
    def open_broadcast():
        w = bcast["win"]; cfg_ = bcast_cfg()
        if w is None or not w.winfo_exists():
            w = tk.Toplevel(root); bcast["win"] = w
            w.title("AimDesk Broadcast")                      # 고정 ASCII 제목 — OBS 창 캡처 소스가 어긋나지 않게
            w.configure(bg="#00FF00" if cfg_.get("chroma") else BC["bg"])
            w.resizable(False, False)
            if cfg_.get("frameless"):
                w.overrideredirect(True)
                w.bind("<ButtonPress-1>", _drag_start); w.bind("<B1-Motion>", _drag_move)
            cv = tk.Canvas(w, bg="#00FF00" if cfg_.get("chroma") else BC["bg"], highlightthickness=0)
            cv.pack(fill="both", expand=True); bcast["cv"] = cv
            cv.bind("<Configure>", lambda e: draw_broadcast(cv))
            def close_b(*_): remember_bcast(); cfg_["open"] = False; save_data(data); w.destroy()
            w.bind("<Escape>", close_b); w.protocol("WM_DELETE_WINDOW", close_b)
            def toggle_full(*_):
                cfg_["preset"] = "full" if cfg_.get("preset") != "full" else bcast.get("prev_preset", "card")
                if cfg_["preset"] == "full": bcast["prev_preset"] = "card"
                save_data(data); apply_bcast_geometry(w)
            w.bind("<F11>", toggle_full)
            apply_bcast_geometry(w)
            cfg_["open"] = True; save_data(data)
        else:
            w.lift()
        update_broadcast()
    def set_bcast(**kw):
        """도구 탭에서 프리셋·프레임·크로마를 바꾸면 창을 다시 연다 (위젯은 만들 때 색이 정해진다)"""
        cfg_ = bcast_cfg(); cfg_.update(kw); save_data(data)
        w = bcast["win"]
        if w is not None and w.winfo_exists():
            remember_bcast(); w.destroy(); bcast["win"] = None; open_broadcast()

    card_win = {"win": None, "cv": None}

    FCARD_H = (FAM, 17, "bold"); FCARD = (FAM, 12); FCARD_C = (FAM, 11, "bold")

    def draw_card(cv, sc):
        """오늘 한 장 — 16:9 한 장. 1280×720 을 기준으로 글자가 창 크기에 비례하므로 스크린샷을 그대로 커뮤니티 글·썸네일에 쓸 수 있다.
        첫 줄은 늘 주인공 줄(DAY N · 골드 2 → 불멸), 가장 큰 글자는 오늘 판정 하나"""
        cv.delete("all")
        W = max(cv.winfo_width(), 320); H = max(cv.winfo_height(), 180); s = W / 1280.0
        f = lambda k, b=False: (FAM, max(8, int(k * s)), "bold") if b else (FAM, max(8, int(k * s)))
        x0 = 56 * s; y = 54 * s; xr = W - x0; bw = W - 2 * x0
        cv.create_text(x0, y, text=sc.get("story") or sc["title"], anchor="w", fill=C["gold"], font=f(28, True))
        cv.create_text(xr, y, text=sc["title"], anchor="e", fill=C["sub"], font=f(20)); y += 66 * s
        if sc.get("verdict"):
            _vw, _vn, _vc = sc["verdict"]; _col = C.get(_vc, C["gold"]) if _vc != "rank" else C["gold"]
            cv.create_text(x0, y, text=_vw, anchor="w", fill=_col, font=f(60, True))
            cv.create_text(xr, y, text=_vn, anchor="e", fill=_col, font=f(60, True)); y += 82 * s
        cv.create_text(x0, y, text=sc["stat"], anchor="w", fill=C["txt"], font=f(26)); y += 48 * s
        cells = ribbon_cells(len(sc["kinds"]), sc["kinds"])
        n = max(1, len(cells)); gap = 3 * s; tw = (bw - gap * (n - 1)) / n; rh = 34 * s
        for i, ck in enumerate(cells):
            x1 = x0 + i * (tw + gap); h = rh * RIBBON_H.get(ck, 0.56); fill = C["card2"] if ck == "todo" else C[ck]
            if tw >= 6: rrect(cv, x1, y + rh - h, x1 + tw, y + rh, min(4 * s, tw / 2, h / 2), fill=fill, outline="")
            else: cv.create_rectangle(x1, y + rh - h, x1 + tw, y + rh, fill=fill, outline="", width=0)
        y += rh + 44 * s
        xc = x0 + bw * 0.56; yl = yr = y                    # 왼쪽: 오늘 바뀐 것 · 오른쪽: 특별편 ★ · 세션 중 상승 · 관문
        cv.create_text(x0, yl, text="오늘 바뀐 것", anchor="w", fill=C["gold"], font=f(22, True)); yl += 40 * s
        lines = sc["changed"][:6] or ["기록이 바뀐 건 없습니다 — 판을 쌓은 것도 그대로 남습니다"]
        for line in lines:
            cv.create_text(x0 + 8 * s, yl, text="· " + _cut(line, 46), anchor="w", fill=C["txt"] if sc["changed"] else C["hint"], font=f(24)); yl += 40 * s
        for st_ in (sc.get("stars") or [])[:3]:
            cv.create_text(xc, yr, text=st_, anchor="w", fill=C["gold"], font=f(26, True)); yr += 44 * s
        if sc["gain"]: cv.create_text(xc, yr, text=sc["gain"], anchor="w", fill=C["ok"], font=f(22)); yr += 40 * s
        if sc.get("gate"): cv.create_text(xc, yr, text="관문 " + sc["gate"], anchor="w", fill=C["sub"], font=f(22)); yr += 40 * s
        if sc["next"]: cv.create_text(x0, H - 44 * s, text=_cut(sc["next"], 60), anchor="w", fill=C["sub"], font=f(20))
        cv.create_text(xr, H - 44 * s, text="아무 곳이나 누르면 닫힘", anchor="e", fill=C["dim"], font=f(15))

    def open_card():
        dkey = today_key[0]; dt = day_state.get("dt", "v")
        sc = session_card(data, dkey, DAY_TYPE[dt][0],
                          main_theme(dkey, data["pb"])[1] if dt == "v" else "", cur_plays())
        CW = max(px(640), min(px(1120), vroot[2] - px(80))); CH = int(CW * 9 / 16)      # 16:9 — 스크린샷이 그대로 썸네일·커뮤니티 글이 된다
        w = card_win["win"]
        if w is None or not w.winfo_exists():
            w = tk.Toplevel(root); card_win["win"] = w
            w.title("오늘 한 장"); w.configure(bg=C["bg"]); w.resizable(False, False)
            cv = tk.Canvas(w, width=CW, height=CH, bg=C["card"], highlightthickness=0)
            cv.pack(padx=px(10), pady=px(10)); card_win["cv"] = cv
            cv.bind("<Button-1>", lambda e: w.destroy())
            w.bind("<Escape>", lambda e: w.destroy())
            w.geometry(clamp_pos("+%d+%d" % (root.winfo_x() + px(60), root.winfo_y() + px(60)),
                                 CW + px(20), CH + px(20), *vroot) or "")
            if seq_alive() and bool(data.get("seq_topmost", True)): w.attributes("-topmost", True)
        else:
            w.lift()
        if int(card_win["cv"].cget("height")) != CH or int(card_win["cv"].cget("width")) != CW: card_win["cv"].configure(width=CW, height=CH)
        card_win["cv"].update_idletasks()
        draw_card(card_win["cv"], sc)

    def add_section(title, extra=None):
        """섹션 하나 = 히어로의 요약 줄(이름 · 6px 막대 · d/t) + 상세 머리글(자세히 안). section_labels[i] = (요약 라벨, 제목, 시작 줄, extra, 막대, 개수 라벨, 상세 머리글)"""
        sm = day_state["summary"]; det = day_state["detail"]
        row = tk.Frame(sm, bg=C["card"])
        if day_state.get("dt") == "b":                                             # 실력 재는 날: 9갈래를 3×3 으로
            i_ = len(section_labels); row.grid(row=i_ // 3, column=i_ % 3, sticky="ew", padx=(0, px(16)), pady=(0, px(6)))
            sm.grid_columnconfigure(i_ % 3, weight=1, uniform="todo")
        else: row.pack(fill="x", pady=(0, px(6)))
        lb = tk.Label(row, text=title, font=FROW, bg=C["card"], fg=C["txt"], anchor="w"); lb.pack(side="left")
        cnt = tk.Label(row, text="", font=FRCNT, bg=C["card"], fg=C["sub"], width=7, anchor="e"); cnt.pack(side="right")
        bar = tk.Canvas(row, width=px(60), height=px(6), bg=C["card"], highlightthickness=0); bar.pack(side="left", fill="x", expand=True, padx=(px(12), px(10)), pady=(px(2), 0))
        f = tk.Frame(det, bg=C["card"]); f.pack(fill="x", pady=(10, 3))
        lb2 = tk.Label(f, text=title, font=FCAP, bg=C["card"], fg=C["gold"]); lb2.pack(side="left")
        tk.Frame(f, bg=C["line"], height=1).pack(side="left", fill="x", expand=True, padx=(10, 0), pady=1)
        section_labels.append((lb, title, len(routine_rows), extra, bar, cnt, lb2))

    def add_row(kind, key, target):
        row = tk.Frame(day_state["detail"], bg=C["card"]); row.pack(fill="x", pady=2)
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
        sl = tk.Label(row, text="", font=FNS, width=24 if kind == "bench" else (22 if TRAINER["targets"] else 12), anchor="e", bg=C["card"], fg=C["dim"])
        sl.pack(side="left")
        routine_rows.append((kind, key, target, bar, cl, sl, gc, mark, nml, row))

    def set_routine_open(v, save=True):
        """'자세히' — 시나리오별 줄(진행바·점수)을 펼치거나 접는다. 기본 접힘(시청자 화면은 요약 4줄이면 충분)"""
        det = day_state.get("detail"); tg_ = day_state.get("toggle")
        if det is None or not det.winfo_exists(): return
        v = bool(v); day_state["open"] = v
        if v:
            det.pack(fill="x", pady=(4, 0), before=day_state["sess_cv"])
            if not cols.winfo_ismapped(): cols.pack(fill="both", expand=True, pady=(px(10), 0))
        else:
            det.pack_forget(); cols.pack_forget()
        if tg_ is not None and tg_.winfo_exists(): cfg(tg_, text=("접기 ▴" if v else "자세히 ▾  시나리오별 점수 · 오늘 곡선 · 코치 메모 · 발로란트 랭크 · 트레이너"))
        if save and bool(data["win"].get("routine_open")) != v:
            data["win"]["routine_open"] = v; save_data(data)
        dirty["today"] = True; root.after(60, lambda: refresh_tab("today"))

    def build_day_ui():
        """헤더의 날짜·요일 칩과 좌측 루틴 카드를 '오늘' 기준으로 (다시) 만든다. 판정 밴드·라이브 스트립은 고정 위젯이라 내용만 바뀐다"""
        d = today_date(); dkey = today_key[0]
        dt = day_type_of(dkey)
        day_state["dt"] = dt
        day_state["pl"] = {"v": "AIMDESK Day", "b": "AIMDESK Bench"}.get(dt)
        dt_name, dt_col = DAY_TYPE[dt]
        date_lbl.configure(text=f"{d.month}월 {d.day}일 {DOWK[d.weekday()]} · " + (("출발선 재는 날" if bench_label(dkey) == "기준 측정" else DAY_WORD["b"]) if dt == "b" else DAY_WORD.get(dt, "훈련하는 날")),
                           fg=C["gold"] if dt == "b" else C["sub"])
        daych.delete("all")
        rrect(daych, 0, 1, px(68), px(17), 8, fill=dt_col, outline="")
        daych.create_text(px(34), px(9), text=dt_name, fill=C["onfill"], font=(FAM, 8, "bold"))

        for w_ in left_scroll.body.winfo_children(): w_.destroy()
        for w_ in todo_host.winfo_children(): w_.destroy()
        for c_ in range(3): todo_host.grid_columnconfigure(c_, weight=0, uniform="")
        routine_rows.clear(); section_labels.clear(); routine_next[0] = None
        day_state["rib_cells"] = []; day_state["val_auto_opened"] = False; day_state["val_row"] = None; day_state["val_open"] = None
        body_ = left_scroll.body; pl = day_state["pl"]
        if TRAINER["targets"] or TRAINER["note"]:
            tl_ = tk.Label(body_, text=(f"트레이너 목표 {len(TRAINER['targets'])}개" if TRAINER["targets"] else "") + (" · 메모" if TRAINER["note"] else ""),
                           font=FCAP, bg=C["card"], fg=C["ok"], cursor="hand2")
            tl_.pack(anchor="w"); tl_.bind("<Button-1>", lambda e: show("tools"))
        if TRAINER["note"]:
            tk.Label(body_, text="트레이너 메모 · " + TRAINER["note"], font=FB, bg=C["card"], fg=C["ok"], wraplength=px(420), justify="left").pack(anchor="w", pady=(2, 0))
        day_state["chal"] = daily_challenge(data, dkey, data["pb"])
        day_state["chal_lbl"] = None
        if day_state["chal"]:
            cf = tk.Frame(body_, bg=C["card2"], highlightbackground=C["gold"], highlightthickness=1)
            cf.pack(fill="x", pady=(8, 0), ipady=px(5), ipadx=px(8))
            day_state["chal_lbl"] = tk.Label(cf, text="", font=FB, bg=C["card2"], fg=C["gold"], wraplength=px(520), justify="left", anchor="w")
            day_state["chal_lbl"].pack(fill="x", padx=px(8))
        # 히어로 안의 ①②③④ — 상세(시나리오별 줄)는 자세히 안
        det = tk.Frame(body_, bg=C["card"]); day_state["detail"] = det
        if dt == "v":
            add_section("① 손 풀기 · 2판 (점수 안 봄)")
            for k, n in WARMUP: add_row("warm", k, n)
            add_section("② 오늘 점수 재기 · 6판")
            tk.Label(todo_host, text="오늘 점수 재기 = 손 푼 뒤 처음 6판의 첫 점수가 오늘 점수예요", font=FS11, bg=C["card"], fg=C["hint"], anchor="w").pack(fill="x", padx=(px(18), 0), pady=(0, px(6)))
            for k in PROBE: add_row("probe", k, 1)
            mt = main_theme(dkey, data["pb"])
            add_section(f"③ 본훈련 · 12판 · {mt[1]}" + (" (트레이너 지정)" if TRAINER["themes"].get(dkey) else ""))
            for k, n in mt[3]: add_row("main", k, n)
            # ④ 발로란트 — 헤더 한 줄 + '적기 ▾' 를 열면 숫자 4칸
            val_row = tk.Frame(todo_host, bg=C["card"]); val_row.pack(fill="x", pady=(px(2), 0)); day_state["val_row"] = val_row
            vh = tk.Frame(val_row, bg=C["card"]); vh.pack(fill="x")
            tk.Label(vh, text="④ 발로란트 · 15분 (사격장 3 → 카운터 스트레이프 3 → 데스매치 9)", font=FROW, bg=C["card"], fg=C["txt"], anchor="w").pack(side="left")
            open_lnk = tk.Label(vh, text="적기 ▾", font=FLINK, bg=C["card"], fg=C["hint"], cursor="hand2"); open_lnk.pack(side="right")
            val_status = tk.Label(vh, text="시작 전", font=FRCNT, bg=C["card"], fg=C["sub"]); val_status.pack(side="right", padx=(0, px(14)))
            vbox = tk.Frame(val_row, bg=C["card"])
            for _ln in ("사격장 · 하드 · 스트레이핑 켬 · 30개 ×2회 → 맞힌 수 (3분)",
                        "카운터 스트레이프 3분 — A/D 이동 → 반대키 탭 → 정지 → 헤드 1발, 봇 무한",
                        "데스매치 1판 · 밴달 고정 · 크로스헤어 머리 높이 · 3발 초과 금지 → K · D · HS% (9분)"):
                tk.Label(vbox, text=_ln, font=FS11, bg=C["card"], fg=C["hint"], wraplength=px(800), justify="left").pack(anchor="w")
            vrow = tk.Frame(vbox, bg=C["card"]); vrow.pack(anchor="w", pady=(px(6), 0))
            val_vars = {}
            for _k, _lbl, _w in (("range", "사격장 맞힌 수 /30", 3), ("dm_k", "데스매치 킬", 3), ("dm_d", "데스", 3), ("dm_hs", "헤드샷 %", 4)):
                cell_ = tk.Frame(vrow, bg=C["card"]); cell_.pack(side="left", padx=(0, px(14)))
                tk.Label(cell_, text=_lbl, font=FS11, bg=C["card"], fg=C["sub"]).pack(anchor="w")
                _v = tk.StringVar(); val_vars[_k] = _v
                _e = tk.Entry(cell_, textvariable=_v, width=_w, font=(MONO, 16, "bold"), bg=C["card2"], fg=C["txt"], insertbackground=C["txt"], bd=0,
                              highlightthickness=1, highlightbackground=C["line"], highlightcolor=C["gold"], justify="center")
                _e.pack(anchor="w", ipady=px(6)); _e.bind("<Return>", lambda e: commit_val()); _e.bind("<FocusOut>", lambda e: commit_val())
            skip_lbl = tk.Label(vbox, text="오늘은 건너뜀", font=FLINK, bg=C["card"], fg=C["dim"], cursor="hand2"); skip_lbl.pack(anchor="w", pady=(px(4), 0))
            def val_open(v_):
                if v_ and not vbox.winfo_ismapped(): vbox.pack(fill="x", pady=(px(6), 0)); cfg(open_lnk, text="접기 ▴")
                elif not v_ and vbox.winfo_ismapped(): vbox.pack_forget(); cfg(open_lnk, text="적기 ▾")
            open_lnk.bind("<Button-1>", lambda e: val_open(not vbox.winfo_ismapped()))
            day_state["val_open"] = val_open
            def sync_val():
                dy_ = data["days"].get(today_key[0], blank_day()); v = dy_.get("val") or {}
                for _k, _v in val_vars.items():
                    x = v.get(_k); _v.set("" if x is None else (f"{x:g}" if isinstance(x, float) else str(x)))
                if v.get("skip"): cfg(val_status, text="건너뜀", fg=C["dim"])
                elif val_done(dy_): cfg(val_status, text=fmt_val(dy_), fg=C["ok"])
                else: cfg(val_status, text="시작 전", fg=C["sub"])
                cfg(skip_lbl, text="건너뜀 취소" if v.get("skip") else "오늘은 건너뜀")
            def commit_val(*_):
                v = data["days"].setdefault(today_key[0], blank_day()).setdefault("val", dict(blank_day()["val"]))
                for _k, _v in val_vars.items():
                    t_ = _v.get().strip().replace("%", "")
                    try: v[_k] = None if not t_ else (float(t_) if _k == "dm_hs" else int(t_))
                    except ValueError: pass
                save_data(data); sync_val(); refresh()
            def toggle_skip(*_):
                v = data["days"].setdefault(today_key[0], blank_day()).setdefault("val", dict(blank_day()["val"]))
                v["skip"] = not v.get("skip"); save_data(data); sync_val(); refresh()
            skip_lbl.bind("<Button-1>", toggle_skip)
            day_state["val_vars"] = val_vars; day_state["commit_val"] = commit_val; day_state["sync_val"] = sync_val
            sync_val()
        elif dt == "b":
            for i, (sid, cat, sub, items) in enumerate(SUBS):
                add_section(f"{'①②③④⑤⑥⑦⑧⑨'[i]} {cat} · {sub}")
                for k, _th in items: add_row("bench", k, 1)
        day_state["off_lbl"] = tk.Label(todo_host, text="", font=FROW, bg=C["card"], fg=C["gold"], wraplength=px(900), justify="left", anchor="w")   # 내용이 있을 때만 pack
        if dt == "b": day_state["off_lbl"].grid(row=3, column=0, columnspan=3, sticky="ew"); day_state["off_lbl"].grid_remove()
        # 자세히 안: 안내 · 코치 두 줄 · 시나리오별 줄 · 오늘 곡선
        _tl = theme_line(dkey, data["pb"])
        if _tl: tk.Label(det, text=_tl, font=FB, bg=C["card"], fg=C["gold"], wraplength=px(520), justify="left").pack(anchor="w", pady=(4, 0))
        _wt = week_themes(dkey, data["pb"])
        if _wt: tk.Label(det, text=_wt, font=FS, bg=C["card"], fg=C["dim"], wraplength=px(520), justify="left").pack(anchor="w")
        if pl:
            tk.Label(det, text=f"코박스 ESC → 샌드박스 브라우저 → 네 번째 탭 '로컬 재생 목록' → {pl} ▶ 플레이 ('도전 과제' 토글). "
                               "판이 끝나면 앱이 NEXT 키를 대신 누릅니다 — 결과창에선 기다리기",
                     font=FS, bg=C["card"], fg=C["hint"], wraplength=px(520), justify="left").pack(anchor="w", pady=(2, 4))
        if dt == "b":
            tk.Label(det, text=(("출발선 재기 — 18개를 한 판씩. 여기서 나온 점수가 앞으로 성장을 재는 출발선이 됩니다"
                                 if bench_label(dkey) == "기준 측정" else
                                 "실력 재는 날 — 18개 한 판씩 · 오늘 베스트 기준 · 점수 옆은 다음 등급까지 남은 점수 · 벤치 탭에 실시간 반영")),
                     font=FS, bg=C["card"], fg=C["hint"], wraplength=px(520), justify="left").pack(anchor="w", pady=(6, 0))
        elif dt == "r":
            tk.Label(det, text="손목도 데이터의 일부입니다. 오늘은 컨디션만 적어도 됩니다.", font=F, bg=C["card"], fg=C["sub"]).pack(anchor="w", pady=6)
        day_state["coach"] = []
        for _i in range(2):
            cl_ = tk.Label(body_, text="", font=FS, bg=C["card"], fg=C["sub"], wraplength=px(520), justify="left")
            cl_.pack(anchor="w", pady=(2, 0)); day_state["coach"].append(cl_)
        day_state["sess_cv"] = tk.Canvas(body_, height=px(170), bg=C["card"], highlightthickness=0)     # 오늘 세션 곡선 (성장 탭과 같은 그림)
        day_state["sess_cv"].pack(fill="x", pady=(10, 0)); tab_of[day_state["sess_cv"]] = "today"; day_state["sess_cv"].bind("<Configure>", on_resize)
        set_routine_open(bool(data["win"].get("routine_open")), save=False)

    # 컨디션 — 발밑 줄 오른쪽 (카드가 아니라 한 줄). 랭크 피드백·트레이너 미니는 '자세히'의 오른쪽 열
    rowc = cond_row
    tk.Label(rowc, text="수면", font=FLINK, bg=C["bg"], fg=C["sub"]).pack(side="left")
    sleep_var = tk.StringVar()
    ent = tk.Entry(rowc, textvariable=sleep_var, width=4, font=FRCNT, bg=C["card2"], fg=C["txt"],
                   insertbackground=C["txt"], bd=0, justify="center")
    ent.pack(side="left", padx=(6, 0), ipady=3)
    tk.Label(rowc, text="시간", font=FLINK, bg=C["bg"], fg=C["sub"]).pack(side="left", padx=(4, 0))
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
    tk.Label(rowc, text="체감", font=FLINK, bg=C["bg"], fg=C["sub"]).pack(side="left", padx=(px(14), 0))
    seg = Segmented(rowc, lambda: dget()["cond"]["feel"],
                    lambda v: (dget()["cond"].__setitem__("feel", v), save_data(data), refresh()))
    seg.pack(side="left", padx=(8, 0))

    # ── 랭크 피드백 (선택) — 루틴이 아니다. 랭크를 돌린 날만 펼쳐서 티어·RR·죽은 이유를 적는다 ──
    rk = card(rbody); rk.pack(fill="x", pady=(0, 10))
    rk_head = tk.Label(rk, text="", font=FB, bg=C["card"], fg=C["txt"], cursor="hand2", anchor="w"); rk_head.pack(fill="x")
    rk_body = tk.Frame(rk, bg=C["card"])
    drawer = {"open": False}
    def set_drawer(v):
        """v6: 접히지 않는다 — 숨어 있던 다섯 칸은 3일 만에 안 쓰게 된다. 항상 펼쳐 두고 헤더는 이름만"""
        drawer["open"] = True
        rk_body.pack(fill="x", pady=(6, 0))
        cfg(rk_head, text="발로란트 오늘")
    rk_head.bind("<Button-1>", lambda e: set_drawer(not drawer["open"]))
    tk.Label(rk_body, text="랭크 돌린 날만 — 티어 · RR · 판 수 · 가장 많이 죽은 이유 하나",
             font=FS, bg=C["card"], fg=C["hint"], wraplength=px(300), justify="left").pack(anchor="w")
    tg2 = None                                                # v6.1: '랭크 2판' 토글 제거 — 판 수 칸이 그 자리
    rrow = tk.Frame(rk_body, bg=C["card"]); rrow.pack(fill="x", pady=(4, 2))
    tk.Label(rrow, text="티어", font=FS, bg=C["card"], fg=C["sub"]).pack(side="left")
    tier_var = tk.StringVar(); rr_var = tk.StringVar()
    tier_ent = tk.Entry(rrow, textvariable=tier_var, width=9, font=FN, bg=C["card2"], fg=C["txt"], insertbackground=C["txt"], bd=0, justify="center")
    tier_ent.pack(side="left", padx=(6, 0), ipady=4)
    tk.Label(rrow, text="RR 변화", font=FS, bg=C["card"], fg=C["sub"]).pack(side="left", padx=(10, 0))
    rr_ent = tk.Entry(rrow, textvariable=rr_var, width=5, font=FN, bg=C["card2"], fg=C["txt"], insertbackground=C["txt"], bd=0, justify="center")
    rr_ent.pack(side="left", padx=(6, 0), ipady=4)
    grow_ = tk.Frame(rk_body, bg=C["card"]); grow_.pack(fill="x", pady=(4, 2))
    tk.Label(grow_, text="판 수", font=FS, bg=C["card"], fg=C["sub"]).pack(side="left")
    games_var = tk.IntVar(value=0); games_lbl = tk.Label(grow_, text="0", font=FN, bg=C["card2"], fg=C["txt"], width=3)
    def _games(d_):
        games_var.set(max(0, min(9, games_var.get() + d_))); cfg(games_lbl, text=str(games_var.get())); commit_rank()
    RBtn(grow_, "−", lambda: _games(-1), padx=8, pady=2).pack(side="left", padx=(6, 0))
    games_lbl.pack(side="left", padx=4, ipady=3)
    RBtn(grow_, "+", lambda: _games(+1), padx=8, pady=2).pack(side="left")
    tk.Label(rk_body, text="가장 많이 죽은 이유", font=FS, bg=C["card"], fg=C["sub"]).pack(anchor="w", pady=(6, 2))
    why_row = tk.Frame(rk_body, bg=C["card"]); why_row.pack(anchor="w")
    why_var = tk.StringVar(value=""); why_btns = {}
    WHY = (("aim", "에임"), ("pos", "피크·위치"), ("dec", "정보·판단"), ("util", "유틸"))
    def set_why(k_):
        why_var.set("" if why_var.get() == k_ else k_); commit_rank()
        for kk, bb in why_btns.items(): bb.restyle(bg=C["gold"] if kk == why_var.get() else C["card2"], fg=C["onfill"] if kk == why_var.get() else C["txt"])
    for k_, nm_ in WHY:
        b_ = RBtn(why_row, nm_, (lambda k_=k_: set_why(k_)), padx=7, pady=3); b_.pack(side="left", padx=(0, 4)); why_btns[k_] = b_
    def sync_rank_entry():
        rk_ = dget().get("rank") or {}
        tier_var.set(str(rk_.get("tier") or "")); rr_var.set("" if rk_.get("rr") is None else f"{int(rk_['rr']):+d}")
        try: games_var.set(int(rk_.get("games") or 0))
        except (TypeError, ValueError): games_var.set(0)
        cfg(games_lbl, text=str(games_var.get()))
        why_var.set(rk_.get("why") or "")
        for kk, bb in why_btns.items(): bb.restyle(bg=C["gold"] if kk == why_var.get() else C["card2"], fg=C["onfill"] if kk == why_var.get() else C["txt"])
        rr_ent.configure(fg=C["txt"])
    def commit_rank(*_):
        v = rr_var.get().strip().replace("＋", "+").replace("−", "-")
        try:
            rr_v = int(v) if v else None
            dget()["rank"] = {"tier": tier_var.get().strip(), "rr": rr_v, "games": int(games_var.get()), "why": why_var.get() or ""}
            save_data(data); rr_ent.configure(fg=C["txt"]); dirty.__setitem__("log", True)
        except ValueError:
            rr_ent.configure(fg=C["val"])
    for _e in (tier_ent, rr_ent): _e.bind("<Return>", commit_rank); _e.bind("<FocusOut>", commit_rank)
    sync_rank_entry(); set_drawer(True)
    steppers = []; dth_lbl = None                          # v6.1: 죽음 4칸 스텝퍼 제거 — '가장 많이 죽은 이유' 칩 하나가 그 자리 (옛 기록의 deaths 는 그대로 읽는다)
    def sync_deaths_lbl(): pass
    set_drawer(False)

    # ── 트레이너 미니 — 오늘 목표 요약 한 줄 + 도구 탭으로 ──
    tm = card(rbody); tm.pack(fill="x", pady=(0, 10))
    tk.Label(tm, text="트레이너", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w")
    trainer_mini = tk.Label(tm, text="", font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left"); trainer_mini.pack(anchor="w", pady=(3, 6))
    tmr = tk.Frame(tm, bg=C["card"]); tmr.pack(anchor="w")
    RBtn(tmr, "답장 붙여넣기 →", lambda: (show("tools"), trainer_txt.focus_set()), padx=10, pady=5).pack(side="left")
    RBtn(tmr, "오늘 기록 저장", lambda: save_report_today(True), padx=10, pady=5).pack(side="left", padx=(8, 0))

    stc = card(tcol2); stc.pack(fill="x")
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
    vc = card(tcol2); vc.pack(fill="x", pady=(10, 0))
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
            b.restyle(bg=C["gold"] if on else C["card2"], fg=C["onfill"] if on else C["txt"])

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
    trow_t = tk.Frame(vc, bg=C["card"]); trow_t.pack(anchor="w", pady=(8, 0))
    tk.Label(trow_t, text="테마", font=FS, bg=C["card"], fg=C["sub"]).pack(side="left")
    theme_btns = {}
    def set_theme(name):
        if data.get("theme", "light") == name: return
        data["theme"] = name; save_data(data)
        if not restart_app(): show_toast("테마는 다시 켜면 적용됩니다")
    for _n, _l in (("light", "밝음"), ("dark", "어두움")):
        _b = RBtn(trow_t, _l, (lambda n=_n: set_theme(n)), padx=10, pady=3); _b.pack(side="left", padx=(6, 0)); theme_btns[_n] = _b
    theme_btns[data.get("theme", "light") if data.get("theme") in ("light", "dark") else "light"].restyle(bg=C["gold"], fg=C["onfill"])
    RBtn(vc, "방송 화면 열기 (Ctrl+B)", open_broadcast, bg=C["ok_bg"], fg=C["ok"], padx=12, pady=6).pack(anchor="w", pady=(8, 0))
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
    brow2 = tk.Frame(vc, bg=C["card"]); brow2.pack(anchor="w", pady=(6, 0))
    Toggle(brow2, "루틴 실행 때 순서창 띄우기", lambda: bool(data.get("seq_popup")),
           lambda v: (data.__setitem__("seq_popup", bool(v)), save_data(data))).pack(side="left")
    tk.Label(vc, text="끄면(기본) 순서창 없이 앱이 NEXT 키만 대신 누릅니다 — 진행은 오늘 탭 라이브 줄에. '순서 보기'로 언제든 열 수 있습니다.",
             font=FS, bg=C["card"], fg=C["dim"], wraplength=px(268), justify="left").pack(anchor="w", pady=(4, 0))
    tk.Label(vc, text="방송 모드: 흐린 회색 글씨를 밝히고 빨강을 연하게 — 영상으로 넘어가면 어두운 색부터 뭉갭니다.\n"
                      "OBS 는 '창 캡처'로 이 창만 담으면 게임 화면과 따로 크기를 맞출 수 있습니다.",
             font=FS, bg=C["card"], fg=C["dim"], wraplength=px(268), justify="left").pack(anchor="w", pady=(7, 0))
    # ── 트레이너: 하루 기록 → 텍스트 → 답장 붙여넣기 ──
    tcd = card(tcol1); tcd.pack(fill="x")
    tk.Label(tcd, text="트레이너", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 4))
    tk.Label(tcd, text="루틴을 마치면 그날 기록이 '기록' 폴더에 텍스트로 저장됩니다. 답장(목표·테마·메모)은 세 갈래 중 어디서 와도 같은 자리에 적용됩니다 — "
                       "① 자동 코치(앱 규칙) ② AI 코치(Claude) ③ 사람 트레이너 답장 붙여넣기.",
             font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left").pack(anchor="w", pady=(0, 7))
    coach_cfg = data.setdefault("coach", {})
    for _k, _v in (("auto", True), ("ai_key", ""), ("ai_auto", False), ("last", ""), ("last_ai", ""), ("ask", ""), ("notes", {})): coach_cfg.setdefault(_k, _v)
    crow = tk.Frame(tcd, bg=C["card"]); crow.pack(anchor="w")
    Toggle(crow, "자동 코치", lambda: bool(coach_cfg.get("auto", True)), lambda v: (coach_cfg.__setitem__("auto", bool(v)), save_data(data))).pack(side="left")
    tk.Label(crow, text="앱이 매일 기록을 보고 목표 · 내일 테마 · 메모를 정합니다 (인터넷 없음)", font=FS, bg=C["card"], fg=C["hint"], wraplength=px(170), justify="left").pack(side="left", padx=(8, 0))
    coach_lbl = tk.Label(tcd, text="", font=FS, bg=C["card"], fg=C["ok"], wraplength=px(268), justify="left"); coach_lbl.pack(anchor="w", pady=(2, 0))
    def auto_coach_now(reason="manual"):
        """규칙 코치 — 시작 때 한 번 · 루틴이 끝나면 한 번 (같은 날 같은 이유로는 다시 돌지 않는다)"""
        if not coach_cfg.get("auto", True): return False
        tag = f"{today_key[0]}:{reason}"
        if reason != "manual" and coach_cfg.get("last") == tag: return False
        coach_cfg["last"] = tag
        try: txt = auto_coach(data, today_key[0], cur_plays(), day_state.get("dt"))
        except Exception: log_exc("auto_coach"); txt = ""
        if not txt:
            save_data(data); cfg(coach_lbl, text="자동 코치: 아직 정할 게 없습니다 — 평소 범위(판 4개 이상)가 생기면 목표를 냅니다", fg=C["hint"]); return False
        p = trainer_apply(data, txt, today_key[0]); save_data(data); replan_today(); set_trainer_status(p)
        cfg(coach_lbl, text="자동 코치 · " + txt.replace("\n", " · "), fg=C["ok"])
        if reason != "start": show_toast("자동 코치 적용 ✓ " + txt.split("\n")[0] + (" …" if "\n" in txt else ""))
        return True
    tk.Label(tcd, text="AI 코치 (선택) — 오늘 기록 · 지난 코치 노트 · 이번 주 결산을 Claude 에 보내 코치 노트(오늘 한 줄 · 잘된 것 · 아쉬운 것 · 내일 이렇게 · 발로란트로 연결 · 이번 주 흐름)를 받고, 목표·테마·메모는 그대로 적용합니다. API 키는 console.anthropic.com 에서 (유료 · 한 번에 몇 십~백 원)",
             font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left").pack(anchor="w", pady=(10, 0))
    akrow = tk.Frame(tcd, bg=C["card"]); akrow.pack(fill="x", pady=(4, 0))
    tk.Label(akrow, text="API 키", font=FS, bg=C["card"], fg=C["sub"]).pack(side="left")
    ai_key_var = tk.StringVar(value=coach_cfg.get("ai_key") or "")
    ai_key_ent = tk.Entry(akrow, textvariable=ai_key_var, show="•", font=FS, bg=C["card2"], fg=C["txt"], insertbackground=C["txt"], relief="flat")
    ai_key_ent.pack(side="left", fill="x", expand=True, padx=(6, 0), ipady=3)
    def _save_ai_key(*_): coach_cfg["ai_key"] = ai_key_var.get().strip(); save_data(data)
    ai_key_ent.bind("<FocusOut>", _save_ai_key); ai_key_ent.bind("<Return>", _save_ai_key)
    tk.Label(tcd, text="코치에게 (선택) — 내 사정·질문. 매번 같이 보내고 코치가 노트 안에서 답합니다 (예: 감도 0.35 · 800dpi / 손목이 뻐근함 / 플릭이 자꾸 넘어감)",
             font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left").pack(anchor="w", pady=(6, 0))
    ask_txt = tk.Text(tcd, height=3, width=28, font=FS, bg=C["card2"], fg=C["txt"], insertbackground=C["txt"], bd=0, wrap="word", padx=6, pady=4, undo=True)
    ask_txt.insert("1.0", coach_cfg.get("ask") or ""); ask_txt.pack(fill="x", pady=(3, 0))
    def _save_ask(*_):
        v_ = ask_txt.get("1.0", "end").strip()
        if v_ != (coach_cfg.get("ask") or ""): coach_cfg["ask"] = v_; save_data(data)
    ask_txt.bind("<FocusOut>", _save_ask)
    arow = tk.Frame(tcd, bg=C["card"]); arow.pack(anchor="w", pady=(6, 0))
    Toggle(arow, "루틴 끝나면 자동으로", lambda: bool(coach_cfg.get("ai_auto")), lambda v: (coach_cfg.__setitem__("ai_auto", bool(v)), save_data(data))).pack(side="left")
    ai_lbl = tk.Label(tcd, text="", font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left"); ai_lbl.pack(anchor="w", pady=(3, 0))
    note_win = {"win": None, "txt": None, "title": None, "dkey": None}
    def open_coach_note(dkey=None):
        """AI 코치 노트 창 — 오늘 것이 없으면 마지막 것. 제목 줄은 금색, 앱 적용 줄은 흐리게"""
        notes = coach_cfg.get("notes") or {}
        dkey = dkey or today_key[0]
        if not notes.get(dkey):
            if not notes: show_toast("아직 코치 노트가 없습니다 — 설정 탭 트레이너 카드에서 '지금 답장 받기'", "warn"); return False
            dkey = sorted(notes)[-1]
        n_ = notes[dkey]
        w = note_win["win"]
        if w is None or not w.winfo_exists():
            w = tk.Toplevel(root); note_win["win"] = w; w.title("AI 코치 노트"); w.configure(bg=C["bg"])
            W_, H_ = px(640), px(680)
            w.geometry(clamp_pos(f"{W_}x{H_}+{root.winfo_x() + px(80)}+{root.winfo_y() + px(50)}", W_, H_, *vroot) or f"{W_}x{H_}")
            hd_ = tk.Frame(w, bg=C["bg"], padx=px(14), pady=px(10)); hd_.pack(fill="x")
            note_win["title"] = tk.Label(hd_, text="", font=FB, bg=C["bg"], fg=C["txt"]); note_win["title"].pack(side="left")
            RBtn(hd_, "닫기", w.destroy, padx=10, pady=4).pack(side="right")
            RBtn(hd_, "파일 열기", lambda: open_uri(str(coach_note_path(data, note_win["dkey"]))), padx=10, pady=4).pack(side="right", padx=(0, 8))
            RBtn(hd_, "복사", lambda: (root.clipboard_clear(), root.clipboard_append(note_win["txt"].get("1.0", "end").strip()), show_toast("코치 노트 복사 ✓")), padx=10, pady=4).pack(side="right", padx=(0, 8))
            bd_ = tk.Frame(w, bg=C["card"], highlightbackground=C["line"], highlightthickness=1); bd_.pack(fill="both", expand=True, padx=px(14), pady=(0, px(14)))
            txt_ = tk.Text(bd_, font=F, bg=C["card"], fg=C["txt"], wrap="word", bd=0, padx=px(16), pady=px(12), spacing1=2, spacing3=3, cursor="arrow")
            sb_ = tk.Scrollbar(bd_, command=txt_.yview); sb_.pack(side="right", fill="y"); txt_.pack(side="left", fill="both", expand=True); txt_.configure(yscrollcommand=sb_.set)
            txt_.tag_configure("h", font=FB, foreground=C["gold"], spacing1=px(12)); txt_.tag_configure("app", foreground=C["hint"], font=FS); txt_.tag_configure("meta", foreground=C["dim"], font=FS)
            note_win["txt"] = txt_; w.bind("<Escape>", lambda e: w.destroy())
        else: w.lift()
        note_win["dkey"] = dkey; txt_ = note_win["txt"]
        cfg(note_win["title"], text=f"AI 코치 노트 · {dkey}" + (f" · {n_.get('at')}" if n_.get("at") else ""))
        txt_.configure(state="normal"); txt_.delete("1.0", "end")
        for ln in str(n_.get("text") or "").splitlines():
            st_ = ln.strip()
            if st_.startswith("[") and st_.endswith("]"): txt_.insert("end", st_ + "\n", "h")
            elif st_: txt_.insert("end", st_ + "\n")
        ap_ = str(n_.get("apply") or "").strip()
        if ap_ and ap_ != str(n_.get("text") or "").strip():
            txt_.insert("end", "\n앱에 적용한 줄\n", "meta"); txt_.insert("end", ap_ + "\n", "app")
        txt_.configure(state="disabled"); return True
    import queue, threading                                   # (발로란트 연동 카드가 뒤에서 다시 들여오지만, 이 카드가 먼저 만들어진다)
    ai_q = queue.Queue(); ai_busy = [False]
    def _ai_poll():
        try: ok, msg, _usage = ai_q.get_nowait()
        except queue.Empty: root.after(200, _ai_poll); return
        ai_busy[0] = False
        if ok:
            note_, apply_ = ai_coach_split(msg)
            p = trainer_apply(data, apply_, today_key[0])
            at_ = datetime.now().strftime("%H:%M")
            notes = coach_cfg.setdefault("notes", {}); notes[today_key[0]] = {"text": note_, "apply": apply_, "at": at_}
            for k_ in sorted(notes)[:-30]: notes.pop(k_, None)                     # 30일치만
            try: save_coach_note(data, today_key[0], note_, apply_)
            except Exception: log_exc("save_coach_note")
            save_data(data); replan_today(); set_trainer_status(p)
            n_ = len(p["targets"]) + len(p["themes"]) + (1 if p["note"] else 0) + (1 if p["challenge"] else 0)
            has_note = any(h_ in note_ for h_ in COACH_SECTIONS)
            cfg(ai_lbl, text=f"AI 코치 노트 ✓ {at_} · " + (f"목표 {len(p['targets'])}개" + (" · 테마" if p["themes"] else "") + (" · 메모" if p["note"] else "") if n_ else "적용할 줄 없음") + " — '코치 노트 보기'", fg=C["ok"] if (n_ or has_note) else C["val"])
            dirty["today"] = True; dirty["cal"] = True; root.after(60, lambda: refresh_tab("today"))
            if ai_reason[0] == "manual": open_coach_note()
            else: show_toast("AI 코치 노트 도착 ✓ — 오늘 탭 '코치 노트' 에서 읽으세요" + (f" · 목표 {len(p['targets'])}개 적용" if p["targets"] else ""), "ok")
        else:
            cfg(ai_lbl, text="AI 코치 실패 — " + msg, fg=C["val"]); show_toast("AI 코치 실패 — " + msg, "warn")
    ai_reason = ["manual"]
    def ai_coach_now(reason="manual"):
        if ai_busy[0]: return False
        _save_ai_key(); _save_ask(); ai_reason[0] = reason
        if not coach_cfg.get("ai_key"):
            if reason == "manual": show_toast("API 키를 먼저 넣으세요 (console.anthropic.com)", "warn")
            return False
        tag = f"{today_key[0]}:{reason}"
        if reason != "manual" and coach_cfg.get("last_ai") == tag: return False
        coach_cfg["last_ai"] = tag; save_data(data)
        cfg(ai_lbl, text="AI 코치에게 보내는 중… (1분 안팎)", fg=C["hint"]); ai_busy[0] = True
        dk_, cp_, dt_, key_, ask_ = today_key[0], cur_plays(), day_state.get("dt"), coach_cfg["ai_key"], coach_cfg.get("ask") or ""
        def work():
            try: ai_q.put(ai_coach(data, dk_, cp_, dt_, key_, ask=ask_))
            except Exception as e: log_exc("ai_coach"); ai_q.put((False, f"{type(e).__name__}: {e}", None))
        threading.Thread(target=work, daemon=True).start(); root.after(200, _ai_poll)
        return True
    RBtn(arow, "지금 답장 받기", lambda: ai_coach_now("manual"), padx=10, pady=4).pack(side="left", padx=(8, 0))
    RBtn(arow, "코치 노트 보기", lambda: open_coach_note(), padx=10, pady=4).pack(side="left", padx=(8, 0))
    trow = tk.Frame(tcd, bg=C["card"]); trow.pack(anchor="w", pady=(10, 0))

    def save_report_today(show=False):
        """오늘 기록 텍스트를 쓴다. 실패해도 앱은 계속 — 로그에 남기고 (버튼으로 눌렀을 때만) 알린다"""
        try: p = save_report(data, today_key[0], cur_plays(), day_state.get("dt"))
        except Exception:
            log_exc("save_report"); p = None
        try: save_upload_pack(data, today_key[0], cur_plays(), day_state.get("dt"))
        except Exception: log_exc("save_upload_pack")
        try: save_thumb_page(data, today_key[0], cur_plays(), day_state.get("dt"))
        except Exception: log_exc("save_thumb_page")
        if routine_complete(data["days"].get(today_key[0], blank_day()), day_state.get("dt"), today_key[0], data["pb"]):
            try: auto_coach_now("done")
            except Exception: log_exc("auto_coach_now")
            if coach_cfg.get("ai_auto"): ai_coach_now("done")
        if show:
            if p: show_toast(f"기록 저장 ✓ {p.parent.name}\\{p.name}")
            else: show_toast("기록 저장 실패 — aim_desk.log 를 확인하세요", "warn")
        set_trainer_status()
        return p

    def open_report_dir():
        try: report_dir().mkdir(parents=True, exist_ok=True)
        except OSError: pass
        open_uri(str(report_dir()))

    RBtn(trow, "오늘 기록 저장", lambda: save_report_today(True), padx=10, pady=5).pack(side="left")
    RBtn(trow, "기록 폴더 열기", open_report_dir, padx=10, pady=5).pack(side="left", padx=(8, 0))
    def save_week_now():
        try:
            _wk = close_key(today_key[0]) if day_state.get("dt") == "r" else today_key[0]      # 쉬는 날엔 방금 끝난 주, 훈련일엔 이번 주 지금까지
            _p = save_week_pack(data, _wk); save_data(data); show_toast(f"주간 결산 저장 ✓ {_p.parent.name}\\{_p.name}")
        except Exception:
            log_exc("save_week_pack"); show_toast("주간 결산 저장 실패 — aim_desk.log 를 확인하세요", "warn")
    RBtn(trow, "주간 결산", save_week_now, padx=10, pady=5).pack(side="left", padx=(8, 0))
    trainer_txt = tk.Text(tcd, height=5, width=28, font=FS, bg=C["card2"], fg=C["txt"], insertbackground=C["txt"],
                          bd=0, wrap="word", padx=6, pady=4, undo=True)
    trainer_txt.pack(fill="x", pady=(8, 4))
    trow2 = tk.Frame(tcd, bg=C["card"]); trow2.pack(anchor="w")
    trainer_lbl = tk.Label(tcd, text="", font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left")
    trainer_lbl.pack(anchor="w", pady=(5, 0))

    def set_trainer_status(p=None):
        parts = []
        if TRAINER["targets"]:
            parts.append(f"목표 {len(TRAINER['targets'])}개" + (f" ({TRAINER['set_on'][5:].replace('-', '/')} 받음)" if TRAINER["set_on"] else "")
                         + " · " + " · ".join(f"{sname(k)} {v}" for k, v in list(TRAINER["targets"].items())[:6])
                         + (" …" if len(TRAINER["targets"]) > 6 else ""))
        th_ = [f"{k[5:].replace('-', '/')} {THEME_NAME.get(v, v)}" + ("" if day_type_of(k) == "v" else " (금·토·일은 고정 루틴 — 무시)")
               for k, v in sorted(TRAINER["themes"].items()) if k >= today_key[0]]
        if th_: parts.append("테마 " + " · ".join(th_))
        if TRAINER["note"]: parts.append("메모 · " + TRAINER["note"])
        rp = report_path(today_key[0])
        parts.append(f"오늘 기록: {rp.name} ✓" if rp.exists() else "오늘 기록: 루틴을 마치면 저장됩니다 (버튼으로 지금 저장 가능)")
        if p and p["errors"]:
            parts.append(f"읽지 못한 줄 {len(p['errors'])} (무시): " + " / ".join(x[:24] for x in p["errors"][:2]))
        ok_ = p and (p["targets"] or p["remove"] or p["themes"] or p["note"] or p["challenge"])
        cfg(trainer_lbl, text="\n".join(parts), fg=C["ok"] if ok_ else (C["val"] if (p and p["errors"]) else C["hint"]))
        cfg(trainer_mini, text=(parts[0] if TRAINER["targets"] else "아직 받은 목표 없음 — 루틴 뒤 기록 파일을 보내고 답장을 붙여넣으세요"), fg=C["ok"] if TRAINER["targets"] else C["hint"])

    def replan_today():
        """오늘 계획이 바뀌었을 수 있다 — 루틴 카드·플레이리스트·(열려 있으면) 순서창을 같은 계획으로 (on_day_change 와 같은 원칙).
        목표·메모·내일 테마만 온 답장이면 순서창은 그대로 둔다"""
        old = list(seq_win["seq"]) if seq_alive() else None
        hidden = old is not None and seq_win["win"].state() == "withdrawn"
        build_day_ui(); install_playlists()
        if old is not None and old != sequence_for(day_state["pl"]):
            open_sequence(day_state["pl"])          # 옛 테마 스냅샷을 버리고 새 계획으로 다시 연다 (자동 진행 상태는 그대로)
            if hidden and seq_alive(): seq_win["win"].withdraw()   # 숨긴 채 돌고 있었으면 새 창도 숨긴 채로
        refresh()
        root.after(300, lambda: (dirty.__setitem__("today", True), refresh_tab("today")))

    def apply_trainer():
        txt = trainer_txt.get("1.0", "end").strip()
        if not txt:
            show_toast("붙여넣을 답장이 없습니다 — 트레이너 답장을 칸에 넣고 누르세요", "warn"); return
        p = trainer_apply(data, txt, today_key[0]); save_data(data)
        got = bool(p["targets"] or p["remove"] or p["themes"] or p["note"] or p["challenge"])
        if got:
            trainer_txt.delete("1.0", "end")
            replan_today()                                             # 오늘 테마가 바뀌었을 수 있다 — 플레이리스트·순서창도 같이
            show_toast(f"트레이너 답장 적용 ✓ 목표 {len(TRAINER['targets'])}개" + (f" · 못 읽은 줄 {len(p['errors'])}" if p["errors"] else ""))
        else:
            show_toast("읽을 수 있는 줄이 없습니다 — '목표 Pasu 850' 처럼 한 줄에 하나", "warn")
        set_trainer_status(p)

    def clear_trainer():
        trainer_clear(data); save_data(data)
        replan_today()
        set_trainer_status(); show_toast("트레이너 목표·테마·메모를 지웠습니다")

    RBtn(trow2, "답장 적용", apply_trainer, bg=C["ok_bg"], fg=C["ok"], padx=12, pady=5).pack(side="left")
    RBtn(trow2, "목표 지우기", clear_trainer, padx=10, pady=5).pack(side="left", padx=(8, 0))
    tk.Label(tcd, text="답장 형식 · 목표 Pasu 850 · 도전 Pasu 850 · 테마 내일 트래킹 · 메모 … · 목표 Pasu 없음",
             font=FS, bg=C["card"], fg=C["dim"], wraplength=px(268), justify="left").pack(anchor="w", pady=(5, 0))

    # ── 훈련일 경계 ──
    dc = card(tcol1); dc.pack(fill="x", pady=(10, 0))
    tk.Label(dc, text="훈련일 경계", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 4))
    tk.Label(dc, text="하루가 바뀌는 시각입니다. 자정으로 두면 밤 11시에 시작해 새벽에 끝난 세션이 이틀로 쪼개지고, "
                      "자정을 넘기는 순간 앱은 다음 날 테마로 갈아타는데 코박스는 켤 때 읽은 어제 플레이리스트를 그대로 씁니다.",
             font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left").pack(anchor="w", pady=(0, 7))
    cut_row = tk.Frame(dc, bg=C["card"]); cut_row.pack(anchor="w")
    cut_btns = {}
    def sync_cut_btns():
        for v, b in cut_btns.items():
            on = v == DAY_CUTOFF_H[0]
            b.restyle(bg=C["gold"] if on else C["card2"], fg=C["onfill"] if on else C["txt"])
    def set_cutoff(v):
        if DAY_CUTOFF_H[0] == v: return
        DAY_CUTOFF_H[0] = v; data["day_cutoff"] = v; save_data(data)
        sync_cut_btns()
        _SCAN_STATE["sig"] = None; _SCORE_CACHE.clear(); TODAY_PLAYS.clear()
        nk = today_date().isoformat()
        if nk != today_key[0]: on_day_change(nk)
        else:
            scan_once(); build_day_ui(); install_playlists(); refresh()
        show_toast(f"훈련일 경계 {v}시 — 지금부터 {v}시에 날이 바뀝니다" if v else "훈련일 경계 자정")
    for _v in (0, 4, 5, 6, 7):
        _b = RBtn(cut_row, ("자정" if _v == 0 else f"{_v}시"), (lambda v=_v: set_cutoff(v)), padx=9, pady=4)
        _b.pack(side="left", padx=(0, 4)); cut_btns[_v] = _b
    sync_cut_btns()
    tk.Label(dc, text="새벽 5시 권장 — 자정 넘겨 치는 날이 있으면 한 세션으로 이어집니다.",
             font=FS, bg=C["card"], fg=C["dim"], wraplength=px(268), justify="left").pack(anchor="w", pady=(6, 0))

    # ── 기록 파일 ── exe 를 다른 폴더에서 실행하면 기록이 조용히 다른 자리에 생긴다.
    # 어느 파일을 쓰는지 안 보여 주면 기록을 통째로 잃는다 — 실제로 그렇게 잃었다.
    fc = card(tcol1); fc.pack(fill="x", pady=(10, 0))
    tk.Label(fc, text="기록 파일", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 4))
    tk.Label(fc, text=mask_user_path(str(DATA_FILE)), font=FS, bg=C["card"], fg=C["sub"],
             wraplength=px(268), justify="left").pack(anchor="w")
    fstat = tk.Label(fc, text="", font=FS, bg=C["card"], fg=C["dim"], wraplength=px(268), justify="left")
    fstat.pack(anchor="w", pady=(2, 0))
    frow = tk.Frame(fc, bg=C["card"]); frow.pack(anchor="w", pady=(6, 0))
    RBtn(frow, "폴더 열기", lambda: open_uri(str(DATA_FILE.parent)), padx=10, pady=4).pack(side="left")
    # 저장 위치 — 기록 텍스트 · 업로드 팩 · 썸네일 · 주간 결산이 가는 폴더 (기본: 기록 파일 옆 '기록')
    tk.Label(fc, text="저장 위치 — 기록 · 업로드 팩 · 썸네일 · 주간 결산", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(12, 4))
    out_lbl = tk.Label(fc, text="", font=FS, bg=C["card"], fg=C["sub"], wraplength=px(268), justify="left"); out_lbl.pack(anchor="w")
    orow = tk.Frame(fc, bg=C["card"]); orow.pack(anchor="w", pady=(6, 0))
    def sync_out_lbl():
        cfg(out_lbl, text=mask_user_path(str(report_dir())) + ("" if OUT_DIR[0] else "  (기본 · 기록 파일 옆)"))
        if OUT_DIR[0]:
            if not out_reset_btn.winfo_ismapped(): out_reset_btn.pack(side="left", padx=(8, 0))
        else: out_reset_btn.pack_forget()
    def apply_out_dir(path):
        """저장 위치를 바꾸고(None = 기본) 이전 폴더의 앱 파일을 옮길지 묻는다. 쓸 수 없는 폴더면 그대로 둔다"""
        old = report_dir()
        ok, why = set_out_dir(data, path)
        if not ok:
            show_toast(f"저장 위치를 바꾸지 못했습니다 — {why}: {mask_user_path(str(path))}", "warn"); return False
        save_data(data); new = report_dir(); sync_out_lbl(); set_trainer_status()
        n = len(out_dir_files(old)) if new != old else 0
        if n and messagebox.askyesno("저장 위치", f"지금까지의 기록 파일 {n}개를 새 폴더로 옮길까요?\n\n{old}\n→ {new}\n\n(같은 이름이 이미 있으면 건너뜁니다 · 다른 파일은 건드리지 않습니다)"):
            moved, skipped = move_out_files(old, new)
            show_toast(f"저장 위치 ✓ {mask_user_path(str(new))} · 기록 {moved}개 옮김" + (f" · {skipped}개 건너뜀" if skipped else ""))
        else: show_toast(f"저장 위치 ✓ {mask_user_path(str(new))}")
        return True
    def pick_out_dir():
        p = filedialog.askdirectory(title="기록을 저장할 폴더 선택", initialdir=str(report_dir() if report_dir().is_dir() else DATA_FILE.parent))
        if p: apply_out_dir(p)
    RBtn(orow, "바꾸기…", pick_out_dir, padx=10, pady=4).pack(side="left")
    RBtn(orow, "열기", open_report_dir, padx=10, pady=4).pack(side="left", padx=(8, 0))
    out_reset_btn = RBtn(orow, "기본으로", lambda: apply_out_dir(None), padx=10, pady=4)
    sync_out_lbl()
    stray_box = tk.Frame(fc, bg=C["card"]); stray_box.pack(fill="x")

    def refresh_files():
        n_d = len(training_days(data)); n_p = total_xp(data) - 5 * total_pbs(data)
        base_txt = (f"기준 측정 {BASE_DATE[0][5:].replace('-', '/')}" if BASE_DATE[0] else "기준 측정 전")
        fstat.configure(text=f"훈련 {n_d}일 · {n_p}판 · {base_txt}")
        for w in stray_box.winfo_children(): w.destroy()
        try: strays = stray_data_files()
        except Exception: strays = []
        if not strays: return
        tk.Label(stray_box, text="다른 폴더에서 기록을 찾았습니다", font=FNS, bg=C["card"], fg=C["gold"],
                 wraplength=px(268), justify="left").pack(anchor="w", pady=(8, 2))
        for info in strays[:3]:
            tk.Label(stray_box, text=fmt_stray(info), font=FS, bg=C["card"], fg=C["sub"],
                     wraplength=px(268), justify="left").pack(anchor="w")
            RBtn(stray_box, "이 기록 합치기", (lambda i=info: do_import(i)), padx=10, pady=4).pack(anchor="w", pady=(2, 6))

    def do_import(info):
        if not messagebox.askyesno("기록 합치기",
                f"{fmt_stray(info)}\n\n지금 기록에 합칩니다. 양쪽 판을 모두 남기고, 겹치는 판은 높은 점수를 씁니다.\n"
                f"합치기 전 지금 기록은 따로 보관합니다."): return
        try:
            other = json.loads(info["path"].read_bytes().decode("utf-8-sig"))
            n_fake = desynth_legacy(other)                 # 옛 파일이면 주입된 가짜 PB 를 걷어내고 들여온다
            kept = archive_data(); merge_data(data, other); save_data(data)
        except Exception:
            log_exc("import"); show_toast("합치기 실패 — 기록은 그대로입니다"); return
        _SCAN_STATE["sig"] = None; _SCORE_CACHE.clear()
        b = data.get("base") or {}
        BASELINE[0] = dict(b.get("scores") or {}) or None; BASE_DATE[0] = b.get("date")
        if BASELINE[0] is None: derive_baseline(data)
        scan_once(); build_day_ui(); refresh(); refresh_files()
        show_toast(f"합쳤습니다 · 훈련 {len(training_days(data))}일" + (f" · 가짜 기본값 {n_fake}개 제외" if n_fake else "") + f" (이전 기록은 {kept.name})")

    # ── 기록 새로 시작 ──
    rc = card(tcol1); rc.pack(fill="x", pady=(10, 0))
    tk.Label(rc, text="기록 새로 시작", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 4))
    tk.Label(rc, text="지금 기록을 날짜 붙여 보관하고 처음부터 시작합니다. 첫날은 기준 측정일이 되어 "
                      "18개를 한 판씩 치고, 그 점수가 새 출발선이 됩니다. 보관한 파일은 지우지 않습니다.",
             font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left").pack(anchor="w", pady=(0, 7))
    def do_reset():
        n_d = len(training_days(data))
        if not messagebox.askyesno("기록 새로 시작",
                f"지금까지 훈련 {n_d}일 기록을 보관하고 처음부터 시작합니다.\n\n"
                f"보관본은 지우지 않으니 언제든 되돌릴 수 있습니다. 계속할까요?"): return
        try: kept = archive_data()
        except OSError:
            log_exc("reset"); show_toast("보관에 실패해 새로 시작하지 않았습니다"); return
        keep = {k: data.get(k) for k in ("stats_dir", "next_key", "win", "seq_popup", "theme", "ui_scale", "coach", "bcast", "valo_cfg", "out_dir") if data.get(k) is not None}
        keep["day_cutoff"] = data.get("day_cutoff", 5)
        data.clear()
        data.update(keep); data.update({"pb": {}, "days": {}})
        BASELINE[0] = BASE_DATE[0] = None; trainer_clear(data)
        bump_ver(); save_data(data)
        _SCAN_STATE["sig"] = None; _SCORE_CACHE.clear(); TODAY_PLAYS.clear()
        scan_once(); build_day_ui(); install_playlists(); refresh(); refresh_files()
        show_toast(f"새로 시작합니다 — 오늘은 기준 측정일 (이전 기록은 {kept.name})")
    RBtn(rc, "기록 새로 시작", do_reset, padx=10, pady=5).pack(anchor="w")

    # ── 발로란트 연동 (선택) ── 에임이 올라도 랭크가 안 오르는 구간을 숫자로 보이게
    vc = card(tcol1); vc.pack(fill="x", pady=(10, 0))
    tk.Label(vc, text="발로란트 전적 연동 (선택)", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 4))
    tk.Label(vc, text="HenrikDev 커뮤니티 API. 키는 api.henrikdev.xyz/dashboard 에서 직접 받습니다 (무료). "
                      "넣어 두면 티어·RR·최근 경쟁전 ACS·HS%·승률이 자동으로 들어옵니다. 없어도 앱은 그대로 돕니다.",
             font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left").pack(anchor="w", pady=(0, 6))
    _vcfg = data.setdefault("valo_cfg", {"rid": "", "region": "ap", "key": ""})
    rid_var = tk.StringVar(value=_vcfg.get("rid") or ""); key_var = tk.StringVar(value=_vcfg.get("key") or ""); reg_var = tk.StringVar(value=_vcfg.get("region") or "ap")
    for lbl, var, show_ in (("라이엇 ID", rid_var, None), ("API 키", key_var, "•")):
        rw = tk.Frame(vc, bg=C["card"]); rw.pack(fill="x", pady=(0, 3))
        tk.Label(rw, text=lbl, font=FS, bg=C["card"], fg=C["sub"], width=7, anchor="w").pack(side="left")
        en = tk.Entry(rw, textvariable=var, font=FS, bg=C["card2"], fg=C["txt"], insertbackground=C["txt"], relief="flat", show=show_ or "")
        en.pack(side="left", fill="x", expand=True)
    rw = tk.Frame(vc, bg=C["card"]); rw.pack(fill="x", pady=(0, 6))
    tk.Label(rw, text="지역", font=FS, bg=C["card"], fg=C["sub"], width=7, anchor="w").pack(side="left")
    reg_btns = {}
    def set_region(r_):
        reg_var.set(r_)
        for k_, b_ in reg_btns.items(): b_.restyle(bg=C["gold"] if k_ == r_ else C["card2"], fg=C["onfill"] if k_ == r_ else C["txt"])
    for r_ in ("ap", "kr", "na", "eu"):
        b_ = RBtn(rw, r_, (lambda r_=r_: set_region(r_)), padx=7, pady=3); b_.pack(side="left", padx=(0, 3)); reg_btns[r_] = b_
    set_region(reg_var.get() if reg_var.get() in reg_btns else "ap")
    val_lbl = tk.Label(vc, text="", font=FS, bg=C["card"], fg=C["dim"], wraplength=px(268), justify="left"); val_lbl.pack(anchor="w")
    def _val_status():
        v = data.get("valo") or {}
        if not v.get("mmr"): val_lbl.configure(text="아직 불러온 적 없음"); return
        r_ = v.get("recent") or {}
        val_lbl.configure(text=f"{v['at']} · {v['mmr']['tier']} {v['mmr']['rr']}RR" +
                          (f" · 최근 {r_['n']}판 승률 {r_['win']:.0f}% · ACS {r_['acs']:.0f} · HS {r_['hs']:.0f}%" if r_ and r_.get("win") is not None and r_.get("hs") is not None else ""))
    # 네트워크는 워커 스레드에서, tkinter 는 메인 스레드에서만 — Tcl 은 스레드 안전하지 않아서 워커가 root.after 를
    # 부르면 메인 루프 밖에서는 RuntimeError 가 난다. 워커는 큐에 결과만 넣고 메인이 폴링한다
    import threading, queue
    val_q = queue.Queue(); val_busy = [False]
    def _val_poll():
        try: ok, msg = val_q.get_nowait()
        except queue.Empty: root.after(200, _val_poll); return
        val_busy[0] = False
        if ok: save_data(data); refresh()
        _val_status(); show_toast(("발로란트 전적 · " if ok else "발로란트 연동 실패 — ") + msg, "ok" if ok else "warn")
    def val_sync_now():
        if val_busy[0]: return
        data["valo_cfg"] = {"rid": rid_var.get().strip(), "region": reg_var.get(), "key": key_var.get().strip()}; save_data(data)
        val_lbl.configure(text="불러오는 중…"); val_busy[0] = True
        def work():
            try: val_q.put(val_sync(data))
            except Exception as e: log_exc("val_sync"); val_q.put((False, f"{type(e).__name__}: {e}"))
        threading.Thread(target=work, daemon=True).start()
        root.after(200, _val_poll)
    RBtn(vc, "지금 불러오기", val_sync_now, padx=10, pady=5).pack(anchor="w")
    _val_status()

    # ── 화면 · 녹화 — 방송창이 곧 녹화되는 화면이다 ──
    sc_ = card(tcol1); sc_.pack(fill="x", pady=(10, 0))
    tk.Label(sc_, text="화면 · 녹화", font=FB, bg=C["card"], fg=C["txt"]).pack(anchor="w", pady=(0, 4))
    tk.Label(sc_, text="OBS 는 '창 캡처 → AimDesk Broadcast' 하나만 잡으세요. 이 창의 크기는 픽셀로 고정돼 소스가 어긋나지 않고, 글자는 폰에서 봐도 읽히는 크기입니다. 본창은 조작용이라 녹화하지 않습니다.",
             font=FS, bg=C["card"], fg=C["hint"], wraplength=px(268), justify="left").pack(anchor="w", pady=(0, 6))
    prow = tk.Frame(sc_, bg=C["card"]); prow.pack(anchor="w")
    preset_btns = {}
    def sync_preset_btns():
        for k_, b_ in preset_btns.items():
            on = bcast_cfg().get("preset") == k_
            b_.restyle(bg=C["gold"] if on else C["card2"], fg=C["onfill"] if on else C["txt"])
    for k_, lbl in (("strip", "띠 1920×240"), ("card", "카드 1280×400"), ("full", "전체 1920×1080")):
        b_ = RBtn(prow, lbl, (lambda k_=k_: (set_bcast(preset=k_), sync_preset_btns())), padx=8, pady=4); b_.pack(side="left", padx=(0, 4)); preset_btns[k_] = b_
    sync_preset_btns()
    trow2 = tk.Frame(sc_, bg=C["card"]); trow2.pack(anchor="w", pady=(6, 0))
    Toggle(trow2, "테두리 없음", lambda: bool(bcast_cfg().get("frameless")), lambda v: set_bcast(frameless=bool(v))).pack(side="left")
    Toggle(trow2, "크로마(초록 배경)", lambda: bool(bcast_cfg().get("chroma")), lambda v: set_bcast(chroma=bool(v))).pack(side="left", padx=(6, 0))
    Toggle(trow2, "시작할 때 열기", lambda: bool(bcast_cfg().get("open", True)), lambda v: (bcast_cfg().__setitem__("open", bool(v)), save_data(data))).pack(side="left", padx=(6, 0))
    RBtn(sc_, "방송 화면 열기 (Ctrl+B · F11 전체)", open_broadcast, padx=10, pady=5).pack(anchor="w", pady=(6, 0))

    def install_playlists():
        sd = data.get("stats_dir")
        if not sd:
            pl_lbl.configure(text="stats 폴더를 먼저 지정하세요", fg=C["val"]); return
        n, d_, wrote = ensure_playlists(sd, today_key[0], data["pb"])
        if n:
            msg = f"플레이리스트 {n}개 설치 ✓ → 코박스 샌드박스 브라우저 네 번째 탭 '로컬 재생 목록'에 AIMDESK Day · Probe · Bench"
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
    cv_trend = tk.Canvas(gbody, height=px(170), bg=C["bg"], highlightthickness=0); cv_trend.pack(fill="x", pady=(0, 12))   # 【요즘】【성장】 (v7: 오늘 탭에서 옮김)
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
    ben_tier_lbl = tk.Label(ben_head, text="볼테익 점수 · 노비스 · 9갈래 평균 — 코박스 랭크 (발로란트 랭크 아님)", font=FS, bg=C["card"], fg=C["hint"])
    ben_tier_lbl.pack(side="left")
    ben_src = tk.Label(ben_head, text="", font=FNS, bg=C["card"], fg=C["dim"])
    ben_src.pack(side="right")
    RBtn(ben_head, "내 볼테익 프로필", lambda: open_uri("https://app.voltaic.gg/j0y0nho"),
         padx=12, pady=5).pack(side="right", padx=(0, 12))
    RBtn(ben_head, "볼테익 벤치 페이지", lambda: open_uri("https://app.voltaic.gg/benchmarks"),
         padx=12, pady=5).pack(side="right", padx=(0, 8))

    advice_lbl = tk.Label(bbody, text="", font=FS, bg=C["bg"], fg=C["hint"], wraplength=px(900), justify="left", anchor="w")
    advice_lbl.pack(fill="x", pady=(0, 10))
    # 관문 · 졸업 — 현재 단계 풀런에서 9갈래 전부 최상위면 버튼이 생긴다. 졸업하면 출발선을 보관하고 다음 단계 기준 측정부터 (앱을 다시 켠다)
    stage_line = tk.Label(bbody, text="", font=FS, bg=C["bg"], fg=C["sub"], anchor="w"); stage_line.pack(fill="x", pady=(0, px(6)))   # 단계 · 다음 단계 조건 (v7: 헤더 칩에서 옮김)
    grad_card = card(bbody, pad=(12, 9)); grad_card.pack(fill="x", pady=(0, 12))
    grad_head = tk.Frame(grad_card, bg=C["card"]); grad_head.pack(fill="x")
    grad_title = tk.Label(grad_head, text="", font=FB, bg=C["card"], fg=C["gold"]); grad_title.pack(side="left")
    def do_graduate(confirm=True, restart=True) -> bool:
        ok_, short_, _dk = tier_ready(data); t_ = CUR_TIER[0]
        nt_ = TIER_ORDER[min(TIER_ORDER.index(t_) + 1, len(TIER_ORDER) - 1)]
        if not ok_ or nt_ == t_:
            show_toast(f"아직 — 마지막 풀런에서 못 채운 갈래 {short_}" if nt_ != t_ else "마지막 단계입니다", "warn"); return False
        if confirm and not messagebox.askyesno("졸업", f"{TIER_KO[t_]} 졸업 → {TIER_KO[nt_]} 로 올라갑니다.\n지금 출발선은 보관되고, 다음 훈련일이 {TIER_KO[nt_]} 기준 측정일(18판)이 됩니다.\n앱을 다시 켭니다. 계속할까요?"):
            return False
        graduate(data); save_data(data)
        show_toast(f"★ {TIER_KO[t_]} 졸업 — {TIER_KO[nt_]} 시작. 다음 훈련일에 기준 측정 18판", "pb")
        if not (restart and restart_app()): refresh()
        return True
    grad_btn = RBtn(grad_head, "졸업 → 다음 단계", lambda: do_graduate(), padx=12, pady=5)
    grad_lbl = tk.Label(grad_card, text="", font=FS, bg=C["card"], fg=C["sub"], wraplength=px(900), justify="left", anchor="w")
    grad_lbl.pack(fill="x", pady=(4, 0))
    ben_body = tk.Frame(bbody, bg=C["bg"]); ben_body.pack(fill="both", expand=True)
    ben_rows = {}
    colf = [tk.Frame(ben_body, bg=C["bg"]) for _ in range(3)]
    for i, f in enumerate(colf):
        f.grid(row=0, column=i, sticky="nsew", padx=(0, 12))
        ben_body.grid_columnconfigure(i, weight=1)
    CATC = {"클리킹": C["val"], "트래킹": C["ow"], "스위칭": C["swt"]}
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
    lv_line = tk.Label(log_left, text="", font=FS, bg=C["bg"], fg=C["sub"], anchor="w"); lv_line.pack(fill="x", pady=(0, px(6)))   # 레벨 · 연속 · 코박스 종합 점수 (v7: 헤더에서 옮김)
    hist_card = card(log_left, pad=(12, 10)); hist_card.pack(fill="x", pady=(0, 12))
    hh = tk.Frame(hist_card, bg=C["card"]); hh.pack(fill="x")
    tk.Label(hh, text="최근 14일", font=FH, bg=C["card"], fg=C["txt"]).pack(side="left")
    tk.Label(hh, text="줄을 누르면 그날 시나리오별 기록 · ✓ R=랭크", font=FS, bg=C["card"], fg=C["hint"]).pack(side="right")
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
        if e1 is None: gt, gold = "시작 대비 · 기준 측정 전", False
        elif e0 is None: gt, gold = f"시작 대비 · 총 에너지 {e1}", False
        else: gt, gold = f"시작 대비 · 총 에너지 {e0} → {e1} ({e1 - e0:+d})", e1 > e0
        cfg(grow_title, text=gt, fg=C["gold"] if gold else C["dim"])
        for r_, g in zip(grow_cells, memo(("growth",), lambda: growth_since_base(data))):
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
                           fill=C["onfill"] if hit else C["dim"])

    def rank_pill(cv, name, color, w=None):
        cv.delete("all"); w = w or px(76)
        if not name or name == "—": return
        rrect(cv, 0, px(2), w, px(24), px(10), fill=color, outline="")
        cv.create_text(w/2, px(13), text=name, font=(FAM, 9, "bold"), fill=C["onfill"])

    # ── 차트 ──
    def draw_idx(cv, series):
        cv.delete("all"); W = max(cv.winfo_width(), px(400))
        _has = [p for p in series if p["vi"] is not None or p["oi"] is not None]
        H = px(236) if _has else px(74)                     # 그릴 게 없으면 자리를 덜 차지한다
        if int(cv.cget("height")) != H: cv.configure(height=H)
        if not _has:
            cv.create_text(px(16), px(20), text="측정 곡선 · 매일 첫 판 6개", anchor="w", fill=C["txt"], font=FB)
            cv.create_text(px(16), px(46), anchor="w", fill=C["hint"], font=FS,
                           text="그날 첫 판만 모아 컨디션을 뺀 실력 곡선을 그립니다 — 오늘 점수 재기 4일치가 쌓이면 여기에 나타납니다")
            return
        H = px(236)
        cv.create_text(px(16), px(16), text="측정 곡선 · 매일 첫 판 6개", anchor="w", fill=C["txt"], font=FB)
        cv.create_text(W-px(16), px(16), text="점 = 일별 · 선 = 7일 평균", anchor="e", fill=C["hint"], font=FS)
        cv.create_rectangle(px(96), px(11), px(108), px(14), fill=C["val"], outline="")
        cv.create_text(px(112), px(13), text="발로", anchor="w", fill=C["sub"], font=FS)
        pts = [p for p in series if p["vi"] is not None or p["oi"] is not None][-30:]
        L, R, T, B = px(46), px(18), px(38), px(24)
        def X(i): return L + (W-L-R) * (0.5 if len(pts) < 2 else i/(len(pts)-1))
        def Y(v): return T + (H-T-B) * (1 - (v+3)/6)
        for v in (-2, 0, 2):
            cv.create_line(L, Y(v), W-R, Y(v), fill=C["grid"] if v else C["grid2"])
            cv.create_text(L-px(9), Y(v), text=f"{v:+d}" if v else "0", anchor="e",
                           fill=C["dim"], font=FNS)
        if not pts:
            cv.create_text((L+W-R)/2, (T+H-B)/2,
                           text="프로브를 시작하면 여기서 성장 곡선이 자랍니다  ·  지수는 4일차부터",
                           fill=C["hint"], font=F)
            return
        for a, col in (("vi", C["val"]),):
            for i, p in enumerate(pts):
                if p[a] is not None:
                    x, y = X(i), Y(p[a])
                    cv.create_oval(x-3, y-3, x+3, y+3, fill=col, outline="")
        for a, col in (("maV", C["val"]),):
            seq = [(X(i), Y(p[a])) for i, p in enumerate(pts) if p[a] is not None]
            if len(seq) > 1:
                cv.create_line(*[c for xy in seq for c in xy], fill=col, width=3, smooth=True)
        cv.create_text(L, H-px(10), text=pts[0]["date"][5:], anchor="w", fill=C["dim"], font=FNS)
        cv.create_text(W-R, H-px(10), text=pts[-1]["date"][5:], anchor="e", fill=C["dim"], font=FNS)

    def draw_bench_chart(cv, bd):
        cv.delete("all"); W = max(cv.winfo_width(), px(400)); H = px(196)
        cv.create_text(px(16), px(16), text="볼테익 점수 · 토요일 시험", anchor="w", fill=C["txt"], font=FB)
        cv.create_text(W-px(16), px(16), text="랭크 선을 넘는 순간이 보입니다", anchor="e", fill=C["hint"], font=FS)
        L, R, T, B = px(70), px(18), px(38), px(22)
        top = max([520] + [e_ + 60 for _, e_ in bd])   # 골드 위로 외삽돼도 점이 차트 밖으로 나가지 않게
        def Y(v): return T + (H-T-B) * (1 - v/top)
        for (t, n, _c) in RANKS:
            if t > top: continue                                              # 차트 위로 나간 랭크 선은 제목과 겹친다
            c = RANKC[RANK_IDX[n]]
            cv.create_line(L, Y(t), W-R, Y(t), fill=C["chart_line"], dash=(3, 4))
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
                    cv.create_text(X(i), H - B + px(11), text=sname(k)[:8], anchor="w" if X(i) < W - px(60) else "e", fill=C["dim"], font=(FAM, 7))
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

    def sync_live(V):
        """히어로: 헤드라인 · 서브라인 · 숫자 · 버튼 · 방금 판 — 상태 하나에 한 문장 (쉬는 날 / 출발선 / 훈련 중 / 코박스 끝 / 오늘 끝)"""
        cp = cur_plays(); dkey = today_key[0]; day = data["days"].get(dkey, blank_day()); dt_ = day_state.get("dt", "v")
        kinds = [k_ for _, _, k_ in day_verdicts(data, dkey, cp)]
        pn = today_plan_n(); n = len(cp); rem = max(0, pn - n) if pn else 0
        cur_k = None
        if seq_alive():
            _dn, _nx, _sc = seq_status()
            if _nx is not None: cur_k = seq_win["seq"][_nx]
        base_day = BASE_DATE[0] is None or dkey == BASE_DATE[0]
        complete = bool(pn) and routine_complete(day, dt_, dkey, data["pb"])
        _est = remaining_estimate(cp, rem) if rem else None
        _eta = (datetime.now() + timedelta(minutes=_est)).strftime("%H:%M") if _est else None
        rem_txt = (f"남은 {rem}판" + (f" ≈ {_est}분 · {_eta}쯤 끝" if _est else "")) if rem else ""
        pl_ = day_state.get("pl")
        def _btn(text, bg, fg, cmd): run_btn.cmd = cmd; run_btn.restyle(bg=bg, fg=fg, text=text)
        def _next_txt():
            if cur_k:
                _sq = seq_win["seq"]; _dn, _nx, _sc = seq_status(); _i = _nx if _nx is not None else -1
                _a = _b = _i
                while _a > 0 and _sq[_a - 1] == cur_k: _a -= 1
                while _b + 1 < len(_sq) and _sq[_b + 1] == cur_k: _b += 1
                return "다음 판 · " + sname(cur_k) + (f" {_i - _a + 1}/{_b - _a + 1}" if _i >= 0 and _b > _a else "")
            nk = next_routine_key([(r[0], r[1], r[2]) for r in routine_rows], day, None)
            return f"다음 판 · {sname(nk)}" if nk else ("실력 재는 날 · 18판" if dt_ == "b" else "오늘 할 일 · 코박스 20판")
        show_cnt = bool(pn)
        if dt_ == "r":
            cfg(cur_lbl, text="오늘은 쉬는 날"); cfg(est_lbl, text="컨디션만 적어도 됩니다 · 앱을 켜 두면 주간 결산이 저장됩니다"); show_cnt = False
        elif base_day:
            n_t = bench_readiness(data, dkey)["n_today"]
            cfg(cur_lbl, text=("출발선 만드는 날 · 18판" if n_t < 18 else "출발선 완성 ✓") if not cur_k else _next_txt())
            cfg(est_lbl, text=("18개를 한 판씩 · 약 27분 · 못 쳐도 다시 치지 않아요" if n_t < 18 else "내일부터 하루 20판 루틴") if not rem_txt else rem_txt)
            if seq_alive(): _btn("자동 진행 중 · 순서 보기", C["card2"], C["txt"], lambda: show_sequence(pl_))
            else: _btn("▶ 벤치 18개 실행", C["gold"], C["onfill"], lambda: run_playlist(pl_))
        elif complete and (dt_ != "v" or val_done(day)):
            cfg(cur_lbl, text=f"오늘 끝 ✓ · {n}판")
            _sl = day_state["sess_lbl"].cget("text")
            cfg(est_lbl, text=f"{n}판" + (f" · 신기록 {V['day'].get('n_pb')}개" if V["day"].get("n_pb") else "") + (f" · {_sl}" if _sl else ""))
            _btn("오늘 끝 ✓ · 오늘 한 장 보기", C["ok_bg2"], C["ok"], lambda: open_card())
        elif complete:
            cfg(cur_lbl, text="코박스 끝 ✓ · 발로란트 15분"); cfg(est_lbl, text="사격장 3분 → 카운터 스트레이프 3분 → 데스매치 9분 · 끝나면 숫자 4개만")
            _btn("오늘 끝 ✓ · 오늘 한 장 보기", C["ok_bg2"], C["ok"], lambda: open_card())
            if day_state.get("val_open") and not day_state.get("val_auto_opened"):
                day_state["val_auto_opened"] = True; day_state["val_open"](True)
        elif cur_k or cp:
            cfg(cur_lbl, text=_next_txt()); cfg(est_lbl, text=rem_txt or "오늘 계획 끝")
            if seq_alive(): _btn("자동 진행 중 · 순서 보기", C["card2"], C["txt"], lambda: show_sequence(pl_))
            else: _btn("▶ 벤치 18개 실행" if dt_ == "b" else "▶ 오늘 루틴 실행", C["gold"], C["onfill"], lambda: run_playlist(pl_))
        else:
            if dt_ == "b": cfg(cur_lbl, text="실력 재는 날 · 18판"); cfg(est_lbl, text="18개를 한 판씩 · 약 27분 · 출발선과 비교합니다")
            else: cfg(cur_lbl, text="오늘 할 일 · 코박스 20판"); cfg(est_lbl, text="손 풀기 2 → 오늘 점수 재기 6 → 본훈련 12 → 발로란트 15분 · 약 48분")
            _btn("▶ 벤치 18개 실행" if dt_ == "b" else "▶ 오늘 루틴 실행", C["gold"], C["onfill"], lambda: run_playlist(pl_))
        # 숫자 · 버튼 줄 · 방금 판 · 띠 — 있을 때만
        if show_cnt:
            cfg(cnt_lbl, text=f"{n}/{pn}", fg=C["dim"] if n == 0 else (C["ok"] if n >= pn else C["txt"]))
            if not cnt_box.winfo_ismapped(): cnt_box.pack(side="right", anchor="s")
        else: cnt_box.pack_forget()
        if pl_:
            if not run_row.winfo_ismapped(): run_row.pack(fill="x", pady=(px(14), 0), after=band_cv)
        else: run_row.pack_forget()
        if cp:
            k_, _t_, sc_ = cp[-1]; kind = kinds[-1] if kinds else "new"; col = C[VERDICT_FILL.get(kind, "sub")]
            cfg(cur_score, text=str(sc_), fg=col)
            cfg(cur_word, text=f"{sname(k_)} · {VERDICT_NAME.get(kind, '')}".rstrip(" ·") + (" ★" if kind == "pb" else ""), fg=col)
            if not last_row.winfo_ismapped(): last_row.pack(fill="x", pady=(px(10), 0), before=band_cv)
        else:
            cfg(cur_score, text="—", fg=C["dim"]); cfg(cur_word, text="", fg=C["hint"]); last_row.pack_forget()
        if dt_ == "r" or day_state.get("open"): day_state["rib_cv"].pack_forget(); todo_host.pack_forget()   # 쉬는 날 · '자세히' 열림: 히어로는 요약만 (줄은 아래 상세 카드에)
        else:
            if not day_state["rib_cv"].winfo_ismapped(): day_state["rib_cv"].pack(fill="x", pady=(px(12), 0), after=est_lbl)
            if not todo_host.winfo_ismapped(): todo_host.pack(fill="x", pady=(px(10), 0), after=day_state["rib_cv"])
        cfg(seq_lnk, text="한 번 더" if complete else "순서 보기")
        if ((data.get("coach") or {}).get("notes") or {}).get(dkey):
            if not note_lnk.winfo_ismapped(): note_lnk.pack(side="left", padx=(0, px(14)))
        else: note_lnk.pack_forget()
        ca = cond_adjust(day.get("cond") or {})
        if ca:
            cfg(cond_chip, text=ca.split(" — ")[0])
            if not cond_chip.winfo_ismapped(): cond_chip.pack(side="left", padx=(px(8), 0))
        else: cond_chip.pack_forget()
        sync_auto_mini()
        if auto_mini.cget("text"):
            if not auto_mini.winfo_ismapped(): auto_mini.pack(fill="x", pady=(px(8), 0))
        else: auto_mini.pack_forget()
        root.after_idle(place_hero)

    def place_hero():
        """자세히가 접혀 있고 창이 높으면 히어로를 살짝 내려 앉힌다 (빈 공간의 28%, 최대 px(160)) — 열리면 위로 붙는다"""
        if not page.winfo_exists(): return
        if day_state.get("open"): top = 0
        else:
            need = hero.winfo_reqheight() + foot.winfo_reqheight() + px(8)
            top = min(px(160), max(0, int((ft.winfo_height() - need) * 0.28)))
        if top != page_pad[1]: page_pad[1] = top; page.pack_configure(pady=(top, 0))

    def refresh_today():
        dkey = today_key[0]; day = data["days"].get(dkey, blank_day())
        # 판정 밴드 — 한 소스(verdicts)에서. 히어로 상태가 바뀌면 한 번 번쩍이고, 상태는 저장(히스테리시스)
        V = verdicts(data, dkey, day_state.get("dt"), cur_plays(), day_state.get("hero_state"))
        st_ = V["day"]["state"]
        if st_ in ("up", "flat", "down") and day_state.get("hero_state") != st_: day_state["hero_state"] = st_
        _h = dict(data.get("hero") or {}); _h["date"] = dkey
        if day_state.get("hero_state") in ("up", "flat", "down"): _h["state"] = day_state["hero_state"]
        for _k in ("grow", "recent"):                         # 확정된 성장·요즘 상태만 기억 (경계 완충의 기준)
            if V[_k]["state"] in ("up", "flat", "down"): _h[_k] = V[_k]["state"]
        if _h != data.get("hero"): data["hero"] = _h; save_data(data)
        key_ = (st_, V["day"]["conf"])
        if day_state.get("last_hero") is not None and day_state["last_hero"] != key_: flash_hero(V)
        else: draw_band(band_cv, V)
        day_state["last_hero"] = key_
        sync_live(V)
        dirty["grow"] = True                                                       # 요즘·성장 타일은 성장 탭에 — 열 때 그린다
        if day_state.get("sess_cv") is not None and day_state["sess_cv"].winfo_exists() and day_state["sess_cv"].winfo_ismapped():
            _cp = cur_plays(); draw_session(day_state["sess_cv"], session_points(data, dkey, _cp), within_day_gain(_cp))
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
            if bar.winfo_width() <= 1 and data["win"].get("routine_open"): unmapped = True   # 접혀 있으면 폭이 없는 게 정상
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
            tg_ = TRAINER["targets"].get(key) if kind != "bench" else None              # 트레이너 목표 (벤치 줄은 등급 거리로 충분)
            if val is None:
                sl.configure(text=(f"목표 {tg_}" if tg_ is not None else ""), fg=C["dim"])
            else:
                kind_, label_, colk_ = play_verdict(val, scen_day_band(data, key, dkey, field), pb_prev.get(key))
                txt, col = f"{val} {label_}".strip(), C[colk_]
                if kind == "bench" and th_of(key):                                       # 벤치 데이: ▲▼ 대신 다음 등급까지 (순서창이 ▲▼를 보여 준다)
                    g_, gcol = fmt_gap(val, th_of(key)); is_pb = kind_ == "pb"
                    txt, col = f"{val}{' 최고' if is_pb else ''} · {g_}", (C["gold"] if is_pb else gcol)
                if tg_ is not None:
                    hit_ = val >= tg_
                    txt += f" · 목표 {tg_}" + (" ✓" if hit_ else "")
                    if hit_ and kind_ != "pb": col = C["ok"]
                cfg(sl, text=txt, fg=col)
        if unmapped and not day_state.get("redraw_pending"):
            day_state["redraw_pending"] = True
            root.after(250, lambda: (day_state.__setitem__("redraw_pending", False), dirty.__setitem__("today", True), refresh_tab("today")))
        # 섹션별 진행 (③ 본훈련 · 12/17 처럼)
        for i, sec in enumerate(section_labels):
            lb, title, start, extra = sec[:4]; bar_, cnt_, lb2 = sec[4], sec[5], sec[6]
            end = section_labels[i + 1][2] if i + 1 < len(section_labels) else len(routine_rows)
            rows = [(r[0], r[1], r[2]) for r in routine_rows[start:end]] + (extra or [])
            if rows:
                d_, t_ = section_progress(rows, day); done_ = d_ >= t_
                cfg(lb, text=f"{title} · {d_}/{t_}", fg=C["txt"]); cfg(lb2, text=f"{title} · {d_}/{t_}", fg=C["ok"] if done_ else C["gold"])
                cfg(cnt_, text=f"{d_}/{t_}" + (" ✓" if done_ else ""), fg=C["ok"] if done_ else C["sub"])
                bar_.delete("all"); bw_ = max(bar_.winfo_width(), px(60)); h_ = px(6)
                segs_ = segment_geometry(bw_, t_)
                filled_ = min(len(segs_), int(d_ * len(segs_) / t_)) if t_ > len(segs_) else min(d_, len(segs_))
                for j_, (x1_, x2_) in enumerate(segs_):
                    fill_ = (C["ok"] if done_ else C["gold"]) if j_ < filled_ else C["card2"]
                    if x2_ - x1_ >= 8: rrect(bar_, x1_, 1, x2_, h_ - 1, min(3, (x2_ - x1_) // 2), fill=fill_, outline="", tags="seg")
                    else: bar_.create_rectangle(x1_, 1, x2_, h_ - 1, fill=fill_, outline="", tags="seg")
        # 계획 밖 판 — 코박스가 예전 플레이리스트를 들고 있으면 여기에 뜬다
        if day_state.get("off_lbl") is not None and day_state["off_lbl"].winfo_exists():
            n_off, ks_off = off_plan_plays(data, dkey, cur_plays(), data["pb"])
            _nst, _thst = stale_playlist(data, dkey, cur_plays())
            if _nst:
                cfg(day_state["off_lbl"], text=f"⚠ 코박스가 어제 플레이리스트({_thst})를 돌고 있습니다 — 코박스를 완전히 껐다 켠 뒤 AIMDESK Day 를 다시 ▶ 하세요 (계획 밖 {n_off}판은 기록엔 남습니다)")
                if auto.get("on") and not day_state.get("stale_warned"):
                    day_state["stale_warned"] = True; stop_auto(f"⚠ 어제 순서({_thst})가 돌고 있어 자동 진행을 멈췄습니다 — 코박스 껐다 켜기")
            else: cfg(day_state["off_lbl"], text=fmt_off_plan(n_off, ks_off))
            _ol = day_state["off_lbl"]
            if day_state.get("dt") == "b":
                (_ol.grid() if _ol.cget("text") else _ol.grid_remove())
            elif _ol.cget("text"):
                if not _ol.winfo_ismapped(): _ol.pack(fill="x", pady=(px(4), 0))
            else: _ol.pack_forget()
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
        if day_state.get("dt") == "r" and not day_state.get("week_closed") and not ((data.get("weeks") or {}).get(iso_week_id(close_key(dkey))) or {}).get("pack"):
            day_state["week_closed"] = True                   # 쉬는 날(월요일) 하루 한 번: 지난 주 마감 — 관문 검사(두 주 연속이면 단계 상승) → 주간 결산 파일
            try:
                _wp, _adv, _idx = week_close(data, dkey); save_data(data)
                show_toast((f"★ 단계 {_idx} 진입 — {STAGES[_idx]['name']} · " if _adv else "") + f"{recap_label(dkey)} 결산 저장 ✓ {_wp.parent.name}\\{_wp.name}", "pb" if _adv else "info")
            except Exception: log_exc("week_close")
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
                if routine_complete(day, dt_, dkey, data["pb"]):
                    avg_ = {k_: recent_stats(data, k_, dkey, "first")[0] for k_ in PROBE}
                    extra = "마무리 · " + next_step(data, dkey, cp, avg_)
                elif dt_ == "b" and alt: alt = alt + [("18개 다 치면 벤치 탭·성장 차트에 오늘 점이 찍힙니다", "hint")]
                return session_brief(data, dkey, dt_, cp, extra=extra, alt=alt)
            lines = memo(("brief", dkey, dt_, COACH_STATE.get("validity"), len(cp)), _brief)
            COACH_STATE["brief"] = lines
            for i, lb_ in enumerate(day_state["coach"]):
                if i < len(lines): cfg(lb_, text=lines[i][0], fg=C[lines[i][1]])
                else: cfg(lb_, text="")
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
        tdays = memo(("tdays",), lambda: training_days(data)); today_d = date.fromisoformat(dkey)
        cur, best = streak(tdays, today_d)
        cfg(hdr_streak, text=f"연속 {cur}일" + (f" · 최고 {best}" if best > cur else ""), fg=C["gold"] if cur >= 3 else C["sub"])
        draw_week(week_strip(tdays, today_d))
        # 헤더 에너지는 PB 기준(항상 9/9) — 오늘 친 몇 판의 부분 조화평균으로 흔들리지 않게
        e_pb, _ = totalE(data["pb"]); rn_pb, rc_pb = rank_of(e_pb)
        _e0 = totalE(BASELINE[0])[0] if BASELINE[0] else None                 # 시청자용 문구: '볼테익 428 · 출발선 +88' — 랭크 단어(Gold)는 발로 티어와 부딪혀 벤치 탭에만
        hdr_e.configure(text=(f"볼테익 {e_pb}" + (f" · 출발선 {e_pb - _e0:+d}" if _e0 is not None else "") if e_pb is not None else "기준 측정 전"),
                        fg=C["onfill"] if e_pb is not None else C["dim"], bg=rc_pb if e_pb is not None else C["card2"])
        hdr_story.configure(text=story_line(data, dkey))
        _ep = episode_no(data, dkey)
        cfg(hdr_day, text=f"DAY {_ep}" + (f" · 연속 {cur}일" if cur >= 1 else ""))
        cfg(lv_line, text=f"{fmt_level(xp)} · 연속 {cur}일" + (f" · 코박스 종합 점수 {e_pb}" + (f" (출발선 {e_pb - _e0:+d})" if _e0 is not None else "") if e_pb is not None else " · 출발선 재기 전"))
        _ss = memo(("stage", dkey), lambda: stage_status(data, dkey))
        cfg(hdr_stage, text=fmt_stage_chip(_ss), fg=C["gold"] if _ss["n_ok"] == _ss["total"] else C["sub"])

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
        t_ = CUR_TIER[0]; cfg(ben_tier_lbl, text=f"볼테익 점수 · {TIER_KO[t_]} · 9갈래 평균 — 코박스 랭크 (발로란트 랭크 아님)")
        ok_, short_, dk_ = tier_ready(data); gw_, gn_, gc_ = fmt_gate(gate_status(data["pb"]))
        nt_ = TIER_ORDER[min(TIER_ORDER.index(t_) + 1, len(TIER_ORDER) - 1)]
        cfg(grad_title, text=(f"{gw_} · {gn_}" if BASE_DATE[0] else "관문 — 기준 측정 18판 뒤에 잽니다"))
        _st = stage_status(data, today_key[0]); cfg(stage_line, text=f"지금 단계 {_st['idx']} · {_st['name']} — 다음 단계 조건 {_st['n_ok']}/{_st['total']} (계획 탭에 자세히)")
        if ok_ and nt_ != t_:
            cfg(grad_lbl, text=f"풀런 {dk_} 에서 9갈래 전부 {TIERS[t_][2][3]} ✓ — 졸업하면 출발선을 보관하고 다음 훈련일에 {TIER_KO[nt_]} 기준 측정 18판부터 다시 잽니다", fg=C["ok"])
            grad_btn.pack(side="right")
        else:
            cfg(grad_lbl, text=(gc_ + (f" · 마지막 풀런 {dk_}: 못 채운 갈래 {short_}" if dk_ else "") + f" · 토요일 보스전 풀런에서 9갈래 전부 {TIERS[t_][2][3]} 이면 졸업 버튼이 생깁니다") if BASE_DATE[0] else "PB 기준 관문 미터. 출발선을 재면 채워집니다", fg=C["sub"])
            grad_btn.pack_forget()
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
        draw_trend(cv_trend, verdicts(data, today_key[0], day_state.get("dt"), _cp, day_state.get("hero_state")))
        draw_session(cv_sess, session_points(data, today_key[0], _cp), within_day_gain(_cp))
        draw_idx(cv_idx, probe_series(data))
        draw_bench_chart(cv_ben, memo(("bench_days",), lambda: bench_days(data)))
        for k, (cv, pbl) in spark_cvs.items(): draw_spark(k, cv, pbl)

    tab_fn.update(cal=refresh_cal, today=refresh_today, grow=refresh_grow, bench=refresh_bench, tools=lambda: (sync_stats_lbl(), set_trainer_status()))

    def refresh():
        """기록이 바뀌었을 때: 헤더 + 지금 보이는 탭만 그린다. 숨은 탭은 dirty 로 표시해 두고 열 때 그린다"""
        for t in dirty: dirty[t] = True
        refresh_header()
        if cur_tab[0] == "tools": refresh_files()
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
    for cv in [cv_trend, cv_sess, cv_idx, cv_ben] + [c for c, _ in spark_cvs.values()]:
        tab_of[cv] = "grow"; cv.bind("<Configure>", on_resize)
    for _, cells_, _card in ben_rows.values():
        for _k, _th, _l, _g, cvth in cells_:
            tab_of[cvth] = "bench"; cvth.bind("<Configure>", on_resize)
    tab_of[left_scroll.cv] = "today"; left_scroll.cv.bind("<Configure>", on_resize, add="+")
    tab_of[band_cv] = "today"; band_cv.bind("<Configure>", on_resize, add="+")
    def on_root_resize(e):
        """창 폭이 바뀌면 오늘 탭 여백을 다시 잰다 — 카드는 최대 px(1100) 으로 가운데 (자식 위젯의 <Configure> 는 무시)"""
        if e.widget is not root: return
        pad_ = max(px(24), (e.width - px(1100)) // 2)
        if pad_ == page_pad[0]: return
        page_pad[0] = pad_; page.pack_configure(padx=pad_)
        dirty["today"] = True
        if resize_job[0]: root.after_cancel(resize_job[0])
        resize_job[0] = root.after(80, _resize_flush)
    root.bind("<Configure>", on_root_resize, add="+")

    def on_day_change(nk):
        """자정 통과: 데이터 키·스캔 캐시·날짜 UI·입력칸을 모두 오늘로 (켜 둔 채 밤을 넘겨도 어제 루틴이 남지 않게)"""
        try:                                     # 입력 중이던 티어·RR·수면은 어제 기록으로 먼저 확정 — 자정 sync 가 덮어쓰기 전에
            fw = root.focus_get()
            if fw in (tier_ent, rr_ent): commit_rank()
            elif fw is ent: commit_sleep()
        except (KeyError, tk.TclError): pass
        if cur_plays(): save_report_today()     # 어제 판이 있으면 어제 기록부터 남긴다 (닫을 때와 같은 규칙)
        today_key[0] = nk
        _SCORE_CACHE.clear(); _MISS_SEEN.clear(); TODAY_PLAYS.clear()
        auto.update(on=False, fired=None, due=None, fired_at=None, pending=None, warned=False, seen=None, start_played=0)
        HDR_STATE.update(vi=None, oi=None)
        COACH_STATE.update(brief=[], validity=None, fat_sig=None, fat_len=0)
        day_state.update(hero_state=None, last_hero=None)
        routine_next[0] = None
        if detail["win"] is not None and detail["win"].winfo_exists(): detail["win"].destroy()
        if card_win["win"] is not None and card_win["win"].winfo_exists(): card_win["win"].destroy()
        if seq_alive(): remember_seq_pos(); seq_win["win"].destroy()
        build_day_ui()
        install_playlists()                     # 오늘 테마로 다시 설치 — 코박스 목록이 어제 구성으로 남지 않게
        sync_sleep_entry(); sync_rank_entry(); set_trainer_status()
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
                TODAY_PLAYS[:] = sorted(plays, key=lambda x: t_key(x[1]))
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
                pn_ = today_plan_n()
                if pn_ and len(cur_plays()) >= pn_ and (changed or day_state.get("rep_day") != nk):
                    save_report_today(); day_state["rep_day"] = nk   # 계획을 다 친 뒤로는 판이 들어올 때마다(다시 켠 직후엔 한 번) 기록 파일을 최신으로
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
    build_day_ui(); set_trainer_status()

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
        act = shortcut_action(e.keysym, e.state, isinstance(e.widget, (tk.Entry, tk.Text)))
        if not act: return
        if act.startswith("tab:"): show(act[4:])
        elif act == "rescan":
            _SCAN_STATE["sig"] = None; _SCORE_CACHE.clear(); _INI_CACHE["sig"] = None; scan_once()
            if seq_alive(): update_sequence()
        elif act == "dismiss": tq.clear(); render_toasts()
        elif act == "folder": pick_stats()
        elif act == "cast": open_broadcast()
        elif act == "run" and day_state["pl"]: run_playlist(day_state["pl"])
        return "break"
    root.bind("<Key>", on_key)
    for _k in ("o", "b"): trainer_txt.bind(f"<Control-{_k}>", on_key); ask_txt.bind(f"<Control-{_k}>", on_key)   # Text 클래스의 Ctrl+O(줄 열기)·Ctrl+B(커서) 보다 먼저 — 앱 단축키만 한 번
    legend_lbl.configure(text="F5 다시 읽기 · Ctrl+R 실행 · Ctrl+B 방송 · 1~5 탭 · 6 계획")

    if data.get("out_dir") and not OUT_DIR[0]:
        root.after(1500, lambda: show_toast(f"저장 위치를 쓸 수 없어 기본 폴더에 저장합니다 — {mask_user_path(str(data.get('out_dir')))}", "warn"))
    root.deiconify(); root.update_idletasks(); win_dark()
    if data["win"].get("zoomed") and sys.platform == "win32":
        try: root.state("zoomed")
        except tk.TclError: pass
    refresh_header()
    refresh_files()
    show(data["win"].get("tab") if data["win"].get("tab") in frames else ("today" if training_days(data) else "cal"))   # 처음 켜면 계획부터
    if bcast_cfg().get("open", True) and not os.environ.get("AIMDESK_NO_BCAST"): root.after(400, open_broadcast)   # 녹화되는 화면은 늘 열려 있어야 한다
    root.after(1500, lambda: auto_coach_now("start"))                 # 자동 코치: 어제까지의 기록으로 오늘 목표
    if LOAD_ERROR:
        root.after(500, lambda: messagebox.showwarning("에임 데스크 — 기록 파일", "\n\n".join(LOAD_ERROR)))
    if MIGRATED[0]:
        root.after(900, lambda: show_toast(f"자정에 쪼개져 있던 {MIGRATED[0]}판을 앞 훈련일로 합쳤습니다 (훈련일 경계 {DAY_CUTOFF_H[0]}시)"))
    if DESYNTH[0]:
        root.after(1300, lambda: show_toast(f"치지 않은 기본값 {DESYNTH[0]}개를 PB 에서 걷어냈습니다 — 이제 PB 는 실제로 친 점수뿐입니다"))
    if BASE_DATE[0] is None:
        root.after(1700, lambda: show_toast("오늘은 기준 측정일 — 18개를 한 판씩 치면 그 점수가 내 출발선이 됩니다"))
    try: _stray = stray_data_files()
    except Exception: _stray = []
    if _stray:
        _mine = len(training_days(data))
        if _stray[0]["days"] > _mine:                 # 저쪽이 더 많다 = 기록이 갈라졌다. 토스트로 흘리면 놓친다
            root.after(1200, lambda: messagebox.showwarning("에임 데스크 — 다른 폴더에 기록이 더 있습니다",
                f"지금 쓰는 기록: 훈련 {_mine}일\n{mask_user_path(str(DATA_FILE))}\n\n"
                f"다른 폴더의 기록: {fmt_stray(_stray[0])}\n\n"
                f"exe 를 옮기거나 다른 폴더에서 실행하면 기록이 이렇게 갈라집니다.\n"
                f"도구 탭 → 기록 파일 → '이 기록 합치기' 로 한쪽으로 모을 수 있습니다 (양쪽 다 남습니다)."))
        else:
            root.after(2100, lambda: show_toast(f"다른 폴더에도 기록이 있습니다 ({fmt_stray(_stray[0])}) — 도구 탭에서 합칠 수 있습니다"))
    root.after(300, tick)
    root.after(450, refresh)
    def on_close():
        remember_seq_pos(); remember_bcast()
        if cur_plays(): save_report_today()                 # 중간에 닫아도 오늘 판이 있으면 기록은 남긴다
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
    _DBG.update(root=root, pl_lbl=pl_lbl, trainer_txt=trainer_txt, apply_trainer=apply_trainer, clear_trainer=clear_trainer,
                band_cv=band_cv, rec_now=rec_now, set_bcast=set_bcast, bcast_cfg=bcast_cfg, BCAST_PRESETS=BCAST_PRESETS, note_pb_flash=note_pb_flash, hdr_story=hdr_story, hdr_stage=hdr_stage, refresh_cal=refresh_cal, cnt_lbl=cnt_lbl, hero=hero, todo_host=todo_host, hdr_day=hdr_day, cv_trend=cv_trend, draw_trend=draw_trend, lv_line=lv_line, stage_line=stage_line, foot=foot, settings_lbl=settings_lbl, run_btn=run_btn, cols=cols, set_theme=set_theme, theme_btns=theme_btns, auto_coach_now=auto_coach_now, ai_coach_now=ai_coach_now, coach_lbl=coach_lbl, ai_lbl=ai_lbl, coach_cfg=coach_cfg, ai_key_var=ai_key_var, cal_state=cal_state, cbody=cbody, do_graduate=do_graduate, grad_btn=grad_btn, grad_title=grad_title, grad_lbl=grad_lbl, save_week_now=save_week_now, games_var=games_var, set_why=set_why, why_var=why_var, val_sync_now=val_sync_now, val_lbl=val_lbl, rid_var=rid_var, set_cutoff=set_cutoff, cut_btns=cut_btns, fstat=fstat, do_reset=do_reset, refresh_files=refresh_files, hdr_mi=hdr_mi, verdicts=lambda: verdicts(data, today_key[0], day_state.get("dt"), cur_plays(), day_state.get("hero_state")),
                set_routine_open=set_routine_open, set_drawer=set_drawer, drawer=drawer, cur_lbl=cur_lbl, cur_score=cur_score, cur_word=cur_word,
                auto_mini=auto_mini, live=live, show_sequence=show_sequence, tier_var=tier_var, rr_var=rr_var, commit_rank=commit_rank, trainer_mini=trainer_mini,
                trainer_lbl=trainer_lbl, save_report_today=save_report_today, draw_ribbon=draw_ribbon, today_plan_n=today_plan_n, cv_sess=cv_sess, hdr_lv=hdr_lv, open_card=open_card, card_win=card_win, set_scale=set_scale, scale_btns=scale_btns, set_broadcast=set_broadcast, open_broadcast=open_broadcast, bcast=bcast, data=data, refresh=refresh, refresh_tab=refresh_tab, dirty=dirty, cur_tab=cur_tab, show=show,
                scan_once=scan_once, tick=tick, seq_win=seq_win, auto=auto, routine_rows=routine_rows, day_state=day_state,
                tq=tq, status_lbl=status_lbl, status_dot=status_dot, show_toast=show_toast, render_toasts=render_toasts,
                toast=toast, toast_tick=toast_tick, on_close=on_close, left_scroll=left_scroll, right_scroll=right_scroll,
                grow_scroll=grow_scroll, bench_scroll=bench_scroll, on_wheel=on_wheel, frames=frames, tabbtns=tabbtns,
                open_sequence=open_sequence, update_sequence=update_sequence, run_playlist=run_playlist,
                VScroll=VScroll, cv_idx=cv_idx, cv_ben=cv_ben, hdr_e=hdr_e, hdr_idx=hdr_idx, set_status=set_status,
                hist_cells=hist_cells, det_lines=det_lines, det_title=det_title, grow_title=grow_title, select_day=select_day,
                hdr_streak=hdr_streak, wk_cv=wk_cv, section_labels=section_labels, advice_lbl=advice_lbl, ben_rows=ben_rows,
                dth_lbl=dth_lbl, steppers=steppers, on_key=on_key, pick_stats=pick_stats,
                detail=detail, open_detail=open_detail, spark_cvs=spark_cvs, daych=daych, set_compact=set_compact,
                apply_out_dir=apply_out_dir, out_lbl=out_lbl, out_reset_btn=out_reset_btn,
                open_coach_note=open_coach_note, note_lnk=note_lnk, note_win=note_win, ask_txt=ask_txt, refresh_today=refresh_today)
    _DBG.setdefault("counters", {}).setdefault("refresh_tab", 0)
    if os.environ.get("AIMDESK_NO_MAINLOOP"): return
    root.mainloop()

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        # 검사 기본 상태 = 기준 측정을 끝낸 사용자. '측정 전' 경로는 그때그때 명시해서 확인한다
        BASE_DATE[0], BASELINE[0] = SAMPLE_DATE, dict(SAMPLE)
        def _fresh():                                   # 기준 측정 전 상태로 잠깐 돌아간다
            BASE_DATE[0], BASELINE[0] = None, None
        def _measured():
            BASE_DATE[0], BASELINE[0] = SAMPLE_DATE, dict(SAMPLE)
        e, n = totalE(SAMPLE)
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
        assert sum(n for _, n in dict(playlists_for("2026-09-10"))["AIMDESK Day"]) == 20
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
        assert contrast_ratio(_c0["dim"], _c0["card"]) >= 4.5                   # v6.1: 기본 팔레트의 dim 도 4.5:1 이상 (예전 3.3:1 은 1080p 에서 '없는 글씨'였다)
        C.update(_c0); RANKC[:] = _r0
        # v6.3: 밝은 테마 — 카드 위 글자색 전부 4.5:1 이상, 고대비 모드도, 랭크색도. 방송 팔레트(BC)는 테마와 무관
        assert apply_theme("light") == "light" and C["card"] == "#FFFFFF" and DAY_TYPE["b"][1] == C["gold"] and BC["bg"] == "#0B0E11"
        for _k in ("txt", "sub", "hint", "dim", "wait", "val", "ow", "ok", "gold", "up", "flat", "down", "swt"):
            assert contrast_ratio(C[_k], C["card"]) >= 4.5, ("light", _k, contrast_ratio(C[_k], C["card"]))
        for _rc in RANKC: assert contrast_ratio(_rc, C["card"]) >= 4.5, ("light rank", _rc)
        assert contrast_ratio(C["onfill"], C["gold"]) >= 4.5 and contrast_ratio(C["onfill"], C["ok"]) >= 4.5 and rank_of(450)[1] == RANKC_LIGHT[3]
        assert apply_broadcast(True) is True and contrast_ratio(C["dim"], C["card"]) >= 5.5 and RANKC == RANKC_HC_LIGHT
        assert apply_theme("dark") == "dark" and C == _c0 and RANKC == _r0 and rank_of(450)[1] == RANKC_DARK[3]
        assert contrast_ratio(C["hint"], C["card"]) >= 4.5 and contrast_ratio(C["txt"], C["card"]) >= 7 and contrast_ratio(C["dim"], C["card"]) >= 3.0
        assert shade("#14191F", 16) == "#24292f" and shade("#000000", -10) == "#000000"
        assert t_min("19.43.00") == 1183
        assert blank_day()["plays"] == [] and blank_day()["sess"] == {"start": None, "end": None}
        assert next_rank_gap(413, [290,340,390,445]) == ("Gold", 445, 32) and next_rank_gap(500, [290,340,390,445])[0] is None
        assert sub_of("zzz") is None and sub_of("dot")[0] == "speed" and th_of("dot") == [845,940,1030,1090]
        pc = pb_context("dot", 1002, 990, {"dot": 1002, "eddie": 780}); assert "Speed" in pc and "→268" in pc and "Silver까지 28점" in pc, pc
        assert "✓" in pb_context("dot", 1100, 990, {"dot": 1100})
        assert len(pb_toast_lines([("dot", 1002, 12)], {"dot": 1002})) == 1 and len(pb_toast_lines([("dot",1,1),("pasu",1,1)], {})) == 2
        assert len(pb_toast_lines([(k, 1, 1) for k in tier_keys("n")], {})) == 1 and len(pb_toast_lines([(k, 1, 1) for k in tier_keys("n")], {})[0]) <= 60
        q = ToastQueue(); [q.push(f"m{i}", "info", 0) for i in range(4)]; assert len(q.items) == 3
        assert q.expire(10.1) and q.items == []; q.push("a","info",0); q.push("b","info",0); q.dismiss(0); assert q.items[0][0] == "b"
        assert status_line({}, False, False, None, False)[1] == "err" and status_line({}, True, True, None, False)[1] == "warn"
        assert status_line({"plays": 0}, True, False, None, False)[1] == "warn" and status_line({}, True, False, "x", False)[0].startswith("● 저장 실패")
        okl = status_line({"plays": 3, "t": "10:00:00", "other": 1}, True, False, None, True); assert okl[1] == "ok" and "루틴 외 1판" in okl[0] and okl[0].endswith("자동 진행 ▶")
        rows_, npb_, rel_ = seq_rows_apply(["pasu","dot","frog"], [True, False, False], 1, [850, None, None],
                                            lambda k: (800.0, 806) if k == "pasu" else (900.0, 1000))
        assert rows_[0][2] == "✓" and rows_[0][6] == "PB!" and rows_[1][2] == "▶" and rows_[1][4] == "900" and rows_[2][2] == "" and npb_ == 1 and len(rel_) == 1, rows_
        assert bench_src_label(SAMPLE_DATE, 9) == "기준 측정 · 8/29 · 9/9" and bench_src_label("2026-09-02", 5) == "2026-09-02 · 5/9" and bench_src_label(None, 0) == ""
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
        assert streak({"2026-09-06","2026-09-08"}, date(2026,9,8))[0] == 2           # 월요일(휴식) 건너뜀
        assert streak({"2026-09-05","2026-09-07"}, date(2026,9,7))[0] == 1           # 일요일은 훈련일 — 빠지면 끊긴다
        ws = week_strip({"2026-09-01"}, date(2026,9,3)); assert len(ws) == 7 and ws[0][1] == "rest" and ws[1][1] == "done" and ws[2][1] == "miss" and ws[3][1] == "today" and ws[4][1] == "future" and ws[6][1] == "future", ws
        assert SAMPLE_DATE not in training_days({"days": {SAMPLE_DATE: {"first": {}, "count": {}, "best": dict(SAMPLE)}, "2026-09-01": {"first": {"pasu": 1}, "count": {"pasu": 1}}}})
        sg = segment_geometry(120, 6); assert len(sg) == 6 and sg[-1][1] <= 120 and max(b-a for a, b in sg) - min(b-a for a, b in sg) <= 1
        assert len(segment_geometry(60, 12)) == 12 and len(segment_geometry(100, 30)) == 12
        dsyn = {"first": {"pasu": 1}, "count": {"ground": 2, "dot": 3}, "checks": {"miyagi": True, "ranked": False}}
        assert section_progress([("probe","pasu",1),("probe","w4",1)], dsyn) == (1, 2) and section_progress([("warm","ground",2)], dsyn) == (2, 2)
        assert section_progress([("main","dot",6)], dsyn) == (3, 6) and section_progress([("check","miyagi",1),("check","ranked",1)], dsyn) == (1, 2)
        assert next_routine_key([("warm","ground",2),("main","dot",6)], dsyn, None) == "dot" and next_routine_key([], dsyn, "frog") == "frog"
        for sub_t in SUBS:
            for _k, th_t in sub_t[3]:
                for e_t in (200, 300, 400): assert scenE(math.ceil(score_for_energy(e_t, th_t)), th_t) >= e_t
        wl = weakest_link(SAMPLE)
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
        assert sm == "오늘 14/27판 · PB 1 🏆 · ▲2.3% · 프로브 6/6 발로 +0.4 · 남은 13판 ≈ 18분", sm
        fx = {"pb": {"eddie": 800}, "days": {SAMPLE_DATE: {"first": {}, "best": dict(SAMPLE)}}}
        for i, v in enumerate((740, 750, 745, 705)):
            fx["days"][f"2026-09-0{i+1}"] = {"first": {"eddie": v}, "best": {"eddie": v}}
        assert focus_pick(fx, "2026-09-05")[0] == "eddie"                                   # 705 는 평균 745 의 -5%
        fx["days"]["2026-09-04"]["first"]["eddie"] = 730; assert focus_pick(fx, "2026-09-05") is None   # -2%
        assert focus_pick({"pb": {}, "days": {"2026-09-01": {"first": {"eddie": 700}, "best": {}}}}, "2026-09-02") is None
        assert cond_adjust({"sleep": 5, "feel": 5}).startswith("수면 5h") and cond_adjust({"sleep": 8, "feel": 7}) is None and cond_adjust({"sleep": None, "feel": 2}).startswith("체감 2")
        assert probe_validity([("pasu","1",1),("ground","2",1),("ground","3",1)]) == ("pasu", "cold")
        assert probe_validity([("ground","1",1),("frog","2",1),("pasu","3",1)]) is None
        assert probe_validity([("ground","0",1)] + [("eddie", str(i), 1) for i in range(4)]) == ("eddie", "extra")
        nr = nearest_rankup(SAMPLE); assert nr and nr[1] in SAMPLE and nr[3] in RANK_NAMES
        sb = session_brief(fx, "2026-09-05", "v", []); assert 1 <= len(sb) <= 3 and ("초점" in sb[0][0] or "랭크업" in sb[0][0]), sb
        assert session_brief(fx, "2026-09-05", "r", [], alt=[("x", "sub")]) == [("x", "sub")]
        # v3 기록 탭 · 단축키
        hx = {"pb": dict(SAMPLE), "days": {SAMPLE_DATE: dict(blank_day(), first=dict(SAMPLE), best=dict(SAMPLE), count={k: 1 for k in SAMPLE}),
              "2026-09-01": dict(blank_day(), first={"pasu": 800}, best={"pasu": 850}, count={"pasu": 2}, sess={"start": "10.00.00", "end": "10.41.00"},
                                 deaths={"aim": 2, "pos": 1, "dec": 0, "trade": 0}, cond={"sleep": 7, "caf": 0, "feel": 6}, checks={"miyagi": True, "ranked": False}),
              "2026-09-03": dict(blank_day(), first={"dot": 1}, best={"dot": 1}, count={"dot": 1})}}
        hx["pb"]["pasu"] = 850
        hr = history_rows(hx, "2026-09-03", probe_series(hx), pb_days(hx), n=6)
        assert len(hr) == 6 and hr[0]["date"] == "2026-09-03" and hr[1]["trained"] is False and hr[2]["trained"] is True
        assert hr[5]["dtype"] == "base" and hr[5]["trained"] is True and hr[5]["energy"] == 339 and hr[2]["energy"] is None
        assert hr[5]["pbs"] == []                                          # 출발선은 신기록으로 세지 않는다
        assert hr[2]["pbs"] == ["pasu"] and hr[2]["minutes"] == 41 and hr[2]["dom"] == "에임"
        fr = fmt_history_row(hr[2]); assert fr[0] == "09-01 화" and fr[2] == "2" and fr[3] == "41" and fr[6] == "1" and fr[7] == "3 에임" and fr[11] == "", fr
        assert fmt_history_row(hr[1])[2] == "·" and fmt_history_row(hr[5])[1] == "기준"
        dd_ = day_detail(hx, "2026-09-01"); assert [x[0] for x in dd_] == [k for sub in SUBS for k, _ in sub[3]] and dd_[0] == ("pasu", 800, 850, 2, True)
        _fresh()
        assert growth_since_base({"pb": dict(SAMPLE), "days": {}}) == [] and energy_delta({"pb": dict(SAMPLE)}) == (None, 339)   # 기준 측정 전엔 잴 게 없다
        _measured()
        g0 = growth_since_base({"pb": dict(SAMPLE), "days": {}}); assert len(g0) == 18 and all(r["stalled"] for r in g0) and energy_delta({"pb": dict(SAMPLE)}) == (339, 339)
        _gu = growth_since_base({"pb": dict(SAMPLE, pasu=900), "days": {}})
        assert _gu[0]["key"] == "pasu" and not _gu[0]["stalled"] and _gu[0]["gain"] == 94, _gu[0]
        g1 = growth_since_base(hx); assert g1[0]["key"] == "pasu" and abs(g1[0]["pct"] - 5.46) < 0.01 and fmt_growth_row(g1[0])[3] == "" and g1[0]["band_pb"] == "Gold"
        assert fmt_growth_row(g1[-1])[2] == "정체"
        # v3.2 훈련 레벨
        assert level_of(0)[:2] == (1, "입문") and level_of(29)[0] == 1 and level_of(30)[:2] == (2, "수련")
        assert level_of(10 ** 6)[3] is None and level_frac(10 ** 6) == 1.0
        assert level_frac(0) == 0.0 and abs(level_frac(55) - 0.5) < 1e-9
        assert fmt_level(55) == "Lv.2 수련  25/50", fmt_level(55)
        _xd = {"days": {SAMPLE_DATE: dict(blank_day(), best={"pasu": 800}),
                        "2026-09-09": dict(blank_day(), best={"pasu": 850}, plays=[["pasu", "10.00.00", 850]] * 3),
                        "2026-09-10": dict(blank_day(), best={"pasu": 840}, plays=[["pasu", "11.00.00", 840]] * 2)}}
        assert total_pbs(_xd) == 1 and total_xp(_xd) == 5 + 5 * 1           # 판 5 + 신기록 1
        assert total_xp({"days": {}}) == 0 and total_pbs({"days": {}}) == 0
        assert total_xp({"days": {"2026-09-09": dict(blank_day(), count={"pasu": 4})}}) == 4   # 옛 파일: count 합
        _fresh(); assert total_pbs(_xd) == 2; _measured()                   # 기준선이 없으면 그 날 점수도 신기록으로 센다
        # v3.2 세션 곡선
        bump_ver()
        _sd = {"pb": {}, "days": {"2026-09-10": dict(blank_day(), plays=[["pasu", "10.00.00", 806], ["pasu", "10.02.00", 900]])}}
        assert play_base(_sd, "pasu", "2026-09-10") == SAMPLE["pasu"]                  # 첫날: 기준값으로 물러난다
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
        _fs = fmt_seq_summary(3, 27, 1, [0.05, -0.05], None, (None, None), None, None, ribbon_counts(_v))
        assert "오늘 3/27판" in _fs and "최고 1" in _fs and "%" not in _fs, _fs        # 판정 개수로 (▲▼% 없음)
        _fs2 = fmt_seq_summary(3, 27, 1, [0.05], None, (None, None), None)
        assert "PB 1 🏆" in _fs2 and "%" in _fs2, _fs2                                  # counts 없으면 옛 표기 유지
        assert shortcut_action("6", 0, False) == "tab:cal" and shortcut_action("2", 0, False) == "tab:grow" and shortcut_action("2", 0, True) is None and shortcut_action("F5", 0, True) == "rescan" and shortcut_action("5", 0, False) == "tab:tools"
        assert shortcut_action("r", 0x4, False) == "run" and shortcut_action("r", 0, False) is None and shortcut_action("o", 0x4, True) == "folder"
        assert shortcut_action("b", 0x4, False) == "cast" and shortcut_action("b", 0, False) is None
        assert seq_shortcut_action("space", 0, False) == "auto" and seq_shortcut_action("space", 0, True) is None and seq_shortcut_action("n", 0x4, False) == "skip"
        assert seq_shortcut_action("Escape", 0, True) == "blur" and seq_shortcut_action("Escape", 0, False) == "close" and seq_shortcut_action("r", 0, False) is None
        # v3 권장: 정체·다음 한 걸음·벤치 준비도·주간 리캡
        assert plateau([800,802,799,801,800,803,798,800,801,799]) and not plateau([800,810,820,830,840,850,860,870,880,890]) and not plateau([800]*5)
        assert spark_tag([800,810,820,830,840,850,860,870,880,890]) == "↗" and spark_tag([]) == "" and spark_tag([900,880,860,840]) == "↘"
        nx = {"pb": dict(SAMPLE), "days": {"2026-09-03": dict(blank_day(), first={"eddie": 720}, best={"eddie": 720}, count={"eddie": 1})}}
        assert "Eddie" in next_step(nx, "2026-09-03", [("eddie","10.00.00",720)], {"eddie": 745.0}) and "745" in next_step(nx, "2026-09-03", [], {"eddie": 745.0})
        dotp = [("dot", f"10.0{i}.00", v) for i, v in enumerate((1000, 990, 970, 950, 940, 930))]
        ns2 = next_step({"pb": dict(SAMPLE), "days": {"2026-09-03": blank_day()}}, "2026-09-03", dotp, {}); assert "6→4판" in ns2, ns2
        ns3 = next_step({"pb": dict(SAMPLE), "days": {"2026-09-03": blank_day()}}, "2026-09-03", [], {}); assert "다음:" in ns3 or "프로브부터" in ns3
        full = dict(blank_day(), count={k: n for k, n in WARMUP + MAIN}, first={k: 1 for k in PROBE})
        assert routine_complete(full, "v") and not val_done(full)                                       # 발로 블록은 완료 조건이 아니다 (숫자만 기록)
        full["val"] = {"range": 25, "dm_k": 20, "dm_d": 15, "dm_hs": 31.0, "skip": False}
        assert routine_complete(full, "v") and val_done(full) and not routine_complete(dict(full, first={k: 1 for k in PROBE[1:]}), "v") and not routine_complete(full, "r")
        assert fmt_val(full) == "사격 25/30 · DM 20/15 (K/D 1.33) · HS 31%" and fmt_val(blank_day()) == ""
        assert val_done(dict(blank_day(), val={"skip": True})) and fmt_val(dict(blank_day(), val={"skip": True})) == "발로 블록 건너뜀"
        bx = {"pb": dict(SAMPLE), "days": {SAMPLE_DATE: dict(blank_day(), best=dict(SAMPLE))}}
        br = bench_readiness(bx, "2026-09-04"); assert br["e_pb"] == 339 and br["week_pbs"] == [] and br["last_run"] == (SAMPLE_DATE, 339), br
        bx["days"]["2026-09-01"] = dict(blank_day(), best={"pasu": 820}, count={"pasu": 1}); bump_ver()
        assert week_pbs(bx, "2026-09-04") == ["pasu"] and projected_energy(SAMPLE, {"pasu": 500})[0] < 339
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
        sh = scen_history(hx, "pasu", "2026-09-03"); assert [h["date"] for h in sh] == [SAMPLE_DATE, "2026-09-01"] and sh[1]["first"] == 800
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
        assert dict(_pls)["AIMDESK Bench"] == [(k, 1) for s in SUBS for k, _ in s[3]] and len(dict(_pls)["AIMDESK Bench"]) == 18 and len(_pls) == 3
        # 요일 변주: 한 주의 훈련일(화~금·일)이 모두 다르고, 다음 주엔 밀린다
        _mon = date.fromisoformat("2026-09-07")
        _vd = [i for i in range(7) if DAYTYPES[i] == "v"]; assert _vd == [1, 2, 3, 4, 6] and DAYTYPES[REST_WD] == "r" and DAYTYPES[BENCH_WD] == "b"
        _wk = [main_theme((_mon + timedelta(days=i)).isoformat(), SAMPLE)[0] for i in _vd]
        assert len(set(_wk)) == 5, _wk
        _wk2 = [main_theme((_mon + timedelta(days=7 + i)).isoformat(), SAMPLE)[0] for i in _vd]
        assert _wk2 != _wk and len(set(_wk2)) == 5, _wk2
        assert _train_ord(date(2026, 9, 14)) == _train_ord(date(2026, 9, 13)) and _train_ord(date(2026, 9, 15)) == _train_ord(date(2026, 9, 13)) + 1 and _train_ord(date(2026, 9, 20)) == _train_ord(date(2026, 9, 18)) + 1
        for _t in MAIN_THEMES: assert sum(n for _, n in _t[3]) == MAIN_PLAYS and all(n <= 2 for _, n in _t[3]) and all(_t[3][i][0] != _t[3][i + 1][0] for i in range(len(_t[3]) - 1)), _t[0]
        assert sum(n for _, n in main_theme("2026-09-10", SAMPLE)[3]) == MAIN_PLAYS
        assert main_theme("2026-09-10")[0] != "weak"                      # 기록 없으면 약점 테마로 안 감
        assert [main_theme((_mon + timedelta(days=i)).isoformat(), SAMPLE)[0] for i in _vd] == ["spd", "clk", "weak", "flk", "swt"], [main_theme((_mon + timedelta(days=i)).isoformat(), SAMPLE)[0] for i in _vd]   # 9/8 화 = 주기 6번(index 5) · 9/15 화 = 1번
        _c10 = [main_theme((date.fromisoformat(CYCLE_EPOCH) + timedelta(days=i)).isoformat(), SAMPLE)[0] for i in range(14) if day_type_of((date.fromisoformat(CYCLE_EPOCH) + timedelta(days=i)).isoformat()) == "v"]
        assert _c10 == CYCLE and all(_c10[i] != _c10[i + 1] for i in range(9)) and all(_c10[i] != _c10[i + 5] for i in range(5)), _c10   # 이틀 연속 같은 테마 없음 · 같은 요일 2주 연속 없음
        assert _c10.count("clk") + _c10.count("spd") == 4 and "trk" not in _c10                                      # 발로: 클리킹 4/10, 트래킹은 지정할 때만
        _w = weak_theme(SAMPLE); assert _w and _w[0] == "weak" and sum(n for _, n in _w[3]) == MAIN_PLAYS and all(n <= 2 for _, n in _w[3])
        assert weak_theme({}) is None and weak_theme({"pasu": 700}) is None
        assert theme_line("2026-09-08", SAMPLE).startswith("오늘 본훈련 · ") and "내일은 " in theme_line("2026-09-08", SAMPLE)   # 화→수
        assert "2일 뒤는 " in theme_line("2026-09-11", SAMPLE), theme_line("2026-09-11", SAMPLE)             # 금→일 (토는 벤치)
        assert "2일 뒤는 " in theme_line("2026-09-13", SAMPLE), theme_line("2026-09-13", SAMPLE)             # 일→화 (월은 쉼)
        assert theme_line("2026-09-11").startswith("오늘 본훈련") and theme_line("2026-09-12") == "" and theme_line("2026-09-14") == ""   # 금·일요일도 테마 · 토·월은 고정
        _wt = week_themes("2026-09-09", SAMPLE)
        assert _wt.startswith("이번 주 · 화 ") and "▶수 " in _wt and _wt.count("·") == 5 and " 금 " in _wt and " 일 " in _wt and "월" not in _wt, _wt
        assert week_themes("2026-09-12") == "" and week_themes("2026-09-14") == ""   # 토·월엔 안 띄운다
        _ch = daily_challenge({"pb": dict(SAMPLE), "days": {}}, "2026-09-10", dict(SAMPLE))
        assert _ch is None or (_ch["target"] > _ch["cur"] and _ch["sigma"] <= 2.5 and _ch["key"] in dict(SCEN)), _ch
        _far = daily_challenge({"pb": {"ww5": 10}, "days": {}}, "2026-09-10", {"ww5": 10}); assert _far is None   # 너무 멀면 안 낸다
        _c2 = {"key": "dot", "target": 1030, "cur": 983, "rank": "Silver", "gap": 47, "sigma": 1.2}
        assert fmt_challenge(_c2).startswith("오늘의 도전 · DotTS 1030점 — 넘으면 Silver 칸")
        assert "17 남음" in fmt_challenge(_c2, 1013) and "✓ 달성" in fmt_challenge(_c2, 1030)
        assert fmt_challenge(None) == "" and daily_challenge({"pb": {}, "days": {}}, "2026-09-13") is None
        assert sum(n for _, n in dict(playlists_for("2026-09-10", SAMPLE))["AIMDESK Day"]) == 20
        assert seq_rows_apply(["pasu"], [True], None, [None], lambda k: (None, None))[0][0][6] == "건너뜀"
        import tempfile as _tf
        with _tf.TemporaryDirectory() as _td:
            _st = Path(_td) / "FPSAimTrainer" / "stats"; _st.mkdir(parents=True)
            _n, _d, _w = ensure_playlists(_st); assert (_n, _w) == (3, 3) and _d == Path(_td) / "FPSAimTrainer" / "Saved" / "SaveGames" / "Playlists"
            _raw = (_d / "AIMDESK Bench.json").read_bytes(); assert _raw[:2] == b"\xff\xfe" and "\r\n" in _raw.decode("utf-16")        # 기본: UTF-16 BOM + CRLF
            _obj = json.loads(_raw.decode("utf-16")); assert _obj["playlistName"] == "AIMDESK Bench" and [x["scenario_Name"] for x in _obj["scenarioList"]] == [SCEN[k][0] for k, _ in BENCH]
            assert ensure_playlists(_st)[2] == 0                                                                    # 같은 내용이면 다시 쓰지 않는다
            (_d / "Mine.json").write_text(json.dumps({"playlistName": "Mine", "version": 3, "scenarioList": [{"scenario_Name": "x", "play_Count": 1}]}), encoding="utf-8")
            _n, _d, _w = ensure_playlists(_st); assert (_n, _w) == (3, 3) and PL_STATE["tpl"] == "Mine" and PL_STATE["enc"] == "utf-8"
            _raw = (_d / "AIMDESK Day.json").read_bytes(); assert _raw[:1] == b"{" and b"\r\n" not in _raw            # 코박스 파일 형식(UTF-8, LF)을 따라간다
            _obj = json.loads(_raw.decode("utf-8")); assert _obj["version"] == 3 and _obj["playlistName"] == "AIMDESK Day" and len(_obj["scenarioList"]) == len(dict(playlists_for(today_date().isoformat()))["AIMDESK Day"])
        os.environ["AIMDESK_TODAY"] = "2026-09-05"; assert today_date().weekday() == 5
        os.environ["AIMDESK_TODAY"] = "bad"; assert today_date() in (date.today(), date.today() - timedelta(days=1)); del os.environ["AIMDESK_TODAY"]   # 새벽 5시 경계 전이면 어제
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
        _sh = sub_shape({"pasu": 660, "popcorn": 500}, SAMPLE)
        assert len(_sh) == 9 and _sh[0]["id"] == "dyn" and _sh[0]["e"] == 200 and _sh[0]["delta"] < 0 and _sh[1]["e"] is None
        assert within_day_gain([("a", "1", 100), ("a", "2", 100)]) is None                   # 3판 미만 제외
        assert within_day_gain([("a", "1", 100), ("a", "2", 110), ("a", "3", 120)]) == 20.0  # 앞1 뒤1: 100→120
        # v3.4 트레이너 루프: 이름 찾기 · 답장 파싱 · 테마/도전 덮어쓰기 · 기록 텍스트
        assert scen_lookup("Pasu") == "pasu" and scen_lookup("VT Pasu Novice S5") == "pasu" and scen_lookup("1w4ts") == "w4" and scen_lookup("floating heads") == "float"
        assert scen_lookup("floating") == "float" and scen_lookup("ground novice") == "ground" and scen_lookup("controlsphere") == "csphere" and scen_lookup("snake") == "snake"
        assert scen_lookup("control") is None and scen_lookup("xyz") is None and scen_lookup("") is None and scen_lookup(None) is None and scen_lookup("pa") is None
        assert scen_lookup("Pasu Novice S5") == "pasu" and scen_lookup("Pasu 861 / 861 /") is None and scen_lookup("pasu850ground") is None   # 기록 파일 줄을 붙여넣어도 엉뚱한 목표가 잡히지 않게
        _pr = parse_trainer("  Pasu            861 /   861 /  1 · PB 902 (09-10)\n목표 Pasu 850 Ground 3300", "2026-09-10")
        assert _pr["targets"] == {} and len(_pr["errors"]) == 2, _pr
        assert theme_lookup("트래킹") == "trk" and theme_lookup("클리킹 집중") == "clk" and theme_lookup("전체 순회") == "mix" and theme_lookup("약점") == "weak"
        assert theme_lookup("switching") == "swt" and theme_lookup("??") is None and theme_lookup("") is None
        assert day_type_of("2026-09-10") == "v" and day_type_of("2026-09-11") == "v" and day_type_of("2026-09-12") == "b" and day_type_of("2026-09-13") == "v" and day_type_of("2026-09-14") == "r"
        _p = parse_trainer("목표 Pasu 850\n- 도전: Ground 3300점 (지금 3181)\nPopcorn 700\n테마 내일 트래킹\n테마 2026-09-15 약점\n"
                           "메모 첫 판 전에 손 풀기\n이상한 줄\n# 주석\n\n목표 Popcorn 없음\ntarget eddie: 800 — 넘으면 Silver", "2026-09-10")
        assert _p["targets"] == {"pasu": 850, "ground": 3300, "eddie": 800} and _p["challenge"] == "ground", _p
        assert _p["themes"] == {"2026-09-11": "trk", "2026-09-15": "weak"} and _p["note"] == "첫 판 전에 손 풀기", _p
        assert _p["errors"] == ["이상한 줄"] and _p["remove"] == ["popcorn"], _p
        assert parse_trainer("", "2026-09-10")["targets"] == {} and parse_trainer("테마 내일 ???", "2026-09-10")["errors"] == ["테마 내일 ???"]
        _pb = parse_trainer("테마 2026-09-31 트래킹\n테마 2026-13-01 약점", "2026-09-10"); assert _pb["themes"] == {} and len(_pb["errors"]) == 2   # 달력에 없는 날
        _tl = {"trainer": {"themes": {"2026-09-31": "trk", "2026-09-15": "trk"}, "targets": {"pasu": "850", "zzz": 1}}}
        trainer_load(_tl); assert TRAINER["themes"] == {"2026-09-15": "trk"} and TRAINER["targets"] == {"pasu": 850}; trainer_load({})
        assert scen_lookup("Pasu는") == "pasu" and scen_lookup("Pasu를") == "pasu" and scen_lookup("Popcorn 오늘") is None and scen_lookup("Ground PB") is None
        assert parse_trainer("Pasu PB 900\nPopcorn 오늘 660\nGround 어제 3181\nPasu는 850", "2026-09-10")["targets"] == {"pasu": 850}   # 답장의 현황 요약 줄은 목표가 아니다
        assert parse_trainer("메모 Pasu 850 넘기, PB 노리기", "2026-09-10")["note"] == "Pasu 850 넘기, PB 노리기"                    # 메모는 대소문자 그대로
        _td = {"pb": dict(SAMPLE), "days": {}}
        _pp = trainer_apply(_td, "목표 Pasu 850\n도전 Pasu 850\n테마 2026-09-15 트래킹\n메모 손 풀기", "2026-09-10")
        assert TRAINER["targets"] == {"pasu": 850} and TRAINER["challenge"] == "pasu" and _td["trainer"]["set_on"] == "2026-09-10" and TRAINER["note"] == "손 풀기"
        assert main_theme("2026-09-15", SAMPLE)[0] == "trk" and main_theme("2026-09-16", SAMPLE)[0] != "trk"     # 그 하루만 지정 (원래 9/15 = clk)
        assert "트레이너 지정" in theme_line("2026-09-15", SAMPLE) and "트레이너 지정" not in theme_line("2026-09-16", SAMPLE)
        assert sum(n for _, n in dict(playlists_for("2026-09-15", SAMPLE))["AIMDESK Day"]) == 20
        _ch = daily_challenge(_td, "2026-09-10", dict(SAMPLE))
        assert _ch and _ch["src"] == "trainer" and _ch["key"] == "pasu" and _ch["target"] == 850 and _ch["cur"] == 806 and _ch["gap"] == 44, _ch
        assert fmt_challenge(_ch).startswith("오늘의 도전 · Pasu 850점 — 트레이너 목표 (지금 최고 806)") and "✓ 달성" in fmt_challenge(_ch, 860)
        trainer_apply(_td, "목표 Pasu 없음", "2026-09-10")
        assert TRAINER["targets"] == {} and TRAINER["challenge"] is None and TRAINER["note"] == "손 풀기"     # 언급 없는 것은 남는다
        _c0 = daily_challenge(_td, "2026-09-10", dict(SAMPLE)); assert _c0 is None or _c0.get("src") != "trainer"
        trainer_apply(_td, "목표 Ground 3300\n목표 Pasu 850", "2026-09-10")
        _c1 = daily_challenge(_td, "2026-09-16", dict(SAMPLE)); assert _c1 and _c1["key"] == "pasu" and _c1["src"] == "trainer", _c1   # 수(스위칭)엔 Ground 없음 (화는 트레이너가 트래킹 지정) · Pasu 는 프로브라 매일 도전이 된다
        trainer_apply(_td, "도전 Snake 3300", "2026-09-10")
        _c3 = daily_challenge(_td, "2026-09-16", dict(SAMPLE)); assert _c3 is None or _c3["key"] != "snake", _c3       # 지정 도전도 오늘 안 치면 안 낸다
        _c4 = daily_challenge(_td, "2026-09-12", dict(SAMPLE)); assert _c4 and _c4["key"] == "snake" and _c4["src"] == "trainer", _c4   # 토요일 벤치엔 친다
        trainer_apply(_td, "도전 Snake 없음", "2026-09-10")
        assert suggest_target(850, 861, {"hi": 842}) == 867 and suggest_target(850, 840, {"hi": 842}) == 850 and suggest_target(850, None, None) == 850
        assert suggest_target(850, 861, {"hi": 880}) == 880 and suggest_target(None, 861, {"hi": 842}, 806) == 879 and suggest_target(None, None, None) is None
        assert plan_count("2026-09-10", SAMPLE) == 20 and plan_count("2026-09-12") == 18 and plan_count("2026-09-14") == 0 and plan_count("2026-09-13") == 20 and plan_count("2026-09-11") == 20
        _rd = {"pb": dict(SAMPLE), "days": {SAMPLE_DATE: dict(blank_day(), best=dict(SAMPLE)),
               "2026-09-09": dict(blank_day(), first={"pasu": 790}, best={"pasu": 800, "ground": 3100}, count={"pasu": 2, "ground": 1},
                                  plays=[["pasu", "10.00.00", 790], ["pasu", "10.02.00", 800], ["ground", "10.04.00", 3100]]),
               "2026-09-10": dict(blank_day(), first={"pasu": 870}, best={"pasu": 900, "ground": 3000}, count={"pasu": 2, "ground": 1},
                                  plays=[["ground", "10.00.00", 3000], ["pasu", "10.02.00", 870], ["pasu", "10.30.00", 900]],
                                  cond={"sleep": 7.5, "caf": 0, "feel": 6}, checks={"miyagi": True, "ranked": False}, deaths={"aim": 2, "pos": 0, "dec": 1, "trade": 0})}}
        _rd["pb"]["pasu"] = 900; bump_ver()
        _rt = daily_report(_rd, "2026-09-10")
        for _sec in ("[요약]", "[판별 기록]", "[시나리오별]", "[서브카테고리 에너지]", "[프로브 첫 판 · 최근 7일]", "[다음 계획]", "[트레이너 목표 현황]", "[트레이너에게]", "[데이터]"):
            assert _sec in _rt, _sec
        assert _rt.startswith("에임 데스크 기록 · 2026-09-10 (목) · 발로 데이 · ") and "판 3/20" in _rt and "수면 7.5h" in _rt and "체감 6/10" in _rt and "죽음 에임 2" in _rt and "[판정]" in _rt, _rt[:400]
        assert "Pasu 900 신기록 (+94)" in _rt and "목표   850 · 오늘   900  ✓ 넘음 · 다음 제안 867" in _rt and "Ground" in _rt and "목표 3300 (300 남음)" in _rt, _rt
        assert "10:30  Pasu" in _rt and "09-11 금  발로 데이" in _rt and "09-12 토  벤치마크 18개" in _rt and "09-13 일  발로 데이" in _rt and "09-14 월  휴식" in _rt, _rt
        assert "09-15 화  발로 데이 · 트래킹 집중 (트레이너 지정)" in _rt, _rt
        _js = json.loads(_rt.split("[데이터]")[1].splitlines()[1]); assert _js["targets"] == {"ground": 3300, "pasu": 850} and _js["today_best"]["pasu"] == 900 and _js["plan"] == 20
        assert "(오늘 판 없음)" in daily_report({"pb": {}, "days": {}}, "2026-09-14") and "휴식" in daily_report({"pb": {}, "days": {}}, "2026-09-14")
        with _tf.TemporaryDirectory() as _td2:
            _pth = save_report(_rd, "2026-09-10", dir_=_td2)
            assert _pth == Path(_td2) / "에임데스크_2026-09-10.txt" and _pth.read_bytes()[:3] == b"\xef\xbb\xbf" and "[요약]" in _pth.read_text(encoding="utf-8-sig")
            assert report_path("2026-09-10", _td2) == _pth and not _pth.with_name(_pth.name + ".tmp").exists()
        trainer_clear(_td); assert TRAINER == {"targets": {}, "themes": {}, "note": "", "challenge": None, "set_on": None}
        assert main_theme("2026-09-15", SAMPLE)[0] == "clk"                                     # 지정이 지워지면 다시 주기대로 (9/15 = 주기 1번)
        # v4.0 판정 엔진 — 합성 기록(그날 계획대로 SAMPLE×배율, 판마다 ±0.4% 번갈아)
        def _syn(days_fac, start="2026-09-15"):                 # 화요일부터 (월요일은 쉬는 날)
            dd = {"pb": dict(SAMPLE), "days": {SAMPLE_DATE: dict(blank_day(), best=dict(SAMPLE))}}; d0 = date.fromisoformat(start)
            for off, fac in sorted(days_fac.items()):
                dk = (d0 + timedelta(days=off)).isoformat()
                if day_type_of(dk) == "r": continue
                seq = [k for k, n in plan_items(dk, SAMPLE) for _ in range(n)]
                if isinstance(fac, tuple): fac, cut = fac; seq = seq[:cut]
                apply_scan(dd, [(k, f"10.{i // 60:02d}.{i % 60:02d}", int(round(SAMPLE[k] * fac * (1 + (0.004 if i % 2 else -0.004))))) for i, k in enumerate(seq)], dk)
            bump_ver(); return dd
        assert verdict_state(0.7, True, False, "up") == "up" and verdict_state(0.7, True, False, "flat") == "flat" and verdict_state(-0.9, False, True) == "down" and verdict_state(0.9, False, False) == "flat"
        assert _median([3, 1, 2]) == 2 and _median([1, 2, 3, 4]) == 2.5 and _median([]) is None and _wa("어제") == "와" and _wa("토요일") == "과"
        _mk = mann_kendall([(i, i * 1.0) for i in range(10)]); assert _mk[0] > 2.3 and _mk[1] == 45 and mann_kendall([(i, 5.0) for i in range(10)]) == (0.0, 0)
        assert theil_sen([(0, 0), (1, 2), (2, 4)]) == 2.0 and theil_sen([(0, 1)]) == 0.0
        _e = _syn({0: 1.0, 1: 1.0}); _v = verdict_day(_e, "2026-09-16")
        assert _v["state"] == "flat" and _v["conf"] == "solid" and _v["n"] == 6 and _v["word"] == "어제와 비슷" and _v["glyph"] == "▬" and _v["fill"] == "solid", _v
        _e = _syn({0: 1.0, 1: 1.08}); _v = verdict_day(_e, "2026-09-16"); assert _v["state"] == "up" and _v["word"] == "어제보다 좋음" and _v["num"].startswith("+") and _v["colk"] == "up", _v
        _e = _syn({0: 1.0, 1: 0.92}); _v = verdict_day(_e, "2026-09-16"); assert _v["state"] == "down" and _v["word"] == "어제보다 별로" and _v["glyph"] == "▼", _v
        _e = _syn({0: 1.0, 1: (1.0, 6)}); _v = verdict_day(_e, "2026-09-16"); assert _v["conf"] == "prov" and _v["n"] == 4 and _v["fill"] == "hollow" and "잠정" in _v["cap"], _v
        _e = _syn({0: 1.0, 1: (1.0, 5)}); _v = verdict_day(_e, "2026-09-16"); assert _v["state"] == "wait" and _v["word"] == "측정 중" and _v["num"] == "3/4쌍", _v
        _e = _syn({0: 1.0}); _v = verdict_day(_e, "2026-09-15"); assert _v["state"] == "none" and _v["word"] == "오늘이 기준선" and _v["colk"] == "gold", _v
        _e = _syn({-3: 1.0, 0: 1.0}); _v = verdict_day(_e, "2026-09-15"); assert _v["word"] == "토요일과 비슷" and "(벤치)" in _v["cap"] and _v["prev"] == "2026-09-12", _v
        _e = _syn({0: 1.0, 1: (1.0, 12)}); _v = verdict_day(_e, "2026-09-16"); assert _v["state"] == "flat" and "어제 12판" in _v["cap2"], _v
        _v = verdict_day(_syn({}), "2026-09-14"); assert _v["state"] == "rest" and _v["word"] == "휴식일"
        _e = _syn({i: 1.0 for i in range(12)}); _e["days"].update(_syn({0: 1.0}, "2026-10-06")["days"]); bump_ver()
        _v = verdict_day(_e, "2026-10-06"); assert _v["state"] == "flat" and "비교할 어제 없음 · 평소 기준" in _v["cap"], _v   # 열흘 쉬고 돌아온 날은 '첫 훈련일'이 아니다 → 평소 기준
        _e["days"].update(_syn({0: 1.0}, "2026-10-20")["days"]); bump_ver()
        _v = verdict_day(_e, "2026-10-20"); assert _v["state"] == "wait" and "비교할 어제 없음" in _v["cap"], _v            # 3주 넘게 쉬면 평소 범위도 없다 → 측정 중
        _v = verdict_day(_syn({0: 1.0, 7: 1.0}), "2026-09-22"); assert _v["word"] == "지난 화요일과 비슷" and _iga("화요일") == "이" and _iga("월요일") == "이" and _iga("어제") == "가", _v
        _e = _syn({0: 1.0, 1: (1.0, 10)}); _v = verdict_day(_e, "2026-09-16"); assert _v["n"] == 6 and "어제 10판" in _v["cap2"], _v   # 같은 지점 = 웜업 뺀 판 수
        _v = verdict_day(_syn({-2: (1.0, 0)}) if False else _syn({0: 1.0}), "2026-09-19"); assert _v["state"] == "wait" and _v["word"] == "벤치마크 시작 전" and _v["num"] == "0/18", _v
        _dv = day_value(_syn({0: 1.0}), "2026-09-15"); assert "frog" in _dv and "float" in _dv and "ground" not in _dv, sorted(_dv)   # 클리킹 정확 날: 본훈련의 frog/float 블록은 남고 웜업 1판만 빠진다
        _e = _syn({-3: 1.0}); _v = verdict_day(_e, "2026-09-12"); assert _v["state"] in ("flat", "up", "down") and _v["word"].startswith("확정") and _v["colk"] == "rank", _v   # 벤치 18/18
        _e = _syn({-3: (1.0, 5)}); _v = verdict_day(_e, "2026-09-12"); assert _v["state"] == "bench" and _v["word"].startswith("예상") and _v["fill"] == "hollow", _v
        _ps = probe_level_series({"days": {SAMPLE_DATE: dict(blank_day(), best=dict(SAMPLE)), "2026-09-15": dict(blank_day(), first={k: SAMPLE[k] * 2 for k in PROBE}), "2026-09-16": dict(blank_day(), first={k: SAMPLE[k] for k in PROBE[:3]})}})
        assert len(_ps) == 1 and _ps[0]["lvl"] == 100.0 and _ps[0]["date"] == "2026-09-15" and _ps[0]["n"] == 6, _ps   # 2배 = +100% (옛 ±30 클램프였다면 30 에서 잘렸다)
        # 이상치는 클램프가 아니라 중앙값이 막는다: 6개 중 하나가 말도 안 되게 크거나 작아도 레벨선은 거의 안 움직인다
        _pn = {k: SAMPLE[k] for k in PROBE}
        bump_ver()
        _l0 = probe_level_series({"days": {"2026-09-15": dict(blank_day(), first=dict(_pn))}})[0]["lvl"]
        bump_ver(); _pn[PROBE[0]] = SAMPLE[PROBE[0]] * 9
        _l1 = probe_level_series({"days": {"2026-09-15": dict(blank_day(), first=dict(_pn))}})[0]["lvl"]
        assert _l0 == 0.0 and abs(_l1) < 1e-9, (_l0, _l1)
        bump_ver(); _pn[PROBE[0]] = SAMPLE[PROBE[0]] * 30                  # 클램프는 완전히 망가진 값만 막는다
        assert probe_level_series({"days": {"2026-09-15": dict(blank_day(), first=dict(_pn))}})[0]["lvl"] == 0.0
        bump_ver()
        # 기준 측정 전에는 레벨선 자체가 없다 → 성장·요즘이 판정을 꾸며내지 않는다
        _fresh()
        assert probe_level_series({"days": {"2026-09-15": dict(blank_day(), first=dict(_pn))}}) == []
        _measured(); bump_ver()
        _g = verdict_growth(_syn({i: 1.0 for i in range(9)}), "2026-09-22"); assert _g["state"] == "hold" and _g["word"].startswith("판정까지") and "에너지" in _g["cap2"], _g
        _g = verdict_growth(_syn({i: 1 + 0.01 * i for i in range(30)}), "2026-10-13"); assert _g["state"] == "up" and _g["word"] == "꾸준히 오르는 중" and _g["glyph"] == "↗" and float(_g["num"].rstrip("%")) > 15, _g
        _g = verdict_growth(_syn({i: 1.0 for i in range(30)}), "2026-10-13"); assert _g["state"] == "flat" and _g["word"] == "큰 변화 없음", _g
        _r = verdict_recent(_syn({i: 1.0 for i in range(8)}), "2026-09-22"); assert _r["state"] == "hold" and _r["word"].startswith("판정까지"), _r
        _r = verdict_recent(_syn({i: (0.95 if i >= 24 else 1.0) for i in range(30)}), "2026-10-13");   # 10/9 금 · 10/10 토 · 10/11 일 · 10/13 화 = 최근 5일 중 4일 (10/12 월은 쉼) assert _r["state"] == "down" and _r["word"] == "요즘 부진" and float(_r["num"].rstrip("%")) < -3, _r
        _r = verdict_recent(_syn({i: (0.90 if i == 28 else 1.0) for i in range(30)}), "2026-10-13"); assert _r["state"] == "flat" and _r["word"] == "요즘 평소 흐름", _r
        _r = verdict_recent(_syn({i: (1.05 if i >= 24 else 1.0) for i in range(30)}), "2026-10-13"); assert _r["state"] == "up" and _r["word"] == "요즘 상승세", _r
        _e = _syn({0: 1.0, 1: 1.0}); _vv = verdicts(_e, "2026-09-16"); assert _vv is verdicts(_e, "2026-09-16") and set(_vv) == {"day", "grow", "recent"}
        assert fmt_verdict_line("오늘", _vv["day"]).startswith("오늘 · 어제와 비슷 ▬ ") and "verdict" in session_card(_e, "2026-09-15", "발로 데이")
        assert "[판정]" in daily_report(_e, "2026-09-16") and "오늘 · 어제와 비슷" in daily_report(_e, "2026-09-16")
        # v4.2 훈련일 경계(새벽 5시) — 자정을 넘긴 세션이 한 날로 모인다
        assert DAY_CUTOFF_H[0] == 5
        assert t_key("23.50.00") < t_key("00.10.00") and t_key("04.59.59") < t_key("05.00.00") + 24 * 3600
        assert t_min("19.43.00") == 1183 and t_min("00.30.00") == 24 * 60 + 30 and t_min("05.00.00") == 300
        assert t_key("bad") == 0 and _hh("23.50.00") == 23 and _hh("") == 0
        _sp = session_summary([("pasu", "23.50.00", 800), ("w4", "00.20.00", 900)], {})
        assert _sp["start"] == "23.50.00" and _sp["end"] == "00.20.00" and _sp["minutes"] == 30, _sp   # 자정 넘겨도 30분
        assert [p[1] for p in merge_plays([], [("a", "00.10.00", 1), ("b", "23.50.00", 2)])] == ["23.50.00", "00.10.00"]
        DAY_CUTOFF_H[0] = 0; assert t_key("00.10.00") < t_key("23.50.00"); DAY_CUTOFF_H[0] = 5      # 자정 설정이면 옛 동작
        with _tf.TemporaryDirectory() as _td3:
            _st3 = Path(_td3); _mk = lambda nm, d_, t_, sc: (_st3 / f"{nm} - Challenge - {d_}-{t_} Stats.csv").write_text(f"Score:,{sc}\n")
            _mk("VT Pasu Novice S5", "2026.09.15", "23.50.00", 800)      # 15일 훈련일
            _mk("VT 1w4ts Novice S5", "2026.09.16", "00.20.00", 900)     # 자정 넘김 → 아직 15일 훈련일
            _mk("VT Popcorn Novice S5", "2026.09.16", "10.00.00", 700)   # 16일 훈련일
            _SCAN_STATE["sig"] = None; _SCORE_CACHE.clear()
            _r15 = sorted(scan_day(_st3, date(2026, 9, 15)), key=lambda x: t_key(x[1]))
            _SCAN_STATE["sig"] = None
            _r16 = scan_day(_st3, date(2026, 9, 16))
            assert [k for k, _t, _s in _r15] == ["pasu", "w4"], _r15      # 자정 넘긴 판이 전날에 붙는다
            assert [k for k, _t, _s in _r16] == ["popcorn"], _r16
        # 계획 밖 판
        _op = {"pb": dict(SAMPLE), "days": {"2026-09-16": dict(blank_day(), plays=[["ww5", "00.10.00", 1200], ["dot", "00.12.00", 900]])}}
        _n_off, _k_off = off_plan_plays(_op, "2026-09-16", pb=SAMPLE)      # 9/16 수 = 스위칭 집중 (ww5t 없음)
        assert (_n_off, _k_off) == (1, ["ww5"]) and "계획 밖 1판" in fmt_off_plan(_n_off, _k_off) and fmt_off_plan(0, []) == ""
        assert off_plan_plays({"pb": {}, "days": {}}, "2026-09-14")[0] == 0        # 휴식일(월)은 계획이 없다
        # 자정에 쪼개진 기록 합치기 — 사용자 사례(워밍업 4판은 전날, 나머지 23판은 자정 뒤)
        _seq = [k for k, n in dict(playlists_for("2026-09-15", SAMPLE))["AIMDESK Day"] for _ in range(n)]
        _mg = {"pb": dict(SAMPLE), "days": {
            "2026-09-15": dict(blank_day(), plays=[[k, f"23.5{i}.00", 900] for i, k in enumerate(_seq[:4])]),
            "2026-09-16": dict(blank_day(), plays=[[k, f"00.{i:02d}.00", 900] for i, k in enumerate(_seq[4:])])}}
        for _d in _mg["days"].values(): _reagg(_d)
        assert len(_mg["days"]["2026-09-15"]["plays"]) == 4 and len(_mg["days"]["2026-09-16"]["plays"]) == 16
        assert migrate_cutoff(_mg) == 16 and _mg["cutoff_migrated"] is True
        assert "2026-09-16" not in _mg["days"] and len(_mg["days"]["2026-09-15"]["plays"]) == 20, sorted(_mg["days"])
        _d15 = _mg["days"]["2026-09-15"]; bump_ver()
        assert _d15["count"]["w4"] == 4 and _d15["first"]["pasu"] is not None and _d15["sess"] == {"start": "23.50.00", "end": "00.15.00"}   # w4 = 프로브 1 + 본훈련 3
        assert migrate_cutoff(_mg) == 0                                            # 두 번 돌지 않는다
        assert migrate_cutoff({"days": {}, "cutoff_migrated": False}) == 0
        _keep = {"days": {"2026-09-16": dict(blank_day(), plays=[["pasu", "10.00.00", 800]], count={"pasu": 1})}}
        assert migrate_cutoff(_keep) == 0 and "2026-09-16" in _keep["days"]          # 경계 이후 판만 있으면 그대로
        # ── v5.0: 출발선을 직접 잰다 · 판정까지 N일이 진짜 N일 ──
        _fresh()
        assert day_type_of("2026-09-16") == "b" and bench_label("2026-09-16") == "기준 측정"   # 측정 전이면 무슨 요일이든 기준 측정일
        assert plan_count("2026-09-16") == 18 and probe_level_series({"days": {}}) == []
        _b0 = {"pb": {}, "days": {}}
        _bp = [k for k, n_ in plan_items("2026-09-16") for _ in range(n_)]
        apply_scan(_b0, [(k, f"20.{i // 60:02d}.{i % 60:02d}", int(SAMPLE[k] * 0.62)) for i, k in enumerate(_bp)], "2026-09-16")
        assert BASE_DATE[0] == "2026-09-16" and base_ok(BASELINE[0]) and len(_b0["pb"]) == 18
        assert day_type_of("2026-09-17") == "v" and day_type_of("2026-09-16") == "b"           # 다음 날부터 주기 복귀
        assert probe_level_series(_b0)[0]["lvl"] == 0.0                                        # 출발선은 정확히 0
        assert totalE(_b0["pb"])[0] == totalE({k: int(SAMPLE[k] * 0.62) for k in SAMPLE})[0]   # 실제로 친 점수만 에너지가 된다
        # 예고한 날짜에 실제로 판정이 선다 (옛 계산은 조건 하나만 봐서 거꾸로 가거나 멈췄다)
        def _grow_days(nd, start=date(2026, 9, 16)):
            dd = {"pb": {}, "days": {}}; cur = start; made = 0
            while made < nd:
                if DAYTYPES[cur.weekday()] != "r":
                    dd["days"][cur.isoformat()] = dict(blank_day(), first={k: int(SAMPLE[k] * (0.7 + 0.004 * made)) for k in PROBE})
                    made += 1
                cur += timedelta(days=1)
            bump_ver(); return dd, (cur - timedelta(days=1)).isoformat()
        BASELINE[0] = {k: int(SAMPLE[k] * 0.7) for k in PROBE}; BASE_DATE[0] = "2026-09-16"
        for _nd, _eg, _er in ((1, 21, 11), (5, 17, 7), (10, 11, 1), (18, 1, None)):     # 훈련일 = 화~금·토·일 (월만 쉼) 기준 달력일
            _dd, _ld = _grow_days(_nd)
            _g, _r2 = verdict_growth(_dd, _ld), verdict_recent(_dd, _ld)
            assert _g["word"] == f"판정까지 {_eg}일", (_nd, _g["word"])
            if _er is None: assert _r2["state"] != "hold", (_nd, _r2["word"])
            else: assert _r2["word"] == f"판정까지 {_er}일", (_nd, _r2["word"])
        # 예고한 만큼 더 치면 그날 정말로 선다
        _dd, _ld = _grow_days(10); _cur = date.fromisoformat(_ld); _made = 0
        while _made < 9:                                   # 11 달력일 = 훈련일 9
            _cur += timedelta(days=1)
            if DAYTYPES[_cur.weekday()] == "r": continue
            _dd["days"][_cur.isoformat()] = dict(blank_day(), first={k: int(SAMPLE[k] * (0.7 + 0.004 * (10 + _made))) for k in PROBE}); _made += 1
        bump_ver()
        assert (_cur - date.fromisoformat(_ld)).days == 11 and verdict_growth(_dd, _cur.isoformat())["state"] != "hold"
        # 휴식일에 실제로 쳤으면 '훈련 안 함' 이라고 하지 않는다
        _sun = "2026-09-21"                                                        # 월요일 = 쉬는 날
        assert day_type_of(_sun) == "r" and day_type_of("2026-09-20") == "v"
        _rd = {"pb": {}, "days": {_sun: dict(blank_day(), plays=[[k, "20.00.00", SAMPLE[k]] for k in PROBE], first={k: SAMPLE[k] for k in PROBE})}}
        bump_ver(); assert verdict_day(_rd, _sun)["word"] != "휴식일"
        assert verdict_day({"pb": {}, "days": {}}, _sun)["word"] == "휴식일"
        # 기록 합치기: 어느 쪽도 잃지 않는다
        _m1 = {"pb": {"pasu": 700}, "days": {"2026-09-16": dict(blank_day(), plays=[["pasu", "10.00.00", 700]], count={"pasu": 1}, best={"pasu": 700}, first={"pasu": 700})}}
        _m2 = {"pb": {"pasu": 810, "dot": 900}, "days": {"2026-09-16": dict(blank_day(), plays=[["pasu", "11.00.00", 810]], count={"pasu": 1}, best={"pasu": 810}, first={"pasu": 810}),
                                                         "2026-09-17": dict(blank_day(), plays=[["dot", "10.00.00", 900]], count={"dot": 1}, best={"dot": 900}, first={"dot": 900})}}
        merge_data(_m1, _m2)
        assert sorted(_m1["days"]) == ["2026-09-16", "2026-09-17"] and len(_m1["days"]["2026-09-16"]["plays"]) == 2
        assert _m1["pb"] == {"pasu": 810, "dot": 900} and _m1["days"]["2026-09-16"]["best"]["pasu"] == 810
        assert _m1["days"]["2026-09-16"]["first"]["pasu"] == 700                              # 첫 판은 시간순으로 다시 계산
        # 옛 파일의 주입된 가짜 PB 걷어내기 — 근거 있는 PB 는 남긴다
        _dp = {"pb": dict(SAMPLE, pasu=900), "days": {"2026-09-16": dict(blank_day(), best={"pasu": 900, "dot": 500})}}
        assert drop_synthetic_pb(_dp) == 17 and _dp["pb"] == {"pasu": 900, "dot": 500}
        # 순서가 중요하다: 가짜 날을 먼저 지워야 '근거 없는 PB' 판정이 성립한다.
        # 거꾸로 하면 그 날이 근거 노릇을 해서 하나도 안 걷히고 마이그레이션이 통째로 무효가 된다
        _lg = {"seeded": True, "pb": dict(SAMPLE), "days": {
            SAMPLE_DATE: dict(blank_day(), best=dict(SAMPLE)),
            "2026-09-15": dict(blank_day(), first={"pasu": 500}, best={"pasu": 520}, count={"pasu": 2})}}
        assert desynth_legacy(_lg) == 18 and _lg["pb"] == {"pasu": 520} and SAMPLE_DATE not in _lg["days"]
        assert _lg["days"]["2026-09-15"]["best"] == {"pasu": 520} and "seeded" not in _lg   # 실제 기록은 그대로
        assert desynth_legacy(_lg) == 0                                    # 두 번 돌지 않는다
        # 합치기로도 되살아나면 안 된다
        _c1 = {"pb": {"pasu": 600}, "days": {"2026-09-16": dict(blank_day(), best={"pasu": 600}, first={"pasu": 600}, count={"pasu": 1})}}
        _s1 = {"seeded": True, "pb": dict(SAMPLE), "days": {SAMPLE_DATE: dict(blank_day(), best=dict(SAMPLE))}}
        desynth_legacy(_s1); merge_data(_c1, _s1)
        assert _c1["pb"] == {"pasu": 600} and SAMPLE_DATE not in _c1["days"], _c1["pb"]
        # 기준 측정 전 에너지 줄 — 뺄셈에서 죽지 않는다 (기록 탭 성장 구역이 통째로 안 그려졌다)
        _fresh()
        assert energy_delta({"pb": {}}) == (None, None) and _energy_line({"pb": {}}) == "기준 측정 전"
        assert _energy_line({"pb": dict(SAMPLE)}) == "에너지 339 Silver"
        _measured()
        # 벤치 풀런 판정: '전체 순회' 날은 9/9 를 덮어도 풀런이 아니다
        _mixk = {k: 500 for k, _n in next(t[3] for t in MAIN_THEMES if t[0] == "mix")}
        assert totalE(_mixk)[1] == 9                                        # 하위분류는 9개를 다 덮는다
        _bd = {"days": {"2026-09-18": dict(blank_day(), best=_mixk),        # 금 전체 순회
                        "2026-09-19": dict(blank_day(), best={k: 500 for k in tier_keys("n")})}}   # 토 벤치 18종
        assert [k for k, _e in bench_days(_bd)] == ["2026-09-19"], bench_days(_bd)
        # stats 폴더 안내는 실제로 폴더 선택이 있는 탭을 가리켜야 한다
        assert "도구 탭" in status_line({}, False, False, None, False)[0]
        # ── v6.0: 볼테익 3단계 — 같은 이름이라도 단계가 다르면 다른 키·다른 척도 ──
        assert len(SCEN) == 54 and len(tier_keys("n")) == len(tier_keys("i")) == len(tier_keys("a")) == 18
        assert NAME2KEY["VT 1w3ts Intermediate S5"] == "i.w4" and NAME2KEY["VT 1w2ts Advanced S5"] == "a.w4" and NAME2KEY["VT 1w4ts Novice S5"] == "w4"
        assert tier_of("i.pasu") == "i" and base_of("i.pasu") == "pasu" and tier_of("pasu") == "n" and tk("pasu", "i") == "i.pasu" and tk("pasu", "n") == "pasu"
        assert th_of("i.pasu") == [770, 850, 930, 980] and sub_of("a.cts")[0] == "stab"
        # 에너지 오프셋: 인터 플래티넘 임계값 = 정확히 500, 마스터 = 800. 노비스 골드 = 400 그대로
        assert E_of("i.pasu", 770) == 500 and E_of("i.pasu", 980) == 800 and E_of("pasu", 800) == 400 and E_of("a.pasu", 910) == 900
        assert E_of("i.pasu", 700) < 500 and E_of("i.pasu", 700) >= 400          # 인터에서 플래 미만 = 골드 구간
        _ib = {tk(b, "i"): th_of(tk(b, "i"))[0] for b in PROBE_BASE + ["ww5", "frog", "float", "pgt", "snake", "aether", "ground", "raw", "csphere", "fly", "penta"]}
        assert tier_of_scores(_ib) == "i" and totalE(_ib) == (500, 9)               # 인터 벤치 전부 플래 임계값 = 500 플래티넘
        assert rank_of(500)[0] == "Platinum" and rank_of(800)[0] == "Master" and rank_of(1200)[0] == "Celestial" and rank_of(399)[0] == "Silver"
        assert next_rank_gap(800, th_of("i.pasu"), "i.pasu") == ("Diamond", 850, 50) and next_rank_gap(800, th_of("pasu"))[0] is None
        _wl = weakest_link(dict(_ib, **{"i.pasu": 700})); assert _wl and _wl["total_next"][0] == "Diamond", _wl["total_next"]
        # set_tier 가 루틴 상수를 그 단계 키로 푼다 · 원래대로 돌아온다
        set_tier("i"); assert PROBE[0] == "i.w4" and WARMUP[0][0] == "i.ground" and "i.ground" in WARM_KEYS and SUBS[0][3][0][0] == "i.pasu"
        assert scen_lookup("floating") == "i.float" and scen_lookup("pasu novice") == "pasu"   # 단계를 안 적으면 지금 단계, 적으면 그 단계
        assert sum(n for _, n in main_theme("2026-09-17")[3]) == MAIN_PLAYS and all(tier_of(k) == "i" for k, _ in main_theme("2026-09-17")[3])
        set_tier("n"); assert PROBE[0] == "w4" and scen_lookup("floating") == "float" and SUBS[0][3][0][0] == "pasu"
        # 졸업 조건 = 현재 단계 풀런에서 9갈래 전부 최상위. 졸업하면 출발선을 보관하고 다음 단계의 기준 측정으로
        _gd = {"tier": "n", "pb": {}, "days": {"2026-09-19": dict(blank_day(), best={k: th_of(k)[3] for k in tier_keys("n")})}, "base": {"date": "2026-09-16", "scores": dict(SAMPLE)}}
        BASE_DATE[0], BASELINE[0] = "2026-09-16", dict(SAMPLE); bump_ver()
        assert tier_ready(_gd) == (True, 0, "2026-09-19")
        _gd["days"]["2026-09-19"]["best"].update(fly=534, drift=429); bump_ver(); assert tier_ready(_gd)[:2] == (False, 1)   # 이배시브 갈래(둘 중 높은 쪽)가 골드 미달
        assert graduate(_gd) == "i" and CUR_TIER[0] == "i" and _gd["tier"] == "i" and "base" not in _gd and _gd["base_hist"][0]["tier"] == "n"
        assert BASE_DATE[0] is None and day_type_of("2026-09-21") == "b" and bench_label("2026-09-21") == "기준 측정"   # 다음 날 = 인터 기준 측정일
        assert plan_items("2026-09-21") == [(k, 1) for k in tier_keys("i")]
        set_tier("n"); _measured()
        # ── v6.0: DAY N · 녹화 오프셋 · 명장면 · 챕터 ──
        _ed = {"pb": {}, "days": {}, "series": {"ep_offset": 0}}
        for _dk in ("2026-09-16", "2026-09-17", "2026-09-18"):
            _ed["days"][_dk] = dict(blank_day(), plays=[["pasu", "20.01.00", 700]], count={"pasu": 1}, first={"pasu": 700}, best={"pasu": 700})
        _ed["days"]["2026-09-19"] = blank_day()
        assert [episode_no(_ed, k) for k in ("2026-09-16", "2026-09-17", "2026-09-18", "2026-09-19", "2026-09-21")] == [1, 2, 3, 4, 4]   # 휴식·안 친 날은 번호를 안 먹는다
        _ed["days"]["2026-09-17"]["ep"] = 7; assert episode_no(_ed, "2026-09-17") == 7            # 얼린 번호가 이긴다
        _ed["series"]["ep_offset"] = 10; assert episode_no(_ed, "2026-09-21") == 14
        _ek = "2026-09-22"; _ep = [("ground", "20.15.05", 3000), ("float", "20.16.05", 600), ("w4", "20.17.10", 1100), ("pasu", "20.18.20", 850),
                                   ("popcorn", "20.19.30", 700), ("eddie", "20.20.40", 800), ("drift", "20.21.50", 400), ("cts", "20.23.00", 430),
                                   ("w4", "20.24.10", 1150), ("ww5", "20.25.20", 1300), ("float", "20.26.30", 640)]
        _ed["days"][_ek] = dict(blank_day(), rec={"start": "20.14.05", "src": "manual"}); bump_ver()
        apply_scan(_ed, _ep, _ek); bump_ver()
        assert _ed["days"][_ek]["ep"] == 14                                                        # 첫 판이 들어오면 번호가 얼린다
        assert [fmt_mmss(o[0]) for o in play_offsets(_ed["days"][_ek], _ep)[:3]] == ["00:00", "01:00", "02:05"]   # 판 시작 = 끝 − 60초
        _hl = highlights(_ed, _ek, _ep)
        assert sum(1 for h in _hl if h["kind"] == "pb") == 3 and any("+150" in h["text"] for h in _hl), [h["text"] for h in _hl]   # PB 는 기록 이력 기준
        assert "마지막 판" in _hl[-1]["text"] and _hl[-1]["out"] - _hl[-1]["off"] == 78 and all(_hl[i]["off"] <= _hl[i + 1]["off"] for i in range(len(_hl) - 1))
        _ch = chapters(_ed, _ek, _ep)
        assert _ch[0][0] == 0 and "워밍업" in _ch[0][1] and len(_ch) == 4 and all(_ch[i + 1][0] - _ch[i][0] >= 10 for i in range(3)), _ch
        _ed["days"][_ek].pop("rec"); bump_ver()
        assert rec_start(_ed["days"][_ek]) == ("20.14.05", "first_play")                          # 표시 없으면 첫 판 시작 = 0:00
        assert fmt_mmss(play_offsets(dict(blank_day(), rec={"start": "23.50.00"}), [("pasu", "00.05.00", 800)])[0][0]) == "14:00"   # 자정 넘김
        # ── v6.0: 발로란트 API 파서 — 문서의 필드 경로 그대로, 깨진 항목은 건너뛴다 ──
        assert riot_id("YouKnowJo#YK1") == ("YouKnowJo", "YK1") and riot_id("nohash") is None and riot_id(" a # b ") == ("a", "b")
        _fm = {"data": {"current": {"tier": {"id": 12, "name": "Gold 2"}, "rr": 37, "elo": 1137, "last_change": 18}, "peak": {"tier": {"name": "Gold 3"}}}}
        assert parse_mmr(_fm) == {"tier": "Gold 2", "rr": 37, "elo": 1137, "last": 18, "peak": "Gold 3"} and parse_mmr({}) is None
        _fx = {"data": [
            {"meta": {"id": "m1", "started_at": "2026-09-16T12:00:00Z", "map": {"name": "Ascent"}, "mode": "Competitive"},
             "stats": {"team": "Red", "kills": 20, "deaths": 15, "assists": 4, "score": 4800, "shots": {"head": 30, "body": 60, "leg": 10}}, "teams": {"red": 13, "blue": 9}},
            {"meta": {"id": "m2", "started_at": "2026-09-15T12:00:00Z", "map": {"name": "Bind"}, "mode": "Competitive"},
             "stats": {"team": "Blue", "kills": 12, "deaths": 18, "assists": 2, "score": 3400, "shots": {"head": 10, "body": 70, "leg": 20}}, "teams": {"red": 13, "blue": 7}},
            {"meta": {}, "stats": None}]}
        _ms = parse_matches(_fx)
        assert len(_ms) == 2 and _ms[0]["won"] is True and _ms[1]["won"] is False and abs(_ms[0]["hs"] - 30.0) < 1e-9
        _ws = week_stats(_ms); assert _ws["n"] == 2 and _ws["win"] == 50.0 and abs(_ws["hs"] - 20.0) < 1e-9 and abs(_ws["kd"] - 32 / 33) < 1e-9, _ws
        assert val_get("/x", "")[1] == "API 키 없음" and val_sync({"valo_cfg": {}})[0] is False
        # ── v6.0: 업로드 팩 · 특별편 ──
        assert ko_tier("Gold 2") == "골드 2" and val_rank_ord("Gold 2") == 32 and val_rank_ord("Immortal 1") == 71 and val_rank_ord("Platinum 3") > val_rank_ord("Gold 3")
        bump_ver(); _up = upload_pack(_ed, _ek, _ep)
        for _sec in ("[제목 후보]", "[설명]", "[명장면]", "[챕터]", "[태그]", "[고정 댓글]"): assert _sec in _up, _sec
        _tl = [l for l in _up.splitlines() if l[:2] in ("1.", "2.", "3.")]
        assert len(_tl) == 3 and all(len(l) <= 103 for l in _tl) and "DAY 14" in _tl[0], _tl
        assert ("★ 볼테익" in _tl[1]) or ("Pasu 850 신기록 (+150)" in _tl[1]), _tl[1]     # 특별편 > 신기록 순으로 고른다
        assert "★ Pasu 850 신기록 (+150)" in _up and "00:00 오늘의 루틴" in _up and "[명장면]" in _up
        _pp = save_upload_pack(_ed, _ek, _ep, dir_="/tmp/aimdesk_selftest_pack"); assert _pp.name == "EP014_2026-09-22_업로드.txt" and _pp.exists()
        _td = thumb_data(_ed, _ek, _ep); assert _td["day"] == "DAY 14" and _td["big"] and _td["word"] and _td["story"].startswith("DAY 14")
        _tp = save_thumb_page(_ed, _ek, _ep, dir_="/tmp/aimdesk_selftest_pack"); _th = _tp.read_text(encoding="utf-8")
        assert _tp.name == "EP014_2026-09-22_썸네일.html" and _th.count("<canvas") == 0 and _th.count('createElement("canvas")') == 1 and "DAY 14" in _th and "cdn" not in _th.lower()
        # 특별편: DAY 30 · 랭크업 · 강등
        _ms = {"pb": {}, "days": {}, "series": {"ep_offset": 28}}
        _ms["days"]["2026-09-22"] = dict(blank_day(), plays=[["pasu", "20.01.00", 700]], count={"pasu": 1}, first={"pasu": 700}, best={"pasu": 700}, rank={"tier": "Gold 2", "rr": 40})
        _ms["days"]["2026-09-23"] = dict(blank_day(), plays=[["pasu", "20.01.00", 700]], count={"pasu": 1}, first={"pasu": 700}, best={"pasu": 700}, rank={"tier": "Gold 3", "rr": 5})
        bump_ver(); _m = dict(milestones(_ms, "2026-09-23"))
        assert _m.get("DAY") == "★ DAY 30" and _m.get("VAL_UP") == "★ 랭크업 골드 2 → 골드 3", _m
        _ms["days"]["2026-09-24"] = dict(blank_day(), plays=[["pasu", "20.01.00", 700]], count={"pasu": 1}, first={"pasu": 700}, best={"pasu": 700}, rank={"tier": "Gold 2", "rr": 80})
        bump_ver(); assert dict(milestones(_ms, "2026-09-24")).get("VAL_DOWN") == "강등 골드 3 → 골드 2"
        # ── v6.0: 관문 미터 · 주인공 줄 ──
        _g = gate_status(dict(SAMPLE)); assert _g["n"] == 2 and _g["total"] == 9 and len(_g["left"]) == 7, (_g["n"], _g["left"])   # 예시 점수: 다이내믹·리액티브만 골드
        assert _g["left"][0][:2] == ("이배시브", "fly") and _g["left"][0][3] == 13 and [x[3] for x in _g["left"]] == sorted(x[3] for x in _g["left"])   # 모자란 점수 순
        _gw, _gn, _gc = fmt_gate(_g); assert _gw == "노비스 졸업 2/9" and _gn == "남은 7" and _gc.startswith("FlyTS +13 · Floating Heads +27 · ControlTS +28…"), (_gw, _gn, _gc)
        _g9 = gate_status({k: th_of(k)[3] for k in tier_keys("n")}); assert _g9["n"] == 9 and fmt_gate(_g9)[0] == "노비스 졸업 ✓" and "인터미디어트" in fmt_gate(_g9)[2]
        assert gate_status({})["n"] == 0 and all(x[3] is None for x in gate_status({})["left"])       # 한 판도 없으면 남은 9, 부족분은 모름
        _fresh(); assert story_line({"days": {}}, "2026-09-16") == "DAY 0 · 기준 측정"; _measured()
        _sl = {"pb": {}, "series": {"ep_offset": 0}, "days": {}}
        for _i, _dk in enumerate(("2026-09-15", "2026-09-16", "2026-09-17")):
            _sl["days"][_dk] = dict(blank_day(), plays=[["pasu", "20.01.00", 700]], count={"pasu": 1}, first={"pasu": 700}, best={"pasu": 700}, rank={"tier": "Gold 2", "rr": [12, -8, 20][_i]})
        BASE_DATE[0] = "2026-09-15"; bump_ver()
        assert story_line(_sl, "2026-09-17") == "DAY 3 · 골드 2 → 불멸 · 연속 3일" and rr_net(_sl, "2026-09-17") == 24, story_line(_sl, "2026-09-17")
        _sl["days"]["2026-09-17"]["rank"]["tier"] = ""; bump_ver(); assert story_line(_sl, "2026-09-17").startswith("DAY 3 · 골드 2 → 불멸")   # 마지막으로 적은 티어를 쓴다
        # ── v6.0: 성장·요즘 히스테리시스 · 기준 측정일 요약 ──
        assert _sticky("flat", "up", False) == "up" and _sticky("flat", "up", True) == "flat" and _sticky("up", None, False) == "up" and _sticky("down", "flat", False) == "flat"
        _hz = _syn({i: 1 + 0.01 * i for i in range(30)}); bump_ver()
        _gA = verdict_growth(_hz, "2026-10-13"); assert _gA["state"] == "up"
        _gB = verdict_growth(_hz, "2026-10-13", prev="up", npr=3); assert _gB["state"] == "up" and _gB["n"] <= _gA["n"]   # 프로브 덜 친 오늘 점은 안 센다
        _bl = {"pb": {k: th_of(k)[2] for k in tier_keys("n")}, "days": {}}; _bl["pb"].update(dot=700, eddie=700)   # 스피드 갈래만 실버 미만
        BASE_DATE[0] = "2026-09-16"; bump_ver()
        _bc = day_changes(_bl, "2026-09-16"); assert len(_bc) == 3 and _bc[0].startswith("출발선 확정 · 총 에너지") and "가장 약한 갈래 스위칭 Speed" in _bc[2], _bc
        # ── v6.0: 어제 플레이리스트 감지 ──
        _sp = {"pb": dict(SAMPLE), "days": {}}
        _pair = None                                                                          # 본훈련이 다른 인접 훈련일 쌍을 찾는다
        for _i in range(15, 30):
            _y, _t = f"2026-09-{_i:02d}", f"2026-09-{_i + 1:02d}"
            if day_type_of(_y) != "v" or day_type_of(_t) != "v": continue
            _ys = {k for k, n_ in plan_items(_y, SAMPLE)}; _ts = {k for k, n_ in plan_items(_t, SAMPLE)}
            if _ys - _ts: _pair = (_y, _t, sorted(_ys - _ts)[0]); break
        assert _pair, "본훈련이 다른 인접 훈련일이 있어야 한다"
        _y, _t, _oy = _pair
        _tsq = [k for k, n_ in plan_items(_t, SAMPLE) for _ in range(n_)]
        _pl_ok = [(k, f"20.{i:02d}.00", 500) for i, k in enumerate(_tsq[:9])]
        _pl_bad = _pl_ok[:8] + [(_oy, "20.08.00", 500)]
        assert stale_playlist(_sp, _t, _pl_ok) == (0, "") and stale_playlist(_sp, _t, _pl_bad) == (1, main_theme(_y, SAMPLE)[1]), stale_playlist(_sp, _t, _pl_bad)
        assert stale_playlist(_sp, _t, []) == (0, "")
        _measured()
        # ── v6.0: 단계 사다리 · 주간 결산 ──
        assert norm_val_tier("골드 2") == "Gold 2" and norm_val_tier("골드2") == "Gold 2" and norm_val_tier("플래 1") == "Platinum 1" and norm_val_tier("gold 2") == "Gold 2" and norm_val_tier("불멸 1") == "Immortal 1" and norm_val_tier("어쩌구") is None and norm_val_tier("") is None
        assert val_rank_ord("골드 2") == 32 and val_rank_ord("Immortal 1") == 71 and val_rank_ord("Gold 2") == 32 and ko_tier("골드2") == "골드 2" and ko_tier("Platinum 3") == "플래티넘 3"
        assert iso_week_id("2026-09-20") == "2026-W38" and _week_after("2026-W38") == "2026-W39" and _week_after("2025-W52") == "2026-W01" and week_range("2026-09-17")[0] == "2026-09-14" and week_range("2026-09-17")[6] == "2026-09-20"
        assert tier_energy(SAMPLE, "n")[0] == totalE(SAMPLE)[0] and tier_energy({}, "i") == (None, 0)
        _hd = {"pb": {}, "days": {}}
        for _dk, _t in (("2026-10-01", "Gold 3"), ("2026-10-05", "Platinum 1"), ("2026-10-12", "플래 1"), ("2026-10-20", "Platinum 2")):
            _hd["days"][_dk] = dict(blank_day(), rank={"tier": _t, "rr": 0, "games": 1, "why": ""})
        bump_ver(); assert held_days(_hd, "2026-10-25", val_rank_ord("Platinum 1")) == 21 and held_days(_hd, "2026-10-03", val_rank_ord("Platinum 1")) == 0 and held_days(_hd, "2026-10-25", val_rank_ord("Diamond 1")) == 0
        _st = {"pb": dict(SAMPLE), "days": {}, "series": {"ep_offset": 0}}
        BASE_DATE[0] = "2026-09-14"; BASELINE[0] = dict(SAMPLE); bump_ver()
        _s0 = stage_status(_st, "2026-09-14"); assert _s0["idx"] == 0 and _s0["total"] == 4 and _s0["n_ok"] == 1 and fmt_stage_chip(_s0) == "단계 0 · 관문 1/4", [(g["label"], g["ok"]) for g in _s0["gates"]]
        _dks = [d for d in (date(2026, 9, 14) + timedelta(days=_j) for _j in range(20)) if DAYTYPES[d.weekday()] == "v" or d == date(2026, 9, 14)][:11]       # 기준 측정일(9/14 월) + 훈련 10일 (화~금·일)
        for _i, _d in enumerate(_dks):
            _st["days"][_d.isoformat()] = dict(blank_day(), plays=[["pasu", "20.01.00", 700]], count={"pasu": 1}, first={"pasu": 700}, best={"pasu": 700},
                                              val={"range": 22 + (_i % 3), "dm_k": 20, "dm_d": 18, "dm_hs": 24.0, "skip": False},
                                              rank={"tier": "골드 2", "rr": 10, "games": 2, "why": "aim" if _i % 2 else "pos"})
        assert _dks[-1].isoformat() == "2026-09-27"                                                                      # 11번째 = 9/27 일 (월요일 둘을 건너뜀)
        _st["days"]["2026-09-29"] = dict(blank_day(), plays=[["pasu", "20.01.00", 700]], count={"pasu": 1}, first={"pasu": 700}, best={"pasu": 700},   # W40 의 훈련 하루 (결산 검사용)
                                         val={"range": 23, "dm_k": 20, "dm_d": 18, "dm_hs": 24.0, "skip": False}, rank={"tier": "골드 2", "rr": 10, "games": 2, "why": "pos"})
        bump_ver(); _lk = "2026-09-29"
        _s0 = stage_status(_st, _lk); assert _s0["n_ok"] == 4 and _s0["total"] == 4 and _s0["by"]["game"] == (1, 1), [(g["label"], g["ok"], g["val"]) for g in _s0["gates"]]
        assert stage_lines(_st, _lk)[0].startswith("단계 0 · 출발선 — 재고 시작한다") and all(x.startswith("  ✓") for x in stage_lines(_st, _lk)[1:5])
        assert "[단계]" in daily_report(_st, _lk) and "관문 4/4" in daily_report(_st, _lk)
        _sc = session_card(_st, _lk, "발로 데이"); assert _sc["story"].startswith("DAY ") and _sc["gate"].startswith("노비스 졸업 2/9 · 남은 7"), _sc
        assert stage_check(_st, "2026-10-04") == (False, 0) and _st["stage"]["ok_weeks"] == ["2026-W40"]            # 한 주 잘된 걸로 올리지 않는다
        assert stage_check(_st, "2026-10-04") == (False, 0) and _st["stage"]["ok_weeks"] == ["2026-W40"]            # 같은 주 두 번 불러도 한 번
        for _i in range(5, 10):                                                                                          # 둘째 주도 랭크 카드·발로 블록을 계속 적어야 관문이 열려 있다
            _st["days"][f"2026-10-{_i:02d}"] = dict(blank_day(), plays=[["pasu", "20.01.00", 700]], count={"pasu": 1}, first={"pasu": 700}, best={"pasu": 700},
                                                   val={"range": 23, "dm_k": 20, "dm_d": 18, "dm_hs": 24.0, "skip": False}, rank={"tier": "골드 2", "rr": 5, "games": 1, "why": "pos"})
        bump_ver()
        assert stage_check(_st, "2026-10-11") == (True, 1) and _st["stage"]["since"] == "2026-10-11" and _st["stage"]["ok_weeks"] == []   # 두 주 연속 → 단계 1
        bump_ver(); assert dict(milestones(_st, "2026-10-11")).get("STAGE_UP") == "★ 단계 1 진입 — 골드 2 → 플래티넘 1"
        _s1 = stage_status(_st, "2026-10-11"); assert _s1["idx"] == 1 and _s1["total"] == 5 and _s1["n_ok"] == 1 and _s1["gates"][0]["val"] == "2/9" and _s1["gates"][3]["ok"] is True and _s1["gates"][4]["val"] == "0/14일", [(g["label"], g["ok"], g["val"]) for g in _s1["gates"]]
        assert _s1["gates"][1]["ok"] is False and _s1["gates"][1]["val"].startswith("24%")                              # DM HS% 24 < 25 — 자료는 있으니 None 이 아니라 False
        _st["stage"]["idx"] = 3; bump_ver(); _s3 = stage_status(_st, "2026-10-11"); assert _s3["total"] == 5 and _s3["gates"][2]["ok"] is None and "자료 없음" in _s3["gates"][2]["val"]   # 전적 연동 전엔 ACS 를 모른다
        _st["stage"]["idx"] = 4; _st["valo"] = {"matches": [{"won": True, "hs": 30.0, "k": 20, "d": 15, "acs": 250.0}] * 60}; bump_ver()
        _s4 = stage_status(_st, "2026-10-11"); assert _s4["final"] and _s4["gates"][2]["ok"] is True and _s4["gates"][3]["ok"] is True and _s4["gates"][3]["val"] == "100%", [(g["label"], g["ok"], g["val"]) for g in _s4["gates"]]
        assert stage_check(_st, "2026-10-18") == (False, 4)                                                              # 마지막 단계는 더 오르지 않는다
        _st["stage"] = {"idx": 0, "since": None, "ok_weeks": []}; _st.pop("valo"); bump_ver()
        _wp = week_pack(_st, "2026-10-04")
        assert _wp.startswith("[Road to Immortal] 2026-W40 결산 · 09/28 ~ 10/04 · DAY ") and "[이번 주]" in _wp and "훈련 1일 · 1판" in _wp and "발로 블록 1/1일 · 사격 중앙 23/30 · DM HS% 24" in _wp and "랭크 골드 2 · RR +10 · 판 2 · 죽은 이유 피크·위치 1" in _wp and "[관문]" in _wp and "[다음 주]" in _wp and "월 쉼 · 결산" in _wp and "토 보스전 18판" in _wp and "· 일 " in _wp.split("[다음 주]")[1].split("\n")[1] and "[제목 후보]" in _wp and "W40 결산 — 골드 2 · 관문 4/4" in _wp, _wp
        assert "훈련 기록 없음" in week_pack({"pb": {}, "days": {}, "series": {"ep_offset": 0}}, "2026-10-04")
        import tempfile as _tf
        with _tf.TemporaryDirectory() as _wd:
            _wpp = save_week_pack(_st, "2026-10-04", dir_=_wd); assert _wpp.name == "WEEK_2026-W40_결산.txt" and _wpp.read_text(encoding="utf-8-sig").startswith("[Road to Immortal]")
            assert _st["weeks"]["2026-W40"]["pack"] == "2026-10-04" and _recap_streak(_st, "2026-10-04") == 1 and _recap_streak(_st, "2026-10-11") == 1 and _recap_streak(_st, "2026-10-18") == 0
            _p2, _adv, _idx = week_close(_st, "2026-10-11", dir_=_wd); assert _p2.name == "WEEK_2026-W41_결산.txt" and (_adv, _idx) == (False, 0) and _st["stage"]["ok_weeks"] == ["2026-W41"]
            assert _recap_streak(_st, "2026-10-11") == 2
            assert close_key("2026-10-19") == "2026-10-18" and close_key("2026-10-18") == "2026-10-18" and close_key("2026-10-21") == "2026-10-18"
            _p3, _adv3, _idx3 = week_close(_st, "2026-10-19", dir_=_wd)               # 월요일(쉬는 날)엔 지난 주(10/12~10/18)를 마감한다
            assert _p3.name == "WEEK_2026-W42_결산.txt" and _st["weeks"]["2026-W42"]["pack"] == "2026-10-18" and _recap_streak(_st, "2026-10-19") == 3, (_p3.name, _recap_streak(_st, "2026-10-19"))
            assert recap_label("2026-10-19") == "지난 주" and recap_label("2026-10-20") == "이번 주" and recap_week("2026-10-19") == week_range("2026-10-18")
        _measured(); bump_ver()
        # ── v7: 판정 한 문장 ──
        _mk = lambda st, colk, word, num, rs=None, rw="", n_pb=0: {"day": {"state": st, "colk": colk, "word": word, "num": num, "n_pb": n_pb}, "recent": {"state": rs, "word": rw, "glyph": "▲"}, "grow": {}}
        assert verdict_sentence(_mk("up", "up", "어제보다 좋음", "+6.1%")) == ("● 오늘은 어제보다 잘 나와요 · +6.1%", "어제 같은 판들과 비교한 평균 차이")
        assert verdict_sentence(_mk("flat", "flat", "어제와 비슷", "+0.4%", "up", "요즘 상승세")) == ("● 오늘은 어제와 비슷해요 · +0.4%", "어제 같은 판들과 비교한 평균 차이 · 요즘 상승세 ▲")
        assert verdict_sentence(_mk("down", "down", "어제보다 별로", "-5.0%"))[1].endswith("하루 오르내림은 정상이에요")
        assert verdict_sentence(_mk("wait", "dim", "측정 중", "2/4쌍"), 3) == ("○ 재는 중 · 오늘 점수 재기 3/6 — 다 치면 어제와 비교해요", "첫 판 점수끼리 비교해요")
        assert verdict_sentence(_mk("bench", "rank", "예상 Silver", "Gold까지 34"))[0] == "● 예상 Silver · Gold까지 34"
        for _bad in ("판정까지", "노비스", "관문", "프로브"): assert _bad not in verdict_sentence(_mk("wait", "dim", "측정 중", "0/4쌍"), 0)[0]
        assert verdict_sentence(_mk("wait", "dim", "측정 중", "0/4쌍"), 0)[0].startswith("○ 아직 안 쳤어요")
        # ── v7.2: 저장 위치 ──
        import shutil as _sh, tempfile as _tfo
        _o = {"out_dir": None}; _tdo = Path(_tfo.gettempdir()) / "aimdesk_selftest_out"; _tdo2 = Path(_tfo.gettempdir()) / "aimdesk_selftest_out2"
        _nope = str(Path(os.path.abspath(__file__)) / "nope")                                          # 파일 밑의 폴더 — 윈도우·리눅스 모두 만들 수 없다 (/proc 은 윈도우에서 만들어진다)
        for _d_ in (_tdo, _tdo2): _sh.rmtree(_d_, ignore_errors=True)
        assert set_out_dir(_o, str(_tdo))[0] and report_dir() == _tdo and _o["out_dir"] == str(_tdo) and _tdo.is_dir()
        assert report_path("2026-09-10") == _tdo / "에임데스크_2026-09-10.txt"
        (_tdo / "에임데스크_2026-09-10.txt").write_text("x"); (_tdo / "EP001_2026-09-10_업로드.txt").write_text("x"); (_tdo / "메모.txt").write_text("x")
        assert move_out_files(_tdo, _tdo2) == (2, 0) and (_tdo2 / "EP001_2026-09-10_업로드.txt").exists() and (_tdo / "메모.txt").exists() and not (_tdo / "에임데스크_2026-09-10.txt").exists()
        (_tdo / "에임데스크_2026-09-10.txt").write_text("y"); assert move_out_files(_tdo, _tdo2) == (0, 1)     # 같은 이름은 건너뛴다
        assert set_out_dir(_o, _nope)[0] is False and _o["out_dir"] == str(_tdo)                              # 못 쓰는 폴더는 거절, 설정 유지
        assert load_out_dir({"out_dir": _nope}) is False and OUT_DIR[0] is None                                # 켤 때 못 쓰면 기본으로
        assert set_out_dir(_o, None) == (True, "기본 위치") and _o["out_dir"] is None and report_dir() == DATA_FILE.parent / "기록"
        for _d_ in (_tdo, _tdo2): _sh.rmtree(_d_, ignore_errors=True)
        # ── v7.1: 창 아이콘 — 64px PNG (exe 의 app.ico 와 같은 그림) ──
        import base64 as _b64, struct as _st
        _ic = _b64.b64decode(ICON_B64); assert _ic[:8] == b"\x89PNG\r\n\x1a\n"; assert _st.unpack(">II", _ic[16:24]) == (64, 64)
        # ── v6.3: 자동 코치 · AI 코치 ──
        _ac = _syn({i: 1.0 + 0.01 * i for i in range(12)}); bump_ver()             # 12 훈련일 — 평소 범위가 있는 상태
        _lk = sorted(d for d in _ac["days"] if d != SAMPLE_DATE)[-1]
        trainer_clear(_ac); _txt = auto_coach(_ac, _lk)
        assert _txt.count("목표 ") >= 4 and parse_trainer(_txt, _lk)["errors"] == [], _txt
        _p = trainer_apply(_ac, _txt, _lk); assert len(_p["targets"]) >= 4 and all(0 < v <= _ac["pb"][k] * 1.05 + 1 for k, v in _p["targets"].items()), _p["targets"]
        _t2 = auto_coach(_ac, _lk); assert "테마" not in _t2 and "메모" not in _t2, _t2                                   # 신호 없는 날엔 테마·메모를 지어내지 않는다
        _fresh(); assert auto_coach(_ac, _lk) == ""; _measured()                                                          # 출발선 전엔 침묵
        _u, _h, _b = ai_coach_request("보고서", "sk-test")
        assert _u.endswith("/v1/messages") and _h["x-api-key"] == "sk-test" and _h["anthropic-version"] == "2023-06-01" and _b["model"] == CLAUDE_MODEL and _b["messages"] == [{"role": "user", "content": "보고서"}] and "목표" in _b["system"] and _b["fallbacks"] == "default"
        assert ai_coach_parse({"stop_reason": "end_turn", "content": [{"type": "text", "text": "목표 Pasu 850\n메모 ok"}]}) == ("목표 Pasu 850\n메모 ok", None)
        assert ai_coach_parse({"stop_reason": "refusal", "stop_details": {"category": "x"}, "content": []})[0] is None and ai_coach_parse({"content": []})[1] == "빈 답장"
        assert ai_coach(_ac, _lk, key="") == (False, "API 키 없음", None)
        # ── v7.3: 코치 노트 ──
        assert COACH_MARK in COACH_SYSTEM and all(h_ in COACH_SYSTEM for h_ in COACH_SECTIONS) and ai_coach_request("x", "k")[2]["max_tokens"] >= 8000
        _nt, _ap = ai_coach_split("[오늘 한 줄]\n좋아요\n[한마디]\n화이팅\n" + COACH_MARK + "\n목표 Pasu 850\n메모 ok\n")
        assert _nt == "[오늘 한 줄]\n좋아요\n[한마디]\n화이팅" and _ap == "목표 Pasu 850\n메모 ok" and parse_trainer(_ap, _lk)["targets"] == {"pasu": 850}
        assert ai_coach_split("목표 Pasu 850") == ("목표 Pasu 850", "목표 Pasu 850") and ai_coach_split("") == ("", "")
        _cxd = dict(_ac, coach={"notes": {"2026-09-01": {"text": "지난 노트 본문"}, _lk: {"text": "오늘 것은 안 보냄"}}}, series={"ep_offset": 0})
        _cx = ai_coach_context(_cxd, _lk, ask="손목이 뻐근합니다")
        assert "[지난 코치 노트 · 2026-09-01]" in _cx and "지난 노트 본문" in _cx and "오늘 것은 안 보냄" not in _cx and "[이번 주 결산" in _cx and "[선수가 코치에게]" in _cx and "손목이 뻐근합니다" in _cx, _cx[:300]
        assert "[선수가 코치에게]" not in ai_coach_context(_ac, _lk) and "[지난 코치 노트" not in ai_coach_context(_ac, _lk)
        with _tf.TemporaryDirectory() as _cd:
            _cp = save_coach_note(_cxd, _lk, "[오늘 한 줄]\n좋아요", "목표 Pasu 850", dir_=_cd); _ct = _cp.read_text(encoding="utf-8-sig")
            assert _cp.name.startswith("EP") and _cp.name.endswith(f"_{_lk}_코치.txt") and "[오늘 한 줄]" in _ct and COACH_MARK in _ct and "목표 Pasu 850" in _ct, _cp.name
            assert "EP*_코치.txt" in OUT_PATTERNS and out_dir_files(Path(_cd)) == [_cp]
        # ── v7.4: 계획 탭 코칭 줄 ──
        _nb = "[오늘 한 줄]\n오늘 20판, 어제와 비슷한 하루였습니다. 둘째 문장은 안 나옵니다.\n[잘된 것]\nPasu 610.\n[내일 이렇게]\n1) Popcorn 첫 판은 팔로 붙이기. 2) EddieTS 12판째부터 손 털기. 3) Pasu는 그대로.\n[이번 주 흐름]\n관문 3/10.\n[한마디]\n화이팅"
        assert note_section(_nb, "[내일 이렇게]").startswith("1) Popcorn") and note_section(_nb, "[한마디]") == "화이팅" and note_section(_nb, "[없음]") == ""
        assert note_items(note_section(_nb, "[내일 이렇게]")) == ["Popcorn 첫 판은 팔로 붙이기", "EddieTS 12판째부터 손 털기", "Pasu는 그대로"] and note_items("가\n나") == ["가", "나"] and note_items("") == []
        assert first_sentence(note_section(_nb, "[오늘 한 줄]")) == "오늘 20판, 어제와 비슷한 하루였습니다." and first_sentence("가" * 60, 10).endswith("…") and len(first_sentence("가" * 60, 10)) == 10
        _cdn = {"pb": {}, "days": {}, "coach": {"notes": {"2026-09-18": {"text": _nb, "at": "21:40"}}}}
        assert coach_for_day(_cdn, "2026-09-18") == ("코치", "오늘 20판, 어제와 비슷한 하루였습니다.") and coach_for_day(_cdn, "2026-09-19") == ("내일 이렇게", "Popcorn 첫 판은 팔로 붙이기")   # 9/19 토(벤치)도 다음 계획일
        assert coach_for_day(_cdn, "2026-09-20") is None and coach_for_day(_cdn, "2026-09-17") is None and _next_plan_day("2026-09-20") == "2026-09-22"   # 월요일은 건너뛴다
        assert latest_note(_cdn)[0] == "2026-09-18" and latest_note(_cdn, "2026-09-17") == (None, None) and latest_note({"coach": {}}) == (None, None)
        TRAINER["note"] = "첫 판 전에 손 풀기"; assert coach_for_day({"coach": {}}, "2026-09-22", today="2026-09-22") == ("메모", "첫 판 전에 손 풀기") and coach_for_day({"coach": {}}, "2026-09-23", today="2026-09-22") is None; TRAINER["note"] = ""
        trainer_clear(_ac); bump_ver()
        print("selftest OK: seed energy =", e, "Silver · scan merge OK · deeplink OK · recent_stats OK · v3 base OK · v3 info OK · v3 coach OK · v3 log OK · v3 should OK · v3 ui OK · v3.1 key OK · v3.2 growth OK · v3.4 trainer OK · v4.0 verdict OK · v4.2 day-cutoff OK · v5.0 baseline OK · v6.0 tiers OK · v6.0 episode OK · v6.0 valo OK · v6.0 upload-pack OK · v6.0 thumb OK · v6.0 story OK · v6.0 hysteresis OK · v6.0 stale-pl OK · v6.0 stage OK · v6.0 week-pack OK · v6.3 theme OK · v6.3 coach OK · v7 sentence OK · v7.1 icon OK · v7.2 out-dir OK · v7.2 monday-rest OK · v7.3 coach-note OK · v7.4 cal-coach OK")
        sys.exit(0)
    main()
