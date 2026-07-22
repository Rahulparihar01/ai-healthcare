def generate_timeline_payload(event_type: str, category: str, summary: str) -> dict:
    """
    Formats the exact title and summary strings based on the record type.
    """
    title = f"Analyzed {event_type}: {category}"
    if not summary:
        summary = "AI processing completed without a specific summary."
        
    return {
        "title": title,
        "summary": summary
    }
