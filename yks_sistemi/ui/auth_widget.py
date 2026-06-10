from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                                QPushButton, QFrame, QMessageBox, QStackedWidget)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from database import get_session, User
import bcrypt
FS = "background:#0f172a;color:#f1f5f9;border:1px solid #334155;border-radius:8px;padding:10px;font-size:14px;"
class AuthWidget(QWidget):
    login_success = Signal(object)
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background:#0f172a;")
        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        box = QFrame()
        box.setFixedWidth(360)
        box.setStyleSheet("background:#1e293b;border-radius:16px;")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(32, 32, 32, 32)
        bl.setSpacing(0)
        t = QLabel("YKS Tracker")
        t.setFont(QFont("Arial", 22, QFont.Bold))
        t.setStyleSheet("color:#3b82f6;")
        t.setAlignment(Qt.AlignCenter)
        bl.addWidget(t)
        self.stack = QStackedWidget()
        self.stack.addWidget(self._login_page())
        self.stack.addWidget(self._reg_page())
        bl.addWidget(self.stack)
        outer.addWidget(box, alignment=Qt.AlignCenter)
    def _lbl(self, text, color="#f1f5f9", bold=False, size=14):
        l = QLabel(text)
        l.setStyleSheet(f"color:{color};font-size:{size}px;{'font-weight:bold;' if bold else ''}background:transparent;")
        return l
    def _login_page(self):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        l = QVBoxLayout(w); l.setSpacing(10); l.setContentsMargins(0,16,0,0)
        l.addWidget(self._lbl("Login", bold=True, size=16))
        self.lu = QLineEdit(); self.lu.setPlaceholderText("Username"); self.lu.setStyleSheet(FS)
        self.lp = QLineEdit(); self.lp.setPlaceholderText("Password")
        self.lp.setEchoMode(QLineEdit.Password); self.lp.setStyleSheet(FS)
        btn = QPushButton("Login")
        btn.setStyleSheet("background:#3b82f6;color:white;border-radius:8px;padding:11px;font-size:14px;font-weight:bold;")
        btn.clicked.connect(self.do_login); self.lp.returnPressed.connect(self.do_login)
        self.lerr = self._lbl("", "#ef4444", size=12); self.lerr.setAlignment(Qt.AlignCenter)
        reg = QPushButton("Create Account")
        reg.setStyleSheet("background:transparent;color:#3b82f6;border:none;font-size:13px;")
        reg.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        for w2 in [self.lu, self.lp, btn, self.lerr, reg]: l.addWidget(w2)
        return w
    def _reg_page(self):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        l = QVBoxLayout(w); l.setSpacing(10); l.setContentsMargins(0,16,0,0)
        l.addWidget(self._lbl("Create Account", bold=True, size=16))
        self.ru = QLineEdit(); self.ru.setPlaceholderText("Username"); self.ru.setStyleSheet(FS)
        self.rp = QLineEdit(); self.rp.setPlaceholderText("Password")
        self.rp.setEchoMode(QLineEdit.Password); self.rp.setStyleSheet(FS)
        self.rp2 = QLineEdit(); self.rp2.setPlaceholderText("Confirm Password")
        self.rp2.setEchoMode(QLineEdit.Password); self.rp2.setStyleSheet(FS)
        btn = QPushButton("Register")
        btn.setStyleSheet("background:#10b981;color:white;border-radius:8px;padding:11px;font-size:14px;font-weight:bold;")
        btn.clicked.connect(self.do_register)
        self.rerr = self._lbl("", "#ef4444", size=12); self.rerr.setAlignment(Qt.AlignCenter)
        back = QPushButton("Back to Login")
        back.setStyleSheet("background:transparent;color:#64748b;border:none;font-size:13px;")
        back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        for w2 in [self.ru, self.rp, self.rp2, btn, self.rerr, back]: l.addWidget(w2)
        return w
    def do_login(self):
        u, p = self.lu.text().strip(), self.lp.text()
        if not u or not p:
            self.lerr.setText("Fill all fields."); return
        try:
            s = get_session()
            user = s.query(User).filter_by(username=u).first()
            if not user:
                self.lerr.setText("User not found."); s.close(); return
            if bcrypt.checkpw(p.encode(), user.password.encode()):
                uid = user.id; s.close()
                s2 = get_session()
                user2 = s2.query(User).get(uid); s2.close()
                self.login_success.emit(user2)
            else:
                self.lerr.setText("Wrong password."); s.close()
        except Exception as e:
            self.lerr.setText(str(e)[:60])
    def do_register(self):
        u, p, p2 = self.ru.text().strip(), self.rp.text(), self.rp2.text()
        if not u or not p:
            self.rerr.setText("Fill all fields."); return
        if p != p2:
            self.rerr.setText("Passwords don't match."); return
        if len(p) < 4:
            self.rerr.setText("Password min 4 characters."); return
        try:
            s = get_session()
            if s.query(User).filter_by(username=u).first():
                self.rerr.setText("Username already taken."); s.close(); return
            pw_hash = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
            s.add(User(username=u, password=pw_hash))
            s.commit(); s.close()
            self.ru.clear(); self.rp.clear(); self.rp2.clear()
            self.rerr.setText("")
            self.lu.setText(u); self.lerr.setText("")
            self.stack.setCurrentIndex(0)
            QMessageBox.information(self, "Success", "Account created! Please log in.")
        except Exception as e:
            self.rerr.setText(str(e)[:60])
