"""
Schemas para análise de desafios
"""

from pydantic import BaseModel, Field
from typing import List, Literal


class Approach(BaseModel):
    """Abordagem para resolver o desafio"""
    name: str = Field(description="Nome da abordagem")
    algorithms: List[str] = Field(description="Algoritmos utilizados")
    description: str = Field(description="Descrição da abordagem")
    steps: List[str] = Field(description="Passos para implementação")
    time_complexity: str = Field(description="Complexidade temporal")
    space_complexity: str = Field(description="Complexidade espacial")


class AnalysisOutput(BaseModel):
    """Saída estruturada da análise"""
    title: str = Field(description="Título do desafio")
    summary: str = Field(description="Resumo da análise")
    categories: List[str] = Field(description="Categorias do desafio")
    difficulty: Literal["FACIL", "MEDIO", "DIFICIL"] = Field(description="Nível de dificuldade")
    approaches: List[Approach] = Field(description="Abordagens possíveis")
    recommended_approach: str = Field(description="Abordagem recomendada")
    recommended_solution: str = Field(description="Solução recomendada com código e explicação detalhada")
    complexity_time: str = Field(description="Complexidade temporal geral")
    complexity_space: str = Field(description="Complexidade espacial geral")
    assumptions: str = Field(description="Suposições feitas")
    references: str = Field(description="Referências completas incluindo: teoria do algoritmo, links da Wikipedia, livros da bibliografia clássica de algoritmos, e outras fontes relevantes para estudo aprofundado")
