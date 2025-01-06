from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QComboBox, QMessageBox, QTableWidget,
                            QTableWidgetItem, QHeaderView, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class DeviceEdit(QWidget):
    def __init__(self, db_connection, admin_window):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.admin_window = admin_window
        self.initUI()
        
    def initUI(self):
        # 设置窗口图标
        self.setWindowIcon(QIcon("resources/logo.png"))
        
        layout = QVBoxLayout()
        
        # 添加设备区域
        add_group = QHBoxLayout()
        self.name_input = QLineEdit()
        self.type_input = QLineEdit()
        self.status_input = QComboBox()
        self.status_input.addItems(['正常', '维修中', '报废'])
        
        # 添加会议室选择下拉框
        self.room_input = QComboBox()
        self.load_meeting_rooms()  # 加载会议室列表
        
        add_group.addWidget(QLabel('设备名称:'))
        add_group.addWidget(self.name_input)
        add_group.addWidget(QLabel('设备类型:'))
        add_group.addWidget(self.type_input)
        add_group.addWidget(QLabel('设备状态:'))
        add_group.addWidget(self.status_input)
        add_group.addWidget(QLabel('所属会议室:'))
        add_group.addWidget(self.room_input)
        
        add_btn = QPushButton('添加设备')
        add_btn.clicked.connect(self.add_device)
        add_group.addWidget(add_btn)
        
        layout.addLayout(add_group)
        
        # 设备列表
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # 增加会议室和操作列
        self.table.setHorizontalHeaderLabels(['设备ID', '设备名称', '设备类型', '设备状态', '所属会议室', '操作'])
        layout.addWidget(self.table)
        
        # 返回按钮
        back_btn = QPushButton('返回')
        back_btn.clicked.connect(self.back_to_admin)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
        self.setWindowTitle('编辑设备信息')
        self.setFixedSize(800, 600)
        
        self.load_devices()
        
    def load_devices(self):
        try:
            self.cursor.execute("""
                SELECT d.DId, d.DName, d.DType, d.DStatus, 
                       GROUP_CONCAT(mr.Name SEPARATOR '、') as RoomNames
                FROM Devices d
                LEFT JOIN MeetingRoomDevices mrd ON d.DId = mrd.DId
                LEFT JOIN MeetingRooms mr ON mrd.CId = mr.CId
                GROUP BY d.DId
                ORDER BY d.DId
            """)
            devices = self.cursor.fetchall()
            
            self.table.setRowCount(len(devices))
            for row, device in enumerate(devices):
                for col, value in enumerate(device):
                    item = QTableWidgetItem(str(value) if value else '')
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)
                
                # 添加操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                edit_btn = QPushButton("编辑")
                delete_btn = QPushButton("删除")
                
                edit_btn.clicked.connect(lambda _, d=device[0]: self.edit_device(d))
                delete_btn.clicked.connect(lambda _, d=device[0]: self.delete_device(d))
                
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.table.setCellWidget(row, 5, btn_widget)
            
            header = self.table.horizontalHeader()
            header.setSectionResizeMode(4, QHeaderView.Stretch)  # 会议室列可伸缩
            for i in [0,1,2,3,5]:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载设备失败: {str(e)}')

    def load_meeting_rooms(self):
        """加载会议室列表到下拉框"""
        try:
            self.cursor.execute("SELECT CId, Name FROM MeetingRooms")
            rooms = self.cursor.fetchall()
            self.room_input.clear()
            self.room_input.addItem('未分配', None)  # 添加一个空选项
            for room in rooms:
                self.room_input.addItem(room[1], room[0])  # 使用room[0]作为userData
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载会议室列表失败: {str(e)}')

    def edit_device(self, device_id):
        """编辑设备"""
        try:
            # 获取设备当前信息，包括会议室关联
            self.cursor.execute("""
                SELECT d.DName, d.DType, d.DStatus, mr.CId
                FROM Devices d
                LEFT JOIN MeetingRoomDevices mrd ON d.DId = mrd.DId
                LEFT JOIN MeetingRooms mr ON mrd.CId = mr.CId
                WHERE d.DId = %s
            """, (device_id,))
            device = self.cursor.fetchone()
            
            dialog = DeviceEditDialog(device, self)
            if dialog.exec_():
                name, device_type, status, room_id = dialog.get_data()
                
                # 更新设备基本信息
                self.cursor.execute("""
                    UPDATE Devices 
                    SET DName = %s, DType = %s, DStatus = %s
                    WHERE DId = %s
                """, (name, device_type, status, device_id))
                
                # 检查是否已存在关联记录
                self.cursor.execute("""
                    SELECT COUNT(*) FROM MeetingRoomDevices 
                    WHERE DId = %s
                """, (device_id,))
                exists = self.cursor.fetchone()[0] > 0
                
                if room_id is not None:  # 选择了会议室
                    if exists:
                        # 更新现有关联
                        self.cursor.execute("""
                            UPDATE MeetingRoomDevices 
                            SET CId = %s 
                            WHERE DId = %s
                        """, (room_id, device_id))
                    else:
                        # 插入新关联
                        self.cursor.execute("""
                            INSERT INTO MeetingRoomDevices (CId, DId)
                            VALUES (%s, %s)
                        """, (room_id, device_id))
                else:  # 选择了"未分配"
                    if exists:
                        # 删除现有关联
                        self.cursor.execute("""
                            DELETE FROM MeetingRoomDevices 
                            WHERE DId = %s
                        """, (device_id,))
                
                self.conn.commit()
                self.load_devices()  # 立即刷新数据
                QMessageBox.information(self, '成功', '更新设备成功')
                
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'更新设备失败: {str(e)}')

    def delete_device(self, device_id):
        """删除设备"""
        try:
            reply = QMessageBox.question(self, '确认', 
                                       '确定要删除这个设备吗？',
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # 先删除关联关系
                self.cursor.execute("DELETE FROM MeetingRoomDevices WHERE DId = %s", (device_id,))
                # 再删除设备
                self.cursor.execute("DELETE FROM Devices WHERE DId = %s", (device_id,))
                self.conn.commit()
                
                QMessageBox.information(self, '成功', '删除设备成功')
                self.load_devices()
                
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'删除设备失败: {str(e)}')

    def add_device(self):
        try:
            name = self.name_input.text().strip()
            device_type = self.type_input.text().strip()
            status = self.status_input.currentText()
            room_id = self.room_input.currentData()  # 获取选中的会议室ID
            
            if not name:
                QMessageBox.warning(self, '警告', '请输入设备名称')
                return
            
            # 获取当前最大的 DId
            self.cursor.execute("SELECT MAX(DId) FROM Devices")
            max_id = self.cursor.fetchone()[0]
            new_id = 1 if max_id is None else max_id + 1
                
            # 添加设备
            self.cursor.execute("""
                INSERT INTO Devices (DId, DName, DType, DStatus)
                VALUES (%s, %s, %s, %s)
            """, (new_id, name, device_type, status))
            
            # 如果选择了会议室，添加关联关系
            if room_id:
                self.cursor.execute("""
                    INSERT INTO MeetingRoomDevices (CId, DId)
                    VALUES (%s, %s)
                """, (room_id, new_id))
            
            self.conn.commit()
            self.load_devices()  # 刷新数据
            QMessageBox.information(self, '成功', '设备添加成功！')
            
            # 清空输入框
            self.name_input.clear()
            self.type_input.clear()
            self.status_input.setCurrentIndex(0)
            self.room_input.setCurrentIndex(0)
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'添加设备失败: {str(e)}')
            
    def back_to_admin(self):
        self.admin_window.refresh()
        self.admin_window.show()
        self.close()
        
    def closeEvent(self, event):
        self.admin_window.show()
        event.accept() 

class DeviceEditDialog(QDialog):
    def __init__(self, device_data, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # 先创建所有控件
        self.name_edit = QLineEdit(device_data[0])
        self.type_edit = QLineEdit(device_data[1])
        self.status_edit = QComboBox()
        self.status_edit.addItems(['正常', '维修中', '报废'])
        self.status_edit.setCurrentText(device_data[2])
        
        self.room_edit = QComboBox()
        self.room_edit.addItem('未分配', None)  # 添加一个空选项
        
        # 获取所有会议室
        try:
            self.parent.cursor.execute("SELECT CId, Name FROM MeetingRooms")
            rooms = self.parent.cursor.fetchall()
            for room in rooms:
                self.room_edit.addItem(room[1], room[0])
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载会议室列表失败: {str(e)}')
            
        # 设置当前会议室
        if device_data[3]:
            index = self.room_edit.findData(device_data[3])
            if index >= 0:
                self.room_edit.setCurrentIndex(index)
        
        # 初始化UI
        self.initUI(device_data)
        
    def initUI(self, device_data):
        layout = QVBoxLayout()
        
        # 创建表单 - 使用垂直布局
        form_layout = QVBoxLayout()
        
        # 设备名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("设备名称:"))
        name_layout.addWidget(self.name_edit)
        form_layout.addLayout(name_layout)
        
        # 设备类型
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("设备类型:"))
        type_layout.addWidget(self.type_edit)
        form_layout.addLayout(type_layout)
        
        # 设备状态
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("设备状态:"))
        status_layout.addWidget(self.status_edit)
        form_layout.addLayout(status_layout)
        
        # 所属会议室
        room_layout = QHBoxLayout()
        room_layout.addWidget(QLabel("所属会议室:"))
        room_layout.addWidget(self.room_edit)
        form_layout.addLayout(room_layout)
        
        layout.addLayout(form_layout)
        
        # 添加确定和取消按钮
        btn_layout = QHBoxLayout()
        confirm_btn = QPushButton("确定")
        cancel_btn = QPushButton("取消")
        
        confirm_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(confirm_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        self.setWindowTitle('编辑设备')
        
    def get_data(self):
        """获取表单数据"""
        return (
            self.name_edit.text().strip(),
            self.type_edit.text().strip(),
            self.status_edit.currentText(),
            self.room_edit.currentData()
        ) 