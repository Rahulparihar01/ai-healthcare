def extract_summary(extracted_data: dict) -> str:
    """
    Extracts the clinical summary from the structured JSON output.
    """
    return extracted_data.get("summary", "AI processing completed without summary.")
