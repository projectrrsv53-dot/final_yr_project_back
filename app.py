

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.emergency_routes import (
    router as emergency_router
)

import os
import uuid
import soundfile as sf
import shutil
from datetime import datetime

# ============================================================
# DATABASE/routes
# ============================================================

from database import db
from routes.auth_routes import (
    router as auth_router
)
from routes.doc_routes import (router as doctor_router)
from routes.admin_routes import router as admin_router
from routes.pat_routes import router as pat_router
from routes.appointment_router import router as appointment_router
from routes.alert_routes import router as alert_router
from routes.ai_routes import router as ai_router
# Removed redundant module import that shadowed `appointment_router` router




# ============================================================
# FASTAPI
# ============================================================

app = FastAPI()
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(pat_router)
app.include_router(doctor_router)
app.include_router(appointment_router)
app.include_router(alert_router)
app.include_router(emergency_router)
app.include_router(ai_router)
# Note: appointment_router is already the `router` instance imported above
# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "Multimodal Depression Backend Running"
    }

