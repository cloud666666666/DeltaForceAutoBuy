import json
import pyautogui
import cv2
import numpy as np
import time
import pytesseract
import os
import keyboard  # 用于监听键盘事件
import win32gui
import win32con
import win32api
import datetime  # 用于时间处理
import sys
import ctypes  # 用于检查管理员权限
import logging  # 用于日志记录
import shutil   # 用于清除文件夹

# 截图保存路径
SCREENSHOTS_DIR = "screenshots"

def clear_screenshots_folder():
    """清除截图文件夹"""
    try:
        # 确保路径存在
        if not os.path.exists(SCREENSHOTS_DIR):
            os.makedirs(SCREENSHOTS_DIR)
            print(f"✅ 创建截图文件夹: {SCREENSHOTS_DIR}")
            return
            
        # 清除文件夹中的所有文件
        for filename in os.listdir(SCREENSHOTS_DIR):
            file_path = os.path.join(SCREENSHOTS_DIR, filename)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"❌ 无法删除文件 {file_path}: {e}")
        
        print(f"✅ 已清除截图文件夹: {SCREENSHOTS_DIR}")
    except Exception as e:
        print(f"❌ 清除截图文件夹失败: {e}")
        # 如果清除失败，尝试创建文件夹
        try:
            if not os.path.exists(SCREENSHOTS_DIR):
                os.makedirs(SCREENSHOTS_DIR)
        except:
            pass

def is_admin():
    """检查是否以管理员身份运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def check_admin_privileges():
    """检查并提示管理员权限"""
    if not is_admin():
        print("⚠️  警告：程序未以管理员身份运行")
        print("🔒 这可能导致以下问题：")
        print("   - 无法发送键盘/鼠标事件到游戏")
        print("   - 热键(F8/F9)可能无法响应")
        print("   - 程序功能受限")
        print()
        print("💡 解决方案：")
        print("   1. 右键点击程序 → 选择'以管理员身份运行'")
        print("   2. 或使用提供的'以管理员身份运行.bat'文件")
        print()
        
        try:
            choice = input("是否继续运行程序？(y/n): ").strip().lower()
            if choice != 'y':
                print("程序已退出")
                sys.exit(0)
        except KeyboardInterrupt:
            print("\n程序已退出")
            sys.exit(0)
        
        print("⚠️  继续以普通权限运行，功能可能受限")
        print("=" * 50)
    else:
        print("✅ 管理员权限已获得")

# 获取资源文件路径（支持打包后的exe）
def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持开发环境和打包后的exe"""
    try:
        # PyInstaller创建临时文件夹，并将路径存储在_MEIPASS中
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境中使用脚本所在目录，而不是当前工作目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)

# 配置部分 - 配置文件应该在exe所在目录，而不是临时目录
def get_config_file_path():
    """获取配置文件路径，确保在exe所在目录而不是临时目录"""
    try:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # 打包后的exe，使用exe文件所在目录
            base_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境，使用脚本文件所在目录
            base_dir = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        base_dir = os.getcwd()
    
    config_file = os.path.join(base_dir, 'keys.json')
    
    # 如果配置文件不存在，从资源目录复制一份
    if not os.path.exists(config_file):
        try:
            default_config = get_resource_path('keys.json')
            if os.path.exists(default_config):
                import shutil
                shutil.copy2(default_config, config_file)
                print(f"✅ 已创建配置文件: {config_file}")
        except Exception as e:
            print(f"⚠️ 创建配置文件失败: {e}")
    
    return config_file

CONFIG_FILE = get_config_file_path()

# Tesseract 环境配置 - 使用资源路径
TESSERACT_PATH = get_resource_path('Tesseract')
TESSERACT_EXE = os.path.join(TESSERACT_PATH, 'tesseract.exe')
TESSDATA_PATH = os.path.join(TESSERACT_PATH, 'tessdata')

# 日志配置
def setup_logger():
    """设置日志记录器"""
    # 简化日志路径，直接在当前目录创建日志文件
    try:
        # 对于打包后的exe，使用exe文件所在目录
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller打包后的exe，使用exe文件所在目录
            base_dir = os.path.dirname(sys.executable)
        else:
            # 开发环境，使用脚本文件所在目录
            base_dir = os.path.dirname(os.path.abspath(__file__))
    except Exception:
        # 如果获取路径失败，使用当前工作目录
        base_dir = os.getcwd()
    
    # 直接在基础目录创建日志文件，不创建子目录
    log_file = os.path.join(base_dir, "price_log.txt")
    
    # 配置日志记录器
    logger = logging.getLogger('price_logger')
    logger.setLevel(logging.INFO)
    
    # 移除旧的handler，避免重复写入
    if logger.hasHandlers():
        logger.handlers.clear()
    
    # 文件处理器（覆盖写入）
    file_handler = logging.FileHandler(log_file, encoding='utf-8', mode='w')
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # 只有警告和错误会显示在控制台
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 初始化日志记录器
price_logger = setup_logger()

# # 设置Tesseract路径
# print(f"🔍 当前工作目录: {os.getcwd()}")
# print(f"🔍 查找Tesseract路径: {TESSERACT_PATH}")
# print(f"🔍 Tesseract exe路径: {TESSERACT_EXE}")
# print(f"🔍 tessdata路径: {TESSDATA_PATH}")

# if os.path.exists(TESSERACT_PATH):
#     print(f"✅ Tesseract文件夹存在")
#     # 列出Tesseract文件夹内容
#     try:
#         files = os.listdir(TESSERACT_PATH)
#         print(f"🔍 Tesseract文件夹内容: {files}")
#     except Exception as e:
#         print(f"❌ 无法读取Tesseract文件夹: {e}")
# else:
#     print(f"❌ Tesseract文件夹不存在: {TESSERACT_PATH}")

if os.path.exists(TESSERACT_EXE):
    # print(f"✅ tesseract.exe存在")
    os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_EXE
    # print(f"✅ 已设置Tesseract路径: {TESSERACT_EXE}")
    
    # 测试Tesseract是否能正常工作
    # try:
    #     version = pytesseract.get_tesseract_version()
    #     print(f"✅ Tesseract版本: {version}")
    # except Exception as e:
    #     print(f"❌ Tesseract测试失败: {e}")
else:
    print(f"❌ 未找到Tesseract: {TESSERACT_EXE}")
    print("请确保Tesseract文件夹在程序目录中")
    
    # 尝试其他可能的路径
    alternative_paths = [
        "tesseract/tesseract.exe",
        "./tesseract/tesseract.exe",
        "./Tesseract/tesseract.exe",
        "Tesseract/tesseract.exe"
    ]
    
    for alt_path in alternative_paths:
        full_path = os.path.abspath(alt_path)
        if os.path.exists(full_path):
            pytesseract.pytesseract.tesseract_cmd = full_path
            tessdata_dir = os.path.join(os.path.dirname(full_path), 'tessdata')
            if os.path.exists(tessdata_dir):
                os.environ["TESSDATA_PREFIX"] = tessdata_dir
            print(f"✅ 使用备用路径: {full_path}")
            break

# 全局变量
keys_config = None
is_running = False  # 控制循环是否运行
is_paused = False   # 控制循环是否暂停
screen_width, screen_height = pyautogui.size()
game_window = None  # 游戏窗口信息

def find_game_window():
    """查找游戏窗口"""
    global game_window
    
    game_titles = ["三角洲行动", "Delta Force", "DeltaForce", "UnrealWindow"]
    exclude_titles = ["Cursor", "Visual Studio", "Code", "Explorer", "Chrome", 
                     "Firefox", "Edge", "Discord", "QQ", "WeChat", "Steam", 
                     "Epic Games", "TaskManager", "cmd", "PowerShell", "Python"]
    
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            
            for exclude in exclude_titles:
                if exclude.lower() in window_title.lower():
                    return True
            
            for title in game_titles:
                if title.lower() in window_title.lower():
                    rect = win32gui.GetWindowRect(hwnd)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]
                    
                    if width >= 800 and height >= 600:
                        windows.append({
                            'hwnd': hwnd,
                            'title': window_title,
                            'rect': rect,
                            'width': width,
                            'height': height
                        })
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    if windows:
        game_window = max(windows, key=lambda w: w['width'] * w['height'])
        return game_window
    else:
        return None

def get_game_coordinates():
    """获取游戏坐标系统"""
    global game_window
    
    game_window = find_game_window()
    
    if game_window:
        try:
            hwnd = game_window['hwnd']
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.1)
            
            current_rect = win32gui.GetWindowRect(hwnd)
            left, top, right, bottom = current_rect
            width = right - left
            height = bottom - top
            
            return {
                'offset_x': left,
                'offset_y': top,
                'width': width,
                'height': height,
                'mode': 'windowed'
            }
            
        except Exception as e:
            pass
    
    return {
        'offset_x': 0,
        'offset_y': 0,
        'width': screen_width,
        'height': screen_height,
        'mode': 'fullscreen'
    }

def load_keys_config():
    """加载钥匙价格配置文件"""
    global keys_config
    if keys_config is not None:
        return keys_config
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            keys_config = config.get('keys', [])
            return keys_config
    except Exception as e:
        print(f"配置文件加载失败: {str(e)}")
        return []

def take_screenshot(region):
    """截图功能"""
    try:
        screenshot = pyautogui.screenshot(region=region)
        screenshot_array = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        return screenshot_array
    except Exception as e:
        return None

def getCardPrice(price_region=None, coords=None, debug_mode=True):
    """获取当前卡片价格，并可选择显示调试信息"""
    try:
        if coords is None:
            coords = get_game_coordinates()
        
        game_width = coords['width']
        game_height = coords['height']
        offset_x = coords['offset_x']
        offset_y = coords['offset_y']
        
        # 确定价格识别区域
        if price_region and price_region.get('top_left') and price_region.get('bottom_right'):
            top_left = price_region['top_left']
            bottom_right = price_region['bottom_right']
            
            if (top_left[0] > 0 and top_left[1] > 0 and 
                bottom_right[0] > 0 and bottom_right[1] > 0):
                
                region_left = offset_x + int(game_width * top_left[0])
                region_top = offset_y + int(game_height * top_left[1])
                region_width = int(game_width * (bottom_right[0] - top_left[0]))
                region_height = int(game_height * (bottom_right[1] - top_left[1]))
                region = (region_left, region_top, region_width, region_height)
            else:
                region_width = int(game_width * 0.15)
                region_height = int(game_height * 0.08)
                region_left = offset_x + int(game_width * 0.35)
                region_top = offset_y + int(game_height * 0.27)
                region = (region_left, region_top, region_width, region_height)
        else:
            region_width = int(game_width * 0.15)
            region_height = int(game_height * 0.08)
            region_left = offset_x + int(game_width * 0.35)
            region_top = offset_y + int(game_height * 0.27)
            region = (region_left, region_top, region_width, region_height)
        
        # 截取整个游戏窗口
        if debug_mode:
            full_game_region = (offset_x, offset_y, game_width, game_height)
            full_screenshot = take_screenshot(region=full_game_region)
            
            if full_screenshot is None:
                return None
                
            # 在全屏截图上画出识别区域的红色框
            roi_x = region_left - offset_x
            roi_y = region_top - offset_y
            roi_w = region_width
            roi_h = region_height
            
            # 在全屏截图上画红框
            cv2.rectangle(full_screenshot, 
                         (roi_x, roi_y), 
                         (roi_x + roi_w, roi_y + roi_h), 
                         (0, 0, 255), 2)  # 红色，线宽2
            
            # 从全屏截图中提取ROI区域进行识别
            roi_screenshot = full_screenshot[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
            
            # 显示调试窗口
            cv2.imshow("游戏窗口 - 价格识别区域", full_screenshot)
            cv2.waitKey(1)  # 显示1毫秒，不阻塞程序
            
            # 保存截图
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            
            # 确保screenshots文件夹存在
            if not os.path.exists(SCREENSHOTS_DIR):
                try:
                    os.makedirs(SCREENSHOTS_DIR)
                except:
                    pass
            
            # 保存全屏带标记的截图
            full_img_path = os.path.join(SCREENSHOTS_DIR, f"full_{timestamp}.jpg")
            cv2.imwrite(full_img_path, full_screenshot)
            
            # 保存ROI区域截图
            roi_img_path = os.path.join(SCREENSHOTS_DIR, f"roi_{timestamp}.jpg")
            cv2.imwrite(roi_img_path, roi_screenshot)
        else:
            # 直接截取识别区域
            roi_screenshot = take_screenshot(region=region)
            if roi_screenshot is None:
                return None
        
        # 图像预处理，提高OCR识别成功率
        def preprocess_image(img):
            # 转换为灰度图
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # 应用高斯模糊去噪
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 自适应阈值处理，增强对比度
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # 形态学操作，清理噪点
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
        
        # 预处理图像
        processed_img = preprocess_image(roi_screenshot)
        
        # 如果是调试模式，保存预处理后的图像
        if debug_mode:
            processed_img_path = os.path.join(SCREENSHOTS_DIR, f"processed_{timestamp}.jpg")
            cv2.imwrite(processed_img_path, processed_img)
        
        # 优化后的OCR识别方法 - 只使用最成功的配置
        ocr_configs = [
            # 配置1：PSM 6 统一文本块模式（从日志看最成功）
            ("--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789,", "PSM6"),
            # 配置2：PSM 7 单行文本模式（备用）
            ("--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789,", "PSM7"),
            # 配置3：PSM 8 单个词模式（最后尝试）
            ("--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789,", "PSM8")
        ]
        
        # 尝试原始图像和预处理图像
        images_to_try = [
            (roi_screenshot, "原始"),
            (processed_img, "预处理")
        ]
        
        for img, img_type in images_to_try:
            for config, config_name in ocr_configs:
                try:
                    text = pytesseract.image_to_string(img, lang='eng', config=config)
                    cleaned_text = text.replace(",", "").replace(" ", "").replace("\n", "").strip()
                    
                    if cleaned_text and cleaned_text.isdigit():
                        price = int(cleaned_text)
                        if 10000 <= price <= 100000000:
                            # 如果是调试模式，保存识别结果到文件名
                            if debug_mode:
                                # 创建一个结果文件，包含识别到的价格
                                result_path = os.path.join(SCREENSHOTS_DIR, f"result_{timestamp}_{price}.txt")
                                with open(result_path, 'w') as f:
                                    f.write(f"识别价格: {price}\n")
                                    f.write(f"配置: {config_name}\n")
                                    f.write(f"图像类型: {img_type}\n")
                            return price
                        
                except Exception:
                    continue
        
        # 所有方法都失败时才记录失败
        if debug_mode:
            # 创建一个失败记录文件
            fail_path = os.path.join(SCREENSHOTS_DIR, f"fail_{timestamp}.txt")
            with open(fail_path, 'w') as f:
                f.write("识别失败\n")
        
        return None
    except Exception as e:
        return None

def getCardName(name_region=None, coords=None):
    """获取当前卡片名称"""
    try:
        # 如果没有传递坐标，则重新获取
        if coords is None:
            coords = get_game_coordinates()
        
        game_width = coords['width']
        game_height = coords['height']
        offset_x = coords['offset_x']
        offset_y = coords['offset_y']
        
        # 如果提供了自定义截图区域，使用自定义区域
        if name_region and name_region.get('top_left') and name_region.get('bottom_right'):
            top_left = name_region['top_left']
            bottom_right = name_region['bottom_right']
            
            # 检查坐标是否有效（不为0）
            if (top_left[0] > 0 and top_left[1] > 0 and 
                bottom_right[0] > 0 and bottom_right[1] > 0):
                
                region_left = offset_x + int(game_width * top_left[0])
                region_top = offset_y + int(game_height * top_left[1])
                region_width = int(game_width * (bottom_right[0] - top_left[0]))
                region_height = int(game_height * (bottom_right[1] - top_left[1]))
                region = (region_left, region_top, region_width, region_height)
                print(f"[OCR] 使用自定义名称区域: {name_region}")
            else:
                # 使用默认区域
                region_width = int(game_width * 0.18)
                region_height = int(game_height * 0.05)
                region_left = offset_x + int(game_width * 0.18)
                region_top = offset_y + int(game_height * 0.19)
                region = (region_left, region_top, region_width, region_height)
                print(f"[OCR] 使用默认名称区域（自定义区域无效）")
        else:
            # 使用默认区域
            region_width = int(game_width * 0.18)
            region_height = int(game_height * 0.05)
            region_left = offset_x + int(game_width * 0.18)
            region_top = offset_y + int(game_height * 0.19)
            region = (region_left, region_top, region_width, region_height)
            print(f"[OCR] 使用默认名称区域")
        
        screenshot = take_screenshot(region=region)
        if screenshot is None:
            return ""
        
        # 使用中英文混合OCR识别，增加更多配置尝试
        configs = [
            ("chi_sim+eng", "--psm 7 --oem 3"),  # 中英文混合，单行文本
            ("chi_sim+eng", "--psm 8 --oem 3"),  # 中英文混合，单个词
            ("chi_sim+eng", "--psm 6 --oem 3"),  # 中英文混合，统一文本块
            ("eng", "--psm 7 --oem 3"),          # 纯英文，单行文本
            ("chi_sim", "--psm 7 --oem 3"),      # 纯中文，单行文本
            ("eng", "--psm 8 --oem 3"),          # 纯英文，单个词
            ("chi_sim", "--psm 8 --oem 3"),      # 纯中文，单个词
        ]
        
        results = []
        
        for lang, config in configs:
            try:
                # 获取带置信度的结果
                data = pytesseract.image_to_data(screenshot, lang=lang, config=config, output_type=pytesseract.Output.DICT)
                
                # 计算平均置信度
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                if confidences:
                    avg_confidence = sum(confidences) / len(confidences)
                    text = pytesseract.image_to_string(screenshot, lang=lang, config=config)
                    text = text.replace(" ", "").replace("\n", "").strip()
                    
                    # 过滤明显错误的结果
                    if len(text) > 0 and avg_confidence > 30:
                        # 检查是否包含常见的错误字符
                        error_chars = ['—', '|', '\\', '/', '_', '`', '~']
                        if not any(char in text for char in error_chars):
                            results.append((text, avg_confidence, lang))
            except:
                continue
        
        # 按置信度排序
        results.sort(key=lambda x: x[1], reverse=True)
        
        # 如果有结果，返回置信度最高的
        if results:
            best_text, best_conf, best_lang = results[0]
            print(f"[OCR] 原始识别: '{best_text}' (置信度: {best_conf:.1f}, 语言: {best_lang})")
            
            # 清理文本，去除常见的多余部分
            cleaned_text = best_text
            
            # 去除常见的界面文字
            remove_prefixes = ['我的收藏', '收藏', '门卡', '卡片']
            for prefix in remove_prefixes:
                if cleaned_text.startswith(prefix):
                    cleaned_text = cleaned_text[len(prefix):]
            
            # 去除常见的后缀
            remove_suffixes = ['RS', 'R', 'S', 'RR', 'SS']
            for suffix in remove_suffixes:
                if cleaned_text.endswith(suffix) and len(cleaned_text) > len(suffix):
                    cleaned_text = cleaned_text[:-len(suffix)]
            
            # 修正常见的OCR错误
            ocr_corrections = {
                'Retink': 'Relink',
                'Re1ink': 'Relink',
                'ReIink': 'Relink',
                'Re1ink': 'Relink'
            }
            
            for wrong, correct in ocr_corrections.items():
                cleaned_text = cleaned_text.replace(wrong, correct)
            
            cleaned_text = cleaned_text.strip()
            
            if cleaned_text != best_text:
                print(f"[OCR] 清理后: '{cleaned_text}'")
            
            return cleaned_text
        
        return ""
        
    except Exception as e:
        print(f"[错误] 获取卡片名称失败: {str(e)}")
        return ""

def price_check_flow(card_info, force_buy=False, debug_mode=True):
    """价格检查主流程"""
    global is_paused
    
    try:
        coords = get_game_coordinates()
        game_width = coords['width']
        game_height = coords['height']
        offset_x = coords['offset_x']
        offset_y = coords['offset_y']
        
        position = card_info.get('position')
        if not position or len(position) < 2:
            return False
            
        if (position[0] > 0 and position[1] > 0):
            click_x = offset_x + int(game_width * position[0])
            click_y = offset_y + int(game_height * position[1])
            
            try:
                if game_window and game_window.get('hwnd'):
                    win32gui.SetForegroundWindow(game_window['hwnd'])
                    time.sleep(0.05)
            except:
                pass
            
            pyautogui.moveTo(click_x, click_y)
            time.sleep(0.05)
            pyautogui.click(click_x, click_y, button='left')
            
            try:
                client_x = click_x - offset_x
                client_y = click_y - offset_y
                lParam = (client_y << 16) | (client_x & 0xFFFF)
                win32gui.SendMessage(game_window['hwnd'], win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
                time.sleep(0.02)
                win32gui.SendMessage(game_window['hwnd'], win32con.WM_LBUTTONUP, 0, lParam)
            except:
                pass
        else:
            return False
        
        # 等待界面加载并循环尝试识别价格，直到成功或超时
        detail_price_region = card_info.get('detail_price_region', card_info.get('price_region'))
        current_price = None
        max_attempts = 10  # 最多尝试10次
        attempt = 0
        
        while current_price is None and attempt < max_attempts:
            # time.sleep(0.3)  # 每次尝试间隔0.3秒
            current_price = getCardPrice(detail_price_region, coords, debug_mode=debug_mode)
            attempt += 1
            
            # 如果用户按了停止键，立即退出
            if not is_running:
                pyautogui.press('esc')
                return False
        
        # 如果超时仍未识别到价格，按ESC退出
        if current_price is None:
            pyautogui.press('esc')
            # time.sleep(0.05)
            return False
        
    except Exception as e:
        pyautogui.press('esc')
        return False
    
    max_price = card_info.get('max_price', 0)
    
    if max_price == 0 and not force_buy:
        pyautogui.press('esc')
        return False
    
    # 确保价格数据类型正确
    try:
        current_price = int(current_price) if current_price is not None else 0
        max_price = int(max_price) if max_price is not None else 0
    except (ValueError, TypeError):
        # print(f"❌ 价格数据类型错误: current_price={current_price}, max_price={max_price}")
        pyautogui.press('esc')
        return False
    
    if force_buy:
        print(f"🕐 定时购买模式 | 当前价格: {current_price:,}")
        # 定时购买模式不记录日志，因为没有价格比较
        will_buy = True
    else:
        print(f"💰 价格模式 | 最高价格: {max_price:,} | 当前价格: {current_price:,}")
        # 只记录价格模式的比较结果
        price_logger.info(f"价格模式 | 最高价格: {max_price:,} | 当前价格: {current_price:,} | 是否购买: {current_price <= max_price}")
        will_buy = current_price <= max_price
        
        # 增加调试信息
        # if will_buy:
        #     print(f"✅ 价格符合条件，准备购买 ({current_price:,} <= {max_price:,})")
        # else:
        #     print(f"❌ 价格超出预算，跳过购买 ({current_price:,} > {max_price:,})")
    
    if will_buy:
        try:
            buy_x = offset_x + int(game_width * 0.825)
            buy_y = offset_y + int(game_height * 0.852)
            
            # print(f"🖱️ 点击购买按钮位置: ({buy_x}, {buy_y})")
            pyautogui.moveTo(buy_x, buy_y)
            time.sleep(0.1)
            pyautogui.click()
            time.sleep(0.4)
            
            print(f"✅ 已购买门卡, 价格: {current_price:,}")
            # 购买成功不记录日志，只在控制台显示
            pyautogui.press('esc')
            return True
            
        except Exception as e:
            # print(f"❌ 购买过程出错: {str(e)}")
            pyautogui.press('esc')
            return False
    else:
        pyautogui.press('esc')
        time.sleep(0.05)  # 最小延时确保ESC生效
        return False

def start_loop():
    """开始循环"""
    global is_running, is_paused
    is_running = True
    is_paused = False
    print("✅ 开始自动购买")
    # 开始购买不记录日志

def stop_loop():
    """停止循环"""
    global is_running, is_paused
    is_running = False
    is_paused = False
    print("⏹️ 停止循环")
    print_price_stats()

def emergency_exit():
    """紧急退出程序"""
    global is_running, is_paused
    is_running = False
    is_paused = False
    print("\n🚨 程序已终止")
    import sys
    sys.exit(0)

def edit_config():
    """交互式编辑配置文件 - 只编辑第一张门卡"""
    print("\n=== 配置编辑器 ===")
    
    # 加载当前配置
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            keys_config = config.get('keys', [])
    except Exception as e:
        print(f"❌ 无法加载配置文件: {str(e)}")
        return
    
    if not keys_config:
        print("❌ 配置文件中没有门卡配置")
        return
    
    # 只编辑第一张门卡
    card = keys_config[0]
    
    while True:
        # 显示当前门卡信息
        price = card.get('max_price', 0)
        amount = card.get('buyAmount', 0)
        start_time = card.get('scheduledTime', '未设置')
        run_duration = card.get('runDuration', 1)
        
        print(f"\n📋 当前门卡配置:")
        print(f"  最高价格: {price:,}")
        print(f"  购买数量: {amount}")
        print(f"  开始时间: {start_time}")
        print(f"  运行时长: {run_duration}分钟")
        
        print(f"\n📝 编辑选项:")
        print("  1 - 修改最高价格")
        print("  2 - 修改购买数量")
        print("  3 - 修改开始时间")
        print("  4 - 修改运行时长")
        print("  s - 保存并退出")
        print("  q - 不保存退出")
        
        try:
            choice = input("\n请选择操作: ").strip().lower()
            
            if choice == 'q':
                print("❌ 已取消，未保存修改")
                return
            elif choice == 's':
                # 保存配置
                try:
                    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                        json.dump(config, f, ensure_ascii=False, indent=4)
                    print("✅ 配置已保存")
                    return
                except Exception as e:
                    print(f"❌ 保存失败: {str(e)}")
                    continue
            elif choice == '1':
                # 修改价格
                edit_price(card)
            elif choice == '2':
                # 修改数量
                edit_amount(card)
            elif choice == '3':
                # 修改开始时间
                edit_start_time(card)
            elif choice == '4':
                # 修改运行时长
                edit_end_time(card)
            else:
                print("❌ 无效选择")
        except KeyboardInterrupt:
            print("\n❌ 已取消")
            return
        except Exception as e:
            print(f"❌ 输入错误: {str(e)}")

def edit_price(card):
    """修改门卡价格"""
    current_price = card.get('max_price', 0)
    while True:
        try:
            new_price_input = input(f"\n💰 当前最高价格: {current_price:,}\n请输入新价格 (直接回车取消): ").strip()
            
            if new_price_input == "":
                return
            
            new_price = int(new_price_input.replace(",", "").replace(" ", ""))
            if new_price > 0:
                card['max_price'] = new_price
                print(f"✅ 价格已更新: {new_price:,}")
                return
            else:
                print("❌ 价格必须大于0")
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            return

def edit_amount(card):
    """修改购买数量"""
    current_amount = card.get('buyAmount', 0)
    while True:
        try:
            new_amount_input = input(f"\n📦 当前购买数量: {current_amount}\n请输入新数量 (直接回车取消): ").strip()
            
            if new_amount_input == "":
                return
            
            new_amount = int(new_amount_input.replace(" ", ""))
            if new_amount > 0:
                card['buyAmount'] = new_amount
                print(f"✅ 数量已更新: {new_amount}")
                return
            else:
                print("❌ 数量必须大于0")
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            return

def edit_start_time(card):
    """修改开始时间"""
    current_time = card.get('scheduledTime', '未设置')
    while True:
        try:
            print(f"\n⏰ 当前开始时间: {current_time}")
            print("格式: HH:MM (24小时制), 例如: 14:30")
            new_time_input = input("请输入新的开始时间 (直接回车取消, 输入 'none' 清除时间): ").strip()
            
            if new_time_input == "":
                return
            elif new_time_input.lower() == 'none':
                if 'scheduledTime' in card:
                    del card['scheduledTime']
                print("✅ 开始时间已清除")
                return
            else:
                # 验证时间格式
                datetime.datetime.strptime(new_time_input, "%H:%M")
                card['scheduledTime'] = new_time_input
                print(f"✅ 开始时间已更新: {new_time_input}")
                return
        except ValueError:
            print("❌ 时间格式错误，请使用 HH:MM 格式")
        except KeyboardInterrupt:
            return

def edit_end_time(card):
    """修改运行时长"""
    current_duration = card.get('runDuration', 1)
    while True:
        try:
            print(f"\n🔴 当前运行时长: {current_duration}分钟")
            print("程序将在启动后运行指定分钟数然后自动停止")
            print("例如: 输入 5 表示运行5分钟后自动停止")
            new_duration_input = input("请输入新的运行时长 (分钟，直接回车取消, 输入 'none' 清除): ").strip()
            
            if new_duration_input == "":
                return
            elif new_duration_input.lower() == 'none':
                if 'runDuration' in card:
                    del card['runDuration']
                print("✅ 运行时长已清除 (程序将持续运行)")
                return
            else:
                # 验证输入是否为正数
                new_duration = float(new_duration_input)
                if new_duration > 0:
                    card['runDuration'] = new_duration
                    print(f"✅ 运行时长已更新: {new_duration}分钟")
                    return
                else:
                    print("❌ 运行时长必须大于0")
        except ValueError:
            print("❌ 请输入有效的数字")
        except KeyboardInterrupt:
            return

def print_price_stats():
    """统计并显示本次日志的价格数据"""
    try:
        import re
        # 获取日志文件路径，与setup_logger保持一致
        try:
            if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
                base_dir = os.path.dirname(sys.executable)
            else:
                base_dir = os.path.dirname(os.path.abspath(__file__))
        except Exception:
            base_dir = os.getcwd()
        log_file = os.path.join(base_dir, 'price_log.txt')
        prices = []
        if os.path.exists(log_file):
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    m = re.search(r'当前价格: ([\d,]+)', line)
                    if m:
                        price = int(m.group(1).replace(',', ''))
                        prices.append(price)
            if prices:
                avg_price = sum(prices) / len(prices)
                max_price = max(prices)
                min_price = min(prices)
                print("\n📊 本次价格统计：")
                print(f"  平均价格: {avg_price:.2f}")
                print(f"  最高价格: {max_price}")
                print(f"  最低价格: {min_price}")
            else:
                print("\n📊 日志中未找到价格数据")
        else:
            print("\n📊 未找到日志文件")
    except Exception as e:
        print(f"\n❌ 统计日志价格出错: {e}")

def main():
    global is_running, is_paused, keys_config
    
    print("=== 三角洲行动 自动购买助手 ===")
    
    # 清除之前的截图
    clear_screenshots_folder()
    
    # 程序启动不记录日志
    
    keys_config = load_keys_config()
    if not keys_config:
        print("❌ 无法加载配置文件")
        # 配置文件加载失败不记录日志
        return
    
    # 过滤出需要购买的门卡（兼容旧的wantBuy和新的buyAmount）
    cards_to_buy = []
    for card in keys_config:
        # 兼容旧的 wantBuy 字段和新的 buyAmount 字段
        buy_amount = card.get('buyAmount', card.get('wantBuy', 0))
        if buy_amount > 0:
            card['buyAmount'] = buy_amount  # 标准化为 buyAmount
            cards_to_buy.append(card)
    
    if not cards_to_buy:
        print("❌ 没有需要购买的门卡")
        return
    
    # 显示当前配置
    print(f"\n📋 当前配置:")
    card = cards_to_buy[0]  # 只显示第一张卡的配置
    price = card.get('max_price', 0)
    amount = card.get('buyAmount', 0)
    start_time = card.get('scheduledTime', '未设置')
    run_duration = card.get('runDuration', 1)
    
    print(f"  最高价格: {price:,}")
    print(f"  购买数量: {amount}")
    print(f"  开始时间: {start_time}")
    print(f"  运行时长: {run_duration}分钟")
    
    # 询问是否启用调试模式
    debug_mode = False
    try:
        debug_choice = input("\n是否启用调试模式? (y/回车跳过): ").strip().lower()
        if debug_choice == 'y':
            debug_mode = True
            print("✅ 已启用调试模式，将显示识别区域")
        else:
            print("❌ 调试模式已关闭")
    except KeyboardInterrupt:
        print("\n程序退出")
        return
    
    # 询问是否需要编辑配置
    try:
        edit_choice = input("\n是否需要修改配置? (y/回车跳过): ").strip().lower()
        if edit_choice == 'y':
            edit_config()
            # 清除配置缓存并重新加载配置
            keys_config = None  # 清除缓存
            keys_config = load_keys_config()
            if not keys_config:
                print("❌ 重新加载配置失败")
                return
            
            # 重新筛选卡片
            cards_to_buy = []
            for card in keys_config:
                buy_amount = card.get('buyAmount', card.get('wantBuy', 0))
                if buy_amount > 0:
                    card['buyAmount'] = buy_amount
                    cards_to_buy.append(card)
            
            if not cards_to_buy:
                print("❌ 没有需要购买的门卡")
                return
                
            # 显示更新后的配置
            print(f"\n📋 更新后的配置:")
            card = cards_to_buy[0]  # 只显示第一张卡的配置
            price = card.get('max_price', 0)
            amount = card.get('buyAmount', 0)
            start_time = card.get('scheduledTime', '未设置')
            run_duration = card.get('runDuration', 1)
            print(f"  最高价格: {price:,}")
            print(f"  购买数量: {amount}")
            print(f"  开始时间: {start_time}")
            print(f"  运行时长: {run_duration}分钟")
    except KeyboardInterrupt:
        print("\n程序退出")
        return
    
    # 继续原有的启动流程
    coords = get_game_coordinates()
    if game_window:
        print(f"\n🎮 检测到游戏: {game_window['title']}")
    else:
        print("\n⚠️ 未检测到游戏窗口")
    
    # 热键设置
    keyboard.add_hotkey('f8', start_loop)
    keyboard.add_hotkey('f9', stop_loop)
    keyboard.add_hotkey('ctrl+shift+q', emergency_exit)
    
    print("\n🎮 操作说明:")
    print("  F8 - 手动开始购买")
    print("  F9 - 终止程序")
    print("  Ctrl+Shift+Q - 紧急退出")
    print("  ⏰ 开始时间: 到达时自动启动购买")
    print("  🔴 运行时长: 到时自动停止程序")
    if debug_mode:
        print("  🔍 调试模式: 已启用，将显示识别区域")
    print("\n等待按键或定时启动...")
    
    # 检查是否有门卡需要定时启动
    def check_auto_start():
        current_time = datetime.datetime.now().strftime("%H:%M")
        for card in cards_to_buy:
            scheduled_time = card.get('scheduledTime', '')
            if scheduled_time and scheduled_time == current_time:
                return True
        return False

    # 记录自动启动的时间
    loop_start_time = None
    loop_run_duration = None

    try:
        last_minute = ""
        while True:
            # 无论程序是否在运行，都检查时间事件
            current_minute = datetime.datetime.now().strftime("%H:%M")
            if current_minute != last_minute:  # 避免重复检查同一分钟
                last_minute = current_minute
                
                # 检查自动启动
                if check_auto_start() and not is_running:
                    print(f"\n🕐 时间到达 {current_minute}，自动启动购买！")
                    start_loop()
                    loop_start_time = time.time()
                    # 获取当前卡的运行时长
                    if cards_to_buy:
                        loop_run_duration = float(cards_to_buy[0].get('runDuration', 1))
                    else:
                        loop_run_duration = 1.0
            
            # 检查运行时长是否到达
            if is_running:
                if loop_start_time is None:
                    loop_start_time = time.time()
                    if cards_to_buy:
                        loop_run_duration = float(cards_to_buy[0].get('runDuration', 1))
                    else:
                        loop_run_duration = 1.0
                
                # 确保loop_run_duration不为None
                if loop_run_duration is not None:
                    elapsed = (time.time() - loop_start_time) / 60.0
                    if elapsed >= loop_run_duration:
                        print(f"\n🔴 已运行 {loop_run_duration} 分钟，自动停止程序！")
                        stop_loop()
                        loop_start_time = None
                        loop_run_duration = None
            else:
                loop_start_time = None
                loop_run_duration = None

            if is_running and not is_paused:
                i = 0
                while i < len(cards_to_buy) and is_running:
                    card_info = cards_to_buy[i]
                    try:
                        result = price_check_flow(card_info, force_buy=False, debug_mode=debug_mode)
                        if result:
                            card_info['buyAmount'] -= 1
                            print(f"✅ 购买成功！剩余需购买数量: {card_info['buyAmount']}")
                            if card_info['buyAmount'] <= 0:
                                cards_to_buy.pop(i)
                                print(f"🎊 该门卡已购买完成！")
                            else:
                                i += 1
                            if not cards_to_buy:
                                print("🎉 所有门卡购买完成！")
                                stop_loop()
                                break
                        else:
                            i += 1
                    except Exception as e:
                        i += 1
                    if not is_running:
                        break
                    time.sleep(0.1)
                if is_running and cards_to_buy:
                    time.sleep(1)
            else:
                time.sleep(1)  # 每秒检查一次时间
    except KeyboardInterrupt:
        print("\n程序退出")
    except Exception as e:
        print(f"\n❌ 程序错误: {str(e)}")
    finally:
        # 关闭所有OpenCV窗口
        if debug_mode:
            cv2.destroyAllWindows()
        print("程序结束")

if __name__ == "__main__":
    check_admin_privileges()
    main()
