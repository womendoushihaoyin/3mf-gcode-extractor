#!/usr/bin/env python3
"""
3MF Gcode批量提取工具
从.3mf文件中批量提取gcode文件
"""

import os
import zipfile
import threading
import queue
from pathlib import Path
from tkinter import Tk, Frame, Label, Button, Listbox, Scrollbar, filedialog, messagebox
from tkinter import ttk
from tkinterdnd2 import DND_FILES, TkinterDnD


class GcodeExtractor:
    """核心提取逻辑"""

    @staticmethod
    def validate_3mf(file_path):
        """验证文件是否为有效的.3mf文件"""
        if not file_path.endswith('.3mf'):
            return False

        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # 检查是否包含Metadata目录
                namelist = zf.namelist()
                return any(name.startswith('Metadata/') for name in namelist)
        except (zipfile.BadZipFile, OSError):
            return False

    @staticmethod
    def get_unique_folder_name(base_path):
        """处理文件夹名冲突，自动重命名"""
        if not os.path.exists(base_path):
            return base_path

        i = 1
        while os.path.exists(f"{base_path}_{i}"):
            i += 1
        return f"{base_path}_{i}"

    @staticmethod
    def extract_from_3mf(file_path, output_dir):
        """从.3mf文件提取gcode"""
        result = {"success": False, "files": [], "error": None}

        try:
            # 创建输出文件夹（以.3mf文件名命名）
            base_name = Path(file_path).stem
            folder_path = os.path.join(output_dir, base_name)
            folder_path = GcodeExtractor.get_unique_folder_name(folder_path)
            os.makedirs(folder_path, exist_ok=True)

            # 解压并提取gcode
            with zipfile.ZipFile(file_path, 'r') as zf:
                gcode_files = [f for f in zf.namelist() if f.startswith('Metadata/') and f.endswith('.gcode')]

                if not gcode_files:
                    result["error"] = "未找到gcode文件"
                    return result

                for gcode_file in gcode_files:
                    # 提取文件名（去掉Metadata/路径）
                    file_name = os.path.basename(gcode_file)
                    zf.extract(gcode_file, folder_path)
                    # 移动到文件夹根目录
                    src = os.path.join(folder_path, gcode_file)
                    dst = os.path.join(folder_path, file_name)
                    os.rename(src, dst)
                    result["files"].append(file_name)

                # 清理Metadata目录
                metadata_dir = os.path.join(folder_path, 'Metadata')
                if os.path.exists(metadata_dir):
                    os.rmdir(metadata_dir)

            result["success"] = True
        except (zipfile.BadZipFile, OSError, PermissionError) as e:
            result["error"] = str(e)

        return result


class ExtractorApp:
    """主窗口应用"""

    def __init__(self, root):
        self.root = root
        self.root.title("3MF Gcode提取工具")
        self.root.geometry("600x400")

        self.file_list = []
        self.output_dir = os.getcwd()
        self.progress_queue = queue.Queue()
        self.is_processing = False

        self.setup_ui()
        self.update_progress()

    def setup_ui(self):
        """构建界面"""
        # 拖拽区域
        drop_frame = Frame(self.root, bg="#e0e0e0", height=100)
        drop_frame.pack(fill="x", padx=10, pady=10)
        drop_frame.pack_propagate(False)

        drop_label = Label(drop_frame, text="拖拽.3mf文件到这里", bg="#e0e0e0", font=("Arial", 12))
        drop_label.pack(expand=True)

        # 注册拖拽
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)

        # 文件列表
        list_frame = Frame(self.root)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")

        self.listbox = Listbox(list_frame, yscrollcommand=scrollbar.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox.yview)

        # 输出目录
        dir_frame = Frame(self.root)
        dir_frame.pack(fill="x", padx=10, pady=5)

        Label(dir_frame, text="输出目录:").pack(side="left")
        self.dir_label = Label(dir_frame, text=self.output_dir, fg="blue")
        self.dir_label.pack(side="left", padx=5)
        Button(dir_frame, text="选择", command=self.select_output).pack(side="left")

        # 进度和按钮
        bottom_frame = Frame(self.root)
        bottom_frame.pack(fill="x", padx=10, pady=10)

        self.progress_label = Label(bottom_frame, text="就绪")
        self.progress_label.pack(side="left")

        self.start_btn = Button(bottom_frame, text="开始提取", command=self.start_extraction)
        self.start_btn.pack(side="right")

    def on_drop(self, event):
        """处理拖拽事件"""
        files = self.root.tk.splitlist(event.data)
        for file_path in files:
            file_path = file_path.strip('{}')
            if os.path.isfile(file_path) and GcodeExtractor.validate_3mf(file_path):
                if file_path not in self.file_list:
                    self.file_list.append(file_path)
                    self.listbox.insert("end", os.path.basename(file_path))
            elif os.path.isdir(file_path):
                # 递归扫描文件夹
                for root, _, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        if GcodeExtractor.validate_3mf(full_path) and full_path not in self.file_list:
                            self.file_list.append(full_path)
                            self.listbox.insert("end", os.path.basename(full_path))

    def select_output(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(initialdir=self.output_dir)
        if directory:
            self.output_dir = directory
            self.dir_label.config(text=directory)

    def start_extraction(self):
        """启动提取线程"""
        if self.is_processing:
            return

        if not self.file_list:
            messagebox.showwarning("警告", "请先添加.3mf文件")
            return

        self.is_processing = True
        self.start_btn.config(state="disabled")
        self.progress_label.config(text="处理中...")

        thread = threading.Thread(target=self.extract_worker, daemon=True)
        thread.start()

    def extract_worker(self):
        """后台提取线程"""
        total = len(self.file_list)
        success_count = 0
        error_count = 0

        for i, file_path in enumerate(self.file_list):
            self.progress_queue.put(("progress", f"处理中 {i+1}/{total}: {os.path.basename(file_path)}"))

            result = GcodeExtractor.extract_from_3mf(file_path, self.output_dir)

            if result["success"]:
                success_count += 1
            else:
                error_count += 1
                self.progress_queue.put(("error", f"失败: {os.path.basename(file_path)} - {result['error']}"))

        self.progress_queue.put(("done", f"完成! 成功: {success_count}, 失败: {error_count}"))

    def update_progress(self):
        """轮询队列更新UI"""
        try:
            while True:
                msg_type, msg = self.progress_queue.get_nowait()

                if msg_type == "progress":
                    self.progress_label.config(text=msg)
                elif msg_type == "error":
                    self.listbox.insert("end", f"❌ {msg}")
                elif msg_type == "done":
                    self.progress_label.config(text=msg)
                    self.start_btn.config(state="normal")
                    self.is_processing = False
                    messagebox.showinfo("完成", msg)
        except queue.Empty:
            pass

        self.root.after(100, self.update_progress)


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = ExtractorApp(root)
    root.mainloop()



