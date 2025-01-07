

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for Devices
-- ----------------------------
DROP TABLE IF EXISTS `Devices`;
CREATE TABLE `Devices`  (
  `DId` int(11) NOT NULL,
  `DName` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `DType` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `DStatus` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`DId`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Devices
-- ----------------------------
INSERT INTO `Devices` VALUES (1, 'ThinkBook16+', '笔记本电脑', '正常');
INSERT INTO `Devices` VALUES (2, 'HP高级投影屏', '投影屏', '正常');
INSERT INTO `Devices` VALUES (3, 'ASUS天选3', '笔记本电脑', '正常');

-- ----------------------------
-- Table structure for MaintenanceRecords
-- ----------------------------
DROP TABLE IF EXISTS `MaintenanceRecords`;
CREATE TABLE `MaintenanceRecords`  (
  `RId` int(11) NOT NULL AUTO_INCREMENT,
  `CId` int(11) NULL DEFAULT NULL,
  `MDate` datetime NULL DEFAULT NULL,
  `MStaff` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `MStatus` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `RContent` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`RId`) USING BTREE,
  INDEX `CId`(`CId`) USING BTREE,
  CONSTRAINT `MaintenanceRecords_ibfk_1` FOREIGN KEY (`CId`) REFERENCES `MeetingRooms` (`CId`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of MaintenanceRecords
-- ----------------------------
INSERT INTO `MaintenanceRecords` VALUES (1, 1, '2025-01-07 15:32:49', 'Jackie', '已维护', '会议结束后例行检查');
INSERT INTO `MaintenanceRecords` VALUES (2, 2, '2025-01-07 16:00:36', 'Jackie', '已维护', '会议结束后例行检查');
INSERT INTO `MaintenanceRecords` VALUES (3, 1, '2025-01-07 17:25:37', 'slm', '已维护', '会议结束后例行检查');
INSERT INTO `MaintenanceRecords` VALUES (4, 1, '2025-01-07 17:35:55', 'gllllll6', '已维护', '会议结束后例行检查');
INSERT INTO `MaintenanceRecords` VALUES (5, 1, '2025-01-07 17:40:24', 'Jackie', '已维护', '会议结束后例行检查');

-- ----------------------------
-- Table structure for MeetingRoomDevices
-- ----------------------------
DROP TABLE IF EXISTS `MeetingRoomDevices`;
CREATE TABLE `MeetingRoomDevices`  (
  `CId` int(11) NOT NULL,
  `DId` int(11) NOT NULL,
  PRIMARY KEY (`CId`, `DId`) USING BTREE,
  INDEX `DId`(`DId`) USING BTREE,
  CONSTRAINT `MeetingRoomDevices_ibfk_1` FOREIGN KEY (`CId`) REFERENCES `MeetingRooms` (`CId`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `MeetingRoomDevices_ibfk_2` FOREIGN KEY (`DId`) REFERENCES `Devices` (`DId`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of MeetingRoomDevices
-- ----------------------------
INSERT INTO `MeetingRoomDevices` VALUES (1, 1);
INSERT INTO `MeetingRoomDevices` VALUES (1, 2);
INSERT INTO `MeetingRoomDevices` VALUES (2, 3);

-- ----------------------------
-- Table structure for MeetingRoomReservation
-- ----------------------------
DROP TABLE IF EXISTS `MeetingRoomReservation`;
CREATE TABLE `MeetingRoomReservation`  (
  `ReservationId` int(11) NOT NULL AUTO_INCREMENT,
  `No` int(11) NULL DEFAULT NULL,
  `CId` int(11) NULL DEFAULT NULL,
  `ReservationTime` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `StartTime` datetime NOT NULL,
  `EndTime` datetime NOT NULL,
  `ReservationStatus` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`ReservationId`) USING BTREE,
  INDEX `No`(`No`) USING BTREE,
  INDEX `CId`(`CId`) USING BTREE,
  CONSTRAINT `MeetingRoomReservation_ibfk_1` FOREIGN KEY (`No`) REFERENCES `Users` (`No`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `MeetingRoomReservation_ibfk_2` FOREIGN KEY (`CId`) REFERENCES `MeetingRooms` (`CId`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 13 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of MeetingRoomReservation
-- ----------------------------
INSERT INTO `MeetingRoomReservation` VALUES (1, 2, 1, '2025-01-05 22:10:04', '2025-01-05 22:10:50', '2025-01-05 22:15:50', '已取消');
INSERT INTO `MeetingRoomReservation` VALUES (2, 2, 1, '2025-01-05 22:10:28', '2025-01-05 22:11:20', '2025-01-05 22:15:20', '已审核');
INSERT INTO `MeetingRoomReservation` VALUES (3, 3, 1, '2025-01-06 15:16:35', '2025-01-06 15:20:22', '2025-01-06 16:16:22', '已取消');
INSERT INTO `MeetingRoomReservation` VALUES (4, 3, 1, '2025-01-06 15:18:02', '2025-01-06 15:18:57', '2025-01-06 16:17:57', '已取消');
INSERT INTO `MeetingRoomReservation` VALUES (6, 2, 1, '2025-01-07 11:20:09', '2025-01-07 11:25:53', '2025-01-07 11:45:53', '已审核');
INSERT INTO `MeetingRoomReservation` VALUES (8, 2, 1, '2025-01-07 15:29:01', '2025-01-07 15:30:49', '2025-01-07 15:32:49', '已审核');
INSERT INTO `MeetingRoomReservation` VALUES (9, 2, 2, '2025-01-07 15:51:50', '2025-01-07 15:55:36', '2025-01-07 16:00:36', '已审核');

-- ----------------------------
-- Table structure for MeetingRooms
-- ----------------------------
DROP TABLE IF EXISTS `MeetingRooms`;
CREATE TABLE `MeetingRooms`  (
  `CId` int(11) NOT NULL AUTO_INCREMENT,
  `Capacity` int(11) NOT NULL,
  `Name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Location` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `MeetingRoomStatus` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`CId`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of MeetingRooms
-- ----------------------------
INSERT INTO `MeetingRooms` VALUES (1, 10, '会议室1', '101H', '空闲');
INSERT INTO `MeetingRooms` VALUES (2, 10, '会议室2', '202H', '空闲');
INSERT INTO `MeetingRooms` VALUES (3, 12, '会议室3', '303H', '空闲');

-- ----------------------------
-- Table structure for Users
-- ----------------------------
DROP TABLE IF EXISTS `Users`;
CREATE TABLE `Users`  (
  `No` int(11) NOT NULL AUTO_INCREMENT,
  `Id` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NOT NULL,
  `Gender` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Phone` char(11) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Dept` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Position` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Password` char(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  `Role` varchar(5) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`No`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 11 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of Users
-- ----------------------------

-- 以下电话号均为杜撰的测试号码
INSERT INTO `Users` VALUES (1, 'test', 'Jackie', '男', '13111111111', '管理部', '管理员', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'Admin');
INSERT INTO `Users` VALUES (2, 'test2', 'gllllll6', '男', '14111111111', '科技部', '职员', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'User');
INSERT INTO `Users` VALUES (3, '22', '李四', '男', '15111111111', '后勤部', '员工', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'User');
INSERT INTO `Users` VALUES (7, '33', '王五', '女', '16111111111', '人事处', 'HR', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'User');
INSERT INTO `Users` VALUES (8, '44', '12138', '男', '17111111111', '产品部', '产品经理', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'Admin');
INSERT INTO `Users` VALUES (9, '55', 'name', '男', '18111111111', '管理部', '管理员', '6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b', 'Admin');

-- ----------------------------
-- View structure for Administers
-- ----------------------------
DROP VIEW IF EXISTS `Administers`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `Administers` AS select `Users`.`No` AS `ANo`,`Users`.`Id` AS `AId`,`Users`.`Name` AS `AName`,`Users`.`Gender` AS `AGender`,`Users`.`Phone` AS `APhone`,`Users`.`Dept` AS `ADept`,`Users`.`Position` AS `APosition`,`Users`.`Password` AS `APassword`,`Users`.`Role` AS `ARole` from `Users` where (`Users`.`Role` = 'Admin')  WITH CASCADED CHECK OPTION;

-- ----------------------------
-- View structure for NormalUsers
-- ----------------------------
DROP VIEW IF EXISTS `NormalUsers`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `NormalUsers` AS select `Users`.`No` AS `UNo`,`Users`.`Id` AS `UId`,`Users`.`Name` AS `UName`,`Users`.`Gender` AS `UGender`,`Users`.`Phone` AS `UPhone`,`Users`.`Dept` AS `UDept`,`Users`.`Position` AS `UPosition`,`Users`.`Password` AS `UPassword`,`Users`.`Role` AS `URole` from `Users` where (`Users`.`Role` = 'User')  WITH CASCADED CHECK OPTION;

-- ----------------------------
-- Triggers structure for table MeetingRoomReservation
-- ----------------------------
DROP TRIGGER IF EXISTS `CheckUserRoleBeforeInsert`;
delimiter ;;
CREATE TRIGGER `CheckUserRoleBeforeInsert` BEFORE INSERT ON `MeetingRoomReservation` FOR EACH ROW BEGIN
    DECLARE userRole VARCHAR(5);
    SELECT Role INTO userRole FROM Users WHERE No = NEW.No;
    IF userRole <> 'User' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Cannot reserve meeting room, only Users can make reservations.';
    END IF;
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
