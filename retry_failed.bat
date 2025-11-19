@echo off
REM 失敗した予想家のリトライスクリプト

cd /d %~dp0

echo ========================================
echo 失敗した予想家のリトライ処理
echo ========================================
echo.
echo 対象: 25人の予想家
echo 推定時間: 約15分（各予想家15秒間隔）
echo.
echo 実行しますか？
pause

REM 仮想環境の有効化
call venv\Scripts\activate.bat

REM PYTHONPATHを設定
set PYTHONPATH=%CD%

echo.
echo ========================================
echo リトライ処理開始...
echo ========================================
echo.

REM リトライスクリプト実行
python retry_failed.py

echo.
echo ========================================
echo リトライ処理完了
echo ========================================
echo.
echo ログを確認してください: logs\retry_*.log
echo.
pause
