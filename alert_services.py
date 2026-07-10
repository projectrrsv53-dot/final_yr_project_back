
from datetime import datetime
from database import db
from email_services import send_high_risk_alert_email


# ============================================================
# Calculate Risk
# ============================================================

def calculate_risk(
    prediction: str,
    prediction_confidence: float,
    sentiment_label: str,
    sentiment_confidence: float,
):

    prediction = prediction.strip().lower()
    sentiment_label = sentiment_label.strip().lower()

    # ---------------------------------------
    # LOW RISK
    # ---------------------------------------

    if prediction != "depressed":

        return (
            "LOW",
            "No significant depressive indicators detected."
        )

    # ---------------------------------------
    # CRITICAL
    # ---------------------------------------

    if (
        prediction_confidence >= 0.60 and
        sentiment_label == "negative" and
        sentiment_confidence >= 0.60
    ):

        return (
            "CRITICAL",
            "Critical depression indicators detected with strong negative sentiment."
        )

    # ---------------------------------------
    # HIGH
    # ---------------------------------------

    if prediction_confidence >= 0.55:

        return (
            "HIGH",
            "High depression indicators detected."
        )

    # ---------------------------------------
    # MODERATE
    # ---------------------------------------

    return (

        "MODERATE",

        "Moderate depression indicators detected."

    )


# ============================================================
# Extract Prediction
# ============================================================

def extract_prediction(session_data: dict):

    prediction = "Non-Depressed"

    confidence = 0.0

    # ---------------------------------------
    # TEXT
    # ---------------------------------------

    if isinstance(
        session_data.get("depression"),
        dict,
    ):

        depression = session_data["depression"]

        prediction = depression.get(
            "label",
            "Non-Depressed",
        )

        confidence = float(
            depression.get(
                "confidence",
                0.0,
            )
        )

    # ---------------------------------------
    # FUSION
    # ---------------------------------------

    elif isinstance(
        session_data.get("fusion_prediction"),
        dict,
    ):

        fusion = session_data["fusion_prediction"]

        prediction = fusion.get(
            "prediction",
            "Non-Depressed",
        )

        confidence = float(
            fusion.get(
                "confidence",
                0.0,
            )
        )

    # ---------------------------------------
    # AUDIO
    # ---------------------------------------

    elif isinstance(
        session_data.get("audio_prediction"),
        dict,
    ):

        audio = session_data["audio_prediction"]

        prediction = audio.get(
            "prediction",
            "Non-Depressed",
        )

        confidence = float(
            audio.get(
                "confidence",
                0.0,
            )
        )

    return prediction, confidence


# ============================================================
# Process Alert
# ============================================================

async def process_alert(
    session_data: dict
):

    # ---------------------------------------
    # Prediction
    # ---------------------------------------

    prediction, prediction_confidence = extract_prediction(
        session_data
    )

    # ---------------------------------------
    # Sentiment
    # ---------------------------------------

    sentiment = session_data.get(
        "sentiment",
        {},
    )

    sentiment_label = sentiment.get(
        "label",
        "Neutral",
    )

    sentiment_confidence = float(
        sentiment.get(
            "confidence",
            0.0,
        )
    )

    # ---------------------------------------
    # Risk
    # ---------------------------------------

    risk_level, message = calculate_risk(

        prediction,

        prediction_confidence,

        sentiment_label,

        sentiment_confidence,

    )

    session_data["risk_level"] = risk_level

    # ---------------------------------------
    # Update Session
    # ---------------------------------------

    await db.analysis_results.update_one(

        {

            "session_id":
                session_data["session_id"]

        },

        {

            "$set": {

                "risk_level":
                    risk_level

            }

        }

    )

    # ---------------------------------------
    # LOW / MODERATE
    # ---------------------------------------

    if risk_level not in [

        "HIGH",

        "CRITICAL",

    ]:

        return

    # ---------------------------------------
    # Doctors
    # ---------------------------------------

    shared_doctors = session_data.get(

        "shared_with",

        [],

    )

    for doctor in shared_doctors:

        doctor_id = doctor.get(
            "doctor_id"
        )

        if not doctor_id:
            continue
        doctor = await db.users.find_one(
    {
        "user_id": doctor_id
    }
)

    patient = await db.users.find_one(
        {
            "user_id": session_data["patient_id"]
        }
    )

    if (
        doctor and
        patient and
        doctor.get("email")
    ):

        await send_high_risk_alert_email(
            to_email=doctor["email"],
            doctor_name=doctor["name"],
            patient_name=patient["name"],
            risk_level=risk_level,
        )

        # ===================================
        # Alert
        # ===================================

        alert_document = {

            "patient_id":

                session_data["patient_id"],

            "doctor_id":

                doctor_id,

            "session_id":

                session_data["session_id"],

            "risk_level":

                risk_level,

            "message":

                message,

            "is_resolved":

                False,

            "created_at":

                datetime.utcnow(),

        }

        await db.alerts.insert_one(

            alert_document

        )

        # ===================================
        # Notification
        # ===================================

        notification_document = {

            "doctor_id":

                doctor_id,

            "title":

                f"{risk_level} Risk Alert",

            "body":

                (
                    f"Patient "
                    f"{session_data['patient_id']} "
                    f"requires immediate review."
                ),

            "session_id":

                session_data["session_id"],

            "is_read":

                False,

            "created_at":

                datetime.utcnow(),

        }

        await db.notifications.insert_one(

            notification_document

        )