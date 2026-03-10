"""LLM-based summarization and action-item extraction.

Uses OpenAI Chat API (if available) to produce a clean JSON response containing
an executive summary, key points, and extracted action items with optional
assignee emails. The implementation is defensive: if `openai` is not
installed or no API key is configured, `available` will be False and callers
should fall back to rule-based extraction.
"""
from __future__ import annotations

import json
import logging
from typing import List, Dict, Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class LLMService:
    def __init__(self):
        self._available = False
        self.openai = None
        self.api_key = getattr(settings, "openai_api_key", None) or None
        try:
            import openai  # type: ignore
            self.openai = openai
            # prefer explicit settings key, else rely on env-based key
            if self.api_key:
                self.openai.api_key = self.api_key
            elif getattr(self.openai, "api_key", None):
                # already set
                pass
            else:
                # not configured
                self.api_key = None

            if self.api_key or getattr(self.openai, "api_key", None):
                self._available = True
        except Exception:
            self.openai = None
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def _clean_response(self, content: str) -> str:
        # Remove code fences if present
        if content.startswith("```") and content.endswith("```"):
            # strip triple backticks and optional language hint
            parts = content.split("\n")
            if parts[0].startswith("```"):
                parts = parts[1:]
            if parts and parts[-1].strip().endswith("```"):
                parts = parts[:-1]
            return "\n".join(parts).strip()
        return content.strip()

    def summarize_and_extract(self, transcript: str, attendees: Optional[List[Dict[str, str]]] = None) -> Optional[Dict]:
        """Return dict with keys: summary (str), key_points (list[str]), action_items (list[dict]).

        Each action item dict should include 'text' and optional 'assignee_email'.
        """
        if not self.available:
            return None

        attendees = attendees or []

        # Guard long transcripts by truncation to avoid excessive token usage.
        # For most LLMs, sending > 40k chars is impractical. We'll cap at 24000 chars
        # and prefer the start+end to preserve context.
        max_chars = 24000
        if len(transcript) > max_chars:
            head = transcript[:12000]
            tail = transcript[-12000:]
            transcript_to_send = head + "\n\n[...omitted middle of transcript...]\n\n" + tail
        else:
            transcript_to_send = transcript

        # Build a prompt that asks for JSON output
        attendee_lines = "\n".join(f"- {a.get('name') or ''} <{a.get('email') or ''}>" for a in attendees)

        system_prompt = (
            "You are an assistant that reads meeting transcripts and produces an executive "
            "summary, a short list of key points, and a list of action items. Output MUST be valid JSON. "
            "Do not include any commentary outside of the JSON object."
        )

        user_prompt = (
            f"Transcript:\n\n{transcript_to_send}\n\n"
            "Attendees:\n"
            f"{attendee_lines}\n\n"
            "Return a JSON object with the following keys:\n"
            "- summary: a concise (2-4 sentence) executive summary.\n"
            "- key_points: an array of 3-6 short bullet points summarizing main decisions.\n"
            "- action_items: an array of objects, each with 'text' (string) and 'assignee_email' (string|null).\n"
            "Extract action items conservatively (only tasks that are clearly actionable). If no assignee can be determined, set assignee_email to null."
        )

        try:
            # Use chat completion
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]

            # Prefer a capable but cost-effective model if available
            model = "gpt-3.5-turbo"
            try:
                # If the OpenAI package exposes capability to check model availability, choose gpt-4 when configured.
                if getattr(self.openai, "api_key", None) and getattr(settings, "use_gpt4", False):
                    model = "gpt-4"
            except Exception:
                pass

            resp = self.openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.0,
                max_tokens=800,
            )

            content = resp.choices[0].message.content if resp and resp.choices else ""
            content = self._clean_response(content)

            # Attempt to parse JSON from the content
            parsed = json.loads(content)

            # Normalize fields
            summary = parsed.get("summary", "")
            key_points = parsed.get("key_points", []) or []
            action_items = parsed.get("action_items", []) or []

            # Ensure action items are normalized to {'text', 'assignee_email'}
            normalized_actions = []
            for ai in action_items:
                if isinstance(ai, dict):
                    text = ai.get("text") or ai.get("action") or ""
                    assignee = ai.get("assignee_email") if ai.get("assignee_email") else None
                    normalized_actions.append({"text": text, "assignee_email": assignee})

            return {"summary": summary, "key_points": key_points, "action_items": normalized_actions}
        except Exception as e:
            logger.exception("llm_summarize_failed", exc_info=e)
            return None
