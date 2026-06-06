from fastapi import APIRouter
from typing import List, Any
from app.plugins.loader import load_plugins

router = APIRouter()
_active_plugins = {}

@router.get("/plugins", response_model=List[Any])
async def list_available_plugins():
    # In a real app we'd load them once or refresh cache
    plugins = load_plugins("app.plugins")
    return [{"name": p.name, "active": p.name in _active_plugins} for p in plugins]

@router.post("/plugins/{plugin_name}/activate")
async def activate_plugin(plugin_name: str):
    # Mock logic for toggling
    _active_plugins[plugin_name] = True
    return {"message": f"Plugin {plugin_name} activated"}

@router.post("/plugins/{plugin_name}/deactivate")
async def deactivate_plugin(plugin_name: str):
    if plugin_name in _active_plugins:
        del _active_plugins[plugin_name]
    return {"message": f"Plugin {plugin_name} deactivated"}
