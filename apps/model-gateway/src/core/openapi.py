from typing import Any

OPENAPI_DESCRIPTION = """
**Manoj Mukherjee API Gateway - Local Mac Server for Research**

This is a local OpenAI-compatible API gateway for routing application traffic to Ollama.

⚠️ **Research Use**: This API gateway is designed for research and development
purposes on local Mac servers.

📧 **Contact**: For questions or to use this API gateway, please contact
Manoj Mukherjee.

---

## Authentication

- Clients must present a gateway API key via `X-API-Key` or an OpenAI-style
  `Authorization: Bearer <key>` header.
- Administrative routes are protected with `X-Admin-Secret` (set via
  `ADMIN_SECRET`).

## Streaming

- Send `stream=true` in the request body, or call
  `/v1/chat/completions?stream=true`.
- Streaming responses use Server-Sent Events with OpenAI-style
  `chat.completion.chunk` payloads and end with `data: [DONE]`.

## API Features

- **OpenAI Compatible**: Full compatibility with OpenAI SDK and API standards
- **Local Deployment**: Run entirely on your local Mac server
- **RAG Support**: Retrieval-Augmented Generation capabilities for enhanced responses
- **Agent Support**: Built-in support for AI agent workflows
- **Admin Management**: Comprehensive API key and configuration management

---

*Built with FastAPI and Ollama for local AI model serving.*
"""

OPENAPI_TAGS: list[dict[str, str]] = [
    {
        "name": "OpenAI Compatible",
        "description": "OpenAI SDK-compatible model and chat completion routes.",
    },
    {
        "name": "Health",
        "description": (
            "Operational health checks for local development and uptime probes."
        ),
    },
    {
        "name": "RAG",
        "description": (
            "Placeholder routes for future retrieval-augmented generation support."
        ),
    },
    {
        "name": "Admin",
        "description": (
            "Administrative routes for managing PostgreSQL-backed gateway API keys."
        ),
    },
]


def apply_openapi_customizations(openapi_schema: dict[str, Any]) -> dict[str, Any]:
    openapi_schema.setdefault("info", {})["contact"] = {
        "name": "Manoj Mukherjee - AI Gateway Local Mac Server for Research",
        "url": "https://github.com/2manoj1/ai-gateway-mac-local-server",
        "email": "info@manojmukherjee.co.in",
    }

    components = openapi_schema.setdefault("components", {})
    security_schemes = components.setdefault("securitySchemes", {})
    security_schemes["ApiKeyHeader"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key",
        "description": "Gateway API key for direct HTTP clients.",
    }
    security_schemes["BearerAuth"] = {
        "type": "http",
        "scheme": "bearer",
        "description": "OpenAI SDK-compatible bearer token.",
    }
    security_schemes["AdminSecret"] = {
        "type": "apiKey",
        "in": "header",
        "name": "X-Admin-Secret",
        "description": "Admin secret header for admin routes.",
    }

    openapi_schema["security"] = [
        {"BearerAuth": []},
        {"ApiKeyHeader": []},
    ]
    return openapi_schema
