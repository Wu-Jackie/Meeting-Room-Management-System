from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QMessageBox, QLineEdit)
from PyQt5.QtCore import Qt
from .base_window import BaseWindow

class ProfileEditWindow(BaseWindow):
    def __init__(self, db_connection, user_info, profile_window):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.user_info = user_info
        self.profile_window = profile_window
        self.edit_widgets = {}
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题
        title = QLabel('修改个人信息')
        title.setAlignment(Qt.AlignCenter)
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        layout.addSpacing(10)
        
        # 编辑区域
        edit_layout = QVBoxLayout()
        edit_layout.setSpacing(10)
        
        # 只读字段
        readonly_fields = [
            ('工号：', 'Id'),
            ('姓名：', 'Name'),
            ('性别：', 'Gender'),
            ('角色：', 'Role')
        ]
        
        # 可编辑字段
        editable_fields = [
            ('电话：', 'Phone', '请输入电话号码'),
            ('部门：', 'Dept', '请输入部门名称'),
            ('职位：', 'Position', '请输入职位名称')
        ]
        
        # 添加只读字段
        for label_text, field in readonly_fields:
            row = QHBoxLayout()
            label = QLabel(label_text)
            value = QLabel(str(self.user_info.get(field, '')))
            font = value.font()
            font.setBold(True)
            value.setFont(font)
            row.addWidget(label)
            row.addWidget(value)
            row.addStretch()
            edit_layout.addLayout(row)
        
        # 添加可编辑字段
        for label_text, field, placeholder in editable_fields:
            row = QHBoxLayout()
            label = QLabel(label_text)
            edit = QLineEdit()
            edit.setText(str(self.user_info.get(field, '')))
            edit.setPlaceholderText(placeholder)
            self.edit_widgets[field] = edit
            row.addWidget(label)
            row.addWidget(edit)
            edit_layout.addLayout(row)
        
        layout.addLayout(edit_layout)
        layout.addSpacing(20)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_btn = QPushButton('保存')
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.save_btn.clicked.connect(self.save_changes)
        self.cancel_btn.clicked.connect(self.close)
        
        self.setLayout(layout)
        self.setWindowTitle('修改个人信息')
        self.setFixedSize(400, 450)

    def save_changes(self):
        """保存修改的信息"""
        try:
            # 获取编辑框的值
            updates = {
                field: widget.text().strip()
                for field, widget in self.edit_widgets.items()
            }
            
            # 验证电话号码格式
            if updates['Phone'] and not updates['Phone'].isdigit():
                QMessageBox.warning(self, '警告', '电话号码只能包含数字！')
                return
            
            # 更新数据库
            self.cursor.execute("""
                UPDATE Users 
                SET Phone = %s, Dept = %s, Position = %s
                WHERE No = %s
            """, (updates['Phone'], updates['Dept'], updates['Position'], self.user_info['No']))
            
            self.conn.commit()
            
            # 更新本地用户信息
            self.user_info.update(updates)
            
            QMessageBox.information(self, '成功', '个人信息已更新！')
            
            # 刷新个人信息窗口的显示
            self.profile_window.refresh_info()
            
            # 关闭修改窗口，显示个人信息窗口
            self.profile_window.show()
            self.close()
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'保存失败: {str(e)}')

    def closeEvent(self, event):
        """窗口关闭时显示个人信息窗口"""
        self.profile_window.show()
        event.accept() 