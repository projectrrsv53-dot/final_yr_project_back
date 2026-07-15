# routes/admin_routes.py
from fastapi import APIRouter
from database import db
from datetime import datetime
from fastapi import Query
import httpx
import os

AI_SERVER_URL = os.getenv("AI_SERVER_URL")

# from email_services import (

#     send_verification_email,

#     send_rejection_email
# )

router = APIRouter()

# # ============================================================
# # ADMIN VERIFY DOCTOR
# # ============================================================

@router.patch("/admin/verify-doctor/{user_id}")
async def verify_doctor(user_id: str):

    user = await db.users.find_one({

        "user_id": user_id,

        "role": "doctor"
    })

    if not user:

        return {
            "error": "Doctor not found"
        }

    # ========================================================
    # ALREADY VERIFIED
    # ========================================================

    if user.get(

        "verification_status"

    ) == "approved":

        return {

            "error":
                "Doctor already verified"
        }

    # ========================================================
    # UPDATE USER
    # ========================================================

    await db.users.update_one(

        {"user_id": user_id},

        {
            "$set": {

                "verification_status":
                    "approved",

                "is_active":
                    True
            }
        }
    )

    # ========================================================
    # UPDATE PROFILE
    # ========================================================

    await db.doctor_profiles.update_one(

        {"user_id": user_id},

        {
            "$set": {

                "verification_status":
                    "approved",

                "verified_at":
                    datetime.utcnow()
            }
        }
    )

    # ========================================================
    # SEND EMAIL
    # ========================================================

    # await send_verification_email(

    #     user["email"],

    #     user["name"]
    # )
   

    async with httpx.AsyncClient() as client:
        await client.post(
            f"{AI_SERVER_URL}/email/doctor-approved",
            json={
                "to_email": user["email"],
                "doctor_name": user["name"],
            },
        )

    return {

        "message":
            "Doctor verified successfully"
    }


# ============================================================
# ADMIN REJECT DOCTOR
# ============================================================

@router.patch("/admin/reject-doctor/{user_id}")
async def reject_doctor(user_id: str):

    user = await db.users.find_one({

        "user_id": user_id,

        "role": "doctor"
    })

    if not user:

        return {
            "error": "Doctor not found"
        }

    # ========================================================
    # UPDATE USER
    # ========================================================

    await db.users.update_one(

        {"user_id": user_id},

        {
            "$set": {

                "verification_status":
                    "rejected",

                "is_active":
                    False
            }
        }
    )

    # ========================================================
    # UPDATE PROFILE
    # ========================================================

    await db.doctor_profiles.update_one(

        {"user_id": user_id},

        {
            "$set": {

                "verification_status":
                    "rejected",

                "verified_at":
                    datetime.utcnow()
            }
        }
    )

    # ========================================================
    # SEND EMAIL
    # ========================================================

    # await send_rejection_email(

    #     user["email"],

    #     user["name"]
    # )
    async with httpx.AsyncClient() as client:
        await client.post(
            f"{AI_SERVER_URL}/email/doctor-rejected",
            json={
                "to_email": user["email"],
                "doctor_name": user["name"],
            },
        )

    return {

        "message":
            "Doctor rejected successfully"
    }


# ============================================================
# GET PENDING DOCTOR REQUESTS
# ============================================================

@router.get("/admin/pending-doctors")
async def get_pending_doctors():

    doctors = []

    cursor = db.doctor_profiles.find({

        "verification_status":
            "pending"
    })

    async for doc in cursor:

        user = await db.users.find_one({

            "user_id":
                doc["user_id"]
        })

        if not user:
            continue

        doctors.append({

            "user_id":
                doc["user_id"],

            "name":
                user.get("name"),

            "email":
                user.get("email"),

            "phone":
                user.get("phone"),

            "specialization":
                doc.get("specialization"),

            "license_id":
                doc.get("license_id"),

            "hospital_name":
                doc.get("hospital_name"),

            "years_experience":
                doc.get("years_experience"),

            "verification_status":
                doc.get("verification_status"),

            "created_at":
                str(doc.get("created_at"))
        })

    return {

        "pending_doctors":
            doctors
    }


# ============================================================
# GET APPROVED DOCTORS
# ============================================================

@router.get("/admin/approved-doctors")
async def get_approved_doctors():

    doctors = []

    cursor = db.doctor_profiles.find({

        "verification_status":
            "approved"
    })

    async for doc in cursor:

        user = await db.users.find_one({

            "user_id":
                doc["user_id"]
        })

        if not user:
            continue

        doctors.append({

            "user_id":
                doc["user_id"],

            "name":
                user.get("name"),

            "email":
                user.get("email"),

            "phone":
                user.get("phone"),

            "specialization":
                doc.get("specialization"),

            "hospital_name":
                doc.get("hospital_name"),

            "years_experience":
                doc.get("years_experience"),

            "verification_status":
                doc.get("verification_status")
        })

    return {

        "approved_doctors":
            doctors
    }


# ============================================================
# GET REJECTED DOCTORS
# ============================================================

@router.get("/admin/rejected-doctors")
async def get_rejected_doctors():

    doctors = []

    cursor = db.doctor_profiles.find({

        "verification_status":
            "rejected"
    })

    async for doc in cursor:

        user = await db.users.find_one({

            "user_id":
                doc["user_id"]
        })

        if not user:
            continue

        doctors.append({

            "user_id":
                doc["user_id"],

            "name":
                user.get("name"),

            "email":
                user.get("email"),

            "phone":
                user.get("phone"),

            "specialization":
                doc.get("specialization"),

            "hospital_name":
                doc.get("hospital_name"),

            "years_experience":
                doc.get("years_experience"),

            "verification_status":
                doc.get("verification_status")
        })

    return {

        "rejected_doctors":
            doctors
    }
# ============================================================
# DASHBOARD STATS
# ============================================================

@router.get("/admin/dashboard-stats")
async def dashboard_stats():

    pending_doctors = await db.doctor_profiles.count_documents({
        "verification_status": "pending"
    })

    approved_doctors = await db.doctor_profiles.count_documents({
        "verification_status": "approved"
    })

    rejected_doctors = await db.doctor_profiles.count_documents({
        "verification_status": "rejected"
    })

    patients = await db.patient_profiles.count_documents({})
    total_sessions = await db.analysis_results.count_documents({})

    return {
        "pending_doctors": pending_doctors,
        "approved_doctors": approved_doctors,
        "rejected_doctors": rejected_doctors,
        "patients": patients,
        "sessions": total_sessions,
    }


# ============================================================
# VERIFICATION STATS
# ============================================================

@router.get("/admin/verification-stats")
async def verification_stats():

    approved = await db.doctor_profiles.count_documents({
        "verification_status": "approved"
    })

    pending = await db.doctor_profiles.count_documents({
        "verification_status": "pending"
    })

    rejected = await db.doctor_profiles.count_documents({
        "verification_status": "rejected"
    })

    return {
        "approved": approved,
        "pending": pending,
        "rejected": rejected
    }


# ============================================================
# GET ALL DOCTORS
# ============================================================

@router.get("/admin/doctors")
async def get_all_doctors():

    doctors = []

    cursor = db.doctor_profiles.find()

    async for doc in cursor:

        user = await db.users.find_one({
            "user_id": doc["user_id"]
        })

        if not user:
            continue

        doctors.append({

            "user_id": doc["user_id"],

            "name": user.get("name"),

            "email": user.get("email"),

            "phone": user.get("phone"),

            "specialization": doc.get("specialization"),

            "license_id": doc.get("license_id"),

            "hospital_name": doc.get("hospital_name"),

            "years_experience": doc.get("years_experience"),

            "verification_status": doc.get("verification_status"),

            "created_at": str(doc.get("created_at")),

            "verified_at": str(doc.get("verified_at"))
        })

    return {
        "doctors": doctors
    }


# ============================================================
# GET SINGLE DOCTOR
# ============================================================

@router.get("/admin/doctor/{user_id}")
async def get_doctor(user_id: str):

    user = await db.users.find_one({
        "user_id": user_id,
        "role": "doctor"
    })

    if not user:
        return {
            "error": "Doctor not found"
        }

    profile = await db.doctor_profiles.find_one({
        "user_id": user_id
    })

    if not profile:
        return {
            "error": "Doctor profile not found"
        }
    connected_patients = await db.doctor_patient_access.count_documents({
    "doctor_id": user_id,
    "active": True
})
    reviewed_sessions = await db.analysis_results.count_documents({
    "doctor_id": user_id,
    "doctor_reviewed": True
})

    return {

        "user_id": user_id,

        "name": user.get("name"),

        "email": user.get("email"),

        "phone": user.get("phone"),

        "specialization": profile.get("specialization"),

        "license_id": profile.get("license_id"),

        "hospital_name": profile.get("hospital_name"),

        "years_experience": profile.get("years_experience"),

        "verification_status": profile.get("verification_status"),

        "created_at": str(profile.get("created_at")),

        "verified_at": str(profile.get("verified_at")),
        "connected_patients": connected_patients,
"reviewed_sessions": reviewed_sessions,
    }


# ============================================================
# GET SINGLE PATIENT
# ============================================================

@router.get("/admin/patient/{user_id}")
async def get_patient(user_id: str):

    user = await db.users.find_one({
        "user_id": user_id,
        "role": "patient"
    })

    if not user:
        return {
            "error": "Patient not found"
        }

    profile = await db.patient_profiles.find_one({
        "user_id": user_id
    })

    if not profile:
        return {
            "error": "Patient profile not found"
        }

    sessions = []

    cursor = db.analysis_results.find({
        "patient_id": user_id
    })

    async for session in cursor:
        session["_id"] = str(session["_id"])
        sessions.append(session)

    return {

        "user_id": user_id,

        "name": user.get("name"),

        "email": user.get("email"),

        "phone": user.get("phone"),

        "age": profile.get("age"),

        "gender": profile.get("gender"),

        "created_at": str(profile.get("created_at")),

        "sessions": sessions
    }
# ============================================================
# GET ALL PATIENTS
# ============================================================

# @router.get("/admin/patients")
# async def get_patients():

#     patients = []

#     cursor = db.patient_profiles.find()

#     async for profile in cursor:

#         user = await db.users.find_one({
#             "user_id": profile["user_id"]
#         })

#         if not user:
#             continue

#         session_count = await db.sessions.count_documents({
#             "patient_id": profile["user_id"]
#         })

#         patients.append({

#             "user_id":
#                 profile["user_id"],

#             "name":
#                 user.get("name"),

#             "email":
#                 user.get("email"),

#             "phone":
#                 user.get("phone"),

#             "age":
#                 profile.get("age"),

#             "gender":
#                 profile.get("gender"),

#             "created_at":
#                 str(profile.get("created_at")),

#             "session_count":
#                 session_count
#         })

#     return {
#         "patients": patients
#     }
# # ============================================================
# # GET SETTINGS
# # ============================================================

# @router.get("/admin/settings")
# async def get_settings():

#     settings = await db.settings.find_one({})

#     if not settings:
#         return {
#             "maintenance_mode": False
#         }

#     settings.pop("_id", None)

#     return settings


# # ============================================================
# # UPDATE SETTINGS
# # ============================================================

# @router.put("/admin/settings")
# async def update_settings(data: dict):

#     await db.settings.update_one(
#         {},
#         {
#             "$set": data
#         },
#         upsert=True
#     )

#     return {
#         "message": "Settings updated successfully"
#     }
# ============================================================
# GET ALL PATIENTS
# ============================================================

@router.get("/admin/patients")
async def get_patients():

    patients = []

    cursor = db.patient_profiles.find()

    async for profile in cursor:

        user = await db.users.find_one({
            "user_id": profile["user_id"]
        })

        if not user:
            continue

        sessions = []

        cursor_sessions = db.analysis_results.find({
            "patient_id": profile["user_id"]
        })

        async for session in cursor_sessions:

            session["_id"] = str(session["_id"])

            sessions.append(session)

        latest_risk = "LOW"

        if sessions:
            latest_session = max(
                sessions,
                key=lambda s: s.get("created_at", datetime.min)
            )

            latest_risk = latest_session.get(
                "risk_level",
                "LOW"
            )

        patients.append({

            "user_id":
                profile["user_id"],

            "name":
                user.get("name"),

            "email":
                user.get("email"),

            "phone":
                user.get("phone"),

            "age":
                profile.get("age"),

            "gender":
                profile.get("gender"),

            "created_at":
                str(profile.get("created_at")),

            "sessions":
                sessions,
            "risk_level": latest_risk,
            "session_count": len(sessions),
        })

    return {
        "patients": patients
    }
from datetime import datetime

@router.get("/admin/recent-activity")
async def get_recent_activity():

    activity = []

    # Recently verified doctors
    # verified = await db.doctor_profiles.find(
    #     {
    #         "verified": True
    #     }
    # ).sort(
    #     "verified_at",
    #     -1
    # ).limit(5).to_list(5)
    verified = await db.doctor_profiles.find(
    {
        "verification_status": "approved"
    }
).sort(
    "verified_at",
    -1
).limit(5).to_list(5)

    for doctor in verified:

        user = await db.users.find_one(
            {
                "user_id": doctor["user_id"]
            }
        )

        activity.append({
            "type": "doctor_verified",
            "name": user.get("name", "Unknown"),
            "time": doctor.get("verified_at")
        })

    # Latest critical/high-risk sessions
    critical = await db.analysis_results.find(
        {
            "risk_level": {
                "$in": ["CRITICAL", "HIGH"]
            }
        }
    ).sort(
        "created_at",
        -1
    ).limit(5).to_list(5)

    for session in critical:

        patient = await db.users.find_one(
            {
                "user_id": session["patient_id"]
            }
        )

        activity.append({
            "type": "critical_session",
            "patient": patient.get("name", "Unknown"),
            "risk_level": session.get("risk_level"),
            "time": session.get("created_at")
        })

    activity.sort(
        key=lambda x: x["time"] or datetime.min,
        reverse=True,
    )

    return {
        "activity": activity
    }
@router.get("/admin/reports")
async def get_reports():

    total_sessions = await db.analysis_results.count_documents({})

    text_sessions = await db.analysis_results.count_documents({
        "analysis_type": "text"
    })

    fusion_sessions = await db.analysis_results.count_documents({
        "analysis_type": "fusion"
    })

    risk_distribution = {
        "CRITICAL":
            await db.analysis_results.count_documents(
                {"risk_level": "CRITICAL"}
            ),

        "HIGH":
            await db.analysis_results.count_documents(
                {"risk_level": "HIGH"}
            ),

        "MEDIUM":
            await db.analysis_results.count_documents(
                {"risk_level": "MEDIUM"}
            ),

        "LOW":
            await db.analysis_results.count_documents(
                {"risk_level": "LOW"}
            ),
    }

    return {

        "total_sessions": total_sessions,

        "analysis_types": {
            "text": text_sessions,
            "fusion": fusion_sessions,
        },

        "risk_distribution": risk_distribution,
    }
@router.get("/admin/search")
async def search(query: str = Query(...)):

    query = query.strip()

    patients = []

    doctors = []

    patient_cursor = db.users.find(
        {
            "role": "patient",
            "name": {
                "$regex": query,
                "$options": "i"
            }
        }
    )

    async for user in patient_cursor:

        patients.append({
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
        })

    doctor_cursor = db.users.find(
        {
            "role": "doctor",
            "name": {
                "$regex": query,
                "$options": "i"
            }
        }
    )

    async for user in doctor_cursor:

        doctors.append({
            "user_id": user["user_id"],
            "name": user["name"],
            "email": user["email"],
        })

    return {

        "patients": patients,

        "doctors": doctors,
    }