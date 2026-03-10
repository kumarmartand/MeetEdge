import re
import structlog
from typing import List, Dict, Tuple

logger = structlog.get_logger()


def _split_sentences(text: str) -> List[str]:
    # Very small sentence splitter using punctuation
    sentences = re.split(r'(?<=[\.|\?|\!])\s+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def summarize_transcript(transcript: str, max_sentences: int = 2) -> Tuple[str, List[str]]:
    """Create a lightweight executive summary from the transcript.

    Returns (summary, key_points)
    """
    if not transcript:
        return ("", [])

    sentences = _split_sentences(transcript)
    if not sentences:
        return ("", [])

    # Heuristic: pick the longest sentences as representative "key" sentences
    ranked = sorted(sentences, key=lambda s: len(s.split()), reverse=True)
    key_points = ranked[: max_sentences * 2]

    # Compose a short summary by joining the top `max_sentences` longest sentences
    summary = " ".join(ranked[:max_sentences])
    # Trim to reasonable length
    if len(summary) > 2000:
        summary = summary[:2000].rsplit(" ", 1)[0] + "..."

    logger.info("nlp_summary_generated", summary_len=len(summary), key_points=len(key_points))
    return (summary, key_points)


def extract_action_items(transcript: str, attendees: List[Dict[str, str]] | None = None) -> List[Dict[str, str]]:
    """Extract action-item-like sentences from transcript.

    attendees: optional list of dicts with 'name' and 'email' keys to help assign items.
    Returns list of {text: str, assignee_email: str|None}
    """
    if not transcript:
        return []

    attendees = attendees or []
    sentences = _split_sentences(transcript)
    action_keywords = re.compile(r"\b(will|should|need to|need|todo|to do|action|assign|follow up|follow-up|please|let's|we'll|i'll)\b", re.I)

    found = []
    seen = set()
    for s in sentences:
        if action_keywords.search(s):
            normalized = re.sub(r"\s+", " ", s).strip()
            if normalized in seen:
                continue
            seen.add(normalized)

            assignee = None
            lower = normalized.lower()
            # try match attendee email or name
            for a in attendees:
                name = (a.get("name") or "").lower()
                email = (a.get("email") or "").lower()
                if name and name in lower:
                    assignee = a.get("email")
                    break
                if email and email in lower:
                    assignee = a.get("email")
                    break

            found.append({"text": normalized, "assignee_email": assignee})

    logger.info("nlp_action_items_extracted", count=len(found))
    return found
