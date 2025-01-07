from PyQt5.QtWidgets import (QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                            QWidget, QDialog, QLineEdit, QComboBox)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QTextOption
from .base_window import BaseWindow

class AdminSystem(BaseWindow):
    def __init__(self, db_connection, user_info, main_window):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.user_info = user_info
        self.main_window = main_window
        self.room_edit_layout = None
        self.device_edit_layout = None  # 添加这一行来跟踪设备编辑按钮的布局
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 按钮布局 - 第一行
        button_layout1 = QHBoxLayout()
        self.users_btn = QPushButton('用户列表')
        self.rooms_btn = QPushButton('会议室列表')
        self.devices_btn = QPushButton('设备列表')
        button_layout1.addWidget(self.users_btn)
        button_layout1.addWidget(self.rooms_btn)
        button_layout1.addWidget(self.devices_btn)
        
        # 按钮布局 - 第二行
        button_layout2 = QHBoxLayout()
        self.pending_bookings_btn = QPushButton('待审核预订记录')
        self.maintenance_btn = QPushButton('维护记录')
        self.back_btn = QPushButton('返回主页')
        button_layout2.addWidget(self.pending_bookings_btn)
        button_layout2.addWidget(self.maintenance_btn)
        button_layout2.addWidget(self.back_btn)
        
        layout.addLayout(button_layout1)
        layout.addLayout(button_layout2)
        
        # 添加状态提示标签
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignLeft)
        font = self.status_label.font()
        font.setPointSize(10)
        self.status_label.setFont(font)
        layout.addSpacing(10)
        layout.addWidget(self.status_label)
        layout.addSpacing(5)
        
        # 创建表格
        self.table = QTableWidget()
        layout.addWidget(self.table)
        
        # 连接信号
        self.users_btn.clicked.connect(self.show_users)
        self.rooms_btn.clicked.connect(self.show_rooms)
        self.devices_btn.clicked.connect(self.show_devices)
        self.back_btn.clicked.connect(self.back_to_main)
        self.pending_bookings_btn.clicked.connect(self.show_pending_bookings)
        self.maintenance_btn.clicked.connect(self.show_maintenance)
        
        self.setLayout(layout)
        self.setWindowTitle('管理系统')
        self.setFixedSize(1000, 600)

    def setup_table_display(self):
        """设置表格的通用显示属性"""
        # 启用自动换行
        self.table.setWordWrap(True)
        
        # 设置所有列自动拉伸
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            if i == self.table.columnCount() - 1:  # 最后一列（操作列）
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.table.setColumnWidth(i, 100)
            else:
                header.setSectionResizeMode(i, QHeaderView.Stretch)
        
        # 自动调整行高
        for row in range(self.table.rowCount()):
            self.table.resizeRowToContents(row)

    def toggle_room_edit_button(self, show=False):
        """控制会议室编辑按钮的显示和隐藏"""
        if show:
            # 如果需要显示且按钮未创建
            if not self.room_edit_layout:
                button_layoutroom = QHBoxLayout()
                self.roomedit_btn = QPushButton('编辑会议室信息')
                button_layoutroom.addWidget(self.roomedit_btn)
                button_layoutroom.addStretch()
                self.roomedit_btn.clicked.connect(self.show_room_edit)
                
                # 将按钮布局添加到窗口的主布局中
                self.layout().insertLayout(2, button_layoutroom)
                self.room_edit_layout = button_layoutroom
        else:
            # 如果需要隐藏且按钮存在
            if self.room_edit_layout:
                # 删除布局中的所有部件
                while self.room_edit_layout.count():
                    item = self.room_edit_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                # 从主布局中移除
                self.layout().removeItem(self.room_edit_layout)
                self.room_edit_layout = None

    def toggle_device_edit_button(self, show=False):
        """控制设备编辑按钮的显示和隐藏"""
        if show:
            if not self.device_edit_layout:
                button_layoutdevice = QHBoxLayout()
                self.deviceedit_btn = QPushButton('编辑设备信息')
                button_layoutdevice.addWidget(self.deviceedit_btn)
                button_layoutdevice.addStretch()
                self.deviceedit_btn.clicked.connect(self.show_device_edit)
                
                self.layout().insertLayout(2, button_layoutdevice)
                self.device_edit_layout = button_layoutdevice
        else:
            if self.device_edit_layout:
                while self.device_edit_layout.count():
                    item = self.device_edit_layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                self.layout().removeItem(self.device_edit_layout)
                self.device_edit_layout = None

    def show_users(self):
        """显示用户列表"""
        try:
            self.toggle_room_edit_button(False)  # 隐藏会议室编辑按钮
            self.toggle_device_edit_button(False)  # 显示设备编辑按钮
            self.status_label.setText("普通用户列表如下：")
            
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(8)
            self.table.setHorizontalHeaderLabels([
                '工号', '姓名', '性别', '电话', '部门', '职位', '角色', '操作'
            ])
            
            # 查询普通用户
            self.cursor.execute("""
                SELECT Id, Name, Gender, Phone, Dept, Position, Role
                FROM Users 
                WHERE Role = 'User'
                ORDER BY Id
            """)
            
            users = self.cursor.fetchall()
            
            # 填充表格
            for row_num, user in enumerate(users):
                self.table.insertRow(row_num)
                for col_num, value in enumerate(user):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_num, col_num, item)
                
                edit_btn = QPushButton('编辑')
                edit_btn.setFixedWidth(60)
                edit_btn.clicked.connect(lambda checked, user_id=user[0]: self.edit_user(user_id))
                
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.addWidget(edit_btn)
                btn_layout.setAlignment(Qt.AlignCenter)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.table.setCellWidget(row_num, 7, btn_widget)
            
            self.setup_table_display()
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查询失败: {str(e)}')

    def edit_user(self, user_id):
        """编辑用户信息"""
        try:
            # 查询用户当前信息
            self.cursor.execute("""
                SELECT Phone, Dept, Position, Role
                FROM Users 
                WHERE Id = %s
            """, (user_id,))
            current_info = self.cursor.fetchone()
            
            # 创建编辑对话框
            dialog = QDialog(self)
            dialog.setWindowTitle('编辑用户信息')
            layout = QVBoxLayout()
            
            # 创建输入框
            phone_label = QLabel('电话:')
            phone_input = QLineEdit(current_info[0])
            dept_label = QLabel('部门:')
            dept_input = QLineEdit(current_info[1])
            position_label = QLabel('职位:')
            position_input = QLineEdit(current_info[2])
            role_label = QLabel('角色:')
            role_combo = QComboBox()
            role_combo.addItems(['User', 'Admin'])
            role_combo.setCurrentText(current_info[3])
            
            # 添加到布局
            layout.addWidget(phone_label)
            layout.addWidget(phone_input)
            layout.addWidget(dept_label)
            layout.addWidget(dept_input)
            layout.addWidget(position_label)
            layout.addWidget(position_input)
            layout.addWidget(role_label)
            layout.addWidget(role_combo)
            
            # 添加确认和取消按钮
            buttons = QHBoxLayout()
            confirm_btn = QPushButton('确认')
            cancel_btn = QPushButton('取消')
            buttons.addWidget(confirm_btn)
            buttons.addWidget(cancel_btn)
            layout.addLayout(buttons)
            
            dialog.setLayout(layout)
            
            # 连接按钮信号
            def on_confirm():
                try:
                    # 更新用户信息
                    self.cursor.execute("""
                        UPDATE Users 
                        SET Phone = %s, Dept = %s, Position = %s, Role = %s
                        WHERE Id = %s
                    """, (phone_input.text(), dept_input.text(), 
                          position_input.text(), role_combo.currentText(), user_id))
                    self.conn.commit()
                    QMessageBox.information(dialog, '成功', '用户信息已更新！')
                    dialog.accept()
                    self.show_users()  # 刷新用户列表
                except Exception as e:
                    self.conn.rollback()
                    QMessageBox.critical(dialog, '错误', f'更新失败: {str(e)}')
            
            confirm_btn.clicked.connect(on_confirm)
            cancel_btn.clicked.connect(dialog.reject)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'编辑用户失败: {str(e)}')

    def show_rooms(self):
        """显示会议室列表"""
        try:
            self.toggle_room_edit_button(True)
            self.toggle_device_edit_button(False)
            self.status_label.setText("会议室列表如下：")
            
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(5)
            self.table.setHorizontalHeaderLabels([
                '会议室名称', '可容纳人数', '位置', '设备列表', '当前状态'
            ])
            
            # 修改查询以使用 MeetingRoomStatus 字段
            self.cursor.execute("""
                SELECT 
                    mr.Name, 
                    mr.Capacity, 
                    mr.Location,
                    GROUP_CONCAT(d.DName SEPARATOR '、') as Devices,
                    mr.MeetingRoomStatus as Status
                FROM MeetingRooms mr
                LEFT JOIN MeetingRoomDevices mrd ON mr.CId = mrd.CId
                LEFT JOIN Devices d ON mrd.DId = d.DId
                GROUP BY mr.CId
                ORDER BY mr.Name
            """)
            
            rooms = self.cursor.fetchall()
            
            # 填充表格
            for row_num, room in enumerate(rooms):
                self.table.insertRow(row_num)
                for col_num, value in enumerate(room):
                    item = QTableWidgetItem(str(value) if value is not None else '')
                    if col_num == 3 and value:  # 设备列表列
                        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                        self.table.setWordWrap(True)
                    else:
                        item.setTextAlignment(Qt.AlignCenter)
                    
                    # 设置状态列的颜色
                    if col_num == 4:  # 状态列
                        if value == '空闲':
                            item.setForeground(Qt.green)
                        else:
                            item.setForeground(Qt.red)
                    
                    self.table.setItem(row_num, col_num, item)
            
            # 调整列宽和行高
            header = self.table.horizontalHeader()
            for i in range(5):
                if i == 3:  # 设备列表列
                    header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
                else:
                    header.setSectionResizeMode(i, QHeaderView.Stretch)
            
            # 自动调整行高
            for row in range(self.table.rowCount()):
                self.table.resizeRowToContents(row)
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查询失败: {str(e)}')

    def show_devices(self):
        """显示设备列表"""
        try:
            self.toggle_room_edit_button(False)  # 隐藏会议室编辑按钮
            self.toggle_device_edit_button(True)  # 显示设备编辑按钮
            self.status_label.setText("设备列表如下：")
            
            # 设置表格列
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(4)  # 改为4列，移除操作列
            self.table.setHorizontalHeaderLabels([
                '设备ID', '设备名称', '设备类型', '设备状态'
            ])
            
            # 查询所有设备
            self.cursor.execute("""
                SELECT DId, DName, DType, DStatus
                FROM Devices 
                ORDER BY DId
            """)
            
            devices = self.cursor.fetchall()
            
            # 填充表格
            for row_num, device in enumerate(devices):
                self.table.insertRow(row_num)
                for col_num, value in enumerate(device):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    # 设置状态列的颜色
                    if col_num == 3:
                        if value == '正常':
                            item.setForeground(Qt.green)
                        else:
                            item.setForeground(Qt.red)
                    self.table.setItem(row_num, col_num, item)
            
            self.setup_table_display()
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查询失败: {str(e)}')

    def back_to_main(self):
        """返回主页"""
        self.main_window.show()
        self.close()

    def closeEvent(self, event):
        """窗口关闭时显示主窗口"""
        self.main_window.show()
        event.accept() 

    def show_pending_bookings(self):
        """显示待审核的预订"""
        try:
            self.toggle_room_edit_button(False)
            self.toggle_device_edit_button(False)
            self.status_label.setText("待审核的预订记录如下：")
            
            # 设置表格列
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(8)
            self.table.setHorizontalHeaderLabels([
                '预订编号', '会议室', '预订人', '开始时间', '结束时间', 
                '预订时间', '状态', '操作'
            ])
            
            # 查询待审核的预订
            self.cursor.execute("""
                SELECT 
                    mrr.ReservationId,
                    mr.Name as RoomName,
                    u.Name as UserName,
                    DATE_FORMAT(mrr.StartTime, '%Y-%m-%d %H:%i') as StartTime,
                    DATE_FORMAT(mrr.EndTime, '%Y-%m-%d %H:%i') as EndTime,
                    DATE_FORMAT(mrr.ReservationTime, '%Y-%m-%d %H:%i') as ReservationTime,
                    mrr.ReservationStatus
                FROM MeetingRoomReservation mrr
                JOIN MeetingRooms mr ON mrr.CId = mr.CId
                JOIN Users u ON mrr.No = u.No
                WHERE mrr.ReservationStatus = '待审核'
                ORDER BY mrr.ReservationTime DESC
            """)
            
            bookings = self.cursor.fetchall()
            
            # 填充表格
            for row_num, booking in enumerate(bookings):
                self.table.insertRow(row_num)
                for col_num, value in enumerate(booking):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row_num, col_num, item)
                
                # 添加审核按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                
                approve_btn = QPushButton('通过')
                reject_btn = QPushButton('拒绝')
                approve_btn.setFixedWidth(50)
                reject_btn.setFixedWidth(50)
                
                approve_btn.clicked.connect(
                    lambda checked, rid=booking[0]: self.handle_booking(rid, True))
                reject_btn.clicked.connect(
                    lambda checked, rid=booking[0]: self.handle_booking(rid, False))
                
                btn_layout.addWidget(approve_btn)
                btn_layout.addWidget(reject_btn)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.table.setCellWidget(row_num, 7, btn_widget)
            
            self.setup_table_display()
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查询失败: {str(e)}')

    def handle_booking(self, reservation_id, is_approved):
        """处理预订审核"""
        try:
            status = '已审核' if is_approved else '已取消'
            
            # 首先获取预订的结束时间
            self.cursor.execute("""
                SELECT EndTime, CId 
                FROM MeetingRoomReservation 
                WHERE ReservationId = %s
            """, (reservation_id,))
            end_time, room_id = self.cursor.fetchone()
            
            # 更新预订状态
            self.cursor.execute("""
                UPDATE MeetingRoomReservation 
                SET ReservationStatus = %s
                WHERE ReservationId = %s
            """, (status, reservation_id))
            
            # 如果审核通过
            if is_approved:
                # 更新会议室状态
                self.cursor.execute("""
                    UPDATE MeetingRooms mr
                    JOIN MeetingRoomReservation mrr ON mr.CId = mrr.CId
                    SET mr.MeetingRoomStatus = 
                        CASE 
                            WHEN NOW() BETWEEN mrr.StartTime AND mrr.EndTime THEN '使用中'
                            WHEN NOW() < mrr.StartTime THEN '已预订'
                            WHEN NOW() > mrr.EndTime THEN '待维护'
                        END
                    WHERE mrr.ReservationId = %s
                """, (reservation_id,))
                
                # 创建维护记录
                self.cursor.execute("""
                    INSERT INTO MaintenanceRecords (CId, MDate, MStatus, RContent, MStaff)
                    SELECT 
                        mr.CId,
                        mrr.EndTime,
                        '未维护',
                        '会议结束后例行检查',
                        '待分配'
                    FROM MeetingRooms mr
                    JOIN MeetingRoomReservation mrr ON mr.CId = mrr.CId
                    WHERE mrr.ReservationId = %s
                """, (reservation_id,))
                
                # 创建定时任务来更新会议室状态（使用直接的时间值）
                event_name = f'update_room_status_{reservation_id}'
                self.cursor.execute("""
                    CREATE EVENT IF NOT EXISTS """ + event_name + """
                    ON SCHEDULE AT %s
                    DO
                    UPDATE MeetingRooms 
                    SET MeetingRoomStatus = '待维护'
                    WHERE CId = %s;
                """, (end_time, room_id))
                
            # 如果取消预订
            else:
                self.cursor.execute("""
                    UPDATE MeetingRooms mr
                    JOIN MeetingRoomReservation mrr ON mr.CId = mrr.CId
                    SET mr.MeetingRoomStatus = 
                        CASE 
                            WHEN EXISTS (
                                SELECT 1 
                                FROM MeetingRoomReservation mrr2 
                                WHERE mrr2.CId = mr.CId 
                                AND mrr2.ReservationStatus = '已审核'
                                AND NOW() BETWEEN mrr2.StartTime AND mrr2.EndTime
                            ) THEN '使用中'
                            WHEN EXISTS (
                                SELECT 1 
                                FROM MeetingRoomReservation mrr2 
                                WHERE mrr2.CId = mr.CId 
                                AND mrr2.ReservationStatus = '已审核'
                                AND mrr2.StartTime > NOW()
                            ) THEN '已预订'
                            ELSE '空闲'
                        END
                    WHERE mrr.ReservationId = %s
                """, (reservation_id,))
            
            self.conn.commit()
            QMessageBox.information(self, '成功', f'预订已{status}！')
            
            # 刷新显示
            self.show_pending_bookings()
            self.show_rooms()  # 同步更新会议室列表显示
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'操作失败: {str(e)}')

    def show_maintenance(self):
        """显示维护记录"""
        try:
            self.toggle_room_edit_button(False)
            self.toggle_device_edit_button(False)
            self.status_label.setText("维护记录如下：")
            
            # 设置表格列
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(7)
            self.table.setHorizontalHeaderLabels([
                '记录编号', '会议室', '维护日期', '维护人员', 
                '维护状态', '维护内容', '操作'
            ])
            
            # 查询维护记录
            self.cursor.execute("""
                SELECT 
                    mr.RId,
                    m.Name as RoomName,
                    mr.MDate,
                    mr.MStaff,
                    mr.MStatus,
                    mr.RContent
                FROM MaintenanceRecords mr
                JOIN MeetingRooms m ON mr.CId = m.CId
                ORDER BY mr.MDate DESC
            """)
            
            records = self.cursor.fetchall()
            
            # 填充表格
            for row_num, record in enumerate(records):
                self.table.insertRow(row_num)
                for col_num, value in enumerate(record):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    if col_num == 4:  # 维护状态列
                        if value == '已维护':
                            item.setForeground(Qt.green)
                        elif value == '维护中':
                            item.setForeground(Qt.blue)
                        else:
                            item.setForeground(Qt.red)
                    self.table.setItem(row_num, col_num, item)
                
                # 添加更新按钮
                update_btn = QPushButton('更新状态')
                update_btn.setFixedWidth(80)
                update_btn.clicked.connect(
                    lambda checked, rid=record[0]: self.update_maintenance_status(rid))
                
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                btn_layout.addWidget(update_btn)
                btn_layout.setAlignment(Qt.AlignCenter)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.table.setCellWidget(row_num, 6, btn_widget)
            
            self.setup_table_display()
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查询失败: {str(e)}')


    def show_room_edit(self):
        """打开会议室编辑界面"""
        from .meetingroom_edit import MeetingRoomEdit
        self.room_edit_window = MeetingRoomEdit(self.conn, self)  # 创建编辑窗口实例
        self.room_edit_window.show()
        self.hide()

    def update_maintenance_status(self, record_id):
        """更新维护状态"""
        try:
            # 获取当前状态
            self.cursor.execute("""
                SELECT MStatus, CId FROM MaintenanceRecords WHERE RId = %s
            """, (record_id,))
            current_status, room_id = self.cursor.fetchone()
            
            # 确定下一个状态
            status_flow = {
                '未维护': '维护中',
                '维护中': '已维护',
                '已维护': '已维护'  # 已维护状态不再改变
            }
            
            new_status = status_flow[current_status]
            
            # 更新维护记录状态
            self.cursor.execute("""
                UPDATE MaintenanceRecords 
                SET MStatus = %s,
                    MStaff = CASE 
                        WHEN %s = '已维护' THEN %s
                        ELSE MStaff
                    END
                WHERE RId = %s
            """, (new_status, new_status, self.user_info['Name'], record_id))
            
            # 如果状态更新为"已维护"，更新会议室状态
            if new_status == '已维护':
                # 首先检查是否有当前或未来的已审核预订
                self.cursor.execute("""
                    SELECT COUNT(*) 
                    FROM MeetingRoomReservation 
                    WHERE CId = %s 
                    AND ReservationStatus = '已审核'
                    AND EndTime > NOW()
                """, (room_id,))
                
                future_bookings = self.cursor.fetchone()[0]
                
                # 更新会议室状态
                self.cursor.execute("""
                    UPDATE MeetingRooms 
                    SET MeetingRoomStatus = CASE
                        WHEN EXISTS (
                            SELECT 1 
                            FROM MeetingRoomReservation 
                            WHERE CId = %s 
                            AND ReservationStatus = '已审核'
                            AND NOW() BETWEEN StartTime AND EndTime
                        ) THEN '使用中'
                        WHEN %s > 0 THEN '已预订'
                        ELSE '空闲'
                    END
                    WHERE CId = %s
                """, (room_id, future_bookings, room_id))
            
            self.conn.commit()
            
            QMessageBox.information(self, '成功', 
                f'维护状态已更新为：{new_status}')
            
            # 刷新列表
            self.show_maintenance()
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'更新失败: {str(e)}')

    def show_device_edit(self):
        """打开设备编辑界面"""
        from .device_edit import DeviceEdit
        self.device_edit_window = DeviceEdit(self.conn, self)
        self.device_edit_window.show()
        self.hide()

    def refresh(self):
        """刷新管理系统界面数据"""
        try:
            # 获取当前状态标签文本来判断显示的是哪种数据
            current_status = self.status_label.text()
            
            if "普通用户列表" in current_status:
                self.show_users()
            elif "会议室列表" in current_status:
                self.show_rooms()
            elif "设备列表" in current_status:
                self.show_devices()
            elif "待审核的预订记录" in current_status:
                self.show_pending_bookings()
            elif "维护记录" in current_status:
                self.show_maintenance()
            else:
                # 默认显示会议室列表
                self.show_rooms()
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'刷新数据失败: {str(e)}') 