# 三角洲行动 自动购买助手

一个基于OCR和图像识别的三角洲行动游戏门卡自动购买工具，能够自动检测游戏窗口、识别价格、并在价格符合条件时自动购买门卡。

## ✨ 特性

- 🎮 **智能游戏窗口检测** - 自动识别并切换到游戏窗口
- 📊 **高精度OCR价格识别** - 使用Tesseract OCR识别游戏内价格
- ⚡ **极速价格检查** - 优化后的检查速度，每秒约1.5次
- 💰 **灵活价格设置** - 启动时可手动输入价格或使用配置文件
- 🔄 **自动购买循环** - 持续监控价格直到找到合适价格
- 🎯 **精确点击定位** - 支持窗口模式和全屏模式的坐标适配
- 🛡️ **安全退出机制** - 多种热键控制和紧急退出功能

## 🚀 快速开始

### 环境要求

- Windows 10/11
- Python 3.8+
- Tesseract OCR

### 安装步骤

1. **克隆仓库**
   ```bash
   git clone [your-repo-url]
   cd DeltaForceKeyBot-1
   ```

2. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **安装Tesseract OCR**
   - 下载并安装 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
   - 默认安装路径：`D:\Tesseract-OCR\`
   - 如果安装到其他路径，请修改 `main.py` 中的路径配置

4. **配置门卡信息**
   - 编辑 `keys.json` 文件
   - 或者使用 `debug.py` 工具获取坐标

### 配置文件说明

`keys.json` 配置示例：

```json
{
    "keys": [
        {
            "max_price": 1650000,
            "position": [0.3517, 0.2678],
            "detail_price_region": {
                "top_left": [0.7795, 0.8211],
                "bottom_right": [0.8862, 0.8820]
            },
            "wantBuy": 1
        }
    ]
}
```

**字段说明：**
- `max_price`: 最高购买价格（必需）
- `position`: 门卡点击位置的百分比坐标 [x, y]（必需）
- `detail_price_region`: 价格识别区域的百分比坐标（必需）
- `wantBuy`: 是否购买此门卡（1=购买，0=不购买）

## 🎮 使用方法

### 基本使用

1. **启动游戏** - 确保三角洲行动正在运行
2. **运行程序** 
   ```bash
   python main.py
   ```
3. **设置价格** - 按提示输入最高价格（或按回车使用配置文件价格）
4. **开始购买** - 按 `F8` 开始自动购买循环
5. **停止程序** - 按 `F9` 终止程序

### 热键控制

- **F8** - 开始自动购买循环
- **F9** - 终止程序
- **Ctrl+Shift+Q** - 紧急退出

### 坐标调试工具

使用 `debug.py` 获取准确的坐标：

```bash
python debug.py
```

**调试工具热键：**
- **F1** - 保存名称区域左上角
- **F2** - 保存名称区域右下角  
- **F3** - 保存价格区域左上角
- **F4** - 保存价格区域右下角
- **F5** - 输出完整配置代码

## 📁 项目结构

```
DeltaForceKeyBot-1/
├── main.py              # 主程序文件
├── debug.py             # 坐标调试工具
├── keys.json            # 门卡配置文件
├── requirements.txt     # Python依赖列表
└── README.md           # 项目说明文档
```

## 🔧 依赖包

- `keyboard==0.13.5` - 键盘事件监听
- `numpy>=1.21.0` - 数值计算
- `opencv-python>=4.8.0` - 图像处理
- `PyAutoGUI>=0.9.50` - 屏幕操作
- `pytesseract>=0.3.10` - OCR文字识别
- `pywin32>=227` - Windows API调用

## ⚡ 性能优化

程序经过深度优化，实现：

- **极速检查**: 单次价格检查仅需0.65秒
- **快速退出**: 价格不符合时0.05秒内退出
- **高效OCR**: 优先使用PSM 6模式，识别成功率高
- **智能循环**: 每秒1.5次检查频率

## 🛡️ 安全特性

- **游戏窗口检测**: 只在检测到游戏时运行
- **价格范围验证**: 防止异常价格导致误购
- **多重退出机制**: 键盘中断、热键退出、紧急停止
- **坐标验证**: 确保点击位置有效

## 📊 购买逻辑

程序使用简单明确的购买逻辑：

```python
will_buy = current_price <= max_price
```

**购买条件：** 当前价格 ≤ 设定的最高价格时自动购买

## 🔧 配置自定义

### Tesseract路径配置

如果Tesseract安装在非默认路径，修改 `main.py` 中的路径：

```python
os.environ["LANGDATA_PATH"] = r"你的路径\tessdata"
os.environ["TESSDATA_PREFIX"] = r"你的路径\tessdata"  
pytesseract.pytesseract.tesseract_cmd = r'你的路径\tesseract.exe'
```

### 游戏窗口标题

支持的游戏窗口标题：
- "三角洲行动"
- "Delta Force"
- "DeltaForce"
- "UnrealWindow"

如需添加其他标题，修改 `find_game_window()` 函数中的 `game_titles` 列表。

## 🐛 故障排除

### 常见问题

1. **无法识别价格**
   - 检查 `detail_price_region` 坐标是否正确
   - 使用 `debug.py` 重新获取价格区域坐标
   - 确认Tesseract OCR正确安装

2. **无法检测游戏窗口**
   - 确认游戏正在运行
   - 检查游戏窗口标题是否匹配
   - 尝试手动切换到游戏窗口

3. **点击位置不准确**
   - 使用 `debug.py` 重新校准 `position` 坐标
   - 确认游戏分辨率和窗口模式设置

4. **程序无响应**
   - 按 `Ctrl+Shift+Q` 紧急退出
   - 检查Tesseract配置路径
   - 查看控制台错误信息

## 📄 许可证

本项目仅供学习交流使用，请遵守游戏服务条款。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

## ⚠️ 免责声明

本工具仅用于学习和研究目的。使用本工具的风险由用户自行承担，开发者不承担任何责任。请确保遵守游戏的服务条款和相关法律法规。 