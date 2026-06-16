from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QScrollArea, QFrame, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database import get_session, StudySession, Subject
class StudyWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet("background:#0f172a;")
        l = QVBoxLayout(self); l.setContentsMargins(30,30,30,30); l.setSpacing(16)
        hdr = QHBoxLayout()
        title = QLabel("Study Sessions"); title.setFont(QFont("Arial",22,QFont.Bold))
        title.setStyleSheet("color:#f1f5f9;"); hdr.addWidget(title); hdr.addStretch()
        fs = "background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:6px;"
        self.filter_cb = QComboBox(); self.filter_cb.setStyleSheet(fs)
        self.filter_cb.addItems(["All","TYT","AYT","YDT"])
        self.filter_cb.currentTextChanged.connect(self.load)
        hdr.addWidget(QLabel("Filter:").setStyleSheet("color:#94a3b8;") or QLabel("Filter:"))
        hdr.addWidget(self.filter_cb)
        l.addLayout(hdr)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        self.container = QWidget(); self.container.setStyleSheet("background:transparent;")
        self.list_l = QVBoxLayout(self.container); self.list_l.setSpacing(8); self.list_l.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.container); l.addWidget(scroll)
        self.load()
    def load(self, _=None):
        while self.list_l.count():
            item = self.list_l.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()
        db = get_session()
        sessions = db.query(StudySession).filter_by(user_id=self.user.id)\
                     .order_by(StudySession.date.desc()).all()
        filt = self.filter_cb.currentText()
        shown = []
        for s in sessions:
            subj = db.query(Subject).get(s.subject_id)
            if filt != "All" and subj and subj.exam_type != filt: continue
            shown.append((s, subj))
        db.close()
        if not shown:
            lbl = QLabel("No study sessions yet."); lbl.setStyleSheet("color:#64748b;font-size:14px;")
            self.list_l.addWidget(lbl)
        else:
            for s, subj in shown: self.list_l.addWidget(self._row(s, subj))
        self.list_l.addStretch()
    def _row(self, s, subj):
        is_inc = bool(s.notes and "Incomplete" in s.notes)
        row = QFrame(); row.setStyleSheet("background:#1e293b;border-radius:8px;")
        l = QHBoxLayout(row); l.setContentsMargins(16,10,16,10)
        subj_name = subj.name if subj else "?"
        date_lbl = QLabel(str(s.date)); date_lbl.setStyleSheet("color:#64748b;font-size:12px;background:transparent;"); date_lbl.setFixedWidth(90)
        name_lbl = QLabel(subj_name); name_lbl.setStyleSheet("color:#f1f5f9;font-size:14px;font-weight:bold;background:transparent;")
        dur_lbl = QLabel(f"{s.duration_minutes} min"); dur_lbl.setStyleSheet("color:#94a3b8;font-size:13px;background:transparent;")
        status_lbl = QLabel("Incomplete" if is_inc else "Done")
        status_lbl.setStyleSheet(f"color:{'#ef4444' if is_inc else '#10b981'};font-size:12px;font-weight:bold;background:transparent;")
        l.addWidget(date_lbl); l.addWidget(name_lbl, 1); l.addWidget(dur_lbl); l.addWidget(status_lbl)
        return row
