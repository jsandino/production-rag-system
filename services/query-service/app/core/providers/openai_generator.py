from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.core.settings import get_settings


class OpenAIGenerator:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(
            model=model,
            api_key=get_settings().openai_api_key,
        )

    def generate(self, query: str, context: str) -> str:
        messages = [
            SystemMessage(content=(
                "You are a helpful assistant. Answer the user's question using "
                "only the context provided below. If the context does not contain "
                "enough information, say so.\n\n"
                f"Context:\n{context}"
            )),
            HumanMessage(content=query),
        ]
        return self.llm.invoke(messages).content
