def check_safety(text):
    """
    Checks for urgent keywords and phrases to prioritize support tickets.
    """
    urgent_keywords = [
        "urgent", "emergency", "broken", "security", "hack", 
        "leak", "lost card", "unauthorized", "fraud", "block",
        "stolen", "immediately", "asap", "not my charge", "danger"
    ]
    
    text_lower = text.lower()
    found_keywords = [word for word in urgent_keywords if word in text_lower]
    
    if found_keywords:
        return "🛑 Escalated", f"Urgent indicators: {', '.join(found_keywords)}"
    
    return "✅ Standard", "No immediate safety risk detected."