from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QComboBox)
from PyQt5.QtCore import Qt

class MeetingRoomEdit(QWidget):
    def __init__(self, db_connection, parent=None):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.parent = parent
        self.initUI()
        self.load_rooms()

    def initUI(self):
        layout = QVBoxLayout()
        
        # 添加会议室表单
        form_layout = QHBoxLayout()
        
        self.name_edit = QLineEdit()
        self.capacity_edit = QLineEdit()
        self.location_edit = QLineEdit()
        
        form_layout.addWidget(QLabel("会议室名称:"))
        form_layout.addWidget(self.name_edit)
        form_layout.addWidget(QLabel("容纳人数:"))
        form_layout.addWidget(self.capacity_edit)
        form_layout.addWidget(QLabel("位置:"))
        form_layout.addWidget(self.location_edit)
        
        # 添加按钮
        self.add_btn = QPushButton("添加会议室")
        form_layout.addWidget(self.add_btn)
        
        layout.addLayout(form_layout)
        
        # 会议室列表
        self.room_table = QTableWidget()
        self.room_table.setColumnCount(5)
        self.room_table.setHorizontalHeaderLabels(["名称", "容纳人数", "位置", "设备", "操作"])
        layout.addWidget(self.room_table)
        
        # 返回按钮
        self.back_btn = QPushButton("返回")
        layout.addWidget(self.back_btn)
        
        # 绑定事件
        self.add_btn.clicked.connect(self.add_room)
        self.back_btn.clicked.connect(self.back_to_admin)
        
        self.setLayout(layout)
        self.setWindowTitle('会议室管理')
        self.setFixedSize(800, 600)

    def load_rooms(self):
        """加载会议室列表"""
        try:
            self.cursor.execute("""
                SELECT mr.Name, mr.Capacity, mr.Location,
                       GROUP_CONCAT(d.DName SEPARATOR '、') as Devices
                FROM MeetingRooms mr
                LEFT JOIN MeetingRoomDevices mrd ON mr.CId = mrd.CId
                LEFT JOIN Devices d ON mrd.DId = d.DId
                GROUP BY mr.CId
            """)
            rooms = self.cursor.fetchall()
            
            self.room_table.setRowCount(0)
            for row, room in enumerate(rooms):
                self.room_table.insertRow(row)
                for col, value in enumerate(room):
                    item = QTableWidgetItem(str(value) if value else '')
                    item.setTextAlignment(Qt.AlignCenter)
                    self.room_table.setItem(row, col, item)
                
                # 添加操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                edit_btn = QPushButton("编辑")
                delete_btn = QPushButton("删除")
                
                edit_btn.clicked.connect(lambda _, r=room[0]: self.edit_room(r))
                delete_btn.clicked.connect(lambda _, r=room[0]: self.delete_room(r))
                
                btn_layout.addWidget(edit_btn)
                btn_layout.addWidget(delete_btn)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.room_table.setCellWidget(row, 4, btn_widget)
            
            # 调整列宽
            header = self.room_table.horizontalHeader()
            for i in range(5):
                if i == 3:  # 设备列
                    header.setSectionResizeMode(i, QHeaderView.Stretch)
                else:
                    header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
                    
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载会议室失败: {str(e)}')

    def add_room(self):
        """添加新会议室"""
        try:
            name = self.name_edit.text().strip()
            capacity = self.capacity_edit.text().strip()
            location = self.location_edit.text().strip()
            
            if not all([name, capacity, location]):
                QMessageBox.warning(self, '警告', '请填写所有字段')
                return
                
            if not capacity.isdigit():
                QMessageBox.warning(self, '警告', '容纳人数必须为数字')
                return
                
            self.cursor.execute("""
                INSERT INTO MeetingRooms (Name, Capacity, Location, MeetingRoomStatus)
                VALUES (%s, %s, %s, '空闲')
            """, (name, int(capacity), location))
            
            self.conn.commit()
            QMessageBox.information(self, '成功', '添加会议室成功')
            
            # 清空输入框并刷新列表
            self.name_edit.clear()
            self.capacity_edit.clear()
            self.location_edit.clear()
            self.load_rooms()
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'添加会议室失败: {str(e)}')

    def edit_room(self, room_id):
        """编辑会议室"""
        # 找到对应的行
        for row in range(self.room_table.rowCount()):
            if self.room_table.item(row, 0).text() == room_id:
                # 使前三列可编辑
                for col in range(3):
                    current_item = self.room_table.item(row, col)
                    current_text = current_item.text()
                    new_item = QTableWidgetItem(current_text)
                    new_item.setTextAlignment(Qt.AlignCenter)
                    self.room_table.setItem(row, col, new_item)

                # 更改操作按钮
                btn_widget = QWidget()
                btn_layout = QHBoxLayout(btn_widget)
                confirm_btn = QPushButton("确认")
                cancel_btn = QPushButton("取消")
                
                confirm_btn.clicked.connect(lambda _, r=row: self.confirm_edit(r))
                cancel_btn.clicked.connect(self.load_rooms)  # 取消直接重新加载
                
                btn_layout.addWidget(confirm_btn)
                btn_layout.addWidget(cancel_btn)
                btn_layout.setContentsMargins(0, 0, 0, 0)
                
                self.room_table.setCellWidget(row, 4, btn_widget)
                break

    def confirm_edit(self, row):
        """确认编辑会议室"""
        try:
            name = self.room_table.item(row, 0).text().strip()
            capacity = self.room_table.item(row, 1).text().strip()
            location = self.room_table.item(row, 2).text().strip()
            
            if not all([name, capacity, location]):
                QMessageBox.warning(self, '警告', '请填写所有字段')
                return
                
            if not capacity.isdigit():
                QMessageBox.warning(self, '警告', '容纳人数必须为数字')
                return

            # 获取原始会议室名称（作为WHERE条件）
            original_name = name  # 因为我们用name作为标识符
                
            self.cursor.execute("""
                UPDATE MeetingRooms 
                SET Name = %s, Capacity = %s, Location = %s
                WHERE Name = %s
            """, (name, int(capacity), location, original_name))
            
            self.conn.commit()
            QMessageBox.information(self, '成功', '更新会议室成功')
            self.load_rooms()
            
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'更新会议室失败: {str(e)}')

    def delete_room(self, room_id):
        """删除会议室"""
        try:
            reply = QMessageBox.question(self, '确认', 
                                       '确定要删除这个会议室吗？',
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM MeetingRoomDevices WHERE CId = %s", (room_id,))
                self.cursor.execute("DELETE FROM MeetingRooms WHERE CId = %s", (room_id,))
                self.conn.commit()
                
                QMessageBox.information(self, '成功', '删除会议室成功')
                self.load_rooms()
                
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, '错误', f'删除会议室失败: {str(e)}')

    def back_to_admin(self):
        """返回管理界面"""
        if self.parent:
            self.parent.refresh()  # 先刷新父窗口数据
            self.parent.show()     # 再显示父窗口
        self.close() 