@echo off
chcp 65001 >nul
title 에임 데스크 — exe 빌드
echo.
echo  ┌─────────────────────────────────────────┐
echo  │  에임 데스크를 exe로 굽습니다 (1~2분)   │
echo  └─────────────────────────────────────────┘
echo.

where py >nul 2>nul
if %errorlevel%==0 (set PY=py) else (set PY=python)

%PY% --version >nul 2>nul
if not %errorlevel%==0 (
  echo  [실패] 파이썬이 없습니다. python.org 에서 설치 후 다시 실행하세요.
  echo         설치 시 "Add python.exe to PATH" 체크 필수!
  pause & exit /b
)

echo  1/3  PyInstaller 설치 확인...
%PY% -m pip install --quiet --upgrade pyinstaller

echo  2/3  빌드 중... (창이 멈춘 듯 보여도 기다리세요)
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed --icon app.ico --name AimDesk aim_desk.py >build_log.txt 2>&1

if not exist dist\AimDesk.exe (
  echo.
  echo  [실패] 빌드 오류 — build_log.txt 내용을 캡처해서 보내주세요.
  pause & exit /b
)

echo  3/3  마무리...
copy /y dist\AimDesk.exe AimDesk.exe >nul
rmdir /s /q build dist >nul 2>nul
del /q AimDesk.spec >nul 2>nul

powershell -NoProfile -Command "$s=(New-Object -ComObject WScript.Shell).CreateShortcut([Environment]::GetFolderPath('Desktop')+'\에임 데스크.lnk');$s.TargetPath='%cd%\AimDesk.exe';$s.WorkingDirectory='%cd%';$s.IconLocation='%cd%\app.ico';$s.Save()" >nul 2>nul

echo.
echo  ✔ 완료!
echo    · 이 폴더에 AimDesk.exe 생성됨 (파이썬 없이 실행 가능)
echo    · 바탕화면에 "에임 데스크" 바로가기 추가됨
echo    · 기록 파일(aim_desk_data.json)은 exe 옆에 저장됩니다
echo.
pause
