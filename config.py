import hashlib

# 数据库配置信息
DB_HOST = "x.x.x.x"
DB_USER = "x"
DB_PASSWORD = "x"
DB_DATABASE = "Meeting_Room_Management_System"

def hash_password(password: str) -> str:
    """对密码进行SHA256加密"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest() 