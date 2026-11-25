"""Shared bits for scenario specs. Not a scenario."""

from makebp.dsl import M, slack


def alert(name: str, text: str) -> dict:
    """Slack module used only as the notify step of an error handler.

    The compiler replaces the key, so the key here is a placeholder.
    """
    return M("alert_step", "slack:CreateMessage", name, text, mapper=slack(text))
