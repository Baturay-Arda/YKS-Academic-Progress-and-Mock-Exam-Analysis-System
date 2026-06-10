from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, QLabel, QFrame)
from PySide6.QtCore import Slot
from PySide6.QtGui import QFont
from database import get_session, StudySession, TrialExam, Subject, Goal
class DashboardWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet("background:#0f172a;")
        l = QVBoxLayout(self); l.setContentsMargins(30,30,30,30); l.setSpacing(20)
        t = QLabel("Dashboard"); t.setFont(QFont("Arial",22,QFont.Bold))
        t.setStyleSheet("color:#f1f5f9;"); l.addWidget(t)
        s = QLabel("Your YKS preparation overview.")
        s.setStyleSheet("color:#64748b;font-size:14px;"); l.addWidget(s)
        self.grid = QGridLayout(); self.grid.setSpacing(16)
        l.addLayout(self.grid); l.addStretch()
        self.refresh()
    @Slot()
    def refresh(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w: w.deleteLater()
        db = get_session()
        all_ss = db.query(StudySession).filter_by(user_id=self.user.id).all()
        complete_ss = [s for s in all_ss if not (s.notes and "Incomplete" in s.notes)]
        total_min = sum(s.duration_minutes or 0 for s in complete_ss)
        h, m = divmod(total_min, 60)
        all_ex = db.query(TrialExam).filter_by(user_id=self.user.id).all()
        try:
            complete_ex = [e for e in all_ex if not (getattr(e, 'notes', None) and "Incomplete" in e.notes)]
        except Exception:
            complete_ex = all_ex
        subjects = db.query(Subject).filter_by(user_id=self.user.id).all()
        total_t = sum(len(s.topics) for s in subjects)
        done_t  = sum(1 for s in subjects for t in s.topics if t.status=="completed")
        try:
            goal_n = db.query(Goal).filter_by(user_id=self.user.id).count()
        except Exception:
            goal_n = 0
        db.close()
        stats = [
            ("Total Study Time", f"{h}h {m}m", "#3b82f6"),
            ("Trial Exams Done", str(len(complete_ex)), "#8b5cf6"),
            ("Topics Completed", f"{done_t}/{total_t}", "#10b981"),
            ("Active Goals",     str(goal_n), "#f59e0b"),
        ]
        for i,(lbl,val,col) in enumerate(stats):
            self.grid.addWidget(self._card(lbl,val,col), 0, i)
    def _card(self, label, value, color):
        c = QFrame()
        c.setStyleSheet(f"background:#1e293b;border-radius:12px;border-left:4px solid {color};")
        l = QVBoxLayout(c); l.setContentsMargins(20,16,20,16)
        lb = QLabel(label); lb.setStyleSheet("color:#64748b;font-size:13px;background:transparent;")
        vl = QLabel(value); vl.setFont(QFont("Arial",22,QFont.Bold))
        vl.setStyleSheet(f"color:{color};background:transparent;")
        l.addWidget(lb); l.addWidget(vl)
        return c
