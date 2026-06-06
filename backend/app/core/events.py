import asyncio
from typing import Dict, List, Callable, Awaitable, Any

EventHandler = Callable[[str, Dict[str, Any]], Awaitable[None]]

class EventDispatcher:
    def __init__(self):
        self._listeners: Dict[str, List[EventHandler]] = {}

    def subscribe(self, event_name: str, handler: EventHandler):
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(handler)

    async def _execute_with_retry(self, handler: EventHandler, event_name: str, payload: Dict[str, Any], max_retries: int = 3):
        for attempt in range(max_retries):
            try:
                await handler(event_name, payload)
                return
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"Handler failed after {max_retries} attempts: {e}")
                else:
                    await asyncio.sleep(2 ** attempt)

    async def dispatch(self, event_name: str, payload: Dict[str, Any]):
        if event_name in self._listeners:
            handlers = self._listeners[event_name]
            tasks = [self._execute_with_retry(handler, event_name, payload) for handler in handlers]
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

dispatcher = EventDispatcher()
