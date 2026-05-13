from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable, RunnableLambda

from .parsers import parse_json_response
from .prompts import analysis_prompt_template


def create_analysis_chain(llm_provider) -> Runnable:
	"""
	Cria a chain de análise de currículos usando LCEL (LangChain Expression Language).
	"""
	chat_model = llm_provider.get_chat()
	try:
		chat_model = chat_model.bind(response_format={"type": "json_object"})
	except Exception:
		pass

	analysis_chain = (analysis_prompt_template | chat_model | StrOutputParser() | RunnableLambda(parse_json_response))
	return analysis_chain


def invoke_chain(chain: Runnable, input_data: dict[str, Any]) -> dict[str, Any]:
	"""
	Helper function para invocar uma chain com tratamento de erro.
	"""
	try:
		result = chain.invoke(input_data)
		return result
	except Exception as exc:
		raise RuntimeError(f"Falha ao invocar chain LCEL: {exc}") from exc
