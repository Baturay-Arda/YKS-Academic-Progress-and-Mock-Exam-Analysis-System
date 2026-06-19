from database import get_session, StudySession, TrialExam, TrialResult, Subject, Goal
def generate_pdf(user, filepath):
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        raise ImportError("reportlab not installed. Run: pip install reportlab")
    db = get_session()
    sessions = db.query(StudySession).filter_by(user_id=user.id).order_by(StudySession.date).all()
    sessions = [s for s in sessions if not (s.notes and "Incomplete" in s.notes)]
    exams = db.query(TrialExam).filter_by(user_id=user.id).order_by(TrialExam.date).all()
    try: exams = [e for e in exams if not (getattr(e,'notes',None) and "Incomplete" in e.notes)]
    except Exception: pass
    subjects = db.query(Subject).filter_by(user_id=user.id).all()
    subj_map = {s.id: s.name for s in subjects}
    exam_results = {}
    for e in exams:
        exam_results[e.id] = db.query(TrialResult).filter_by(trial_exam_id=e.id).all()
    exam_data = [{"date":str(e.date),"name":e.name,"exam_type":e.exam_type,
                  "total":sum(r.net for r in exam_results.get(e.id,[]))} for e in exams]
    sess_data = [{"date":str(s.date),"subject":subj_map.get(s.subject_id,"?"),
                  "duration":s.duration_minutes} for s in sessions]
    db.close()
    doc = SimpleDocTemplate(filepath, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle("title", fontSize=20, fontName="Helvetica-Bold", spaceAfter=6, alignment=TA_CENTER)
    h2_style = ParagraphStyle("h2", fontSize=14, fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=10)
    body_style = ParagraphStyle("body", fontSize=10, spaceAfter=3)
    story.append(Paragraph(f"YKS Tracker - {user.username}", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Study Sessions", h2_style))
    if sess_data:
        data = [["Date","Subject","Duration"]]
        for s in sess_data: data.append([s["date"], s["subject"], f"{s['duration']} min"])
        tbl = Table(data, repeatRows=1)
        tbl.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),9),("GRID",(0,0),(-1,-1),0.3,colors.grey),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(tbl)
    else:
        story.append(Paragraph("No completed study sessions.", body_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Trial Exams", h2_style))
    if exam_data:
        data2 = [["Date","Name","Type","Total Net"]]
        for e in exam_data: data2.append([e["date"], e["name"], e["exam_type"], f"{e['total']:.2f}"])
        tbl2 = Table(data2, repeatRows=1)
        tbl2.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1e3a8a")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
            ("FONTSIZE",(0,0),(-1,-1),9),("GRID",(0,0),(-1,-1),0.3,colors.grey),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
        story.append(tbl2)
    else:
        story.append(Paragraph("No completed trial exams.", body_style))
    doc.build(story)
