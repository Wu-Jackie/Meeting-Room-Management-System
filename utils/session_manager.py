from datetime import datetime, timedelta

class SessionManager:
    def __init__(self, timeout_minutes=1):
        self.timeout_minutes = timeout_minutes
        self.last_activity = datetime.now()
        
    def update_activity(self):
        """更新最后活动时间"""
        self.last_activity = datetime.now()
        
    def is_session_expired(self):
        """检查会话是否过期"""
        current_time = datetime.now()
        time_difference = current_time - self.last_activity
        return time_difference > timedelta(minutes=self.timeout_minutes) 