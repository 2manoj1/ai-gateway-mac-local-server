from collections.abc import AsyncIterator
from typing import Any, TypedDict, cast

import httpx
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from src.core.config import Settings
from src.dependencies.auth import AuthContext
from src.schemas.agent import DirectMessageRequest
from src.schemas.openai import ChatCompletionRequest, ChatMessage
from src.services.openai_service import OpenAICompatibleService


class DirectMessageAgentState(TypedDict):
    message: str
    model: str | None
    auth_context: AuthContext


class CompletionApiAgentState(TypedDict):
    message: str
    model: str | None
    api_key: str


class DirectMessageAgentService:
    def __init__(
        self,
        *,
        settings: Settings,
        openai_service: OpenAICompatibleService,
    ) -> None:
        self._settings = settings
        self._openai_service = openai_service
        self._graph = self._build_graph()
        self._completion_api_graph = self._build_completion_api_graph()

    def _build_graph(
        self,
    ) -> CompiledStateGraph[
        DirectMessageAgentState,
        Any,
        DirectMessageAgentState,
        DirectMessageAgentState,
    ]:
        graph = StateGraph(DirectMessageAgentState)
        graph.add_node("llm", self._stream_llm)
        graph.add_edge(START, "llm")
        graph.add_edge("llm", END)
        return graph.compile()

    def _build_completion_api_graph(
        self,
    ) -> CompiledStateGraph[
        CompletionApiAgentState,
        Any,
        CompletionApiAgentState,
        CompletionApiAgentState,
    ]:
        graph = StateGraph(CompletionApiAgentState)
        graph.add_node("completion_api", self._stream_completion_api)
        graph.add_edge(START, "completion_api")
        graph.add_edge("completion_api", END)
        return graph.compile()

    async def _stream_llm(self, state: DirectMessageAgentState) -> dict[str, Any]:
        writer = get_stream_writer()

        async for chunk in self._openai_service.stream_chat_completion(
            request=ChatCompletionRequest(
                model=state["model"],
                messages=[
                    ChatMessage(
                        role="user",
                        content=state["message"],
                    )
                ],
                stream=True,
            ),
            auth_context=state["auth_context"],
        ):
            writer(chunk)

        return {}

    async def _stream_completion_api(
        self,
        state: CompletionApiAgentState,
    ) -> dict[str, Any]:
        writer = get_stream_writer()
        completion_url = (
            f"{self._settings.internal_gateway_base_url.rstrip('/')}"
            "/v1/chat/completions"
        )

        async with (
            httpx.AsyncClient(timeout=None) as client,
            client.stream(
                "POST",
                completion_url,
                headers={
                    "Authorization": f"Bearer {state['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": state["model"],
                    "stream": True,
                    "messages": [
                        {
                            "role": "user",
                            "content": state["message"],
                        }
                    ],
                },
            ) as response,
        ):
            response.raise_for_status()
            async for chunk in response.aiter_text():
                if chunk:
                    writer(chunk)

        return {}

    async def stream_direct_message(
        self,
        *,
        request: DirectMessageRequest,
        auth_context: AuthContext,
    ) -> AsyncIterator[str]:
        async for event in self._graph.astream(
            {
                "message": request.message,
                "model": request.model,
                "auth_context": auth_context,
            },
            stream_mode="custom",
        ):
            yield cast(str, event)

    async def stream_direct_message_via_completion_api(
        self,
        *,
        request: DirectMessageRequest,
        api_key: str,
    ) -> AsyncIterator[str]:
        async for event in self._completion_api_graph.astream(
            {
                "message": request.message,
                "model": request.model,
                "api_key": api_key,
            },
            stream_mode="custom",
        ):
            yield cast(str, event)
