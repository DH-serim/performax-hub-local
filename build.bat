@echo off
echo ==============================
echo  Performax Hub exe 빌드
echo ==============================

echo [1/3] 패키지 설치 중...
pip install flask requests pyinstaller --quiet

echo [2/3] exe 빌드 중... (1~2분 소요)
pyinstaller ^
  --onefile ^
  --noconsole ^
  --name "PerformaxHub" ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  app.py

echo [3/3] 완료
if exist dist\PerformaxHub.exe (
  echo.
  echo  빌드 성공!
  echo  dist\PerformaxHub.exe 파일을 배포하세요.
  echo.
  explorer dist
) else (
  echo.
  echo  빌드 실패. 오류 메시지를 확인해주세요.
)

pause
