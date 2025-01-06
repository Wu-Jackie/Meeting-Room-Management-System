from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QLineEdit, QComboBox, QMessageBox, QTableWidget,
                            QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt

class DeviceEdit(QWidget):
    def __init__(self, db_connection, admin_window):
        super().__init__()
        self.conn = db_connection
        self.cursor = self.conn.cursor()
        self.admin_window = admin_window
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()
        
        # 添加设备区域
        add_group = QHBoxLayout()
        self.name_input = QLineEdit()
        self.type_input = QLineEdit()
        self.status_input = QComboBox()
        self.status_input.addItems(['正常', '维修中', '报废'])
        
        add_group.addWidget(QLabel('设备名称:'))
        add_group.addWidget(self.name_input)
        add_group.addWidget(QLabel('设备类型:'))
        add_group.addWidget(self.type_input)
        add_group.addWidget(QLabel('设备状态:'))
        add_group.addWidget(self.status_input)
        
        add_btn = QPushButton('添加设备')
        add_btn.clicked.connect(self.add_device)
        add_group.addWidget(add_btn)
        
        layout.addLayout(add_group)
        
        # 设备列表
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['设备ID', '设备名称', '设备类型', '设备状态'])
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
                SELECT DId, DName, DType, DStatus
                FROM Devices
                ORDER BY DId
            """)
            devices = self.cursor.fetchall()
            
            self.table.setRowCount(len(devices))
            for row, device in enumerate(devices):
                for col, value in enumerate(device):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    self.table.setItem(row, col, item)
            
            header = self.table.horizontalHeader()
            for i in range(4):
                header.setSectionResizeMode(i, QHeaderView.Stretch)
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载设备失败: {str(e)}')
            
    def add_device(self):
        try:
            name = self.name_input.text().strip()
            device_type = self.type_input.text().strip()
            status = self.status_input.currentText()
            
            if not name:
                QMessageBox.warning(self, '警告', '请输入设备名称')
                return
            
            # 获取当前最大的 DId
            self.cursor.execute("SELECT MAX(DId) FROM Devices")
            max_id = self.cursor.fetchone()[0]
            new_id = 1 if max_id is None else max_id + 1
                
            self.cursor.execute("""
                INSERT INTO Devices (DId, DName, DType, DStatus)
                VALUES (%s, %s, %s, %s)
            """, (new_id, name, device_type, status))
            
            self.conn.commit()
            QMessageBox.information(self, '成功', '设备添加成功！')
            
            self.name_input.clear()
            self.type_input.clear()  # 清空类型输入框
            self.load_devices()
            
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