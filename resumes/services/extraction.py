import logging
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import IO

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
	"""Erro ao extrair texto de um arquivo."""


class BaseExtractor(ABC):
	"""Interface para extratores de texto de arquivos."""

	extensions: tuple[str, ...] = ()

	@abstractmethod
	def extract(self, file_obj: IO[bytes] | str | os.PathLike) -> str:
		"""Extrai texto do arquivo."""
		pass


class PdfExtractor(BaseExtractor):
	"""Extrai texto de arquivos PDF."""

	extensions = (".pdf",)

	def extract(self, file_obj) -> str:
		"""
		Tenta extrair texto do PDF usando pypdf.
		Se falhar, tenta com pdfminer como fallback.
		"""
		try:
			from pypdf import PdfReader
		except ImportError as exc:
			raise ExtractionError("pypdf não instalado") from exc

		try:
			reader = PdfReader(file_obj)
			pages_text = [page.extract_text() or "" for page in reader.pages]
			text = "\n".join(pages_text).strip()
			if text:
				return text
		except Exception as exc:
			logger.warning("pypdf falhou: %s, tentando pdfminer", exc)

		try:
			from pdfminer.high_level import extract_text
			if hasattr(file_obj, "seek"):
				file_obj.seek(0)
			return (extract_text(file_obj) or "").strip()
		except Exception as exc:
			raise ExtractionError(f"Falha ao extrair PDF: {exc}") from exc


class DocxExtractor(BaseExtractor):
	"""Extrai texto de arquivos Word (.docx)."""

	extensions = (".docx",)

	def extract(self, file_obj) -> str:
		"""Extrai texto de todos os parágrafos do documento."""
		try:
			from docx import Document
		except ImportError as exc:
			raise ExtractionError("python-docx não instalado") from exc

		try:
			doc = Document(file_obj)
			paragraphs = [p.text for p in doc.paragraphs if p.text]
			return "\n".join(paragraphs).strip()
		except Exception as exc:
			raise ExtractionError(f"Falha ao extrair DOCX: {exc}") from exc


class TxtExtractor(BaseExtractor):
	"""Extrai texto de arquivos .txt."""

	extensions = (".txt",)

	def extract(self, file_obj) -> str:
		"""Lê o arquivo de texto simples."""
		try:
			if hasattr(file_obj, "read"):
				data = file_obj.read()
				if isinstance(data, bytes):
					data = data.decode("utf-8", errors="ignore")
				return data.strip()
			return Path(file_obj).read_text(encoding="utf-8", errors="ignore").strip()

		except Exception as exc:  # noqa: BLE001
			raise ExtractionError(f"Falha ao ler TXT: {exc}") from exc


class TextExtractorService:
	"""
    Serviço de extração de texto de currículos.
    Suporta PDF, DOCX e TXT.
	Detecta automaticamente o tipo de arquivo e usa o extrator correto.
	"""

	def __init__(self) -> None:
		"""Inicializa com os extratores padrão (PDF, DOCX, TXT)."""
		self._extractors = [
			PdfExtractor(),
			DocxExtractor(),
			TxtExtractor()
		]

	def _find_extractor(self, extension: str) -> BaseExtractor:
		"""
		Encontra o extrator correto para a extensão do arquivo.
		"""
		ext = extension.lower()
		for extractor in self._extractors:
			if ext in extractor.extensions:
				return extractor
		raise ExtractionError(f"Extensão não suportada: {extension}")

	def extract_from_path(self, path: str | os.PathLike) -> str:
		"""
		Extrai texto de um arquivo no disco.
		"""
		path = Path(path)
		extractor = self._find_extractor(path.suffix)

		with open(path, "rb") as file:
			return extractor.extract(file)

	def extract_from_uploaded(self, uploaded_file) -> str:
		"""
		Extrai texto de um arquivo do uploaded
		"""
		filename = getattr(uploaded_file, "name", "") or ""
		extension = Path(filename).suffix
		extractor = self._find_extractor(extension)

		if hasattr(uploaded_file, "open"):
			uploaded_file.open("rb")

		try:
			return extractor.extract(uploaded_file)
		finally:
			if hasattr(uploaded_file, "close"):
				try:
					uploaded_file.close()
				except Exception:
					pass
