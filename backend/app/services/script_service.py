"""
Script generation service — orchestrates Compatibility Engine + Template Engine.
"""
import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.compatibility.models import PackageConstraint
from app.compatibility.resolver import CompatibilityResolver
from app.models.profile import EnvironmentProfile
from app.models.script_job import GeneratedScript, ScriptGenerationJob
from app.schemas.script import (
    GenerationRequest,
    GenerationResponse,
    ResolvedPackage,
    ScriptPreview,
)
from app.templates.engine import TemplateRenderer
from app.templates.models import TemplateContext

_resolver = CompatibilityResolver()
_renderer = TemplateRenderer()


async def generate_scripts(
    db: AsyncSession,
    profile: EnvironmentProfile,
    request: GenerationRequest,
) -> GenerationResponse:
    """
    Main script generation pipeline:
    1. Build PackageConstraints from profile
    2. Run CompatibilityResolver
    3. Render templates
    4. Persist job + scripts to DB
    5. Return GenerationResponse
    """
    # Step 1: Build constraints from profile packages
    constraints = [
        PackageConstraint(
            name=pkg.package_name,
            version_spec=pkg.version_spec,
            cuda_variant=pkg.cuda_variant,
        )
        for pkg in sorted(profile.packages, key=lambda p: p.install_order)
    ]

    # Step 2: Resolve compatible versions
    resolved = _resolver.resolve(
        packages=constraints,
        python_version=request.python_version,
        cuda_version=request.cuda_version,
        target_os=request.target_os,
        profile_slug=profile.slug,
        os_support=list(profile.os_support),
        cuda_required=profile.cuda_required,
        overrides=request.overrides,
    )

    # Step 3: Render templates
    ctx = TemplateContext(
        profile_id=profile.slug,
        profile_name=profile.name,
        resolved=resolved,
        warnings=resolved.warnings,
        use_uv=request.use_uv,
        use_micromamba=request.use_micromamba,
    )
    render_results = _renderer.render_all(request.output_formats, ctx)

    # Step 4: Persist job + scripts
    job = ScriptGenerationJob(
        id=uuid.uuid4(),
        profile_id=profile.id,
        target_os=request.target_os,
        python_version=request.python_version,
        cuda_version=request.cuda_version,
        overrides=request.overrides or {},
        status="completed",
        resolved_env=resolved.to_dict(),
        completed_at=datetime.utcnow(),
    )
    db.add(job)

    for rr in render_results:
        db.add(GeneratedScript(
            id=uuid.uuid4(),
            job_id=job.id,
            filename=rr.filename,
            content=rr.content,
            size_bytes=rr.size_bytes,
        ))

    await db.flush()  # Get job.id without committing transaction

    # Step 5: Build response
    return GenerationResponse(
        job_id=job.id,
        status="completed",
        profile_slug=profile.slug,
        target_os=request.target_os,
        python_version=request.python_version,
        cuda_version=request.cuda_version,
        resolved_packages=[
            ResolvedPackage(
                name=p.name,
                version=p.version,
                cuda_variant=p.cuda_variant,
            )
            for p in resolved.packages
        ],
        scripts=[
            ScriptPreview(
                filename=rr.filename,
                content=rr.content,
                size_bytes=rr.size_bytes,
            )
            for rr in render_results
        ],
        warnings=resolved.warnings,
        download_url=f"/api/v1/scripts/{job.id}/download",
    )
