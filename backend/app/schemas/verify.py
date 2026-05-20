"""Pydantic schemas for environment verification."""
import uuid

from pydantic import BaseModel, ConfigDict, Field


class VerificationCheckSchema(BaseModel):
    """Schema for a single verification check result."""
    check_name: str
    passed: bool
    detail: str | None = None

    model_config = ConfigDict(from_attributes=True)


class VerificationRequest(BaseModel):
    """Request schema for POST /api/v1/verify."""
    profile_id: uuid.UUID
    report_id: uuid.UUID | None = None
    raw_output: str


class VerificationResponse(BaseModel):
    """Response schema for POST /api/v1/verify."""
    result_id: uuid.UUID
    profile_id: uuid.UUID
    overall_status: str = Field(..., description="Either 'passed' or 'failed'")
    checks: list[VerificationCheckSchema]

    model_config = ConfigDict(from_attributes=True)
