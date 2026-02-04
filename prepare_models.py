"""
========================================================
模型文件准备脚本
========================================================

功能说明：
    验证和准备 PaddleOCR 模型文件，用于 Android APK 编译。

使用方式：
    python prepare_models.py

输出：
    - 在 models/ 目录创建模型文件副本（用于 buildozer assets）
    - 验证模型文件完整性
========================================================
"""

import os
import sys
import shutil
from pathlib import Path


# 必需的模型文件（PaddleOCR v5 新格式不需要 pdmodel）
REQUIRED_MODEL_FILES = [
    'inference.pdiparams',
    'inference.yml'
]

# 模型目录配置
MODELS_CONFIG = {
    'PP-OCRv5_mobile_det_infer': 'PP-OCRv5_mobile_det_infer',
    'PP-OCRv5_mobile_rec_infer': 'PP-OCRv5_mobile_rec_infer'
}


def verify_model_files(model_dir):
    """
    验证模型文件是否完整

    Args:
        model_dir: 模型目录路径

    Returns:
        (是否完整, 缺失文件列表)
    """
    if not os.path.exists(model_dir):
        return False, [f"模型目录不存在: {model_dir}"]

    missing_files = []
    for filename in REQUIRED_MODEL_FILES:
        filepath = os.path.join(model_dir, filename)
        if not os.path.exists(filepath):
            missing_files.append(filename)

    is_complete = len(missing_files) == 0
    return is_complete, missing_files


def prepare_assets(source_dir='testmodel', target_dir='models'):
    """
    准备 Android assets 文件

    Args:
        source_dir: 源模型目录
        target_dir: 目标 assets 目录
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    source_base = os.path.join(base_dir, source_dir)
    target_base = os.path.join(base_dir, target_dir)

    print("=" * 60)
    print("PaddleOCR 模型文件准备工具")
    print("=" * 60)

    # 创建目标目录
    os.makedirs(target_base, exist_ok=True)

    # 验证并复制每个模型
    all_valid = True
    for model_name in MODELS_CONFIG.values():
        source_path = os.path.join(source_base, model_name)
        target_path = os.path.join(target_base, model_name)

        print(f"\n检查模型: {model_name}")
        print(f"源路径: {source_path}")

        # 验证模型文件
        is_complete, missing = verify_model_files(source_path)

        if not is_complete:
            print(f"  [错误] 模型文件不完整!")
            for f in missing:
                print(f"    缺失: {f}")
            all_valid = False
            continue

        print(f"  [OK] 模型文件完整")

        # 复制文件
        os.makedirs(target_path, exist_ok=True)
        for filename in REQUIRED_MODEL_FILES:
            src_file = os.path.join(source_path, filename)
            dst_file = os.path.join(target_path, filename)

            # 检查是否需要复制
            if os.path.exists(dst_file):
                src_size = os.path.getsize(src_file)
                dst_size = os.path.getsize(dst_file)
                if src_size == dst_size:
                    print(f"    {filename} (已存在，跳过)")
                    continue

            shutil.copy2(src_file, dst_file)
            file_size = os.path.getsize(dst_file) / 1024  # KB
            print(f"    {filename} ({file_size:.1f} KB)")

    print("\n" + "=" * 60)
    if all_valid:
        print("[成功] 所有模型文件已准备完成!")
        print(f"目标目录: {target_base}")
        print("\nbuildozer.spec 配置:")
        print("  android.assets = testmodel/PP-OCRv5_mobile_det_infer:models/PP-OCRv5_mobile_det_infer")
        print("  android.assets = testmodel/PP-OCRv5_mobile_rec_infer:models/PP-OCRv5_mobile_rec_infer")
    else:
        print("[失败] 部分模型文件不完整，请检查!")
        return 1

    return 0


def print_model_info():
    """打印模型信息"""
    base_dir = os.path.dirname(os.path.abspath(__file__))

    print("\n" + "=" * 60)
    print("模型文件信息")
    print("=" * 60)

    for model_name in MODELS_CONFIG.values():
        model_dir = os.path.join(base_dir, 'testmodel', model_name)

        if not os.path.exists(model_dir):
            print(f"\n{model_name}: [目录不存在]")
            continue

        print(f"\n{model_name}:")
        total_size = 0
        for filename in REQUIRED_MODEL_FILES:
            filepath = os.path.join(model_dir, filename)
            if os.path.exists(filepath):
                size = os.path.getsize(filepath)
                total_size += size
                print(f"  {filename}: {size:,} bytes")
            else:
                print(f"  {filename}: [缺失]")

        print(f"  总计: {total_size:,} bytes ({total_size/1024/1024:.2f} MB)")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='PaddleOCR 模型文件准备工具')
    parser.add_argument('--info', action='store_true',
                        help='显示模型文件信息')
    parser.add_argument('--source', default='testmodel',
                        help='源模型目录 (默认: testmodel)')
    parser.add_argument('--target', default='models',
                        help='目标 assets 目录 (默认: models)')

    args = parser.parse_args()

    if args.info:
        print_model_info()
        return 0

    return prepare_assets(args.source, args.target)


if __name__ == "__main__":
    sys.exit(main())
