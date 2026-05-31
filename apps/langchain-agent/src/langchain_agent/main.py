from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from httpx import HTTPError

from langchain_agent.agent import LangChainAgentService
from langchain_agent.config import Settings, get_settings
from langchain_agent.gateway_client import GatewayClient
from langchain_agent.schemas import DirectMessageRequest, DirectMessageResponse


def get_gateway_client(
    settings: Annotated[Settings, Depends(get_settings)],
) -> GatewayClient:
    return GatewayClient(settings)


def get_agent_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> LangChainAgentService:
    return LangChainAgentService(settings)


app = FastAPI(
    title="External LangChain Agent Smoke App",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/httpx/direct-message")
async def httpx_direct_message(
    request: DirectMessageRequest,
    client: Annotated[GatewayClient, Depends(get_gateway_client)],
) -> DirectMessageResponse:
    try:
        response = await client.chat_completion(
            message=request.message,
            model=request.model,
        )
    except HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Production gateway request failed",
        ) from exc

    return DirectMessageResponse(response=response)


@app.post("/httpx/direct-message/stream")
async def httpx_direct_message_stream(
    request: DirectMessageRequest,
    client: Annotated[GatewayClient, Depends(get_gateway_client)],
) -> StreamingResponse:
    return StreamingResponse(
        client.stream_chat_completion(
            message=request.message,
            model=request.model,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.post("/langchain/agent/direct-message")
async def langchain_agent_direct_message(
    request: DirectMessageRequest,
    agent_service: Annotated[LangChainAgentService, Depends(get_agent_service)],
) -> DirectMessageResponse:
    try:
        response = await agent_service.invoke_direct_message(
            message=request.message,
            model=request.model,
        )
    except HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Production gateway request failed",
        ) from exc

    return DirectMessageResponse(response=response)
