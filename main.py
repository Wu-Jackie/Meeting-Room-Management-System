import sys
from PyQt5.QtWidgets import QApplication
import mysql.connector
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_DATABASE
from views.login_window import LoginWindow

def create_tables(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            No INT PRIMARY KEY AUTO_INCREMENT,
            Id VARCHAR(100) NOT NULL,
            Name VARCHAR(100) NOT NULL,
            Gender VARCHAR(10) CHECK (Gender IN ('男', '女')),
            Phone CHAR(11) DEFAULT NULL,
            Dept VARCHAR(100) DEFAULT NULL,
            Position VARCHAR(100) DEFAULT NULL,
            Password CHAR(64),
            Role VARCHAR(5) CHECK (Role IN ('User', 'Admin'))
        )
    """)

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        # 创建数据库连接
        self.conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        
        # 创建表
        cursor = self.conn.cursor()
        create_tables(cursor)
        self.conn.commit()
        
        # 创建登录窗口
        self.login_window = LoginWindow(self.conn)
        self.login_window.show()

    def run(self):
        return self.app.exec_()

if __name__ == '__main__':
    app = App()
    sys.exit(app.run())
