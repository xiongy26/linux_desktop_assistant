# Linux桌面助手

这是一个为Ubuntu/Linux环境开发的桌面助手程序，提供了便捷的笔记、截图和写作功能。

## 主要功能

1. **灵感收集**
   - 快速截取全屏，自动保存并归类
   - 截图自动保存在 "Inspiration Collection" 文件夹中

2. **快速笔记**
   - 支持截图加笔记的形式记录想法
   - 截图自动保存在 "Quick Notes" 文件夹中

3. **写作功能**
   - 支持长文写作
   - 支持图文混排（可直接粘贴图片）
   - 自动保存上一次的写作内容
   - 使用 Markdown 格式保存

4. **截图笔记**
   - 结合截图和文字笔记功能
   - 支持图文混排记录
   - 自动归类管理

5. **快捷功能**
   - 悬浮窗口始终置顶
   - 鼠标移入时显示功能菜单
   - 支持自由拖动位置

6. **聊天功能**
   - 集成AI对话功能
   - 支持独立窗口运行

## 系统要求

- Ubuntu 18.04 或更高版本
- Python 3.7 或更高版本
- X Window System

## 安装步骤

1. 安装系统依赖：
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-pyqt5 python3-xlib scrot
```

2. 安装Python依赖：
```bash
pip3 install -r requirements.txt
```

3. 配置环境变量：
```bash
cp .env.example .env
# 编辑 .env 文件，设置必要的API密钥
```

## 运行程序

```bash
python3 desktop_assistant.py
```

## 开机自启动设置

1. 创建桌面启动项：
```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/desktop-assistant.desktop << EOL
[Desktop Entry]
Type=Application
Name=Desktop Assistant
Exec=python3 /path/to/desktop_assistant.py
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
EOL
```

2. 确保启动脚本有执行权限：
```bash
chmod +x ~/.config/autostart/desktop-assistant.desktop
```

## 文件管理

程序会自动创建以下文件夹：
- `Free Writing Images/`：写作中使用的图片
- `Inspiration Collection/`：灵感收集的截图
- `Quick Notes/`：快速笔记
- `Writing/`：写作内容
- `Screenshot Notes/`：带截图的笔记

## 注意事项

- 确保程序所在目录有足够的写入权限
- 建议定期备份各个文件夹中的内容
- 首次运行时需要设置环境变量

## 贡献

欢迎提出建议和改进意见！如果您有任何想法，请随时提出 issue 或提交 pull request。

## 许可

本项目采用 MIT 许可证。 