class WindowManager:
    def __init__(self):
        self.current_window = None

    def show_login(self, conn):
        from .login_window import LoginWindow
        self.current_window = LoginWindow(conn)
        self.current_window.show()
        return self.current_window

    def show_main(self, conn, user_info):
        from .main_window import MainWindow
        self.current_window = MainWindow(conn, user_info)
        self.current_window.show()
        return self.current_window