# Meeting_Room_Management_System

# 服务器配置MySQL

```shell
#安装MySQL
yum localinstall https://dev.mysql.com/get/mysql57-community-release-el7-11.noarch.rpm -y
rpm --import https://repo.mysql.com/RPM-GPG-KEY-mysql-2022
yum install -y mysql-community-server
systemctl start mysqld
systemctl enable mysqld
grep 'temporary password' /var/log/mysqld.log
mysql_secure_installation
mysql -u root -p

#开启远程登录
show databases;
use mysql;
select user,host from user;
update user set host = '%' where user = 'root';
flush privileges;
```

- 开启日志

<details>
  <summary>my.cnf</summary>

```bash
vim /etc/my.cnf
```

```ini
[client]
port = 3306
socket = /tmp/mysql.sock

[mysqld]
port = 3306
socket = /tmp/mysql.sock
datadir = /var/lib/mysql
pid-file = /var/run/mysqld/mysqld.pid
symbolic-links = 0

default_storage_engine = InnoDB
performance_schema_max_table_instances = 400
table_definition_cache = 400
skip-external-locking
key_buffer_size = 32M
max_allowed_packet = 100G
table_open_cache = 128
sort_buffer_size = 768K
net_buffer_length = 4K
read_buffer_size = 768K
read_rnd_buffer_size = 256K
myisam_sort_buffer_size = 8M
thread_cache_size = 16
query_cache_size = 16M
tmp_table_size = 32M
sql-mode = NO_ENGINE_SUBSTITUTION,STRICT_TRANS_TABLES
explicit_defaults_for_timestamp = true
max_connections = 500
max_connect_errors = 100
open_files_limit = 65535

log-bin = mysql-bin
binlog_format = mixed
server-id = 1
expire_logs_days = 10
slow_query_log = 1
slow_query_log_file = /var/log/mysql-slow.log
long_query_time = 2

innodb_data_home_dir = /var/lib/mysql
innodb_data_file_path = ibdata1:10M:autoextend
innodb_log_group_home_dir = /var/lib/mysql
innodb_buffer_pool_size = 128M
innodb_log_file_size = 64M
innodb_log_buffer_size = 16M
innodb_flush_log_at_trx_commit = 1
innodb_lock_wait_timeout = 50
innodb_max_dirty_pages_pct = 90
innodb_read_io_threads = 2
innodb_write_io_threads = 2

general-log = 1
general-log-file = /var/log/mysql.log
log-error = /var/log/mysql-error.log

[mysqldump]
quick
max_allowed_packet = 500M

[mysql]
no-auto-rehash

[myisamchk]
key_buffer_size = 32M
sort_buffer_size = 768K
read_buffer = 2M
write_buffer = 2M

[mysqlhotcopy]
interactive-timeout
```

</details>

```bash
systemctl restart mysqld
```

- 用户管理

```mysql
CREATE USER 'jackie'@'%' IDENTIFIED BY 'password';
CREATE USER 'Almighty'@'%' IDENTIFIED BY 'password';
CREATE USER 'gllllll6'@'%' IDENTIFIED BY 'password';
CREATE USER 'cure'@'%' IDENTIFIED BY 'password';
```

```mysql
GRANT ALTER,CREATE,SELECT,INSERT,UPDATE ON `Meeting_Room_Management_System`.* TO 'jackie'@'%';
GRANT ALTER,CREATE,SELECT,INSERT,UPDATE ON `Meeting_Room_Management_System`.* TO 'Almighty'@'%';
GRANT ALTER,CREATE,SELECT,INSERT,UPDATE ON `Meeting_Room_Management_System`.* TO 'cure'@'%';
GRANT ALTER,CREATE,SELECT,INSERT,UPDATE ON `Meeting_Room_Management_System`.* TO 'gllllll6'@'%';
FLUSH PRIVILEGES;
```

# 数据库

```mysql
-- 查看字符集
SHOW VARIABLES LIKE 'character_set_database';
-- 更改字符集使其支持中文
ALTER DATABASE `Meeting_Room_Management_System` CHARACTER SET 'utf8mb4';
```

## 创建数据库

```mysql
CREATE DATABASE `Meeting_Room_Management_System`;
```

## 创建表

### Users表

```mysql
-- 创建Users表
CREATE TABLE Users (
    No INT AUTO_INCREMENT PRIMARY KEY,
    Id VARCHAR(100) NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Gender VARCHAR(5) CHECK (Gender IN ('男', '女')),
    Phone CHAR(11),
    Dept VARCHAR(100),
    Position VARCHAR(100),
    Password CHAR(64),
    Role VARCHAR(5) CHECK (Role IN ('User', 'Admin'))
);
```

- NormalUsers视图

```mysql
-- 创建NormalUsers视图
CREATE VIEW NormalUsers AS
SELECT No AS UNo,Id AS UId,Name AS UName,Gender AS UGender,Phone AS UPhone,Dept AS UDept,Position AS UPosition,Password AS UPassword,Role AS URole
FROM Users
WHERE Role = 'User'
WITH CHECK OPTION;
```

- Administers视图

```mysql
-- 创建Administers视图
CREATE VIEW Administers AS
SELECT No AS ANo,Id AS AId,Name AS AName,Gender AS AGender,Phone AS APhone,Dept AS ADept,Position AS APosition,Password AS APassword,Role AS ARole
FROM Users
WHERE Role = 'Admin'
WITH CHECK OPTION;
```

### MeetingRooms表

```mysql
-- 创建MeetingRooms表
CREATE TABLE MeetingRooms (
    CId INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Capacity INT NOT NULL,
    Name VARCHAR(100) NOT NULL,
    Location VARCHAR(100),
    MeetingRoomStatus VARCHAR(100) CHECK (MeetingRoomStatus IN('空闲','使用中','待维护','维护中'))
);
```

### MeetingRoomReservation表

```mysql
-- 创建MeetingRoomReservation表
CREATE TABLE MeetingRoomReservation (
    ReservationId INT AUTO_INCREMENT PRIMARY KEY,
    No INT,
    CId INT,
    ReservationTime DATETIME DEFAULT CURRENT_TIMESTAMP,
    StartTime DATETIME NOT NULL,
    EndTime DATETIME NOT NULL,
    ReservationStatus VARCHAR(20) CHECK (ReservationStatus IN('待审核', '审核通过', '审核未通过', '用户已取消')),
    FOREIGN KEY (No) REFERENCES Users(No),
    FOREIGN KEY (CId) REFERENCES MeetingRooms(CId)
);
```

- CheckUserRoleBeforeInsert触发器

```mysql
-- 使用TRIGGER限定对应No的Role为User
DELIMITER $$

CREATE TRIGGER CheckUserRoleBeforeInsert
BEFORE INSERT ON MeetingRoomReservation
FOR EACH ROW
BEGIN
    DECLARE userRole VARCHAR(5);
    SELECT Role INTO userRole FROM Users WHERE No = NEW.No;
    IF userRole <> 'User' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot reserve meeting room, only Users can make reservations.';
    END IF;
END$$

DELIMITER ;
```

### Divices表

```mysql
-- 创建Divices表
CREATE TABLE Devices (
    DId INT PRIMARY KEY,
    DName VARCHAR(100) NOT NULL,
    DType VARCHAR(50) NOT NULL,
    DStatus VARCHAR(20) CHECK (DStatus IN ('正常', '损坏'))
);
```

### MeetingRoomDevices表

```mysql 
-- 创建MeetingRoomDevices表
CREATE TABLE MeetingRoomDevices (
    CId INT,
    DId INT,
    PRIMARY KEY (CId, DId),
    FOREIGN KEY (CId) REFERENCES MeetingRooms(CId),
    FOREIGN KEY (DId) REFERENCES Devices(DId)
);
```

### MaintenanceRecords表

```mysql
-- 创建MaintenanceRecords表
CREATE TABLE MaintenanceRecords (
    RId INT AUTO_INCREMENT PRIMARY KEY,
    CId INT,
    MDate DATETIME,
    MStaff VARCHAR(50),
    MStatus VARCHAR(20) CHECK (MStatus IN ('未维护', '已维护', '维护中')),
    RContent VARCHAR(255),
    FOREIGN KEY (CId) REFERENCES MeetingRooms(CId)
);
```

# 结构

```
入口
│
登录界面
│
├─主界面
│  ├─查看个人信息
│  │  ├─修改信息
│  │  ├─修改密码
│  │  ├─注销用户
│  │  └─返回主页
│  ├─进入预订系统（普通用户）
│  │  ├─查询总的会议室
│  │  ├─查询空闲会议室
│  │  │  └─预订会议室
│  │  ├─预订查询
│  │  │  └─撤销预订
│  │  └─返回主页
│  ├─进入管理系统（管理员）
│  │  ├─用户列表
│  │  │  └─编辑用户信息
│  │  ├─会议室列表
│  │  │  └─编辑会议室信息
│  │  │     └─添加、编辑、删除会议室
│  │  ├─设备列表
│  │  │  └─编辑会议设备
│  │  │     └─添加、编辑、删除设备
│  │  ├─待审核预订记录
│  │  │  └─处理预订
│  │  ├─维护记录
│  │  │  └─对会议室进行维护
│  │  └─返回主页
│  └─退出登录
```
