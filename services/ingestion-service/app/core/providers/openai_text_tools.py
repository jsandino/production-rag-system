from typing import List
from openai import OpenAI
import tiktoken

from app.core.embedder import Embedder
from app.core.settings import get_settings
from app.core.chunker import Chunker
from app.core.tokenizer import Tokenizer


class OpenAITextTools:
    """
    OpenAI implementation of text-manipulation tools.

    The tokenization process is model-specific: tiktoken encodes text using
    OpenAI-style tokenization.  Thus, different embedding/LLM providers may
    tokenize differently.  So when chunking with this tokenizer, chunk boundaries
    become approximate to OpenAI semantics.

    So if only the embedding model was switched, embeddings (produced from tokenized
    chunks) would still work, but chunk sizes may be suboptimal, which may
    cause retrieval quality to degrade slightly.

    This is the reason for this class: to maintain high cohesion among implicitly
    dependent components, so that they can change together.
    """

    def __init__(self, tokenizer: Tokenizer, chunker: Chunker, embedder: Embedder):
        self.tokenizer = tokenizer
        self.chunker = chunker
        self.embedder = embedder

    @classmethod
    def create(cls) -> "OpenAITextTools":
        settings = get_settings()

        tokenizer = OpenAITokenizer()

        chunker = Chunker(tokenizer=tokenizer, max_tokens=512, overlap=50)

        embedder = OpenAIEmbedder(api_key=settings.openai_api_key)

        return cls(tokenizer=tokenizer, chunker=chunker, embedder=embedder)


class OpenAIEmbedder:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]


class OpenAITokenizer:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.encoding = tiktoken.encoding_for_model(model)

    def encode(self, text: str) -> list[int]:
        return self.encoding.encode(text)

    def decode(self, tokens: list[int]) -> str:
        return self.encoding.decode(tokens)
