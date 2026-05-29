import pytest
from pydantic import ValidationError

from app.schemas.script import GenerationRequest


def test_generation_request_accepts_environment_yml():
    request = GenerationRequest(
        profile_id="pytorch-cuda",
        target_os="LINUX",
        python_version="3.11",
        output_formats=["environment.yml"],
    )

    assert request.output_formats == ["environment.yml"]


def test_generation_request_rejects_unknown_output_format():
    with pytest.raises(ValidationError):
        GenerationRequest(
            profile_id="pytorch-cuda",
            target_os="LINUX",
            python_version="3.11",
            output_formats=["invalid-format.yml"],
        )
