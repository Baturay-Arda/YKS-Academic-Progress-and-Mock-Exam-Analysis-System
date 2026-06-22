from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel,
                                QLineEdit, QPushButton, QMessageBox,
                                QFormLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database import get_session, User
class RegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.new_user = None
        self.setWindowTitle("Create Account")
        self.setFixedSize(360, 280)
        self.setStyleSheet(
            "QDialog{background:#0f172a;}"
            "QLabel{color:#f1f5f9;}"
            "QLineEdit{background:#1e293b;color:white;border:1px solid #334155;"
            "border-radius:6px;padding:10px;font-size:14px;}"
            "QPushButton{background:#10b981;color:white;border-radius:6px;"
            "padding:10px;font-size:14px;font-weight:bold;}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)
        title = QLabel("Create New Account")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color:#10b981;")
        layout.addWidget(title)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        layout.addWidget(self.username_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choose a password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)
        self.password2_input = QLineEdit()
        self.password2_input.setPlaceholderText("Confirm password")
        self.password2_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password2_input)
        btn = QPushButton("Create Account")
        btn.clicked.connect(self.register)
        layout.addWidget(btn)
    def register(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        password2 = self.password2_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
            return
        if password != password2:
            QMessageBox.warning(self, "Error", "Passwords do not match.")
            return
        session = get_session()
        existing = session.query(User).filter_by(username=username).first()
        if existing:
            QMessageBox.warning(self, "Error", "Username already taken.")
            session.close()
            return
        user = User(username=username, password=password)
        session.add(user)
        session.commit()
        self.new_user = user
        session.close()
        QMessageBox.information(self, "Success",
                                "Account created! Welcome, " + username + "!")
        self.accept()
class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.current_user = None
        self.setWindowTitle("YKS Academic Development System")
        self.setFixedSize(400, 380)
        self.setStyleSheet("background-color: #0f172a;")
        self._build_ui()
    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(40, 40, 40, 40)
        title = QLabel("YKS Tracker")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #3b82f6;")
        layout.addWidget(title)
        subtitle = QLabel("Login with your account")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #64748b; font-size: 12px;")
        layout.addWidget(subtitle)
        field_style = ("background:#1e293b;color:white;"
                       "border:1px solid #334155;border-radius:6px;"
                       "padding:10px;font-size:14px;")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet(field_style)
        layout.addWidget(self.username_input)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(field_style)
        layout.addWidget(self.password_input)
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet(
            "background:#3b82f6;color:white;border-radius:6px;"
            "padding:10px;font-size:14px;font-weight:bold;")
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)
        register_btn = QPushButton("Register - Create new account")
        register_btn.setStyleSheet(
            "background:#1e293b;color:#94a3b8;border:1px solid #334155;"
            "border-radius:6px;padding:10px;font-size:13px;")
        register_btn.clicked.connect(self.open_register)
        layout.addWidget(register_btn)
    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in both fields.")
            return
        session = get_session()
        user = session.query(User).filter_by(
            username=username, password=password).first()
        session.close()
        if user:
            self.current_user = user
            self.accept()
        else:
            QMessageBox.warning(self, "Error",
                                "Incorrect username or password.")
    def open_register(self):
        dialog = RegisterDialog(self)
        if dialog.exec():
            self.current_user = dialog.new_user
            self.accept()