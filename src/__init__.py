bl_info = {
    "name": "Auto-Reload Linked Libraries",
    "author": "gandalf3",
    "version": (0, 0, 2),
    "blender": (2, 80, 0),
    "description": "Automatically reload linked libraries when they are modified.",
    "doc_url": "https://github.com/gandalf3/auto-reload-linked-libraries",
    "tracker_url": "https://github.com/gandalf3/auto-reload-linked-libraries/issues",
    "category": "System",
}

try:
    import bpy
except ModuleNotFoundError:
    pass
else:
    from .main import *
