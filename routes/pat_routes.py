# routes/pat_routes.py
from fastapi import APIRouter
from analysis_model import AnalysisModel
from datetime import datetime
from database import db
from fastapi import HTTPException
from email_services import send_doctor_added_email
import httpx
import os

AI_SERVER_URL = os.getenv("AI_SERVER_URL")

router = APIRouter()


@router.post("/analyse")
async def analyse(data: AnalysisModel):

    return {
        "message": "Analysis complete",
        "result": data
    }

# @router.get("/patient/history")
# async def patient_history(patient_id:str):

#     sessions=await db.analysis_results.find(

#         {"patient_id":patient_id}

#     ).sort(

#         "timestamp",-1

#     ).to_list(100)

#     return{

#         "sessions":sessions

#     }

# @router.get("/patient/history/{patient_id}")
# async def patient_history(patient_id: str):

#     sessions = await db.analysis_results.find(
#         {"patient_id": patient_id}
#     ).sort(
#         "created_at", -1
#     ).to_list(100)

#     for session in sessions:

#         session["_id"] = str(session["_id"])

#         if "created_at" in session:
#             session["created_at"] = session["created_at"].isoformat()

#     return {
#         "sessions": sessions
#     }
@router.post("/save-mood")
async def save_mood(data: dict):

    mood = {
        "patient_id": data.get("patient_id"),
        "mood": data.get("mood"),
        "timestamp": datetime.utcnow()
    }

    await db.patient_moods.insert_one(mood)

    return {
        "message": "Mood saved successfully"
    }



# @router.post("/patient/connect-doctor")
# async def connect_doctor(data: dict):

#     patient_id = data.get("patient_id")
#     doctor_id = data.get("doctor_id")

#     if not patient_id or not doctor_id:
#         raise HTTPException(
#             status_code=400,
#             detail="patient_id and doctor_id are required"
#         )

#     # Verify doctor exists
#     doctor = await db.users.find_one({
#         "user_id": doctor_id,
#         "role": "doctor",
#         "is_verified": True,
#         "is_active": True
#     })

#     if not doctor:
#         raise HTTPException(
#             status_code=404,
#             detail="Doctor not found"
#         )

#     # Prevent duplicate connection
#     existing = await db.doctor_patient_access.find_one({
#         "patient_id": patient_id,
#         "doctor_id": doctor_id,
#         "active": True
#     })

#     if existing:
#         return {
#             "message": "Doctor already connected"
#         }

#     connection = {
#         "patient_id": patient_id,
#         "doctor_id": doctor_id,
#         "active": True,
#         "connected_at": datetime.utcnow()
#     }

#     result = await db.doctor_patient_access.insert_one(connection)

#     return {
#         "message": "Doctor connected successfully",
#         "connection_id": str(result.inserted_id)
#     }
@router.post("/patient/connect-doctor")
async def connect_doctor(data: dict):

    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")

    if not patient_id or not doctor_id:
        raise HTTPException(
            status_code=400,
            detail="patient_id and doctor_id are required"
        )

    doctor = await db.users.find_one({
        "user_id": doctor_id,
        "role": "doctor",
        "is_active": True
    })

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    doctor_profile = await db.doctor_profiles.find_one({
        "user_id": doctor_id,
        "verification_status": "approved"
    })

    if not doctor_profile:
        raise HTTPException(
            status_code=404,
            detail="Doctor not approved"
        )

    existing = await db.doctor_patient_access.find_one({
        "patient_id": patient_id,
        "doctor_id": doctor_id
    })

    if existing:
        return {
            "message": "Doctor already connected"
        }

    connection = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "active": True,
        "connected_at": datetime.utcnow()
    }

    # result = await db.doctor_patient_access.insert_one(
    #     connection
    # )

    # return {
    #     "message": "Doctor connected successfully",
    #     "connection_id": str(
    #         result.inserted_id
    #     )
    # }
    result = await db.doctor_patient_access.insert_one(
        connection
    )

    # ==========================================
    # SEND EMAIL TO DOCTOR
    # ==========================================

    patient = await db.users.find_one({
        "user_id": patient_id
    })

    # await send_doctor_added_email(
    #     to_email=doctor["email"],
    #     doctor_name=doctor["name"],
    #     patient_name=patient["name"]
    # )
    try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{AI_SERVER_URL}/email/doctor-added",
                    json={
                        "to_email": doctor["email"],
                        "doctor_name": doctor["name"],
                        "patient_name": patient["name"],
                    },
                )

            response.raise_for_status()

    except Exception as e:
            print(f"Failed to send doctor notification: {e}")

            return {
                "message": "Doctor connected successfully",
                "connection_id": str(
                    result.inserted_id
                )
            }


@router.get("/patient/my-doctors/{patient_id}")
async def get_my_doctors(patient_id: str):

    doctors = []

    cursor = db.doctor_patient_access.find({
        "patient_id": patient_id,
        "active": True
    })

    async for access in cursor:

        doctor = await db.users.find_one({
            "user_id": access["doctor_id"]
        })

        profile = await db.doctor_profiles.find_one({
            "user_id": access["doctor_id"]
        })
        availability = await db.doctor_availability.find_one({
    "doctor_id": access["doctor_id"]
})

        if doctor:
            # doctors.append({
            #     "user_id": doctor["user_id"],
            #     "name": doctor["name"],
            #     "specialization":
            #         profile.get("specialization", "")
            #         if profile else "",
            #     "hospital_name":
            #         profile.get("hospital_name", "")
            #         if profile else "",
            #     "rating":
            #         profile.get("rating", 5.0)
            #         if profile else 5.0
            # })
            doctors.append({

    "user_id":
        doctor["user_id"],

    "name":
        doctor["name"],

    "specialization":
        profile.get(
            "specialization",
            "",
        ) if profile else "",

    "experience":
        profile.get(
            "experience",
            "N/A",
        ) if profile else "N/A",

    "hospital_name":
        profile.get(
            "hospital_name",
            "",
        ) if profile else "",

    "rating":
        profile.get(
            "rating",
            5.0,
        ) if profile else 5.0,

    "working_days":
        availability.get(
            "working_days",
            [],
        ) if availability else [],

    "start_time":
        availability.get(
            "start_time",
        ) if availability else None,

    "end_time":
        availability.get(
            "end_time",
        ) if availability else None,

    "break_start":
        availability.get(
            "break_start",
        ) if availability else None,

    "break_end":
        availability.get(
            "break_end",
        ) if availability else None,

    "slot_duration":
        availability.get(
            "slot_duration",
            30,
        ) if availability else 30,

    "availability_configured":
        availability.get(
            "availability_configured",
            False,
        ) if availability else False,
})

    return {
        "doctors": doctors
    }
# @router.get("/patient/available-doctors/{patient_id}")
# async def available_doctors(patient_id: str):

#     connected_ids = []

#     cursor = db.doctor_patient_access.find({
#         "patient_id": patient_id,
#         "active": True
#     })

#     async for access in cursor:
#         connected_ids.append(
#             access["doctor_id"]
#         )

#     doctors = []

#     cursor = db.users.find({
#         "role": "doctor",
#         "verification_status": True,
#         "is_active": True,
#         "user_id": {
#             "$nin": connected_ids
#         }
#     })

#     async for user in cursor:

#         profile = await db.doctor_profiles.find_one({
#             "user_id": user["user_id"]
#         })

#         doctors.append({
#             "user_id": user["user_id"],
#             "name": user["name"],
#             "specialization":
#                 profile.get("specialization", "")
#                 if profile else "",
#             "hospital_name":
#                 profile.get("hospital_name", "")
#                 if profile else "",
#             "rating":
#                 profile.get("rating", 5.0)
#                 if profile else 5.0
#         })

#     return {
#         "doctors": doctors
#     }
@router.get("/patient/available-doctors/{patient_id}")
async def available_doctors(patient_id: str):

    connected_ids = []

    cursor = db.doctor_patient_access.find({
        "patient_id": patient_id
    })

    async for access in cursor:
        connected_ids.append(
            access["doctor_id"]
        )

    doctors = []

    cursor = db.doctor_profiles.find({
        "verification_status": "approved",
        "user_id": {
            "$nin": connected_ids
        }
    })

    async for profile in cursor:

        user = await db.users.find_one({
            "user_id": profile["user_id"]
        })

        if user:
            doctors.append({
                "user_id": user["user_id"],
                "name": user["name"],
                "specialization":
                    profile.get(
                        "specialization",
                        ""
                    ),
                "hospital_name":
                    profile.get(
                        "hospital_name",
                        ""
                    ),
                "rating":
                    profile.get(
                        "rating",
                        5.0
                    )
            })

    return {
        "doctors": doctors
    }
# @router.get("/patient/session/{session_id}")
# async def get_patient_session(
#     session_id: str
# ):

#     session = await db.analysis_results.find_one(
#         {
#             "session_id": session_id
#         }
#     )

#     if not session:
#         raise HTTPException(
#             status_code=404,
#             detail="Session not found"
#         )

#     session["_id"] = str(
#         session["_id"]
#     )

#     if "created_at" in session:
#         session["created_at"] = (
#             session["created_at"]
#             .isoformat()
#         )

#     if "reviewed_at" in session:
#         session["reviewed_at"] = (
#             session["reviewed_at"]
#             .isoformat()
#         )

#     return session
