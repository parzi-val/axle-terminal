from typing import List

from pydantic import BaseModel, Field


class Correction(BaseModel):
    command: str = Field(..., description="The corrected command")
    description: str = Field(..., description="A brief description of the correction (2 lines max)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence level (0.0 to 1.0)")

class CorrectionResponse(BaseModel):
    corrections: List[Correction] = Field(..., description="List of possible corrections")