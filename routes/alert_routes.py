# from fastapi import APIRouter
# from database import db

# router = APIRouter()

# @router.get("/doctor/alerts/{doctor_id}")
# async def get_alerts(doctor_id: str):

#     alerts = await db.alerts.find(
#         {
#             "doctor_id": doctor_id,
#             "is_resolved": False
#         }
#     ).sort(
#         "created_at",
#         -1
#     ).to_list(100)

#     for alert in alerts:
#         alert["_id"] = str(alert["_id"])

#     return {
#         "alerts": alerts
#     }
from fastapi import APIRouter
from database import db

router = APIRouter()


@router.get("/doctor/alerts/{doctor_id}")
async def get_alerts(doctor_id: str):

    alerts = await db.alerts.find(
        {
            "doctor_id": doctor_id,
            "is_resolved": False,
        }
    ).sort(
        "created_at",
        -1,
    ).to_list(100)

    formatted = []

    for alert in alerts:

        patient = await db.users.find_one(
            {
                "user_id": alert["patient_id"]
            }
        )

        session = await db.analysis_results.find_one(
            {
                "session_id": alert["session_id"]
            }
        )

        formatted.append({

            "id":
                str(alert["_id"]),

            "patient_id":
                alert["patient_id"],

            "patient_name":
                patient["name"] if patient else "Unknown Patient",

            "session_id":
                alert["session_id"],

            "analysis_type":
                session.get(
                    "analysis_type",
                    "",
                ) if session else "",

            "risk_level":
                alert["risk_level"],

            "message":
                alert["message"],

            "doctor_reviewed":
                session.get(
                    "doctor_reviewed",
                    False,
                ) if session else False,

            "created_at":
                alert["created_at"].isoformat(),

            "is_resolved":
                alert["is_resolved"],
        })

    return {
        "alerts": formatted
    }
from fastapi import HTTPException
from bson import ObjectId

@router.put("/doctor/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):

    result = await db.alerts.update_one(
        {"_id": ObjectId(alert_id)},
        {
            "$set": {
                "is_resolved": True,
            }
        }
    )

    if result.modified_count == 0:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    return {
        "message": "Alert resolved successfully"
    }