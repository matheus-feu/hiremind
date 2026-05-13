import logging
import os
from functools import lru_cache
from typing import Any

from django.conf import settings

from .llm import get_default_provider

logger = logging.getLogger(__name__)


class VectorStoreService:
	"""Wraps a persistent Chroma collection used for RAG over resumes."""

	COLLECTION_NAME = "hiremind_resumes"

	def __init__(self) -> None:
		self.provider = get_default_provider()
		self.persist_dir = settings.CHROMA_PERSIST_DIR
		self.collection_name = self.COLLECTION_NAME
		os.makedirs(self.persist_dir, exist_ok=True)
		self._store = None

	def _get_store(self):
		if self._store is None:
			from langchain_chroma import Chroma

			self._store = Chroma(
				collection_name=self.collection_name,
				embedding_function=self.provider.get_embeddings(),
				persist_directory=self.persist_dir,
			)
		return self._store

	@staticmethod
	def _split(text: str, chunk_size: int = 1000, chunk_overlap: int = 150) -> list[str]:
		from langchain_text_splitters import RecursiveCharacterTextSplitter

		splitter = RecursiveCharacterTextSplitter(
			chunk_size=chunk_size,
			chunk_overlap=chunk_overlap,
			separators=["\n\n", "\n", ". ", " ", ""],
		)
		return splitter.split_text(text)

	def index_resume(self, resume_id: str, text: str, metadata: dict | None = None) -> int:
		"""Index a resume's text into the vector store. Returns chunks indexed."""
		if not text.strip():
			return 0
		store = self._get_store()

		try:
			store.delete(where={"resume_id": str(resume_id)})
		except Exception as exc:
			logger.debug(f"delete por resume_id falhou (provavelmente não existe), ignorando: {exc}")

		chunks = self._split(text)
		metadatas = [
			{"resume_id": str(resume_id), "chunk": i, **(metadata or {})}
			for i, _ in enumerate(chunks)
		]
		ids = [f"{resume_id}-{i}" for i in range(len(chunks))]
		store.add_texts(texts=chunks, metadatas=metadatas, ids=ids)
		return len(chunks)

	def retrieve_for_job(self, job_text: str, resume_id: str | None = None, k: int = 6) -> list[str]:
		"""RAG: get top-k chunks most relevant to the job description."""
		store = self._get_store()
		kwargs: dict[str, Any] = {"k": k}
		if resume_id:
			kwargs["filter"] = {"resume_id": str(resume_id)}
		docs = store.similarity_search(job_text, **kwargs)
		return [d.page_content for d in docs]

	def remove_resume(self, resume_id: str) -> None:
		try:
			self._get_store().delete(where={"resume_id": str(resume_id)})
		except Exception as exc:
			logger.warning(f"Falha ao remover resume {resume_id} do vector store: {exc}")


@lru_cache(maxsize=1)
def get_default_vector_store() -> VectorStoreService:
	return VectorStoreService()
