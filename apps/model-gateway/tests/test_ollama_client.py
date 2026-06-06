import pytest
from src.clients.ollama import OllamaClient, OllamaClientError
from src.core.config import get_settings


@pytest.mark.asyncio
async def test_chat_slot_rejects_when_concurrency_limit_is_exhausted() -> None:
    settings = get_settings().model_copy(
        update={
            "ollama_chat_concurrency_limit": 1,
            "ollama_chat_acquire_timeout_seconds": 0.01,
        },
    )
    client = OllamaClient(settings)

    try:
        async with client._chat_slot():
            with pytest.raises(OllamaClientError) as exc_info:
                async with client._chat_slot():
                    pass
    finally:
        await client.close()

    assert exc_info.value.status_code == 429
    assert exc_info.value.code == "chat_concurrency_limit"
