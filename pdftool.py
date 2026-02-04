"""
========================================================
PaddleOCR 图形化识别工具
========================================================

功能说明：
    提供图形化界面，支持选择 PDF 或图片文件进行 OCR 识别。
    自动加载本地模型，识别完成后自动打开结果。

模型路径：
    - 检测模型：./testmodel/PP-OCRv5_mobile_det_infer
    - 识别模型：./testmodel/PP-OCRv5_mobile_rec_infer

运行方式：
    python pdftool.py
========================================================
"""

import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from paddleocr import PaddleOCR


def open_file(file_path):
    """跨平台打开文件"""
    try:
        if sys.platform == 'win32':
            os.startfile(file_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.call(['open', file_path])
        else:  # Linux
            subprocess.call(['xdg-open', file_path])
    except Exception as e:
        print(f"无法打开文件 {file_path}: {e}")


def init_ocr_model(det_model_path, rec_model_path):
    """初始化 PaddleOCR 模型"""
    print("正在初始化 OCR 模型...")
    ocr = PaddleOCR(
        text_detection_model_name="PP-OCRv5_mobile_det",
        text_recognition_model_name="PP-OCRv5_mobile_rec",
        text_detection_model_dir=det_model_path,
        text_recognition_model_dir=rec_model_path,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False
    )
    print("OCR 模型初始化完成")
    return ocr


def process_file(file_path, ocr, output_dir="output", progress_callback=None):
    """
    处理文件（PDF 或图片），进行 OCR 识别

    Args:
        file_path: 文件路径
        ocr: PaddleOCR 实例
        output_dir: 输出目录
        progress_callback: 进度回调函数
    """
    os.makedirs(output_dir, exist_ok=True)

    print(f"正在处理文件: {file_path}")

    if progress_callback:
        progress_callback("正在加载文件...")

    # 执行 OCR 识别
    result = ocr.predict(input=file_path)

    # 保存结果
    page_num = 1
    all_text = []
    first_result_dir = None

    for res in result:
        if progress_callback:
            progress_callback(f"正在处理第 {page_num}/{len(result)} 页...")

        # 为每页创建单独的文件夹
        page_dir = os.path.join(output_dir, f"page_{page_num:03d}_result")
        os.makedirs(page_dir, exist_ok=True)

        # 保存第一次的结果目录（用于后续自动打开）
        if first_result_dir is None:
            first_result_dir = page_dir

        # 保存可视化图像
        res.save_to_img(page_dir)

        # 保存 JSON 结果
        res.save_to_json(page_dir)

        # 保存文本结果
        texts = res.get('rec_texts', [])
        txt_path = os.path.join(page_dir, f"page_{page_num:03d}_result.txt")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(texts))

        all_text.extend(texts)
        page_num += 1

    return first_result_dir, all_text


class OCRApp:
    """OCR 图形化应用"""

    def __init__(self, root):
        self.root = root
        self.root.title("PaddleOCR 文字识别工具")
        self.root.geometry("600x450")

        # 模型路径
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.det_model_path = os.path.join(self.base_dir, "testmodel", "PP-OCRv5_mobile_det_infer")
        self.rec_model_path = os.path.join(self.base_dir, "testmodel", "PP-OCRv5_mobile_rec_infer")

        self.ocr = None
        self.selected_file = None

        self.setup_ui()

    def setup_ui(self):
        """设置界面"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="PaddleOCR 文字识别工具",
            font=("Microsoft YaHei", 18, "bold")
        )
        title_label.pack(pady=20)

        # 模型状态
        self.model_status_label = tk.Label(
            self.root,
            text=f"检测模型: {os.path.basename(self.det_model_path)}",
            font=("Microsoft YaHei", 9),
            fg="gray"
        )
        self.model_status_label.pack(pady=5)

        self.model_status_label2 = tk.Label(
            self.root,
            text=f"识别模型: {os.path.basename(self.rec_model_path)}",
            font=("Microsoft YaHei", 9),
            fg="gray"
        )
        self.model_status_label2.pack(pady=5)

        # 文件选择区域
        file_frame = tk.Frame(self.root)
        file_frame.pack(pady=20)

        tk.Button(
            file_frame,
            text="📁 选择 PDF 文件",
            font=("Microsoft YaHei", 11),
            command=self.select_pdf,
            width=20,
            height=2
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            file_frame,
            text="🖼️ 选择图片文件",
            font=("Microsoft YaHei", 11),
            command=self.select_image,
            width=20,
            height=2
        ).grid(row=0, column=1, padx=10)

        # 选中的文件显示
        self.file_label = tk.Label(
            self.root,
            text="未选择文件",
            font=("Microsoft YaHei", 10),
            fg="blue",
            wraplength=500
        )
        self.file_label.pack(pady=10)

        # 进度条
        self.progress_label = tk.Label(
            self.root,
            text="",
            font=("Microsoft YaHei", 10)
        )
        self.progress_label.pack(pady=5)

        self.progress_bar = ttk.Progressbar(
            self.root,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.pack(pady=5)

        # 开始按钮
        self.start_button = tk.Button(
            self.root,
            text="🚀 开始识别",
            font=("Microsoft YaHei", 12, "bold"),
            command=self.start_ocr,
            state=tk.DISABLED,
            width=15,
            height=2,
            bg="#4CAF50",
            fg="white"
        )
        self.start_button.pack(pady=20)

        # 提示信息
        tip_label = tk.Label(
            self.root,
            text="支持格式: PDF, JPG, PNG, BMP",
            font=("Microsoft YaHei", 9),
            fg="gray"
        )
        tip_label.pack(pady=10)

    def update_progress(self, message):
        """更新进度"""
        self.progress_label.config(text=message)
        self.root.update()

    def select_pdf(self):
        """选择 PDF 文件"""
        file_path = filedialog.askopenfilename(
            title="选择 PDF 文件",
            filetypes=[("PDF 文件", "*.pdf"), ("所有文件", "*.*")]
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"已选择: {os.path.basename(file_path)}\n{file_path}")
            self.start_button.config(state=tk.NORMAL)

    def select_image(self):
        """选择图片文件"""
        file_path = filedialog.askopenfilename(
            title="选择图片文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.gif *.tiff"),
                ("所有文件", "*.*")
            ]
        )
        if file_path:
            self.selected_file = file_path
            self.file_label.config(text=f"已选择: {os.path.basename(file_path)}\n{file_path}")
            self.start_button.config(state=tk.NORMAL)

    def start_ocr(self):
        """开始 OCR 识别"""
        if not self.selected_file:
            messagebox.showerror("错误", "请先选择文件！")
            return

        # 禁用开始按钮
        self.start_button.config(state=tk.DISABLED)

        # 在新线程中执行 OCR
        import threading
        thread = threading.Thread(target=self._run_ocr)
        thread.start()

    def _run_ocr(self):
        """执行 OCR 识别（在后台线程中）"""
        try:
            # 初始化模型
            if self.ocr is None:
                self.update_progress("正在初始化 OCR 模型，请稍候...")
                self.progress_bar.start(10)
                self.ocr = init_ocr_model(self.det_model_path, self.rec_model_path)
                self.progress_bar.stop()

            # 处理文件
            self.update_progress("正在识别文字，请稍候...")
            self.progress_bar.start(10)

            result_dir, all_text = process_file(
                self.selected_file,
                self.ocr,
                progress_callback=self.update_progress
            )

            self.progress_bar.stop()

            # 在主线程中显示结果
            self.root.after(0, lambda: self._show_result(result_dir, all_text))

        except Exception as e:
            self.progress_bar.stop()
            self.root.after(0, lambda: messagebox.showerror("错误", f"识别失败: {str(e)}"))
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))

    def _show_result(self, result_dir, all_text):
        """显示结果并打开文件"""
        self.update_progress("识别完成！")

        # 显示统计信息
        msg = f"识别完成！\n\n共识别 {len(all_text)} 行文字\n结果保存在: {result_dir}"
        messagebox.showinfo("识别完成", msg)

        # 自动打开结果文件夹
        try:
            # 打开文件夹
            if sys.platform == 'win32':
                subprocess.call(['explorer', os.path.dirname(result_dir)])
            else:
                open_file(result_dir)
        except:
            pass

        # 尝试打开可视化图片和文本文件
        try:
            # 查找图片文件
            for file in os.listdir(result_dir):
                if file.endswith('_ocr_res_img.png'):
                    img_path = os.path.join(result_dir, file)
                    open_file(img_path)
                    break

            # 查找文本文件
            for file in os.listdir(result_dir):
                if file.endswith('.txt'):
                    txt_path = os.path.join(result_dir, file)
                    open_file(txt_path)
                    break
        except Exception as e:
            print(f"打开结果文件时出错: {e}")

        # 重置界面
        self.start_button.config(state=tk.NORMAL)
        self.progress_label.config(text="")


def main():
    """主函数"""
    # 检查模型是否存在
    base_dir = os.path.dirname(os.path.abspath(__file__))
    det_model_path = os.path.join(base_dir, "testmodel", "PP-OCRv5_mobile_det_infer")
    rec_model_path = os.path.join(base_dir, "testmodel", "PP-OCRv5_mobile_rec_infer")

    if not os.path.exists(det_model_path):
        print(f"错误: 检测模型不存在: {det_model_path}")
        return

    if not os.path.exists(rec_model_path):
        print(f"错误: 识别模型不存在: {rec_model_path}")
        return

    # 创建 GUI 应用
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
