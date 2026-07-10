# from fastapi import (
#     APIRouter,
#     UploadFile,
#     File,
#     Form,
#     HTTPException
# )
# from pydantic import BaseModel
# import httpx
# import os

# router = APIRouter(
#     prefix="/ai",
#     tags=["AI"]
# )

# # ==========================================================
# # CONFIG
# # ==========================================================

# AI_SERVER_URL = os.getenv("AI_SERVER_URL")

# if not AI_SERVER_URL:
#     raise RuntimeError(
#         "AI_SERVER_URL environment variable is not set."
#     )

# AI_SERVER_URL = AI_SERVER_URL.rstrip("/")

# TIMEOUT = httpx.Timeout(300.0)


# # ==========================================================
# # REQUEST MODEL
# # ==========================================================

# class TextRequest(BaseModel):
#     patient_id: str
#     text: str


# # ==========================================================
# # TEXT + AUDIO
# # ==========================================================

# @router.post("/predict-text")
# async def predict_text(
#     patient_id: str = Form(...),
#     file: UploadFile = File(...)
# ):

#     try:

#         file_bytes = await file.read()

#         async with httpx.AsyncClient(timeout=TIMEOUT) as client:

#             response = await client.post(
#                 f"{AI_SERVER_URL}/predict-text",
#                 data={
#                     "patient_id": patient_id
#                 },
#                 files={
#                     "file": (
#                         file.filename,
#                         file_bytes,
#                         file.content_type
#                     )
#                 }
#             )

#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=response.text
#             )

#         return response.json()

#     except httpx.RequestError:

#         raise HTTPException(
#             status_code=503,
#             detail="AI Server is unavailable."
#         )

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )


# # ==========================================================
# # TEXT ONLY
# # ==========================================================

# @router.post("/predict-text-direct")
# async def predict_text_direct(
#     request: TextRequest
# ):

#     try:

#         async with httpx.AsyncClient(timeout=TIMEOUT) as client:

#             response = await client.post(
#                 f"{AI_SERVER_URL}/predict-text-direct",
#                 json=request.model_dump()
#             )

#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=response.text
#             )

#         return response.json()

#     except httpx.RequestError:

#         raise HTTPException(
#             status_code=503,
#             detail="AI Server is unavailable."
#         )

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )


# # ==========================================================
# # AUDIO ONLY
# # ==========================================================

# @router.post("/predict-audio")
# async def predict_audio(
#     patient_id: str = Form(...),
#     file: UploadFile = File(...)
# ):

#     try:

#         file_bytes = await file.read()

#         async with httpx.AsyncClient(timeout=TIMEOUT) as client:

#             response = await client.post(
#                 f"{AI_SERVER_URL}/predict-audio",
#                 data={
#                     "patient_id": patient_id
#                 },
#                 files={
#                     "file": (
#                         file.filename,
#                         file_bytes,
#                         file.content_type
#                     )
#                 }
#             )

#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=response.text
#             )

#         return response.json()

#     except httpx.RequestError:

#         raise HTTPException(
#             status_code=503,
#             detail="AI Server is unavailable."
#         )

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )


# # ==========================================================
# # FUSION
# # ==========================================================

# @router.post("/predict-fusion")
# async def predict_fusion(
#     patient_id: str = Form(...),
#     file: UploadFile = File(...)
# ):

#     try:

#         file_bytes = await file.read()

#         async with httpx.AsyncClient(timeout=TIMEOUT) as client:

#             response = await client.post(
#                 f"{AI_SERVER_URL}/predict-fusion",
#                 data={
#                     "patient_id": patient_id
#                 },
#                 files={
#                     "file": (
#                         file.filename,
#                         file_bytes,
#                         file.content_type
#                     )
#                 }
#             )

#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=response.status_code,
#                 detail=response.text
#             )

#         return response.json()

#     except httpx.RequestError:

#         raise HTTPException(
#             status_code=503,
#             detail="AI Server is unavailable."
#         )

#     except Exception as e:

#         raise HTTPException(
#             status_code=500,
#             detail=str(e)
#         )
from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form
)

from pydantic import BaseModel

from ai_services import (
    predict_text,
    predict_text_direct,
    predict_audio,
    predict_fusion,
    get_patient_history,
    get_patient_session,
    get_trend_data,
     review_session,
    confirm_critical,
)


router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


class TextRequest(BaseModel):
    patient_id: str
    text: str
class ReviewRequest(BaseModel):
    doctor_id: str
    doctor_name: str
    feedback: str = ""
    requires_emergency_contact: bool = False



@router.post("/predict-text")
async def text_route(
    patient_id: str = Form(...),
    file: UploadFile = File(...)
):

    return await predict_text(
        patient_id,
        file
    )


@router.post("/predict-text-direct")
async def text_direct_route(
    request: TextRequest
):

    return await predict_text_direct(
        request.patient_id,
        request.text
    )


@router.post("/predict-audio")
async def audio_route(
    patient_id: str = Form(...),
    file: UploadFile = File(...)
):

    return await predict_audio(
        patient_id,
        file
    )


@router.post("/predict-fusion")
async def fusion_route(
    patient_id: str = Form(...),
    file: UploadFile = File(...)
):

    return await predict_fusion(
        patient_id,
        file
    )
@router.get("/patient/history/{patient_id}")
async def history_route(patient_id: str):

    return await get_patient_history(
        patient_id
    )
@router.get("/patient/session/{session_id}")
async def session_route(session_id: str):

    return await get_patient_session(
        session_id
    )
@router.get("/sessions/trend")
async def trend_route():

    return await get_trend_data()



@router.put("/patient/session/{session_id}/review")
async def review_route(
    session_id: str,
    request: ReviewRequest
):

    return await review_session(
        session_id,
        request.model_dump()
    )

@router.post("/patient/session/{session_id}/confirm-critical")
async def confirm_route(
    session_id: str
):

    return await confirm_critical(
        session_id
    )


