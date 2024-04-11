"""Embedders for the RAG module."""
from abc import ABC, abstractmethod
from typing import ClassVar, Generic, Optional, TypeVar

from pydantic import BaseModel

from .types import BaseEmbeddingParams

BaseEmbeddingT = TypeVar("BaseEmbeddingT", bound=BaseModel)


class BaseEmbedder(BaseModel, Generic[BaseEmbeddingT], ABC):
    api_key: ClassVar[Optional[str]] = None
    base_url: ClassVar[Optional[str]] = None
    embedding_params: ClassVar[BaseEmbeddingParams] = BaseEmbeddingParams(
        model="text-embedding-ada-002"
    )

    @abstractmethod
    def embed(self, input: list[str]) -> list[BaseEmbeddingT]:
        """A call to the embedder with a single input"""
        ...  # pragma: no cover

    @abstractmethod
    async def embed_async(self, input: list[str]) -> list[BaseEmbeddingT]:
        """Asynchronously call the embedder with a single input"""
        ...  # pragma: no cover
