from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                            QVBoxLayout, QHBoxLayout, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QKeyEvent
import os
from config import hash_password
from .main_window import MainWindow
from .register_window import RegisterWindow
from .base_window import BaseWindow

class LoginWindow(BaseWindow):
    def __init__(self, db_connection):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.main_window = None
        self.initUI()
        self.center()  # 将窗口居中

    def initUI(self):
        # 设置窗口图标
        icon_path = os.path.join('Resources', 'Logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # 创建控件
        self.id_label = QLabel('工号:')
        self.id_input = QLineEdit()
        self.password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        # 连接回车键信号
        self.password_input.returnPressed.connect(self.login)
        
        self.login_button = QPushButton('登录')
        self.register_button = QPushButton('注册')
        
        # 设置布局
        vbox = QVBoxLayout()
        
        # ID输入行
        id_hbox = QHBoxLayout()
        id_hbox.addWidget(self.id_label)
        id_hbox.addWidget(self.id_input)
        
        # 密码行
        password_hbox = QHBoxLayout()
        password_hbox.addWidget(self.password_label)
        password_hbox.addWidget(self.password_input)
        
        # 按钮行
        button_hbox = QHBoxLayout()
        button_hbox.addWidget(self.login_button)
        button_hbox.addWidget(self.register_button)
        
        vbox.addLayout(id_hbox)
        vbox.addLayout(password_hbox)
        vbox.addLayout(button_hbox)
        
        self.setLayout(vbox)
        
        # 连接信号
        self.login_button.clicked.connect(self.login)
        self.register_button.clicked.connect(self.show_register)
        
        self.setWindowTitle('登录系统')
        self.setFixedSize(400, 200)  # 设置固定窗口大小

    def show_register(self):
        """显示注册窗口"""
        try:
            self.register_window = RegisterWindow(self.conn, self)
            self.register_window.show()
            self.hide()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'无法打开注册窗口: {str(e)}')

    def login(self):
        """登录验证"""
        user_id = self.id_input.text().strip()
        password = self.password_input.text()
        
        if not user_id or not password:
            QMessageBox.warning(self, '警告', '请输入工号和密码！')
            return
            
        try:
            # 查询用户
            self.cursor.execute("""
                SELECT No, Id, Name, Gender, Phone, Dept, Position, Role 
                FROM Users 
                WHERE Id = %s AND Password = %s
            """, (user_id, hash_password(password)))
            
            user = self.cursor.fetchone()
            
            if user:
                # 创建用户信息字典
                user_info = {
                    'No': user[0],
                    'Id': user[1],
                    'Name': user[2],
                    'Gender': user[3],
                    'Phone': user[4],
                    'Dept': user[5],
                    'Position': user[6],
                    'Role': user[7]
                }
                
                # 创建并显示主窗口，传递登录窗口实例
                self.main_window = MainWindow(self.conn, user_info, self)
                self.main_window.show()
                self.hide()
            else:
                QMessageBox.warning(self, '警告', '工号或密码错误！')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'登录失败: {str(e)}')

    def showEvent(self, event):
        """当窗口显示时触发"""
        # 清空输入框
        self.id_input.clear()
        self.password_input.clear()
        super().showEvent(event) 

    def center(self):
        """将窗口居中显示"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2,
                 (screen.height() - size.height()) // 2) 

    def closeEvent(self, event):
        """窗口关闭时关闭数据库连接"""
        if hasattr(self, 'conn') and self.conn:
            try:
                self.conn.close()
            except:
                pass
        event.accept() 