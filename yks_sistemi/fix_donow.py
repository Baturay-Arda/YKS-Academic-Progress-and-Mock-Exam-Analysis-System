code = r"""
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QComboBox, QSpinBox, QLineEdit,
                                QFrame, QStackedWidget, QListWidget,
                                QListWidgetItem, QDialog, QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
from database import get_session, Subject, Topic, StudySession, TrialExam, TrialResult
from datetime import date
import sys
def play_alarm():
    try:
        if sys.platform == "win32":
            import winsound
            for _ in range(5):
                winsound.Beep(1000, 400)
    except Exception:
        pass
class DoItNowWidget(QWidget):
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
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._left_panel(), 3)
        layout.addWidget(self._right_panel(), 2)
    def _left_panel(self):
        frame = QFrame()
        frame.setStyleSheet("background:#0f172a;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(30, 30, 20, 30)
        layout.setSpacing(18)
        title = QLabel("Do It Now!")
        title.setFont(QFont("Arial", 26, QFont.Bold))
        title.setStyleSheet("color:#f1f5f9;")
        layout.addWidget(title)
        toggle = QHBoxLayout()
        self.study_btn = QPushButton("Study Session")
        self.exam_btn  = QPushButton("Trial Exam")
        self._on  = "background:#3b82f6;color:white;border-radius:8px;padding:10px 20px;font-size:14px;font-weight:bold;"
        self._off = "background:#1e293b;color:#64748b;border-radius:8px;padding:10px 20px;font-size:14px;"
        self.study_btn.setStyleSheet(self._on)
        self.exam_btn.setStyleSheet(self._off)
        self.study_btn.clicked.connect(lambda: self.switch_mode("study"))
        self.exam_btn.clicked.connect(lambda: self.switch_mode("exam"))
        toggle.addWidget(self.study_btn)
        toggle.addWidget(self.exam_btn)
        layout.addLayout(toggle)
        self.form_stack = QStackedWidget()
        self.form_stack.addWidget(self._study_form())
        self.form_stack.addWidget(self._exam_form())
        layout.addWidget(self.form_stack)
        tf = QFrame()
        tf.setStyleSheet("background:#1e293b;border-radius:16px;")
        tl = QVBoxLayout(tf)
        tl.setContentsMargins(20, 20, 20, 12)
        self.timer_lbl = QLabel("00:00")
        self.timer_lbl.setFont(QFont("Arial", 64, QFont.Bold))
        self.timer_lbl.setAlignment(Qt.AlignCenter)
        self.timer_lbl.setStyleSheet("color:#3b82f6;background:transparent;")
        tl.addWidget(self.timer_lbl)
        self.status_lbl = QLabel("Set duration and press Start")
        self.status_lbl.setAlignment(Qt.AlignCenter)
        self.status_lbl.setStyleSheet("color:#64748b;font-size:13px;background:transparent;")
        tl.addWidget(self.status_lbl)
        layout.addWidget(tf)
        btn_row = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.setStyleSheet("background:#10b981;color:white;border-radius:8px;padding:12px;font-size:16px;font-weight:bold;")
        self.start_btn.clicked.connect(self.start_session)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setStyleSheet("background:#ef4444;color:white;border-radius:8px;padding:12px;font-size:16px;font-weight:bold;")
        self.stop_btn.clicked.connect(self.stop_session)
        self.stop_btn.setVisible(False)
        btn_row.addWidget(self.start_btn)
        btn_row.addWidget(self.stop_btn)
        layout.addLayout(btn_row)
        layout.addStretch()
        return frame
    def _study_form(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        fs = "background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:8px;"
        ls = "color:#94a3b8;font-size:13px;"
        session = get_session()
        subjects = session.query(Subject).filter_by(user_id=self.user.id).all()
        session.close()
        self.study_subj_cb = QComboBox()
        self.study_subj_cb.setStyleSheet(fs)
        for s in subjects:
            self.study_subj_cb.addItem(s.name, s.id)
        self.study_topic_cb = QComboBox()
        self.study_topic_cb.setStyleSheet(fs)
        def upd_topics(idx):
            self.study_topic_cb.clear()
            if self.study_subj_cb.count() == 0:
                return
            sid = self.study_subj_cb.itemData(idx)
            sess = get_session()
            for t in sess.query(Topic).filter_by(subject_id=sid).all():
                self.study_topic_cb.addItem(t.name, t.id)
            sess.close()
        self.study_subj_cb.currentIndexChanged.connect(upd_topics)
        if subjects:
            upd_topics(0)
        self.study_dur = QSpinBox()
        self.study_dur.setRange(1, 300)
        self.study_dur.setValue(25)
        self.study_dur.setSuffix(" min")
        self.study_dur.setStyleSheet(fs)
        for ltext, wgt in [("Subject:", self.study_subj_cb),
                            ("Topic:",   self.study_topic_cb),
                            ("Duration:",self.study_dur)]:
            row = QHBoxLayout()
            l = QLabel(ltext); l.setStyleSheet(ls); l.setFixedWidth(80)
            row.addWidget(l); row.addWidget(wgt)
            layout.addLayout(row)
        return w
    def _exam_form(self):
        w = QWidget()
        w.setStyleSheet("background:transparent;")
        layout = QVBoxLayout(w)
        layout.setSpacing(10)
        fs = "background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:8px;"
        ls = "color:#94a3b8;font-size:13px;"
        self.exam_type_cb = QComboBox()
        self.exam_type_cb.setStyleSheet(fs)
        self.exam_type_cb.addItems(["TYT", "AYT", "YDT"])
        self.exam_name_inp = QLineEdit()
        self.exam_name_inp.setPlaceholderText("e.g. 345 Yayinlari")
        self.exam_name_inp.setStyleSheet(fs)
        self.exam_dur = QSpinBox()
        self.exam_dur.setRange(1, 300)
        self.exam_dur.setValue(135)
        self.exam_dur.setSuffix(" min")
        self.exam_dur.setStyleSheet(fs)
        def upd_dur(text):
            self.exam_dur.setValue({"TYT":135,"AYT":180,"YDT":120}.get(text,135))
        self.exam_type_cb.currentTextChanged.connect(upd_dur)
        for ltext, wgt in [("Type:",     self.exam_type_cb),
                            ("Name:",     self.exam_name_inp),
                            ("Duration:", self.exam_dur)]:
            row = QHBoxLayout()
            l = QLabel(ltext); l.setStyleSheet(ls); l.setFixedWidth(80)
            row.addWidget(l); row.addWidget(wgt)
            layout.addLayout(row)
        return w
    def _right_panel(self):
        frame = QFrame()
        frame.setStyleSheet("background:#020617;")
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 30, 30, 30)
        layout.setSpacing(10)
        title = QLabel("Completed")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color:#f1f5f9;")
        layout.addWidget(title)
        hint = QLabel("Double-click any item to enter scores")
        hint.setStyleSheet("color:#475569;font-size:12px;")
        layout.addWidget(hint)
        self.done_list = QListWidget()
        self.done_list.setStyleSheet(
            "QListWidget{background:#0f172a;color:#f1f5f9;border:none;border-radius:8px;}"
            "QListWidget::item{padding:14px;border-bottom:1px solid #1e293b;}"
            "QListWidget::item:hover{background:#1e293b;}"
            "QListWidget::item:selected{background:#1e3a5f;}")
        self.done_list.itemDoubleClicked.connect(self.open_score_dialog)
        layout.addWidget(self.done_list)
        return frame
    def switch_mode(self, mode):
        self.current_mode = mode
        self.study_btn.setStyleSheet(self._on  if mode=="study" else self._off)
        self.exam_btn.setStyleSheet( self._off if mode=="study" else self._on)
        self.form_stack.setCurrentIndex(0 if mode=="study" else 1)
    def start_session(self):
        if self.current_mode == "study":
            if not self.study_subj_cb.currentData():
                QMessageBox.warning(self,"Error","No subjects. Add one first.")
                return
            self.current_data = {
                "mode":"study",
                "subject_id":self.study_subj_cb.currentData(),
                "topic_id":  self.study_topic_cb.currentData(),
                "duration":  self.study_dur.value(),
                "label":     self.study_subj_cb.currentText()+" - "+self.study_topic_cb.currentText(),
            }
        else:
            name = self.exam_name_inp.text().strip() or self.exam_type_cb.currentText()
            self.current_data = {
                "mode":"exam",
                "exam_type":self.exam_type_cb.currentText(),
                "name":name,
                "duration":self.exam_dur.value(),
                "label":name+" ("+self.exam_type_cb.currentText()+")",
            }
        self.remaining_seconds = self.current_data["duration"] * 60
        self._refresh_display()
        self.timer.start(1000)
        self.start_btn.setVisible(False)
        self.stop_btn.setVisible(True)
        self.status_lbl.setText("In progress: "+self.current_data["label"])
    def tick(self):
        self.remaining_seconds -= 1
        self._refresh_display()
        if self.remaining_seconds <= 0:
            self.timer.stop()
            play_alarm()
            self._save_session(completed=True)
    def _refresh_display(self):
        m, s = divmod(self.remaining_seconds, 60)
        self.timer_lbl.setText(f"{m:02d}:{s:02d}")
        color = "#ef4444" if self.remaining_seconds<=300 else "#f59e0b" if self.remaining_seconds<=600 else "#3b82f6"
        self.timer_lbl.setStyleSheet(f"color:{color};background:transparent;")
    def stop_session(self):
        reply = QMessageBox.question(self,"Stop?",
            "Stop this session?\nIt will be marked as incomplete.",
            QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.timer.stop()
            self._save_session(completed=False)
    def _save_session(self, completed):
        self.start_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.timer_lbl.setText("00:00")
        self.timer_lbl.setStyleSheet("color:#3b82f6;background:transparent;")
        self.status_lbl.setText("Set duration and press Start")
        data = self.current_data
        if not data:
            return
        elapsed = max(1, data["duration"] - self.remaining_seconds // 60)
        note   = None if completed else "Incomplete"
        status = "DONE" if completed else "INCOMPLETE"
        color  = QColor("#10b981" if completed else "#ef4444")
        db = get_session()
        if data["mode"] == "study":
            obj = StudySession(
                user_id=self.user.id,
                subject_id=data["subject_id"],
                topic_id=data["topic_id"],
                date=date.today(),
                duration_minutes=elapsed,
                notes=note)
            db.add(obj)
            db.flush()
            session_id = obj.id
            db.commit()
            suffix = "  (double-click for scores)" if completed else "  [incomplete]"
            item = QListWidgetItem(status+"  |  Study: "+data["label"]+"  |  "+str(elapsed)+" min"+suffix)
            item.setData(Qt.UserRole, {
                "type": "study",
                "session_id": session_id,
                "label": data["label"],
                "completed": completed})
        else:
            exam = TrialExam(user_id=self.user.id, name=data["name"],
                             exam_type=data["exam_type"], date=date.today())
            db.add(exam)
            db.flush()
            eid = exam.id
            db.commit()
            suffix = "  (double-click for scores)" if completed else "  [incomplete]"
            item = QListWidgetItem(status+"  |  Exam: "+data["label"]+suffix)
            item.setData(Qt.UserRole, {
                "type": "exam",
                "exam_id": eid,
                "exam_type": data["exam_type"],
                "label": data["label"],
                "completed": completed})
        db.close()
        item.setForeground(color)
        self.done_list.insertItem(0, item)
        self.current_data = None
    def open_score_dialog(self, item):
        data = item.data(Qt.UserRole)
        if not data:
            return
        if not data.get("completed", True):
            QMessageBox.information(self, "Info", "This session was incomplete. No scores to enter.")
            return
        if data.get("type") == "study":
            self._study_score_dialog(item, data)
        elif data.get("type") == "exam":
            self._exam_score_dialog(item, data)
    def _study_score_dialog(self, item, data):
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter Test Scores")
        dialog.setFixedSize(340, 260)
        dialog.setStyleSheet(
            "QDialog{background:#0f172a;}QLabel{color:#f1f5f9;}"
            "QSpinBox{background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:6px;}"
            "QPushButton{background:#3b82f6;color:white;border-radius:6px;padding:8px 16px;}")
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)
        info = QLabel("Session: " + data.get("label", ""))
        info.setStyleSheet("color:#64748b;font-size:12px;")
        layout.addWidget(info)
        fs = "background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:6px;"
        ls = "color:#94a3b8;font-size:13px;"
        c_spin = QSpinBox(); c_spin.setRange(0, 200); c_spin.setStyleSheet(fs)
        w_spin = QSpinBox(); w_spin.setRange(0, 200); w_spin.setStyleSheet(fs)
        e_spin = QSpinBox(); e_spin.setRange(0, 200); e_spin.setStyleSheet(fs)
        for ltext, wgt in [("Correct:", c_spin), ("Wrong:", w_spin), ("Empty:", e_spin)]:
            row = QHBoxLayout()
            l = QLabel(ltext); l.setStyleSheet(ls); l.setFixedWidth(70)
            row.addWidget(l); row.addWidget(wgt)
            layout.addLayout(row)
        net_lbl = QLabel("Net: 0.00")
        net_lbl.setStyleSheet("color:#10b981;font-size:15px;font-weight:bold;")
        net_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(net_lbl)
        def upd(_):
            net = c_spin.value() - w_spin.value() * 0.25
            net_lbl.setText(f"Net: {net:.2f}")
            net_lbl.setStyleSheet("color:"+("#10b981" if net>=0 else "#ef4444")+";font-size:15px;font-weight:bold;")
        c_spin.valueChanged.connect(upd)
        w_spin.valueChanged.connect(upd)
        save_btn = QPushButton("Save Scores")
        layout.addWidget(save_btn)
        def save():
            net = round(c_spin.value() - w_spin.value() * 0.25, 2)
            note_text = f"Correct:{c_spin.value()} Wrong:{w_spin.value()} Empty:{e_spin.value()} Net:{net}"
            if data.get("session_id"):
                db = get_session()
                sess = db.query(StudySession).get(data["session_id"])
                if sess:
                    sess.notes = note_text
                    db.commit()
                db.close()
            dialog.accept()
            old = item.text()
            item.setText(old.replace("(double-click for scores)", f"[Net:{net:.2f}]"))
            QMessageBox.information(self, "Saved", f"Scores saved!  Net: {net:.2f}")
        save_btn.clicked.connect(save)
        dialog.exec()
    def _exam_score_dialog(self, item, data):
        db = get_session()
        subjects = db.query(Subject).filter_by(
            user_id=self.user.id, exam_type=data["exam_type"]).all()
        db.close()
        if not subjects:
            QMessageBox.information(self,"Info","No subjects for "+data["exam_type"]); return
        dialog = QDialog(self)
        dialog.setWindowTitle("Enter Scores - "+data["exam_type"])
        dialog.setMinimumSize(480, 80+len(subjects)*44)
        dialog.setStyleSheet(
            "QDialog{background:#0f172a;}QLabel{color:#f1f5f9;}"
            "QSpinBox{background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:4px;}"
            "QPushButton{background:#3b82f6;color:white;border-radius:6px;padding:8px 16px;}")
        dl = QVBoxLayout(dialog); dl.setContentsMargins(20,20,20,20)
        header = QHBoxLayout()
        for h in ["Subject","Correct","Wrong","Empty","Net"]:
            l=QLabel(h); l.setStyleSheet("color:#64748b;font-weight:bold;"); header.addWidget(l)
        dl.addLayout(header)
        rows=[]
        for subj in subjects:
            row=QHBoxLayout()
            nl=QLabel(subj.name)
            c=QSpinBox(); c.setRange(0,40)
            w=QSpinBox(); w.setRange(0,40)
            e=QSpinBox(); e.setRange(0,40)
            nl2=QLabel("0.00"); nl2.setStyleSheet("color:#10b981;font-weight:bold;")
            def upd(_,c=c,w=w,nl=nl2):
                net=c.value()-w.value()*0.25
                nl.setText(f"{net:.2f}")
                nl.setStyleSheet("color:"+("#10b981" if net>=0 else "#ef4444")+";font-weight:bold;")
            c.valueChanged.connect(upd); w.valueChanged.connect(upd)
            for ww in [nl,c,w,e,nl2]: row.addWidget(ww)
            dl.addLayout(row); rows.append((subj.id,c,w,e))
        save_btn=QPushButton("Save Scores"); dl.addWidget(save_btn)
        def save():
            s=get_session()
            for sid,c,w,e in rows:
                net=round(c.value()-w.value()*0.25,2)
                s.add(TrialResult(trial_exam_id=data["exam_id"],subject_id=sid,
                    correct=c.value(),wrong=w.value(),empty=e.value(),net=net))
            s.commit(); s.close(); dialog.accept()
            item.setText(item.text().replace("(double-click for scores)","(scores saved)"))
            QMessageBox.information(self,"Saved","Scores saved!")
        save_btn.clicked.connect(save)
        dialog.exec()
"""
with open("ui/do_it_now_widget.py", "w", encoding="utf-8") as f:
    f.write(code.strip())
print("Done! Run: python main.py")