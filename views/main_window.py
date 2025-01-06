from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QMessageBox, QDesktopWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import os
from .profile_window import ProfileWindow
from utils.session_manager import SessionManager
from .booking_system import BookingSystem

class MainWindow(QMainWindow):
    def __init__(self, db_connection, user_info, login_window):
        super().__init__()
        self.conn = db_connection
        self.user_info = user_info
        self.login_window = login_window
        
        # 初始化会话管理器
        self.session_manager = SessionManager()
        
        # 创建定时器检查会话状态
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_session)
        self.timer.start(60000)  # 每分钟检查一次
        
        self.initUI()
        self.center()

    def check_session(self):
        """检查会话是否过期"""
        if self.session_manager.is_session_expired():
            QMessageBox.warning(self, '会话超时', '由于长时间未操作，请重新登录！')
            self.logout()

    def mousePressEvent(self, event):
        """鼠标点击事件"""
        self.update_activity()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        self.update_activity()
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        """键盘事件"""
        self.update_activity()
        super().keyPressEvent(event)

    def update_activity(self):
        """更新最后活动时间"""
        self.session_manager.update_activity()

    def initUI(self):
        # 设置窗口图标
        icon_path = os.path.join('Resources', 'Logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
            
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout(central_widget)
        
        # 欢迎信息
        welcome_label = QLabel(f'欢迎{self.user_info["Name"]}！')
        welcome_label.setAlignment(Qt.AlignCenter)
        # 设置字体大小
        font = welcome_label.font()
        font.setPointSize(14)  # 设置字体大小为14
        welcome_label.setFont(font)
        layout.addWidget(welcome_label)
        
        # 添加一些间距
        layout.addSpacing(20)
        
        # 创建按钮
        self.profile_btn = QPushButton('查看个人信息')
        layout.addWidget(self.profile_btn)
        
        # 根据用户角色添加不同的按钮
        if self.user_info['Role'] == 'Admin':
            self.admin_btn = QPushButton('进入管理系统')
            layout.addWidget(self.admin_btn)
            self.admin_btn.clicked.connect(self.show_admin_system)
        else:
            self.booking_btn = QPushButton('进入预订系统')
            layout.addWidget(self.booking_btn)
            self.booking_btn.clicked.connect(self.show_booking)
        
        self.logout_btn = QPushButton('退出登录')
        layout.addWidget(self.logout_btn)
        
        # 连接信号
        self.profile_btn.clicked.connect(self.show_profile)
        self.logout_btn.clicked.connect(self.logout)
        
        # 设置窗口
        self.setWindowTitle('会议室管理系统')
        self.setFixedSize(500, 400)  # 设置固定窗口大小

    def show_profile(self):
        self.update_activity()
        self.profile_window = ProfileWindow(self.conn, self.user_info, self)
        self.profile_window.show()
        self.hide()

    def show_booking(self):
        self.update_activity()
        self.booking_window = BookingSystem(self.conn, self.user_info, self)
        self.booking_window.show()
        self.hide()
        
    def show_admin_system(self):
        self.update_activity()
        from .admin_system import AdminSystem
        self.admin_window = AdminSystem(self.conn, self.user_info, self)
        self.admin_window.show()
        self.hide()

    def logout(self):
        """登出系统，清理所有窗口并返回登录界面"""
        try:
            windows_to_close = [
                'main_window',      # 主窗口实例
                'admin_window',     # 管理系统窗口实例
                'booking_window',   # 预订系统窗口实例
                'profile_window',   # 个人信息窗口实例
                'edit_window',      # 个人信息编辑窗口实例
                'register_window',  # 注册窗口实例
                'booking_detail',   # 预订详情窗口实例
                'room_edit_window', # 会议室编辑窗口实例
                'device_edit_window', # 设备编辑窗口实例
            ]
            
            # 安全地关闭每个窗口
            for window_name in windows_to_close:
                if hasattr(self, window_name):
                    window = getattr(self, window_name)
                    if window is not None and window != self:  # 避免关闭自身
                        window.close()
                    delattr(self, window_name)
            
            # 安全地关闭旧的数据库连接
            if hasattr(self, 'conn') and self.conn:
                try:
                    self.conn.close()
                except:
                    pass  # 忽略关闭连接时的错误
                delattr(self, 'conn')
            
            # 清理用户信息
            if hasattr(self, 'user_info'):
                delattr(self, 'user_info')
            
            # 创建新的数据库连接并显示登录窗口
            import mysql.connector
            from config import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE
            from .login_window import LoginWindow
            
            new_conn = mysql.connector.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
            )
            
            # 创建并显示新的登录窗口
            self.login_window = LoginWindow(new_conn)
            self.login_window.show()
            
            # 最后关闭主窗口
            self.close()
            
        except Exception as e:
            print(f"登出时发生错误: {str(e)}")  # 打印错误信息以便调试

    def center(self):
        """将窗口居中显示"""
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2,
                 (screen.height() - size.height()) // 2)

