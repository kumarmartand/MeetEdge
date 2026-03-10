"""Transcription service with pluggable adapters.

Supports:
- OpenAI Whisper (if `openai` package is installed and `OPENAI_API_KEY` is set in config)
- Google Cloud Speech-to-Text (if `google-cloud-speech` installed and credentials provided)

This module is intentionally defensive: adapters are attempted only when their
dependencies and credentials are present. For bilingual Hindi+English audio,
configure adapters to either auto-detect language (Whisper) or provide
`alternative_language_codes` for Google Speech-to-Text (e.g. ["hi-IN","en-US"]).

Usage:
    svc = TranscriptionService()
    result = svc.transcribe_audio("/path/to/audio.wav")

Result format:
    {
        "text": "full transcript text",
        "segments": [ {"start": 0.0, "end": 1.23, "text": "..."}, ... ]
    }

Note: This file only provides adapters/logic. Installing provider SDKs and
setting API keys / credentials is required for real transcription.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List, Dict, Optional
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class Segment:
    start: float
    end: float
    text: str


class TranscriptionService:
    def __init__(self):
        self.settings = settings

        # Decide available adapters
        self._openai_available = False
        self._google_available = False
        try:
            import openai  # type: ignore

            self.openai = openai
            if getattr(self.settings, "openai_api_key", None):
                self.openai.api_key = getattr(self.settings, "openai_api_key")
                self._openai_available = True
        except Exception:
            self.openai = None

        try:
            from google.cloud import speech_v1p1beta1 as speech  # type: ignore

            self.speech = speech
            # Google credentials may be provided by env var or via application default
            self._google_available = True
        except Exception:
            self.speech = None

    async def transcribe_audio(self, file_path: str, provider: Optional[str] = None, languages: Optional[List[str]] = None) -> Dict:
        """Transcribe an audio file.

        - file_path: local path to audio file
        - provider: optional override: "openai" or "google". If not provided,
          the service picks an available adapter (OpenAI preferred).
        - languages: optional list of language codes to hint the recognizer (eg ['hi-IN','en-US'])

        Returns dict with keys: text (str) and segments (list of dicts)
        """
        # Default languages: Hindi + English (India)
        languages = languages or ["hi-IN", "en-US"]

        # Prefer explicit provider when given
        if provider == "openai" and self._openai_available:
            return await self._transcribe_with_openai(file_path)
        if provider == "google" and self._google_available:
            return await self._transcribe_with_google(file_path, languages)

        # Automatic selection: openai -> google -> fallback
        if self._openai_available:
            return await self._transcribe_with_openai(file_path)
        if self._google_available:
            return await self._transcribe_with_google(file_path, languages)

        # Fallback: no provider available in this environment
        logger.warning("No transcription provider available; returning empty transcript")
        return {"text": "", "segments": []}

    async def _transcribe_with_openai(self, file_path: str) -> Dict:
        """Attempt to transcribe using OpenAI's Whisper model via openai package.

        This code is defensive because OpenAI SDK naming can change. If the
        environment doesn't support the call, the error will be logged and an
        empty result returned.
        """
        if not self.openai:
            return {"text": "", "segments": []}

        try:
            # The recommended modern call is openai.Audio.transcribe; older SDKs
            # used different signatures. We'll try the common pattern.
            with open(file_path, "rb") as fh:
                # Use 'whisper-1' which is multi-lingual and good for mixed audio
                resp = self.openai.Audio.transcribe("whisper-1", fh)

            # Response formats vary. Try to extract best-effort
            text = ""
            segments: List[Dict] = []
            if isinstance(resp, dict):
                text = resp.get("text") or resp.get("transcript") or ""
                segs = resp.get("segments") or []
                for s in segs:
                    segments.append({
                        "start": float(s.get("start", 0.0)),
                        "end": float(s.get("end", 0.0)),
                        "text": s.get("text", "")
                    })
            else:
                # Fallback: try string repr
                text = str(resp)

            return {"text": text, "segments": segments}
        except Exception as e:
            logger.exception("openai_transcription_failed", exc_info=e)
            return {"text": "", "segments": []}

    async def _transcribe_with_google(self, file_path: str, languages: List[str]) -> Dict:
        """Transcribe using Google Cloud Speech-to-Text.

        Uses alternative_language_codes to support mixed Hindi+English recognition.
        """
        if not self.speech:
            return {"text": "", "segments": []}

        try:
            client = self.speech.SpeechClient()

            # Read file bytes
            with open(file_path, "rb") as f:
                content = f.read()

            audio = self.speech.RecognitionAudio(content=content)

            # Primary language set to first provided, alternatives to others
            config = self.speech.RecognitionConfig(
                encoding=self.speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=languages[0] if languages else "hi-IN",
                alternative_language_codes=languages[1:] if len(languages) > 1 else None,
                enable_automatic_punctuation=True,
                enable_word_time_offsets=True,
            )

            # For longer files, use long_running_recognize
            operation = client.long_running_recognize(config=config, audio=audio)
            response = operation.result(timeout=600)

            full_text_parts: List[str] = []
            segments: List[Dict] = []
            for result in response.results:
                alt = result.alternatives[0]
                full_text_parts.append(alt.transcript)
                # Build time-aligned segments roughly per alternative
                start = 0.0
                end = 0.0
                if alt.words:
                    # take first and last word times
                    try:
                        start = float(alt.words[0].start_time.total_seconds())
                        end = float(alt.words[-1].end_time.total_seconds())
                    except Exception:
                        start = 0.0
                        end = 0.0
                segments.append({"start": start, "end": end, "text": alt.transcript})

            return {"text": "\n".join(full_text_parts), "segments": segments}
        except Exception as e:
            logger.exception("google_transcription_failed", exc_info=e)
            return {"text": "", "segments": []}
