import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Mock core dependencies that might be missing in this environment
mock_structlog = MagicMock()
sys.modules["structlog"] = mock_structlog

mock_openai = MagicMock()
sys.modules["openai"] = mock_openai

mock_sqlalchemy = MagicMock()
sys.modules["sqlalchemy"] = mock_sqlalchemy
sys.modules["sqlalchemy.orm"] = mock_sqlalchemy
sys.modules["sqlalchemy.ext.asyncio"] = mock_sqlalchemy

mock_httpx = MagicMock()
sys.modules["httpx"] = mock_httpx

# Add backend to path
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, BACKEND_PATH)

# Stub out app.core.database and app.core.config before importing services
sys.modules["app.core.database"] = MagicMock()
sys.modules["app.core.config"] = MagicMock()
sys.modules["app.tasks.notification_tasks"] = MagicMock()
sys.modules["app.services.nps_service"] = MagicMock() # typo in original code? nlp_service?
sys.modules["app.services.nlp_service"] = MagicMock()
sys.modules["app.services.transcription_service"] = MagicMock()

async def test_summary_logic():
    print("Starting isolated verification of summary generation logic...")
    
    # Setup OpenAI Client Mock
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client
    
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "summary": "This is a test summary.",
            "key_points": ["Point 1", "Point 2"],
            "action_items": [{"text": "Fix the bug", "assignee_email": "test@example.com"}]
        })))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    # Import Service
    from app.services.llm_service import LLMService
    llm = LLMService()
    llm._available = True 
    
    res = llm.summarize_and_extract("Test transcript", [{"name": "Test User", "email": "test@example.com"}])
    
    if res and res["summary"] == "This is a test summary.":
        print("✅ LLMService OpenAI v1.x integration verified.")
    else:
        print("❌ LLMService verification failed.")
        return

    # Test BotService Retry Logic (Modularly)
    from app.services.bot_service import BotService
    bot_service = BotService()
    bot_service.api_key = "test-key"
    bot_service.headers = {}
    
    with patch("httpx.AsyncClient", new_callable=MagicMock) as mock_client_class:
        mock_client_instance = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client_instance
        
        # Mock 1: empty transcript, Mock 2: empty, Mock 3: success
        mock_client_instance.get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"transcripts": []}, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: {"transcripts": []}, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: {"transcripts": [{"words": [{"text": "Hello"}]}]}, raise_for_status=lambda: None)
        ]
        
        with patch("asyncio.sleep", new_callable=AsyncMock):
            # We mock the parts that use DB to avoid import errors
            bot_service.fetch_transcript = AsyncMock(side_effect=bot_service.fetch_transcript)
            
            try:
                # This will run the loop in fetch_transcript
                await bot_service.fetch_transcript("bot_123", 1)
            except Exception:
                # Might fail on DB call later, but we check get call count
                pass
            
            if mock_client_instance.get.call_count == 3:
                print("✅ BotService transcript retry logic verified.")
            else:
                print(f"❌ BotService verification failed (calls: {mock_client_instance.get.call_count})")

    print("Verification complete.")

if __name__ == "__main__":
    asyncio.run(test_summary_logic())
