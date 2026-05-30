import pytest

from app.compatibility.matrix.rocm import (
    ROCM_MATRIX,
    SUPPORTED_ROCM_VERSIONS,
    get_rocm_entry,
    get_supported_rocm_for_framework,
)


def test_get_rocm_entry_valid():
    entry = get_rocm_entry("5.6.0")

    assert entry is not None
    assert entry.rocm_version == "5.6.0"
    assert entry.min_driver_linux == "5.19"
    assert "gfx1100" in entry.supported_gpus


def test_get_rocm_entry_invalid():
    assert get_rocm_entry("9.9.9") is None


@pytest.mark.parametrize(
    "framework, version, expected",
    [
        ("torch", "2.0.0", ["5.4.2"]),
        ("torch", "2.3.0", ["5.7.0", "6.0.0"]),
        ("torch", "2.4.0", ["6.0.0", "6.1.0"]),
        ("torch", "2.5.0", ["6.2.0"]),
        ("tensorflow", "2.14.0", ["5.6.0"]),
    ],
)
def test_framework_rocm_support(framework, version, expected):
    result = get_supported_rocm_for_framework(framework, version)

    assert result == expected


def test_invalid_framework():
    result = get_supported_rocm_for_framework("invalid_framework", "1.0")

    assert result == []


def test_invalid_framework_version():
    result = get_supported_rocm_for_framework("torch", "99.0")

    assert result == []


def test_supported_rocm_versions_sorted():
    assert SUPPORTED_ROCM_VERSIONS == sorted(ROCM_MATRIX.keys())


@pytest.mark.parametrize(
    "rocm_version, gpu_arch",
    [
        ("5.4.2", "gfx906"),
        ("5.6.0", "gfx1100"),
        ("5.7.0", "gfx1101"),
        ("6.0.0", "gfx940"),
        ("6.1.0", "gfx942"),
        ("6.2.0", "gfx1150"),
    ],
)
def test_gpu_architecture_mapping(rocm_version, gpu_arch):
    entry = get_rocm_entry(rocm_version)

    assert entry is not None
    assert gpu_arch in entry.supported_gpus
