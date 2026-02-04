"""
========================================================
PaddleOCR Kivy 移动端应用
========================================================

功能说明：
    基于 Kivy 框架的移动端 OCR 识别工具，支持编译为 Android APK。
    支持选择 PDF 或图片文件进行 OCR 识别。

模型路径：
    - 检测模型：./testmodel/PP-OCRv5_mobile_det_infer
    - 识别模型：./testmodel/PP-OCRv5_mobile_rec_infer

运行方式：
    Python: python pdftool_kivy.py
    Android: 使用 buildozer 编译 APK 后安装
========================================================
"""

import os
import sys
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window

# 设置窗口大小（仅在桌面端有效）
Window.size = (dp(400), dp(600))

# Android 平台检测
IS_ANDROID = False
try:
    from kivy.utils import platform
    IS_ANDROID = platform == 'android'
except:
    pass

# Android 权限请求
if IS_ANDROID:
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

    # 请求存储权限
    request_permissions([Permission.READ_EXTERNAL_STORAGE,
                        Permission.WRITE_EXTERNAL_STORAGE])


def get_asset_path(relative_path):
    """
    获取资源文件路径（支持 Android assets）

    Args:
        relative_path: 相对路径

    Returns:
        实际文件路径
    """
    if IS_ANDROID:
        # Android 环境，使用 assets 路径
        from kivy.utils import get_asset_path
        return get_asset_path(relative_path)
    else:
        # 桌面环境，使用相对路径
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, relative_path)


def get_user_data_dir():
    """
    获取用户数据目录

    Returns:
        用户数据目录路径
    """
    if IS_ANDROID:
        from android.storage import primary_external_storage_path
        return os.path.join(primary_external_storage_path(), 'PaddleOCR')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')


def init_ocr_model(det_model_path, rec_model_path):
    """
    初始化 PaddleOCR 模型

    Args:
        det_model_path: 检测模型路径
        rec_model_path: 识别模型路径

    Returns:
        PaddleOCR 实例
    """
    print("正在初始化 OCR 模型...")
    from paddleocr import PaddleOCR

    ocr = PaddleOCR(
        text_detection_model_name="PP-OCRv5_mobile_det",
        text_recognition_model_name="PP-OCRv5_mobile_rec",
        text_detection_model_dir=det_model_path,
        text_recognition_model_dir=rec_model_path,
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        show_log=False  # 减少日志输出
    )
    print("OCR 模型初始化完成")
    return ocr


def process_file(file_path, ocr, output_dir, progress_callback=None):
    """
    处理文件（PDF 或图片），进行 OCR 识别

    Args:
        file_path: 文件路径
        ocr: PaddleOCR 实例
        output_dir: 输出目录
        progress_callback: 进度回调函数

    Returns:
        (结果目录, 所有文本行列表)
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

        # 保存第一次的结果目录
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


class MainScreen(BoxLayout):
    """主界面布局"""

    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app = app_instance
        self.orientation = 'vertical'
        self.padding = dp(20)
        self.spacing = dp(15)

        # 应用状态
        self.ocr = None
        self.selected_file = None

        # 模型路径
        if IS_ANDROID:
            # Android: 模型需要从 assets 复制到应用目录
            self.det_model_path = None  # 将在初始化时设置
            self.rec_model_path = None
        else:
            # 桌面: 直接使用本地路径
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.det_model_path = os.path.join(base_dir, "testmodel", "PP-OCRv5_mobile_det_infer")
            self.rec_model_path = os.path.join(base_dir, "testmodel", "PP-OCRv5_mobile_rec_infer")

        self._setup_ui()

    def _setup_ui(self):
        """设置界面"""
        # 标题
        title_label = Label(
            text='PaddleOCR 文字识别',
            font_size=dp(22),
            size_hint_y=None,
            height=dp(60),
            bold=True
        )
        self.add_widget(title_label)

        # 模型状态标签
        self.model_status_label = Label(
            text='模型: PP-OCRv5 Mobile',
            font_size=dp(12),
            size_hint_y=None,
            height=dp(40),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(self.model_status_label)

        # 文件选择区域
        file_box = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(60),
            spacing=dp(10)
        )

        self.pdf_button = Button(
            text='选择 PDF',
            font_size=dp(14),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.pdf_button.bind(on_press=self.select_pdf)
        file_box.add_widget(self.pdf_button)

        self.image_button = Button(
            text='选择图片',
            font_size=dp(14),
            background_color=(0.2, 0.6, 1, 1)
        )
        self.image_button.bind(on_press=self.select_image)
        file_box.add_widget(self.image_button)

        self.add_widget(file_box)

        # 选中的文件显示
        self.file_label = Label(
            text='未选择文件',
            font_size=dp(12),
            size_hint_y=None,
            height=dp(60),
            color=(0, 0.5, 1, 1),
            text_size=(dp(380), None)
        )
        self.add_widget(self.file_label)

        # 进度标签
        self.progress_label = Label(
            text='',
            font_size=dp(12),
            size_hint_y=None,
            height=dp(30)
        )
        self.add_widget(self.progress_label)

        # 进度条
        self.progress_bar = ProgressBar(
            size_hint_y=None,
            height=dp(20),
            value=0,
            max=100
        )
        self.add_widget(self.progress_bar)

        # 开始按钮
        self.start_button = Button(
            text='开始识别',
            font_size=dp(16),
            size_hint_y=None,
            height=dp(60),
            background_color=(0.3, 0.8, 0.4, 1),
            disabled=True
        )
        self.start_button.bind(on_press=self.start_ocr)
        self.add_widget(self.start_button)

        # 提示信息
        tip_label = Label(
            text='支持格式: PDF, JPG, PNG, BMP',
            font_size=dp(10),
            size_hint_y=None,
            height=dp(40),
            color=(0.5, 0.5, 0.5, 1)
        )
        self.add_widget(tip_label)

    def select_pdf(self, instance):
        """选择 PDF 文件"""
        if IS_ANDROID:
            self._select_file_android(['application/pdf'])
        else:
            self._select_file_desktop([('PDF 文件', '*.pdf')])

    def select_image(self, instance):
        """选择图片文件"""
        if IS_ANDROID:
            self._select_file_android(['image/*'])
        else:
            self._select_file_desktop([
                ('图片文件', '*.jpg;*.jpeg;*.png;*.bmp;*.gif'),
                ('所有文件', '*.*')
            ])

    def _select_file_android(self, mime_types):
        """Android 文件选择"""
        from plyer import filechooser

        try:
            file_path = filechooser.open_file(
                title="选择文件",
                filters=[{"extensions": ["*"]}]
            )
            if file_path and len(file_path) > 0:
                self.selected_file = file_path[0]
                self._on_file_selected()
        except Exception as e:
            self._show_popup('错误', f'文件选择失败: {str(e)}')

    def _select_file_desktop(self, filetypes):
        """桌面端文件选择"""
        from tkinter import filedialog as tk_filedialog
        import tkinter as tk

        # 创建隐藏的 tkinter 窗口
        root = tk.Tk()
        root.withdraw()

        file_path = tk_filedialog.askopenfilename(
            title="选择文件",
            filetypes=filetypes
        )
        root.destroy()

        if file_path:
            self.selected_file = file_path
            self._on_file_selected()

    def _on_file_selected(self):
        """文件选择完成后的处理"""
        filename = os.path.basename(self.selected_file)
        self.file_label.text = f'已选择:\n{filename}'
        self.start_button.disabled = False

    def start_ocr(self, instance):
        """开始 OCR 识别"""
        if not self.selected_file:
            self._show_popup('错误', '请先选择文件！')
            return

        # 禁用按钮
        self.start_button.disabled = True
        self.pdf_button.disabled = True
        self.image_button.disabled = True

        # 在后台线程执行 OCR
        thread = threading.Thread(target=self._run_ocr)
        thread.daemon = True
        thread.start()

    def _run_ocr(self):
        """执行 OCR 识别（在后台线程中）"""
        try:
            # 初始化模型
            if self.ocr is None:
                self._update_progress("正在初始化 OCR 模型，请稍候...", 10)

                # 检查模型文件
                if IS_ANDROID:
                    # Android: 从 assets 复制模型文件
                    self._setup_android_models()

                self.ocr = init_ocr_model(self.det_model_path, self.rec_model_path)

            # 处理文件
            self._update_progress("正在识别文字，请稍候...", 50)

            output_dir = get_user_data_dir()
            result_dir, all_text = process_file(
                self.selected_file,
                self.ocr,
                output_dir,
                progress_callback=lambda msg: Clock.schedule_once(
                    lambda dt: self._update_progress(msg, 70)
                )
            )

            # 显示结果
            Clock.schedule_once(lambda dt: self._show_result(result_dir, all_text))

        except Exception as e:
            import traceback
            error_msg = f"识别失败: {str(e)}\n{traceback.format_exc()}"
            Clock.schedule_once(lambda dt: self._show_popup('错误', error_msg))
            Clock.schedule_once(lambda dt: self._reset_ui(True))

    def _setup_android_models(self):
        """设置 Android 模型文件（从 assets 复制）"""
        from kivy.utils import get_asset_path
        import shutil

        # 目标目录
        user_data_dir = get_user_data_dir()
        det_model_dir = os.path.join(user_data_dir, 'PP-OCRv5_mobile_det_infer')
        rec_model_dir = os.path.join(user_data_dir, 'PP-OCRv5_mobile_rec_infer')

        # 如果已存在则跳过
        if os.path.exists(det_model_dir) and os.path.exists(rec_model_dir):
            self.det_model_path = det_model_dir
            self.rec_model_path = rec_model_dir
            return

        # 复制检测模型
        os.makedirs(det_model_dir, exist_ok=True)
        for filename in ['inference.pdiparams', 'inference.pdmodel', 'inference.yml']:
            src = get_asset_path(f'models/PP-OCRv5_mobile_det_infer/{filename}')
            if os.path.exists(src):
                shutil.copy(src, os.path.join(det_model_dir, filename))

        # 复制识别模型
        os.makedirs(rec_model_dir, exist_ok=True)
        for filename in ['inference.pdiparams', 'inference.pdmodel', 'inference.yml']:
            src = get_asset_path(f'models/PP-OCRv5_mobile_rec_infer/{filename}')
            if os.path.exists(src):
                shutil.copy(src, os.path.join(rec_model_dir, filename))

        self.det_model_path = det_model_dir
        self.rec_model_path = rec_model_dir

    def _update_progress(self, message, value):
        """更新进度"""
        self.progress_label.text = message
        self.progress_bar.value = value

    def _show_result(self, result_dir, all_text):
        """显示结果"""
        self._update_progress("识别完成！", 100)
        self._reset_ui(False)

        msg = f'识别完成！\n\n共识别 {len(all_text)} 行文字\n结果保存在:\n{result_dir}'
        self._show_popup('识别完成', msg)

    def _reset_ui(self, enable_button):
        """重置界面"""
        self.start_button.disabled = not enable_button
        self.pdf_button.disabled = False
        self.image_button.disabled = False

    def _show_popup(self, title, message):
        """显示弹窗"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        label = Label(
            text=message,
            font_size=dp(14),
            text_size=(dp(350), None)
        )
        content.add_widget(label)

        close_btn = Button(
            text='确定',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(14)
        )

        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.9, 0.5)
        )

        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)

        popup.open()


class OCRKivyApp(App):
    """Kivy OCR 应用主类"""

    def build(self):
        """构建应用"""
        self.title = 'PaddleOCR 文字识别'
        return MainScreen(self)

    def on_start(self):
        """应用启动时的处理"""
        print("应用启动")

        # 检查模型文件（桌面端）
        if not IS_ANDROID:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            det_model_path = os.path.join(base_dir, "testmodel", "PP-OCRv5_mobile_det_infer")
            rec_model_path = os.path.join(base_dir, "testmodel", "PP-OCRv5_mobile_rec_infer")

            if not os.path.exists(det_model_path):
                print(f"警告: 检测模型不存在: {det_model_path}")
            if not os.path.exists(rec_model_path):
                print(f"警告: 识别模型不存在: {rec_model_path}")

    def on_stop(self):
        """应用停止时的处理"""
        print("应用停止")


def main():
    """主函数"""
    OCRKivyApp().run()


if __name__ == "__main__":
    main()
