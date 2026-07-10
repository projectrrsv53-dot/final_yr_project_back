import os
import httpx

from fastapi import (
    UploadFile,
    HTTPException
)


# ==========================================================
# CONFIG
# ==========================================================

AI_SERVER_URL = os.getenv("AI_SERVER_URL")

if not AI_SERVER_URL:
    raise RuntimeError(
        "AI_SERVER_URL environment variable is not set."
    )

AI_SERVER_URL = AI_SERVER_URL.rstrip("/")

TIMEOUT = httpx.Timeout(300.0)


# ==========================================================
# COMMON REQUEST
# ==========================================================

async def _send_request(
    endpoint: str,
    data=None,
    json=None,
    files=None
):

    try:

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:

            response = await client.post(
                f"{AI_SERVER_URL}/{endpoint}",
                data=data,
                json=json,
                files=files
            )

        if response.status_code != 200:

            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        return response.json()

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail="AI Server is unavailable."
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==========================================================
# TEXT + AUDIO
# ==========================================================

async def predict_text(
    patient_id: str,
    file: UploadFile
):

    file_bytes = await file.read()

    return await _send_request(

        endpoint="predict-text",

        data={
            "patient_id": patient_id
        },

        files={
            "file": (
                file.filename,
                file_bytes,
                file.content_type
            )
        }
    )


# ==========================================================
# TEXT ONLY
# ==========================================================

async def predict_text_direct(
    patient_id: str,
    text: str
):

    return await _send_request(

        endpoint="predict-text-direct",

        json={
            "patient_id": patient_id,
            "text": text
        }
    )


# ==========================================================
# AUDIO
# ==========================================================

async def predict_audio(
    patient_id: str,
    file: UploadFile
):

    file_bytes = await file.read()

    return await _send_request(

        endpoint="predict-audio",

        data={
            "patient_id": patient_id
        },

        files={
            "file": (
                file.filename,
                file_bytes,
                file.content_type
            )
        }
    )


# ==========================================================
# FUSION
# ==========================================================

async def predict_fusion(
    patient_id: str,
    file: UploadFile
):

    file_bytes = await file.read()

    return await _send_request(

        endpoint="predict-fusion",

        data={
            "patient_id": patient_id
        },

        files={
            "file": (
                file.filename,
                file_bytes,
                file.content_type
            )
        }
    )
# ==========================================================
# COMMON GET REQUEST
# ==========================================================

async def _get_request(endpoint: str):

    try:

        async with httpx.AsyncClient(timeout=TIMEOUT) as client:

            response = await client.get(
                f"{AI_SERVER_URL}/{endpoint}"
            )

        if response.status_code != 200:

            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )

        return response.json()

    except httpx.RequestError:

        raise HTTPException(
            status_code=503,
            detail="AI Server is unavailable."
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# ==========================================================
# PATIENT HISTORY
# ==========================================================

async def get_patient_history(
    patient_id: str
):

    return await _get_request(
        f"patient/history/{patient_id}"
    )
# ==========================================================
# PATIENT SESSION
# ==========================================================

async def get_patient_session(
    session_id: str
):

    return await _get_request(
        f"patient/session/{session_id}"
    )
# ==========================================================
# TREND DATA
# ==========================================================

async def get_trend_data():

    return await _get_request(
        "sessions/trend"
    )

async def review_session(
    session_id: str,
    data: dict
):
   return await _send_request(
        method="PUT",
        endpoint=f"patient/session/{session_id}/review",
        json=data
    )

async def confirm_critical(
    session_id: str
):

    return await _send_request(
        method="POST",
        endpoint=f"patient/session/{session_id}/confirm-critical"
    )
    