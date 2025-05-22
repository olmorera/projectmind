# projectmind/utils/agent_evaluator.py

def is_prompt_successful(result: dict) -> bool:
    """Basic evaluator for agent output."""
    if not isinstance(result, dict):
        return False
    if result.get("success") is False:
        return False
    output = result.get("output", "")
    return isinstance(output, str) and len(output.strip()) > 10  # puedes afinar esta regla
