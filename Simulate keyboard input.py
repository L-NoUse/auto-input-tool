import sys
import time
import threading
import pygetwindow as gw

from PyQt5.QtCore import Qt, QVariantAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
)

import pyautogui


# =========================
# mac 风格圆点按钮
# =========================
class MacButton(QPushButton):
    def __init__(self, color, button_type):
        super().__init__()

        self.base_color = QColor(color)
        self.button_type = button_type
        self.hovered = False

        self.setFixedSize(18, 18)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
        """)

    def enterEvent(self, event):
        self.hovered = True
        self.update()

    def leaveEvent(self, event):
        self.hovered = False
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        color = QColor(self.base_color)
        if self.hovered:
            color = color.darker(120)

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 18, 18)

        if self.hovered:
            pen = QPen(QColor(60, 60, 60))
            pen.setWidth(2)
            painter.setPen(pen)

            if self.button_type == "close":
                painter.drawLine(6, 6, 12, 12)
                painter.drawLine(12, 6, 6, 12)

            elif self.button_type == "min":
                painter.drawLine(5, 9, 13, 9)

            elif self.button_type == "max":
                painter.drawLine(5, 9, 13, 9)
                painter.drawLine(9, 5, 9, 13)


# =========================
# 置顶按钮
# =========================
class PinButton(QPushButton):
    def __init__(self):
        super().__init__("📌")

        self.active = False
        self.setFixedSize(36, 28)
        self.update_style()

    def toggle(self):
        self.active = not self.active
        self.update_style()

    def update_style(self):
        bg = "#4A90E2" if self.active else "#3A3A3A"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }}
        """)


# =========================
# 主窗口
# =========================
class AutoInputWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.running = False
        self.dark_mode = True
        self.bg_color = QColor("#1E1E1E")

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Auto Input Tool")
        self.setFixedSize(600, 420)

        self.setWindowFlags(Qt.FramelessWindowHint)

        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: white;
                font-family: Microsoft YaHei;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)

        # =========================
        # 顶部栏
        # =========================
        top_bar = QHBoxLayout()

        self.close_btn = MacButton("#FF5F57", "close")
        self.min_btn = MacButton("#FEBC2E", "min")
        self.max_btn = MacButton("#28C840", "max")

        self.close_btn.clicked.connect(self.close)
        self.min_btn.clicked.connect(self.showMinimized)
        self.max_btn.clicked.connect(self.toggle_max)

        self.pin_btn = PinButton()
        self.pin_btn.clicked.connect(self.toggle_topmost)

        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedSize(36, 28)
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setCursor(Qt.PointingHandCursor)

        self.theme_btn.setStyleSheet("""
            QPushButton {
                background-color: #3A3A3A;
                border-radius: 8px;
                border: none;
                color: white;
                font-size: 16px;
            }
        """)

        top_bar.addWidget(self.close_btn)
        top_bar.addWidget(self.min_btn)
        top_bar.addWidget(self.max_btn)
        top_bar.addStretch()
        top_bar.addWidget(self.pin_btn)
        top_bar.addWidget(self.theme_btn)

        # =========================
        # 文本框
        # =========================
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("粘贴要自动输入的内容...")

        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2A2A2A;
                border-radius: 14px;
                border: 2px solid #3A3A3A;
                padding: 12px;
                font-size: 16px;
                color: white;
            }
        """)

        # =========================
        # 按钮区
        # =========================
        bottom = QHBoxLayout()

        self.start_btn = QPushButton("开始输入")
        self.stop_btn = QPushButton("终止输入")

        self.start_btn.clicked.connect(self.start_typing)
        self.stop_btn.clicked.connect(self.stop_typing)

        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ECC71;
                border-radius: 12px;
                height: 50px;
                font-size: 18px;
                color: white;
                font-weight: bold;
            }
        """)

        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
                border-radius: 12px;
                height: 50px;
                font-size: 18px;
                color: white;
                font-weight: bold;
            }
        """)

        bottom.addWidget(self.start_btn)
        bottom.addWidget(self.stop_btn)

        main_layout.addLayout(top_bar)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.text_edit)
        main_layout.addSpacing(12)
        main_layout.addLayout(bottom)

        self.setLayout(main_layout)

    # =========================
    # 置顶
    # =========================
    def toggle_topmost(self):
        self.pin_btn.toggle()

        self.setWindowFlag(Qt.WindowStaysOnTopHint, self.pin_btn.active)
        self.show()

    # =========================
    # 最大化
    # =========================
    def toggle_max(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    # =========================
    # 开始输入
    # =========================
    def start_typing(self):

        if self.running:
            return

        text = self.text_edit.toPlainText()

        if not text.strip():
            return

        self.current_text = text

        self.running = True

        self.start_btn.setText("等待输入框...")

        threading.Thread(
            target=self.wait_for_target,
            daemon=True
        ).start()

    # =========================
    # 停止输入
    # =========================
    def stop_typing(self):
        self.running = False
    #等待函数
    def wait_for_target(self):

        while self.running:

            try:
                active = gw.getActiveWindow()

                # 当前激活窗口不是自己
                if active and active.title != self.windowTitle():
                    time.sleep(0.3)

                    self.type_text()

                    break

            except:
                pass

            time.sleep(0.1)

    # =========================
    # 模拟键盘输入
    # =========================
    def type_text(self):

        for c in self.current_text:

            if not self.running:
                break

            pyautogui.write(c)

            time.sleep(0.02)

        self.running = False

        self.start_btn.setText("开始输入")

    # =========================
    # 丝滑主题切换
    # =========================
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            target = QColor("#1E1E1E")
            self.theme_btn.setText("🌙")
            text_bg = "#2A2A2A"
            text_color = "white"
            border = "#3A3A3A"
        else:
            target = QColor("#F5F5F5")
            self.theme_btn.setText("☀️")
            text_bg = "white"
            text_color = "black"
            border = "#D0D0D0"

        self.anim = QVariantAnimation()
        self.anim.setDuration(300)
        self.anim.setStartValue(self.bg_color)
        self.anim.setEndValue(target)
        self.anim.setEasingCurve(QEasingCurve.InOutCubic)

        def on_change(color):
            self.bg_color = color

            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {color.name()};
                    color: {text_color};
                }}
            """)

            self.text_edit.setStyleSheet(f"""
                QTextEdit {{
                    background-color: {text_bg};
                    border: 2px solid {border};
                    border-radius: 14px;
                    padding: 12px;
                    font-size: 16px;
                    color: {text_color};
                }}
            """)

        self.anim.valueChanged.connect(on_change)
        self.anim.start()

    # =========================
    # 拖动窗口
    # =========================
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.globalPos() - self.drag_pos)
            self.drag_pos = event.globalPos()


# =========================
# 运行
# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = AutoInputWindow()
    win.show()
    sys.exit(app.exec_())