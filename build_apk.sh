#!/bin/bash
# ========================================================
# PaddleOCR APK 编译脚本 (Linux/macOS)
# ========================================================
#
# 功能：自动化编译 Android APK
#
# 前置要求：
#   1. 安装 Python 3.9+
#   2. 安装 Java JDK 11+
#   3. 安装 Android SDK 和 NDK
#   4. 安装 buildozer: pip install buildozer cython
#
# ========================================================

set -e

echo "========================================"
echo "PaddleOCR APK 编译脚本"
echo "========================================"
echo ""

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到 Python3，请先安装 Python 3.9+"
    exit 1
fi

echo "Python 版本: $(python3 --version)"

# 检查 buildozer
if ! python3 -c "import buildozer" 2>/dev/null; then
    echo "[警告] 未找到 buildozer"
    echo "正在安装 buildozer 和依赖..."
    pip3 install buildozer cython
    if [ $? -ne 0 ]; then
        echo "[错误] buildozer 安装失败"
        exit 1
    fi
fi

# 检查模型文件
if [ ! -d "testmodel/PP-OCRv5_mobile_det_infer" ]; then
    echo "[错误] 未找到检测模型文件"
    echo "请确保 testmodel/PP-OCRv5_mobile_det_infer 目录存在"
    exit 1
fi

if [ ! -d "testmodel/PP-OCRv5_mobile_rec_infer" ]; then
    echo "[错误] 未找到识别模型文件"
    echo "请确保 testmodel/PP-OCRv5_mobile_rec_infer 目录存在"
    exit 1
fi

# 准备模型文件
echo ""
echo "[1/4] 准备模型文件..."
python3 prepare_models.py
if [ $? -ne 0 ]; then
    echo "[错误] 模型文件准备失败"
    exit 1
fi

# 检查 buildozer.spec
echo ""
echo "[2/4] 检查配置文件..."
if [ ! -f "buildozer.spec" ]; then
    echo "[错误] 未找到 buildozer.spec 配置文件"
    exit 1
fi

# 编译 APK
echo ""
echo "[3/4] 开始编译 APK..."
echo "注意: 首次编译需要下载依赖，可能需要 30-60 分钟"
echo ""

buildozer android debug
if [ $? -ne 0 ]; then
    echo ""
    echo "[错误] APK 编译失败"
    echo "请检查错误信息并重试"
    exit 1
fi

# 完成
echo ""
echo "[4/4] 编译完成!"
echo "========================================"
echo "APK 文件位置: bin/"
echo "========================================"
echo ""

# 列出生成的 APK 文件
ls -lh bin/*.apk 2>/dev/null || echo "未找到 APK 文件"

echo ""
echo "安装到设备:"
echo "  adb install -r bin/[APK文件名]"
echo ""
