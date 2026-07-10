from fastapi import APIRouter
from fastapi import HTTPException
from datetime import datetime

from database import db
from email_services import (
    send_emergency_contact_email
)

router = APIRouter()


@router.post(
    "/doctor/session/{session_id}/confirm-critical"
)
async def confirm_critical(
        session_id: str
):

    session = await db.analysis_results.find_one(
        {
            "session_id": session_id
        }
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    if session.get(
            "risk_level"
    ) != "CRITICAL":
        raise HTTPException(
            status_code=400,
            detail="Session is not critical"
        )

    if not session.get(
            "doctor_reviewed",
            False
    ):
        raise HTTPException(
            status_code=400,
            detail="Doctor review required"
        )

    if session.get(
            "emergency_notified",
            False
    ):
        raise HTTPException(
            status_code=400,
            detail="Emergency contacts already notified"
        )

    contacts = await db.emergency_contacts.find(
        {
            "user_id":
                session["patient_id"]
        }
    ).to_list(20)

    patient = await db.users.find_one(
        {
            "user_id":
                session["patient_id"]
        }
    )

    patient_name = (
        patient["name"]
        if patient
        else session["patient_id"]
    )

    # for contact in contacts:

    #     if not contact.get("email"):
    #         continue

    #     await send_emergency_contact_email(
    #         to_email=
    #             contact["email"],

    #         contact_name=
    #             contact["name"],

    #         patient_name=
    #             patient_name,
    #     )
    if not contacts:

        raise HTTPException(
            status_code=404,
            detail="No emergency contacts found for this patient"
        )
    for contact in contacts:

        if not contact.get("email"):
            continue

        try:

            await send_emergency_contact_email(
                to_email=contact["email"],
                contact_name=contact["name"],
                patient_name=patient_name,
            )

        except Exception as e:

            print(
                f"Failed to send emergency email "
                f"to {contact['email']}: {e}"
            )

    await db.analysis_results.update_one(
        {
            "session_id":
                session_id
        },
        {
            "$set": {

                "critical_confirmed":
                    True,

                "emergency_notified":
                    True,

                "emergency_notified_at":
                    datetime.utcnow()
            }
        }
    )

    return {
        "message":
            "Emergency contacts notified successfully",
             "patient":
        patient_name,

    "contacts_notified":
        len(
            [
                c
                for c in contacts
                if c.get("email")
            ]
        ),

    "session_id":
        session_id,
    }