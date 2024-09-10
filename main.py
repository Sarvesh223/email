# File: main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

class EmailData(BaseModel):
    doctorEmail: str
    patientEmail: str
    appointmentDate: str
    doctorName: str
    patientName: str
    hospitalName: str

@app.post("/send-emails")
async def send_emails(email_data: EmailData):
    try:
        # Email configuration
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")

        # Create message for doctor
        doctor_message = MIMEMultipart("alternative")
        doctor_message["Subject"] = "New Appointment Scheduled"
        doctor_message["From"] = sender_email
        doctor_message["To"] = email_data.doctorEmail

        doctor_text = f"""
        Dear Dr. {email_data.doctorName},

        A new appointment has been scheduled with the following details:

        Patient: {email_data.patientName}
        Date: {email_data.appointmentDate}

        Please ensure you're available at the scheduled time.

        Best regards,
        Your Hospital Team
        """

        doctor_html = f"""
        <html>
        <body>
            <h1>New Appointment Scheduled</h1>
            <p>Dear Dr. {email_data.doctorName},</p>
            <p>A new appointment has been scheduled with the following details:</p>
            <ul>
                <li><strong>Patient:</strong> {email_data.patientName}</li>
                <li><strong>Date:</strong> {email_data.appointmentDate}</li>
            </ul>
            <p>Please ensure you're available at the scheduled time.</p>
            <p>Best regards,<br>Your Hospital Team</p>
        </body>
        </html>
        """

        doctor_part1 = MIMEText(doctor_text, "plain")
        doctor_part2 = MIMEText(doctor_html, "html")
        doctor_message.attach(doctor_part1)
        doctor_message.attach(doctor_part2)

        # Create message for patient
        patient_message = MIMEMultipart("alternative")
        patient_message["Subject"] = "Appointment Confirmation"
        patient_message["From"] = sender_email
        patient_message["To"] = email_data.patientEmail

        patient_text = f"""
        Dear {email_data.patientName},

        Your appointment has been successfully scheduled with the following details:

        Doctor: Dr. {email_data.doctorName}
        Date: {email_data.appointmentDate}
        Location: {email_data.hospitalName}

        If you need to reschedule or cancel, please contact us at least 24 hours in advance.

        Best regards,
        Your Hospital Team
        """

        patient_html = f"""
        <html>
        <body>
            <h1>Appointment Confirmation</h1>
            <p>Dear {email_data.patientName},</p>
            <p>Your appointment has been successfully scheduled with the following details:</p>
            <ul>
                <li><strong>Doctor:</strong> Dr. {email_data.doctorName}</li>
                <li><strong>Date:</strong> {email_data.appointmentDate}</li>
                <li><strong>Location:</strong> {email_data.hospitalName}</li>
            </ul>
            <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
            <p>Best regards,<br>Your Hospital Team</p>
        </body>
        </html>
        """

        patient_part1 = MIMEText(patient_text, "plain")
        patient_part2 = MIMEText(patient_html, "html")
        patient_message.attach(patient_part1)
        patient_message.attach(patient_part2)

        # Send emails
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(doctor_message)
            server.send_message(patient_message)

        return {"message": "Emails sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
