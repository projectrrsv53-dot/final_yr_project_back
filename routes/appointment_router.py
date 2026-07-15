# routes/appointment_router.py
from calendar import day_name
from bson import ObjectId
from fastapi import APIRouter, HTTPException
from database import db
from datetime import datetime, timedelta
# from email_services import (
#     send_appointment_confirmation_to_patient,
#     send_appointment_notification_to_doctor
# )
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

AI_SERVER_URL = os.getenv("AI_SERVER_URL")

router = APIRouter()

# @router.post("/appointment/book")

# async def book(data: dict):

#     appointment={

#         "patient_id": data["patient_id"],

#         "doctor_id": data["doctor_id"],

#         "date": data["date"],

#         "time": data["time"],

#         "reason": data["reason"],

#         "status": "Pending",

#         "created_at": datetime.utcnow()

#     }

#     await db.appointments.insert_one(appointment)

#     return {

#         "message": "Appointment booked"

#     }
@router.post("/appointment/book")
async def book(data: dict):

    patient_id = data.get("patient_id")
    doctor_id = data.get("doctor_id")
    appointment_date = data.get("date")
    appointment_time = data.get("time")

    if not all([patient_id, doctor_id, appointment_date, appointment_time]):
        raise HTTPException(
            status_code=400,
            detail="Missing required fields: patient_id, doctor_id, date, time"
        )

    existing = await db.appointments.find_one(
        {
            "doctor_id": doctor_id,
            "date": appointment_date,
            "time": appointment_time,
            # "status": {
            #     "$in": [
            #         "pending",
            #         "confirmed"
            #     ]
            # }
            "status": "confirmed"
        }
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Slot already booked"
        )

    appointment = {
        "patient_id": data["patient_id"],
        "doctor_id": data["doctor_id"],
        "date": data["date"],
        "time": data["time"],
        "reason": data["reason"],
        "status": "confirmed",
        "created_at": datetime.utcnow()
    }

    result = await db.appointments.insert_one(
        appointment
    )

    patient_id = data["patient_id"]
    doctor_id = data["doctor_id"]

    patient = await db.users.find_one(
        {"user_id": patient_id}
    )

    doctor = await db.users.find_one(
        {"user_id": doctor_id}
    )

    if patient and patient.get("email"):
        try:
            # await send_appointment_confirmation_to_patient(
            #     to_email=patient["email"],
            #     patient_name=patient.get("name", "Patient"),
            #     doctor_name=doctor.get("name", "Doctor") if doctor else "Doctor",
            #     appointment_date=data["date"],
            #     appointment_time=data["time"],
            #     reason=data.get("reason", "Consultation")
            # )
            async with httpx.AsyncClient() as client:
                await client.post(
                f"{AI_SERVER_URL}/email/appointment-patient",
                json={
                    "to_email": patient["email"],
                    "patient_name": patient.get("name", "Patient"),
                    "doctor_name": doctor.get("name", "Doctor") if doctor else "Doctor",
                    "appointment_date": appointment_date,
                    "appointment_time": appointment_time,
                    "reason": data.get("reason", "Consultation"),
                },
            )
        except Exception as e:
            print(f"Error sending patient email: {e}")

    if doctor and doctor.get("email"):
        try:
            # await send_appointment_notification_to_doctor(
            #     to_email=doctor["email"],
            #     doctor_name=doctor.get("name", "Doctor"),
            #     patient_name=patient.get("name", "Patient") if patient else "Patient",
            #     appointment_date=data["date"],
            #     appointment_time=data["time"],
            #     reason=data.get("reason", "Consultation")
            # )
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{AI_SERVER_URL}/email/appointment-doctor",
                    json={
                        "to_email": doctor["email"],
                        "doctor_name": doctor["name"],
                        "patient_name": patient["name"],
                        "appointment_date": appointment_date,
                        "appointment_time": appointment_time,
                        "reason": data.get("reason", "Consultation"),
    },
)
        except Exception as e:
            print(f"Error sending doctor email: {e}")

    return {
        "message":
            "Appointment booked",

        "appointment_id":
            str(
                result.inserted_id
            )
    }



@router.post("/doctor/availability")
async def save_availability(data: dict):

    doctor_id = data.get("doctor_id")
    start = datetime.strptime(
        data["start_time"],
        "%H:%M"
    )

    end = datetime.strptime(
        data["end_time"],
        "%H:%M"
    )

    if end <= start:
        raise HTTPException(
            status_code=400,
            detail=(
                "End time must be "
                "after start time."
            )
        )

    duration_hours = (
        end - start
    ).total_seconds() / 3600

    if duration_hours < 4:
        raise HTTPException(
            status_code=400,
            detail=(
                "Availability must "
                "be at least "
                "4 hours long."
            )
        )

    if (
        data.get("break_start") and
        data.get("break_end")
    ):

        break_start_time = datetime.strptime(
            data["break_start"],
            "%H:%M"
        )

        break_end_time = datetime.strptime(
            data["break_end"],
            "%H:%M"
        )

        if break_end_time <= break_start_time:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Break end time "
                    "must be after "
                    "break start time."
                )
            )

        if (
            break_start_time < start or
            break_end_time > end
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Break time must "
                    "be inside working "
                    "hours."
                )
            )

    doctor = await db.users.find_one(
        {
            "user_id": doctor_id,
            "role": "doctor"
        }
    )

    if not doctor:
        raise HTTPException(
            status_code=404,
            detail="Doctor not found"
        )

    existing = await db.doctor_availability.find_one(
        {
            "doctor_id": doctor_id
        }
    )

    created_at = datetime.utcnow()
    if existing:
        created_at = existing.get("created_at", datetime.utcnow())

    availability = {
        "doctor_id": doctor_id,

        "working_days":
            data.get(
                "working_days",
                [],
            ),

        "start_time":
            data.get(
                "start_time",
            ),

        "end_time":
            data.get(
                "end_time",
            ),

        "slot_duration":
            data.get(
                "slot_duration",
                30,
            ),

        "break_start":
            data.get(
                "break_start",
            ),

        "break_end":
            data.get(
                "break_end",
            ),

        "availability_configured":
            True,

        "created_at":
            created_at,

        "updated_at":
            datetime.utcnow(),
    }

    await db.doctor_availability.update_one(
        {
            "doctor_id":
                doctor_id
        },

        {
            "$set":
                availability
        },

        upsert=True,
    )

    await db.doctor_profiles.update_one(
        {
            "user_id":
                doctor_id
        },

        {
            "$set": {
                "availability_configured":
                    True
            }
        }
    )

    return {
        "message":
            "Availability saved successfully"
    }
@router.get(
    "/doctor/availability/{doctor_id}"
)
async def get_availability(
    doctor_id: str
):

    availability = await db.doctor_availability.find_one(
        {
            "doctor_id":
                doctor_id
        }
    )

    if not availability:
        return {
            "availability_configured":
                False
        }

    availability["_id"] = str(
        availability["_id"]
    )

    return availability
@router.get(
    "/doctor/available-slots/{doctor_id}"
)
async def get_available_slots(
    doctor_id: str,
    date: str,
):

    availability = await db.doctor_availability.find_one(
        {
            "doctor_id":
                doctor_id
        }
    )

    if not availability:
        return {
            "availability_configured":
                False
        }

    appointment_date = datetime.strptime(
        date,
        "%Y-%m-%d"
    )

    day_name = appointment_date.strftime(
        "%A"
    )

    if day_name not in availability[
        "working_days"
    ]:
        return {
            "slots": []
        }

    start = datetime.strptime(
        availability["start_time"],
        "%H:%M"
    )

    end = datetime.strptime(
        availability["end_time"],
        "%H:%M"
    )

    duration = availability[
        "slot_duration"
    ]

    break_start = availability.get(
        "break_start"
    )

    break_end = availability.get(
        "break_end"
    )

    booked = await db.appointments.find(
        {
            "doctor_id":
                doctor_id,

            "date":
                date,

            # "status": {
            #     "$in": [
            #         "pending",
            #         "confirmed"
            #     ]
            # }
            "status": "confirmed"
        }
    ).to_list(100)

    booked_slots = [
        appointment["time"]
        for appointment in booked
    ]

    slots = []

    # current = start

    # while current < end:

    #     current_slot = current.strftime(
    #         "%H:%M"
    #     )

    #     if (
    #         break_start and
    #         break_end and
    #         break_start <= current_slot < break_end
    #     ):
    #         current += timedelta(
    #             minutes=duration
    #         )
    #         continue

    #     if current_slot not in booked_slots:
    #         slots.append(
    #             current_slot
    #         )

    #     current += timedelta(
    #         minutes=duration
    #     )

    # return {
    #     "slots":
    #         slots
    # }
    current = start

    now = datetime.now()

    while current < end:

        current_slot = current.strftime("%H:%M")

        slot_datetime = datetime.combine(
            appointment_date.date(),
            current.time()
        )

        # Skip past time slots if booking for today
        if slot_datetime <= now:
            current += timedelta(minutes=duration)
            continue

        # Skip break time
        if (
            break_start and
            break_end and
            break_start <= current_slot < break_end
        ):
            current += timedelta(minutes=duration)
            continue

        # Skip booked slots
        if current_slot not in booked_slots:
            slots.append(current_slot)

        current += timedelta(minutes=duration)

    print("Booked Slots:", booked_slots)
    print("Available Slots:", slots)

    return {
        "slots": slots
    }
@router.get(
    "/doctor/appointments/{doctor_id}"
)
async def get_doctor_appointments(
    doctor_id: str
):

    appointments = await db.appointments.find(
        {
            "doctor_id":
                doctor_id
        }
    ).sort(
        "created_at",
        -1
    ).to_list(100)

    for appointment in appointments:

        appointment["_id"] = str(
            appointment["_id"]
        )

        patient = await db.users.find_one(
            {
                "user_id":
                    appointment[
                        "patient_id"
                    ]
            }
        )

        appointment[
            "patient_name"
        ] = (
            patient.get(
                "name"
            )
            if patient
            else "Unknown Patient"
        )

    return {
        "appointments":
            appointments
    }
@router.get("/patient/appointments/{patient_id}")
async def get_patient_appointments(patient_id: str):

    appointments = []

    cursor = db.appointments.find(
        {
            "patient_id": patient_id
        }
    ).sort("date", 1)

    async for appointment in cursor:

        doctor = await db.users.find_one(
            {
                "user_id": appointment["doctor_id"]
            }
        )

        profile = await db.doctor_profiles.find_one(
            {
                "user_id": appointment["doctor_id"]
            }
        )

        appointments.append({

            "appointment_id":
                str(appointment["_id"]),

            "doctor_name":
                doctor.get("name", "Doctor")
                if doctor else "Doctor",

            "specialization":
                profile.get("specialization", "")
                if profile else "",

            "date":
                appointment["date"],

            "time":
                appointment["time"],

            "reason":
                appointment.get(
                    "reason",
                    "",
                ),

            "status":
                appointment.get(
                    "status",
                    "Confirmed",
                ),
        })

    return {
        "appointments": appointments
    }