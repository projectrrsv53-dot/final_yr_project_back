from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime


class AnalysisModel(BaseModel):

    patient_id: str = Field(..., min_length=1)

    analysis_type: Literal[
        "fusion",
        "text",
        "audio"
    ]

    depression_score: float = Field(
        ...,
        ge=0,
        le=100
    )

    risk_level: Literal[
        "low",
        "moderate",
        "high",
        "critical"
    ]

    transcript: Optional[str] = None

    recommendation: Optional[str] = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )