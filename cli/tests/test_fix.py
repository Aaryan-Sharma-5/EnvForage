"""
Integration tests for the `envforge fix` CLI command.

Tests mock the backend API using unittest.mock.patch("httpx.AsyncClient")
to intercept the async HTTP requests sent by the CLI agent.
"""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch, AsyncMock

import pytest
from click.testing import CliRunner

from envforge_agent.cli import cli

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_report(tmp_path) -> Path:
    """Write a valid DiagnosticReport JSON to a temp file."""
    raw = (FIXTURES_DIR / "linux_gpu.json").read_text(encoding="utf-8")
    report_file = tmp_path / "report.json"
    report_file.write_text(raw, encoding="utf-8")
    return report_file


@pytest.fixture
def mock_api_success() -> MagicMock:
    """Mock a successful API response from /api/v1/scripts/generate."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {
        "job_id": "test-job-123",
        "resolved_packages": ["torch==2.3.0", "torchvision==0.18.0"],
        "scripts": [
            {
                "filename": "setup.sh",
                "content": "#!/bin/bash\npip install torch==2.3.0"
            }
        ],
        "download_url": "/api/v1/scripts/download/test-job-123"
    }
    return mock_resp


@pytest.fixture(autouse=True)
def mock_httpx(mock_api_success):
    """Globally mock httpx.AsyncClient for all tests in this file."""
    mock_client = MagicMock()
    mock_client.post = AsyncMock(return_value=mock_api_success)
    
    mock_async_client_class = MagicMock()
    mock_async_client_class.return_value.__aenter__.return_value = mock_client
    
    with patch("httpx.AsyncClient", mock_async_client_class):
        yield mock_client


class TestFixHappyPath:
    """Happy path tests for envforge fix."""

    def test_fix_displays_script_content(self, valid_report):
        """Standard run should print script content in a rich panel."""
        runner = CliRunner()
        with patch("httpx.AsyncClient.post", return_value=mock_api_success):
            result = runner.invoke(cli, [
                "fix",
                "--report", str(valid_report),
                "--profile", "pytorch-cuda",
            ])

        assert result.exit_code == 0
        assert "setup.sh" in result.output
        assert "test-job-123" in result.output

    def test_fix_dry_run_lists_filenames_only(self, valid_report):
        """--dry-run should list script filenames without printing content."""
        runner = CliRunner()
        with patch("httpx.AsyncClient.post", return_value=mock_api_success):
            result = runner.invoke(cli, [
                "fix",
                "--report", str(valid_report),
                "--profile", "pytorch-cuda",
                "--dry-run",
            ])

        assert result.exit_code == 0
        assert "setup.sh" in result.output
        # Full script content should NOT appear in dry-run
        assert "pip install torch" not in result.output

    def test_fix_shows_resolved_packages(self, valid_report):
        """Output should include resolved packages from API response."""
        runner = CliRunner()
        with patch("httpx.AsyncClient.post", return_value=mock_api_success):
            result = runner.invoke(cli, [
                "fix",
                "--report", str(valid_report),
                "--profile", "pytorch-cuda",
            ])

        assert result.exit_code == 0
        assert "torch==2.3.0" in result.output

    def test_fix_sends_correct_payload(self, valid_report, mock_httpx):
        """API request payload must contain profile_id, target_os, python_version."""
        runner = CliRunner()
        runner.invoke(cli, [
            "fix",
            "--report", str(valid_report),
            "--profile", "pytorch-cuda",
        ])

        assert mock_httpx.post.called
        call_kwargs = mock_httpx.post.call_args[1]
        payload = call_kwargs["json"]
        assert payload["profile_id"] == "pytorch-cuda"
        assert "target_os" in payload
        assert "python_version" in payload

    def test_fix_uses_custom_api_url(self, valid_report, mock_httpx):
        """--api-url flag should override the default localhost URL."""
        runner = CliRunner()
        with patch("httpx.AsyncClient.post", return_value=mock_api_success) as mock_post:
            runner.invoke(cli, [
                "fix",
                "--report", str(valid_report),
                "--profile", "pytorch-cuda",
                "--api-url", "http://myserver:9000",
            ])

        called_url = mock_httpx.post.call_args[0][0]
        assert "myserver:9000" in called_url


class TestFixAPIErrors:
    """Tests for API error handling in envforge fix."""

    def test_fix_exits_on_connect_error(self, valid_report):
        """ConnectError should print a helpful message and exit 1."""
        import httpx
        runner = CliRunner()
        
        mock_client = MagicMock()
        mock_client.post.side_effect = httpx.ConnectError("refused")
        mock_async_client_class = MagicMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client

        with patch("httpx.AsyncClient", mock_async_client_class):
            result = runner.invoke(cli, [
                "fix",
                "--report", str(valid_report),
                "--profile", "pytorch-cuda",
            ])

        assert result.exit_code == 1
        assert "connect" in result.output.lower()

    def test_fix_exits_on_http_error(self, valid_report):
        """4xx/5xx API responses should exit with code 1."""
        import httpx
        runner = CliRunner()

        mock_resp = MagicMock()
        mock_resp.status_code = 400
        mock_resp.text = "Bad Request"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "400", request=MagicMock(), response=mock_resp
        )

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp
        mock_async_client_class = MagicMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client

        with patch("httpx.AsyncClient", mock_async_client_class):
            result = runner.invoke(cli, [
                "fix",
                "--report", str(valid_report),
                "--profile", "pytorch-cuda",
            ])

        assert result.exit_code == 1

    def test_fix_exits_on_500_error(self, valid_report):
        """500 server error should exit with code 1."""
        import httpx
        runner = CliRunner()

        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.text = "Internal Server Error"
        mock_resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            "500", request=MagicMock(), response=mock_resp
        )

        mock_client = MagicMock()
        mock_client.post.return_value = mock_resp
        mock_async_client_class = MagicMock()
        mock_async_client_class.return_value.__aenter__.return_value = mock_client

        with patch("httpx.AsyncClient", mock_async_client_class):
            result = runner.invoke(cli, [
                "fix",
                "--report", str(valid_report),
                "--profile", "pytorch-cuda",
            ])

        assert result.exit_code == 1


class TestFixMalformedReport:
    """Tests for invalid/malformed report file handling."""

    def test_fix_exits_on_invalid_json(self, tmp_path):
        """Malformed JSON should print parse error and exit 1."""
        bad_report = tmp_path / "bad.json"
        bad_report.write_text("{ this is not valid json }", encoding="utf-8")

        runner = CliRunner()
        result = runner.invoke(cli, [
            "fix",
            "--report", str(bad_report),
            "--profile", "pytorch-cuda",
        ])

        assert result.exit_code == 1

    def test_fix_exits_on_missing_required_fields(self, tmp_path):
        """JSON missing required DiagnosticReport fields should exit 1."""
        bad_report = tmp_path / "incomplete.json"
        bad_report.write_text(
            json.dumps({"agent_version": "1.0.0"}),
            encoding="utf-8"
        )

        runner = CliRunner()
        result = runner.invoke(cli, [
            "fix",
            "--report", str(bad_report),
            "--profile", "pytorch-cuda",
        ])

        assert result.exit_code == 1

    def test_fix_exits_on_nonexistent_report(self, tmp_path):
        """Nonexistent report path should be caught by Click and exit non-zero."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            "fix",
            "--report", str(tmp_path / "nonexistent.json"),
            "--profile", "pytorch-cuda",
        ])

        assert result.exit_code != 0