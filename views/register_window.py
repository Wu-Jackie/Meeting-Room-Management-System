from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QMessageBox, QComboBox,
                            QDesktopWidget)
from enum import Enum
from config import hash_password
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QRegExp

# 直接在这里定义枚举类
class Gender(Enum):
    MALE = "男"
    FEMALE = "女"

class Role(Enum):
    USER = "User"
    ADMIN = "Admin"

class RegisterWindow(QWidget):
    def __init__(self, db_connection, parent=None):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.parent = parent  # 保存父窗口引用
        self.initUI()
        self.center()

    def initUI(self):
        # 创建控件
        self.id_label = QLabel('工号:')
        self.id_input = QLineEdit()
        
        self.name_label = QLabel('姓名:')
        self.name_input = QLineEdit()
        
        self.password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        # 添加重复密码输入框
        self.confirm_password_label = QLabel('确认密码:')
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        
        self.gender_label = QLabel('性别:')
        self.gender_combo = QComboBox()
        self.gender_combo.addItems([gender.value for gender in Gender])
        
        self.phone_label = QLabel('电话:')
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText('请输入11位手机号')
        # 设置手机号验证器
        phone_validator = QRegExpValidator(QRegExp('^[0-9]{11}$'))
        self.phone_input.setValidator(phone_validator)
        
        self.dept_label = QLabel('部门:')
        self.dept_input = QLineEdit()
        
        self.position_label = QLabel('职位:')
        self.position_input = QLineEdit()
        
        self.submit_button = QPushButton('提交注册')
        
        # 创建布局
        layout = QVBoxLayout()
        
        # 添加所有输入框到布局
        for label, widget in [
            (self.id_label, self.id_input),
            (self.name_label, self.name_input),
            (self.password_label, self.password_input),
            (self.confirm_password_label, self.confirm_password_input),
            (self.gender_label, self.gender_combo),
            (self.phone_label, self.phone_input),
            (self.dept_label, self.dept_input),
            (self.position_label, self.position_input)
        ]:
            hbox = QHBoxLayout()
            hbox.addWidget(label)
            hbox.addWidget(widget)
            layout.addLayout(hbox)
        
        layout.addWidget(self.submit_button)
        
        self.setLayout(layout)
        self.submit_button.clicked.connect(self.register)
        
        self.setWindowTitle('用户注册')
        self.setGeometry(300, 300, 400, 400)

    def center(self):
        """使窗口在屏幕中居中"""
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def register(self):
        """处理注册逻辑"""
        # 获取所有输入
        user_id = self.id_input.text()
        name = self.name_input.text()
        password = self.password_input.text()
        gender = self.gender_combo.currentText()
        phone = self.phone_input.text().strip()
        dept = self.dept_input.text()
        position = self.position_input.text()
        
        # 验证输入
        if not all([user_id, name, password]):
            QMessageBox.warning(self, '警告', 'ID、姓名和密码为必填项！')
            return
        
        # 获取手机号并验证
        if not phone:
            QMessageBox.warning(self, '警告', '请输入手机号！')
            return
        if len(phone) != 11:
            QMessageBox.warning(self, '警告', '手机号必须是11位！')
            return
        if not phone.isdigit():
            QMessageBox.warning(self, '警告', '手机号必须全为数字！')
            return
        
        # 可以添加更严格的手机号格式验证
        if not phone.startswith(('13', '14', '15', '16', '17', '18', '19')):
            QMessageBox.warning(self, '警告', '请输入有效的手机号！')
            return
            
        # 设置默认角色为普通用户
        role = Role.USER.value
        
        try:
            # 检查用户ID是否已存在
            self.cursor.execute("SELECT Id FROM Users WHERE Id = %s", (user_id,))
            if self.cursor.fetchone():
                QMessageBox.warning(self, '错误', '该ID已被注册！')
                return
            
            # 获取最大的No值
            self.cursor.execute("SELECT MAX(No) FROM Users")
            max_no = self.cursor.fetchone()[0]
            next_no = 1 if max_no is None else max_no + 1
            
            # 验证两次输入的密码是否一致
            confirm_password = self.confirm_password_input.text()
            if password != confirm_password:
                QMessageBox.warning(self, '错误', '两次输入的密码不一致！')
                return
            
            # 注册新用户
            hashed_password = hash_password(password)
            self.cursor.execute("""
                INSERT INTO Users (No, Id, Name, Gender, Phone, Dept, Position, Password, Role) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (next_no, user_id, name, gender, phone, dept, position, hashed_password, role))
            
            self.conn.commit()
            QMessageBox.information(self, '成功', '注册成功！请使用新账号登录。')
            
            # 返回登录界面
            if self.parent:
                self.parent.show()  # 显示登录窗口
            self.close()  # 关闭注册窗口
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'注册失败：{str(e)}')
            self.conn.rollback()