"""Diagnose endpoint -- POST /api/v1/diagnose."""

import asyncio
import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends

from app.api.deps import DB
from app.compatibility.errors import (
    IncompatibilityError,
    UnknownVersionError,
    UnsupportedOSError,
)
from app.compatibility.models import OSTarget, PackageConstraint, ResolvedEnvironment
from app.compatibility.resolver import CompatibilityResolver
from app.middleware.rate_limit import ai_rate_limit
from app.models.diagnostic import DiagnosticReport
from app.models.profile import EnvironmentProfile
from app.schemas.diagnostic import (
    CompatibilityIssue,
    DiagnoseResponse,
    DiagnosticReportSchema,
)
from app.schemas.profile import ProfileFilters
from app.services.profile_service import list_profiles

logger = logging.getLogger(__name__)

router = APIRouter()

# Maximum number of profiles fetched per page when paginating.
# Kept intentionally small so each page fetch is cheap; the while-loop below
# accumulates all pages before running the resolver.
_PROFILE_PAGE_SIZE = 100


@router.post(
    "/diagnose",
    response_model=DiagnoseResponse,
    status_code=201,
    summary="Analyze environment compatibility",
    description=(
        "Accept a diagnostic report from the EnvForge CLI agent and return "
        "a compatibility analysis showing compatible profiles, detected issues, "
        "and recommendations."
    ),
    tags=["Diagnostics"],
    responses={
        201: {"description": "Diagnostic report analyzed successfully"},
        422: {"description": "Invalid diagnostic report payload"},
        500: {"description": "Internal server error"},
    },
)
async def diagnose(
    report: DiagnosticReportSchema,
    db: DB,
    _rate_limit: None = Depends(ai_rate_limit),
) -> DiagnoseResponse:
    """
    Accept a DiagnosticReport from the CLI agent and return
    a compatibility analysis: which profiles are compatible,
    and what issues were found.
    """
    # Map OS to OSTarget: "LINUX", "WSL", "WIN"
    target_os: OSTarget
    if report.os and report.os.wsl_version:
        target_os = "WSL"
    elif report.os and "windows" in report.os.name.lower():
        target_os = "WIN"
    else:
        target_os = "LINUX"

    # Persist the raw report
    db_report = DiagnosticReport(
        id=uuid.uuid4(),
        report_data=report.model_dump(),
        os_type=target_os,
        gpu_name=report.gpus[0].name if report.gpus else None,
        cuda_version=report.cuda.version if report.cuda else None,
        rocm_version=report.rocm.version if report.rocm else None,
        python_version=".".join(report.active_python.version.split(".")[:2])
        if report.active_python
        else None,
        driver_version=report.gpus[0].driver_version if report.gpus else None,
        created_at=datetime.utcnow(),
    )
    db.add(db_report)
    await db.flush()

    # Fetch every profile using pagination so profiles beyond the first page
    # are not silently omitted from the compatibility analysis.
    all_profiles = []
    page = 1
    while True:
        batch, total = await list_profiles(
            db,
            ProfileFilters(
                tags=None,
                os=None,
                cuda_required=None,
                page=page,
                limit=_PROFILE_PAGE_SIZE,
            ),
        )
        all_profiles.extend(batch)
        if len(all_profiles) >= total:
            break
        page += 1

    if not all_profiles:
        return DiagnoseResponse(
            report_id=str(db_report.id),
            compatible_profiles=[],
            issues=[],
            recommendations=[],
        )

    resolver = CompatibilityResolver()

    issues: list[CompatibilityIssue] = []
    compatible_profiles: list[str] = []
    recommendations: list[str] = []

    # CompatibilityResolver.resolve() is a CPU-bound synchronous function.
    # Calling it directly inside an async handler blocks the event loop for
    # the duration of every resolve call. Under concurrent load, all other
    # requests queue behind the resolver. Each call is offloaded to a thread
    # via asyncio.to_thread so the event loop stays free.
    async def _resolve(profile: EnvironmentProfile) -> ResolvedEnvironment:
        packages = [
            PackageConstraint(
                name=package.package_name,
                version_spec=package.version_spec,
                cuda_variant=package.cuda_variant,
            )
            for package in sorted(profile.packages, key=lambda item: item.install_order)
        ]
        return await asyncio.to_thread(
            resolver.resolve,
            packages=packages,
            python_version=(
                report.active_python.version if report.active_python else None
            ) or "3.10",
            cuda_version=report.cuda.version if report.cuda else None,
            rocm_version=report.rocm.version if report.rocm else None,
            target_os=target_os,
            profile_slug=profile.slug,
            os_support=profile.os_support,
            cuda_required=profile.cuda_required,
            rocm_required=getattr(profile, "rocm_required", False),
        )

    results = await asyncio.gather(
        *[_resolve(p) for p in all_profiles],
        return_exceptions=True,
    )

    for profile, result in zip(all_profiles, results):
        if isinstance(result, IncompatibilityError):
            issues.append(
                CompatibilityIssue(
                    severity="ERROR",
                    component=result.component,
                    message=str(result),
                    suggested_fix=result.suggestion,
                    docs_url=result.docs_url,
                )
            )
        elif isinstance(result, (UnknownVersionError, UnsupportedOSError)):
            issues.append(
                CompatibilityIssue(
                    severity="ERROR",
                    component="compatibility",
                    message=str(result),
                    suggested_fix=None,
                    docs_url=None,
                )
            )
        elif isinstance(result, Exception):
            logger.warning("Resolver raised unexpected error for profile %s: %s", profile.slug, result)
        else:
            assert isinstance(result, ResolvedEnvironment)
            compatible_profiles.append(profile.slug)
            if result.warnings:
                recommendations.extend(result.warnings)

    return DiagnoseResponse(
        report_id=str(db_report.id),
        compatible_profiles=compatible_profiles,
        issues=issues,
        recommendations=recommendations,
    )
