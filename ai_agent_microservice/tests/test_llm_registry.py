def test_registry_get_returns_default_when_agent_not_set():
    """Registry falls back to settings.claude_model for unknown agents."""
    from pim_core.llm.registry import AgentModelRegistry
    from pim_core.config import settings
    reg = AgentModelRegistry()
    assert reg.get("content") == settings.claude_model


def test_registry_set_and_get():
    """set() stores a model; get() returns it."""
    from pim_core.llm.registry import AgentModelRegistry
    reg = AgentModelRegistry()
    reg.set("content", "gpt-4o")
    assert reg.get("content") == "gpt-4o"


def test_registry_multiple_agents_independent():
    """Different agents have independent model assignments."""
    from pim_core.llm.registry import AgentModelRegistry
    reg = AgentModelRegistry()
    reg.set("content", "claude-sonnet-4-6")
    reg.set("catalog", "gpt-4o")
    assert reg.get("content") == "claude-sonnet-4-6"
    assert reg.get("catalog") == "gpt-4o"


def test_registry_all_returns_snapshot():
    """all() returns a dict copy — mutating it does not affect the registry."""
    from pim_core.llm.registry import AgentModelRegistry
    reg = AgentModelRegistry()
    reg.set("content", "gemini-1.5-pro")
    snapshot = reg.all()
    assert snapshot == {"content": "gemini-1.5-pro"}
    snapshot["content"] = "changed"
    assert reg.get("content") == "gemini-1.5-pro"


def test_registry_remove_reverts_to_default():
    """remove() clears an agent's model; subsequent get() returns default."""
    from pim_core.llm.registry import AgentModelRegistry
    from pim_core.config import settings
    reg = AgentModelRegistry()
    reg.set("content", "gpt-4o")
    reg.remove("content")
    assert reg.get("content") == settings.claude_model
