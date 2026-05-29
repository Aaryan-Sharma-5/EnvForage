"""Pydantic schemas for validating backend/seeds/profiles.yaml."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

ALLOWED_OS = frozenset({"LINUX", "WSL", "WIN"})


class ProfilePackageSeedSchema(BaseModel):
    """Package entry as defined in profiles.yaml."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Package name from the seed profile.",
        examples=["torch"],
    )
    version_spec: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Package version constraint.",
        examples=["==2.1.0"],
    )
    cuda_variant: str | None = Field(
        None,
        max_length=32,
        description="CUDA-specific package variant, if applicable.",
        examples=["cu121"],
    )
    is_optional: bool = Field(
        False,
        description="Whether this package is optional.",
        examples=[False],
    )
    install_order: int = Field(
        0,
        ge=0,
        description="Package installation order.",
        examples=[1],
    )


class ProfileSeedSchema(BaseModel):
    """Single environment profile entry from profiles.yaml."""

    slug: str = Field(
        ...,
        min_length=1,
        max_length=64,
        pattern=r"^[a-z0-9-]+$",
        description="Unique slug for the seeded profile.",
        examples=["pytorch-cu121"],
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=128,
        description="Human-readable seed profile name.",
        examples=["PyTorch CUDA 12.1"],
    )
    description: str = Field(
        "",
        description="Description of the seeded profile.",
        examples=["GPU-ready PyTorch environment for CUDA 12.1."],
    )
    tags: list[str] = Field(
        default_factory=list,
        description="Tags used to categorize the profile.",
        examples=[["ml", "cuda", "pytorch"]],
    )
    os_support: list[str] = Field(
        ...,
        min_length=1,
        description="Supported operating systems.",
        examples=[["LINUX", "WSL"]],
    )
    cuda_required: bool = Field(
        False,
        description="Whether CUDA is required by this profile.",
        examples=[True],
    )
    python_versions: list[str] = Field(
        ...,
        min_length=1,
        description="Supported Python versions.",
        examples=[["3.10", "3.11"]],
    )
    cuda_versions: list[str] = Field(
        default_factory=list,
        description="Supported CUDA versions.",
        examples=[["12.1"]],
    )
    status: Literal["ACTIVE", "DEPRECATED"] = Field(
        "ACTIVE",
        description="Lifecycle status of the seed profile.",
        examples=["ACTIVE"],
    )
    last_validated: date | None = Field(
        None,
        description="Date when this profile was last validated.",
        examples=["2026-05-26"],
    )
    packages: list[ProfilePackageSeedSchema] = Field(
        default_factory=list,
        description="Packages included in the seed profile.",
    )

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> str:
        if value is None:
            return ""
        if not isinstance(value, str):
            raise ValueError("description must be a string")
        return value.strip()

    @field_validator("os_support")
    @classmethod
    def validate_os_support(cls, value: list[str]) -> list[str]:
        invalid = [os_name for os_name in value if os_name not in ALLOWED_OS]
        if invalid:
            allowed = ", ".join(sorted(ALLOWED_OS))
            raise ValueError(
                f"Invalid os_support values: {invalid}. Allowed: {allowed}"
            )
        return value


class ProfilesYamlSchema(BaseModel):
    """Root structure of profiles.yaml."""

    profiles: list[ProfileSeedSchema] = Field(
        ...,
        description="List of environment profiles loaded from profiles.yaml.",
    )


class GenerationRequest(BaseModel):
    """Schema for validating a generation request payload."""

    target_os: Literal["Linux", "Windows", "WSL"] = Field(
        ...,
        description="Target operating system for generation.",
        examples=["Linux"],
    )
    framework: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Framework requested for generation.",
        examples=["pytorch"],
    )
    cuda_version: str = Field(
        ...,
        min_length=1,
        max_length=16,
        description="Requested CUDA version.",
        examples=["12.1"],
    )
