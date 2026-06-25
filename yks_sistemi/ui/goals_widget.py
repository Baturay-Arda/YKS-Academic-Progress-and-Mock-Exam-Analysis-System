from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                QPushButton, QDialog, QFormLayout, QComboBox,
                                QDoubleSpinBox, QDateEdit, QTableWidget,
                                QTableWidgetItem, QMessageBox)
from PySide6.QtCore import QDate
from PySide6.QtGui import QFont
from database import get_session, Goal, Subject
class GoalsWidget(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setStyleSheet("background:#0f172a;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(16)
        header = QHBoxLayout()
        title = QLabel("Goals")
        title.setFont(QFont("Arial", 22, QFont.Bold))
        title.setStyleSheet("color:#f1f5f9;")
        header.addWidget(title)
        header.addStretch()
        add_btn = QPushButton("+ Add Goal")
        add_btn.setStyleSheet(
            "background:#f59e0b;color:white;border-radius:6px;padding:8px 16px;")
        add_btn.clicked.connect(self.add_goal)
        header.addWidget(add_btn)
        layout.addLayout(header)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["Subject", "Target Net", "Deadline", "Status", "Action"])
        self.table.setStyleSheet(
            "QTableWidget{background:#1e293b;color:#f1f5f9;border:none;}"
            "QHeaderView::section{background:#0f172a;color:#64748b;"
            "padding:8px;border:none;}")
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.load()
    def load(self):
        session = get_session()
        goals = session.query(Goal).filter_by(user_id=self.user.id).all()
        self.table.setRowCount(len(goals))
        for i, g in enumerate(goals):
            subj_name = g.subject.name if g.subject else "-"
            status = "Achieved" if g.achieved else "Active"
            self.table.setItem(i, 0, QTableWidgetItem(subj_name))
            self.table.setItem(i, 1, QTableWidgetItem(f"{g.target_net:.1f}"))
            self.table.setItem(i, 2, QTableWidgetItem(str(g.deadline)))
            item = QTableWidgetItem(status)
            item.setForeground(
                __import__("PySide6.QtGui", fromlist=["QColor"]).QColor(
                    "#10b981" if g.achieved else "#f59e0b"))
            self.table.setItem(i, 3, item)
            del_btn = QPushButton("Delete")
            del_btn.setStyleSheet(
                "background:#ef4444;color:white;border-radius:4px;padding:4px 8px;")
            del_btn.clicked.connect(lambda _, gid=g.id: self.delete(gid))
            self.table.setCellWidget(i, 4, del_btn)
        self.table.resizeColumnsToContents()
        session.close()
    def add_goal(self):
        session = get_session()
        subjects = session.query(Subject)\
            .filter_by(user_id=self.user.id).all()
        session.close()
        if not subjects:
            QMessageBox.information(self, "Info",
                "Add a subject first.")
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Goal")
        dialog.setFixedSize(320, 220)
        dialog.setStyleSheet(
            "QDialog{background:#0f172a;}QLabel{color:#f1f5f9;}"
            "QComboBox,QDoubleSpinBox,QDateEdit{"
            "background:#1e293b;color:#f1f5f9;"
            "border:1px solid #334155;border-radius:6px;padding:6px;}"
            "QPushButton{background:#f59e0b;color:white;"
            "border-radius:6px;padding:8px;}")
        form = QFormLayout(dialog)
        subj_cb = QComboBox()
        for s in subjects:
            subj_cb.addItem(s.name, s.id)
        net_spin = QDoubleSpinBox()
        net_spin.setRange(0, 160)
        net_spin.setDecimals(1)
        net_spin.setValue(20.0)
        date_inp = QDateEdit(QDate.currentDate().addMonths(1))
        date_inp.setCalendarPopup(True)
        form.addRow("Subject:", subj_cb)
        form.addRow("Target Net:", net_spin)
        form.addRow("Deadline:", date_inp)
        btn = QPushButton("Save")
        form.addRow(btn)
        def save():
            s = get_session()
            goal = Goal(user_id=self.user.id,
                        subject_id=subj_cb.currentData(),
                        target_net=net_spin.value(),
                        deadline=date_inp.date().toPython())
            s.add(goal)
            s.commit()
            s.close()
            dialog.accept()
            self.load()
        btn.clicked.connect(save)
        dialog.exec()
    def delete(self, goal_id):
        s = get_session()
        g = s.query(Goal).get(goal_id)
        if g:
            s.delete(g)
            s.commit()
        s.close()
        self.load()