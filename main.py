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



# 配置部分
CONFIG_FILE = 'keys.json'

# Tesseract 环境配置
os.environ["LANGDATA_PATH"] = r"D:\Tesseract-OCR\tessdata"
os.environ["TESSDATA_PREFIX"] = r"D:\Tesseract-OCR\tessdata"
pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract-OCR\tesseract.exe'

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

def getCardPrice(price_region=None, coords=None):
    """获取当前卡片价格"""
    try:
        if coords is None:
            coords = get_game_coordinates()
        
        game_width = coords['width']
        game_height = coords['height']
        offset_x = coords['offset_x']
        offset_y = coords['offset_y']
        
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
        
        screenshot = take_screenshot(region=region)
        if screenshot is None:
            return None
        
        try:
            # PSM 6 统一文本块模式（最有效，优先使用）
            text = pytesseract.image_to_string(screenshot, lang='eng', config="--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789,")
            cleaned_text = text.replace(",", "").replace(" ", "").replace("\n", "").strip()
            
            if cleaned_text and cleaned_text.isdigit():
                price = int(cleaned_text)
                if 10000 <= price <= 100000000:
                    return price
            
            # 快速失败，只试一种备选方法
            if not cleaned_text:
                text2 = pytesseract.image_to_string(screenshot, lang='eng', config="--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789,")
                cleaned_text2 = text2.replace(",", "").replace(" ", "").replace("\n", "").strip()
                
                if cleaned_text2 and cleaned_text2.isdigit():
                    price2 = int(cleaned_text2)
                    if 10000 <= price2 <= 100000000:
                        return price2
                    
        except Exception as e:
            pass
        
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

def price_check_flow(card_info):
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
            time.sleep(0.3)
            
            try:
                client_x = click_x - offset_x
                client_y = click_y - offset_y
                lParam = (client_y << 16) | (client_x & 0xFFFF)
                win32gui.SendMessage(game_window['hwnd'], win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
                time.sleep(0.02)
                win32gui.SendMessage(game_window['hwnd'], win32con.WM_LBUTTONUP, 0, lParam)
                time.sleep(0.2)
            except:
                pass
        else:
            return False
        
        detail_price_region = card_info.get('detail_price_region', card_info.get('price_region'))
        
        current_price = getCardPrice(detail_price_region, coords)
        if current_price is None:
            pyautogui.press('esc')
            time.sleep(0.05)
            return False
        
    except Exception as e:
        pyautogui.press('esc')
        return False
    
    max_price = card_info.get('max_price', 0)
    
    if max_price == 0:
        pyautogui.press('esc')
        return False
    
    print(f"最高价格: {max_price} | 当前价格: {current_price}")
    
    will_buy = current_price <= max_price
    
    if will_buy:
        try:
            buy_x = offset_x + int(game_width * 0.825)
            buy_y = offset_y + int(game_height * 0.852)
            
            pyautogui.moveTo(buy_x, buy_y)
            time.sleep(0.1)
            pyautogui.click()
            time.sleep(0.4)
            
            print(f"✅ 已购买门卡, 价格: {current_price}")
            pyautogui.press('esc')
            return True
            
        except Exception as e:
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

def stop_loop():
    """停止循环"""
    global is_running, is_paused
    is_running = False
    is_paused = False
    print("⏹️ 停止循环")

def emergency_exit():
    """紧急退出程序"""
    global is_running, is_paused
    is_running = False
    is_paused = False
    print("\n🚨 程序已终止")
    import sys
    sys.exit(0)

def main():
    global is_running, is_paused
    
    print("=== 三角洲行动 自动购买助手 ===")
    
    keys_config = load_keys_config()
    if not keys_config:
        print("❌ 无法加载配置文件")
        return
    
    cards_to_buy = [card for card in keys_config if card.get('wantBuy', 0) == 1]
    if not cards_to_buy:
        print("❌ 没有需要购买的门卡")
        return
    
    # 显示当前配置的价格并询问是否修改
    print(f"📋 需要购买 {len(cards_to_buy)} 个门卡")
    for i, card in enumerate(cards_to_buy):
        current_price = card.get('max_price', 0)
        print(f"  门卡 {i+1}: 当前最高价格 = {current_price:,}")
    
    print("\n💰 价格设置:")
    print("  直接按回车使用配置文件中的价格")
    print("  输入新价格覆盖配置文件中的价格")
    
    # 为每个门卡询问价格
    for i, card in enumerate(cards_to_buy):
        current_price = card.get('max_price', 0)
        while True:
            try:
                user_input = input(f"\n门卡 {i+1} 最高价格 (当前: {current_price:,}): ").strip()
                
                if user_input == "":
                    # 使用配置文件中的价格
                    print(f"✅ 使用配置价格: {current_price:,}")
                    break
                else:
                    # 用户输入新价格
                    new_price = int(user_input.replace(",", "").replace(" ", ""))
                    if new_price > 0:
                        card['max_price'] = new_price
                        print(f"✅ 设置新价格: {new_price:,}")
                        break
                    else:
                        print("❌ 价格必须大于0，请重新输入")
            except ValueError:
                print("❌ 请输入有效的数字")
            except KeyboardInterrupt:
                print("\n程序被中断")
                return
    
    # 显示最终价格设置
    print(f"\n🎯 最终价格设置:")
    for i, card in enumerate(cards_to_buy):
        final_price = card.get('max_price', 0)
        print(f"  门卡 {i+1}: {final_price:,}")
    
    coords = get_game_coordinates()
    if game_window:
        print(f"🎮 检测到游戏: {game_window['title']}")
    else:
        print("⚠️ 未检测到游戏窗口")
    
    # 热键设置
    keyboard.add_hotkey('f8', start_loop)
    keyboard.add_hotkey('f9', stop_loop)
    keyboard.add_hotkey('ctrl+shift+q', emergency_exit)
    
    print("\n🎮 操作说明:")
    print("  F8 - 开始自动购买")
    print("  F9 - 终止程序")
    print("  Ctrl+Shift+Q - 紧急退出")
    print("\n等待按键...")
    
    try:
        while True:
            if is_running and not is_paused:
                i = 0
                while i < len(cards_to_buy) and is_running:
                    card_info = cards_to_buy[i]
                    
                    try:
                        result = price_check_flow(card_info)
                        if result:
                            cards_to_buy.pop(i)
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
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n程序退出")
    except Exception as e:
        print(f"\n❌ 程序错误: {str(e)}")
    finally:
        print("程序结束")

if __name__ == "__main__":
    main()
