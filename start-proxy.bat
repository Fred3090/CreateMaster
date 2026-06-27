@echo off
title CreateMaster CORS Proxy
chcp 65001 >nul

echo ===============================================
echo   创图大师 CORS 代理启动器
echo ===============================================
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python！
    echo 请先安装 Python: https://www.python.org/downloads/
    echo 安装时勾选 "Add Python to PATH"
    pause
    exit /b 1
)

:: Download proxy.py
echo [1/3] 下载代理脚本...
curl -s -o "%TEMP%\createmaster_proxy.py" https://raw.githubusercontent.com/Fred3090/CreateMaster/gh-pages/proxy.py
if not exist "%TEMP%\createmaster_proxy.py" (
    echo [错误] 下载失败，请检查网络连接
    pause
    exit /b 1
)
echo [完成]

:: Run proxy
echo [2/3] 启动代理服务器...
echo.
echo ===============================================
echo   ✅ 代理已启动！
echo   现在请完成以下操作：
echo.
echo   ① 打开网站 https://fred3090.github.io/CreateMaster/
echo   ② 选择模型「GPT Image 2 4K」
echo   ③ 在「⚙ 代理设置」中填入：
echo      http://localhost:9901
echo   ④ 点击「保存」
echo   ⑤ 输入提示词，点击「开始生成」
echo ===============================================
echo.
start https://fred3090.github.io/CreateMaster/
echo [3/3] 正在打开网站...
echo.
echo 按 Ctrl+C 停止代理服务器
echo.

python "%TEMP%\createmaster_proxy.py"

pause
