"""Unit tests for StreamTracker (graceful SSE shutdown drain)."""

import asyncio

from app.core.stream_tracker import StreamTracker


async def _consume(stream) -> list[str]:
    return [item async for item in stream]


async def test_track_counts_active_then_releases() -> None:
    tracker = StreamTracker()

    async def gen():
        yield "a"
        yield "b"

    wrapped = tracker.track(gen())
    assert tracker.active == 1  # counted as soon as it is handed over

    assert await _consume(wrapped) == ["a", "b"]
    assert tracker.active == 0  # released once exhausted


async def test_drain_returns_immediately_when_idle() -> None:
    tracker = StreamTracker()
    assert await tracker.drain(timeout=0.1) is True


async def test_drain_waits_for_active_stream_to_finish() -> None:
    tracker = StreamTracker()
    started = asyncio.Event()

    async def slow():
        started.set()
        await asyncio.sleep(0.05)
        yield "done"

    wrapped = tracker.track(slow())
    consumer = asyncio.create_task(_consume(wrapped))

    await started.wait()
    assert tracker.active == 1

    assert await tracker.drain(timeout=1.0) is True
    assert tracker.active == 0
    await consumer


async def test_drain_times_out_when_stream_is_stuck() -> None:
    tracker = StreamTracker()
    release = asyncio.Event()

    async def stuck():
        yield "first"
        await release.wait()  # not released within the drain timeout
        yield "second"

    wrapped = tracker.track(stuck())
    consumer = asyncio.create_task(_consume(wrapped))

    await asyncio.sleep(0.01)  # let it start and yield "first"
    assert tracker.active == 1

    assert await tracker.drain(timeout=0.05) is False
    assert tracker.active == 1  # still in flight

    release.set()
    await consumer
    assert tracker.active == 0
