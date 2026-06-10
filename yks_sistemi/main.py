import sys
import database
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    login = LoginWindow()
    if login.exec():
        user = login.current_user
        try:
            window = MainWindow(user)
            window.show()
            sys.exit(app.exec())
        except Exception as e:
            QMessageBox.critical(None, "Error", str(e))
if __name__ == "__main__":
    main()