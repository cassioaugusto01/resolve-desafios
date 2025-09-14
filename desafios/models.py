"""
Modelos Django para Resolve Desafios
"""

from django.db import models
from django.utils import timezone
import json


class Challenge(models.Model):
    """Modelo para desafios de programação"""
    
    DIFFICULTY_CHOICES = [
        ('FACIL', 'Fácil'),
        ('MEDIO', 'Médio'),
        ('DIFICIL', 'Difícil'),
    ]
    
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descrição")
    objectives = models.TextField(blank=True, null=True, verbose_name="Objetivos")
    constraints = models.TextField(blank=True, null=True, verbose_name="Restrições")
    language = models.CharField(max_length=10, default='pt-BR', verbose_name="Idioma")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Desafio"
        verbose_name_plural = "Desafios"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title


class Analysis(models.Model):
    """Modelo para análises de desafios"""
    
    DIFFICULTY_CHOICES = [
        ('FACIL', 'Fácil'),
        ('MEDIO', 'Médio'),
        ('DIFICIL', 'Difícil'),
    ]
    
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name='analyses', verbose_name="Desafio")
    title = models.CharField(max_length=200, verbose_name="Título")
    summary = models.TextField(verbose_name="Resumo")
    categories = models.JSONField(default=list, verbose_name="Categorias")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, verbose_name="Dificuldade")
    approaches = models.JSONField(default=list, verbose_name="Abordagens")
    recommended_approach = models.CharField(max_length=200, verbose_name="Abordagem Recomendada")
    recommended_solution = models.TextField(default="Solução não disponível", verbose_name="Solução Recomendada")
    complexity_time = models.CharField(max_length=50, verbose_name="Complexidade de Tempo")
    complexity_space = models.CharField(max_length=50, verbose_name="Complexidade de Espaço")
    assumptions = models.TextField(blank=True, null=True, verbose_name="Suposições")
    references = models.TextField(blank=True, null=True, verbose_name="Referências")
    model = models.CharField(max_length=100, default='gpt-4o-mini', verbose_name="Modelo")
    raw_data = models.JSONField(default=dict, verbose_name="Dados Brutos")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    
    class Meta:
        verbose_name = "Análise"
        verbose_name_plural = "Análises"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Análise: {self.title}"
    
    def get_difficulty_display_color(self):
        """Retorna a cor CSS para a dificuldade"""
        colors = {
            'FACIL': 'facil',
            'MEDIO': 'medio', 
            'DIFICIL': 'dificil'
        }
        return colors.get(self.difficulty, 'medio')
    
    def get_approaches_list(self):
        """Retorna lista de abordagens formatada"""
        if isinstance(self.approaches, str):
            try:
                return json.loads(self.approaches)
            except:
                return []
        return self.approaches or []
    
    def get_categories_list(self):
        """Retorna lista de categorias formatada"""
        if isinstance(self.categories, str):
            try:
                return json.loads(self.categories)
            except:
                return []
        return self.categories or []