from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QDialog, QLineEdit, QComboBox,
                                QScrollArea, QFrame, QMessageBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from database import get_session, Subject, Topic
class SubjectsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet("background:#0f172a;")
        main = QVBoxLayout(self); main.setContentsMargins(30,30,30,30); main.setSpacing(16)
        hdr = QHBoxLayout()
        title = QLabel("Subjects / Topics"); title.setFont(QFont("Arial",22,QFont.Bold))
        title.setStyleSheet("color:#f1f5f9;"); hdr.addWidget(title); hdr.addStretch()
        main.addLayout(hdr)
        fs = "background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:8px;"
        add_bar = QHBoxLayout()
        self.subj_name = QLineEdit(); self.subj_name.setPlaceholderText("Subject name"); self.subj_name.setStyleSheet(fs)
        self.subj_type = QComboBox(); self.subj_type.addItems(["TYT","AYT","YDT"]); self.subj_type.setStyleSheet(fs)
        self.subj_type.setFixedWidth(100)
        add_s_btn = QPushButton("+ Add Subject")
        add_s_btn.setStyleSheet("background:#3b82f6;color:white;border-radius:6px;padding:9px 16px;font-weight:bold;")
        add_s_btn.clicked.connect(self.add_subject)
        add_bar.addWidget(self.subj_name, 1); add_bar.addWidget(self.subj_type); add_bar.addWidget(add_s_btn)
        main.addLayout(add_bar)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        self.container = QWidget(); self.container.setStyleSheet("background:transparent;")
        self.list_l = QVBoxLayout(self.container); self.list_l.setSpacing(12); self.list_l.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.container); main.addWidget(scroll)
        self.load()
    def load(self):
        while self.list_l.count():
            item = self.list_l.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()
        db = get_session()
        subjects = db.query(Subject).filter_by(user_id=self.user.id).all()
        for s in subjects: self.list_l.addWidget(self._subject_card(s))
        db.close()
        if not subjects:
            lbl = QLabel("No subjects yet. Add one above.")
            lbl.setStyleSheet("color:#64748b;font-size:14px;"); self.list_l.addWidget(lbl)
        self.list_l.addStretch()
    def _subject_card(self, subj):
        card = QFrame(); card.setStyleSheet("background:#1e293b;border-radius:12px;")
        l = QVBoxLayout(card); l.setContentsMargins(20,16,20,16); l.setSpacing(10)
        top = QHBoxLayout()
        nm = QLabel(subj.name); nm.setFont(QFont("Arial",15,QFont.Bold))
        nm.setStyleSheet("color:#f1f5f9;background:transparent;")
        badge = QLabel(subj.exam_type)
        badge.setStyleSheet("background:#1e40af;color:white;border-radius:4px;padding:2px 8px;font-size:12px;")
        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background:#7f1d1d;color:#fca5a5;border-radius:4px;padding:4px 10px;font-size:11px;")
        del_btn.clicked.connect(lambda _, sid=subj.id: self.delete_subject(sid))
        top.addWidget(nm); top.addStretch(); top.addWidget(badge); top.addWidget(del_btn)
        l.addLayout(top)
        db = get_session()
        topics = db.query(Topic).filter_by(subject_id=subj.id).all()
        db.close()
        for t in topics:
            tr = QHBoxLayout()
            status_color = {"completed":"#10b981","in_progress":"#f59e0b"}.get(t.status,"#64748b")
            tl = QLabel(f"• {t.name}"); tl.setStyleSheet("color:#cbd5e1;font-size:13px;background:transparent;")
            ts = QLabel(t.status.replace("_"," ").title()); ts.setStyleSheet(f"color:{status_color};font-size:11px;background:transparent;")
            tr.addWidget(tl); tr.addStretch(); tr.addWidget(ts)
            l.addLayout(tr)
        fs = "background:#0f172a;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:6px;"
        tadd = QHBoxLayout()
        tinp = QLineEdit(); tinp.setPlaceholderText("New topic name"); tinp.setStyleSheet(fs)
        tbtn = QPushButton("+ Topic")
        tbtn.setStyleSheet("background:#0f172a;color:#3b82f6;border:1px solid #3b82f6;border-radius:6px;padding:6px 12px;font-size:12px;")
        tbtn.clicked.connect(lambda _, sid=subj.id, inp=tinp: self.add_topic(sid, inp))
        tadd.addWidget(tinp); tadd.addWidget(tbtn)
        l.addLayout(tadd)
        return card
    def add_subject(self):
        name = self.subj_name.text().strip()
        if not name: QMessageBox.warning(self,"Error","Subject name required."); return
        db = get_session()
        db.add(Subject(user_id=self.user.id, name=name, exam_type=self.subj_type.currentText()))
        db.commit(); db.close()
        self.subj_name.clear(); self.load()
    def add_topic(self, subject_id, inp):
        name = inp.text().strip()
        if not name: return
        db = get_session()
        db.add(Topic(subject_id=subject_id, name=name))
        db.commit(); db.close()
        inp.clear(); self.load()
    def delete_subject(self, subject_id):
        if QMessageBox.question(self,"Delete?","Delete this subject and all its topics?",
                                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db = get_session()
            s = db.query(Subject).get(subject_id)
            if s: db.delete(s); db.commit()
            db.close(); self.load()
