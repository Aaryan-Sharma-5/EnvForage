"""Tests for RepairService — template rendering and safety validation."""
import pytest

from app.services.repair_service import (
    REPAIR_TEMPLATE_MAP,
    RepairService,
    RepairTemplateNotFoundError,
)


@pytest.fixture
def service():
    return RepairService()


class TestRepairService:
    def test_list_templates_returns_all(self, service):
        templates = service.list_templates()
        assert len(templates) == 5
        ids = [t["id"] for t in templates]
        assert "repair_cuda_upgrade" in ids
        assert "repair_python_install" in ids
        assert "repair_driver_update" in ids
        assert "repair_venv_recreate" in ids
        assert "repair_pip_reinstall" in ids

    def test_list_templates_have_descriptions(self, service):
        templates = service.list_templates()
        for t in templates:
            assert "id" in t
            assert "description" in t
            assert len(t["description"]) > 10

    @pytest.mark.parametrize("template_id", list(REPAIR_TEMPLATE_MAP.keys()))
    def test_render_all_templates(self, service, template_id):
        """Every registered template renders without errors."""
        params = {
            "target_cuda_version": "12.1",
            "target_python_version": "3.11",
            "min_driver_version": "525.0",
            "python_bin": "python3",
            "venv_dir": ".venv",
            "packages": [
                {"name": "torch", "version": "2.3.0", "pip_spec": "torch==2.3.0", "index_url": None},
            ],
        }
        result = service.render_repair(template_id, params)
        assert result["template_id"] == template_id
        assert result["filename"].endswith(".sh")
        assert not result["filename"].endswith(".j2")
        assert len(result["content"]) > 50
        assert result["size_bytes"] > 0
        assert "EnvForge" in result["content"]

    def test_render_unknown_template_raises(self, service):
        with pytest.raises(RepairTemplateNotFoundError) as exc_info:
            service.render_repair("nonexistent_template")
        assert "nonexistent_template" in str(exc_info.value)
        assert exc_info.value.template_id == "nonexistent_template"

    def test_render_cuda_upgrade_injects_version(self, service):
        result = service.render_repair("repair_cuda_upgrade", {"target_cuda_version": "12.4"})
        assert "12.4" in result["content"]

    def test_render_python_install_injects_version(self, service):
        result = service.render_repair("repair_python_install", {"target_python_version": "3.12"})
        assert "3.12" in result["content"]

    def test_render_includes_timestamp(self, service):
        result = service.render_repair("repair_driver_update")
        # Generated timestamp is injected from _DEFAULT_CONTEXT
        assert "Generated:" in result["content"]

    def test_render_includes_envforge_version(self, service):
        result = service.render_repair("repair_venv_recreate")
        assert "EnvForge" in result["content"]

    def test_output_filename_strips_j2(self, service):
        result = service.render_repair("repair_cuda_upgrade")
        assert result["filename"] == "repair_cuda_upgrade.sh"
