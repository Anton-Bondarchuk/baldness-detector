from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class BaldnessRegion(str, Enum):
    CROWN = "CROWN"
    FRONTAL = "FRONTAL"
    TEMPORAL = "TEMPORAL"
    VERTEX = "VERTEX"
    OVERALL = "OVERALL"

class BaldnessCategory(str, Enum):
    NONE = "NONE"
    SLIGHT = "SLIGHT"
    MODERATE = "MODERATE"
    SIGNIFICANT = "SIGNIFICANT"
    SEVERE = "SEVERE"
    COMPLETE = "COMPLETE"

class BaldnessArea(BaseModel):
    region: BaldnessRegion
    confidenceScore: float = Field(..., ge=0, le=1)
    pixelPercentage: float = Field(..., ge=0, le=100)

class BaldnessResult(BaseModel):
    processedImage: str
    baldnessLevel: float = Field(..., ge=0, le=1)
    baldnessCategory: BaldnessCategory
    baldnessAreas: Optional[List[BaldnessArea]] = []

class ErrorResponse(BaseModel):
    code: int
    message: str
    details: Optional[str] = None