"""
OS-specific constraint rules for script generation.

These rules encode platform-level requirements that affect what can be
generated, not package version compatibility.
"""
from typing import Literal

OSTarget = Literal["LINUX", "WSL", "WIN"]

# ── Script format rules ────────────────────────────────────────────────────────

# Map OS target to the valid script formats it supports
OS_SCRIPT_FORMATS: dict[str, list[str]] = {
    "LINUX": ["setup.sh", "requirements.txt", "Dockerfile", "docker-compose.yml", "devcontainer.json"],
    "WSL":   ["setup.sh", "requirements.txt", "Dockerfile", "docker-compose.yml", "devcontainer.json"],
    "WIN": ["setup.ps1", "requirements.txt", "Dockerfile", "docker-compose.yml", "devcontainer.json"],
}

# ── CUDA / GPU rules ──────────────────────────────────────────────────────────

# TensorFlow dropped native Windows GPU support after 2.10.
# GPU on Windows requires WSL2 for TF 2.11+.
TENSORFLOW_WINDOWS_GPU_NOTE = (
    "TensorFlow 2.11+ does not support native GPU on Windows. "
    "GPU acceleration requires WSL2. "
    "See: https://www.tensorflow.org/install/pip#windows-wsl2"
)

# WSL2 requires GPU drivers to be installed on the Windows HOST, not inside WSL.
WSL_GPU_NOTE = (
    "WSL2 GPU access requires NVIDIA drivers installed on the Windows host. "
    "Do NOT install CUDA toolkit inside WSL if drivers are already on Windows. "
    "See: https://docs.nvidia.com/cuda/wsl-user-guide/"
)


def get_os_notes(
    target_os: OSTarget,
    cuda_required: bool,
    frameworks: list[str],
) -> list[str]:
    """
    Return a list of OS-specific informational notes for the given
    target configuration. Notes are non-fatal — they are warnings
    displayed to the user alongside the generated scripts.
    """
    notes: list[str] = []

    if target_os == "WSL" and cuda_required:
        notes.append(WSL_GPU_NOTE)

    if target_os == "WIN" and "tensorflow" in frameworks and cuda_required:
        notes.append(TENSORFLOW_WINDOWS_GPU_NOTE)

    return notes


def validate_output_format(target_os: OSTarget, output_format: str) -> bool:
    """Return True if the output format is valid for the given OS target."""
    return output_format in OS_SCRIPT_FORMATS.get(target_os, [])
