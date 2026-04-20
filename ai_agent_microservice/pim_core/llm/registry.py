from __future__ import annotations


class AgentModelRegistry:
    """Maps agent names to LLM model identifiers at runtime.

    Rules:
    - One agent has at most one model assigned at a time.
    - Multiple agents can share the same model.
    - Falls back to settings.claude_model when an agent has no explicit assignment.
    """

    def __init__(self) -> None:
        self._registry: dict[str, str] = {}

    def set(self, agent_name: str, model_name: str) -> None:
        """Assign a model to an agent."""
        self._registry[agent_name] = model_name

    def get(self, agent_name: str) -> str:
        """Return the model assigned to the agent, or the default Claude model."""
        if agent_name in self._registry:
            return self._registry[agent_name]
        from pim_core.config import settings
        return settings.claude_model

    def all(self) -> dict[str, str]:
        """Return a snapshot of all current assignments."""
        return dict(self._registry)

    def remove(self, agent_name: str) -> None:
        """Clear the model assignment for an agent, reverting to default."""
        self._registry.pop(agent_name, None)


agent_model_registry = AgentModelRegistry()
