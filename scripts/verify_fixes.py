import asyncio
import json
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add backend to path
BACKEND_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, BACKEND_PATH)

async def test_summary_logic():
    print("Starting verification of summary generation logic...")
    
    # Mocking OpenAI module
    mock_openai = MagicMock()
    mock_client = MagicMock()
    mock_openai.OpenAI.return_value = mock_client
    sys.modules["openai"] = mock_openai
    
    # Mocking chat completions
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps({
            "summary": "This is a test summary.",
            "key_points": ["Point 1", "Point 2"],
            "action_items": [{"text": "Fix the bug", "assignee_email": "test@example.com"}]
        })))
    ]
    mock_client.chat.completions.create.return_value = mock_response
    
    from app.services.llm_service import LLMService
    llm = LLMService()
    llm._available = True # Force available for test
    
    res = llm.summarize_and_extract("Test transcript", [{"name": "Test User", "email": "test@example.com"}])
    
    assert res is not None
    assert res["summary"] == "This is a test summary."
    assert len(res["key_points"]) == 2
    assert res["action_items"][0]["text"] == "Fix the bug"
    print("✅ LLMService OpenAI v1.x integration verified.")

    # Mocking BotService and Recall.ai
    from app.services.bot_service import BotService
    bot_service = BotService()
    bot_service.api_key = "test-key"
    
    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        # Mock 1: empty transcript, Mock 2: empty, Mock 3: success
        mock_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"transcripts": []}, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: {"transcripts": []}, raise_for_status=lambda: None),
            MagicMock(status_code=200, json=lambda: {"transcripts": [{"words": [{"text": "Hello"}]}]}, raise_for_status=lambda: None)
        ]
        
        # Mock database session and post-processing to avoid actual DB hits
        with patch("app.services.bot_service.AsyncSessionLocal"), \
             patch("app.services.bot_service.update"), \
             patch("app.services.bot_service.select"), \
             patch("app.services.bot_service.send_summary_notification"):
            
            # Run fetch_transcript
            # We use a short sleep in the real code, we can patch asyncio.sleep to speed up test
            with patch("asyncio.sleep", new_callable=AsyncMock):
                # We expect this to call get 3 times
                await bot_service.fetch_transcript("bot_123", 1)
                
                assert mock_get.call_count == 3
                print("✅ BotService transcript retry logic verified.")

    print("Verification complete.")

if __name__ == "__main__":
    asyncio.run(test_summary_logic())
