from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                                QVBoxLayout, QLabel, QPushButton,
                                QStackedWidget, QFrame, QFileDialog,
                                QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.dashboard_widget import DashboardWidget
from ui.subjects_widget import SubjectsWidget
from ui.study_widget import StudyWidget
from ui.exams_widget import ExamsWidget
from ui.goals_widget import GoalsWidget
from ui.do_it_now_widget import DoItNowWidget
from utils.pdf_reporter import generate_report

class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("YKS Analiz - " + user.username)
        self.setMinimumSize(1100, 700)
        self.setStyleSheet("background-color: #0f172a;")
        self._build_ui()
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        sidebar = QFrame()
        sidebar.setFixedWidth(210)
        sidebar.setStyleSheet("background: #020617;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        logo = QLabel("YKS Tracker")
        logo.setFont(QFont("Arial", 16, QFont.Bold))
        logo.setStyleSheet("color:#3b82f6;padding:24px 20px 8px 20px;")
        sidebar_layout.addWidget(logo)
        user_lbl = QLabel(self.user.username)
        user_lbl.setStyleSheet(
            "color:#64748b;font-size:12px;padding:0 20px 16px 20px;")
        sidebar_layout.addWidget(user_lbl)
        divider = QFrame()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background:#1e293b;")
        sidebar_layout.addWidget(divider)
        self.stack = QStackedWidget()
        self.nav_buttons = []
        pages = [
            ("Dashboard", DashboardWidget(self.user)),
            ("Subjects", SubjectsWidget(self.user)),
            ("Study Sessions", StudyWidget(self.user)),
            ("Trial Exams", ExamsWidget(self.user)),
            ("Goals", GoalsWidget(self.user)),
            ("Do It Now!", DoItNowWidget(self.user)),
        ]
        for idx, (name, widget) in enumerate(pages):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    color:#64748b;background:transparent;
                    border:none;padding:13px 20px;
                    text-align:left;font-size:14px;
                }
                QPushButton:hover{color:#f1f5f9;background:#0f172a;}
                QPushButton:checked{
                    color:#3b82f6;background:#0f172a;
                    border-left:3px solid #3b82f6;
                }
            """)
            btn.clicked.connect(lambda _, i=idx: self.switch_page(i))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)
            self.stack.addWidget(widget)
        sidebar_layout.addStretch()
        divider2 = QFrame()
        divider2.setFixedHeight(1)
        divider2.setStyleSheet("background:#1e293b;")
        sidebar_layout.addWidget(divider2)
        pdf_btn = QPushButton("Export PDF Report")
        pdf_btn.setStyleSheet("""
            QPushButton{
                background:#1e293b;color:#94a3b8;
                border:none;padding:14px 20px;
                text-align:left;font-size:13px;
            }
            QPushButton:hover{color:#f1f5f9;}
        """)
        pdf_btn.clicked.connect(self.export_pdf)
        sidebar_layout.addWidget(pdf_btn)
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stack)
        self.switch_page(0)
    def switch_page(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setChecked(i == index)
    def export_pdf(self):
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export PDF", "yks_report.pdf", "PDF (*.pdf)")
        if filepath:
            try:
                generate_report(self.user, filepath)
                QMessageBox.information(self, "Success",
                                        "Report saved:\n" + filepath)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))