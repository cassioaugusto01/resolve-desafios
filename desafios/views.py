"""
Views Django para análise de desafios - Arquitetura MTV
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import json

from .models import Challenge, Analysis
from .services import AnalysisService


def index(request):
    """Página principal"""
    return render(request, 'desafios/index.html')


@csrf_exempt
@require_http_methods(["POST"])
def analyze_challenge(request):
    """Analisar desafio via AJAX"""
    try:
        # Log environment variables
        import os
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        print(f"WEB SERVER - API Key loaded: {api_key[:20] if api_key else 'None'}...")
        
        data = json.loads(request.body)
        print(f"WEB SERVER - Request data received")
        
        # Test LLM adapter directly
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        from resolve_desafios.llm_adapter import OpenAILLMAdapter
        llm_adapter = OpenAILLMAdapter()
        print(f"WEB SERVER - LLM Adapter created successfully")
        
        service = AnalysisService()
        print(f"WEB SERVER - Service created successfully")
        
        analysis = service.analyze_challenge(
            title=data.get('title'),
            description=data.get('description'),
            objectives=data.get('objectives'),
            constraints=data.get('constraints'),
            language=data.get('language', 'pt-BR')
        )
        print(f"WEB SERVER - Analysis completed successfully")
        
        return JsonResponse({
            'id': analysis.id,
            'title': analysis.title,
            'summary': analysis.summary,
            'categories': analysis.get_categories_list(),
            'difficulty': analysis.get_difficulty_display(),
            'approaches': analysis.get_approaches_list(),
            'recommended_approach': analysis.recommended_approach,
            'recommended_solution': analysis.recommended_solution,
            'complexity_time': analysis.complexity_time,
            'complexity_space': analysis.complexity_space,
            'assumptions': analysis.assumptions,
            'references': analysis.references,
            'created_at': analysis.created_at.isoformat(),
        })
        
    except Exception as e:
        error_msg = str(e)
        
        if "401" in error_msg or "AuthenticationError" in error_msg:
            return JsonResponse(
                {'error': 'Chave da API OpenAI inválida. Verifique sua configuração.'},
                status=400
            )
        elif "429" in error_msg:
            return JsonResponse(
                {'error': 'Limite de taxa excedido. Tente novamente em alguns minutos.'},
                status=429
            )
        elif "quota" in error_msg.lower():
            return JsonResponse(
                {'error': 'Cota da API OpenAI esgotada. Adicione créditos à sua conta.'},
                status=402
            )
        else:
            return JsonResponse(
                {'error': f'Erro interno: {error_msg}'},
                status=500
            )


@require_http_methods(["GET"])
def list_analyses(request):
    """Listar análises via AJAX"""
    try:
        limit = int(request.GET.get('limit', 10))
        service = AnalysisService()
        analyses = service.list_analyses(limit)
        
        return JsonResponse([
            {
                'id': analysis.id,
                'challenge_id': analysis.challenge.id,
                'title': analysis.title,
                'difficulty': analysis.get_difficulty_display(),
                'categories': analysis.get_categories_list(),
                'summary': analysis.summary,
                'created_at': analysis.created_at.isoformat(),
            }
            for analysis in analyses
        ], safe=False)
        
    except Exception as e:
        return JsonResponse(
            {'error': f'Erro ao carregar análises: {str(e)}'},
            status=500
        )


@require_http_methods(["GET"])
def get_analysis(request, analysis_id):
    """Obter análise específica via AJAX"""
    try:
        service = AnalysisService()
        analysis = service.get_analysis(analysis_id)
        
        if not analysis:
            return JsonResponse({'error': 'Análise não encontrada'}, status=404)
        
        return JsonResponse({
            'id': analysis.id,
            'challenge_id': analysis.challenge.id,
            'title': analysis.title,
            'difficulty': analysis.get_difficulty_display(),
            'categories': analysis.get_categories_list(),
            'summary': analysis.summary,
            'recommended_approach': analysis.recommended_approach,
            'recommended_solution': analysis.recommended_solution,
            'complexity_time': analysis.complexity_time,
            'complexity_space': analysis.complexity_space,
            'assumptions': analysis.assumptions,
            'references': analysis.references,
            'created_at': analysis.created_at.isoformat(),
        })
        
    except Exception as e:
        return JsonResponse(
            {'error': f'Erro ao carregar análise: {str(e)}'},
            status=500
        )


def analysis_detail(request, analysis_id):
    """Página de detalhes da análise"""
    try:
        analysis = get_object_or_404(Analysis, id=analysis_id)
        return render(request, 'desafios/analysis_result.html', {
            'analysis': analysis
        })
        
    except Exception as e:
        return render(request, 'desafios/error.html', {
            'error': 'Erro ao carregar análise',
            'message': str(e)
        })


def challenge_list(request):
    """Lista de desafios"""
    challenges = Challenge.objects.all().order_by('-created_at')
    paginator = Paginator(challenges, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'desafios/challenge_list.html', {
        'page_obj': page_obj
    })


def challenge_detail(request, challenge_id):
    """Detalhes de um desafio"""
    challenge = get_object_or_404(Challenge, id=challenge_id)
    analyses = Analysis.objects.filter(challenge=challenge).order_by('-created_at')
    
    return render(request, 'desafios/challenge_detail.html', {
        'challenge': challenge,
        'analyses': analyses
    })


def search(request):
    """Busca de análises"""
    query = request.GET.get('q', '')
    analyses = []
    
    if query:
        service = AnalysisService()
        analyses = service.search_analyses(query)
    
    return render(request, 'desafios/search.html', {
        'query': query,
        'analyses': analyses
    })


@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    return JsonResponse({'status': 'healthy', 'service': 'resolve-desafios-django'})