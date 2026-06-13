from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QDialog, QFormLayout, QLineEdit,
                                QComboBox, QDateEdit, QSpinBox, QScrollArea,
                                QFrame, QGridLayout, QMessageBox)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from database import get_session, TrialExam, TrialResult, Subject
class ExamsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet("background:#0f172a;")
        l = QVBoxLayout(self); l.setContentsMargins(30,30,30,30); l.setSpacing(16)
        hdr = QHBoxLayout()
        title = QLabel("Trial Exams"); title.setFont(QFont("Arial",22,QFont.Bold))
        title.setStyleSheet("color:#f1f5f9;"); hdr.addWidget(title); hdr.addStretch()
        add_btn = QPushButton("+ Add Exam")
        add_btn.setStyleSheet("background:#3b82f6;color:white;border-radius:6px;padding:8px 16px;")
        add_btn.clicked.connect(self.add_exam); hdr.addWidget(add_btn)
        l.addLayout(hdr)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        container = QWidget(); container.setStyleSheet("background:transparent;")
        self.grid = QGridLayout(container); self.grid.setSpacing(16)
        scroll.setWidget(container); l.addWidget(scroll)
        self.load()
    def load(self):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w: w.deleteLater()
        db = get_session()
        all_exams = db.query(TrialExam).filter_by(user_id=self.user.id)\
                      .order_by(TrialExam.date.desc()).all()
        try:
            exams = [e for e in all_exams if not (getattr(e,'notes',None) and "Incomplete" in e.notes)]
        except Exception:
            exams = all_exams
        rows = []
        for e in exams:
            try: total = sum(r.net for r in db.query(TrialResult).filter_by(trial_exam_id=e.id).all())
            except Exception: total = 0.0
            rows.append({"id":e.id,"name":e.name,"exam_type":e.exam_type,"date":str(e.date),"total":total})
        db.close()
        for i, row in enumerate(rows):
            self.grid.addWidget(self._exam_card(row), i//3, i%3)
        if not rows:
            lbl = QLabel("No trial exams yet. Click '+ Add Exam' to get started.")
            lbl.setStyleSheet("color:#64748b;font-size:14px;")
            self.grid.addWidget(lbl, 0, 0)
    def _exam_card(self, row):
        card = QFrame(); card.setStyleSheet("background:#1e293b;border-radius:12px;")
        l = QVBoxLayout(card); l.setContentsMargins(20,16,20,16); l.setSpacing(8)
        top = QHBoxLayout()
        name = QLabel(row["name"]); name.setFont(QFont("Arial",14,QFont.Bold))
        name.setStyleSheet("color:#f1f5f9;background:transparent;")
        top.addWidget(name); top.addStretch()
        badge = QLabel(row["exam_type"])
        badge.setStyleSheet("background:#1e40af;color:white;border-radius:4px;padding:2px 8px;font-size:12px;")
        top.addWidget(badge); l.addLayout(top)
        dl = QLabel(row["date"]); dl.setStyleSheet("color:#64748b;font-size:13px;background:transparent;")
        l.addWidget(dl)
        sep = QFrame(); sep.setFrameShape(QFrame.HLine); sep.setStyleSheet("color:#334155;"); l.addWidget(sep)
        nl = QLabel("Total Net"); nl.setStyleSheet("color:#64748b;font-size:12px;background:transparent;"); l.addWidget(nl)
        nv = QLabel(f"{row['total']:.2f}"); nv.setFont(QFont("Arial",22,QFont.Bold))
        nv.setStyleSheet("color:#3b82f6;background:transparent;"); l.addWidget(nv)
        sb = QPushButton("View / Edit Scores")
        sb.setStyleSheet("background:#0f172a;color:#94a3b8;border:1px solid #334155;border-radius:6px;padding:6px;font-size:12px;")
        sb.clicked.connect(lambda _, eid=row["id"], etype=row["exam_type"], ename=row["name"]: self._score_dialog(eid, etype, ename))
        l.addWidget(sb)
        return card
    def _score_dialog(self, exam_id, exam_type, exam_name):
        db = get_session()
        subjects = db.query(Subject).filter_by(user_id=self.user.id, exam_type=exam_type).all()
        results = db.query(TrialResult).filter_by(trial_exam_id=exam_id).all()
        existing = {r.subject_id: {"correct":r.correct,"wrong":r.wrong,"empty":r.empty} for r in results}
        subj_data = [{"id":s.id,"name":s.name} for s in subjects]
        db.close()
        if not subj_data:
            QMessageBox.information(self,"Info",f"No subjects for {exam_type}."); return
        d = QDialog(self); d.setWindowTitle(f"Scores - {exam_name}")
        d.setMinimumSize(500, 80+len(subj_data)*44)
        d.setStyleSheet("QDialog{background:#0f172a;}QLabel{color:#f1f5f9;}"
            "QSpinBox{background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:4px;}"
            "QPushButton{background:#3b82f6;color:white;border-radius:6px;padding:8px 16px;}")
        dl=QVBoxLayout(d); dl.setContentsMargins(20,20,20,20)
        hdr=QHBoxLayout()
        for h in ["Subject","Correct","Wrong","Empty","Net"]:
            lb=QLabel(h); lb.setStyleSheet("color:#64748b;font-weight:bold;"); hdr.addWidget(lb)
        dl.addLayout(hdr); rows=[]
        for sub in subj_data:
            ex_r=existing.get(sub["id"],{})
            row=QHBoxLayout(); nl=QLabel(sub["name"])
            c=QSpinBox(); c.setRange(0,40); c.setValue(ex_r.get("correct",0))
            w=QSpinBox(); w.setRange(0,40); w.setValue(ex_r.get("wrong",0))
            e=QSpinBox(); e.setRange(0,40); e.setValue(ex_r.get("empty",0))
            ni=round(ex_r.get("correct",0)-ex_r.get("wrong",0)*0.25,2)
            nl2=QLabel(f"{ni:.2f}")
            nl2.setStyleSheet("color:"+("#10b981" if ni>=0 else "#ef4444")+";font-weight:bold;")
            def upd(_,c=c,w=w,nl=nl2):
                net=c.value()-w.value()*0.25; nl.setText(f"{net:.2f}")
                nl.setStyleSheet("color:"+("#10b981" if net>=0 else "#ef4444")+";font-weight:bold;")
            c.valueChanged.connect(upd); w.valueChanged.connect(upd)
            for ww in [nl,c,w,e,nl2]: row.addWidget(ww)
            dl.addLayout(row); rows.append((sub["id"],c,w,e))
        sb=QPushButton("Save Scores"); dl.addWidget(sb)
        def save():
            s=get_session()
            for sid,c,w,e in rows:
                net=round(c.value()-w.value()*0.25,2)
                ex_r=s.query(TrialResult).filter_by(trial_exam_id=exam_id,subject_id=sid).first()
                if ex_r: ex_r.correct=c.value(); ex_r.wrong=w.value(); ex_r.empty=e.value(); ex_r.net=net
                else: s.add(TrialResult(trial_exam_id=exam_id,subject_id=sid,correct=c.value(),wrong=w.value(),empty=e.value(),net=net))
            s.commit(); s.close(); d.accept()
            QMessageBox.information(self,"Saved","Scores saved!"); self.load()
        sb.clicked.connect(save); d.exec()
    def add_exam(self):
        d=QDialog(self); d.setWindowTitle("Add Trial Exam"); d.setFixedSize(320,220)
        d.setStyleSheet("QDialog{background:#0f172a;}QLabel{color:#f1f5f9;}"
            "QLineEdit,QComboBox,QDateEdit{background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:8px;}"
            "QPushButton{background:#3b82f6;color:white;border-radius:6px;padding:8px;}")
        form=QFormLayout(d)
        ni=QLineEdit(); ni.setPlaceholderText("e.g. 345 Yayinlari")
        tc=QComboBox(); tc.addItems(["TYT","AYT","YDT"])
        di=QDateEdit(QDate.currentDate()); di.setCalendarPopup(True)
        form.addRow("Name:",ni); form.addRow("Type:",tc); form.addRow("Date:",di)
        btn=QPushButton("Save"); form.addRow(btn)
        def nxt():
            name=ni.text().strip()
            if not name: QMessageBox.warning(d,"Error","Name required."); return
            s=get_session()
            exam=TrialExam(user_id=self.user.id,name=name,exam_type=tc.currentText(),date=di.date().toPython())
            s.add(exam); s.commit(); s.close()
            d.accept(); self.load()
        btn.clicked.connect(nxt); d.exec()
