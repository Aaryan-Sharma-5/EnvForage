def test_get_rocm_entry_valid():
    entry = get_rocm_entry("5.6.0")

    assert entry is not None
    assert entry.rocm_version == "5.6.0"
    assert "gfx1100" in entry.supported_gpus
