from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph

from langchain_agent.config import Settings
from langchain_agent.gateway_langchain_model import GatewayChatModel


class LangChainAgentService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def create_direct_message_agent(self, model: str | None) -> CompiledStateGraph:
        llm = GatewayChatModel(
            settings=self._settings,
            model_name=model or self._settings.default_model,
        )
        return create_agent(
            model=llm,
            tools=[],
            system_prompt=(
                "You are a minimal smoke-test agent. Follow the user's instruction "
                "directly and keep the answer concise."
            ),
        )

    async def invoke_direct_message(
        self,
        *,
        message: str,
        model: str | None,
    ) -> str:
        agent = self.create_direct_message_agent(model)
        result = await agent.ainvoke(
            {
                "messages": [
                    HumanMessage(content=message),
                ],
            }
        )
        messages = result.get("messages", [])
        if not messages:
            return ""

        content = getattr(messages[-1], "content", "")
        return str(content or "")
