import logging
from functools import lru_cache

from django.conf import settings

logger = logging.getLogger(__name__)


class LLMConfigurationError(RuntimeError):
	"""Raised when the LLM provider is not properly configured."""


class LLMProvider:
	"""Singleton-ish factory for chat models and embeddings."""

	def __init__(self, temperature: float = 0.2) -> None:
		self.api_key = settings.OPENAI_API_KEY
		self.chat_model = settings.OPENAI_MODEL
		self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
		self.temperature = temperature

	def _ensure_key(self) -> None:
		if not self.api_key:
			raise LLMConfigurationError(
				"OPENAI_API_KEY não configurada. Defina no .env"
			)

	def get_chat(self):
		self._ensure_key()
		from langchain_openai import ChatOpenAI

		return ChatOpenAI(
			api_key=self.api_key,
			model=self.chat_model,
			temperature=self.temperature,
		)

	def get_embeddings(self):
		self._ensure_key()
		from langchain_openai import OpenAIEmbeddings
		return OpenAIEmbeddings(api_key=self.api_key, model=self.embedding_model)


@lru_cache(maxsize=1)
def get_default_provider() -> LLMProvider:
	return LLMProvider()
