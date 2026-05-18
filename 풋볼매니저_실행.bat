@echo off
chcp 65001 > nul
echo.
echo ==========================================
echo      Football Manager Web 시작
echo ==========================================
echo.

echo [1/2] 의존성 설치 확인 중...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo 의존성 설치에 실패했습니다.
    pause
    exit /b 1
)

echo.
echo [2/2] 웹 서버 시작 중...
echo 브라우저에서 http://localhost:5000 으로 접속하세요.
echo.
python app.py

if errorlevel 1 (
    echo.
    echo 서버 실행 중 오류가 발생했습니다.
    pause
)
