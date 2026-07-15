from dotenv import load_dotenv
import os

load_dotenv()


EMAIL_ADDRESS = os.getenv(
    "EMAIL_ADDRESS"
)

EMAIL_PASSWORD = os.getenv(
    "EMAIL_PASSWORD"
)

import smtplib

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# async def send_email(
#         to_email: str,
#         subject: str,
#         body: str
# ):

#     msg = MIMEMultipart()

#     msg["From"] = EMAIL_ADDRESS
#     msg["To"] = to_email
#     msg["Subject"] = subject

#     msg.attach(
#         MIMEText(body, "plain")
#     )

#     server = smtplib.SMTP(
#         "smtp.gmail.com",
#         587
#     )

#     server.starttls()

#     server.login(
#         EMAIL_ADDRESS,
#         EMAIL_PASSWORD
#     )

#     server.send_message(msg)

#     server.quit()

async def send_email(
        to_email: str,
        subject: str,
        body: str
):

    msg = MIMEMultipart()

    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(
        MIMEText(body, "plain")
    )

    server = smtplib.SMTP(
        "smtp.gmail.com",
        587
    )

    server.starttls()

    server.login(
        EMAIL_ADDRESS,
        EMAIL_PASSWORD
    )

    server.send_message(msg)

    server.quit()



async def send_verification_email(
        to_email: str,
        doctor_name: str
):

    subject = "Doctor Verification Approved"

    body = f"""
Hello Dr. {doctor_name},

Your MindSense doctor account has been verified successfully.

You can now login to the platform.

Regards,
MindSense Team
"""

    await send_email(
        to_email,
        subject,
        body
    )


async def send_rejection_email(
        to_email: str,
        doctor_name: str
):

    subject = "Doctor Verification Rejected"

    body = f"""
Hello Dr. {doctor_name},

Your verification request was rejected.

Please contact admin for more details.

Regards,
MindSense Team
"""

    await send_email(
        to_email,
        subject,
        body
    )
async def send_doctor_added_email(
    to_email: str,
    doctor_name: str,
    patient_name: str
):

    subject = "New Patient Added"

    body = f"""
Hello Dr. {doctor_name},

{patient_name} has added you as their doctor on MindSense.

You now have access to all of their previous and future session analyses.

Please login to your dashboard to review their history.

Regards,
MindSense Team
"""

    await send_email(
        to_email,
        subject,
        body
    )
async def send_new_session_email(
    to_email: str,
    doctor_name: str,
    patient_name: str,
    analysis_type: str
):

    subject = "New Patient Session Submitted"

    body = f"""
Hello Dr. {doctor_name},

{patient_name} has submitted a new {analysis_type} session.

You can now review the report from your dashboard.

Regards,
MindSense Team
"""

    await send_email(
        to_email,
        subject,
        body
    )
async def send_emergency_contact_email(
        to_email: str,
        contact_name: str,
        patient_name: str,
):

    subject = (
        f"Urgent Mental Health Alert "
        f"for {patient_name}"
    )

    body = f"""
Dear {contact_name},

A clinician has reviewed the recent
mental health assessment for
{patient_name} and identified
a situation requiring urgent attention.

Recommended actions:

• Stay in contact with the patient.
• Avoid leaving the patient alone.
• Encourage professional support.
• If immediate danger exists,
  contact emergency services.

This notification was generated
after review and confirmation
by a doctor.

Regards,
Mindful Platform
"""

    await send_email(
        to_email=to_email,
        subject=subject,
        body=body,
    )


async def send_appointment_confirmation_to_patient(
    to_email: str,
    patient_name: str,
    doctor_name: str,
    appointment_date: str,
    appointment_time: str,
    reason: str
):

    subject = "Appointment Confirmation"

    body = f"""
Hello {patient_name},

Your appointment has been successfully booked.

Appointment Details:
• Doctor: Dr. {doctor_name}
• Date: {appointment_date}
• Time: {appointment_time}
• Reason: {reason}

Please arrive 5-10 minutes before the scheduled time.

If you need to reschedule or cancel, please contact us as soon as possible.

Regards,
MindSense Team
"""

    await send_email(
        to_email,
        subject,
        body
    )


async def send_appointment_notification_to_doctor(
    to_email: str,
    doctor_name: str,
    patient_name: str,
    appointment_date: str,
    appointment_time: str,
    reason: str
):

    subject = "New Appointment Scheduled"

    body = f"""
Hello Dr. {doctor_name},

A new appointment has been scheduled with your patient.

Appointment Details:
• Patient: {patient_name}
• Date: {appointment_date}
• Time: {appointment_time}
• Reason: {reason}

Please ensure you review the patient's history before the appointment.

Regards,
MindSense Team
"""

    await send_email(
        to_email,
        subject,
        body
    )
async def send_high_risk_alert_email(
    to_email: str,
    doctor_name: str,
    patient_name: str,
    risk_level: str,
):

    subject = f"{risk_level} Depression Alert"

    body = f"""
Hello Dr. {doctor_name},

A {risk_level} depression risk has been detected for your patient.

Please log in to MindSense and review the patient's latest analysis as soon as possible.

Regards,
MindSense Team
"""

    await send_email(
        to_email,
        subject,
        body,
    )