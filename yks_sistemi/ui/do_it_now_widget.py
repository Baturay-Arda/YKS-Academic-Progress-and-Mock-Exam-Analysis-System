from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QComboBox, QSpinBox, QLineEdit,
                                QFrame, QStackedWidget, QListWidget,
                                QListWidgetItem, QDialog, QMessageBox)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont, QColor
from database import get_session, Subject, Topic, StudySession, TrialExam, TrialResult
from datetime import date, timedelta
import sys
def play_alarm():
    try:
        if sys.platform == "win32":
            import winsound
            for _ in range(5): winsound.Beep(1000, 400)
    except Exception: pass
class DoItNowWidget(QWidget):
    session_saved = Signal()
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.remaining_seconds = 0
        self.current_mode = "study"
        self.current_data = None
        self.setStyleSheet("background:#0f172a;")
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)
        layout.addWidget(self._left_panel(), 3)
        layout.addWidget(self._right_panel(), 2)
        self._load_history()
    def _left_panel(self):
        frame = QFrame(); frame.setStyleSheet("background:#0f172a;")
        l = QVBoxLayout(frame); l.setContentsMargins(30,30,20,30); l.setSpacing(18)
        title = QLabel("Do It Now!")
        title.setFont(QFont("Arial",26,QFont.Bold)); title.setStyleSheet("color:#f1f5f9;")
        l.addWidget(title)
        toggle = QHBoxLayout()
        self.study_btn = QPushButton("Study Session")
        self.exam_btn  = QPushButton("Trial Exam")
        self._on  = "background:#3b82f6;color:white;border-radius:8px;padding:10px 20px;font-size:14px;font-weight:bold;"
        self._off = "background:#1e293b;color:#64748b;border-radius:8px;padding:10px 20px;font-size:14px;"
        self.study_btn.setStyleSheet(self._on); self.exam_btn.setStyleSheet(self._off)
        self.study_btn.clicked.connect(lambda: self.switch_mode("study"))
        self.exam_btn.clicked.connect(lambda: self.switch_mode("exam"))
        toggle.addWidget(self.study_btn); toggle.addWidget(self.exam_btn)
        l.addLayout(toggle)
        self.form_stack = QStackedWidget()
        self.form_stack.addWidget(self._study_form())
        self.form_stack.addWidget(self._exam_form())
        l.addWidget(self.form_stack)
        tf = QFrame(); tf.setStyleSheet("background:#1e293b;border-radius:16px;")
        tl = QVBoxLayout(tf); tl.setContentsMargins(20,20,20,12)
        self.timer_lbl = QLabel("00:00")
        self.timer_lbl.setFont(QFont("Arial",64,QFont.Bold))
        self.timer_lbl.setAlignment(Qt.AlignCenter)
        self.timer_lbl.setStyleSheet("color:#3b82f6;background:transparent;")
        tl.addWidget(self.timer_lbl)
        self.status_lbl = QLabel("Set duration and press Start")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet("color:#64748b;font-size:13px;background:transparent;")
        tl.addWidget(self.status_lbl)
        l.addWidget(tf)
        br = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("background:#10b981;color:white;border-radius:8px;padding:12px;font-size:16px;font-weight:bold;")
        self.start_btn.clicked.connect(self.start_session)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("background:#ef4444;color:white;border-radius:8px;padding:12px;font-size:16px;font-weight:bold;")
        self.stop_btn.clicked.connect(self.stop_session); self.stop_btn.setVisible(False)
        br.addWidget(self.start_btn); br.addWidget(self.stop_btn)
        l.addLayout(br); l.addStretch()
        return frame
    def _study_form(self):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        l = QVBoxLayout(w); l.setSpacing(10)
        fs = "background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:8px;"
        ls = "color:#94a3b8;font-size:13px;"
        db = get_session()
        subjects = db.query(Subject).filter_by(user_id=self.user.id).all(); db.close()
        self.study_subj_cb = QComboBox(); self.study_subj_cb.setStyleSheet(fs)
        for s in subjects: self.study_subj_cb.addItem(s.name, s.id)
        self.study_topic_cb = QComboBox(); self.study_topic_cb.setStyleSheet(fs)
        def upd_t(idx):
            self.study_topic_cb.clear()
            if self.study_subj_cb.count()==0: return
            sid = self.study_subj_cb.itemData(idx)
            s2 = get_session()
            for t in s2.query(Topic).filter_by(subject_id=sid).all():
                self.study_topic_cb.addItem(t.name, t.id)
            s2.close()
        self.study_subj_cb.currentIndexChanged.connect(upd_t)
        if subjects: upd_t(0)
        self.study_dur = QSpinBox(); self.study_dur.setRange(1,300); self.study_dur.setValue(25)
        self.study_dur.setSuffix(" min"); self.study_dur.setStyleSheet(fs)
        for lt,wg in [("Subject:",self.study_subj_cb),("Topic:",self.study_topic_cb),("Duration:",self.study_dur)]:
            row=QHBoxLayout(); lb=QLabel(lt); lb.setStyleSheet(ls); lb.setFixedWidth(80)
            row.addWidget(lb); row.addWidget(wg); l.addLayout(row)
        return w
    def _exam_form(self):
        w = QWidget(); w.setStyleSheet("background:transparent;")
        l = QVBoxLayout(w); l.setSpacing(10)
        fs = "background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:8px;"
        ls = "color:#94a3b8;font-size:13px;"
        self.exam_type_cb = QComboBox(); self.exam_type_cb.setStyleSheet(fs)
        self.exam_type_cb.addItems(["TYT","AYT","YDT"])
        self.exam_name_inp = QLineEdit(); self.exam_name_inp.setPlaceholderText("e.g. 345 Yayinlari")
        self.exam_name_inp.setStyleSheet(fs)
        self.exam_dur = QSpinBox(); self.exam_dur.setRange(1,300); self.exam_dur.setValue(135)
        self.exam_dur.setSuffix(" min"); self.exam_dur.setStyleSheet(fs)
        def upd_d(text): self.exam_dur.setValue({"TYT":135,"AYT":180,"YDT":120}.get(text,135))
        self.exam_type_cb.currentTextChanged.connect(upd_d)
        for lt,wg in [("Type:",self.exam_type_cb),("Name:",self.exam_name_inp),("Duration:",self.exam_dur)]:
            row=QHBoxLayout(); lb=QLabel(lt); lb.setStyleSheet(ls); lb.setFixedWidth(80)
            row.addWidget(lb); row.addWidget(wg); l.addLayout(row)
        return w
    def _right_panel(self):
        frame = QFrame(); frame.setStyleSheet("background:#020617;")
        l = QVBoxLayout(frame); l.setContentsMargins(20,30,30,30); l.setSpacing(10)
        title = QLabel("Completed")
        title.setFont(QFont("Arial",18,QFont.Bold)); title.setStyleSheet("color:#f1f5f9;")
        l.addWidget(title)
        hint = QLabel("Double-click any item to enter scores")
        hint.setStyleSheet("color:#475569;font-size:12px;"); l.addWidget(hint)
        self.done_list = QListWidget()
        self.done_list.setStyleSheet(
            "QListWidget{background:#0f172a;color:#f1f5f9;border:none;border-radius:8px;}"
            "QListWidget::item{padding:14px;border-bottom:1px solid #1e293b;}"
            "QListWidget::item:hover{background:#1e293b;}"
            "QListWidget::item:selected{background:#1e3a5f;}")
        self.done_list.itemDoubleClicked.connect(self.open_score_dialog)
        l.addWidget(self.done_list)
        return frame
    def _load_history(self):
        since = date.today() - timedelta(days=7)
        db = get_session()
        try:
            sessions = db.query(StudySession).filter(
                StudySession.user_id==self.user.id, StudySession.date>=since
            ).order_by(StudySession.date.desc()).all()
            for s in sessions:
                is_inc = bool(s.notes and "Incomplete" in s.notes)
                status = "INCOMPLETE" if is_inc else "DONE"
                subj = s.subject.name if s.subject else "?"
                topic = s.topic.name if s.topic else "?"
                label = f"{subj} - {topic}"
                suffix = "  [incomplete]" if is_inc else "  (double-click for scores)"
                item = QListWidgetItem(f"{status}  |  Study: {label}  |  {s.duration_minutes}min  [{s.date}]{suffix}")
                item.setData(Qt.UserRole, {"type":"study","session_id":s.id,"label":label,"completed":not is_inc})
                item.setForeground(QColor("#ef4444" if is_inc else "#10b981"))
                self.done_list.addItem(item)
            exams = db.query(TrialExam).filter(
                TrialExam.user_id==self.user.id, TrialExam.date>=since
            ).order_by(TrialExam.date.desc()).all()
            for e in exams:
                try: is_inc = bool(getattr(e, 'notes', None) and "Incomplete" in e.notes)
                except Exception: is_inc = False
                status = "INCOMPLETE" if is_inc else "DONE"
                suffix = "  [incomplete]" if is_inc else "  (double-click for scores)"
                item = QListWidgetItem(f"{status}  |  Exam: {e.name} ({e.exam_type})  [{e.date}]{suffix}")
                item.setData(Qt.UserRole, {"type":"exam","exam_id":e.id,"exam_type":e.exam_type,"label":e.name,"completed":not is_inc})
                item.setForeground(QColor("#ef4444" if is_inc else "#10b981"))
                self.done_list.addItem(item)
        except Exception as ex:
            print(f"History load: {ex}")
        db.close()
    def switch_mode(self, mode):
        self.current_mode = mode
        self.study_btn.setStyleSheet(self._on if mode=="study" else self._off)
        self.exam_btn.setStyleSheet(self._off if mode=="study" else self._on)
        self.form_stack.setCurrentIndex(0 if mode=="study" else 1)
    def start_session(self):
        if self.current_mode == "study":
            if not self.study_subj_cb.currentData():
                QMessageBox.warning(self,"Error","No subjects. Add one first."); return
            self.current_data = {"mode":"study","subject_id":self.study_subj_cb.currentData(),
                "topic_id":self.study_topic_cb.currentData(),"duration":self.study_dur.value(),
                "label":self.study_subj_cb.currentText()+" - "+self.study_topic_cb.currentText()}
        else:
            name = self.exam_name_inp.text().strip() or self.exam_type_cb.currentText()
            self.current_data = {"mode":"exam","exam_type":self.exam_type_cb.currentText(),"name":name,
                "duration":self.exam_dur.value(),"label":name+" ("+self.exam_type_cb.currentText()+")"}
        self.remaining_seconds = self.current_data["duration"] * 60
        self._refresh_display()
        self.timer.start(1000)
        self.start_btn.setVisible(False); self.stop_btn.setVisible(True)
        self.status_lbl.setText("In progress: "+self.current_data["label"])
    def tick(self):
        self.remaining_seconds -= 1; self._refresh_display()
        if self.remaining_seconds <= 0:
            self.timer.stop(); play_alarm(); self._save_session(True)
    def _refresh_display(self):
        m, s = divmod(self.remaining_seconds, 60)
        self.timer_lbl.setText(f"{m:02d}:{s:02d}")
        color = "#ef4444" if self.remaining_seconds<=300 else "#f59e0b" if self.remaining_seconds<=600 else "#3b82f6"
        self.timer_lbl.setStyleSheet(f"color:{color};background:transparent;")
    def stop_session(self):
        if QMessageBox.question(self,"Stop?","Stop this session?\nIt will be marked as incomplete.",
                                QMessageBox.Yes|QMessageBox.No)==QMessageBox.Yes:
            self.timer.stop(); self._save_session(False)
    def _save_session(self, completed):
        self.start_btn.setVisible(True); self.stop_btn.setVisible(False)
        self.timer_lbl.setText("00:00"); self.timer_lbl.setStyleSheet("color:#3b82f6;background:transparent;")
        self.status_lbl.setText("Set duration and press Start")
        data = self.current_data
        if not data: return
        elapsed = max(1, data["duration"] - self.remaining_seconds//60)
        note = None if completed else "Incomplete"
        status = "DONE" if completed else "INCOMPLETE"
        color = QColor("#10b981" if completed else "#ef4444")
        db = get_session()
        try:
            if data["mode"] == "study":
                obj = StudySession(user_id=self.user.id, subject_id=data["subject_id"],
                    topic_id=data["topic_id"], date=date.today(), duration_minutes=elapsed, notes=note)
                db.add(obj); db.flush(); sid = obj.id; db.commit()
                suffix = "  (double-click for scores)" if completed else "  [incomplete]"
                item = QListWidgetItem(f"{status}  |  Study: {data['label']}  |  {elapsed}min{suffix}")
                item.setData(Qt.UserRole, {"type":"study","session_id":sid,"label":data["label"],"completed":completed})
            else:
                exam = TrialExam(user_id=self.user.id, name=data["name"],
                                 exam_type=data["exam_type"], date=date.today())
                try: exam.notes = note
                except Exception: pass
                db.add(exam); db.flush(); eid = exam.id; db.commit()
                suffix = "  (double-click for scores)" if completed else "  [incomplete]"
                item = QListWidgetItem(f"{status}  |  Exam: {data['label']}{suffix}")
                item.setData(Qt.UserRole, {"type":"exam","exam_id":eid,"exam_type":data["exam_type"],"label":data["label"],"completed":completed})
        except Exception as ex:
            print(f"Save error: {ex}"); db.rollback(); db.close(); return
        db.close()
        item.setForeground(color)
        self.done_list.insertItem(0, item)
        self.current_data = None
        self.session_saved.emit()
    def open_score_dialog(self, item):
        data = item.data(Qt.UserRole)
        if not data: return
        if not data.get("completed", True):
            QMessageBox.information(self,"Info","This session was incomplete."); return
        if data.get("type") == "study": self._study_scores(item, data)
        elif data.get("type") == "exam": self._exam_scores(item, data)
    def _study_scores(self, item, data):
        d = QDialog(self); d.setWindowTitle("Enter Test Scores"); d.setFixedSize(340,280)
        d.setStyleSheet("QDialog{background:#0f172a;}QLabel{color:#f1f5f9;}"
            "QSpinBox{background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:6px;}"
            "QPushButton{background:#3b82f6;color:white;border-radius:6px;padding:8px 16px;}")
        l = QVBoxLayout(d); l.setContentsMargins(20,20,20,20); l.setSpacing(12)
        fs = "background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:6px;"
        ls = "color:#94a3b8;font-size:13px;"
        info = QLabel("Session: "+data.get("label",""))
        info.setStyleSheet("color:#64748b;font-size:12px;background:transparent;"); l.addWidget(info)
        c = QSpinBox(); c.setRange(0,200); c.setStyleSheet(fs)
        w = QSpinBox(); w.setRange(0,200); w.setStyleSheet(fs)
        e = QSpinBox(); e.setRange(0,200); e.setStyleSheet(fs)
        for lt,sp in [("Correct:",c),("Wrong:",w),("Empty:",e)]:
            row=QHBoxLayout(); lb=QLabel(lt); lb.setStyleSheet(ls); lb.setFixedWidth(70)
            row.addWidget(lb); row.addWidget(sp); l.addLayout(row)
        nl = QLabel("Net: 0.00")
        nl.setStyleSheet("color:#10b981;font-size:15px;font-weight:bold;background:transparent;")
        nl.setAlignment(Qt.AlignCenter); l.addWidget(nl)
        def upd(_):
            net = c.value()-w.value()*0.25
            nl.setText(f"Net: {net:.2f}")
            nl.setStyleSheet("color:"+("#10b981" if net>=0 else "#ef4444")+";font-size:15px;font-weight:bold;background:transparent;")
        c.valueChanged.connect(upd); w.valueChanged.connect(upd)
        sb = QPushButton("Save Scores"); l.addWidget(sb)
        def save():
            net = round(c.value()-w.value()*0.25,2)
            if data.get("session_id"):
                db=get_session(); sess=db.query(StudySession).get(data["session_id"])
                if sess: sess.notes=f"Correct:{c.value()} Wrong:{w.value()} Empty:{e.value()} Net:{net}"; db.commit()
                db.close()
            d.accept()
            item.setText(item.text().replace("(double-click for scores)",f"[Net:{net:.2f}]"))
            QMessageBox.information(self,"Saved",f"Net: {net:.2f}")
        sb.clicked.connect(save); d.exec()
    def _exam_scores(self, item, data):
        db=get_session()
        subs=db.query(Subject).filter_by(user_id=self.user.id, exam_type=data["exam_type"]).all()
        db.close()
        if not subs: QMessageBox.information(self,"Info","No subjects for "+data["exam_type"]); return
        d=QDialog(self); d.setWindowTitle("Enter Scores - "+data["exam_type"])
        d.setMinimumSize(480,80+len(subs)*44)
        d.setStyleSheet("QDialog{background:#0f172a;}QLabel{color:#f1f5f9;}"
            "QSpinBox{background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:4px;}"
            "QPushButton{background:#3b82f6;color:white;border-radius:6px;padding:8px 16px;}")
        dl=QVBoxLayout(d); dl.setContentsMargins(20,20,20,20)
        hdr=QHBoxLayout()
        for h in ["Subject","Correct","Wrong","Empty","Net"]:
            lb=QLabel(h); lb.setStyleSheet("color:#64748b;font-weight:bold;"); hdr.addWidget(lb)
        dl.addLayout(hdr); rows=[]
        for sub in subs:
            row=QHBoxLayout(); nl=QLabel(sub.name)
            c=QSpinBox(); c.setRange(0,40); w=QSpinBox(); w.setRange(0,40)
            e=QSpinBox(); e.setRange(0,40); nl2=QLabel("0.00")
            nl2.setStyleSheet("color:#10b981;font-weight:bold;")
            def upd(_,c=c,w=w,nl=nl2):
                net=c.value()-w.value()*0.25; nl.setText(f"{net:.2f}")
                nl.setStyleSheet("color:"+("#10b981" if net>=0 else "#ef4444")+";font-weight:bold;")
            c.valueChanged.connect(upd); w.valueChanged.connect(upd)
            for ww in [nl,c,w,e,nl2]: row.addWidget(ww)
            dl.addLayout(row); rows.append((sub.id,c,w,e))
        sb=QPushButton("Save Scores"); dl.addWidget(sb)
        def save():
            s=get_session()
            for sid,c,w,e in rows:
                net=round(c.value()-w.value()*0.25,2)
                s.add(TrialResult(trial_exam_id=data["exam_id"],subject_id=sid,
                    correct=c.value(),wrong=w.value(),empty=e.value(),net=net))
            s.commit(); s.close(); d.accept()
            item.setText(item.text().replace("(double-click for scores)","(scores saved)"))
            QMessageBox.information(self,"Saved","Scores saved!")
        sb.clicked.connect(save); d.exec()
