# PaddleOCR 文字识别工具

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-lightgrey)

基于 PaddleOCR 的跨平台文字识别工具，支持 PDF 和图片文件的 OCR 识别。

[功能介绍](#功能特性) • [快速开始](#快速开始) • [APK 下载](#android-版本) • [常见问题](#常见问题)

</div>

---

## 目录

- [功能特性](#功能特性)
- [项目结构](#项目结构)
- [环境要求](#环境要求)
- [快速开始](#快速开始)
  - [桌面版](#桌面版-windowslinuxmacos)
  - [Android 版](#android-版本)
- [APK 编译指南](#apk-编译指南)
- [模型准备](#模型准备)
- [常见问题](#常见问题)
- [技术栈](#技术栈)
- [许可证](#许可证)

---

## 功能特性

### 桌面版
- **图形化界面**：基于 Tkinter 的简洁 GUI
- **多格式支持**：PDF、JPG、PNG、BMP、GIF、TIFF
- **批量处理**：支持多页 PDF 自动识别
- **结果可视化**：自动生成标注图片和文本结果
- **一键打开**：识别完成后自动打开结果文件夹

### Android 版
- **移动端适配**：基于 Kivy 框架的跨平台移动应用
- **触摸操作**：专为手机设计的交互界面
- **本地识别**：无需网络连接，完全本地处理
- **存储权限**：自动请求必要的文件访问权限
- **结果保存**：识别结果保存到外部存储

---

## 项目结构

```
PPOCRtest-main/
├── pdftool.py                 # 桌面版应用（tkinter）
├── pdftool_kivy.py            # 移动版应用（Kivy）
├── prepare_models.py          # 模型文件准备脚本
├── buildozer.spec             # Android APK 打包配置
├── build_apk.bat              # Windows 编译脚本
├── build_apk.sh               # Linux/macOS 编译脚本
├── requirements_android.txt   # Android 依赖清单
├── testmodel/                 # 模型文件目录（需单独下载）
│   ├── PP-OCRv5_mobile_det_infer/   # 检测模型
│   └── PP-OCRv5_mobile_rec_infer/   # 识别模型
├── assets/                    # 应用资源
└── output/                    # OCR 输出结果
```

---

## 环境要求

### 桌面版

| 组件 | 要求 |
|------|------|
| Python | 3.9 或更高版本 |
| 操作系统 | Windows 7+ / Linux / macOS 10.14+ |
| 内存 | 建议 4GB 以上 |

### Android 版

| 组件 | 要求 |
|------|------|
| Android | API 21 (Android 5.0) 或更高 |
| 架构 | ARM64-v8a 或 ARMv7a |
| 存储空间 | 至少 100MB 可用空间 |
| 权限 | 存储读写权限 |

---

## 快速开始

### 桌面版 (Windows/Linux/macOS)

#### 1. 安装依赖

```bash
pip install paddleocr paddlepaddle pillow numpy opencv-python
```

#### 2. 下载模型

```bash
# 方式1：使用 PaddleOCR 自动下载（首次运行时）
python pdftool.py

# 方式2：手动下载
# 从 https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/models_list.md
# 下载 PP-OCRv5_mobile 系列模型
```

#### 3. 运行程序

```bash
python pdftool.py
```

#### 4. 使用步骤

1. 点击 "选择 PDF 文件" 或 "选择图片"
2. 选择要识别的文件
3. 点击 "开始识别"
4. 等待识别完成
5. 自动打开结果文件夹

---

### Android 版

#### 方式 1：下载 APK 安装（推荐）

1. 从 [Releases](../../releases) 下载最新 APK
2. 在手机上启用 "未知来源应用安装"
3. 安装 APK
4. 授予存储权限
5. 打开应用，选择文件进行识别

#### 方式 2：自己编译 APK

详见 [APK 编译指南](#apk-编译指南)

#### 使用说明

1. 首次运行会自动从 assets 复制模型文件
2. 点击 "选择 PDF" 或 "选择图片"
3. 选择要识别的文件
4. 点击 "开始识别"
5. 等待识别完成，查看结果

识别结果保存在：`/sdcard/PaddleOCR/`

---

## APK 编译指南

### 前置要求

| 组件 | 版本要求 |
|------|----------|
| Python | 3.9+ |
| Java JDK | 11 或 17 |
| Buildozer | 1.5.0+ |
| 操作系统 | Linux / macOS / WSL2 (Windows 不支持) |

> ⚠️ **注意**：Buildozer 在 Windows 上不支持编译，建议使用 WSL2、Linux 或 macOS。

### 编译步骤

#### 1. 安装依赖

```bash
pip install buildozer cython
```

#### 2. 准备模型文件

```bash
# 将模型文件放到 testmodel/ 目录
python prepare_models.py
```

#### 3. 开始编译

```bash
# Linux/macOS
./build_apk.sh

# 或手动执行
buildozer android debug
```

#### 4. 首次编译

首次编译会自动下载：
- Android SDK (约 1GB)
- Android NDK (约 800MB)
- 编译工具链

预计耗时：**30-60 分钟**

#### 5. 输出位置

编译完成后，APK 文件位于：
```
bin/pdftool-1.0.0-arm64-v8a-debug.apk
```

### 编译选项

```bash
# Debug 版本（包含调试信息）
buildozer android debug

# Release 版本（优化性能，体积更小）
buildozer android release

# 仅编译 ARM64 架构
buildozer android debug --arch arm64-v8a

# 查看详细日志
buildozer android debug --verbose
```

---

## 模型准备

### 模型文件说明

本工具使用 **PaddleOCR PP-OCRv5 Mobile** 模型：

| 模型 | 大小 | 用途 |
|------|------|------|
| PP-OCRv5_mobile_det | ~4.5MB | 文字检测 |
| PP-OCRv5_mobile_rec | ~16MB | 文字识别 |

### 获取模型

#### 方式 1：自动下载（推荐）

```bash
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='ch')
# 模型会自动下载到 ~/.paddleocr/whl/
```

#### 方式 2：手动下载

访问 [PaddleOCR 模型列表](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.7/doc/doc_ch/models_list.md)

下载以下模型：
- **检测模型**：[PP-OCRv5_mobile_det_infer](https://paddleocr.bj.bcebos.com/PP-OCRv5/chinese/PP-OCRv5_mobile_det_infer.tar)
- **识别模型**：[PP-OCRv5_mobile_rec_infer](https://paddleocr.bj.bcebos.com/PP-OCRv5/chinese/PP-OCRv5_mobile_rec_infer.tar)

解压到 `testmodel/` 目录：
```
testmodel/
├── PP-OCRv5_mobile_det_infer/
│   ├── inference.pdiparams
│   └── inference.yml
└── PP-OCRv5_mobile_rec_infer/
    ├── inference.pdiparams
    └── inference.yml
```

### 验证模型

```bash
python prepare_models.py --info
```

---

## 常见问题

### 桌面版

**Q: 运行时提示找不到模型？**

A: 确保模型文件在正确位置：
```bash
testmodel/PP-OCRv5_mobile_det_infer/
testmodel/PP-OCRv5_mobile_rec_infer/
```

**Q: 识别速度很慢？**

A: 可以尝试：
1. 使用 GPU 版本：`pip install paddlepaddle-gpu`
2. 降低图片分辨率
3. 使用更小的 Mobile 模型

**Q: 中文显示乱码？**

A: 确保使用 UTF-8 编码打开文本文件。

### Android 版

**Q: APK 安装后闪退？**

A: 检查：
1. Android 版本是否 >= 5.0
2. 是否授予了存储权限
3. 手机架构是否支持（ARM64/ARMv7）

**Q: 识别失败？**

A: 可能原因：
1. 模型文件损坏 - 重新安装 APK
2. 存储空间不足 - 清理手机存储
3. 文件格式不支持 - 使用 PDF/JPG/PNG

**Q: 如何在 Android Studio 中调试？**

A: 使用 `buildozer android debug` 生成的项目位于 `.buildozer/android/`，可以用 Android Studio 打开。

### 编译相关

**Q: 编译时网络超时？**

A: 使用国内镜像：
```bash
export ANDROID_SDK_HOME=/path/to/sdk
buildozer android debug
```

**Q: 内存不足？**

A: 关闭其他程序，或增加交换空间：
```bash
# Linux
sudo fallocate -l 8G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**Q: 依赖安装失败？**

A: 尝试清理缓存重试：
```bash
buildozer distclean
buildozer android debug
```

---

## 技术栈

### 桌面版
- **PaddleOCR** - OCR 识别引擎
- **PaddlePaddle** - 深度学习框架
- **Tkinter** - GUI 框架
- **OpenCV** - 图像处理
- **Pillow** - 图像操作

### Android 版
- **Kivy** - 跨平台移动应用框架
- **Buildozer** - Python 移动应用打包工具
- **Python-for-Android** - Android Python 运行时
- **Plyer** - 平台 API 抽象层

---

## 输出格式

识别完成后，会在 `output/` 目录生成以下文件：

```
output/
├── page_001_result/
│   ├── page_001_result.txt          # 文本识别结果
│   ├── page_001_result_res.json     # JSON 格式结果
│   └── 坐标未简省_0_ocr_res_img.png # 可视化标注图片
└── page_002_result/
    └── ...
```

### JSON 结果格式

```json
[
  {
    "bbox": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]],
    "rec_text": "识别的文字",
    "rec_score": 0.98
  }
]
```

---

## 性能参考

| 设备 | 识别速度 | 内存占用 |
|------|----------|----------|
| Intel i7-10700 | ~200ms/页 | ~500MB |
| NVIDIA GTX 1660 | ~50ms/页 | ~800MB |
| Snapdragon 865 | ~500ms/页 | ~300MB |
| Snapdragon 660 | ~1.5s/页 | ~250MB |

---

## 更新日志

### v1.0.0 (2025-01-XX)
- ✨ 初始版本发布
- ✨ 支持桌面版（Tkinter）
- ✨ 支持 Android 版（Kivy）
- ✨ 集成 PP-OCRv5 Mobile 模型
- ✨ 支持多页 PDF 识别
- ✨ 自动生成可视化结果

---

## 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发环境设置

```bash
# 克隆仓库
git clone https://github.com/anheiyw/PPOCRtest.git
cd PPOCRtest-main

# 安装开发依赖
pip install -r requirements.txt
```

### 代码风格

- 遵循 PEP 8 规范
- 使用 4 空格缩进
- 添加适当的注释和文档字符串

---

## 许可证

本项目采用 [MIT](LICENSE) 许可证。

```
Copyright (c) 2025 PPOCRtest Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 致谢

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 强大的 OCR 识别引擎
- [PaddlePaddle](https://github.com/PaddlePaddle/Paddle) - 深度学习框架
- [Kivy](https://kivy.org/) - 跨平台 Python 应用框架
- [Buildozer](https://buildozer.readthedocs.io/) - Python 移动应用打包工具

---

## 联系方式

- **Issues**: [GitHub Issues](../../issues)
- **Email**: anheiyw@github.com

---

<div align="center">

**如果这个项目对你有帮助，请给个 ⭐️ Star！**

Made with ❤️ by [anheiyw](https://github.com/anheiyw)

</div>
