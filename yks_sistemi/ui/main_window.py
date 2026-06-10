from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                                QPushButton, QLabel, QStackedWidget, QFrame,
                                QFileDialog, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from ui.dashboard_widget import DashboardWidget
from ui.subjects_widget import SubjectsWidget
from ui.study_widget import StudyWidget
from ui.exams_widget import ExamsWidget
from ui.goals_widget import GoalsWidget
from ui.do_it_now_widget import DoItNowWidget
ACTIVE   = "background:#3b82f6;color:white;border:none;border-radius:8px;padding:10px 16px;text-align:left;font-size:14px;font-weight:bold;"
INACTIVE = "background:transparent;color:#94a3b8;border:none;border-radius:8px;padding:10px 16px;text-align:left;font-size:14px;"
NAV = [("Dashboard","dashboard"),("Subjects","subjects"),("Study Sessions","study"),
       ("Trial Exams","exams"),("Goals","goals"),("Do It Now!","donow")]
class MainWindow(QMainWindow):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("YKS Tracker")
        self.setMinimumSize(1100, 680)
        c = QWidget(); self.setCentralWidget(c)
        root = QHBoxLayout(c); root.setContentsMargins(0,0,0,0); root.setSpacing(0)
        sb = QFrame(); sb.setFixedWidth(210); sb.setStyleSheet("background:#020617;")
        sl = QVBoxLayout(sb); sl.setContentsMargins(12,24,12,16); sl.setSpacing(4)
        brand = QLabel("YKS Tracker")
        brand.setFont(QFont("Arial",16,QFont.Bold))
        brand.setStyleSheet("color:#3b82f6;padding:0 8px 2px 8px;")
        sl.addWidget(brand)
        ul = QLabel(self.user.username)
        ul.setStyleSheet("color:#475569;font-size:11px;padding:0 8px 14px 8px;")
        sl.addWidget(ul)
        self.nav_btns = []
        for lbl, key in NAV:
            btn = QPushButton(lbl); btn.setStyleSheet(INACTIVE)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda _, k=key: self.navigate(k))
            sl.addWidget(btn); self.nav_btns.append((key, btn))
        sl.addStretch()
        pdf_btn = QPushButton("Export to PDF")
        pdf_btn.setStyleSheet(
            "background:#1e293b;color:#cbd5e1;border:1px solid #334155;"
            "border-radius:6px;padding:9px;font-size:12px;")
        pdf_btn.setCursor(Qt.PointingHandCursor)
        pdf_btn.clicked.connect(self.export_pdf)
        sl.addWidget(pdf_btn)
        root.addWidget(sb)
        cw = QFrame(); cw.setStyleSheet("background:#0f172a;")
        cl = QVBoxLayout(cw); cl.setContentsMargins(0,0,0,0)
        self.stack = QStackedWidget()
        self.pages = {
            "dashboard": DashboardWidget(self.user),
            "subjects":  SubjectsWidget(self.user),
            "study":     StudyWidget(self.user),
            "exams":     ExamsWidget(self.user),
            "goals":     GoalsWidget(self.user),
            "donow":     DoItNowWidget(self.user),
        }
        for p in self.pages.values(): self.stack.addWidget(p)
        self.pages["donow"].session_saved.connect(self.pages["dashboard"].refresh)
        cl.addWidget(self.stack)
        root.addWidget(cw, 1)
        self.navigate("dashboard")
    def navigate(self, key):
        if key in self.pages: self.stack.setCurrentWidget(self.pages[key])
        for k, btn in self.nav_btns:
            btn.setStyleSheet(ACTIVE if k==key else INACTIVE)
    def export_pdf(self):
        try:
            from ui.pdf_export import generate_pdf
            fname, _ = QFileDialog.getSaveFileName(
                self, "Save PDF", f"YKS_Report_{self.user.username}.pdf",
                "PDF Files (*.pdf)")
            if fname:
                generate_pdf(self.user, fname)
                QMessageBox.information(self, "Done", f"PDF saved:\n{fname}")
        except ImportError:
            QMessageBox.warning(self, "Missing packages",
                "Run: pip install reportlab matplotlib")
        except Exception as e:
            QMessageBox.warning(self, "PDF Error", str(e))
