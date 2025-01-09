from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                            QWidget)
from PyQt5.QtCore import Qt
from .base_window import BaseWindow

class BookingSystem(BaseWindow):
    def __init__(self, db_connection, user_info, main_window):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.user_info = user_info
        self.main_window = main_window
        self.room_data = []  # 存储会议室数据
        self.booking_data = []  # 存储预订数据
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 创建按钮
        self.query_all_btn = QPushButton('查询总的会议室')
        self.query_room_btn = QPushButton('查询空闲会议室')
        self.my_bookings_btn = QPushButton('预订查询')
        self.back_btn = QPushButton('返回主页')
        
        button_layout.addWidget(self.query_all_btn)
        button_layout.addWidget(self.query_room_btn)
        button_layout.addWidget(self.my_bookings_btn)
        button_layout.addWidget(self.back_btn)
        
        layout.addLayout(button_layout)
        
        # 添加状态提示标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignLeft)
        # 设置字体
        font = self.status_label.font()
        font.setPointSize(10)
        self.status_label.setFont(font)
        # 添加一些上下边距
        layout.addSpacing(10)
        layout.addWidget(self.status_label)
        layout.addSpacing(5)
        
        # 创建表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)  # 增加一列用于放置预订按钮
        self.table.setHorizontalHeaderLabels(['会议室名称', '可容纳人数', '位置', '操作'])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # 设置表格列宽
        header = self.table.horizontalHeader()
        for i in range(3):  # 前三列自动拉伸
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)  # 最后一列固定宽度
        self.table.setColumnWidth(3, 100)  # 设置操作列的宽度
        
        layout.addWidget(self.table)
        
        # 连接信号
        self.query_all_btn.clicked.connect(self.show_all_rooms)
        self.query_room_btn.clicked.connect(self.show_available_rooms)
        self.my_bookings_btn.clicked.connect(self.show_my_bookings)
        self.back_btn.clicked.connect(self.back_to_main)
        
        self.setLayout(layout)
        self.setWindowTitle('会议室预订系统')
        self.setFixedSize(800, 600)

    def reset_table_for_rooms(self):
        """重置表格为会议室显示模式"""
        self.table.clear()  # 清除所有内容
        self.table.setRowCount(0)  # 重置行数
        header = self.table.horizontalHeader()
        
        # 重置列数和标题
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['会议室名称', '可容纳人数', '位置', '当前状态'])
        
        # 设置列宽
        for i in range(4):
            header.setSectionResizeMode(i, QHeaderView.Stretch)

    def reset_table_for_available_rooms(self):
        """重置表格为空闲会议室显示模式"""
        self.table.clear()  # 清除所有内容
        self.table.setRowCount(0)  # 重置行数
        header = self.table.horizontalHeader()
        
        # 重置列数和标题
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['会议室名称', '可容纳人数', '位置', '操作'])
        
        # 设置列宽
        for i in range(3):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 100)

    def reset_table_for_bookings(self):
        """重置表格为预订记录显示模式"""
        self.table.clear()  # 清除所有内容
        self.table.setRowCount(0)  # 重置行数
        header = self.table.horizontalHeader()
        
        # 重置列数和标题
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            '会议室名称', '预订时间', '开始时间', '结束时间', '状态', '操作'
        ])
        
        # 设置列宽
        for i in range(5):
            header.setSectionResizeMode(i, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        self.table.setColumnWidth(5, 100)

    def show_all_rooms(self):
        """显示所有会议室"""
        try:
            self.reset_table_for_rooms()
            self.status_label.setText("所有会议室信息如下：")
            
            # 修改查询以直接使用 MeetingRoomStatus 字段
            self.cursor.execute("""
                SELECT 
                    mr.Name, 
                    mr.Capacity, 
                    mr.Location,
                    mr.MeetingRoomStatus
                FROM MeetingRooms mr
                ORDER BY mr.Name
            """)
            
            rooms = self.cursor.fetchall()
            
            # 填充表格
            for row_num, room in enumerate(rooms):
                self.table.insertRow(row_num)
                for col_num, value in enumerate(room):
                    item = QTableWidgetItem(str(value))
                    # 设置状态列的颜色
                    if col_num == 3:  # 状态列
                        if value == '使用中' or value == '已预订':
                            item.setForeground(Qt.red)
                        else:
                            item.setForeground(Qt.green)
                    self.table.setItem(row_num, col_num, item)
            
            # 调整列宽
            header = self.table.horizontalHeader()
            for i in range(4):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查询失败: {str(e)}')

    def show_available_rooms(self):
        """显示空闲会议室"""
        try:
            self.reset_table_for_available_rooms()
            self.status_label.setText("当前空闲会议室如下：")
            
            # 修改查询语句，使用 MeetingRoomStatus 字段
            self.cursor.execute("""
                SELECT DISTINCT mr.CId, mr.Name, mr.Capacity, mr.Location 
                FROM MeetingRooms mr
                WHERE mr.MeetingRoomStatus = '空闲'
                ORDER BY mr.Name
            """)
            
            self.room_data = self.cursor.fetchall()
            
            # 清空表格
            self.table.setRowCount(0)
            
            # 填充表格
            for row_num, room in enumerate(self.room_data):
                self.table.insertRow(row_num)
                
                # 添加会议室信息（跳过CId）
                for col_num, value in enumerate(room[1:]):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_num, col_num, item)
                
                # 添加预订按钮
                book_btn = QPushButton('预订')
                book_btn.setFixedWidth(80)
                book_btn.clicked.connect(lambda checked, row=row_num: self.book_room(row))
                
                # 创建一个widget来居中放置按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.addWidget(book_btn)
                btn_layout.setAlignment(Qt.AlignCenter)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.table.setCellWidget(row_num, 3, btn_widget)
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查询失败: {str(e)}')

    def book_room(self, row):
        """打开预订详情窗口"""
        from .booking_detail_window import BookingDetailWindow
        room_info = self.room_data[row]
        self.booking_detail = BookingDetailWindow(self.conn, self.user_info, room_info, self)
        self.booking_detail.show()

    def show_my_bookings(self):
        """显示我的预订"""
        try:
            self.reset_table_for_bookings()  # 重置表格
            self.status_label.setText("您的预订记录如下：")
            
            # 修改SQL查询，使用DATE_FORMAT来格式化所有时间字段
            self.cursor.execute("""
                SELECT 
                    mrr.ReservationId,
                    mr.Name, 
                    DATE_FORMAT(mrr.ReservationTime, '%Y-%m-%d %H:%i') as ReservationTime,
                    DATE_FORMAT(mrr.StartTime, '%Y-%m-%d %H:%i') as StartTime,
                    DATE_FORMAT(mrr.EndTime, '%Y-%m-%d %H:%i') as EndTime,
                    mrr.ReservationStatus
                FROM MeetingRoomReservation mrr
                JOIN MeetingRooms mr ON mrr.CId = mr.CId
                WHERE mrr.No = %s
                ORDER BY mrr.ReservationTime DESC
            """, (self.user_info['No'],))
            
            self.booking_data = self.cursor.fetchall()
            
            # 填充表格
            for row_num, booking in enumerate(self.booking_data):
                self.table.insertRow(row_num)
                
                # 添加预订信息（跳过ReservationId）
                for col_num, value in enumerate(booking[1:]):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)  # 居中对齐
                    self.table.setItem(row_num, col_num, item)
                
                # 根据状态添加操作按钮
                if booking[5] == '待审核':  # booking[5]是状态
                    cancel_btn = QPushButton('撤销')
                    cancel_btn.setFixedWidth(80)
                    cancel_btn.clicked.connect(lambda checked, row=row_num: self.cancel_booking(row))
                    
                    # 创建一个widget来居中放置按钮
                    btn_widget = QWidget()
                    btn_layout = QHBoxLayout(btn_widget)
                    btn_layout.addWidget(cancel_btn)
                    btn_layout.setAlignment(Qt.AlignCenter)
                    btn_layout.setContentsMargins(0, 0, 0, 0)
                    
                    self.table.setCellWidget(row_num, 5, btn_widget)
                else:
                    # 其他状态不显示按钮
                    self.table.setItem(row_num, 5, QTableWidgetItem(''))
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查询失败: {str(e)}')

    def cancel_booking(self, row):
        """撤销预订"""
        try:
            booking_id = self.booking_data[row][0]
            room_name = self.booking_data[row][1]
            
            reply = QMessageBox.question(self, '确认撤销', 
                                       f'确定要撤销 {room_name} 的预订吗？',
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # 开始事务
                self.cursor.execute("START TRANSACTION")
                
                # 更新预订状态为"已取消"
                self.cursor.execute("""
                    UPDATE MeetingRoomReservation 
                    SET ReservationStatus = '已取消'
                    WHERE ReservationId = %s
                """, (booking_id,))
                
                # 更新会议室状态
                self.cursor.execute("""
                    UPDATE MeetingRooms mr
                    JOIN MeetingRoomReservation mrr ON mr.CId = mrr.CId
                    SET mr.MeetingRoomStatus = 
                        CASE 
                            WHEN NOT EXISTS (
                                SELECT 1 
                                FROM MeetingRoomReservation mrr2 
                                WHERE mrr2.CId = mr.CId 
                                AND mrr2.ReservationStatus = '已审核'
                                AND NOW() BETWEEN mrr2.StartTime AND mrr2.EndTime
                            ) THEN '空闲'
                            ELSE '使用中'
                        END
                    WHERE mrr.ReservationId = %s
                """, (booking_id,))
                
                self.conn.commit()
                QMessageBox.information(self, '成功', '预订已成功撤销！')
                self.show_my_bookings()
                
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'撤销失败: {str(e)}')

    def back_to_main(self):
        """返回主页"""
        self.main_window.show()
        self.close()

    def closeEvent(self, event):
        """窗口关闭时显示主窗口"""
        self.main_window.show()
        event.accept()

    # 会话活动监控
    def mousePressEvent(self, event):
        self.main_window.update_activity()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.main_window.update_activity()
        super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        self.main_window.update_activity()
        super().keyPressEvent(event) 