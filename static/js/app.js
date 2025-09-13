// Global variables
const API_BASE_URL = '';

// DOM elements
const navTabs = document.querySelectorAll('.nav-tab');
const tabContents = document.querySelectorAll('.tab-content');
const analyzeForm = document.getElementById('analyzeForm');
const loading = document.getElementById('loading');
const results = document.getElementById('results');
const historyList = document.getElementById('historyList');

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
    initializeNavigation();
    initializeForm();
    loadHistory();
});

// Navigation functionality
function initializeNavigation() {
    navTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
}

function switchTab(tabName) {
    // Remove active class from all tabs and contents
    navTabs.forEach(tab => tab.classList.remove('active'));
    tabContents.forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab and content
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(tabName).classList.add('active');
    
    // Load content if needed
    if (tabName === 'history') {
        loadHistory();
    }
}

// Form functionality
function initializeForm() {
    analyzeForm.addEventListener('submit', function(e) {
        e.preventDefault();
        analyzeChallenge();
    });
}

async function analyzeChallenge() {
    const formData = new FormData(analyzeForm);
    const data = {
        title: formData.get('title'),
        description: formData.get('description'),
        objectives: formData.get('objectives') || null,
        constraints: formData.get('constraints') || null,
        language: 'pt-BR',
        persist: true
    };

    // Show loading
    showLoading();
    hideResults();

    try {
        const response = await fetch(`${API_BASE_URL}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        displayResults(result);
        showToast('Análise concluída com sucesso!', 'success');
        
        // Refresh history
        loadHistory();
        
    } catch (error) {
        console.error('Error analyzing challenge:', error);
        
        let errorMessage = 'Erro ao analisar desafio';
        if (error.message.includes('Chave da API OpenAI inválida')) {
            errorMessage = 'Chave da API OpenAI inválida. Verifique sua configuração.';
        } else if (error.message.includes('Limite de taxa excedido')) {
            errorMessage = 'Limite de taxa excedido. Tente novamente em alguns minutos.';
        } else if (error.message.includes('Cota da API OpenAI esgotada')) {
            errorMessage = 'Cota da API OpenAI esgotada. Adicione créditos à sua conta.';
        } else if (error.message) {
            errorMessage = error.message;
        }
        
        showToast(errorMessage, 'error');
    } finally {
        hideLoading();
    }
}

function displayResults(result) {
    const resultContent = results.querySelector('.result-content');
    
    resultContent.innerHTML = `
        <div class="result-card">
            <h4><i class="fas fa-info-circle"></i> Informações Gerais</h4>
            <p><strong>Título:</strong> ${result.title}</p>
            <p><strong>Dificuldade:</strong> <span class="difficulty-badge difficulty-${result.difficulty.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')}">${result.difficulty}</span></p>
            <div class="categories">
                ${result.categories.map(cat => `<span class="category-tag">${cat}</span>`).join('')}
            </div>
        </div>

        <div class="result-card">
            <h4><i class="fas fa-file-text"></i> Resumo</h4>
            <p>${result.summary}</p>
        </div>

        <div class="result-card">
            <h4><i class="fas fa-lightbulb"></i> Abordagem Recomendada</h4>
            <p><strong>${result.recommended_approach}</strong></p>
        </div>

        <div class="result-card">
            <h4><i class="fas fa-cogs"></i> Abordagens Disponíveis</h4>
            <div class="approaches">
                ${result.approaches.map(approach => `
                    <div class="approach-item">
                        <h5>${approach.name}</h5>
                        <p>${approach.description}</p>
                        <div class="complexity">
                            <div class="complexity-item">
                                <h6>Tempo</h6>
                                <span>${approach.time_complexity}</span>
                            </div>
                            <div class="complexity-item">
                                <h6>Espaço</h6>
                                <span>${approach.space_complexity}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>

        <div class="result-card">
            <h4><i class="fas fa-chart-line"></i> Complexidade Global</h4>
            <div class="complexity">
                <div class="complexity-item">
                    <h6>Tempo</h6>
                    <span>${result.complexity_time}</span>
                </div>
                <div class="complexity-item">
                    <h6>Espaço</h6>
                    <span>${result.complexity_space}</span>
                </div>
            </div>
        </div>

        ${result.assumptions ? `
            <div class="result-card">
                <h4><i class="fas fa-exclamation-triangle"></i> Suposições</h4>
                <p>${result.assumptions}</p>
            </div>
        ` : ''}

        ${result.references ? `
            <div class="result-card">
                <h4><i class="fas fa-book"></i> Referências</h4>
                <p>${result.references}</p>
            </div>
        ` : ''}
    `;

    showResults();
}

async function loadHistory() {
    historyList.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Carregando histórico...</p>
        </div>
    `;

    try {
        const response = await fetch(`${API_BASE_URL}/analyses?limit=20`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const analyses = await response.json();
        displayHistory(analyses);
        
    } catch (error) {
        console.error('Error loading history:', error);
        
        let errorMessage = 'Erro ao carregar histórico';
        if (error.message) {
            errorMessage = error.message;
        }
        
        historyList.innerHTML = `
            <div class="text-center">
                <p style="color: #f56565;">${errorMessage}</p>
                <button class="btn btn-primary" onclick="loadHistory()">
                    <i class="fas fa-refresh"></i> Tentar Novamente
                </button>
            </div>
        `;
    }
}

function displayHistory(analyses) {
    if (analyses.length === 0) {
        historyList.innerHTML = `
            <div class="text-center">
                <p style="color: #718096;">Nenhuma análise encontrada.</p>
                <p style="color: #a0aec0;">Analise seu primeiro desafio na aba "Analisar"!</p>
            </div>
        `;
        return;
    }

    historyList.innerHTML = analyses.map(analysis => `
        <div class="history-item" onclick="showAnalysisDetails(${analysis.id})">
            <h4>${analysis.title}</h4>
            <p>${analysis.summary.substring(0, 100)}${analysis.summary.length > 100 ? '...' : ''}</p>
            <div class="history-meta">
                <div>
                    <span class="difficulty-badge difficulty-${analysis.difficulty.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')}">${analysis.difficulty}</span>
                    <span class="category-tag">${analysis.categories[0] || 'Geral'}</span>
                </div>
                <span class="history-date">${formatDate(analysis.created_at)}</span>
            </div>
        </div>
    `).join('');
}

async function showAnalysisDetails(analysisId) {
    try {
        // Redirect to Django template view
        window.location.href = `/analysis/${analysisId}/`;
        
    } catch (error) {
        console.error('Error loading analysis details:', error);
        showToast('Erro ao carregar detalhes da análise', 'error');
    }
}

function showAnalysisModal(analysis) {
    // Create modal HTML
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3>Detalhes da Análise #${analysis.id}</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="result-card">
                    <h4>Informações Gerais</h4>
                    <p><strong>Título:</strong> ${analysis.title || 'N/A'}</p>
                    <p><strong>Dificuldade:</strong> <span class="difficulty-badge difficulty-${analysis.difficulty.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '')}">${analysis.difficulty}</span></p>
                    <p><strong>Categorias:</strong> ${analysis.categories.join(', ')}</p>
                </div>
                <div class="result-card">
                    <h4>Resumo</h4>
                    <p>${analysis.summary}</p>
                </div>
                <div class="result-card">
                    <h4>Abordagem Recomendada</h4>
                    <p><strong>${analysis.recommended_approach}</strong></p>
                </div>
                <div class="result-card">
                    <h4>Complexidade</h4>
                    <div class="complexity">
                        <div class="complexity-item">
                            <h6>Tempo</h6>
                            <span>${analysis.complexity_time}</span>
                        </div>
                        <div class="complexity-item">
                            <h6>Espaço</h6>
                            <span>${analysis.complexity_space}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    // Add modal styles
    const style = document.createElement('style');
    style.textContent = `
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background: white;
            border-radius: 15px;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
            margin: 20px;
        }
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 20px;
            border-bottom: 1px solid #e2e8f0;
        }
        .modal-header h3 {
            color: #4a5568;
        }
        .modal-close {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #a0aec0;
        }
        .modal-body {
            padding: 20px;
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(modal);
}

function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

// Utility functions
function clearForm() {
    analyzeForm.reset();
    hideResults();
}

function showLoading() {
    loading.classList.remove('hidden');
}

function hideLoading() {
    loading.classList.add('hidden');
}

function showResults() {
    results.classList.remove('hidden');
}

function hideResults() {
    results.classList.add('hidden');
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    const icon = toast.querySelector('.toast-icon');
    const messageEl = toast.querySelector('.toast-message');
    
    toast.className = `toast ${type}`;
    icon.className = `toast-icon fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}`;
    messageEl.textContent = message;
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Close modal when clicking outside
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        closeModal();
    }
});
