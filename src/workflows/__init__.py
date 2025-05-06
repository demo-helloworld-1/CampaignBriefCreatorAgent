# src/workflows/__init__.py

# Import and expose the compiled workflow graph
# This will be defined and compiled in brief_generation_workflow.py
# The import might be None if brief_generation_workflow.py fails to compile
from .brief_generation_workflow import compiled_supervisor_workflow

# Optionally define __all__ for clarity
__all__ = [
    "compiled_supervisor_workflow",
]

print("src.workflows package initialized.")