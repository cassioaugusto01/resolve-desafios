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
        self.demo_mode = self.settings.openai_api_key == "sk-test-key-for-demo"
        
        if not self.settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY não definido. Configure o arquivo .env (veja env.example)."
            )

        if not self.demo_mode:
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
        if self.demo_mode:
            # Modo de demonstração com dados simulados
            return self._get_demo_result(title, description)

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

    def _get_demo_result(self, title: str, description: str):
        """Get demo result for demonstration mode"""
        # Determinar dificuldade baseada no título
        if "two sum" in title.lower() or "soma" in title.lower():
            difficulty = "FACIL"
            categories = ["Arrays", "Hash Table"]
            approaches = [
                {
                    'name': "Hash Map (Complement Lookup)",
                    'algorithms': ["Hash Map", "Two Pointers"],
                    'description': "Use um hash map para armazenar números já visitados e procurar pelo complemento.",
                    'steps': ["Iterar pelo array", "Para cada número, calcular complemento", "Verificar se complemento existe no hash map", "Se sim, retornar índices", "Se não, adicionar número atual ao hash map"],
                    'time_complexity': "O(n)",
                    'space_complexity': "O(n)"
                },
                {
                    'name': "Two Pointers (Array Ordenado)",
                    'algorithms': ["Two Pointers", "Sorting"],
                    'description': "Ordenar o array e usar dois ponteiros para encontrar a soma.",
                    'steps': ["Ordenar o array", "Usar dois ponteiros (início e fim)", "Comparar soma com target", "Ajustar ponteiros baseado na comparação"],
                    'time_complexity': "O(n log n)",
                    'space_complexity': "O(1)"
                }
            ]
            recommended_approach = "Hash Map (Complement Lookup)"
            complexity_time = "O(n)"
            complexity_space = "O(n)"
            summary = "Problema clássico de busca em array. A solução com hash map é mais eficiente em tempo, enquanto two pointers é mais eficiente em espaço."
            
        elif "binary search" in title.lower() or "busca binária" in title.lower():
            difficulty = "MEDIO"
            categories = ["Binary Search", "Arrays"]
            approaches = [
                {
                    'name': "Binary Search",
                    'algorithms': ["Binary Search"],
                    'description': "Busca binária clássica em array ordenado.",
                    'steps': ["Definir left e right", "Calcular middle", "Comparar com target", "Ajustar boundaries", "Repetir até encontrar"],
                    'time_complexity': "O(log n)",
                    'space_complexity': "O(1)"
                }
            ]
            recommended_approach = "Binary Search"
            complexity_time = "O(log n)"
            complexity_space = "O(1)"
            summary = "Busca binária em array ordenado. Algoritmo eficiente que reduz o espaço de busca pela metade a cada iteração."
            
        else:
            difficulty = "MEDIO"
            categories = ["Algorithms", "Data Structures"]
            approaches = [
                {
                    'name': "Análise Geral",
                    'algorithms': ["Problem Analysis", "Algorithm Design"],
                    'description': "Análise geral do problema para determinar a melhor abordagem.",
                    'steps': ["Analisar requisitos", "Identificar padrões", "Escolher estrutura de dados", "Implementar solução", "Otimizar se necessário"],
                    'time_complexity': "O(n)",
                    'space_complexity': "O(n)"
                }
            ]
            recommended_approach = "Análise Geral"
            complexity_time = "O(n)"
            complexity_space = "O(n)"
            summary = f"Análise do problema '{title}'. {description[:100]}..."

        return {
            'title': title,
            'summary': summary,
            'categories': categories,
            'difficulty': difficulty,
            'approaches': approaches,
            'recommended_approach': recommended_approach,
            'complexity_time': complexity_time,
            'complexity_space': complexity_space,
            'assumptions': "Modo de demonstração - resultados simulados",
            'references': "Este é um resultado de demonstração. Configure uma chave da API OpenAI válida para resultados reais."
        }
