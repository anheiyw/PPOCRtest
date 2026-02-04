@echo off
REM ========================================================
REM PaddleOCR APK 编译脚本 (Windows)
REM ========================================================
REM
REM 功能：自动化编译 Android APK
REM
REM 前置要求：
REM   1. 安装 Python 3.9+
REM   2. 安装 Java JDK 11+
REM   3. 安装 Android SDK 和 NDK
REM   4. 安装 buildozer: pip install buildozer cython
REM
REM ========================================================

setlocal enabledelayedexpansion

echo ========================================
echo PaddleOCR APK 编译脚本
echo ========================================
echo.

REM 检查 Python
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

REM 检查 buildozer
python -c "import buildozer" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [警告] 未找到 buildozer
    echo 正在安装 buildozer 和依赖...
    pip install buildozer cyython
    if %ERRORLEVEL% NEQ 0 (
        echo [错误] buildozer 安装失败
        pause
        exit /b 1
    )
)

REM 检查模型文件
if not exist "testmodel\PP-OCRv5_mobile_det_infer" (
    echo [错误] 未找到检测模型文件
    echo 请确保 testmodel\PP-OCRv5_mobile_det_infer 目录存在
    pause
    exit /b 1
)

if not exist "testmodel\PP-OCRv5_mobile_rec_infer" (
    echo [错误] 未找到识别模型文件
    echo 请确保 testmodel\PP-OCRv5_mobile_rec_infer 目录存在
    pause
    exit /b 1
)

REM 准备模型文件
echo.
echo [1/4] 准备模型文件...
python prepare_models.py
if %ERRORLEVEL% NEQ 0 (
    echo [错误] 模型文件准备失败
    pause
    exit /b 1
)

REM 初始化 buildozer
echo.
echo [2/4] 初始化 buildozer...
if not exist "buildozer.spec" (
    echo [错误] 未找到 buildozer.spec 配置文件
    pause
    exit /b 1
)

REM 编译 APK
echo.
echo [3/4] 开始编译 APK...
echo 注意: 首次编译需要下载依赖，可能需要 30-60 分钟
echo.

buildozer android debug
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [错误] APK 编译失败
    echo 请检查错误信息并重试
    pause
    exit /b 1
)

REM 完成
echo.
echo [4/4] 编译完成!
echo ========================================
echo APK 文件位置: bin\
echo ========================================
echo.

REM 列出生成的 APK 文件
dir /b bin\*.apk 2>nul

echo.
echo 安装到设备:
echo   adb install -r bin\[APK文件名]
echo.
pause
