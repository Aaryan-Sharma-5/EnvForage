# Architecture System Design Updates

This document expands upon the core architectural concepts introduced during the massive implementation blueprint, detailing how advanced systems scale and interact.

## 1. Event Bus & Webhook Dispatcher
**The Problem:** Triggering external URLs synchronously during a diagnostic completion blocks the FastAPI event loop, causing massive latency for the end-user.
**The Solution:** We utilize FastAPI's native `BackgroundTasks` (or a Celery worker pool for heavy enterprise scale) as an asynchronous Event Bus.
- When `diagnose.completed` occurs, the payload is serialized and handed to the background queue.
- The dispatcher generates an **HMAC SHA-256 signature** using the user's registered webhook secret.
- Delivery utilizes `requests` with a strict 3-second timeout and exponential backoff logic (up to 3 retries) for failed HTTP deliveries.

## 2. Distributed Rate Limiter (Redis)
**The Problem:** In-memory dictionary rate limiters fail when the backend is horizontally scaled across multiple Kubernetes pods.
**The Solution:** We implement a Token-Bucket algorithm backed by a shared Redis instance.
- Middleware intercepts every request and maps it to either a client IP or an authenticated JWT Token.
- **Tiered Rules:** Expensive routes (like `/api/v1/troubleshoot` hitting AI Providers) are capped strictly (e.g., 5 requests/minute). Static profile retrievals are capped loosely (e.g., 100 requests/minute).
- Redis handles the atomic decrement operations (`DECR`) guaranteeing race-condition-free throttling.

## 3. CLI Offline Caching & Synchronization
**The Problem:** Developers often work in air-gapped environments or on servers lacking outbound internet access.
**The Solution:** The CLI Agent (`envforge_agent`) initializes a local SQLite database at `~/.envforge/cache.db`.
- **Offline Flag:** When run with `--offline`, the HTTP POST to the backend is bypassed entirely.
- Telemetry data is timestamped, hashed, and stored locally.
- Users can run `envforge restore` to read the cached database and execute automated rollback scripts to undo a previously generated setup.

## 4. Asynchronous AI Streaming Responses
**The Problem:** Waiting 15-20 seconds for an LLM to generate a complex dependency resolution script results in terrible UX.
**The Solution:** The backend standardizes all AI interactions through a unified `BaseProvider` interface utilizing `AsyncGenerator` yields.
- FastAPI's `StreamingResponse` wraps these yields, pushing Server-Sent Events (SSE) `text/event-stream` chunks directly to the client over an open HTTP connection.
- The frontend utilizes a custom `useAIStream` React Hook to append the chunks to a state variable, which is parsed in real-time by the MDX component tree.
- Context summarization middleware ensures that bloated local log files are truncated *before* interacting with token-limited AI models.
