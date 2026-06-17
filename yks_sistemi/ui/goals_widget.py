from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QDialog, QFormLayout, QDoubleSpinBox,
                                QComboBox, QDateEdit, QScrollArea, QFrame, QMessageBox)
from PySide6.QtCore import QDate, Qt
from PySide6.QtGui import QFont
from database import get_session, Goal, Subject
class GoalsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet("background:#0f172a;")
        l = QVBoxLayout(self); l.setContentsMargins(30,30,30,30); l.setSpacing(16)
        hdr = QHBoxLayout()
        title = QLabel("Goals"); title.setFont(QFont("Arial",22,QFont.Bold))
        title.setStyleSheet("color:#f1f5f9;"); hdr.addWidget(title); hdr.addStretch()
        add_btn = QPushButton("+ Add Goal")
        add_btn.setStyleSheet("background:#3b82f6;color:white;border-radius:6px;padding:8px 16px;")
        add_btn.clicked.connect(self.add_goal); hdr.addWidget(add_btn)
        l.addLayout(hdr)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{border:none;background:transparent;}")
        self.container = QWidget(); self.container.setStyleSheet("background:transparent;")
        self.list_l = QVBoxLayout(self.container); self.list_l.setSpacing(10); self.list_l.setAlignment(Qt.AlignTop)
        scroll.setWidget(self.container); l.addWidget(scroll)
        self.load()
    def load(self):
        while self.list_l.count():
            item = self.list_l.takeAt(0)
            if item and item.widget(): item.widget().deleteLater()
        db = get_session()
        goals = db.query(Goal).filter_by(user_id=self.user.id).all()
        subj_map = {s.id: s.name for s in db.query(Subject).filter_by(user_id=self.user.id).all()}
        goal_data = [{"id":g.id,"subject_id":g.subject_id,"target_net":g.target_net,
                      "deadline":g.deadline,"achieved":g.achieved} for g in goals]
        db.close()
        for g in goal_data: self.list_l.addWidget(self._goal_card(g, subj_map))
        if not goal_data:
            lbl = QLabel("No goals yet. Add one!"); lbl.setStyleSheet("color:#64748b;font-size:14px;")
            self.list_l.addWidget(lbl)
        self.list_l.addStretch()
    def _goal_card(self, g, subj_map):
        color = "#10b981" if g["achieved"] else "#3b82f6"
        card = QFrame()
        card.setStyleSheet(f"background:#1e293b;border-radius:12px;border-left:4px solid {color};")
        l = QHBoxLayout(card); l.setContentsMargins(20,14,20,14)
        name = QLabel(subj_map.get(g["subject_id"],"?")); name.setStyleSheet("color:#f1f5f9;font-weight:bold;font-size:14px;background:transparent;")
        net = QLabel(f"Target Net: {g['target_net']:.1f}"); net.setStyleSheet("color:#94a3b8;font-size:13px;background:transparent;")
        dl = QLabel(f"Deadline: {g['deadline']}"); dl.setStyleSheet("color:#64748b;font-size:12px;background:transparent;")
        status = QLabel("Achieved" if g["achieved"] else "In Progress")
        status.setStyleSheet(f"color:{color};font-size:12px;font-weight:bold;background:transparent;")
        del_btn = QPushButton("Delete")
        del_btn.setStyleSheet("background:#7f1d1d;color:#fca5a5;border-radius:4px;padding:4px 10px;font-size:11px;")
        del_btn.clicked.connect(lambda _, gid=g["id"]: self.delete_goal(gid))
        l.addWidget(name, 1); l.addWidget(net); l.addWidget(dl); l.addWidget(status); l.addWidget(del_btn)
        return card
    def add_goal(self):
        db = get_session()
        subjects = db.query(Subject).filter_by(user_id=self.user.id).all(); db.close()
        if not subjects: QMessageBox.warning(self,"Error","Add subjects first."); return
        d = QDialog(self); d.setWindowTitle("Add Goal"); d.setFixedSize(300,220)
        d.setStyleSheet("QDialog{background:#0f172a;}QLabel{color:#f1f5f9;}"
            "QDoubleSpinBox,QComboBox,QDateEdit{background:#1e293b;color:#f1f5f9;border:1px solid #334155;border-radius:6px;padding:8px;}"
            "QPushButton{background:#3b82f6;color:white;border-radius:6px;padding:8px;}")
        form = QFormLayout(d)
        sc = QComboBox()
        for s in subjects: sc.addItem(s.name, s.id)
        ns = QDoubleSpinBox(); ns.setRange(0,200); ns.setValue(50)
        di = QDateEdit(QDate.currentDate().addMonths(1)); di.setCalendarPopup(True)
        btn = QPushButton("Save")
        form.addRow("Subject:",sc); form.addRow("Target Net:",ns); form.addRow("Deadline:",di); form.addRow(btn)
        def save():
            db2 = get_session()
            db2.add(Goal(user_id=self.user.id, subject_id=sc.currentData(),
                         target_net=ns.value(), deadline=di.date().toPython()))
            db2.commit(); db2.close(); d.accept(); self.load()
        btn.clicked.connect(save); d.exec()
    def delete_goal(self, gid):
        if QMessageBox.question(self,"Delete?","Delete this goal?",
                                QMessageBox.Yes|QMessageBox.No) == QMessageBox.Yes:
            db = get_session(); g = db.query(Goal).get(gid)
            if g: db.delete(g); db.commit()
            db.close(); self.load()
