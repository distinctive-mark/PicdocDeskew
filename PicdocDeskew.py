import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFile, ImageDraw, ImageGrab
import math
import os
import re
import threading
import cv2
import numpy as np
import locale
import gettext
import webbrowser
import shutil

# 常量定义
DEFAULT_WINDOW_SIZE = "900x900"
THUMBNAIL_SIZE = 80
MAX_ZOOM_LEVEL = 10.0
MIN_ZOOM_LEVEL = 0.1
ZOOM_FACTOR = 1.2
DEFAULT_BG_COLOR = (255, 255, 255)
SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif', 
                        '.webp', '.ico', '.ppm', '.pgm', '.pbm')
CROSSHAIR_WARNING_THRESHOLD = 10  # 角度阈值，超过10度弹出警告

# 尝试导入 tkinterdnd2
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("警告: 未找到 tkinterdnd2 库，拖拽功能将不可用。")
    print("请安装: pip install tkinterdnd2")


class Internationalization:
    """国际化管理类"""
    
    def __init__(self):
        self.current_language = self.detect_system_language()
        self.translations = self.load_translations()
        
    def detect_system_language(self):
        """检测系统语言"""
        try:
            # 使用 locale 模块
            try:
                # 首先尝试新的方法
                system_lang = locale.getlocale()[0]
            except AttributeError:
                # 回退到旧方法（用于Python旧版本）
                system_lang = locale.getdefaultlocale()[0]
            
            if system_lang and 'zh' in system_lang.lower():
                return 'zh_CN'
            else:
                return 'en_US'
        except:
            return 'en_US'
    
    def load_translations(self):
        """加载翻译字典"""
        translations = {
            'zh_CN': {
                # 窗口标题
                'window_title': "图文纠偏",
                
                # 状态信息
                'select_folder_or_drag': "请选择文件夹或打开图片",
                'select_folder_only': "请选择文件夹（拖拽功能需要安装tkinterdnd2）",
                'auto_deskewing': "正在自动纠偏当前图片...",
                'auto_deskew_complete': "自动纠偏完成，旋转角度: {:.2f}°",
                'no_rotation_needed': "自动纠偏完成，无需旋转",
                'batch_deskewing': "正在批量纠偏...",
                'batch_complete': "批量纠偏完成，共处理 {} 张图片",
                'batch_stopped': "批量纠偏已停止，已处理 {}/{} 张图片",
                'current_image': "当前图片: {}",
                'modified': " [已修改]",
                'current_angle': "当前角度: {:.2f}°",
                'single_rotation': "单次旋转: {}°",
                'bg_color': "填充色: {},{},{}",
                'size': "尺寸: {}",
                'size_locked': " 已锁定",
                'hough_method': "霍夫方法: {}",
                'batch_status': " (批量纠偏中...)",
                
                # 按钮文本
                'auto_deskew': "📄 自动纠偏 (V)",
                'batch_deskew': "📄 批量纠偏 (B)",
                'select_folder': "选择文件夹 (O)",
                'open_images': "打开图片 (I)",
                'rotate_left': "↺ (Q)",
                'zoom_in': "🔍+ (W)",
                'rotate_right': "↻ (E)",
                'previous': "⬅ (A)",
                'zoom_out': "🔍- (S)",
                'next': "➡ (D)",
                'reset': "重置图片 (R)",
                'lock_size': "锁定尺寸 (L)",
                
                # 提示信息
                'drag_prompt': "拖拽图片或文件夹至此",
                'shortcuts_prompt': (" L: 锁定尺寸(保存前裁切至原尺寸) \n\n P: 从光标处获得填充色 \n\n 左键单击: 两点调平 \n\n "
                                   "滚轮单击: 重置缩放 \n\n A/D: 保存修改并切换 \n\n Q/E: 旋转图片内容 \n\n "
                                   "数字键+回车: 单次旋转角度 \n\n 删除键: 清空图片(初始化) \n\n V: 自动纠偏当前图片 \n\n "
                                   "B: 批量自动纠偏 \n\n H: 切换霍夫方法 \n\n Tab: 切换语言 \n\n F1: 源代码详情"),
                
                # 警告和错误信息
                'no_images_warning': "没有可纠偏的图片",
                'batch_confirm': "将从当前图片开始，对剩余 {} 张图片进行批量自动纠偏，是否继续？",
                'crop_warning': "警告",
                'crop_warning_detail': "当前旋转角度 {:.1f}° 较大，裁切可能会丢失部分内容。",
                'save_changes': "图片 {} 已被修改，是否保存更改？",
                'no_images_found': "文件夹中没有找到图片文件",
                'no_valid_images': "没有找到有效的图片文件",
                'image_error': "无法打开图片 {}: {}",
                'image_format_error': "\n这可能是因为文件格式不受支持或文件已损坏。",
                
                # 点选择状态
                'select_second_point': "请选择要与点A调平的点 (按Esc取消)",
                
                # 角度输入
                'angle_input': "输入角度: {}° (按回车确认，Esc取消，退格修改)",
                'invalid_input': "无效输入",
                
                # 霍夫方法名称
                'hough_standard': "标准",
                'hough_probabilistic': "概率",
                'hough_optimized': "优化",
                
                # 文件对话框
                'select_folder_title': "选择文件夹",
                'open_images_title': "打开图片",
                'all_image_files': "所有图片文件",
                'png_files': "PNG 文件",
                'jpeg_files': "JPEG 文件",
                'bitmap_files': "位图文件",
                'gif_files': "GIF 文件",
                'tiff_files': "TIFF 文件",
                'all_files': "所有文件"
            },
            'en_US': {
                # Window title
                'window_title': "PicdocDeskew",
                
                # Status messages
                'select_folder_or_drag': "Please select folder or open pictures",
                'select_folder_only': "Please select folder (drag & drop requires tkinterdnd2)",
                'auto_deskewing': "Auto-deskewing current picture...",
                'auto_deskew_complete': "Auto-deskewion complete, rotation angle: {:.2f}°",
                'no_rotation_needed': "Auto-deskewion complete, no rotation needed",
                'batch_deskewing': "Batch deskewing...",
                'batch_complete': "Batch deskewion complete, processed {} pictures",
                'batch_stopped': "Batch deskewion stopped, processed {}/{} pictures",
                'current_image': "Current picture: {}",
                'modified': " [Modified]",
                'current_angle': "Current angle: {:.2f}°",
                'single_rotation': "Single rotation: {}°",
                'bg_color': "Background: {},{},{}",
                'size': "Size: {}",
                'size_locked': " Locked",
                'hough_method': "Hough method: {}",
                'batch_status': " (Batch deskewing...)",
                
                # Button texts
                'auto_deskew': "📄 Auto Deskew (V)",
                'batch_deskew': "📄 Batch Deskew (B)",
                'select_folder': "Select Folder (O)",
                'open_images': "Open Pictures (I)",
                'rotate_left': "↺ (Q)",
                'zoom_in': "🔍+ (W)",
                'rotate_right': "↻ (E)",
                'previous': "⬅ (A)",
                'zoom_out': "🔍- (S)",
                'next': "➡ (D)",
                'reset': "Reset Picture (R)",
                'lock_size': "Lock Size (L)",
                
                # Prompt messages
                'drag_prompt': "Drag pictures or folder here",
                'shortcuts_prompt': (" L: Lock size(crop to original before save) \n\n P: Pick background color \n\n LMB Click: Two-point deskewing \n\n "
                                   "MMB Click: Reset zoom \n\n A/D: Save and navigate \n\n Q/E: Rotate picture \n\n "
                                   "Num+Enter: Single rotation angle \n\n Delete: Reset software \n\n V: Auto deskew current \n\n "
                                   "B: Batch auto deskew \n\n H: Switch Hough method \n\n Tab: Switch language \n\n F1: Source Code Details"),
                
                # Warning and error messages
                'no_images_warning': "No pictures to deskew",
                'batch_confirm': "Start from current picture and batch auto-deskew remaining {} pictures?",
                'crop_warning': "Warning",
                'crop_warning_detail': "Current rotation angle {:.1f}° is large, cropping may lose content.",
                'save_changes': "Picture {} has been modified, save changes?",
                'no_images_found': "No picture files found in folder",
                'no_valid_images': "No valid picture files found",
                'image_error': "Cannot open picture {}: {}",
                'image_format_error': "\nThis may be due to unsupported format or corrupted file.",
                
                # Point selection status
                'select_second_point': "Select point to level with point A (Press Esc to cancel)",
                
                # Angle input
                'angle_input': "Input angle: {}° (Enter to confirm, Esc to cancel, Backspace to edit)",
                'invalid_input': "Invalid input",
                
                # Hough method names
                'hough_standard': "Standard",
                'hough_probabilistic': "Probabilistic",
                'hough_optimized': "Optimized",
                
                # File dialogs
                'select_folder_title': "Select Folder",
                'open_images_title': "Open Pictures",
                'all_image_files': "All picture files",
                'png_files': "PNG files",
                'jpeg_files': "JPEG files",
                'bitmap_files': "Bitmap files",
                'gif_files': "GIF files",
                'tiff_files': "TIFF files",
                'all_files': "All files"
            }
        }
        return translations
    
    def set_language(self, language_code):
        """设置语言"""
        if language_code in self.translations:
            self.current_language = language_code
    
    def get_text(self, key, *args):
        """获取翻译文本"""
        if self.current_language in self.translations and key in self.translations[self.current_language]:
            text = self.translations[self.current_language][key]
            if args:
                return text.format(*args)
            return text
        else:
            # 回退到英文
            if key in self.translations['en_US']:
                text = self.translations['en_US'][key]
                if args:
                    return text.format(*args)
                return text
            return key


class AutoDeskewer:
    """自动纠偏功能类 - 使用霍夫变换方法"""
    
    def __init__(self, app):
        self.app = app
        self.is_batch_deskewing = False
        self.stop_batch_deskewion = False
        self.hough_method = "optimized"  # 默认使用优化版霍夫变换
    
    def preprocess_image(self, pil_image):
        """预处理PIL图像：转灰度、二值化"""
        # 将PIL图像转换为OpenCV格式
        opencv_image = np.array(pil_image)
        if len(opencv_image.shape) == 3:
            if opencv_image.shape[2] == 4:  # RGBA转RGB
                opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGBA2RGB)
            opencv_image = cv2.cvtColor(opencv_image, cv2.COLOR_RGB2GRAY)
        
        _, binary = cv2.threshold(opencv_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        binary = 255 - binary  # 背景白色=255，文本黑色=0
        return binary
    
    def detect_angle_hough(self, binary, angle_range=(-30, 30), rho_resolution=1, theta_resolution=np.pi/180, threshold=100):
        """使用标准霍夫变换检测文本行角度"""
        # 边缘检测
        edges = cv2.Canny(binary, 50, 150, apertureSize=3)
        
        # 霍夫直线检测
        lines = cv2.HoughLines(edges, rho_resolution, theta_resolution, threshold)
        
        if lines is None:
            print("Hough transform detected no lines")
            return 0
        
        # 转换角度并筛选
        angles = []
        for line in lines:
            rho, theta = line[0]
            
            # 将theta转换为角度（度）
            angle_deg = np.degrees(theta) - 90  # 转换为水平线的角度
            
            # 调整角度到[-90, 90)范围
            if angle_deg < -90:
                angle_deg += 180
            elif angle_deg >= 90:
                angle_deg -= 180
                
            # 只保留在指定范围内的角度
            if angle_range[0] <= angle_deg <= angle_range[1]:
                angles.append(angle_deg)
        
        if not angles:
            print("No lines found in specified range")
            return 0
        
        # 使用直方图找到最集中的角度
        hist, bins = np.histogram(angles, bins=30, range=angle_range)
        peak_bin = np.argmax(hist)
        peak_angle = (bins[peak_bin] + bins[peak_bin+1]) / 2
        
        print(f"Standard Hough detected {len(angles)} lines")
        print(f"Most concentrated angle: {peak_angle:.2f}°")
        
        return peak_angle
    
    def detect_angle_hough_probabilistic(self, binary, angle_range=(-30, 30), threshold=50, min_line_length=50, max_line_gap=10):
        """使用概率霍夫变换检测文本行角度"""
        # 边缘检测
        edges = cv2.Canny(binary, 50, 150, apertureSize=3)
        
        # 概率霍夫直线检测（返回线段端点）
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold, 
                               minLineLength=min_line_length, maxLineGap=max_line_gap)
        
        if lines is None:
            print("Probabilistic Hough detected no lines")
            return 0
        
        # 计算每条线段的角度
        angles = []
        lengths = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 计算线段角度
            dx = x2 - x1
            dy = y2 - y1
            
            if dx == 0:  # 垂直线
                angle_deg = 90
            else:
                angle_rad = math.atan2(dy, dx)
                angle_deg = math.degrees(angle_rad)
                
            # 调整角度到[-90, 90)范围
            if angle_deg < -90:
                angle_deg += 180
            elif angle_deg >= 90:
                angle_deg -= 180
                
            # 只保留在指定范围内的角度
            if angle_range[0] <= angle_deg <= angle_range[1]:
                angles.append(angle_deg)
                # 计算线段长度作为权重
                length = math.sqrt(dx*dx + dy*dy)
                lengths.append(length)
        
        if not angles:
            print("No lines found in specified range")
            return 0
        
        # 使用加权平均（线段长度作为权重）
        total_length = sum(lengths)
        weighted_angle = sum(angle * length for angle, length in zip(angles, lengths)) / total_length
        
        print(f"Probabilistic Hough detected {len(angles)} line segments")
        print(f"Weighted average angle: {weighted_angle:.2f}°")
        
        return weighted_angle
    
    def detect_angle_hough_optimized(self, binary, angle_range=(-30, 30)):
        """优化版的霍夫变换角度检测"""
        h, w = binary.shape
        
        # 1. 预处理 - 使用形态学操作增强文本行
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 1))  # 水平核，增强水平特征
        enhanced = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 2. 边缘检测
        edges = cv2.Canny(enhanced, 50, 150, apertureSize=3)
        
        # 3. 概率霍夫变换，参数根据图像大小自适应
        min_line_length = max(50, w * 0.3)  # 最小线段长度为图像宽度的30%
        threshold = max(50, w * 0.1)  # 阈值根据图像宽度调整
        
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, int(threshold), 
                               minLineLength=int(min_line_length), maxLineGap=20)
        
        if lines is None:
            print("Hough transform detected no lines, trying lower threshold...")
            # 降低阈值再次尝试
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, int(threshold * 0.5), 
                                   minLineLength=int(min_line_length * 0.5), maxLineGap=30)
            
            if lines is None:
                print("Still no lines detected, returning 0 degrees")
                return 0
        
        # 4. 计算每条线段的角度和权重
        angles = []
        weights = []
        
        for line in lines:
            x1, y1, x2, y2 = line[0]
            
            # 计算线段角度
            dx = x2 - x1
            dy = y2 - y1
            
            if abs(dx) < 1:  # 接近垂直线
                continue
                
            angle_rad = math.atan2(dy, dx)
            angle_deg = math.degrees(angle_rad)
            
            # 调整角度到[-90, 90)范围
            if angle_deg < -90:
                angle_deg += 180
            elif angle_deg >= 90:
                angle_deg -= 180
                
            # 只保留在指定范围内的角度
            if angle_range[0] <= angle_deg <= angle_range[1]:
                # 计算线段长度和水平投影作为权重
                length = math.sqrt(dx*dx + dy*dy)
                horizontal_projection = abs(dx)  # 水平投影长度
                
                # 综合权重：长度 + 水平投影
                weight = length + horizontal_projection * 0.5
                
                angles.append(angle_deg)
                weights.append(weight)
        
        if not angles:
            print("No lines found in specified range")
            return 0
        
        # 5. 使用加权平均
        total_weight = sum(weights)
        weighted_angle = sum(angle * weight for angle, weight in zip(angles, weights)) / total_weight
        
        print(f"Optimized Hough detected {len(angles)} line segments")
        print(f"Weighted average angle: {weighted_angle:.2f}°")
        
        return weighted_angle
    
    def calculate_rotation_angle_by_two_points(self, point1, point2):
        """完全按照您提供的两点法计算旋转角度"""
        x1, y1 = point1
        x2, y2 = point2
        
        # 计算两点距离
        dx = x2 - x1
        dy = y2 - y1
        
        # 计算直线与水平线的夹角
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # 判断是水平矫正还是垂直矫正
        if abs(dx) > abs(dy):  # 横向距离大于纵向距离 - 水平矫正
            target_angle = angle_deg
        else:  # 纵向距离大于横向距离 - 垂直矫正
            if x1 > x2:  # 上点更靠右
                target_angle = -(90 - angle_deg)
            else:  # 下点更靠右
                target_angle = -(90 - angle_deg)
        
        return target_angle
    
    def set_hough_method(self, method):
        """设置霍夫变换方法"""
        valid_methods = ["standard", "probabilistic", "optimized"]
        if method in valid_methods:
            self.hough_method = method
            print(f"Switched to {method} Hough method")
        else:
            print(f"Invalid Hough method: {method}")
    
    def auto_deskew_image(self, pil_image):
        """自动纠偏单张图片 - 使用霍夫变换方法"""
        try:
            # 1. 预处理图像
            binary = self.preprocess_image(pil_image)
            h, w = binary.shape
            
            # 2. 使用霍夫变换检测角度
            detected_angle = 0
            if self.hough_method == "standard":
                detected_angle = self.detect_angle_hough(binary)
                method_name = "Standard Hough"
            elif self.hough_method == "probabilistic":
                detected_angle = self.detect_angle_hough_probabilistic(binary)
                method_name = "Probabilistic Hough"
            else:  # optimized
                detected_angle = self.detect_angle_hough_optimized(binary)
                method_name = "Optimized Hough"
            
            print(f"{method_name} detected angle: {detected_angle:.2f}°")
            
            # 3. 使用两点法计算旋转角度
            center_x, center_y = w // 2, h // 2
            distance = min(w, h) // 4
            
            angle_rad = math.radians(detected_angle)
            point1 = (
                int(center_x - distance * math.cos(angle_rad)),
                int(center_y - distance * math.sin(angle_rad))
            )
            point2 = (
                int(center_x + distance * math.cos(angle_rad)),
                int(center_y + distance * math.sin(angle_rad))
            )
            
            rotation_angle = self.calculate_rotation_angle_by_two_points(point1, point2)
            print(f"Two-point method calculated rotation angle: {rotation_angle:.2f}°")
            
            return rotation_angle
            
        except Exception as e:
            print(f"Error in auto-deskewion: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def auto_deskew_current(self):
        """自动纠偏当前图片"""
        if not self.app.image:
            messagebox.showwarning(
                self.app._("crop_warning"), 
                self.app._("no_images_warning")
            )
            return
        
        # 显示处理状态
        self.app.status_label.config(text=self.app._("auto_deskewing"))
        self.app.root.update()
        
        # 获取当前图片和背景色
        current_image = self.app.image
        bg_color = self.app.bg_color
        
        # 执行自动纠偏
        rotation_angle = self.auto_deskew_image(current_image)
        
        if abs(rotation_angle) > 0.1:  # 只有角度大于0.1度时才旋转
            # 使用图片转转的旋转逻辑
            self.app.rotate_by_angle(rotation_angle)
            self.app.status_label.config(text=self.app._("auto_deskew_complete", rotation_angle))
        else:
            self.app.status_label.config(text=self.app._("no_rotation_needed"))
    
    def batch_auto_deskew(self):
        """批量自动纠偏所有图片"""
        if not self.app.image_files:
            messagebox.showwarning(
                self.app._("crop_warning"), 
                self.app._("no_images_warning")
            )
            return
        
        if self.is_batch_deskewing:
            # 如果正在批量纠偏，则停止
            self.stop_batch_deskewion = True
            self.app.status_label.config(text=self.app._("batch_deskewing"))
            return
        
        # 确认对话框 - 修改提示信息
        total_count = len(self.app.image_files)
        start_index = self.app.current_image_index
        remaining_count = total_count - start_index
        
        if not messagebox.askyesno(
            self.app._("batch_deskew"), 
            self.app._("batch_confirm", remaining_count)
        ):
            return
        
        # 启动批量纠偏线程
        self.is_batch_deskewing = True
        self.stop_batch_deskewion = False
        threading.Thread(target=self._batch_deskew_thread, daemon=True).start()
    
    def _batch_deskew_thread(self):
        """批量纠偏线程 - 从当前图片开始"""
        total_count = len(self.app.image_files)
        start_index = self.app.current_image_index  # 从当前图片开始
        processed_count = 0
        
        for i in range(start_index, total_count):
            if self.stop_batch_deskewion:
                break
            
            # 切换到当前图片
            self.app.root.after(0, lambda idx=i: self._switch_to_image(idx))
            
            # 等待图片加载
            import time
            time.sleep(0.5)
            
            # 执行自动纠偏
            self.app.root.after(0, self._deskew_current_in_batch)
            
            # 等待纠偏完成
            time.sleep(0.5)
            
            # 保存并切换到下一张（模拟手动切换）
            self.app.root.after(0, self._save_and_next_in_batch)
            
            # 等待保存完成
            time.sleep(0.3)
            
            processed_count += 1
            
            # 更新状态 - 显示从当前开始的进度
            progress = f"Batch progress: {processed_count}/{total_count - start_index} (from #{start_index + 1})"
            self.app.root.after(0, lambda p=progress: self.app.status_label.config(text=p))
        
        # 批量纠偏完成
        self.app.root.after(0, self._batch_deskewion_finished, processed_count, total_count - start_index)
    
    def _switch_to_image(self, index):
        """切换到指定索引的图片，并确保缩略图可见"""
        self.app.current_image_index = index
        self.app.load_current_image()
        self.app.update_thumbnails_selection()
        
        # 立即滚动到当前缩略图，确保可见
        self.app.root.after(100, self.app.scroll_to_current_thumbnail)
    
    def _deskew_current_in_batch(self):
        """在批量纠偏中纠偏当前图片"""
        if self.app.image:
            current_image = self.app.image
            bg_color = self.app.bg_color
            
            rotation_angle = self.auto_deskew_image(current_image)
            
            if abs(rotation_angle) > 0.1:
                self.app.rotate_by_angle(rotation_angle)
    
    def _save_and_next_in_batch(self):
        """在批量纠偏中保存当前图片"""
        self.app.save_current_image_if_modified()
    
    def _batch_deskewion_finished(self, processed, batch_total):
        """批量纠偏完成处理"""
        self.is_batch_deskewing = False
        self.stop_batch_deskewion = False
        
        if processed == batch_total:
            self.app.status_label.config(text=self.app._("batch_complete", processed))
        else:
            self.app.status_label.config(text=self.app._("batch_stopped", processed, batch_total))


class ImageDisplayManager:
    """管理图片显示相关的功能 - 重新设计"""
    
    def __init__(self, app):
        self.app = app
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.is_panning = False
        self.zoom_mode = "height"

    def get_resample_method(self, original_pixels, display_pixels):
        """根据像素数量选择合适的重采样方法"""
        if display_pixels > original_pixels * 4:
            return Image.BILINEAR
        else:
            return Image.Resampling.LANCZOS

    def apply_zoom_mode(self):
        """应用当前缩放模式"""
        if not self.app.image:
            return
        self.zoom_level = 1.0
        self.pan_x = 0
        self.pan_y = 0

    def calculate_display_size(self, canvas_width, canvas_height, img_width, img_height):
        """计算图片显示尺寸"""
        if self.zoom_mode == "height":
            base_scale = canvas_height / img_height
        else:  # width mode
            base_scale = canvas_width / img_width
        
        scale = base_scale * self.zoom_level
        scale = min(scale, MAX_ZOOM_LEVEL)
        
        display_width = int(img_width * scale)
        display_height = int(img_height * scale)
        
        return display_width, display_height, scale, base_scale

    def update_display_info(self, img_x, img_y, display_width, display_height, 
                          scale, base_scale, canvas_width, canvas_height):
        """更新显示信息用于坐标转换"""
        self.display_info = {
            'scale': scale,
            'base_scale': base_scale,
            'offset_x': img_x - display_width // 2,
            'offset_y': img_y - display_height // 2,
            'canvas_width': canvas_width,
            'canvas_height': canvas_height,
            'display_width': display_width,
            'display_height': display_height,
            'img_x': img_x,
            'img_y': img_y
        }


class PointManager:
    """管理点选择和连线功能"""
    
    def __init__(self, app):
        self.app = app
        self.points = []
        self.drawing_line = False
        self.temp_line = None
        self.first_point = None
        self.original_points = []

    def reset_points(self):
        """重置所有点状态"""
        self.points = []
        self.drawing_line = False
        if self.temp_line:
            self.app.canvas.delete(self.temp_line)
            self.temp_line = None

    def cancel_point_selection(self):
        """取消当前点选择"""
        if self.drawing_line:
            self.points = self.original_points.copy()
            self.drawing_line = False
            if self.temp_line:
                self.app.canvas.delete(self.temp_line)
                self.temp_line = None
            self.app.redraw_points()
            self.app.update_status()


class CrosshairManager:
    """管理参考线功能 - 使用整图反相色滤镜，支持无图片时显示"""
    
    def __init__(self, app):
        self.app = app
        self.show_crosshair = True
        self.is_visible = False
        self.mouse_x = 0
        self.mouse_y = 0
        self.crosshair_items = []
        
        # 用于存储反相图像
        self.inverted_image = None
        self.inverted_photo = None
        self.inverted_image_id = None

    def update_mouse_position(self, x, y):
        """更新鼠标位置"""
        self.mouse_x = x
        self.mouse_y = y
        if self.is_visible and self.show_crosshair:
            self.draw_crosshair()

    def set_visibility(self, visible):
        """设置可见性"""
        self.is_visible = visible
        if visible and self.show_crosshair:
            self.app.canvas.config(cursor="none")
            self.draw_crosshair()
        else:
            self.app.canvas.config(cursor="")
            self.clear_crosshair()

    def draw_crosshair(self):
        """绘制十字参考线"""
        # 清除之前的参考线
        self.clear_crosshair()
        
        # 直接获取画布的实际尺寸，而不是依赖display_info
        canvas_width = self.app.canvas.winfo_width()
        canvas_height = self.app.canvas.winfo_height()
        
        # 如果画布尺寸无效，使用默认值
        if canvas_width <= 1:
            canvas_width = 800
        if canvas_height <= 1:
            canvas_height = 600
        
        # 确保鼠标位置在画布范围内
        mouse_x = max(0, min(self.mouse_x, canvas_width))
        mouse_y = max(0, min(self.mouse_y, canvas_height))
        
        # 绘制贯穿整个画布的水平线
        horizontal_line = self.app.canvas.create_line(
            0, mouse_y, canvas_width, mouse_y,
            fill="#4affff", width=1, tags="crosshair"
        )
        self.crosshair_items.append(horizontal_line)
        
        # 绘制贯穿整个画布的垂直线
        vertical_line = self.app.canvas.create_line(
            mouse_x, 0, mouse_x, canvas_height,
            fill="#4affff", width=1, tags="crosshair"
        )
        self.crosshair_items.append(vertical_line)
        
        # 绘制中心点标记（稍微大一点，更明显）
        center_dot = self.app.canvas.create_oval(
            mouse_x-1, mouse_y-1, 
            mouse_x+1, mouse_y+1,
            fill="#4affff", width=0, tags="crosshair"
        )
        self.crosshair_items.append(center_dot)

    def clear_crosshair(self):
        """清除参考线"""
        for item in self.crosshair_items:
            self.app.canvas.delete(item)
        self.crosshair_items = []
        
        # 清除反相图像引用
        self.inverted_image = None
        self.inverted_photo = None
        self.inverted_image_id = None

        
class ThumbnailManager:
    """管理缩略图功能"""
    
    def __init__(self, app):
        self.app = app
        self.images = []
        self.buttons = []
        self.cache = {}
        self.size = THUMBNAIL_SIZE

    def clear(self):
        """清除所有缩略图"""
        for widget in self.app.thumbnail_frame.winfo_children():
            widget.destroy()
        self.images = []
        self.buttons = []
        self.cache = {}

    def create_placeholder(self, scrollable_frame, index, filename):
        """创建缩略图占位符"""
        placeholder_text = self._get_placeholder_text(filename)
        thumb_btn = tk.Button(
            scrollable_frame, 
            text=placeholder_text,
            width=12,
            height=5,
            command=lambda idx=index: self.app.select_thumbnail(idx)
        )
        thumb_btn.grid(row=0, column=index, padx=5, pady=5)
        
        # 标记当前选中的图片
        if index == self.app.current_image_index:
            thumb_btn.config(relief=tk.SUNKEN, bg="light blue")
        else:
            thumb_btn.config(relief=tk.RAISED)
            
        self.buttons.append(thumb_btn)

    def _get_placeholder_text(self, filename):
        """获取占位符文本"""
        if self.app.i18n.current_language == 'zh_CN':
            if len(filename) > 10:
                return f"加载中...\n{filename[:10]}..."
            return f"加载中...\n{filename}"
        else:
            if len(filename) > 10:
                return f"Loading...\n{filename[:10]}..."
            return f"Loading...\n{filename}"

    def update_thumbnail(self, index, photo):
        """更新缩略图显示"""
        if index < len(self.buttons):
            btn = self.buttons[index]
            btn.config(
                image=photo, 
                text="", 
                width=photo.width(), 
                height=photo.height()
            )
            self.images.append(photo)


class AngleInputManager:
    """管理角度输入功能"""
    
    def __init__(self, app):
        self.app = app
        self.custom_angle_str = "0.25"
        self.should_clear_input = False
        self.angle_input_mode = False
        self.temp_angle_str = ""

    def handle_numeric_input(self, key):
        """处理数字输入"""
        if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            self.temp_angle_str += key
        elif key == 'period' and '.' not in self.temp_angle_str:
            self.temp_angle_str += '.'
        elif key == 'backspace' and self.temp_angle_str:
            self.temp_angle_str = self.temp_angle_str[:-1]
        
        self.app.update_angle_input_status()

    def confirm_input(self):
        """确认角度输入"""
        if self.temp_angle_str:
            try:
                angle = float(self.temp_angle_str)
                self.custom_angle_str = self.temp_angle_str
                self.app.update_status()
                self.app.status_label.config(text=f"Set single rotation to {angle}°")
            except ValueError:
                self.app.status_label.config(text="Invalid angle input, restored previous value")
        
        self.angle_input_mode = False
        self.temp_angle_str = ""

    def cancel_input(self):
        """取消角度输入"""
        self.angle_input_mode = False
        self.temp_angle_str = ""
        self.app.update_status()
        self.app.status_label.config(text="Angle input cancelled")


class SizeLockManager:
    """管理尺寸锁定功能"""
    
    def __init__(self, app):
        self.app = app
        self.lock_size = False  # 默认关闭
        self.original_size = None  # 原始图片尺寸
        
    def toggle_lock(self):
        """切换锁定状态"""
        if self.app.original_image:
            self.lock_size = not self.lock_size
            if self.lock_size and self.original_size is None:
                # 第一次锁定，记录原始尺寸
                self.original_size = self.app.original_image.size
            self.app.update_status()
            
    def crop_to_original_size(self, image):
        """将图片裁切回原始尺寸"""
        if not self.lock_size or self.original_size is None:
            return image
            
        original_width, original_height = self.original_size
        current_width, current_height = image.size
        
        # 计算裁切区域（居中裁切）
        left = (current_width - original_width) // 2
        top = (current_height - original_height) // 2
        right = left + original_width
        bottom = top + original_height
        
        # 确保裁切区域在图片范围内
        left = max(0, left)
        top = max(0, top)
        right = min(current_width, right)
        bottom = min(current_height, bottom)
        
        # 如果裁切区域小于原始尺寸，需要填充
        if (right - left) < original_width or (bottom - top) < original_height:
            # 创建新图片并填充背景色
            new_image = Image.new('RGB', self.original_size, self.app.bg_color)
            # 将裁切的部分粘贴到新图片中
            paste_x = (original_width - (right - left)) // 2
            paste_y = (original_height - (bottom - top)) // 2
            cropped = image.crop((left, top, right, bottom))
            new_image.paste(cropped, (paste_x, paste_y))
            return new_image
        else:
            # 直接裁切
            return image.crop((left, top, right, bottom))
    
    def should_show_warning(self):
        """检查是否需要显示警告"""
        if not self.lock_size:
            return False
        return abs(self.app.rotation_angle) > CROSSHAIR_WARNING_THRESHOLD
    
    def show_warning_dialog(self):
        """显示裁切警告对话框"""
        return messagebox.askyesno(
            self.app._("crop_warning"), 
            self.app._("crop_warning"),
            detail=self.app._("crop_warning_detail", self.app.rotation_angle)
        )


class AdvancedImageRotator:
    def __init__(self, root):
        self.root = root
        self.i18n = Internationalization()
        self._ = self.i18n.get_text  # 创建翻译方法别名
        
        self._setup_fonts()  # 设置全局字体
        self._setup_window()
        self._initialize_managers()
        self._initialize_variables()
        self._create_ui()
        self._setup_bindings()
        
        # 初始显示提示信息
        self.root.after(100, self.force_display_prompt)

    def _setup_fonts(self):
        """设置全局字体"""
        # 定义字体
        self.default_font = ("Microsoft YaHei", 10)  # 微软雅黑，10号
        self.title_font = ("Microsoft YaHei", 12, "bold")  # 标题字体
        self.large_font = ("Microsoft YaHei", 14)  # 大字体
        self.small_font = ("Microsoft YaHei", 9)  # 小字体
        
        # 设置Tkinter默认字体
        self.root.option_add("*Font", self.default_font)
        
        # 设置特定控件的字体
        self.root.option_add("*Label*Font", self.default_font)
        self.root.option_add("*Button*Font", self.default_font)
        self.root.option_add("*Entry*Font", self.default_font)

    def _setup_window(self):
        """设置窗口属性"""
        self.root.title(self._("window_title"))
        
        # 设置窗口大小并居中
        window_size = DEFAULT_WINDOW_SIZE  # "900x900"
        self.root.geometry(window_size)
        
        # 强制居中窗口
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"+{x}+{y}")
        
        self._set_window_icon()

    def _set_window_icon(self):
        """综合图标设置方法"""
        icon_set = False
        
        # 尝试多个可能的图标位置
        possible_paths = [
            "PicdocDeskew.ico",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "PicdocDeskew.ico"),
            os.path.join(os.getcwd(), "PicdocDeskew.ico"),
        ]
        
        for icon_path in possible_paths:
            try:
                if os.path.exists(icon_path):
                    self.root.iconbitmap(icon_path)
                    # print(f"成功设置图标: {icon_path}")
                    icon_set = True
                    break
            except Exception as e:
                print(f"设置图标失败 {icon_path}: {e}")
                continue
        
        # 如果所有方法都失败，清除可能存在的默认图标
        if not icon_set:
            try:
                self.root.iconbitmap('')  # 清除默认图标
                print("已清除默认图标")
            except:
                pass
        
        # 强制刷新窗口
        self.root.update_idletasks()

    def _initialize_managers(self):
        """初始化各个功能管理器"""
        self.auto_deskewer = AutoDeskewer(self)
        self.display_manager = ImageDisplayManager(self)
        self.point_manager = PointManager(self)
        self.crosshair_manager = CrosshairManager(self)
        self.thumbnail_manager = ThumbnailManager(self)
        self.angle_input_manager = AngleInputManager(self)
        self.size_lock_manager = SizeLockManager(self)

    def _initialize_variables(self):
        """初始化变量"""
        self.image_folder = ""
        self.image_files = []
        self.current_image_index = -1
        self.image = None
        self.photo = None
        self.original_image = None
        self.rotation_angle = 0
        self.bg_color = DEFAULT_BG_COLOR
        self.image_modified = {}

        # 启用PIL对所有格式的支持
        ImageFile.LOAD_TRUNCATED_IMAGES = True

    def _create_ui(self):
        """创建用户界面"""
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 配置grid权重
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        self._create_top_frame(main_container)
        self._create_middle_frame(main_container)
        self._create_buttons_frame(main_container)
        self._create_thumbnail_frame(main_container)

    def _create_top_frame(self, parent):
        """创建顶部信息显示区域"""
        top_frame = tk.Frame(parent, height=55)
        top_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=2)
        top_frame.grid_propagate(False)
        
        top_frame.grid_columnconfigure(0, weight=1)
        center_top_frame = tk.Frame(top_frame)
        center_top_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self._create_status_display(center_top_frame)
        self._create_info_display(center_top_frame)

    def _create_status_display(self, parent):
        """创建状态显示"""
        status_text = self._("select_folder_or_drag") if HAS_DND else self._("select_folder_only")
        self.status_label = tk.Label(
            parent, 
            text=status_text, 
            wraplength=800,
            anchor="center",
            font=("Microsoft YaHei", 10, "bold")  # 添加粗体字体
        )
        self.status_label.pack(anchor=tk.CENTER)

    def _create_info_display(self, parent):
        """创建信息显示"""
        info_frame = tk.Frame(parent)
        info_frame.pack(anchor=tk.CENTER, pady=2)
        
        self.angle_label = tk.Label(info_frame, text=self._("current_angle", 0))
        self.angle_label.pack(side=tk.LEFT, padx=5)
        
        self.custom_angle_label = tk.Label(info_frame, text=self._("single_rotation", "0"))
        self.custom_angle_label.pack(side=tk.LEFT, padx=5)
        
        self.bg_color_label = tk.Label(info_frame, text=self._("bg_color", 255, 255, 255))
        self.bg_color_label.pack(side=tk.LEFT, padx=5)
        
        # 尺寸显示标签
        self.size_label = tk.Label(info_frame, text=self._("size", "-"))
        self.size_label.pack(side=tk.LEFT, padx=5)
        
        # 霍夫变换方法显示
        self.hough_method_label = tk.Label(info_frame, text=self._("hough_method", self._("hough_optimized")))
        self.hough_method_label.pack(side=tk.LEFT, padx=5)

    def _create_middle_frame(self, parent):
        """创建中间图片预览区域"""
        middle_frame = tk.Frame(parent)
        middle_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=2)
        
        self.canvas = tk.Canvas(middle_frame, bg="#666666")
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def _create_buttons_frame(self, parent):
        """创建操作按钮区域"""
        buttons_frame = tk.Frame(parent, height=120)  # 增加高度以容纳新按钮
        buttons_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=2)
        buttons_frame.grid_propagate(False)
        
        buttons_frame.grid_columnconfigure(0, weight=2)
        buttons_frame.grid_columnconfigure(1, weight=0)
        buttons_frame.grid_columnconfigure(2, weight=2)
        
        # 新增自动纠偏按钮行
        self._create_auto_deskew_buttons(buttons_frame)
        self._create_left_buttons(buttons_frame)
        self._create_center_buttons(buttons_frame)
        self._create_right_buttons(buttons_frame)

    def _create_auto_deskew_buttons(self, parent):
        """创建自动纠偏按钮行"""
        auto_deskew_frame = tk.Frame(parent)
        auto_deskew_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=2)
        
        # 配置列权重使按钮居中
        auto_deskew_frame.grid_columnconfigure(0, weight=1)
        auto_deskew_frame.grid_columnconfigure(1, weight=0)
        auto_deskew_frame.grid_columnconfigure(2, weight=0)
        auto_deskew_frame.grid_columnconfigure(3, weight=1)
        
        # 自动纠偏按钮
        auto_deskew_btn = tk.Button(
            auto_deskew_frame, 
            text=self._("auto_deskew"), 
            command=self.auto_deskewer.auto_deskew_current, 
            width=16,
            height=1,
            bg="#CFCFCF"
        )
        auto_deskew_btn.grid(row=0, column=1, padx=5)
        
        # 批量纠偏按钮
        batch_deskew_btn = tk.Button(
            auto_deskew_frame, 
            text=self._("batch_deskew"), 
            command=self.auto_deskewer.batch_auto_deskew, 
            width=16,
            height=1,
            bg="#CFCFCF"
        )
        batch_deskew_btn.grid(row=0, column=2, padx=5)

    def _create_left_buttons(self, parent):
        """创建左侧按钮"""
        left_buttons_frame = tk.Frame(parent)
        left_buttons_frame.grid(row=1, column=0, sticky="e", padx=0, pady=5)
        
        button_configs = [
            (self._("select_folder"), self.open_folder),
            (self._("open_images"), self.open_files)
        ]
        
        for text, command in button_configs:
            btn = tk.Button(
                left_buttons_frame, 
                text=text, 
                command=command, 
                width=14,
                height=1
            )
            btn.pack(pady=2)

    def _create_center_buttons(self, parent):
        """创建中间按钮"""
        center_buttons_frame = tk.Frame(parent)
        center_buttons_frame.grid(row=1, column=1, sticky="nsew", pady=5)
        
        # 第二行按钮
        second_row = tk.Frame(center_buttons_frame)
        second_row.pack(pady=2)
        
        second_buttons = [
            (self._("rotate_left"), self.rotate_left),
            (self._("zoom_in"), self.zoom_in_center),
            (self._("rotate_right"), self.rotate_right)
        ]
        
        for text, command in second_buttons:
            btn = tk.Button(
                second_row, 
                text=text, 
                command=command, 
                width=8,
                height=1
            )
            btn.pack(side=tk.LEFT, padx=2)
        
        # 第三行按钮
        third_row = tk.Frame(center_buttons_frame)
        third_row.pack(pady=2)
        
        third_buttons = [
            (self._("previous"), self.previous_image),
            (self._("zoom_out"), self.zoom_out_center),
            (self._("next"), self.next_image)
        ]
        
        for text, command in third_buttons:
            btn = tk.Button(
                third_row, 
                text=text, 
                command=command, 
                width=8,
                height=1
            )
            btn.pack(side=tk.LEFT, padx=2)

    def _create_right_buttons(self, parent):
        """创建右侧按钮"""
        right_buttons_frame = tk.Frame(parent)
        right_buttons_frame.grid(row=1, column=2, sticky="w", padx=0, pady=5)
        
        button_configs = [
            (self._("reset"), self.reset_image),
            (self._("lock_size"), self.size_lock_manager.toggle_lock)
        ]
        
        for text, command in button_configs:
            btn = tk.Button(
                right_buttons_frame, 
                text=text, 
                command=command, 
                width=14,
                height=1
            )
            btn.pack(pady=2)

    def _create_thumbnail_frame(self, parent):
        """创建缩略图区域"""
        thumbs_frame = tk.Frame(parent, height=100)
        thumbs_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=2)
        thumbs_frame.grid_propagate(False)
        
        self.thumbnail_frame = tk.Frame(thumbs_frame)
        self.thumbnail_frame.pack(fill=tk.BOTH, expand=True)

    def _setup_bindings(self):
        """设置事件绑定"""
        # 键盘事件
        self.root.bind('<KeyPress>', self.on_key_press)
        self.root.focus_set()
        
        # 窗口事件
        self.root.bind('<Configure>', self.on_window_resize)
        
        # 鼠标事件
        self._setup_mouse_bindings()
        
        # 拖拽支持
        if HAS_DND:
            self._setup_drag_drop()

    def _setup_mouse_bindings(self):
        """设置鼠标事件绑定"""
        # 左键事件
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        
        # 右键事件
        self.canvas.bind("<Button-3>", self.on_right_click_start)
        self.canvas.bind("<B3-Motion>", self.on_right_click_drag)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_click_end)
        
        # 中键和滚轮事件
        self.canvas.bind("<Button-2>", self.on_middle_click)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        
        # 鼠标移动事件 - 新增进入和离开事件
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Enter>", self.on_canvas_enter)
        self.canvas.bind("<Leave>", self.on_canvas_leave)

    def _setup_drag_drop(self):
        """设置拖拽支持"""
        try:
            self.canvas.drop_target_register(DND_FILES)
            self.canvas.dnd_bind('<<Drop>>', self.on_drop)
            self.status_label.config(text=self._("select_folder_or_drag"))
        except Exception as e:
            print(f"拖拽功能设置失败: {str(e)}")

    def on_canvas_enter(self, event):
        """鼠标进入画布事件"""
        self.crosshair_manager.set_visibility(True)

    def on_canvas_leave(self, event):
        """鼠标离开画布事件"""
        self.crosshair_manager.set_visibility(False)

    # 以下是原有的功能方法，保持接口不变但内部使用管理器
    def force_display_prompt(self):
        """强制显示提示信息"""
        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if not self.image:
            self.show_no_image_prompt(canvas_width, canvas_height)

    def on_drop(self, event):
        """处理拖拽放置事件"""
        files = self.root.tk.splitlist(event.data)
        if files:
            if len(files) == 1 and os.path.isdir(files[0]):
                self.load_folder(files[0])
            else:
                self.load_files(files)

    def open_folder(self):
        """选择文件夹"""
        folder_path = filedialog.askdirectory(title=self._("select_folder_title"))
        if folder_path:
            self.load_folder(folder_path)

    def open_files(self):
        """打开图片"""
        file_paths = filedialog.askopenfilenames(
            title=self._("open_images_title"),
            filetypes=[
                (self._("all_image_files"), "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.tif *.webp *.ico *.ppm *.pgm *.pbm"),
                (self._("png_files"), "*.png"),
                (self._("jpeg_files"), "*.jpg *.jpeg"),
                (self._("bitmap_files"), "*.bmp"),
                (self._("gif_files"), "*.gif"),
                (self._("tiff_files"), "*.tiff *.tif"),
                ("WebP 文件", "*.webp"),
                (self._("all_files"), "*.*")
            ]
        )
        
        if file_paths:
            self.load_files(file_paths)

    def load_folder(self, folder_path):
        """加载文件夹中的图片"""
        self.image_folder = folder_path
        self.image_files = self._get_image_files(folder_path)
        
        if not self.image_files:
            messagebox.showwarning(self._("crop_warning"), self._("no_images_found"))
            return
        
        self._initialize_image_loading()

    def _get_image_files(self, folder_path):
        """获取文件夹中的图片文件"""
        image_files = []
        for file in os.listdir(folder_path):
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                image_files.append(file)
        return self._natural_sort(image_files)

    def _natural_sort(self, files):
        """自然排序算法"""
        def natural_sort_key(filename):
            parts = re.split(r'(\d+)', filename)
            return [int(part) if part.isdigit() else part.lower() for part in parts]
        
        return sorted(files, key=natural_sort_key)

    def load_files(self, file_paths):
        """加载多个文件"""
        if not file_paths:
            return
        
        self.image_files = self._extract_image_files(file_paths)
        
        if not self.image_files:
            messagebox.showwarning(self._("crop_warning"), self._("no_valid_images"))
            return
        
        self.image_folder = os.path.dirname(file_paths[0])
        self.image_files = self._natural_sort(self.image_files)
        self._initialize_image_loading()

    def _extract_image_files(self, file_paths):
        """从文件路径中提取图片文件"""
        image_files = []
        for file_path in file_paths:
            if (os.path.isfile(file_path) and 
                file_path.lower().endswith(SUPPORTED_EXTENSIONS)):
                image_files.append(os.path.basename(file_path))
        return image_files

    def _initialize_image_loading(self):
        """初始化图片加载"""
        self.thumbnail_manager.cache = {}
        self.image_modified = {}
        
        # 显示缩略图区域
        thumbs_frame = self.thumbnail_frame.master
        thumbs_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=2)

        self.update_thumbnails()
        self.current_image_index = 0
        self.load_current_image()
        self.update_status()

    def update_thumbnails(self):
        """更新缩略图显示"""
        self.thumbnail_manager.clear()
        
        if not self.image_files:
            return
            
        # 创建滚动区域
        self._create_thumbnail_scroll_area()
        
        # 在后台线程中加载缩略图
        threading.Thread(
            target=self.load_thumbnails_thread, 
            args=(self.scrollable_frame,), 
            daemon=True
        ).start()

    def _create_thumbnail_scroll_area(self):
        """创建缩略图滚动区域"""
        self.thumbnail_canvas = tk.Canvas(
            self.thumbnail_frame, 
            height=self.thumbnail_manager.size + 20
        )
        self.thumbnail_scrollbar = tk.Scrollbar(
            self.thumbnail_frame, 
            orient=tk.HORIZONTAL, 
            command=self.thumbnail_canvas.xview
        )
        
        self.scrollable_frame = tk.Frame(self.thumbnail_canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.thumbnail_canvas.configure(
                scrollregion=self.thumbnail_canvas.bbox("all")
            )
        )
        
        self.thumbnail_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.thumbnail_canvas.configure(xscrollcommand=self.thumbnail_scrollbar.set)
        
        self.thumbnail_canvas.pack(side="top", fill="x", expand=True)
        self.thumbnail_scrollbar.pack(side="bottom", fill="x")

    def load_thumbnails_thread(self, scrollable_frame):
        """在后台线程中加载缩略图"""
        for i, filename in enumerate(self.image_files):
            self.root.after(0, self.thumbnail_manager.create_placeholder, scrollable_frame, i, filename)
            
            file_path = os.path.join(self.image_folder, filename)
            photo = self._load_thumbnail_image(file_path)
            
            if photo:
                self.root.after(0, self.thumbnail_manager.update_thumbnail, i, photo)
        
        self.root.after(0, self.scroll_to_current_thumbnail)

    def _load_thumbnail_image(self, file_path):
        """加载缩略图图片 - 智能缓存方案"""
        filename = os.path.basename(file_path)
        folder_path = os.path.dirname(file_path)
        
        # 检查Deskew文件夹中的文件
        deskew_file_path = os.path.join(folder_path, "Deskew", filename)
        
        # 确定实际文件路径和修改时间
        if os.path.exists(deskew_file_path):
            actual_file_path = deskew_file_path
            file_mtime = os.path.getmtime(deskew_file_path)
        else:
            actual_file_path = file_path
            file_mtime = os.path.getmtime(file_path)
        
        # 使用文件路径和修改时间作为缓存键
        cache_key = f"{actual_file_path}_{file_mtime}_{self.thumbnail_manager.size}"
        
        # 检查缓存
        if cache_key in self.thumbnail_manager.cache:
            return self.thumbnail_manager.cache[cache_key]
        
        try:
            img = Image.open(actual_file_path)
            img_width, img_height = img.size
            
            # 计算缩略图尺寸
            thumb_height = self.thumbnail_manager.size
            thumb_width = int(img_width * thumb_height / img_height)
            
            img = img.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            
            # 缓存结果
            self.thumbnail_manager.cache[cache_key] = photo
            
            # 清理旧缓存（防止内存泄漏）
            self._clean_thumbnail_cache()
            
            return photo
            
        except Exception as e:
            print(f"无法加载缩略图 {filename}: {str(e)}")
            error_img = Image.new('RGB', (80, 80), color='red')
            return ImageTk.PhotoImage(error_img)

    def _clean_thumbnail_cache(self):
        """清理缩略图缓存，保留最近使用的"""
        max_cache_size = 100  # 最大缓存数量
        if len(self.thumbnail_manager.cache) > max_cache_size:
            # 简单策略：随机删除一半旧缓存
            keys_to_remove = list(self.thumbnail_manager.cache.keys())[:max_cache_size//2]
            for key in keys_to_remove:
                del self.thumbnail_manager.cache[key]

    def update_current_thumbnail(self):
        """更新当前缩略图显示 - 高效版本"""
        if 0 <= self.current_image_index < len(self.thumbnail_manager.buttons):
            filename = self.image_files[self.current_image_index]
            file_path = os.path.join(self.image_folder, filename)
            
            # 强制清除当前缩略图的缓存
            deskew_file_path = os.path.join(self.image_folder, "Deskew", filename)
            cache_keys_to_remove = []
            
            for cache_key in self.thumbnail_manager.cache:
                if filename in cache_key:
                    cache_keys_to_remove.append(cache_key)
            
            for key in cache_keys_to_remove:
                del self.thumbnail_manager.cache[key]
            
            # 重新加载缩略图
            photo = self._load_thumbnail_image(file_path)
            
            if photo:
                btn = self.thumbnail_manager.buttons[self.current_image_index]
                btn.config(
                    image=photo, 
                    text="", 
                    width=photo.width(), 
                    height=photo.height()
                )
                # 保存引用防止被垃圾回收
                if self.current_image_index < len(self.thumbnail_manager.images):
                    self.thumbnail_manager.images[self.current_image_index] = photo
                else:
                    self.thumbnail_manager.images.append(photo)

    def scroll_to_current_thumbnail(self):
        """滚动到当前选中的缩略图"""
        if (not self.thumbnail_canvas or self.current_image_index < 0 or 
            self.current_image_index >= len(self.thumbnail_manager.buttons)):
            return
        
        current_btn = self.thumbnail_manager.buttons[self.current_image_index]
        self.root.update_idletasks()
        
        btn_x = current_btn.winfo_x()
        btn_width = current_btn.winfo_width()
        canvas_width = self.thumbnail_canvas.winfo_width()
        visible_start = self.thumbnail_canvas.canvasx(0)
        visible_end = visible_start + canvas_width
        
        btn_start = btn_x
        btn_end = btn_x + btn_width
        margin = 20
        
        if btn_end > visible_end - margin:
            target_x = btn_end - canvas_width + margin
            self.thumbnail_canvas.xview_moveto(target_x / self.thumbnail_canvas.bbox("all")[2])
        elif btn_start < visible_start + margin:
            target_x = btn_start - margin
            self.thumbnail_canvas.xview_moveto(target_x / self.thumbnail_canvas.bbox("all")[2])

    def select_thumbnail(self, index):
        """选择缩略图"""
        if 0 <= index < len(self.image_files):
            self.save_current_image_if_modified()
            self.current_image_index = index
            self.load_current_image()
            self.update_thumbnails_selection()
            self.root.after(100, self.scroll_to_current_thumbnail)

    def update_thumbnails_selection(self):
        """更新缩略图选中状态"""
        for i, btn in enumerate(self.thumbnail_manager.buttons):
            if i == self.current_image_index:
                btn.config(relief=tk.SUNKEN, bg="light blue")
            else:
                btn.config(relief=tk.RAISED, bg="SystemButtonFace")

    def rotate_left(self):
        """左旋按钮的处理方法"""
        try:
            angle = float(self.angle_input_manager.custom_angle_str) if self.angle_input_manager.custom_angle_str else 0
            self.rotate_by_angle(angle)
        except ValueError:
            pass

    def rotate_right(self):
        """右旋按钮的处理方法"""
        try:
            angle = float(self.angle_input_manager.custom_angle_str) if self.angle_input_manager.custom_angle_str else 0
            self.rotate_by_angle(-angle)
        except ValueError:
            pass

    def zoom_in_center(self):
        """放大按钮的处理方法"""
        self.zoom_in()

    def zoom_out_center(self):
        """缩小按钮的处理方法"""
        self.zoom_out()

    def load_current_image(self):
        """加载当前图片 - 自动创建Deskew文件夹副本"""
        self.canvas.delete("prompt")
        self.point_manager.reset_points()
        
        if 0 <= self.current_image_index < len(self.image_files):
            filename = self.image_files[self.current_image_index]
            original_file_path = os.path.join(self.image_folder, filename)
            
            # 创建Deskew文件夹
            deskew_folder = os.path.join(self.image_folder, "Deskew")
            if not os.path.exists(deskew_folder):
                os.makedirs(deskew_folder)
            
            # Deskew文件夹中的文件路径
            deskew_file_path = os.path.join(deskew_folder, filename)
            
            try:
                # 如果Deskew文件夹中还没有该文件的副本，则创建副本
                if not os.path.exists(deskew_file_path):
                    # 复制原文件到Deskew文件夹
                    import shutil
                    shutil.copy2(original_file_path, deskew_file_path)
                    print(f"Created copy in Deskew folder: {filename}")
                
                # 始终从Deskew文件夹加载图片
                self.original_image = Image.open(deskew_file_path)
                self.image = self.original_image.copy()
                self.rotation_angle = 0
                
                # 重置尺寸锁定管理器的原始尺寸
                if self.size_lock_manager.lock_size:
                    self.size_lock_manager.original_size = self.original_image.size
                
                self.display_manager.apply_zoom_mode()
                self.display_image()
                self.update_status()
                
            except Exception as e:
                error_msg = self._get_image_error_message(e, original_file_path)
                messagebox.showerror("错误", error_msg)

    def _get_image_error_message(self, error, file_path):
        """获取图片错误信息"""
        base_msg = self._("image_error", os.path.basename(file_path), str(error))
        if "cannot identify picture file" in str(error).lower():
            base_msg += self._("image_format_error")
        return base_msg

    def display_image(self):
        """显示图片"""
        self.canvas.update_idletasks()
        
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 800, 600
        
        # 清空画布
        self.canvas.delete("all")

        if self.image:
            img_width, img_height = self.image.size
            
            # 计算显示尺寸
            display_width, display_height, scale, base_scale = \
                self.display_manager.calculate_display_size(
                    canvas_width, canvas_height, img_width, img_height
                )
            
            # 如果有透明通道，创建带棋盘格背景的图片
            if self.has_alpha_channel(self.image):
                display_image = self._create_checkerboard_image(self.image, display_width, display_height)
            else:
                # 非透明图片正常处理
                display_image = self._resize_image(self.image, display_width, display_height, img_width, img_height)
            
            self.photo = ImageTk.PhotoImage(display_image)
            
            # 计算图片位置
            img_x = canvas_width // 2 + self.display_manager.pan_x
            img_y = canvas_height // 2 + self.display_manager.pan_y
            
            self.canvas.create_image(img_x, img_y, image=self.photo, anchor=tk.CENTER)
            
            # 更新显示信息
            self.display_manager.update_display_info(
                img_x, img_y, display_width, display_height, 
                scale, base_scale, canvas_width, canvas_height
            )
            
            # 重绘点
            self.redraw_points()
            
        else:
            # 没有图片时显示提示信息
            self.show_no_image_prompt(canvas_width, canvas_height)
            
        # 如果鼠标在画布内，更新参考线位置
        if self.crosshair_manager.is_visible and self.crosshair_manager.show_crosshair:
            self.crosshair_manager.draw_crosshair()

    def _create_checkerboard_image(self, image, display_width, display_height):
        """为透明图片创建带棋盘格背景的显示图片"""
        # 创建棋盘格背景
        cell_size = 20
        checkerboard = Image.new('RGB', (display_width, display_height), "#E0E0E0")
        draw = ImageDraw.Draw(checkerboard)
        
        # 绘制棋盘格
        for y in range(0, display_height, cell_size):
            for x in range(0, display_width, cell_size):
                if (x // cell_size + y // cell_size) % 2 == 0:
                    color = "#666666"  # 浅灰色
                else:
                    color = "#B8B8B8"  # 深灰色
                draw.rectangle([x, y, x+cell_size, y+cell_size], fill=color)
        
        # 调整原图大小
        resized_image = image.resize((display_width, display_height), Image.Resampling.LANCZOS)
        
        # 将透明图片叠加在棋盘格上
        if resized_image.mode == 'RGBA':
            checkerboard.paste(resized_image, (0, 0), resized_image)
        else:
            checkerboard.paste(resized_image, (0, 0))
        
        return checkerboard

    def _resize_image(self, image, display_width, display_height, original_width, original_height):
        """调整图片大小"""
        scale = display_width / original_width
        
        if scale != 1.0:
            original_pixels = original_width * original_height
            display_pixels = display_width * display_height
            resample_method = self.display_manager.get_resample_method(original_pixels, display_pixels)
            return image.resize((display_width, display_height), resample_method)
        else:
            return image.copy()

    def show_no_image_prompt(self, canvas_width, canvas_height):
        """在没有图片时显示提示信息""" 
        # 计算居中位置
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        
        # 主提示文字
        main_font = ("Microsoft YaHei", 20, "bold")
        main_text = self._("drag_prompt")
        
        self.canvas.create_text(
            center_x, 
            center_y - 240,  # 向上偏移，为下方内容留空间
            text=main_text,
            font=main_font,
            fill="#F0F0F0",
            tags="prompt"
        )
        
        # 说明文字 - 更新快捷键说明
        subtitle_font = ("Microsoft YaHei", 10, "bold")
        subtitle_text = self._("shortcuts_prompt")
        
        self.canvas.create_text(
            canvas_width // 2, 
            canvas_height // 2 + 40,
            text=subtitle_text,
            font=subtitle_font,
            fill="#F0F0F0",
            justify=tk.LEFT,
            tags="prompt"
        )

    def on_canvas_click(self, event):
        """画布点击事件处理"""
        if not self.image:
            return

        # 更新鼠标位置
        self.crosshair_manager.update_mouse_position(event.x, event.y)

        # 转换坐标到图片坐标
        actual_x, actual_y = self._convert_canvas_to_image_coords(event.x, event.y)
        
        # 检查点击是否在图片范围内
        if self._is_point_in_image(actual_x, actual_y):
            self._handle_image_click(actual_x, actual_y)

    def _convert_canvas_to_image_coords(self, canvas_x, canvas_y):
        """转换画布坐标到图片坐标"""
        if not hasattr(self.display_manager, 'display_info') or not self.image:
            return canvas_x, canvas_y
            
        display_info = self.display_manager.display_info
        
        # 计算相对于图片显示区域的坐标
        rel_x = canvas_x - display_info['offset_x']
        rel_y = canvas_y - display_info['offset_y']
        
        scale = display_info['scale']
        
        if scale > 0:
            img_x = rel_x / scale
            img_y = rel_y / scale
            
            # 确保坐标在图像范围内
            img_width, img_height = self.image.size
            img_x = max(0, min(img_width - 1, img_x))
            img_y = max(0, min(img_height - 1, img_y))
            
            return img_x, img_y
        else:
            return rel_x, rel_y

    def _is_point_in_image(self, x, y):
        """检查点是否在图片范围内"""
        if not self.image:
            return False
        img_width, img_height = self.image.size
        return 0 <= x < img_width and 0 <= y < img_height

    def _handle_image_click(self, x, y):
        """处理图片点击事件"""
        if not self.point_manager.drawing_line:
            # 开始绘制动态连线 - 点击第一个点
            self.point_manager.original_points = self.point_manager.points.copy()
            self.point_manager.points = [(x, y)]
            self.point_manager.first_point = (x, y)
            self.point_manager.drawing_line = True
            self.redraw_points()
            self.status_label.config(text=self._("select_second_point"))
        else:
            # 点击第二个点，完成连线
            self.point_manager.points.append((x, y))
            self.point_manager.drawing_line = False
            self.redraw_points()
            self.rotate_by_points()
            self.update_status()

    def redraw_points(self):
        """重绘点"""
        self.canvas.delete("points")
        self.canvas.delete("line")
        
        if not hasattr(self.display_manager, 'display_info') or not self.point_manager.points:
            return
            
        scale = self.display_manager.display_info['scale']
        offset_x = self.display_manager.display_info['offset_x']
        offset_y = self.display_manager.display_info['offset_y']
        
        # 绘制点
        for i, (x, y) in enumerate(self.point_manager.points):
            display_x = x * scale + offset_x
            display_y = y * scale + offset_y
            
            self.canvas.create_oval(
                display_x-1.5, display_y-1.5, display_x+1.5, display_y+1.5,
                fill="#DD23DD", width=0, tags="points"
            )
            label = 'A' if i == 0 else 'B'
            self.canvas.create_text(
                display_x, display_y-15,
                text=label, fill="#DD23DD", width=0, tags="points"
            )

    def rotate_by_points(self):
        """通过两点旋转图片，支持水平和垂直纠偏"""
        if len(self.point_manager.points) != 2:
            return
            
        x1, y1 = self.point_manager.points[0]
        x2, y2 = self.point_manager.points[1]
        
        # 计算两点距离
        dx = x2 - x1
        dy = y2 - y1
        
        # 计算直线与水平线的夹角（-180到180度）
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        
        # 定义特殊角度（0, ±45, ±90, ±135, ±180度）
        special_angles = [0, 45, 90, 135, 180, -45, -90, -135, -180]
        
        # 检查是否接近特殊角度（容差设为0.1度）
        is_special_angle = False
        for special_angle in special_angles:
            if abs(angle_deg - special_angle) < 0.1:
                is_special_angle = True
                break
        
        # 如果是特殊角度，不旋转
        if is_special_angle:
            return
        
        # 判断是水平纠偏还是垂直纠偏
        if abs(dx) > abs(dy):  # 水平纠偏
            # 检查角度是否在0~45度之间
            if 0 <= angle_deg <= 45:
                target_angle = abs(0 - angle_deg)  # 按绝对值旋转
            # 检查角度是否在0~-45度之间
            elif -45 <= angle_deg < 0:
                target_angle = -(0 - angle_deg)  # 按相反数旋转
            # 检查角度是否在135~180度之间
            elif 135 <= angle_deg <= 180:
                target_angle = angle_deg + 180  # 按角度加180后的角度旋转
            # 检查角度是否在-135~-180度之间
            elif -180 <= angle_deg <= -135:
                target_angle = angle_deg + 180  # 按角度加180后的角度旋转
            else:
                # 其他情况不旋转
                return
        else:  # 垂直纠偏
            # 检查角度是否在45~90度之间
            if 45 <= angle_deg <= 90:
                target_angle = -(90 - angle_deg)  # 按90度减去角度后的相反数旋转
            # 检查角度是否在90~135度之间
            elif 90 <= angle_deg <= 135:
                target_angle = abs(90 - angle_deg)  # 按90度减去角度后的绝对值旋转
            # 检查角度是否在-45~-90度之间
            elif -90 <= angle_deg <= -45:
                target_angle = angle_deg + 90  # 按角度加90后的角度旋转
            # 检查角度是否在-90~-135度之间
            elif -135 <= angle_deg <= -90:
                target_angle = angle_deg + 90  # 按角度加90后的角度旋转
            else:
                # 其他情况不旋转
                return
        
        # 旋转图片
        self.rotate_image_to(target_angle)
        self.point_manager.reset_points()
        self.display_image()

    def rotate_image_to(self, angle):
        """旋转图片到指定角度"""
        if self.original_image:
            # 检查是否有透明通道
            if self.has_alpha_channel(self.original_image):
                # 透明图片：使用透明背景旋转
                fillcolor = None
            else:
                # 非透明图片：使用设置的背景色
                fillcolor = self.bg_color
                
            rotated_image = self.original_image.rotate(
                angle, 
                expand=True, 
                resample=Image.BICUBIC,
                fillcolor=fillcolor
            )
            
            self.image = rotated_image
            self.rotation_angle = angle
            self.display_image()
            self.update_status()
            
            # 标记图片已被修改
            self._mark_image_modified()

    def rotate_by_angle(self, angle):
        """按指定角度旋转图片"""
        if self.original_image:
            total_angle = self.rotation_angle + angle
            
            # 检查是否有透明通道
            if self.has_alpha_channel(self.original_image):
                # 透明图片：使用透明背景旋转
                fillcolor = None  # 或者 (255, 255, 255, 0)
            else:
                # 非透明图片：使用设置的背景色
                fillcolor = self.bg_color
            
            rotated_image = self.original_image.rotate(
                total_angle, 
                expand=True, 
                resample=Image.BICUBIC,
                fillcolor=fillcolor
            )
            
            self.image = rotated_image
            self.rotation_angle = total_angle
            self.point_manager.reset_points()
            self.display_image()
            self.update_status()
            self._mark_image_modified()
            
            # 旋转后标记需要清除输入
            self.angle_input_manager.should_clear_input = True

    def _mark_image_modified(self):
        """标记图片已被修改"""
        if 0 <= self.current_image_index < len(self.image_files):
            filename = self.image_files[self.current_image_index]
            self.image_modified[filename] = True

    def update_status(self):
        """更新状态信息"""
        if 0 <= self.current_image_index < len(self.image_files):
            filename = self.image_files[self.current_image_index]
            modified_indicator = self._("modified") if self.image_modified.get(filename, False) else ""
            display_filename = self.adaptive_filename_display(filename)
            
            self.status_label.config(
                text=self._("current_image", f"{display_filename}{modified_indicator}") + 
                     f" ({self.current_image_index + 1}/{len(self.image_files)})"
            )
        
        self.angle_label.config(text=self._("current_angle", self.rotation_angle))
        
        # 显示单次旋转角度
        try:
            custom_angle = float(self.angle_input_manager.custom_angle_str) if self.angle_input_manager.custom_angle_str else 0
            self.custom_angle_label.config(text=self._("single_rotation", custom_angle))
        except ValueError:
            self.custom_angle_label.config(text=self._("single_rotation", "0"))
        
        # 显示填充色
        self.bg_color_label.config(text=self._("bg_color", self.bg_color[0], self.bg_color[1], self.bg_color[2]))
        
        # 显示尺寸信息
        if self.image:
            width, height = self.image.size
            lock_status = self._("size_locked") if self.size_lock_manager.lock_size else ""
            self.size_label.config(text=self._("size", f"{width}×{height}{lock_status}"))
        else:
            self.size_label.config(text=self._("size", "-"))
            
        # 显示霍夫变换方法
        method_names = {
            "standard": self._("hough_standard"),
            "probabilistic": self._("hough_probabilistic"), 
            "optimized": self._("hough_optimized")
        }
        method_name = method_names.get(self.auto_deskewer.hough_method, self._("hough_optimized"))
        self.hough_method_label.config(text=self._("hough_method", method_name))
            
        # 显示批量纠偏状态
        if self.auto_deskewer.is_batch_deskewing:
            batch_status = self._("batch_status")
            current_text = self.status_label.cget("text")
            if batch_status not in current_text:
                self.status_label.config(text=current_text + batch_status)

    def adaptive_filename_display(self, filename):
        """自适应文件名显示"""
        try:
            label_width = self.status_label.winfo_width()
            if label_width <= 1:
                main_width = self.root.winfo_width()
                if main_width > 1:
                    label_width = main_width - 100
                else:
                    return self.truncate_filename(filename, 50)
        except:
            return self.truncate_filename(filename, 50)
        
        char_width = 8
        max_chars = max(70, int(label_width / char_width) - 20)
        
        if len(filename) <= max_chars:
            return filename
        
        return self.truncate_filename(filename, max_chars)

    def truncate_filename(self, filename, max_length):
        """截断文件名"""
        if len(filename) <= max_length:
            return filename
        
        front_chars = int(max_length * 0.6)
        back_chars = max_length - front_chars - 2
        
        if front_chars + back_chars >= len(filename):
            return filename
        
        return filename[:front_chars] + "……" + filename[-back_chars:]

    def reset_image(self):
        """重置当前图片到原始状态"""
        if self.original_image:
            self.image = self.original_image.copy()
            self.rotation_angle = 0
            self.point_manager.reset_points()
            self.display_manager.apply_zoom_mode()
            self.display_image()
            self.update_status()
            
            # 重置修改状态
            if 0 <= self.current_image_index < len(self.image_files):
                filename = self.image_files[self.current_image_index]
                self.image_modified[filename] = False

    def previous_image(self):
        """切换到上一张图片"""
        if self.image_files:
            # 检查是否需要显示警告
            if self.size_lock_manager.should_show_warning():
                if not self.size_lock_manager.show_warning_dialog():
                    return  # 用户选择取消
            
            self.save_current_image_if_modified()
            
            if self.current_image_index > 0:
                self.current_image_index -= 1
            else:
                self.current_image_index = len(self.image_files) - 1
                
            self.load_current_image()
            self.update_thumbnails_selection()
            self.root.after(100, self.scroll_to_current_thumbnail)

    def next_image(self):
        """切换到下一张图片"""
        if self.image_files:
            # 检查是否需要显示警告
            if self.size_lock_manager.should_show_warning():
                if not self.size_lock_manager.show_warning_dialog():
                    return  # 用户选择取消
            
            self.save_current_image_if_modified()
            
            if self.current_image_index < len(self.image_files) - 1:
                self.current_image_index += 1
            else:
                self.current_image_index = 0
                
            self.load_current_image()
            self.update_thumbnails_selection()
            self.root.after(100, self.scroll_to_current_thumbnail)

    def save_current_image_if_modified(self):
        """保存当前图片到Deskew文件夹"""
        if self.image and 0 <= self.current_image_index < len(self.image_files):
            filename = self.image_files[self.current_image_index]
            if self.image_modified.get(filename, False):
                try:
                    deskew_folder = os.path.join(self.image_folder, "Deskew")
                    original_file_path = os.path.join(self.image_folder, filename)
                    file_path = os.path.join(deskew_folder, filename)
                    
                    # 如果启用了尺寸锁定，先裁切图片
                    save_image = self.image
                    if self.size_lock_manager.lock_size:
                        save_image = self.size_lock_manager.crop_to_original_size(self.image)
                    
                    # 获取文件扩展名
                    file_ext = os.path.splitext(filename)[1].lower()
                    
                    # 智能保存策略
                    if file_ext in ['.jpg', '.jpeg']:
                        # JPEG转为PNG避免质量损失
                        new_filename = os.path.splitext(filename)[0] + '.png'
                        file_path = os.path.join(deskew_folder, new_filename)
                        save_image.save(file_path, optimize=True)
                        print(f"JPEG转换为PNG保存: {filename} -> {new_filename}")
                        
                    elif file_ext == '.webp':
                        # WebP使用无损模式保存
                        save_image.save(file_path, lossless=True)
                        
                    elif file_ext == '.gif':
                        # GIF保持原格式，但优化调色板
                        save_image.save(file_path, optimize=True)
                        
                    elif file_ext in ['.tiff', '.tif']:
                        # TIFF使用无损压缩
                        save_image.save(file_path, compression='tiff_deflate')
                        
                    elif file_ext == '.png':
                        # PNG优化压缩
                        save_image.save(file_path, optimize=True)
                        
                    else:
                        # 其他格式默认保存
                        save_image.save(file_path)
                    
                    self.image_modified[filename] = False
                    print(f"Saved to Deskew folder: {filename}")
                    
                    # 更新文件列表（如果格式改变）
                    if file_ext in ['.jpg', '.jpeg'] and new_filename:
                        self.image_files[self.current_image_index] = new_filename
                    
                    # 强制重新加载所有缩略图
                    self.reload_all_thumbnails()
                    
                except Exception as e:
                    print(f"Save failed: {str(e)}")

    def reload_all_thumbnails(self):
        """重新加载所有缩略图"""
        # 清除缓存
        self.thumbnail_manager.cache = {}
        
        # 重新加载所有缩略图
        for i, filename in enumerate(self.image_files):
            file_path = os.path.join(self.image_folder, filename)
            photo = self._load_thumbnail_image(file_path)
            
            if photo and i < len(self.thumbnail_manager.buttons):
                btn = self.thumbnail_manager.buttons[i]
                btn.config(
                    image=photo, 
                    text="", 
                    width=photo.width(), 
                    height=photo.height()
                )
                # 保存引用
                if i < len(self.thumbnail_manager.images):
                    self.thumbnail_manager.images[i] = photo
                else:
                    self.thumbnail_manager.images.append(photo)

    def on_key_press(self, event):
        """键盘事件处理"""
        key = event.keysym.lower()

        # Tab键切换语言
        if key == 'tab':
            self.toggle_language_simple()
            return "break"
        
        # F1键打开网页功能
        if key == 'f1':
            self.open_help_webpage()
            return
        
        # 批量纠偏过程中按Esc键中止（与B键功能相同）
        if key == 'escape' and self.auto_deskewer.is_batch_deskewing:
            self.auto_deskewer.batch_auto_deskew()  # 直接调用相同的方法
            return "break"

        # 角度输入模式处理
        if self.angle_input_manager.angle_input_mode:
            if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'period', 'backspace']:
                self.angle_input_manager.handle_numeric_input(key)
                return
            elif key in ['return', 'enter']:
                self.angle_input_manager.confirm_input()
                return
            elif key == 'escape':
                self.angle_input_manager.cancel_input()
                return
        
        # 自动纠偏快捷键
        if key == 'v':
            self.auto_deskewer.auto_deskew_current()
            return
        elif key == 'b':
            self.auto_deskewer.batch_auto_deskew()
            return
        
        # 霍夫变换方法切换快捷键
        if key == 'h':
            self._cycle_hough_method()
            return
        
        # 常规快捷键处理
        self._handle_shortcuts(key)

    def _cycle_hough_method(self):
        """循环切换霍夫变换方法"""
        methods = ["standard", "probabilistic", "optimized"]
        current_index = methods.index(self.auto_deskewer.hough_method)
        next_index = (current_index + 1) % len(methods)
        self.auto_deskewer.set_hough_method(methods[next_index])
        self.update_status()

    def _handle_shortcuts(self, key):
        """处理快捷键"""
        shortcut_actions = {
            'o': self.open_folder,
            'i': self.open_files,
            'a': self.previous_image,
            'left': self.previous_image,
            'd': self.next_image,
            'right': self.next_image,
            'q': self.rotate_left,
            'e': self.rotate_right,
            'r': self.reset_image,
            'p': self.set_background_color,
            'w': lambda: self._zoom_with_cursor(self.zoom_in),
            'up': lambda: self._zoom_with_cursor(self.zoom_in),
            's': lambda: self._zoom_with_cursor(self.zoom_out),
            'down': lambda: self._zoom_with_cursor(self.zoom_out),
            'l': self.size_lock_manager.toggle_lock,
            'delete': self.initialize_software,
            'escape': self.point_manager.cancel_point_selection
        }
        
        # 数字键进入角度输入模式
        if key in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'period']:
            self.angle_input_manager.angle_input_mode = True
            self.angle_input_manager.temp_angle_str = "0." if key == 'period' else key
            self.update_angle_input_status()
            return
        
        # 执行快捷键动作
        if key in shortcut_actions:
            shortcut_actions[key]()

    def update_angle_input_status(self):
        """更新角度输入状态显示"""
        if self.angle_input_manager.angle_input_mode:
            status_text = self._("angle_input", self.angle_input_manager.temp_angle_str)
            self.status_label.config(text=status_text)
            
            try:
                angle = float(self.angle_input_manager.temp_angle_str) if self.angle_input_manager.temp_angle_str else 0
                self.custom_angle_label.config(text=self._("single_rotation", f"{angle} (inputting)"))
            except ValueError:
                self.custom_angle_label.config(text=self._("single_rotation", self._("invalid_input")))
        else:
            self.update_status()

    def set_background_color(self):
        """设置填充色为光标位置实际显示的颜色"""
        try:
            # 如果有透明通道，显示提示
            if self.image and self.has_alpha_channel(self.image):
                self.status_label.config(text="透明图片：对含透明通道的图片禁用填充色")
                return
            
            # 临时隐藏参考线
            was_visible = self.crosshair_manager.show_crosshair
            self.crosshair_manager.show_crosshair = False
            self.crosshair_manager.clear_crosshair()
            self.canvas.update()
            
            # 短暂延迟确保参考线已完全隐藏
            self.root.update()
            
            # 获取鼠标在屏幕上的绝对位置
            x = self.root.winfo_pointerx()
            y = self.root.winfo_pointery()
            
            # 使用PIL的ImageGrab截取颜色
            from PIL import ImageGrab
            screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
            color = screenshot.getpixel((0, 0))
            
            # 解析颜色
            if len(color) == 4:  # RGBA
                self.bg_color = color[:3]  # 忽略Alpha通道
            elif len(color) == 3:  # RGB
                self.bg_color = color
            else:
                self.bg_color = DEFAULT_BG_COLOR
                
            self.update_status()
            self.status_label.config(text=f"已设置填充色为: {self.bg_color}")
            
            # 恢复参考线
            self.crosshair_manager.show_crosshair = was_visible
            if self.crosshair_manager.is_visible and was_visible:
                self.crosshair_manager.draw_crosshair()
                
        except Exception as e:
            print(f"获取颜色失败: {str(e)}")
            # 确保参考线被恢复
            if 'was_visible' in locals():
                self.crosshair_manager.show_crosshair = was_visible
                if self.crosshair_manager.is_visible and was_visible:
                    self.crosshair_manager.draw_crosshair()
            self.bg_color = DEFAULT_BG_COLOR
            self.update_status()

    def _get_mouse_image_coordinates(self):
        """获取鼠标在图片上的坐标"""
        x = self.root.winfo_pointerx() - self.root.winfo_rootx()
        y = self.root.winfo_pointery() - self.root.winfo_rooty()
        
        canvas_x = x - self.canvas.winfo_x()
        canvas_y = y - self.canvas.winfo_y()
        
        actual_x, actual_y = self._convert_canvas_to_image_coords(canvas_x, canvas_y)
        return x, y, actual_x, actual_y

    def _parse_color_value(self, color):
        """解析颜色值"""
        if isinstance(color, int):
            # 灰度图像
            return (color, color, color)
        elif hasattr(color, '__len__'):
            if len(color) >= 3:
                return tuple(color[:3])
            else:
                return DEFAULT_BG_COLOR
        else:
            return DEFAULT_BG_COLOR

    def zoom_in(self, event=None):
        """放大图片 - 修复抖动问题"""
        if not self.image:
            return
            
        # 获取鼠标位置
        if event:
            mouse_x, mouse_y = event.x, event.y
        else:
            mouse_x = self.canvas.winfo_width() // 2
            mouse_y = self.canvas.winfo_height() // 2
        
        # 保存旧的缩放级别和显示信息
        old_zoom = self.display_manager.zoom_level
        
        if not hasattr(self.display_manager, 'display_info'):
            # 如果没有显示信息，直接缩放
            self.display_manager.zoom_level *= ZOOM_FACTOR
            self.display_manager.zoom_level = min(self.display_manager.zoom_level, MAX_ZOOM_LEVEL)
            self.display_image()
            return
        
        # 计算鼠标在图像上的实际坐标
        display_info = self.display_manager.display_info
        if display_info['scale'] > 0:
            img_x = (mouse_x - display_info['offset_x']) / display_info['scale']
            img_y = (mouse_y - display_info['offset_y']) / display_info['scale']
            
            # 应用缩放
            self.display_manager.zoom_level *= ZOOM_FACTOR
            self.display_manager.zoom_level = min(self.display_manager.zoom_level, MAX_ZOOM_LEVEL)
            
            # 如果缩放级别没有变化，直接返回
            if old_zoom == self.display_manager.zoom_level:
                return
            
            # 预计算新的显示参数
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.image.size
            
            # 计算新的显示尺寸和缩放比例
            if self.display_manager.zoom_mode == "height":
                base_scale = canvas_height / img_height
            else:
                base_scale = canvas_width / img_width
                
            new_scale = base_scale * self.display_manager.zoom_level
            new_scale = min(new_scale, MAX_ZOOM_LEVEL)
            
            display_width = int(img_width * new_scale)
            display_height = int(img_height * new_scale)
            
            # 计算新的偏移量，使鼠标位置保持不变
            new_offset_x = mouse_x - img_x * new_scale
            new_offset_y = mouse_y - img_y * new_scale
            
            # 计算新的平移量
            img_center_x = canvas_width // 2
            img_center_y = canvas_height // 2
            self.display_manager.pan_x = new_offset_x - (img_center_x - display_width // 2)
            self.display_manager.pan_y = new_offset_y - (img_center_y - display_height // 2)
        
        # 只显示一次最终结果
        self.display_image()

    def zoom_out(self, event=None):
        """缩小图片 - 修复抖动问题"""
        if not self.image:
            return
            
        # 获取鼠标位置
        if event:
            mouse_x, mouse_y = event.x, event.y
        else:
            mouse_x = self.canvas.winfo_width() // 2
            mouse_y = self.canvas.winfo_height() // 2
        
        # 保存旧的缩放级别和显示信息
        old_zoom = self.display_manager.zoom_level
        
        if not hasattr(self.display_manager, 'display_info'):
            # 如果没有显示信息，直接缩放
            self.display_manager.zoom_level /= ZOOM_FACTOR
            self.display_manager.zoom_level = max(self.display_manager.zoom_level, MIN_ZOOM_LEVEL)
            self.display_image()
            return
        
        # 计算鼠标在图像上的实际坐标
        display_info = self.display_manager.display_info
        if display_info['scale'] > 0:
            img_x = (mouse_x - display_info['offset_x']) / display_info['scale']
            img_y = (mouse_y - display_info['offset_y']) / display_info['scale']
            
            # 应用缩放
            self.display_manager.zoom_level /= ZOOM_FACTOR
            self.display_manager.zoom_level = max(self.display_manager.zoom_level, MIN_ZOOM_LEVEL)
            
            # 如果缩放级别没有变化，直接返回
            if old_zoom == self.display_manager.zoom_level:
                return
            
            # 预计算新的显示参数
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            img_width, img_height = self.image.size
            
            # 计算新的显示尺寸和缩放比例
            if self.display_manager.zoom_mode == "height":
                base_scale = canvas_height / img_height
            else:
                base_scale = canvas_width / img_width
                
            new_scale = base_scale * self.display_manager.zoom_level
            new_scale = max(new_scale, MIN_ZOOM_LEVEL)  # 注意这里用 max 而不是 min
            
            display_width = int(img_width * new_scale)
            display_height = int(img_height * new_scale)
            
            # 计算新的偏移量，使鼠标位置保持不变
            new_offset_x = mouse_x - img_x * new_scale
            new_offset_y = mouse_y - img_y * new_scale
            
            # 计算新的平移量
            img_center_x = canvas_width // 2
            img_center_y = canvas_height // 2
            self.display_manager.pan_x = new_offset_x - (img_center_x - display_width // 2)
            self.display_manager.pan_y = new_offset_y - (img_center_y - display_height // 2)
        
        # 只显示一次最终结果
        self.display_image()
        
        # 标记需要清除输入
        self.angle_input_manager.should_clear_input = True

    def _zoom_with_cursor(self, zoom_func):
        """使用光标位置进行缩放"""
        # 获取鼠标在画布上的位置
        abs_x = self.root.winfo_pointerx()
        abs_y = self.root.winfo_pointery()
        
        canvas_abs_x = self.root.winfo_rootx() + self.canvas.winfo_x()
        canvas_abs_y = self.root.winfo_rooty() + self.canvas.winfo_y()
        
        canvas_x = abs_x - canvas_abs_x
        canvas_y = abs_y - canvas_abs_y
        
        # 检查鼠标是否在画布范围内
        if (0 <= canvas_x < self.canvas.winfo_width() and 
            0 <= canvas_y < self.canvas.winfo_height()):
            # 创建模拟事件
            class FakeEvent:
                def __init__(self, x, y):
                    self.x = x
                    self.y = y
            fake_event = FakeEvent(canvas_x, canvas_y)
            zoom_func(fake_event)
        else:
            # 如果鼠标不在画布内，不使用事件（将使用画布中心）
            zoom_func(None)

    def _adjust_pan_for_zoom(self, event, old_zoom):
        """调整平移量以实现以光标为中心的缩放"""
        if event and hasattr(self.display_manager, 'display_info') and self.image:
            display_info = self.display_manager.display_info
            
            # 获取当前图像尺寸
            img_width, img_height = self.image.size
            
            # 计算鼠标在图像上的坐标
            if display_info['scale'] > 0:
                # 将鼠标位置转换为图像坐标
                img_x = (event.x - display_info['offset_x']) / display_info['scale']
                img_y = (event.y - display_info['offset_y']) / display_info['scale']
                
                # 确保坐标在图像范围内
                img_x = max(0, min(img_width - 1, img_x))
                img_y = max(0, min(img_height - 1, img_y))
                
                # 计算新的缩放比例
                new_scale = display_info['base_scale'] * self.display_manager.zoom_level
                
                # 计算缩放前后鼠标在图像上的位置对应的画布坐标
                old_canvas_x = img_x * display_info['scale'] + display_info['offset_x']
                old_canvas_y = img_y * display_info['scale'] + display_info['offset_y']
                
                new_canvas_x = img_x * new_scale + display_info['offset_x']
                new_canvas_y = img_y * new_scale + display_info['offset_y']
                
                # 调整平移量，使鼠标位置的图像点在画布上保持固定
                delta_x = new_canvas_x - old_canvas_x
                delta_y = new_canvas_y - old_canvas_y
                
                self.display_manager.pan_x -= delta_x
                self.display_manager.pan_y -= delta_y

    def on_mouse_wheel(self, event):
        """鼠标滚轮事件"""
        if event.delta > 0:
            self.zoom_in(event)
        else:
            self.zoom_out(event)

    def on_middle_click(self, event):
        """中键点击事件 - 切换缩放模式"""
        if self.display_manager.zoom_mode == "height":
            self.display_manager.zoom_mode = "width"
        else:
            self.display_manager.zoom_mode = "height"
            
        self.display_manager.apply_zoom_mode()
        self.display_image()

    def on_right_click_start(self, event):
        """右键开始拖拽"""
        self.display_manager.is_panning = True
        self.display_manager.pan_start_x = event.x
        self.display_manager.pan_start_y = event.y

    def on_right_click_drag(self, event):
        """右键拖拽"""
        if self.display_manager.is_panning:
            dx = event.x - self.display_manager.pan_start_x
            dy = event.y - self.display_manager.pan_start_y
            self.display_manager.pan_x += dx
            self.display_manager.pan_y += dy
            self.display_manager.pan_start_x = event.x
            self.display_manager.pan_start_y = event.y
            self.display_image()

    def on_right_click_end(self, event):
        """右键释放"""
        self.display_manager.is_panning = False

    def on_mouse_move(self, event):
        """鼠标移动事件"""
        # 更新鼠标位置
        self.crosshair_manager.update_mouse_position(event.x, event.y)
        
        # 更新动态连线
        self._update_temp_line(event)

    def _update_temp_line(self, event):
        """更新临时连线"""
        if (self.point_manager.drawing_line and hasattr(self.display_manager, 'display_info') and
            self.point_manager.first_point is not None):
            
            if self.point_manager.temp_line:
                self.canvas.delete(self.point_manager.temp_line)
            
            # 转换当前鼠标位置到图片坐标
            actual_x, actual_y = self._convert_canvas_to_image_coords(event.x, event.y)
            
            # 检查是否在图片范围内
            if self._is_point_in_image(actual_x, actual_y):
                # 计算第一个点在画布上的位置
                x1, y1 = self.point_manager.first_point
                scale = self.display_manager.display_info['scale']
                offset_x = self.display_manager.display_info['offset_x']
                offset_y = self.display_manager.display_info['offset_y']
                
                display_x1 = x1 * scale + offset_x
                display_y1 = y1 * scale + offset_y
                
                # 绘制新的临时连线
                self.point_manager.temp_line = self.canvas.create_line(
                    display_x1, display_y1, event.x, event.y,
                    fill="#DD23DD", width=2, tags="temp_line"
                )

    def on_window_resize(self, event):
        """窗口大小改变事件处理"""
        # 只有当事件是主窗口时才刷新显示
        if event.widget == self.root:
            # 使用 after 方法延迟刷新，避免过于频繁的重绘
            if hasattr(self, '_resize_timer'):
                self.root.after_cancel(self._resize_timer)
            self._resize_timer = self.root.after(100, self.on_resize_display)  # 减少延迟时间

    def on_resize_display(self):
        """窗口大小改变后的显示更新"""
        # 更新主图片显示
        self.display_image()
        
        # 如果没有图片，强制重新显示提示信息
        if not self.image:
            self.canvas.update_idletasks()
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width, canvas_height = 800, 600
            
            # 清除画布并重新显示提示
            self.canvas.delete("all")
            self.show_no_image_prompt(canvas_width, canvas_height)
        
        # 更新缩略图显示
        if self.image_files and self.current_image_index >= 0:
            self.root.after(100, self.scroll_to_current_thumbnail)
        
        # 更新状态显示
        self.update_status()

    def initialize_software(self):
        """重置软件到初始状态"""
        # 保存当前修改
        if self.image and 0 <= self.current_image_index < len(self.image_files):
            filename = self.image_files[self.current_image_index]
            if self.image_modified.get(filename, False):
                response = messagebox.askyesnocancel(
                    self._("save_changes", ""), 
                    self._("save_changes", filename)
                )
                if response is None:  # 用户点击取消
                    return
                elif response:  # 用户点击是
                    self.save_current_image_if_modified()
        
        # 重置所有状态
        self._reset_application_state()
        
        # 清空界面并显示初始提示
        self._reset_ui()
        
        print("Software reset to initial state")

    def _reset_application_state(self):
        """重置应用程序状态"""
        self.image_folder = ""
        self.image_files = []
        self.current_image_index = -1
        self.image = None
        self.photo = None
        self.original_image = None
        self.rotation_angle = 0
        
        # 重置各个管理器状态
        self.display_manager.zoom_level = 1.0
        self.display_manager.pan_x = 0
        self.display_manager.pan_y = 0
        self.crosshair_manager.set_visibility(False)
        self.thumbnail_manager.cache = {}
        self.image_modified = {}
        self.point_manager.reset_points()
        self.size_lock_manager.lock_size = False
        self.size_lock_manager.original_size = None
        self.auto_deskewer.is_batch_deskewing = False
        self.auto_deskewer.stop_batch_deskewion = True

    def _reset_ui(self):
        """重置用户界面"""
        # 清空缩略图区域
        self.thumbnail_manager.clear()

        # 隐藏缩略图区域
        thumbs_frame = self.thumbnail_frame.master
        thumbs_frame.grid_remove()

        # 清空画布
        self.canvas.delete("all")
        self.canvas.update_idletasks()
        
        # 显示初始提示
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            canvas_width, canvas_height = 800, 600
        
        self.show_no_image_prompt(canvas_width, canvas_height)
        
        # 更新状态显示
        self.update_status()
        
        # 更新状态标签
        status_text = self._("select_folder_or_drag") if HAS_DND else self._("select_folder_only")
        self.status_label.config(text=status_text)

    def toggle_language_simple(self):
        """切换语言"""
        try:
            # 切换语言
            if self.i18n.current_language == 'zh_CN':
                self.i18n.current_language = 'en_US'
                status_text = "Switched to English"
            else:
                self.i18n.current_language = 'zh_CN'
                status_text = "已切换到中文"
            
            # 更新窗口标题
            self.root.title(self._("window_title"))
            
            # 更新状态栏
            self.status_label.config(text=status_text)
            
            # 保存当前状态
            current_image_index = self.current_image_index
            has_image = self.image is not None
            
            # 清除并重新创建UI
            for widget in self.root.winfo_children():
                widget.destroy()
            
            self._create_ui()
            self._setup_bindings()
            
            # 恢复状态
            if has_image and 0 <= current_image_index < len(self.image_files):
                self.current_image_index = current_image_index
                self.load_current_image()
                self.update_thumbnails()
            
            self.update_status()
            
            print(f"语言已切换到: {self.i18n.current_language}")
            
            # 如果没有图片，立即重绘画布
            if not self.image:
                self.force_display_prompt()  # 使用现有的方法
        
        except Exception as e:
            print(f"语言切换失败: {e}")

    def open_help_webpage(self):
        """使用系统默认浏览器打开官方网页"""
        try:
            import webbrowser
            if self.i18n.current_language == 'zh_CN':
                url = "https://gitee.com/distinctive-mark/PicdocDeskew"
            else:
                url = "https://github.com/distinctive-mark/PicdocDeskew"
            webbrowser.open(url)
            print(f"已打开网页: {url}")
        except Exception as e:
            print(f"打开网页失败: {str(e)}")
            messagebox.showerror("错误", f"无法打开网页: {str(e)}")

    def has_alpha_channel(self, image):
        """检查图片是否有透明通道"""
        return image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info)

def main():
    # 根据是否支持拖拽创建不同的窗口
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
        
    app = AdvancedImageRotator(root)
    root.mainloop()

if __name__ == "__main__":
    main()
