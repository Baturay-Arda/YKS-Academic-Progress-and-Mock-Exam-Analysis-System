import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from database import get_session, TrialExam, Subject
class NetProgressChart(FigureCanvasQTAgg):
    def __init__(self, user):
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.fig.patch.set_facecolor("#1e293b")
        self.ax.set_facecolor("#1e293b")
        super().__init__(self.fig)
        self.user = user
        self.plot()
    def plot(self):
        session = get_session()
        exams = session.query(TrialExam)\
            .filter_by(user_id=self.user.id)\
            .order_by(TrialExam.date).all()
        subjects = session.query(Subject)\
            .filter_by(user_id=self.user.id).all()
        colors = ["#3b82f6", "#ef4444", "#10b981",
                  "#f59e0b", "#8b5cf6", "#06b6d4"]
        for idx, subj in enumerate(subjects[:6]):
            nets = []
            labels = []
            for exam in exams:
                result = next(
                    (r for r in exam.results if r.subject_id == subj.id), None)
                if result:
                    nets.append(result.net)
                    labels.append(exam.name)
            if nets:
                self.ax.plot(labels, nets, marker="o",
                             label=subj.name,
                             color=colors[idx % len(colors)],
                             linewidth=2)
        self.ax.set_title("Net Gelisimi", color="#f1f5f9", fontsize=13)
        self.ax.tick_params(colors="#94a3b8")
        self.ax.legend(facecolor="#0f172a", labelcolor="#f1f5f9")
        self.fig.tight_layout()
        session.close()