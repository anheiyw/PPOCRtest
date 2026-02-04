[app]

# (str) 应用名称
title = PaddleOCR 文字识别

# (str) 应用包名
package.name = pdftool

# (str) 应用域名
package.domain = org.paddleocr

# (str) 应用源文件（不含 .py 扩展名）
source.filename = pdftool_kivy.py

# (str) 应用版本
version = 1.0.0

# (str) 支持的平台
supported_platforms = android

# (list) 官方权限列表 (android)
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE

# (list) Android API 级别
android.minapi = 21
android.api = 33

# (int) NDK 版本
android.ndk = 25b

# (list) Android 架构 (aarch64, armv7a)
android.archs = arm64-v8a,armeabi-v7a

# (str) Android 入口点
android.entrypoint = org.kivy.android.PythonActivity

# (str) Android apptheme
android.apptheme = @android:style/Theme.NoTitleBar

# (bool) 是否全屏
android.fullscreen = False

# (str) 屏幕方向
orientation = portrait

# (str) Python 版本
python.version = 3.9

# (str) Python 实现类型
python.implementation = cpython

# (list) 包含的文件和目录
source.include_dirs = testmodel

# (str) 包含的文件扩展名
source.include_exts = py,png,jpg,kv,atlas,json,yml,yaml,pdiparams

# (str) 应用源代码目录
source.dir = .

# (list) Python 依赖
requirements = python3,kivy,pillow,numpy,opencv-python-headless,paddleocr,paddlepaddle,plyer,pyjnius

# (list) Android assets（模型文件）
android.assets = testmodel/PP-OCRv5_mobile_det_infer:models/PP-OCRv5_mobile_det_infer,testmodel/PP-OCRv5_mobile_rec_infer:models/PP-OCRv5_mobile_rec_infer

# (str) 应用图标（使用默认）
# icon.filename = assets/icon.png

# (str) 应用预设文件（使用默认）
# presplash.filename = assets/presplash.png

# (str) Buildozer 输出目录
output_dir = bin

# (int) 日志级别 (0 = error only, 1 = info, 2 = debug)
log_level = 2
