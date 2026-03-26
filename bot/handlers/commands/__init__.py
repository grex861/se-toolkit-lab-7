"""Command handlers - pure functions that return text responses."""


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
    # Placeholder - will be implemented in Task 2
    return "Backend status: OK (placeholder)"


def handle_labs() -> str:
    """Handle /labs command.
    
    Returns:
        List of available labs.
    """
    # Placeholder - will be implemented in Task 2
    return "Available labs: (placeholder - will fetch from backend)"


def handle_scores(lab_name: str = "") -> str:
    """Handle /scores command.
    
    Args:
        lab_name: The lab to get scores for.
        
    Returns:
        Scores information.
    """
    # Placeholder - will be implemented in Task 2
    if lab_name:
        return f"Scores for {lab_name}: (placeholder - will fetch from backend)"
    return "Please specify a lab name, e.g., /scores lab-04"
