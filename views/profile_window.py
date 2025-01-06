from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QMessageBox)
from PyQt5.QtCore import Qt
from .base_window import BaseWindow

class ProfileWindow(BaseWindow):
    def __init__(self, db_connection, user_info, main_window):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.user_info = user_info
        self.main_window = main_window
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)  # 设置布局间距
        
        # 标题
        title = QLabel('个人信息')
        title.setAlignment(Qt.AlignCenter)
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        layout.addSpacing(10)  # 减小标题与内容的间距
        
        # 个人信息显示
        info_layout = QVBoxLayout()
        info_layout.setSpacing(10)  # 设置信息项之间的间距
        
        fields = [
            ('工号：', 'Id'),
            ('姓名：', 'Name'),
            ('性别：', 'Gender'),
            ('电话：', 'Phone'),
            ('部门：', 'Dept'),
            ('职位：', 'Position'),
            ('角色：', 'Role')
        ]
        
        # 创建字典来存储标签引用
        self.info_labels = {}
        
        for label_text, field in fields:
            row = QHBoxLayout()
            label = QLabel(label_text)
            value = QLabel(str(self.user_info.get(field, '')))
            font = value.font()
            font.setBold(True)
            value.setFont(font)
            row.addWidget(label)
            row.addWidget(value)
            row.addStretch()
            info_layout.addLayout(row)
            # 保存值标签的引用
            self.info_labels[field] = value
        
        layout.addLayout(info_layout)
        layout.addSpacing(20)  # 信息区域与按钮之间的间距
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)  # 设置按钮之间的间距
        
        self.edit_btn = QPushButton('修改信息')
        self.edit_btn.setStyleSheet("""
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
        
        self.logout_btn = QPushButton('注销用户')
        self.logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4d4d;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #ff1a1a;
            }
        """)
        
        self.back_btn = QPushButton('返回主页')
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 5px;
                border-radius: 3px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.logout_btn)
        button_layout.addWidget(self.back_btn)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.edit_btn.clicked.connect(self.edit_profile)
        self.logout_btn.clicked.connect(self.logout_account)
        self.back_btn.clicked.connect(self.back_to_main)
        
        self.setLayout(layout)
        self.setWindowTitle('个人信息')
        self.setFixedSize(400, 450)  # 调整窗口大小

    def edit_profile(self):
        """打开修改信息窗口"""
        from .profile_edit_window import ProfileEditWindow
        self.edit_window = ProfileEditWindow(self.conn, self.user_info, self)
        self.edit_window.show()
        self.hide()

    def logout_account(self):
        """注销用户账号"""
        # 确认对话框
        reply = QMessageBox.question(
            self, 
            '确认注销', 
            '您确定要注销账号吗？\n注销后将无法恢复，所有相关数据将被删除。',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # 开始事务
                self.cursor.execute("START TRANSACTION")
                
                # 删除用户的预订记录
                self.cursor.execute("""
                    DELETE FROM MeetingRoomReservation 
                    WHERE No = %s
                """, (self.user_info['No'],))
                
                # 删除用户账号
                self.cursor.execute("""
                    DELETE FROM Users 
                    WHERE No = %s
                """, (self.user_info['No'],))
                
                # 提交事务
                self.conn.commit()
                
                QMessageBox.information(self, '成功', '账号已成功注销！')
                
                # 关闭所有窗口并返回登录界面
                self.main_window.logout()
                
            except Exception as e:
                # 回滚事务
                self.conn.rollback()
                QMessageBox.critical(self, '错误', f'注销失败: {str(e)}')

    def back_to_main(self):
        """返回主页"""
        self.main_window.show()
        self.close()

    def closeEvent(self, event):
        """窗口关闭时显示主窗口"""
        self.main_window.show()
        event.accept() 

    def refresh_info(self):
        """刷新显示的用户信息"""
        # 更新所有显示的用户信息标签
        for field, label in self.info_labels.items():
            label.setText(str(self.user_info.get(field, ''))) 