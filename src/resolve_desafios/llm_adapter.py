"""
LLM Adapter - Implementação para análise com OpenAI
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from .config import get_settings


class OpenAILLMAdapter:
    """Adapter para OpenAI LLM operations"""

    def __init__(self):
        self.settings = get_settings()
        
        if not self.settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY não definido. Configure o arquivo .env (veja env.example)."
            )

        self.llm = ChatOpenAI(
            api_key=self.settings.openai_api_key,
            model=self.settings.openai_model,
            temperature=0.2,
        )

    def analyze_challenge(
        self,
        title: str,
        description: str,
        objectives: str,
        constraints: str,
        taxonomy_summary: str,
    ):
        """Analyze a challenge using OpenAI"""
        from .schemas import AnalysisOutput

        structured_llm = self.llm.with_structured_output(AnalysisOutput)

        system_msg = SystemMessage(content=self._build_system_prompt(taxonomy_summary))
        human_msg = HumanMessage(
            content=self._build_human_prompt(
                title=title,
                description=description,
                objectives=objectives,
                constraints=constraints,
            )
        )

        result: AnalysisOutput = structured_llm.invoke([system_msg, human_msg])

        # Convert to simple dict structure
        approaches = [
            {
                'name': approach.name,
                'algorithms': approach.algorithms,
                'description': approach.description,
                'steps': approach.steps,
                'time_complexity': approach.time_complexity,
                'space_complexity': approach.space_complexity,
            }
            for approach in result.approaches
        ]

        return {
            'title': result.title,
            'summary': result.summary,
            'categories': result.categories,
            'difficulty': result.difficulty,
            'approaches': approaches,
            'recommended_approach': result.recommended_approach,
            'complexity_time': result.complexity_time,
            'complexity_space': result.complexity_space,
            'assumptions': result.assumptions,
            'references': result.references,
        }

    def _build_system_prompt(self, taxonomy_summary: str) -> str:
        """Build system prompt for LLM"""
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

    def _build_human_prompt(
        self,
        title: str,
        description: str,
        objectives: str,
        constraints: str,
    ) -> str:
        """Build human prompt for LLM"""
        return (
            f"Título: {title}\n"
            f"Enunciado:\n{description}\n\n"
            f"Objetivos/Metas:\n{objectives or '-'}\n\n"
            f"Restrições/Observações:\n{constraints or '-'}\n\n"
            "Produza a saída estruturada seguindo o esquema fornecido."
        )

