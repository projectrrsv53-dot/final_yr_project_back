# from fastapi import APIRouter
# from pymongo import ReturnDocument
# from database import db
# from pydantic import BaseModel

# from passwordhashing import (
#     hash_password,
#     verify_password
# )

# import random

# router = APIRouter()


# # ============================================================
# # REGISTER API
# # ============================================================
# # ============================================================
# # REQUEST MODEL
# # ============================================================

# # ============================================================
# # REGISTER REQUEST MODEL
# # ============================================================

# class RegisterRequest(BaseModel):

#     # ========================================================
#     # BASIC INFO
#     # ========================================================

#     name: str

#     email: str

#     phone: str

#     age: int

#     gender: str

#     # ========================================================
#     # SECURITY
#     # ========================================================

#     password: str

#     role: str

#     # ========================================================
#     # EMERGENCY CONTACT
#     # ========================================================

#     emergency_contact_name:str | None = None

#     emergency_contact_phone:str | None = None

#     emergency_contact_relation:str | None = None

#     # ========================================================
#     # OPTIONAL
#     # ========================================================

#     preferred_doctor_id:str | None = None

#     primary_concern:str | None = None

#     # ========================================================
#     # CONSENT
#     # ========================================================

#     consent_given: bool = False


#  #============================================================
# # AUTO INCREMENT FUNCTION
# # ============================================================

# async def get_next_sequence(name: str):

#     counter = await db.counters.find_one_and_update(

#         {"_id": name},

#         {"$inc": {"sequence_value": 1}},

#         return_document=ReturnDocument.AFTER
#     )

#     return counter["sequence_value"]
# # @router.post("/register")
# # async def register_user(data: RegisterRequest):

# #     users = db.users

# #     # ========================================================
# #     # CHECK EXISTING EMAIL
# #     # ========================================================

# #     existing = await users.find_one({
# #         "email": data.email
# #     })

# #     if existing:

# #         return {
# #             "error": "Email already exists"
# #         }

# #     role = data.role

# #     # ========================================================
# #     # GENERATE USER ID
# #     # ========================================================

# #     if role == "patient":

# #         seq = await get_next_sequence(
# #             "patient_id"
# #         )

# #         user_id = f"PAT_{seq:04d}"

# #     elif role == "doctor":

# #         seq = await get_next_sequence(
# #             "doctor_id"
# #         )

# #         user_id = f"DOC_{seq:04d}"

# #     elif role == "admin":

# #         seq = await get_next_sequence(
# #             "admin_id"
# #         )

# #         user_id = f"ADM_{seq:04d}"

# #     else:

# #         return {
# #             "error": "Invalid role"
# #         }

# #     # ========================================================
# #     # HASH PASSWORD
# #     # ========================================================

# #     hashed = hash_password(
# #         data.password
# #     )

# #     # ========================================================
# #     # USER OBJECT
# #     # ========================================================

# #     user = {

# #         "user_id": user_id,

# #         "name": data.name,

# #         "email": data.email,

# #         "password_hash": hashed,

# #         "role": role
# #     }

# #     result = await users.insert_one(user)

# #     return {

# #         "message": "User created successfully",

# #         "user_id": user_id,

# #         "mongo_id": str(result.inserted_id)
# #     }
# # ============================================================
# # REGISTER API
# # ============================================================

# @router.post("/register")
# async def register_user(data: RegisterRequest):

#     users = db.users

#     # ========================================================
#     # CHECK EXISTING EMAIL
#     # ========================================================

#     existing = await users.find_one({

#         "email": data.email
#     })

#     if existing:

#         return {
#             "error": "Email already exists"
#         }

#     role = data.role.lower()

#     # ========================================================
#     # GENERATE USER ID
#     # ========================================================

#     if role == "patient":

#         seq = await get_next_sequence(
#             "patient_id"
#         )

#         user_id = f"PAT_{seq:04d}"

#     elif role == "doctor":

#         seq = await get_next_sequence(
#             "doctor_id"
#         )

#         user_id = f"DOC_{seq:04d}"

#     elif role == "admin":

#         seq = await get_next_sequence(
#             "admin_id"
#         )

#         user_id = f"ADM_{seq:04d}"

#     else:

#         return {
#             "error": "Invalid role"
#         }

#     # ========================================================
#     # HASH PASSWORD
#     # ========================================================

#     hashed = hash_password(
#         data.password
#     )

#     # ========================================================
#     # USER OBJECT
#     # ========================================================

#     user = {

#         # ====================================================
#         # SYSTEM INFO
#         # ====================================================

#         "user_id": user_id,

#         "role": role,

#         # ====================================================
#         # BASIC INFO
#         # ====================================================

#         "name": data.name,

#         "email": data.email,

#         "phone": data.phone,

#         "age": data.age,

#         "gender": data.gender,

#         # ====================================================
#         # SECURITY
#         # ====================================================

#         "password_hash": hashed,

#         # ====================================================
#         # EMERGENCY CONTACT
#         # ====================================================

#         "emergency_contact": {

#             "name":
#                 data.emergency_contact_name,

#             "phone":
#                 data.emergency_contact_phone,

#             "relation":
#                 data.emergency_contact_relation
#         },

#         # ====================================================
#         # OPTIONAL
#         # ====================================================

#         "preferred_doctor_id":
#             data.preferred_doctor_id,

#         "primary_concern":
#             data.primary_concern,

#         # ====================================================
#         # CONSENT
#         # ====================================================

#         "consent_given":
#             data.consent_given
#     }

#     # ========================================================
#     # SAVE USER
#     # ========================================================

#     result = await users.insert_one(user)

#     # ========================================================
#     # RESPONSE
#     # ========================================================

#     return {

#         "message":
#             "User created successfully",

#         "user_id": user_id,

#         "mongo_id":
#             str(result.inserted_id)
#     }
# # # ============================================================
# # # LOGIN API
# # # ============================================================

# # @router.post("/login")
# # async def login_user(data: dict):

# #     users = db.users

# #     identifier = data["identifier"]

# #     # ========================================================
# #     # FIND USER
# #     # ========================================================

# #     user = await users.find_one({

# #         "$or": [

# #             {"email": identifier},

# #             {"user_id": identifier}
# #         ]
# #     })

# #     if not user:

# #         return {
# #             "error": "User not found"
# #         }

# #     # ========================================================
# #     # VERIFY PASSWORD
# #     # ========================================================

# #     valid = verify_password(
# #         data["password"],
# #         user["password_hash"]
# #     )

# #     if not valid:

# #         return {
# #             "error": "Invalid password"
# #         }

# #     # ========================================================
# #     # SUCCESS
# #     # ========================================================

# #     return {

# #         "message": "Login successful",

# #         "user": {

# #             "id": str(user["_id"]),

# #             "user_id": user["user_id"],

# #             "name": user["name"],

# #             "email": user["email"],

# #             "role": user["role"]
# #         }
# #     }
# # ============================================================
# # LOGIN REQUEST MODEL
# # ============================================================

# class LoginRequest(BaseModel):

#     identifier: str

#     password: str

#     role: str

# # ============================================================
# # LOGIN API
# # ============================================================

# @router.post("/login")
# async def login_user(data: LoginRequest):

#     users = db.users

#     identifier = data.identifier

#     role = data.role.lower()

#     # ========================================================
#     # FIND USER
#     # ========================================================

#     user = await users.find_one({

#         "$or": [

#             {"email": identifier},

#             {"user_id": identifier}
#         ]
#     })

#     if not user:

#         return {
#             "error": "User not found"
#         }

#     # ========================================================
#     # ROLE CHECK
#     # ========================================================

#     if user["role"].lower() != role.lower():

#         return {
#             "error": "Invalid role login"
#         }

#     # ========================================================
#     # VERIFY PASSWORD
#     # ========================================================

#     valid = verify_password(
#         data.password,
#         user["password_hash"]
#     )

#     if not valid:

#         return {
#             "error": "Invalid password"
#         }

#     # ========================================================
#     # SUCCESS
#     # ========================================================

#     return {

#         "message": "Login successful",

#         "user": {

#             "id": str(user["_id"]),

#             "user_id": user["user_id"],

#             "name": user["name"],

#             "email": user["email"],

#             "role": user["role"]
#         }
#     }

# routes/auth_routes.py
from fastapi import APIRouter
from pymongo import ReturnDocument
from database import db
from pymongo.errors import DuplicateKeyError
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from passwordhashing import (
    hash_password,
    verify_password
)

from datetime import datetime

router = APIRouter()

# ============================================================
# EMERGENCY CONTACT MODEL
# ============================================================

class EmergencyContact(BaseModel):

    name: str

    phone: str

    relationship: str

    email: Optional[str] = None


# ============================================================
# REGISTER REQUEST MODEL
# ============================================================

class RegisterRequest(BaseModel):

    # ========================================================
    # COMMON
    # ========================================================

    role: str

    name: str

    email: EmailStr

    phone: str

    password: str

    # ========================================================
    # PATIENT FIELDS
    # ========================================================

    age: Optional[int] = None

    gender: Optional[str] = None

    primary_concerns: Optional[List[str]] = []

    preferred_doctor_id: Optional[str] = None

    consent_given: bool = False

    emergency_contacts: Optional[List[EmergencyContact]] = []

    # ========================================================
    # DOCTOR FIELDS
    # ========================================================

    specialization: Optional[str] = None

    license_id: Optional[str] = None

    hospital_name: Optional[str] = None

    years_experience: Optional[int] = None


# ============================================================
# LOGIN REQUEST MODEL
# ============================================================

class LoginRequest(BaseModel):

    identifier: str

    password: str

    role: str


# ============================================================
# AUTO INCREMENT FUNCTION
# ============================================================

async def get_next_sequence(name: str):

    counter = await db.counters.find_one_and_update(

        {"_id": name},

        {"$inc": {"sequence_value": 1}},

        return_document=ReturnDocument.AFTER,

        upsert=True
    )

    return counter["sequence_value"]


# ============================================================
# REGISTER API
# ============================================================

@router.post("/register")
async def register_user(data: RegisterRequest):

    users = db.users

    # ========================================================
    # CHECK EXISTING EMAIL
    # ========================================================

    existing = await users.find_one({

        "email": data.email
    })

    if existing:

        return {
            "error": "Email already exists"
        }

    role = data.role.lower()

    # ========================================================
    # GENERATE USER ID
    # ========================================================

    if role == "patient":

        seq = await get_next_sequence(
            "patient_id"
        )

        user_id = f"PAT_{seq:04d}"

    elif role == "doctor":

        seq = await get_next_sequence(
            "doctor_id"
        )

        user_id = f"DOC_{seq:04d}"

    elif role == "admin":

        seq = await get_next_sequence(
            "admin_id"
        )

        user_id = f"ADM_{seq:04d}"

    else:

        return {
            "error": "Invalid role"
        }

    # ========================================================
    # HASH PASSWORD
    # ========================================================

    hashed = hash_password(
        data.password
    )

    # ========================================================
    # COMMON USER OBJECT
    # ========================================================

    user = {

        "user_id": user_id,

        "role": role,

        "name": data.name,

        "email": data.email,

        "phone": data.phone,

        "password": hashed,

        "is_active": True,

        # doctors require admin verification
        # "is_verified":
        #     False if role == "doctor" else True,
        "verification_status":

    "pending"
    if role == "doctor"
    else "approved",

        "created_at":
            datetime.utcnow(),

        "last_login":
            None
    }

    await users.insert_one(user)
    

    # # ========================================================
    # # PATIENT PROFILE
    # # ========================================================

    # if role == "patient":

    #     patient_profile = {

    #         "user_id": user_id,

    #         "age": data.age,

    #         "gender": data.gender,

    #         "primary_concerns":
    #             data.primary_concerns,

    #         "preferred_doctor_id":
    #             data.preferred_doctor_id,

    #         "consent_given":
    #             data.consent_given,

    #         "created_at":
    #             datetime.utcnow()
    #     }

    #     await db.patient_profiles.insert_one(
    #         patient_profile
    #     )

    #     # ====================================================
    #     # EMERGENCY CONTACTS
    #     # ====================================================

    #     for contact in data.emergency_contacts:

    #         await db.emergency_contacts.insert_one({

    #             "user_id": user_id,

    #             "name": contact.name,

    #             "phone": contact.phone,

    #             "email": contact.email,

    #             "relationship": contact.relationship
    #         })

    # # ========================================================
    # # DOCTOR PROFILE
    # # ========================================================

    # elif role == "doctor":

    #     doctor_profile = {

    #         "user_id": user_id,

    #         "specialization":
    #             data.specialization,

    #         "license_id":
    #             data.license_id,

    #         "hospital_name":
    #             data.hospital_name,

    #         "years_experience":
    #             data.years_experience,

    #         "verification_status":
    #             "pending",

    #         "verified_by":
    #             None,

    #         "verified_at":
    #             None,

    #         "created_at":
    #             datetime.utcnow()
    #     }

    #     await db.doctor_profiles.insert_one(
    #         doctor_profile
    #     )

    # # ========================================================
    # # RESPONSE
    # # ========================================================

    # return {

    #     "message":
    #         "User registered successfully",

    #     "user_id":
    #         user_id,

    #     "role":
    #         role,

    #     "verification_required":
    #         True if role == "doctor" else False
    # }
        # ========================================================
    # PATIENT PROFILE
    # ========================================================

    if role == "patient":

        try:

            patient_profile = {

                "user_id": user_id,

                "age": data.age,

                "gender": data.gender,

                "primary_concerns":
                    data.primary_concerns,

                "preferred_doctor_id":
                    data.preferred_doctor_id,

                "consent_given":
                    data.consent_given,

                "created_at":
                    datetime.utcnow()
            }

            await db.patient_profiles.insert_one(
                patient_profile
            )

            # ====================================================
            # EMERGENCY CONTACTS
            # ====================================================

            for contact in data.emergency_contacts:

                await db.emergency_contacts.insert_one({

                    "user_id": user_id,

                    "name": contact.name,

                    "phone": contact.phone,

                    "email": contact.email,

                    "relationship": contact.relationship
                })

        except DuplicateKeyError:

            # rollback inserted user
            await users.delete_one({

                "user_id": user_id
            })

            return {

                "error":
                    "Patient profile already exists"
            }

        except Exception as e:

            # rollback inserted user
            await users.delete_one({

                "user_id": user_id
            })

            return {

                "error":
                    f"Patient registration failed: {str(e)}"
            }

    # ========================================================
    # DOCTOR PROFILE
    # ========================================================

    elif role == "doctor":

        try:

            doctor_profile = {

                "user_id": user_id,

                "specialization":
                    data.specialization,

                "license_id":
                    data.license_id,

                "hospital_name":
                    data.hospital_name,

                "years_experience":
                    data.years_experience,

                "verification_status":
                    "pending",

                "verified_by":
                    None,

                "verified_at":
                    None,

                "created_at":
                    datetime.utcnow()
            }

            await db.doctor_profiles.insert_one(
                doctor_profile
            )

        except DuplicateKeyError:

            # rollback inserted user
            await users.delete_one({

                "user_id": user_id
            })

            return {

                "error":
                    "License ID already exists"
            }

        except Exception as e:

            # rollback inserted user
            await users.delete_one({

                "user_id": user_id
            })

            return {

                "error":
                    f"Doctor registration failed: {str(e)}"
            }
# ========================================================
# RESPONSE
# ========================================================

    return {

        "message":
            "User registered successfully",

        "user_id":
            user_id,

        "role":
            role,

        "verification_required":
            True if role == "doctor"
            else False
    }


# # ============================================================
# # LOGIN API
# # ============================================================

# @router.post("/login")
# async def login_user(data: LoginRequest):

#     users = db.users

#     identifier = data.identifier

#     role = data.role.lower()

#     # ========================================================
#     # FIND USER
#     # ========================================================

#     user = await users.find_one({

#         "$or": [

#             {"email": identifier},

#             {"user_id": identifier}
#         ]
#     })

#     if not user:

#         return {
#             "error": "User not found"
#         }

#     # ========================================================
#     # ROLE CHECK
#     # ========================================================

#     if user["role"].lower() != role:

#         return {
#             "error": "Invalid role login"
#         }

#     # ========================================================
#     # VERIFY PASSWORD
#     # ========================================================

#     valid = verify_password(

#         data.password,

#         user["password"]
#     )

#     if not valid:

#         return {
#             "error": "Invalid password"
#         }

#     # ========================================================
# # DOCTOR VERIFICATION CHECK
# # ========================================================

#     if role == "doctor":

#         doctor_profile = await db.doctor_profiles.find_one({

#             "user_id":
#                 user["user_id"]
#         })

#         if not doctor_profile:

#             return {

#                 "error":
#                     "Doctor profile not found"
#             }

#         verification_status = doctor_profile.get(

#             "verification_status",

#             "pending"
#         )

#         # ----------------------------------------------------
#         # PENDING
#         # ----------------------------------------------------

#         if verification_status == "pending":

#             return {

#                 "error":
#                     "Your account is still under admin verification",

#                 "verification_status":
#                     "pending"
#             }

#         # ----------------------------------------------------
#         # REJECTED
#         # ----------------------------------------------------

#         if verification_status == "rejected":

#             return {

#                 "error":
#                     "Your verification request was rejected. Contact admin.",

#                 "verification_status":
#                     "rejected"
#             }

#     # ----------------------------------------------------
#     # SAFETY CHECK
#     # ----------------------------------------------------

#     if verification_status != "approved":

#         return {

#             "error":
#                 "Invalid verification state"
#         }
#     # ========================================================
#     # UPDATE LAST LOGIN
#     # ========================================================

#     await users.update_one(

#         {"_id": user["_id"]},

#         {
#             "$set": {
#                 "last_login":
#                     datetime.utcnow()
#             }
#         }
#     )
#     # ========================================================
# # SAVE LOGIN HISTORY
# # ========================================================

#     await db.login_history.insert_one({

#         "user_id":
#             user["user_id"],

#         "role":
#             user["role"],

#         "login_time":
#             datetime.utcnow(),

#         "platform":
#             "flutter_app"
#     })

#     # ========================================================
#     # SUCCESS
#     # ========================================================

#     return {

#         "message":
#             "Login successful",

#         "user": {

#             "id":
#                 str(user["_id"]),

#             "user_id":
#                 user["user_id"],

#             "name":
#                 user["name"],

#             "email":
#                 user["email"],

#             "role":
#                 user["role"],

#             "is_verified":
#                 user.get("is_verified", False)
#         }
#     }


# ============================================================
# LOGIN API
# ============================================================

@router.post("/login")
async def login_user(data: LoginRequest):

    users = db.users

    identifier = data.identifier

    role = data.role.lower()

    # ========================================================
    # FIND USER
    # ========================================================

    user = await users.find_one({

        "$or": [

            {"email": identifier},

            {"user_id": identifier}
        ]
    })

    if not user:

        raise HTTPException(

            status_code=404,

            detail="User not found"
        )

    # ========================================================
    # ROLE CHECK
    # ========================================================

    if user["role"].lower() != role:

        raise HTTPException(

            status_code=403,

            detail="Invalid role login"
        )

    # ========================================================
    # VERIFY PASSWORD
    # ========================================================

    valid = verify_password(

        data.password,

        user["password"]
    )

    if not valid:

        raise HTTPException(

            status_code=401,

            detail="Invalid password"
        )

    # ========================================================
    # DOCTOR VERIFICATION CHECK
    # ========================================================

    if role == "doctor":

        doctor_profile = await db.doctor_profiles.find_one({

            "user_id":
                user["user_id"]
        })

        if not doctor_profile:

            raise HTTPException(

                status_code=404,

                detail="Doctor profile not found"
            )

        verification_status = doctor_profile.get(

            "verification_status",

            "pending"
        )

        # ----------------------------------------------------
        # PENDING
        # ----------------------------------------------------

        if verification_status == "pending":

            raise HTTPException(

                status_code=403,

                detail=
                "Your account is still under admin verification"
            )

        # ----------------------------------------------------
        # REJECTED
        # ----------------------------------------------------

        if verification_status == "rejected":

            raise HTTPException(

                status_code=403,

                detail=
                "Your verification request was rejected. Contact admin."
            )

        # ----------------------------------------------------
        # SUSPENDED
        # ----------------------------------------------------

        if verification_status == "suspended":

            raise HTTPException(

                status_code=403,

                detail=
                "Your account has been suspended"
            )

        # ----------------------------------------------------
        # SAFETY CHECK
        # ----------------------------------------------------

        if verification_status != "approved":

            raise HTTPException(

                status_code=500,

                detail="Invalid verification state"
            )

    # ========================================================
    # UPDATE LAST LOGIN
    # ========================================================

    await users.update_one(

        {"_id": user["_id"]},

        {
            "$set": {

                "last_login":
                    datetime.utcnow()
            }
        }
    )

    # ========================================================
    # SAVE LOGIN HISTORY
    # ========================================================

    await db.login_history.insert_one({

        "user_id":
            user["user_id"],

        "role":
            user["role"],

        "login_time":
            datetime.utcnow(),

        "platform":
            "flutter_app"
    })

    # ========================================================
    # SUCCESS
    # ========================================================

    return {

        "message":
            "Login successful",

        "user": {

            "id":
                str(user["_id"]),

            "user_id":
                user["user_id"],

            "name":
                user["name"],

            "email":
                user["email"],

            "role":
                user["role"],

            "verification_status":
                doctor_profile.get(
                    "verification_status",
                    "approved"
                )
                if role == "doctor"
                else "approved"
        }
    }

# ============================================================
# GET APPROVED DOCTORS
# ============================================================

@router.get("/doctors")
async def get_doctors():

    doctors = []

    cursor = db.doctor_profiles.find({

        "verification_status": "approved"
    })

    async for profile in cursor:

        user = await db.users.find_one({

            "user_id": profile["user_id"]
        })

        if not user:
            continue

        doctors.append({

            "user_id":
                user["user_id"],

            "name":
                user["name"],

            "specialization":
                profile.get("specialization"),

            "hospital_name":
                profile.get("hospital_name")
        })

    return {

        "doctors": doctors
    }
