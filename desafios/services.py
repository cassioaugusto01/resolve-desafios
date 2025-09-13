"""
Serviços Django para análise de desafios - Arquitetura MTV
"""

import sys
from pathlib import Path
from typing import Dict, Any, List
from django.conf import settings

# Adiciona o diretório src ao path para importar os módulos
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from resolve_desafios.llm_adapter import OpenAILLMAdapter
from resolve_desafios.taxonomy_adapter import FileTaxonomyAdapter
from .models import Challenge, Analysis


class AnalysisService:
    """Serviço Django para análise de desafios"""
    
    def __init__(self):
        self.llm_adapter = OpenAILLMAdapter()
        self.taxonomy_adapter = FileTaxonomyAdapter()
    
    def analyze_challenge(self, title: str, description: str, objectives: str = None, 
                         constraints: str = None, language: str = 'pt-BR') -> Analysis:
        """Analisa um desafio e retorna um objeto Analysis"""
        
        # Carregar taxonomia
        taxonomy_summary = self.taxonomy_adapter.summarize_taxonomy_for_prompt()
        
        # Analisar com LLM
        result = self.llm_adapter.analyze_challenge(
            title=title,
            description=description,
            objectives=objectives or "",
            constraints=constraints or "",
            taxonomy_summary=taxonomy_summary
        )
        
        # Criar ou buscar desafio
        challenge, created = Challenge.objects.get_or_create(
            title=title,
            defaults={
                'description': description,
                'objectives': objectives,
                'constraints': constraints
            }
        )
        
        # Criar análise
        analysis = Analysis.objects.create(
            challenge=challenge,
            title=result['title'],
            difficulty=result['difficulty'],
            categories=result['categories'],
            summary=result['summary'],
            approaches=result['approaches'],
            recommended_approach=result['recommended_approach'],
            complexity_time=result['complexity_time'],
            complexity_space=result['complexity_space'],
            assumptions=result['assumptions'],
            references=result['references'],
            model="gpt-4o-mini",  # TODO: Get from settings
            raw_data=result
        )
        
        return analysis
    
    def get_analysis(self, analysis_id: int) -> Analysis:
        """Obtém uma análise por ID"""
        try:
            return Analysis.objects.get(id=analysis_id)
        except Analysis.DoesNotExist:
            return None
    
    def list_analyses(self, limit: int = 10) -> List[Analysis]:
        """Lista análises recentes"""
        return Analysis.objects.select_related('challenge').order_by('-created_at')[:limit]
    
    def get_analyses_by_challenge(self, challenge_id: int) -> List[Analysis]:
        """Obtém análises por desafio"""
        return Analysis.objects.filter(challenge_id=challenge_id).order_by('-created_at')
    
    def search_analyses(self, query: str) -> List[Analysis]:
        """Busca análises por título ou resumo"""
        from django.db import models
        return Analysis.objects.filter(
            models.Q(challenge__title__icontains=query) | 
            models.Q(summary__icontains=query)
        ).order_by('-created_at')
