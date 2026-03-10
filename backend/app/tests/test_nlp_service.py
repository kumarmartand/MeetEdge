from app.services import nlp_service


def test_summarize_transcript_basic():
    text = """
    Alice: I'll create the report by Friday. Bob: We should also sync the numbers.
    Carol: The project is on track. Dave: Let's follow up on the budget.
    """
    summary, key_points = nlp_service.summarize_transcript(text, max_sentences=2)
    assert isinstance(summary, str)
    assert summary != ""
    assert isinstance(key_points, list)


def test_extract_action_items_basic():
    text = """
    Alice: I'll create the report by Friday.
    Bob: We should also sync the numbers.
    Carol: The project is on track.
    Dave: Let's follow up on the budget.
    """
    attendees = [
        {"name": "Alice", "email": "alice@example.com"},
        {"name": "Bob", "email": "bob@example.com"},
    ]
    items = nlp_service.extract_action_items(text, attendees)
    # Should extract at least two action-like sentences
    assert any("report" in i["text"].lower() for i in items)
    assert any("sync" in i["text"].lower() or "follow up" in i["text"].lower() for i in items)
