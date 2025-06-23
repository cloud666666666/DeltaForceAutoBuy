@echo off
chcp 65001 >nul

:: 检查是否已经是管理员权限
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run_program
) else (
    echo ================================
    echo 三角洲行动自动购买助手
    echo ================================
    echo 检测到需要管理员权限才能正常使用键盘热键功能
    echo 正在请求管理员权限...
    echo.
    goto :request_admin
)

:request_admin
:: 请求管理员权限并重新运行
powershell -Command "Start-Process '%~f0' -Verb RunAs"
exit /b

:run_program
title 三角洲行动自动购买助手 - 管理员模式
cd /d "%~dp0"

echo ================================
echo 三角洲行动自动购买助手
echo 管理员权限模式
echo ================================
echo 正在启动程序...
echo.

:: 检查虚拟环境是否存在
if not exist ".venv\Scripts\python.exe" (
    echo 错误：未找到虚拟环境！
    echo 请确保 .venv 目录存在
    echo.
    echo 如果您下载的是完整包，请确保：
    echo 1. 完整解压了所有文件
    echo 2. .venv 文件夹在当前目录下
    echo 3. 没有被杀毒软件删除
    pause
    exit /b 1
)

:: 启动程序
echo 启动中，请稍等...
echo.
".venv\Scripts\python.exe" "main.py"

:: 检查程序退出状态
set exit_code=%errorlevel%
echo.
if %exit_code% == 0 (
    echo 程序正常退出
) else (
    echo 程序异常退出，错误代码: %exit_code%
    echo.
    echo 可能的解决方案：
    echo 1. 检查游戏是否正在运行
    echo 2. 确保以管理员权限运行
    echo 3. 检查配置文件是否正确
    echo 4. 查看上方的错误信息
)

echo.
echo 按任意键退出...
pause >nul 