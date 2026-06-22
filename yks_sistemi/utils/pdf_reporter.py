from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from database import get_session, TrialExam
from datetime import datetime
def generate_report(user, filepath="yks_rapor.pdf"):
    doc = SimpleDocTemplate(filepath, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    story.append(Paragraph("YKS Raporu", styles["Title"]))
    story.append(Paragraph(
        "Kullanici: " + user.username, styles["Normal"]))
    story.append(Paragraph(
        "Tarih: " + datetime.now().strftime("%d/%m/%Y"), styles["Normal"]))
    story.append(Spacer(1, 0.5*cm))
    session = get_session()
    exams = session.query(TrialExam)\
        .filter_by(user_id=user.id).all()
    for exam in exams:
        total = sum(r.net for r in exam.results)
        story.append(Paragraph(
            exam.name + " - " + exam.exam_type +
            " - Net: " + f"{total:.2f}", styles["Normal"]))
    session.close()
    doc.build(story)
    return filepath