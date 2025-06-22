import pyautogui
import time
import win32gui
import win32con

# 获取屏幕分辨率
screen_width, screen_height = pyautogui.size()

def find_game_window():
    """查找游戏窗口"""
    # 常见的游戏窗口标题关键词
    game_titles = [
        "三角洲行动",    # 用户确认的游戏窗口标题
        "Delta Force",  
        "DeltaForce", 
        "UnrealWindow",  # 虚幻引擎游戏常用
    ]
    
    # 需要排除的窗口标题关键词
    exclude_titles = [
        "Cursor", "Visual Studio", "Code", "Explorer", "Chrome", 
        "Firefox", "Edge", "Discord", "QQ", "WeChat", "Steam", 
        "Epic Games", "TaskManager", "cmd", "PowerShell", "Python",
    ]
    
    def enum_windows_callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            window_title = win32gui.GetWindowText(hwnd)
            
            # 首先检查是否包含排除的关键词
            for exclude in exclude_titles:
                if exclude.lower() in window_title.lower():
                    return True  # 跳过这个窗口
            
            # 然后检查是否包含游戏关键词
            for title in game_titles:
                if title.lower() in window_title.lower():
                    rect = win32gui.GetWindowRect(hwnd)
                    width = rect[2] - rect[0]
                    height = rect[3] - rect[1]
                    
                    # 只考虑足够大的窗口（至少800x600）
                    if width >= 800 and height >= 600:
                        windows.append({
                            'hwnd': hwnd,
                            'title': window_title,
                            'rect': rect,  # (left, top, right, bottom)
                            'width': width,
                            'height': height
                        })
        return True
    
    windows = []
    win32gui.EnumWindows(enum_windows_callback, windows)
    
    if windows:
        # 选择最大的窗口（通常是游戏主窗口）
        return max(windows, key=lambda w: w['width'] * w['height'])
    else:
        return None

print("=== 窗口模式坐标调试工具（自适应） ===")
print("正在检测游戏窗口...")

# 初始检测游戏窗口
game_window = find_game_window()
if not game_window:
    print("❌ 未找到游戏窗口")
    print("请确保游戏正在运行，或检查游戏窗口标题")
    print("程序将在3秒后退出...")
    time.sleep(3)
    exit(1)

print(f"✅ 检测到游戏窗口: {game_window['title']}")
print("💡 程序将实时跟踪窗口位置变化")
print("💡 获取的百分比坐标可直接用于窗口模式的main.py")
print("\n🎮 操作说明:")
print("  移动鼠标查看实时坐标")
print("  按 F1 保存当前位置为名称区域左上角")
print("  按 F2 保存当前位置为名称区域右下角")
print("  按 F3 保存当前位置为价格区域左上角")
print("  按 F4 保存当前位置为价格区域右下角")
print("  按 F5 输出完整的配置代码")
print("  按 Ctrl+C 结束程序")
print("-" * 60)

# 存储坐标的变量
saved_coords = {
    'name_top_left': None,
    'name_bottom_right': None,
    'price_top_left': None,
    'price_bottom_right': None
}

last_window_pos = None

# 热键处理函数
def save_name_top_left():
    global saved_coords
    x, y = pyautogui.position()
    try:
        current_rect = win32gui.GetWindowRect(game_window['hwnd'])
        left, top, right, bottom = current_rect
        width = right - left
        height = bottom - top
        
        relative_x = x - left
        relative_y = y - top
        x_percent = round(relative_x / width, 4)
        y_percent = round(relative_y / height, 4)
        
        saved_coords['name_top_left'] = [x_percent, y_percent]
        print(f"\n✅ F1: 名称区域左上角已保存 [{x_percent}, {y_percent}]")
    except:
        print(f"\n❌ F1: 保存失败")

def save_name_bottom_right():
    global saved_coords
    x, y = pyautogui.position()
    try:
        current_rect = win32gui.GetWindowRect(game_window['hwnd'])
        left, top, right, bottom = current_rect
        width = right - left
        height = bottom - top
        
        relative_x = x - left
        relative_y = y - top
        x_percent = round(relative_x / width, 4)
        y_percent = round(relative_y / height, 4)
        
        saved_coords['name_bottom_right'] = [x_percent, y_percent]
        print(f"\n✅ F2: 名称区域右下角已保存 [{x_percent}, {y_percent}]")
    except:
        print(f"\n❌ F2: 保存失败")

def save_price_top_left():
    global saved_coords
    x, y = pyautogui.position()
    try:
        current_rect = win32gui.GetWindowRect(game_window['hwnd'])
        left, top, right, bottom = current_rect
        width = right - left
        height = bottom - top
        
        relative_x = x - left
        relative_y = y - top
        x_percent = round(relative_x / width, 4)
        y_percent = round(relative_y / height, 4)
        
        saved_coords['price_top_left'] = [x_percent, y_percent]
        print(f"\n✅ F3: 价格区域左上角已保存 [{x_percent}, {y_percent}]")
    except:
        print(f"\n❌ F3: 保存失败")

def save_price_bottom_right():
    global saved_coords
    x, y = pyautogui.position()
    try:
        current_rect = win32gui.GetWindowRect(game_window['hwnd'])
        left, top, right, bottom = current_rect
        width = right - left
        height = bottom - top
        
        relative_x = x - left
        relative_y = y - top
        x_percent = round(relative_x / width, 4)
        y_percent = round(relative_y / height, 4)
        
        saved_coords['price_bottom_right'] = [x_percent, y_percent]
        print(f"\n✅ F4: 价格区域右下角已保存 [{x_percent}, {y_percent}]")
    except:
        print(f"\n❌ F4: 保存失败")

def output_config():
    print(f"\n" + "="*60)
    print("📋 配置代码输出:")
    print("="*60)
    
    if all(saved_coords.values()):
        print('"name_region": {')
        print(f'  "top_left": {saved_coords["name_top_left"]},')
        print(f'  "bottom_right": {saved_coords["name_bottom_right"]}')
        print('},')
        print('"price_region": {')
        print(f'  "top_left": {saved_coords["price_top_left"]},')
        print(f'  "bottom_right": {saved_coords["price_bottom_right"]}')
        print('}')
        print("="*60)
        print("✅ 复制上面的代码到keys.json配置文件中")
    else:
        print("❌ 请先保存所有4个坐标点:")
        print(f"  名称左上角: {'✅' if saved_coords['name_top_left'] else '❌'}")
        print(f"  名称右下角: {'✅' if saved_coords['name_bottom_right'] else '❌'}")
        print(f"  价格左上角: {'✅' if saved_coords['price_top_left'] else '❌'}")
        print(f"  价格右下角: {'✅' if saved_coords['price_bottom_right'] else '❌'}")
    print("="*60)

# 注册热键
import keyboard
keyboard.add_hotkey('f1', save_name_top_left)
keyboard.add_hotkey('f2', save_name_bottom_right)
keyboard.add_hotkey('f3', save_price_top_left)
keyboard.add_hotkey('f4', save_price_bottom_right)
keyboard.add_hotkey('f5', output_config)

try:
    while True:
        x, y = pyautogui.position()
        
        # 实时获取窗口位置
        try:
            current_rect = win32gui.GetWindowRect(game_window['hwnd'])
            left, top, right, bottom = current_rect
            width = right - left
            height = bottom - top
            
            current_pos = (left, top, width, height)
            
            # 检查窗口位置是否改变
            if current_pos != last_window_pos:
                if last_window_pos is not None:
                    print(f"\n🔄 检测到窗口位置变化: ({left}, {top}) 尺寸: {width}x{height}")
                last_window_pos = current_pos
            
            coords = {
                'offset_x': left,
                'offset_y': top,
                'width': width,
                'height': height
            }
            
        except Exception as e:
            print(f"\n❌ 无法获取窗口位置: {str(e)}")
            print("游戏窗口可能已关闭，程序退出...")
            break
        
        # 计算相对于游戏窗口的坐标
        relative_x = x - coords['offset_x']
        relative_y = y - coords['offset_y']
        
        # 计算百分比
        if coords['width'] > 0 and coords['height'] > 0:
            x_percent = round(relative_x / coords['width'], 4)
            y_percent = round(relative_y / coords['height'], 4)
        else:
            x_percent = y_percent = 0
        
        # 检查鼠标是否在游戏窗口内
        in_window = (0 <= relative_x <= coords['width'] and 
                    0 <= relative_y <= coords['height'])
        
        status = "✅游戏内" if in_window else "❌游戏外"
        
        # 实时显示坐标信息
        print(
            f"屏幕坐标: ({x:<4}, {y:<4}) | "
            f"窗口相对: ({relative_x:<4}, {relative_y:<4}) | "
            f"百分比: [{x_percent:.4f}, {y_percent:.4f}] | {status}",
            end="\r"
        )
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\n程序已终止")