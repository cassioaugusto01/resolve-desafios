#!/bin/bash

# Script de gerenciamento da aplicação Resolve Desafios
# Uso: ./manage-app.sh [comando]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    print_error "Não execute este script como root!"
    exit 1
fi

# Função para mostrar ajuda
show_help() {
    echo "Script de gerenciamento da aplicação Resolve Desafios"
    echo ""
    echo "Uso: ./manage-app.sh [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  start       - Iniciar a aplicação"
    echo "  stop        - Parar a aplicação"
    echo "  restart     - Reiniciar a aplicação"
    echo "  status      - Verificar status da aplicação"
    echo "  logs        - Ver logs da aplicação"
    echo "  deploy      - Fazer deploy da aplicação"
    echo "  backup      - Fazer backup do banco de dados"
    echo "  update      - Atualizar dependências"
    echo "  migrate     - Executar migrações do banco"
    echo "  collectstatic - Coletar arquivos estáticos"
    echo "  shell       - Abrir shell Django"
    echo "  help        - Mostrar esta ajuda"
}

# Função para iniciar a aplicação
start_app() {
    print_status "Iniciando aplicação..."
    sudo systemctl start resolve-desafios
    sudo systemctl start nginx
    print_status "Aplicação iniciada!"
}

# Função para parar a aplicação
stop_app() {
    print_status "Parando aplicação..."
    sudo systemctl stop resolve-desafios
    sudo systemctl stop nginx
    print_status "Aplicação parada!"
}

# Função para reiniciar a aplicação
restart_app() {
    print_status "Reiniciando aplicação..."
    sudo systemctl restart resolve-desafios
    sudo systemctl restart nginx
    print_status "Aplicação reiniciada!"
}

# Função para verificar status
check_status() {
    print_info "Status da aplicação:"
    echo ""
    echo "=== Resolve Desafios Service ==="
    sudo systemctl status resolve-desafios --no-pager
    echo ""
    echo "=== Nginx Service ==="
    sudo systemctl status nginx --no-pager
    echo ""
    echo "=== Portas em uso ==="
    sudo netstat -tlnp | grep -E ':(80|8000)'
}

# Função para ver logs
show_logs() {
    print_info "Logs da aplicação (Ctrl+C para sair):"
    sudo journalctl -u resolve-desafios -f
}

# Função para fazer deploy
deploy_app() {
    print_status "Fazendo deploy da aplicação..."
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Atualizar dependências
    pip install -r requirements.txt
    
    # Executar migrações
    python manage.py migrate
    
    # Coletar arquivos estáticos
    python manage.py collectstatic --noinput
    
    # Reiniciar aplicação
    restart_app
    
    print_status "Deploy concluído!"
}

# Função para backup
backup_db() {
    print_status "Fazendo backup do banco de dados..."
    
    DATE=$(date +%Y%m%d_%H%M%S)
    BACKUP_DIR="/opt/backups"
    DB_FILE="db.sqlite3"
    
    mkdir -p $BACKUP_DIR
    
    if [ -f "$DB_FILE" ]; then
        cp "$DB_FILE" "$BACKUP_DIR/db_backup_$DATE.sqlite3"
        print_status "Backup criado: $BACKUP_DIR/db_backup_$DATE.sqlite3"
    else
        print_error "Arquivo de banco de dados não encontrado!"
    fi
}

# Função para atualizar dependências
update_deps() {
    print_status "Atualizando dependências..."
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_status "Dependências atualizadas!"
}

# Função para executar migrações
run_migrations() {
    print_status "Executando migrações..."
    
    source venv/bin/activate
    python manage.py migrate
    
    print_status "Migrações executadas!"
}

# Função para coletar arquivos estáticos
collect_static() {
    print_status "Coletando arquivos estáticos..."
    
    source venv/bin/activate
    python manage.py collectstatic --noinput
    
    print_status "Arquivos estáticos coletados!"
}

# Função para abrir shell Django
open_shell() {
    print_status "Abrindo shell Django..."
    
    source venv/bin/activate
    python manage.py shell
}

# Processar comando
case "${1:-help}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs
        ;;
    deploy)
        deploy_app
        ;;
    backup)
        backup_db
        ;;
    update)
        update_deps
        ;;
    migrate)
        run_migrations
        ;;
    collectstatic)
        collect_static
        ;;
    shell)
        open_shell
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Comando inválido: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
