from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QMessageBox, QDateTimeEdit)
from PyQt5.QtCore import Qt, QDateTime
from .base_window import BaseWindow

class BookingDetailWindow(BaseWindow):
    def __init__(self, db_connection, user_info, room_info, parent=None):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.user_info = user_info
        self.room_info = room_info  # (CId, Name, Capacity, Location)
        self.parent = parent
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 会议室信息显示
        room_info_layout = QVBoxLayout()
        
        title_label = QLabel(f'预订会议室：{self.room_info[1]}')
        title_label.setAlignment(Qt.AlignCenter)
        font = title_label.font()
        font.setPointSize(12)
        font.setBold(True)
        title_label.setFont(font)
        room_info_layout.addWidget(title_label)
        
        info_label = QLabel(f'容纳人数：{self.room_info[2]}    位置：{self.room_info[3]}')
        info_label.setAlignment(Qt.AlignCenter)
        room_info_layout.addWidget(info_label)
        
        layout.addLayout(room_info_layout)
        layout.addSpacing(20)
        
        # 时间选择
        time_layout = QVBoxLayout()
        
        # 开始时间
        start_layout = QHBoxLayout()
        start_label = QLabel('开始时间：')
        self.start_time_edit = QDateTimeEdit(self)
        self.start_time_edit.setCalendarPopup(True)  # 允许弹出日历
        self.start_time_edit.setDateTime(QDateTime.currentDateTime())  # 设置当前时间
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_time_edit)
        time_layout.addLayout(start_layout)
        
        # 结束时间
        end_layout = QHBoxLayout()
        end_label = QLabel('结束时间：')
        self.end_time_edit = QDateTimeEdit(self)
        self.end_time_edit.setCalendarPopup(True)  # 允许弹出日历
        self.end_time_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))  # 默认一小时后
        end_layout.addWidget(end_label)
        end_layout.addWidget(self.end_time_edit)
        time_layout.addLayout(end_layout)
        
        layout.addLayout(time_layout)
        layout.addSpacing(20)
        
        # 按钮
        button_layout = QHBoxLayout()
        self.confirm_btn = QPushButton('确认预订')
        self.cancel_btn = QPushButton('取消')
        
        button_layout.addWidget(self.confirm_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.confirm_btn.clicked.connect(self.confirm_booking)
        self.cancel_btn.clicked.connect(self.close)
        
        self.setLayout(layout)
        self.setWindowTitle('预订详情')
        self.setFixedSize(400, 300)

    def confirm_booking(self):
        """确认预订"""
        try:
            start_time = self.start_time_edit.dateTime()
            end_time = self.end_time_edit.dateTime()
            
            # 检查时间是否合法
            if start_time >= end_time:
                QMessageBox.warning(self, '警告', '结束时间必须晚于开始时间！')
                return
                
            if start_time <= QDateTime.currentDateTime():
                QMessageBox.warning(self, '警告', '开始时间必须晚于当前时间！')
                return
            
            # 检查时间段是否已被预订
            self.cursor.execute("""
                SELECT COUNT(*) 
                FROM MeetingRoomReservation 
                WHERE CId = %s 
                AND ReservationStatus IN ('待审核', '已审核')
                AND (
                    (StartTime <= %s AND EndTime >= %s)
                    OR (StartTime <= %s AND EndTime >= %s)
                    OR (StartTime >= %s AND EndTime <= %s)
                )
            """, (
                self.room_info[0],
                start_time.toString('yyyy-MM-dd HH:mm:ss'),
                start_time.toString('yyyy-MM-dd HH:mm:ss'),
                end_time.toString('yyyy-MM-dd HH:mm:ss'),
                end_time.toString('yyyy-MM-dd HH:mm:ss'),
                start_time.toString('yyyy-MM-dd HH:mm:ss'),
                end_time.toString('yyyy-MM-dd HH:mm:ss')
            ))
            
            if self.cursor.fetchone()[0] > 0:
                QMessageBox.warning(self, '警告', '该时间段已被预订！')
                return
            
            # 插入预订记录
            self.cursor.execute("""
                INSERT INTO MeetingRoomReservation 
                (No, CId, StartTime, EndTime, ReservationStatus) 
                VALUES (%s, %s, %s, %s, '待审核')
            """, (
                self.user_info['No'],
                self.room_info[0],
                start_time.toString('yyyy-MM-dd HH:mm:ss'),
                end_time.toString('yyyy-MM-dd HH:mm:ss')
            ))
            
            self.conn.commit()
            
            QMessageBox.information(self, '成功', f'已成功预订{self.room_info[1]}，等待管理员审核！')
            
            # 关闭窗口并刷新父窗口的会议室列表
            self.close()
            if self.parent:
                self.parent.show_available_rooms()
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'预订失败: {str(e)}') 