"""
========================================================
PaddleOCR PDF 文字识别测试脚本
========================================================

功能说明：
    使用本地下载的 PaddleOCR 模型对 PDF 文件进行 OCR 识别。
    PaddleOCR 原生支持 PDF 输入。

模型路径：
    - 检测模型：./testmodel/PP-OCRv5_mobile_det_infer
    - 识别模型：./testmodel/PP-OCRv5_mobile_rec_infer

依赖安装：
    pip install paddleocr paddlepaddle

运行方式：
    python pdf.py
========================================================
"""

import os
from paddleocr import PaddleOCR


def init_ocr_model(det_model_path, rec_model_path):
    """
    初始化 PaddleOCR 模型，使用本地下载的模型

    Args:
        det_model_path: 检测模型路径
        rec_model_path: 识别模型路径

    Returns:
        PaddleOCR 实例
    """
    print("正在初始化 OCR 模型...")
    ocr = PaddleOCR(
        text_detection_model_name="PP-OCRv5_mobile_det",
        text_recognition_model_name="PP-OCRv5_mobile_rec",
        text_detection_model_dir=det_model_path,
        text_recognition_model_dir=rec_model_path,
        use_doc_orientation_classify=False,  # 是否使用文档方向分类
        use_doc_unwarping=False,            # 是否使用文档展平
        use_textline_orientation=False      # 是否使用文字行方向检测
    )
    print("OCR 模型初始化完成")
    return ocr


def process_pdf(pdf_path, ocr, output_dir="output"):
    """
    处理 PDF 文件，进行 OCR 识别

    Args:
        pdf_path: PDF 文件路径
        ocr: PaddleOCR 实例
        output_dir: 输出目录
    """
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    print(f"正在处理 PDF: {pdf_path}")

    # 直接对 PDF 文件进行 OCR 识别（PaddleOCR 原生支持）
    result = ocr.predict(input=pdf_path)

    # 保存结果
    page_num = 1
    all_text = []

    for res in result:
        # 打印识别结果
        print(f"\n=== 第 {page_num} 页识别结果 ===")
        res.print()

        # 为每页创建单独的文件夹
        page_dir = os.path.join(output_dir, f"page_{page_num:03d}_result")
        os.makedirs(page_dir, exist_ok=True)

        # 直接使用文件夹路径作为前缀（save_to_img 和 save_to_json 会自动添加文件名）
        res.save_to_img(page_dir)
        print(f"可视化图像已保存: {page_dir}")

        res.save_to_json(page_dir)
        print(f"JSON 结果已保存: {page_dir}")

        # 保存文本结果（手动指定文件名）
        texts = res.get('rec_texts', [])
        txt_path = os.path.join(page_dir, f"page_{page_num:03d}_result.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(texts))
        print(f"文本已保存: {txt_path}")

        # 收集所有文本用于汇总显示
        all_text.extend(texts)
        page_num += 1

    print("\n" + "="*50)
    print("所有页面的文本内容汇总:")
    print("="*50)
    for line in all_text:
        print(line)

    return result


def main():
    # 模型路径配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DET_MODEL_PATH = os.path.join(BASE_DIR,  "testmodel", "PP-OCRv5_mobile_det_infer")
    REC_MODEL_PATH = os.path.join(BASE_DIR,  "testmodel", "PP-OCRv5_mobile_rec_infer")

    # 检查模型是否存在
    if not os.path.exists(DET_MODEL_PATH):
        print(f"错误: 检测模型不存在: {DET_MODEL_PATH}")
        return
    if not os.path.exists(REC_MODEL_PATH):
        print(f"错误: 识别模型不存在: {REC_MODEL_PATH}")
        return

    # PDF 文件路径
    PDF_PATH = os.path.join(BASE_DIR, "吴嘉豪简历.pdf")

    # 检查 PDF 是否存在
    if not os.path.exists(PDF_PATH):
        print(f"错误: PDF 文件不存在: {PDF_PATH}")
        print(f"\n当前目录下的 PDF 文件:")
        found_pdf = False
        for f in os.listdir(BASE_DIR):
            if f.lower().endswith('.pdf'):
                print(f"  - {f}")
                found_pdf = True
        if not found_pdf:
            print("  (无)")
            return

    # 初始化 OCR 模型
    ocr = init_ocr_model(DET_MODEL_PATH, REC_MODEL_PATH)

    # 处理 PDF
    results = process_pdf(PDF_PATH, ocr)

    print("\n处理完成！")


if __name__ == "__main__":
    main()
