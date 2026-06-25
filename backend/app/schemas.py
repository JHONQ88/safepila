from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SemaphoreStatus(str, Enum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"


class Flag(BaseModel):
    layer: str = Field(..., description="Capa de validación: metadata, dates, structure, ai")
    finding: str = Field(..., description="Hallazgo detectado")
    severity: Severity = Field(..., description="Severidad del hallazgo")
    weight: int = Field(..., ge=0, le=100, description="Peso en el score final")


class ValidationDetails(BaseModel):
    producer: Optional[str] = None
    creator: Optional[str] = None
    creation_date: Optional[str] = None
    mod_date: Optional[str] = None
    pages: Optional[int] = None
    has_incremental_updates: bool = False
    incremental_update_count: int = 0
    suspicious_objects: List[str] = Field(default_factory=list)
    fonts: List[str] = Field(default_factory=list)
    images_count: int = 0
    images_without_metadata: int = 0


class ValidationResult(BaseModel):
    filename: str
    status: Literal["APPROVED", "SUSPICIOUS", "REJECTED"]
    semaphore: SemaphoreStatus
    score: int = Field(..., ge=0, le=100)
    verdict: str
    flags: List[Flag] = Field(default_factory=list)
    details: ValidationDetails
    processed_at: datetime = Field(default_factory=datetime.utcnow)


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)