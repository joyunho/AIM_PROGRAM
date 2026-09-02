# 에임 데스크 (AimDesk)

발로란트 · 오버워치 2 에임 향상을 위한 코박스(KovaaK's) 훈련 데스크.
코박스 `stats` 폴더를 2초마다 읽어 오늘 친 판 수 · 점수 · 신기록을 자동 기록하고,
볼테익(Voltaic) Novice S5 벤치마크와 같은 수식으로 에너지·랭크를, 그날 첫 판으로 컨디션(프로브 지수)을 계산합니다.

## 다운로드

**완성된 exe** (파이썬 설치 불필요) — `main` 에 푸시될 때마다 GitHub Actions 가 Windows 에서 자동 빌드합니다.

- 주소: https://github.com/joyunho/AIM_PROGRAM/releases/latest/download/AimDesk.exe
- PowerShell 한 줄 (바탕화면 `AimDesk` 폴더에 받고 SmartScreen 차단 해제):

```powershell
$d="$env:USERPROFILE\Desktop\AimDesk"; New-Item -ItemType Directory -Force $d | Out-Null; Invoke-WebRequest "https://github.com/joyunho/AIM_PROGRAM/releases/latest/download/AimDesk.exe" -OutFile "$d\AimDesk.exe"; Unblock-File "$d\AimDesk.exe"; explorer $d
```

**소스로 직접 빌드** (git + 파이썬 필요):

```bat
git clone https://github.com/joyunho/AIM_PROGRAM.git && cd AIM_PROGRAM && make_exe.bat
```

기존에 쓰던 `aim_desk_data.json` 이 있으면 새 exe 옆으로 복사해야 기록이 이어집니다.

## 파일

| 파일 | 역할 |
|---|---|
| `aim_desk.py` | 프로그램 전체 (파이썬 3.9+, 표준 라이브러리만 사용) |
| `make_exe.bat` | 더블클릭 → PyInstaller로 `AimDesk.exe` 생성 + 바탕화면 바로가기 |
| `app.ico` (선택) | exe 아이콘. 없으면 기본 아이콘으로 빌드 |
| `.github/workflows/build-exe.yml` | main 푸시 시 exe 자동 빌드 → `latest` 릴리스에 업로드 |

실행: `python aim_desk.py` 또는 빌드한 `AimDesk.exe`. 자가 점검: `python aim_desk.py --selftest`.

## 사용 흐름

1. 첫 실행 시 스팀 코박스 `stats` 폴더를 자동 탐지합니다 (못 찾으면 우측 카드에서 "폴더 선택").
2. 플레이리스트 `AIMDESK Day / Friday / Probe` 도 코박스 Local Playlists 에 자동 설치됩니다 (자동 진행 대신 코박스 안에서 직접 돌리고 싶을 때용).
3. **▶ 오늘 루틴 실행** — 오늘 칠 시나리오 전체가 순서대로 나열된 **순서창**이 열리고, 1번 시나리오가 코박스로 바로 전송됩니다
   (코박스가 꺼져 있으면 스팀이 켜서 시작). 한 판이 끝나면 잠깐 뒤 다음 시나리오가 **자동으로** 뜹니다 — 결과창에서 NEXT를 누를 필요가 없습니다.
   순서창은 항상 위에 떠 있고 끝난 판은 ✓, 다음 판은 ▶ 로 표시됩니다.
   - **자동 진행** 토글 · **다음 판 ▶**(지금 차례 건너뛰고 바로 전송) · **다시 보내기**(안 넘어갔을 때) · **처음부터**(오늘 두 번째 세션) · 판 사이 **대기 초** 조절
   - 순서창을 닫거나 코박스를 끄면 자동 진행이 멈춥니다. "순서 보기"는 전송 없이 순서만 봅니다.
4. 코박스 좌하단 토글이 FREEPLAY 면 기록이 남지 않으니 CHALLENGE 로.

요일 루틴: 월–목 발로 데이(웜업 4 → 프로브 6 → 본훈련 17) · 금 약점 데이(컨트롤) · 토 벤치마크 18개 풀런 · 일 휴식.

## 기록 파일

- 기본 위치: exe(또는 스크립트) 옆 `aim_desk_data.json`.
  그 폴더에 쓸 수 없거나(Program Files 등) 임시폴더에서 실행되면(zip 안에서 더블클릭) `%LOCALAPPDATA%\AimDesk\` 를 사용합니다.
- 저장은 임시 파일에 쓴 뒤 교체(원자적)라 강제 종료로 파일이 잘리지 않습니다.
- 실행할 때마다 직전 정상본을 `aim_desk_data.backup.json` 으로 보관합니다.
- 파일이 손상되면 덮어쓰지 않고 `aim_desk_data.corrupt-날짜.json` 으로 이름을 바꿔 두고 경고창을 띄웁니다.
- 오류는 같은 폴더의 `aim_desk.log` 에 남습니다 (창 모드 exe는 콘솔이 없으므로).

## 알아둘 것

- 자동 진행은 코박스 **공식 딥링크**(`steam://run/824270/?action=jump-to-scenario;name=…`, 3.0.0+)를 씁니다. Steam 이 켜져 있어야 하고,
  시나리오가 안 넘어가면 순서창의 "다시 보내기"를 누르세요. 다음 판까지의 대기 시간(기본 4초)은 순서창에서 바꿀 수 있습니다.
- **타이머가 안 보이면 코박스가 FREEPLAY 모드입니다.** 딥링크는 코박스의 현재 모드(FREEPLAY/CHALLENGE)를 그대로 따르고 이 모드는 게임이 기억하므로,
  결과창의 "FREEPLAY" 버튼을 한 번이라도 누르면 그 뒤 모든 판이 타이머·기록 없이 열립니다. 결과창에선 아무것도 누르지 말고 기다리세요.
  이미 바뀌었다면 게임에서 ESC → 좌하단 토글을 CHALLENGE 로 → 순서창 "다시 보내기". 앱은 보낸 지 100초가 지나도 기록이 없으면 이 경고를 띄웁니다.

- 시나리오 이름과 랭크 임계값은 **Voltaic Novice S5** 기준으로 하드코딩되어 있습니다. 볼테익이 시즌을 바꾸면 `SCEN` / `SUBS` 를 갱신해야 합니다.
- 헤더의 에너지는 **PB 기준**(항상 9/9 카테고리)이고, 벤치 탭은 오늘(없으면 마지막 기록일)의 베스트 기준으로 `n/9` 를 표시합니다.
- 프로브 지수는 같은 시나리오의 첫 판이 4일 이상 쌓여야 계산됩니다.
- 직접 빌드한 exe는 서명이 없어 다른 PC에서 SmartScreen/백신 경고가 뜰 수 있습니다. 배포 대신 각자 `make_exe.bat` 로 빌드하는 편이 안전합니다.
