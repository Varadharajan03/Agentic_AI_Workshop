# agents/notifier.py

import smtplib
from email.mime.text import MIMEText
from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId

# ✅ SMTP Configuration
SMTP_EMAIL = "suryaraina0987@gmail.com"
SMTP_PASSWORD = "mlva ayly nlpa qsow"
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(to_email: str, subject: str, html_body: str):
    msg = MIMEText(html_body, "html")
    msg["Subject"] = subject
    msg["From"] = SMTP_EMAIL
    msg["To"] = to_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_EMAIL, SMTP_PASSWORD)
        smtp.send_message(msg)

def format_email(student, eligibility, gaps, training):
    deadline = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    gap_text = ", ".join(gaps.get("gaps", [])) if gaps else "None"
    training_plan = training.get("training_plan", "No training plan available.")

    return f"""
    <h3>Hello {student['name']},</h3>
    <p><strong>Status:</strong> {eligibility.get('status').capitalize()}</p>
    <p><strong>Gaps:</strong> {gap_text}</p>
    <p><strong>Training Plan:</strong></p>
    <div style=\"background:#f4f4f4;padding:10px;border-radius:5px;\">
        <pre>{training_plan}</pre>
    </div>
    <p><strong>Deadline:</strong> {deadline}</p>
    <p>Regards,<br>Placement Team</p>
    """

def run(state):
    print("📬 Notifier started...")
    summary = []
    client = MongoClient("mongodb://localhost:27017/")
    db = client.eligibility_tracker
    students = {s["student_id"]: s for s in db.students.find({}, {"_id": 0})}

    for item in state.eligibility_results:
        student_id = item["student_id"]
        student = students.get(student_id)
        if not student:
            print(f"⚠️ Student not found: {student_id}")
            continue

        gaps = next((g for g in state.gap_analysis if g["student_id"] == student_id), {})
        training = next((t for t in state.training_recommendations if t["student_id"] == student_id), {})

        # 🔔 Compose structured notification
        notification = {
            "student_id": student_id,
            "status": item["status"],
            "email": student["email"],
            "message": "See training plan." if item["status"] == "eligible" else "Improve profile.",
            "gaps": gaps.get("gaps", []),
            "training": training.get("training_plan", ""),
            "deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "sent_at": datetime.now().isoformat(),
            "email_status": "pending"
        }

        try:
            html_body = format_email(student, item, gaps, training)
            send_email(student["email"], "📬 Eligibility & Training Plan Update", html_body)
            print(f"✅ Email sent to {student['email']}")
            notification["email_status"] = "sent"
        except Exception as e:
            print(f"❌ Email failed for {student['email']}: {e}")
            notification["message"] = f"Email failed: {str(e)}"
            notification["email_status"] = "failed"

        try:
            db.notifications.insert_one(notification)
        except Exception as mongo_error:
            print(f"⚠️ Mongo log failed for {student_id}: {mongo_error}")

        summary.append(notification)

    state.notification_summary = summary
    client.close()
    return state
