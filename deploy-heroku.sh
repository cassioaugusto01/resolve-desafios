#!/bin/bash

# Script de deploy para Heroku
# Uso: ./deploy-heroku.sh [APP_NAME]

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

# Verificar se o nome da app foi fornecido
if [ -z "$1" ]; then
    print_error "Nome da app é obrigatório!"
    echo "Uso: ./deploy-heroku.sh [APP_NAME]"
    echo "Exemplo: ./deploy-heroku.sh resolve-desafios-app"
    exit 1
fi

APP_NAME=$1

print_status "Iniciando deploy para Heroku..."
print_status "App Name: $APP_NAME"

# Verificar se Heroku CLI está instalado
if ! command -v heroku &> /dev/null; then
    print_error "Heroku CLI não está instalado!"
    echo "Instale em: https://devcenter.heroku.com/articles/heroku-cli"
    exit 1
fi

# Verificar se está logado no Heroku
if ! heroku auth:whoami &> /dev/null; then
    print_error "Você não está logado no Heroku!"
    echo "Execute: heroku login"
    exit 1
fi

# Verificar se a app existe
if heroku apps:info $APP_NAME &> /dev/null; then
    print_status "App já existe, usando app existente..."
else
    print_status "Criando nova app no Heroku..."
    heroku create $APP_NAME
fi

# Configurar buildpacks
print_status "Configurando buildpacks..."
heroku buildpacks:set heroku/python --app $APP_NAME

# Configurar variáveis de ambiente
print_status "Configurando variáveis de ambiente..."
heroku config:set DJANGO_SETTINGS_MODULE=resolve_desafios_web.settings_heroku --app $APP_NAME

# Solicitar chave secreta Django
print_warning "Configure a chave secreta Django:"
echo "Gere uma chave em: https://djecrety.ir/"
read -p "Digite a SECRET_KEY: " SECRET_KEY
heroku config:set SECRET_KEY="$SECRET_KEY" --app $APP_NAME

# Solicitar chave da API OpenAI
print_warning "Configure a chave da API OpenAI:"
read -p "Digite a OPENAI_API_KEY: " OPENAI_API_KEY
heroku config:set OPENAI_API_KEY="$OPENAI_API_KEY" --app $APP_NAME

# Adicionar addon do PostgreSQL
print_status "Adicionando PostgreSQL..."
heroku addons:create heroku-postgresql:mini --app $APP_NAME

# Fazer deploy
print_status "Fazendo deploy..."
git add .
git commit -m "Deploy para Heroku" || echo "Nenhuma mudança para commitar"

# Verificar se o remote heroku existe
if ! git remote | grep -q heroku; then
    print_status "Adicionando remote heroku..."
    heroku git:remote -a $APP_NAME
fi

# Push para Heroku
print_status "Enviando código para Heroku..."
git push heroku main

# Executar migrações
print_status "Executando migrações..."
heroku run python manage.py migrate --app $APP_NAME

# Coletar arquivos estáticos
print_status "Coletando arquivos estáticos..."
heroku run python manage.py collectstatic --noinput --app $APP_NAME

# Abrir app no navegador
print_status "Abrindo app no navegador..."
heroku open --app $APP_NAME

# Mostrar informações da app
print_status "Informações da app:"
heroku apps:info --app $APP_NAME

print_status "Deploy concluído com sucesso!"
print_status "URL da aplicação: https://$APP_NAME.herokuapp.com"

print_info "Comandos úteis:"
echo "  heroku logs --tail --app $APP_NAME    # Ver logs"
echo "  heroku run bash --app $APP_NAME       # Abrir shell"
echo "  heroku config --app $APP_NAME         # Ver variáveis"
echo "  heroku restart --app $APP_NAME        # Reiniciar app"
