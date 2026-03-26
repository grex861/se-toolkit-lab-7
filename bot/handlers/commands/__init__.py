"""Command handlers - pure functions that return text responses."""

from services.api_client import get_items, get_pass_rates, APIError


def handle_start() -> str:
    """Handle /start command.

    Returns:
        Welcome message.
    """
    return "Welcome to the LMS Bot! I can help you check system health, browse labs, view scores, and answer questions. Use /help to see all available commands."


def handle_help() -> str:
    """Handle /help command.

    Returns:
        List of available commands.
    """
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend system status
/labs - List available labs
/scores <lab> - View scores for a specific lab

You can also ask questions in plain language, and I'll try to help!"""


def handle_health() -> str:
    """Handle /health command.

    Returns:
        Backend health status.
    """
    try:
        items = get_items()
        item_count = len(items)
        return f"Backend is healthy. {item_count} items available."
    except APIError as e:
        return f"Backend error: {str(e)}"


def handle_labs() -> str:
    """Handle /labs command.

    Returns:
        List of available labs.
    """
    try:
        items = get_items()
        # Filter for labs (items with type 'lab' or items that have tasks)
        labs = [item for item in items if item.get("type") == "lab" or "tasks" in item]

        if not labs:
            return "No labs found in the backend."

        lines = ["Available labs:"]
        for lab in labs:
            # API uses 'title' field for the lab name
            lab_name = lab.get("title", lab.get("name", "Unknown Lab"))
            # Format: "- Lab 01 — Products, Architecture & Roles"
            lines.append(f"- {lab_name}")

        return "\n".join(lines)
    except APIError as e:
        return f"Backend error: {str(e)}"


def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command.

    Args:
        lab_name: The lab to get scores for.

    Returns:
        Scores information.
    """
    if not lab_name:
        return "Please specify a lab name, e.g., /scores lab-04"

    try:
        pass_rates = get_pass_rates(lab_name)

        if not pass_rates:
            return f"No pass rate data found for lab '{lab_name}'. The lab may not exist or has no submissions."

        # Format the lab name for display (e.g., "lab-04" -> "Lab 04")
        display_lab = lab_name.replace("lab-", "Lab ").replace("-", " ").title()
        if display_lab.startswith("Lab "):
            # Ensure proper formatting like "Lab 04" not "Lab 4"
            parts = display_lab.split()
            if len(parts) >= 2 and parts[1].isdigit():
                parts[1] = parts[1].zfill(2)
            display_lab = " ".join(parts)

        lines = [f"Pass rates for {display_lab}:"]
        for task in pass_rates:
            task_name = task.get("task_name", task.get("name", "Unknown Task"))
            pass_rate = task.get("pass_rate", 0)
            attempts = task.get("attempts", 0)
            # Format: "- Repository Setup: 92.1% (187 attempts)"
            lines.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")

        return "\n".join(lines)
    except APIError as e:
        return f"Backend error: {str(e)}"
