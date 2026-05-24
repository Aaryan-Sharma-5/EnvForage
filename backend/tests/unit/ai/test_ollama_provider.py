import json
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest
from pydantic import BaseModel

from app.ai.providers.base import LLMProviderError
from app.ai.providers.ollama import OllamaProvider


class MockResponse(BaseModel):
    message: str


# -----------------------------
# INIT TESTS
# -----------------------------

def test_empty_base_url():
    with pytest.raises(LLMProviderError):
        OllamaProvider(base_url="")


def test_empty_model():
    with pytest.raises(LLMProviderError):
        OllamaProvider(model="")


# -----------------------------
# COMPLETE SUCCESS TEST
# -----------------------------

@pytest.mark.asyncio
async def test_complete_success():

    provider = OllamaProvider()

    mock_response = Mock()

    mock_response.json.return_value = {
        "response": json.dumps({"message": "Hello"})
    }

    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_async_client:

        mock_async_client.return_value.__aenter__.return_value = mock_client

        result = await provider.complete(
            "system",
            "user",
            MockResponse,
        )

        assert result.message == "Hello"


# -----------------------------
# EMPTY RESPONSE TEST
# -----------------------------

@pytest.mark.asyncio
async def test_complete_empty_response():

    provider = OllamaProvider()

    mock_response = Mock()

    mock_response.json.return_value = {
        "response": ""
    }

    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_async_client:

        mock_async_client.return_value.__aenter__.return_value = mock_client

        with pytest.raises(LLMProviderError):

            await provider.complete(
                "system",
                "user",
                MockResponse,
            )


# -----------------------------
# INVALID JSON TEST
# -----------------------------

@pytest.mark.asyncio
async def test_complete_invalid_json():

    provider = OllamaProvider()

    mock_response = Mock()

    mock_response.json.return_value = {
        "response": "not valid json"
    }

    mock_response.raise_for_status.return_value = None

    mock_client = AsyncMock()
    mock_client.post.return_value = mock_response

    with patch("httpx.AsyncClient") as mock_async_client:

        mock_async_client.return_value.__aenter__.return_value = mock_client

        with pytest.raises(LLMProviderError):

            await provider.complete(
                "system",
                "user",
                MockResponse,
            )


# -----------------------------
# CONNECTION ERROR TEST
# -----------------------------

@pytest.mark.asyncio
async def test_complete_connection_error():

    provider = OllamaProvider()

    mock_client = AsyncMock()

    mock_client.post.side_effect = httpx.ConnectError(
        "Connection failed"
    )

    with patch("httpx.AsyncClient") as mock_async_client:

        mock_async_client.return_value.__aenter__.return_value = mock_client

        with pytest.raises(LLMProviderError):

            await provider.complete(
                "system",
                "user",
                MockResponse,
            )


# -----------------------------
# STREAM SUCCESS TEST
# -----------------------------

@pytest.mark.asyncio
async def test_stream_success():

    provider = OllamaProvider()

    stream_lines = [
        json.dumps({"response": "Hello"}),
        json.dumps({"response": " World"}),
    ]

    mock_response = Mock()

    async def mock_aiter_lines():
        for line in stream_lines:
            yield line

    mock_response.aiter_lines = mock_aiter_lines
    mock_response.raise_for_status.return_value = None

    mock_stream = AsyncMock()
    mock_stream.__aenter__.return_value = mock_response

    mock_client = Mock()
    mock_client.stream.return_value = mock_stream

    with patch("httpx.AsyncClient") as mock_async_client:

        mock_async_client.return_value.__aenter__.return_value = mock_client

        chunks = []

        async for chunk in provider.stream(
            "system",
            "user",
            MockResponse,
        ):
            chunks.append(chunk)

        assert "".join(chunks) == "Hello World"


# -----------------------------
# STREAM MALFORMED JSON TEST
# -----------------------------

@pytest.mark.asyncio
async def test_stream_skips_invalid_json():

    provider = OllamaProvider()

    stream_lines = [
        "invalid json",
        json.dumps({"response": "Hello"}),
    ]

    mock_response = Mock()

    async def mock_aiter_lines():
        for line in stream_lines:
            yield line

    mock_response.aiter_lines = mock_aiter_lines
    mock_response.raise_for_status.return_value = None

    mock_stream = AsyncMock()
    mock_stream.__aenter__.return_value = mock_response

    mock_client = Mock()
    mock_client.stream.return_value = mock_stream

    with patch("httpx.AsyncClient") as mock_async_client:

        mock_async_client.return_value.__aenter__.return_value = mock_client

        chunks = []

        async for chunk in provider.stream(
            "system",
            "user",
            MockResponse,
        ):
            chunks.append(chunk)

        assert "".join(chunks) == "Hello"


# -----------------------------
# STREAM CONNECTION ERROR
# -----------------------------

@pytest.mark.asyncio
async def test_stream_connection_error():

    provider = OllamaProvider()

    mock_client = Mock()

    mock_client.stream.side_effect = httpx.ConnectError(
        "Connection failed"
    )

    with patch("httpx.AsyncClient") as mock_async_client:

        mock_async_client.return_value.__aenter__.return_value = mock_client

        with pytest.raises(LLMProviderError):

            async for _ in provider.stream(
                "system",
                "user",
                MockResponse,
            ):
                pass
