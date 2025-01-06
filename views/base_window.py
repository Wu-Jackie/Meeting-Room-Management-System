from PyQt5.QtWidgets import QWidget, QDesktopWidget
from PyQt5.QtGui import QIcon
import os

class BaseWindow(QWidget):
    def __init__(self):
        super().__init__()
        # 设置窗口图标
        icon_path = os.path.join('Resources', 'Logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def center(self):
        """将窗口居中显示"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2,
                 (screen.height() - size.height()) // 2)

    def showEvent(self, event):
        """窗口显示时自动居中"""
        self.center()
        super().showEvent(event) 