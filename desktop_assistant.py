#!/usr/bin/env python3
import sys
import os
from PIL import Image
import subprocess
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout,
                            QHBoxLayout, QLabel, QDialog, QLineEdit, QTextEdit,
                            QPlainTextEdit, QMessageBox, QScrollArea, QFileDialog)
from PyQt5.QtCore import Qt, QPoint, QTimer, QEvent
from PyQt5.QtGui import (QPainter, QPixmap, QColor, QPen, QBrush, QPainterPath,
                        QImage, QTextDocument, QKeySequence, QCursor, QFont,
                        QTextImageFormat, QTextCharFormat, QTextCursor)
import datetime
import uuid
import json
from openai import OpenAI
from dotenv import load_dotenv
from Xlib import display, X
import tempfile

class ImageTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Free Writing Images")
        os.makedirs(self.image_folder, exist_ok=True)
        self.document().setDefaultStyleSheet("""
            img {
                max-width: 300px;
                height: auto;
                margin: 5px 0;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
        """)
        self.setAcceptRichText(True)

    def keyPressEvent(self, event):
        if event.matches(QKeySequence.Paste):
            mime_data = QApplication.clipboard().mimeData()
            
            if mime_data.hasImage():
                self.handle_image_paste(mime_data)
                return
            elif mime_data.hasHtml():
                self.handle_html_paste(mime_data)
                return
            elif mime_data.hasUrls():
                self.handle_urls_paste(mime_data)
                return
                
        super().keyPressEvent(event)

    def handle_image_paste(self, mime_data):
        try:
            image = QImage(mime_data.imageData())
            if not image.isNull():
                self.insert_image(image)
            else:
                QMessageBox.warning(self, "错误", "无效的图片数据")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"处理图片时出错: {str(e)}")

    def insert_image(self, image):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            random_str = str(uuid.uuid4())[:8]
            image_filename = f"image_{timestamp}_{random_str}.png"
            image_path = os.path.join(self.image_folder, image_filename)
            
            if image.save(image_path):
                max_width = 300
                scaled_image = image.scaled(max_width, max_width, 
                                          Qt.KeepAspectRatio, 
                                          Qt.SmoothTransformation)
                
                image_format = QTextImageFormat()
                image_format.setName(image_path)
                
                if image.width() > max_width:
                    scale_ratio = max_width / image.width()
                    new_width = max_width
                    new_height = int(image.height() * scale_ratio)
                else:
                    new_width = image.width()
                    new_height = image.height()
                
                image_format.setWidth(new_width)
                image_format.setHeight(new_height)
                
                cursor = self.textCursor()
                
                if not cursor.atStart():
                    cursor.movePosition(QTextCursor.StartOfBlock)
                    line_start = cursor.position()
                    cursor.movePosition(QTextCursor.EndOfBlock)
                    line_end = cursor.position()
                    current_line = self.document().toPlainText()[line_start:line_end]
                    
                    if current_line.strip():
                        cursor.insertBlock()
                
                cursor.insertImage(image_format)
                cursor.insertBlock()
                
                hidden_format = QTextCharFormat()
                hidden_format.setForeground(QColor(0, 0, 0, 0))
                hidden_format.setFontPointSize(1)
                cursor.insertText(f"![Image]({image_filename})", hidden_format)
                cursor.insertBlock()
                
                print(f"图片已保存到: {image_path}")
            else:
                QMessageBox.warning(self, "错误", "图片保存失败")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"处理图片时出错: {str(e)}")

class ButtonWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(5, 5, 5, 5)

        buttons = [
            "灵感记录",
            "快速笔记",
            "自由写作",
            "截图笔记",
            "AI对话"
        ]

        for text in buttons:
            btn = self.create_button(text)
            layout.addWidget(btn)

        self.setLayout(layout)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()

    def create_button(self, text):
        btn = QPushButton(text)
        btn.setFixedSize(100, 30)
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 5px;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(240, 240, 240, 0.9);
                border: 1px solid #aaa;
            }
        """)
        return btn

class PandaAssistant(QWidget):
    def __init__(self):
        super().__init__()
        self.button_window = ButtonWindow(self)
        self.initUI()
        self.setup_button_connections()
        self.move_to_top_right()

    def initUI(self):
        self.setFixedSize(50, 50)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 创建必要的目录
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.directories = [
            "Free Writing Images",
            "Inspiration Collection",
            "Quick Notes",
            "Writing",
            "Screenshot Notes"
        ]
        for directory in self.directories:
            os.makedirs(os.path.join(self.base_path, directory), exist_ok=True)

    def setup_button_connections(self):
        buttons = self.button_window.findChildren(QPushButton)
        for button in buttons:
            text = button.text()
            if text == "灵感记录":
                button.clicked.connect(self.on_idea_btn_clicked)
            elif text == "快速笔记":
                button.clicked.connect(lambda: self.record_idea(False))
            elif text == "自由写作":
                button.clicked.connect(self.free_writing)
            elif text == "截图笔记":
                button.clicked.connect(self.add_idea_with_screenshot)
            elif text == "AI对话":
                button.clicked.connect(self.show_chat_dialog)

    def take_screenshot(self, folder_name):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            save_path = os.path.join(self.base_path, folder_name, filename)
            
            # 使用scrot进行截图
            temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
            subprocess.run(['scrot', temp_file.name])
            
            # 处理图片
            img = Image.open(temp_file.name)
            img.save(save_path)
            
            # 清理临时文件
            os.unlink(temp_file.name)
            
            return save_path
        except Exception as e:
            QMessageBox.warning(self, "错误", f"截图失败: {str(e)}")
            return None

    def enterEvent(self, event):
        button_pos = self.mapToGlobal(QPoint(0, 0))
        self.button_window.move(button_pos.x() - self.button_window.width() - 5, button_pos.y())
        self.button_window.show()

    def leaveEvent(self, event):
        if not self.button_window.geometry().contains(QCursor.pos()):
            self.button_window.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制圆形背景
        path = QPainterPath()
        path.addEllipse(0, 0, 50, 50)
        painter.fillPath(path, QBrush(QColor(255, 255, 255, 230)))

        # 绘制图标（这里使用简单的文字作为示例）
        painter.setPen(QPen(QColor("#333")))
        painter.setFont(QFont("Arial", 20))
        painter.drawText(0, 0, 50, 50, Qt.AlignCenter, "📝")

    def move_to_top_right(self):
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() - self.width() - 20, 20)

    def show_chat_dialog(self):
        dialog = ChatDialog(self)
        dialog.exec_()

    def free_writing(self):
        dialog = FreeWritingDialog(self)
        dialog.exec_()

    def add_idea_with_screenshot(self):
        screenshot_path = self.take_screenshot("Screenshot Notes")
        if screenshot_path:
            dialog = IdeaWithScreenshotDialog(self, screenshot_path)
            dialog.exec_()

    def record_idea(self, with_screenshot=False):
        screenshot_path = None
        if with_screenshot:
            screenshot_path = self.take_screenshot("Inspiration Collection")
        dialog = IdeaDialog(self, with_screenshot, screenshot_path)
        dialog.exec_()

    def on_idea_btn_clicked(self):
        self.record_idea(True)

# 其他对话框类的实现（IdeaDialog, FreeWritingDialog, ChatDialog等）
# 这些类的实现与Windows版本基本相同，只需要替换截图相关的功能

def main():
    # 加载环境变量
    load_dotenv()
    
    app = QApplication(sys.argv)
    assistant = PandaAssistant()
    assistant.show()
    sys.exit(app.exec_()) 