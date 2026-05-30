"""Tests for system prompt constants and integrity."""

from app.ai.prompts.system import (
    AVAILABLE_REPAIR_TEMPLATES,
    TROUBLESHOOT_SYSTEM_PROMPT,
)
from app.services.repair_service import REPAIR_TEMPLATE_MAP


class TestSystemPrompt:
    def test_prompt_is_non_empty(self):
        assert len(TROUBLESHOOT_SYSTEM_PROMPT) > 500

    def test_prompt_contains_json_rule(self):
        assert "JSON" in TROUBLESHOOT_SYSTEM_PROMPT

    def test_prompt_contains_safety_rules(self):
        assert "rm -rf" in TROUBLESHOOT_SYSTEM_PROMPT
        assert "DROP TABLE" in TROUBLESHOOT_SYSTEM_PROMPT
        assert "NEVER" in TROUBLESHOOT_SYSTEM_PROMPT

    def test_prompt_contains_all_template_ids(self):
        for template_id in AVAILABLE_REPAIR_TEMPLATES:
            assert template_id in TROUBLESHOOT_SYSTEM_PROMPT, (
                f"Template '{template_id}' is in AVAILABLE_REPAIR_TEMPLATES "
                f"but not mentioned in the system prompt"
            )

    def test_prompt_lists_read_only_commands(self):
        """The prompt should list safe diagnostic commands."""
        assert "nvidia-smi" in TROUBLESHOOT_SYSTEM_PROMPT
        assert "nvcc --version" in TROUBLESHOOT_SYSTEM_PROMPT
        assert "python --version" in TROUBLESHOOT_SYSTEM_PROMPT

    def test_prompt_blocks_install_commands(self):
        assert "pip install" in TROUBLESHOOT_SYSTEM_PROMPT  # Listed as blocked
        assert "Blocked" in TROUBLESHOOT_SYSTEM_PROMPT


class TestTemplateRegistrySync:
    """Ensure AVAILABLE_REPAIR_TEMPLATES stays in sync with REPAIR_TEMPLATE_MAP."""

    def test_all_available_templates_have_files(self):
        for template_id in AVAILABLE_REPAIR_TEMPLATES:
            assert template_id in REPAIR_TEMPLATE_MAP, (
                f"Template '{template_id}' is in AVAILABLE_REPAIR_TEMPLATES "
                f"but has no entry in REPAIR_TEMPLATE_MAP"
            )

    def test_all_mapped_templates_are_available(self):
        for template_id in REPAIR_TEMPLATE_MAP:
            assert template_id in AVAILABLE_REPAIR_TEMPLATES, (
                f"Template '{template_id}' is in REPAIR_TEMPLATE_MAP "
                f"but not in AVAILABLE_REPAIR_TEMPLATES"
            )

    def test_template_count_matches(self):
        assert len(AVAILABLE_REPAIR_TEMPLATES) == len(REPAIR_TEMPLATE_MAP)
