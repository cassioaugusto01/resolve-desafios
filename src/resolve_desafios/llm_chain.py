from typing import Dict, List

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from .config import get_settings
from .schemas import AnalysisOutput
from .taxonomy import summarize_taxonomy_for_prompt


def build_system_prompt(taxonomy_summary: str) -> str:
    return (
        "Você é um assistente especialista em algoritmos e estruturas de dados, ajudando candidatos a entrevistas e competidores de programação.\n"
        "Tarefas: classificar o desafio por categoria e dificuldade, listar abordagens plausíveis, avaliar complexidades em notação Big O e recomendar a melhor estratégia.\n"
        "Responda sempre em PT-BR, de forma concisa porém completa.\n\n"
        "Regras:\n"
        "- Use categorias e técnicas inspiradas em fontes canônicas (McDowell, Halim, Skiena, EPI, LeetCode).\n"
        "- Seja específico na análise de complexidade (tempo e espaço).\n"
        "- Considere restrições e objetivos antes de recomendar.\n"
        "- Mencione suposições quando necessário.\n\n"
        "Taxonomia (resumo):\n"
        f"{taxonomy_summary}\n"
    )


def build_human_prompt(
    *,
    title: str,
    description: str,
    objectives: str,
    constraints: str,
) -> str:
    return (
        f"Título: {title}\n"
        f"Enunciado:\n{description}\n\n"
        f"Objetivos/Metas:\n{objectives or '-'}\n\n"
        f"Restrições/Observações:\n{constraints or '-'}\n\n"
        "Produza a saída estruturada seguindo o esquema fornecido."
    )


def run_structured_analysis(
    *, title: str, description: str, objectives: str = "", constraints: str = "", taxonomy_summary: str
) -> AnalysisOutput:
    settings = get_settings()
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY não definido. Configure o arquivo .env (veja env.example)."
        )

    llm = ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.openai_model,
        temperature=0.2,
    )

    structured_llm = llm.with_structured_output(AnalysisOutput)

    system_msg = SystemMessage(content=build_system_prompt(taxonomy_summary))
    human_msg = HumanMessage(
        content=build_human_prompt(
            title=title, description=description, objectives=objectives, constraints=constraints
        )
    )

    result: AnalysisOutput = structured_llm.invoke([system_msg, human_msg])
    return result


