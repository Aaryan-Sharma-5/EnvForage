from envforge_agent.schemas import DiagnosticReport

def _map_os_to_target(report: DiagnosticReport) -> str:
    """Map detected operating system to EnvForge target identifier."""
    if report.os.wsl_version:
        return "WSL"
    if "windows" in report.os.name.lower():
        return "WIN"
    return "LINUX"


def _extract_python_version(report: DiagnosticReport) -> str:
    """Extract major.minor Python version from DiagnosticReport."""
    if report.active_python:
        version = report.active_python.version
        parts = version.split(".")
        if len(parts) >= 2 and parts[0] and parts[1]:
            return f"{parts[0]}.{parts[1]}"
    return "3.11"  # safe default

