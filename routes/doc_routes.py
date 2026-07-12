# routes/doc_routes.py
# ============================================================
# GET VERIFIED DOCTORS API
# ============================================================

from fastapi import APIRouter
from database import db
from fastapi import HTTPException
from datetime import datetime
from bson import ObjectId
from email_services import (
    send_emergency_contact_email
)

router = APIRouter()



@router.get("/doctors")
async def get_doctors():

    doctors = []

    cursor = db.users.find({

        "role": "doctor",

        "is_verified": True,

        "is_active": True
    })

    async for user in cursor:

        doctor_profile = await db.doctor_profiles.find_one({

            "user_id":
                user["user_id"]
        })

        doctors.append({

            "user_id":
                user["user_id"],

            "name":
                user["name"],

            "email":
                user["email"],

            "specialization":

                doctor_profile.get(
                    "specialization",
                    ""
                ) if doctor_profile else "",

            "hospital_name":

                doctor_profile.get(
                    "hospital_name",
                    ""
                ) if doctor_profile else "",

            "years_experience":

                doctor_profile.get(
                    "years_experience",
                    0
                ) if doctor_profile else 0,
                
            "rating": doctor_profile.get("rating", 5.0) if doctor_profile else 5.0
        })

    return {

        "doctors":
            doctors
    }

@router.post("/doctor/note")
async def add_doctor_note(data: dict):

    note = {

        "session_id":
            data.get("session_id"),

        "patient_id":
            data.get("patient_id"),

        "doctor_id":
            data.get("doctor_id"),

        "doctor_name":
            data.get("doctor_name"),

        "note":
            data.get("note"),

        "private_note":
            True,

        "created_at":
            datetime.utcnow(),

        "updated_at":
            None
    }

    result = await db.doctor_notes.insert_one(note)

    return {

        "message":
            "Note added successfully",

        "note_id":
            str(result.inserted_id)
    }

@router.get("/doctor/notes/{session_id}")
async def get_notes(session_id: str):

    notes = []

    cursor = db.doctor_notes.find({

        "session_id": session_id
    })

    async for note in cursor:

        notes.append({

            "id":
                str(note["_id"]),

            "doctor_name":
                note["doctor_name"],

            "note":
                note["note"],

            "created_at":
                str(note["created_at"])
        })

    return {

        "notes": notes
    }



# @router.get("/doctor/patients/{doctor_id}")
# async def get_connected_patients(doctor_id: str):

#     connections = await db.doctor_patient_access.find({
#         "doctor_id": doctor_id,
#         "active": True
#     }).to_list(100)

#     patients = []

#     for connection in connections:

#         user = await db.users.find_one({
#             "user_id": connection["patient_id"]
#         })

#         profile = await db.patient_profiles.find_one({
#             "user_id": connection["patient_id"]
#         })

#         patients.append({
#             "patient_id": connection["patient_id"],

#             "name":
#                 user.get("name", "")
#                 if user else "",

#             "email":
#                 user.get("email", "")
#                 if user else "",

#             "age":
#                 profile.get("age", None)
#                 if profile else None,

#             "gender":
#                 profile.get("gender", "")
#                 if profile else "",

#             "primary_concerns":
#                 profile.get("primary_concerns", [])
#                 if profile else [],

#             "consent_given":
#                 profile.get("consent_given", False)
#                 if profile else False,

#             "connected_at":
#                 connection.get("connected_at")
#         })

#     return {
#         "patients": patients,
#         "count": len(patients)
#     }
@router.get("/doctor/patients/{doctor_id}")
async def get_connected_patients(doctor_id: str):

    connections = await db.doctor_patient_access.find({
        "doctor_id": doctor_id,
        "active": True
    }).to_list(100)

    patients = []

    for connection in connections:

        patient_id = connection["patient_id"]

        user = await db.users.find_one({
            "user_id": patient_id
        })

        profile = await db.patient_profiles.find_one({
            "user_id": patient_id
        })

        latest_result = await db.analysis_results.find(
            {
                "patient_id": patient_id
            }
        ).sort(
            "created_at",
            -1
        ).limit(
            1
        ).to_list(
            1
        )

        session_count = await db.analysis_results.count_documents({
            "patient_id": patient_id
        })
        last_session_display = "No sessions"
        prediction = "Unknown"
        confidence = 0.0
        risk_level = "LOW"

        if latest_result:
            created_at = latest_result[0].get("created_at")
            risk_level = latest_result[0].get(
    "risk_level",
    "LOW"
)

            if created_at:
                last_session_display = created_at.strftime(
                    "%d %b %Y"
                )

            # fusion = latest_result[0].get(
            #     "fusion_prediction",
            #     {}
            # )

            # prediction = fusion.get(
            #     "prediction",
            #     "Unknown"
            # )

            # confidence = fusion.get(
            #     "confidence",
            #     0.0
            # )
            prediction_data = (
            latest_result[0].get("fusion_prediction")
            or latest_result[0].get("depression")
            or {}
        )

        prediction = prediction_data.get(
            "prediction",
            prediction_data.get("label", "Unknown")
        )

        confidence = float(
            prediction_data.get(
                "confidence",
                0.0
            )
        )

        risk_level = latest_result[0].get(
            "risk_level",
            "LOW"
        )

        patients.append({
            "patient_id": patient_id,
            "name": user.get("name", "") if user else "",
            "email": user.get("email", "") if user else "",
            "age": profile.get("age") if profile else None,
            "gender": profile.get("gender") if profile else "",
            "prediction": prediction,
            "confidence": confidence,
            "session_count": session_count,
            "risk_level": risk_level,
            "last_session_display": last_session_display,
            "connected_at": connection.get("connected_at")
        })

    return {
        "patients": patients,
        "count": len(patients)
    }
@router.get("/doctor/patient/{patient_id}")
async def get_patient_details(patient_id: str):

    user = await db.users.find_one({
        "user_id": patient_id
    })

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Patient not found"
        )

    profile = await db.patient_profiles.find_one({
        "user_id": patient_id
    })

    emergency_contacts = await db.emergency_contacts.find({
        "user_id": patient_id
    }).to_list(20)

    for contact in emergency_contacts:
        contact["_id"] = str(
            contact["_id"]
        )

    sessions_cursor = db.analysis_results.find({
        "patient_id": patient_id
    }).sort(
        "created_at",
        -1
    )

    sessions = []

    async for session in sessions_cursor:

        # fusion = session.get(
        #     "fusion_prediction",
        #     {})
        fusion = session.get("fusion_prediction") or session.get("depression") or {}
        

        # sessions.append({
        #     "session_id":
        #         session.get("session_id") or str(session.get("_id", "")),

        #     "prediction":
        #         fusion.get(
        #             "prediction",
        #             "Unknown"
        #         ),

        #     "confidence":
        #         fusion.get(
        #             "confidence",
        #             0
        #         ),

        #     "created_at":
        #         session.get(
        #             "created_at"
        #         )
        # })
        sessions.append({
            "session_id":
                session.get("session_id")
                or str(session.get("_id", "")),

            "created_at":
                session.get(
                    "created_at"
                ),

            # "fusion_prediction": {
            #     "prediction":
            #         fusion.get(
            #             "prediction",
            #             "Unknown"
            #         ),

            #     "confidence":
            #         fusion.get(
            #             "confidence",
            #             0.0
            #         )
            # },
            "fusion_prediction": {
    "prediction": fusion.get(
        "prediction",
        fusion.get("label", "Unknown")
    ),
    "confidence": float(fusion.get("confidence", 0.0))
},

            "sentiment":
                session.get(
                    "sentiment",
                    {}
                ),

            "transcript":
                session.get(
                    "transcript",
                    ""
                ),

            "audio_url":
                session.get(
                    "audio_url",
                    ""
                ),

            "doctor_reviewed":
                session.get(
                    "doctor_reviewed",
                    False
                ),

            "risk_level":
                session.get(
                    "risk_level",
                    "LOW"
                ),

            "doctor_feedback":
                session.get(
                    "doctor_feedback",
                    ""
                )
        })

    return {
        "patient": {
            "patient_id": patient_id,
            "name": user.get("name"),
            "email": user.get("email"),
            "age": profile.get("age") if profile else None,
            "gender": profile.get("gender") if profile else "",
            "primary_concerns":
                profile.get(
                    "primary_concerns",
                    []
                ) if profile else []
        },
        "emergency_contacts":
        emergency_contacts,

        "session_count":
            len(sessions),

        "sessions":
            sessions
    }
@router.get(
    "/doctor/session/{session_id}"
)
async def get_session_details(
    session_id: str
):

    print("[doctor_routes] get_session_details request for session_id:", session_id)

    session = await db.analysis_results.find_one({
        # "_id": ObjectId(session_id)
        "session_id": session_id
    })

    if not session:
        raise HTTPException(
            404,
            "Session not found"
        )

    session["_id"] = str(
        session["_id"]
    )
    session["risk_level"] = session.get(
        "risk_level",
        "LOW"
    )

    session["critical_confirmed"] = session.get(
        "critical_confirmed",
        False
    )
    session[
    "requires_emergency_contact"
] = session.get(
    "requires_emergency_contact",
    False
)

    session["emergency_notified"] = session.get(
        "emergency_notified",
        False
    )

    if session.get("emergency_notified_at"):
        session["emergency_notified_at"] = (
            session["emergency_notified_at"]
            .isoformat()
        )

    print("[doctor_routes] get_session_details fetched from database:", session)

    return session

@router.get("/doctor/patient/{patient_id}/moods")
async def get_patient_moods(patient_id: str):

    cursor = db.patient_moods.find({
        "patient_id": patient_id
    }).sort(
        "timestamp",
        1
    )

    moods = []

    async for mood in cursor:

        moods.append({
            "mood": mood.get("mood", "😐"),
            "timestamp": mood.get("timestamp")
        })

    return {
        "patient_id": patient_id,
        "moods": moods
    }
@router.put(
    "/doctor/session/{session_id}/review"
)
async def mark_session_reviewed(
    session_id: str,
    data: dict
):

    doctor_id = data.get("doctor_id")
    doctor_name = data.get("doctor_name")

    result = await db.analysis_results.update_one(
        {
            "session_id": session_id
        },
        {
            "$set": {
                "doctor_reviewed": True,
                "reviewed_by": doctor_id,
                "reviewed_by_name": doctor_name,
                "reviewed_at": datetime.utcnow()
            }
        }
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return {
        "message": "Session marked as reviewed",
        "session_id": session_id,
        "doctor_reviewed": True,
        "reviewed_by": doctor_id,
        "reviewed_at": datetime.utcnow()
    }
@router.put(
    "/doctor/session/{session_id}/review"
)
async def mark_session_reviewed(
    session_id: str,
    data: dict
):

    doctor_id = data.get(
        "doctor_id"
    )

    doctor_name = data.get(
        "doctor_name"
    )

    feedback = data.get(
        "feedback",
        ""
    )

    requires_emergency_contact = data.get(
        "requires_emergency_contact",
        False
    )

    existing_session = await db.analysis_results.find_one(
        {
            "session_id": session_id
        }
    )

    if not existing_session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    result = await db.analysis_results.update_one(
        {
            "session_id": session_id
        },
        {
            "$set": {
                "doctor_reviewed": True,
                "doctor_feedback": feedback,
                "reviewed_by": doctor_id,
                "reviewed_by_name": doctor_name,
                "reviewed_at": datetime.utcnow(),
                "critical_confirmed": requires_emergency_contact,
                "requires_emergency_contact": requires_emergency_contact,
            }
        }
    )

    updated_session = await db.analysis_results.find_one(
        {
            "session_id": session_id
        }
    )

    return {
        "message":
            "Session marked as reviewed",

        "session_id":
            session_id,

        "doctor_reviewed":
            True,

        "doctor_feedback":
            updated_session.get(
                "doctor_feedback",
                ""
            ),

        "reviewed_by":
            doctor_id,

        "reviewed_by_name":
            doctor_name,

        "reviewed_at":
            updated_session.get(
                "reviewed_at"
            )
    }
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

    # if session.get(
    #     "risk_level"
    # ) != "CRITICAL":
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Session is not critical"
    #     )

    # if not session.get(
    #     "doctor_reviewed",
    #     False
    # ):
    #     raise HTTPException(
    #         status_code=400,
    #         detail="Doctor review required"
    #     )
#     if not session.get(
#         "doctor_reviewed",
#         False
#     ):
#     raise HTTPException(
#         status_code=400,
#         detail="Doctor review required"
#     )

# if not session.get(
#         "requires_emergency_contact",
#         False
#     ):
#     raise HTTPException(
#         status_code=400,
#         detail=(
#             "Doctor has not approved "
#             "emergency escalation."
#         )
#     )

#     if session.get(
#         "emergency_notified",
#         False
#     ):
#         raise HTTPException(
#             status_code=400,
#             detail="Emergency contacts already notified"
#         )
    if not session.get(
        "doctor_reviewed",
        False
    ):
        raise HTTPException(
            status_code=400,
            detail="Doctor review required"
        )

    if not session.get(
        "requires_emergency_contact",
        False
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Doctor has not approved "
                "emergency escalation."
            )
        )

    if session.get(
        "emergency_notified",
        False
    ):
        raise HTTPException(
            status_code=400,
            detail="Emergency contacts already notified"
        )

    patient = await db.users.find_one(
        {
            "user_id":
            session["patient_id"]
        }
    )

    contacts = await db.emergency_contacts.find(
        {
            "user_id":
            session["patient_id"]
        }
    ).to_list(20)

    for contact in contacts:

        if not contact.get("email"):
            continue

        await send_emergency_contact_email(
            to_email=
                contact["email"],

            contact_name=
                contact["name"],

            patient_name=
                patient["name"]
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
            "Emergency contacts notified successfully"
    }