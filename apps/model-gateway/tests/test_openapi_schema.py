from src.main import app


def test_openapi_schema_documents_auth_and_streaming() -> None:
    schema = app.openapi()

    security_schemes = schema["components"]["securitySchemes"]
    assert "BearerAuth" in security_schemes
    assert "ApiKeyHeader" in security_schemes

    chat_completion = schema["paths"]["/v1/chat/completions"]["post"]
    assert chat_completion["summary"] == "Create a chat completion"
    assert chat_completion["operationId"] == "createChatCompletion"
    assert "text/event-stream" in chat_completion["responses"]["200"]["content"]

    tags = {tag["name"]: tag["description"] for tag in schema["tags"]}
    assert "OpenAI Compatible" in tags
    assert "OpenAI SDK-compatible" in tags["OpenAI Compatible"]
    assert "Admin" in tags
    assert "/admin/api-keys" in schema["paths"]
    assert "/admin/api-keys/{api_key_id}" in schema["paths"]
