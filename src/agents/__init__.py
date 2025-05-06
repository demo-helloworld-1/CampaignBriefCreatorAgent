# src/agents/__init__.py

# Import the agents so they can be easily accessed from 'from src.agents import ...'
from .summarizer_agent import summarizer_agent
from .brief_generator_agent import brief_generator_agent

# Optionally define __all__ for clarity
__all__ = [
    "summarizer_agent",
    "brief_generator_agent",
]

print("src.agents package initialized.")