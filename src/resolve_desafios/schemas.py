from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    facil = "Fácil"
    medio = "Médio"
    dificil = "Difícil"


class Approach(BaseModel):
    name: str = Field(..., description="Nome da abordagem/estratégia")
    algorithms: List[str] = Field(default_factory=list, description="Algoritmos/técnicas principais envolvidos")
    description: str = Field(..., description="Resumo da ideia e quando usar")
    steps: List[str] = Field(default_factory=list, description="Passos de alto nível para implementar")
    time_complexity: str = Field(..., description="Complexidade de tempo Big-O, ex: O(n log n)")
    space_complexity: str = Field(..., description="Complexidade de espaço Big-O")


class AnalysisOutput(BaseModel):
    title: str
    summary: str
    categories: List[str]
    difficulty: Difficulty
    approaches: List[Approach]
    recommended_approach: str = Field(..., description="Nome da abordagem recomendada")
    complexity_time: str = Field(..., description="Complexidade global recomendada (tempo)")
    complexity_space: str = Field(..., description="Complexidade global recomendada (espaço)")
    assumptions: Optional[str] = None
    constraints: Optional[str] = None
    references: Optional[str] = None


