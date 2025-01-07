from PyQt5.QtWidgets import (QLabel, QLineEdit, QPushButton, QVBoxLayout, 
                            QMessageBox, QWidget)
from PyQt5.QtCore import Qt
import hashlib

class PasswordChangeWindow(QWidget):
    def __init__(self, db_connection, user_info, profile_window):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.user_info = user_info
        self.profile_window = profile_window
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题
        title = QLabel('修改密码')
        title.setAlignment(Qt.AlignCenter)
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # 输入框
        self.old_pwd = QLineEdit()
        self.old_pwd.setEchoMode(QLineEdit.Password)
        self.old_pwd.setPlaceholderText('请输入原密码')
        layout.addWidget(self.old_pwd)
        
        self.new_pwd = QLineEdit()
        self.new_pwd.setEchoMode(QLineEdit.Password)
        self.new_pwd.setPlaceholderText('请输入新密码')
        layout.addWidget(self.new_pwd)
        
        self.confirm_pwd = QLineEdit()
        self.confirm_pwd.setEchoMode(QLineEdit.Password)
        self.confirm_pwd.setPlaceholderText('请确认新密码')
        layout.addWidget(self.confirm_pwd)
        
        # 确认按钮
        self.submit_btn = QPushButton('确认修改')
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.submit_btn.clicked.connect(self.submit_change)
        layout.addWidget(self.submit_btn)
        
        # 返回按钮
        self.back_btn = QPushButton('返回')
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.back_btn.clicked.connect(self.back_to_profile)
        layout.addWidget(self.back_btn)
        
        self.setLayout(layout)
        self.setWindowTitle('修改密码')
        self.setFixedSize(300, 350)
        
    def submit_change(self):
        old_pwd = self.old_pwd.text()
        new_pwd = self.new_pwd.text()
        confirm_pwd = self.confirm_pwd.text()
        
        if not all([old_pwd, new_pwd, confirm_pwd]):
            QMessageBox.warning(self, '警告', '请填写所有密码字段！')
            return
            
        if new_pwd != confirm_pwd:
            QMessageBox.warning(self, '警告', '两次输入的新密码不一致！')
            return
            
        # 验证原密码
        old_pwd_hash = hashlib.sha256(old_pwd.encode()).hexdigest()
        self.cursor.execute("""
            SELECT Password FROM Users WHERE No = %s
        """, (self.user_info['No'],))
        stored_pwd = self.cursor.fetchone()[0]
        
        if old_pwd_hash != stored_pwd:
            QMessageBox.warning(self, '警告', '原密码错误！')
            return
            
        # 更新密码
        try:
            new_pwd_hash = hashlib.sha256(new_pwd.encode()).hexdigest()
            self.cursor.execute("""
                UPDATE Users SET Password = %s WHERE No = %s
            """, (new_pwd_hash, self.user_info['No']))
            self.conn.commit()
            QMessageBox.information(self, '成功', '密码修改成功！')
            self.back_to_profile()
            self.close()
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'密码修改失败: {str(e)}')
            
    def back_to_profile(self):
        self.profile_window.show()
        self.close()
        
    def closeEvent(self, event):
        self.profile_window.show()
        event.accept() 