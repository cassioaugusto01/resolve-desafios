#!/bin/bash

# Script de deploy para Google Cloud Platform - Compute Engine (VM)
# Uso: ./deploy.sh [PROJECT_ID] [VM_NAME] [ZONE]

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Verificar parâmetros
if [ -z "$1" ] || [ -z "$2" ]; then
    print_error "Parâmetros obrigatórios!"
    echo "Uso: ./deploy.sh [PROJECT_ID] [VM_NAME] [ZONE]"
    echo "Exemplo: ./deploy.sh my-project-123 resolve-desafios-vm us-central1-a"
    exit 1
fi

PROJECT_ID=$1
VM_NAME=$2
ZONE=${3:-"us-central1-a"}

print_status "Iniciando deploy para Google Cloud Platform - Compute Engine..."
print_status "Project ID: $PROJECT_ID"
print_status "VM Name: $VM_NAME"
print_status "Zone: $ZONE"

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    print_error "Google Cloud SDK não está instalado!"
    echo "Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Configurar projeto
print_status "Configurando projeto..."
gcloud config set project $PROJECT_ID

# Habilitar APIs necessárias
print_status "Habilitando APIs necessárias..."
gcloud services enable compute.googleapis.com

# Criar VM se não existir
print_status "Verificando se a VM existe..."
if ! gcloud compute instances describe $VM_NAME --zone=$ZONE &> /dev/null; then
    print_status "Criando VM..."
    gcloud compute instances create $VM_NAME \
        --zone=$ZONE \
        --machine-type=e2-medium \
        --image-family=ubuntu-2004-lts \
        --image-project=ubuntu-os-cloud \
        --boot-disk-size=20GB \
        --boot-disk-type=pd-standard \
        --tags=http-server,https-server \
        --metadata-from-file startup-script=startup-script.sh
else
    print_status "VM já existe, pulando criação..."
fi

# Aguardar VM estar pronta
print_status "Aguardando VM estar pronta..."
sleep 30

# Obter IP externo da VM
EXTERNAL_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)')
print_status "IP externo da VM: $EXTERNAL_IP"

# Criar arquivo de configuração para upload
print_status "Preparando arquivos para upload..."
tar -czf resolve-desafios.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='db.sqlite3' \
    --exclude='staticfiles' \
    .

# Upload dos arquivos para a VM
print_status "Enviando arquivos para a VM..."
gcloud compute scp resolve-desafios.tar.gz $VM_NAME:~/ --zone=$ZONE

# Executar comandos na VM
print_status "Configurando aplicação na VM..."
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    # Extrair arquivos
    cd ~/
    tar -xzf resolve-desafios.tar.gz
    rm resolve-desafios.tar.gz
    
    # Atualizar sistema
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv nginx
    
    # Criar ambiente virtual
    python3 -m venv venv
    source venv/bin/activate
    
    # Instalar dependências
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Configurar variáveis de ambiente
    echo 'export DJANGO_SETTINGS_MODULE=resolve_desafios_web.settings_production' >> ~/.bashrc
    echo 'export SECRET_KEY=your-secret-key-here' >> ~/.bashrc
    echo 'export OPENAI_API_KEY=your-openai-api-key-here' >> ~/.bashrc
    
    # Executar migrações
    python manage.py migrate
    
    # Coletar arquivos estáticos
    python manage.py collectstatic --noinput
    
    # Configurar Gunicorn
    sudo tee /etc/systemd/system/resolve-desafios.service > /dev/null <<EOF
[Unit]
Description=Resolve Desafios Django App
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu
Environment=DJANGO_SETTINGS_MODULE=resolve_desafios_web.settings_production
Environment=SECRET_KEY=your-secret-key-here
Environment=OPENAI_API_KEY=your-openai-api-key-here
ExecStart=/home/ubuntu/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 resolve_desafios_web.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

    # Configurar Nginx
    sudo tee /etc/nginx/sites-available/resolve-desafios > /dev/null <<EOF
server {
    listen 80;
    server_name $EXTERNAL_IP;
    
    location /static/ {
        alias /home/ubuntu/staticfiles/;
    }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    # Ativar site
    sudo ln -sf /etc/nginx/sites-available/resolve-desafios /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Reiniciar serviços
    sudo systemctl daemon-reload
    sudo systemctl enable resolve-desafios
    sudo systemctl start resolve-desafios
    sudo systemctl restart nginx
"

# Limpar arquivo temporário
rm resolve-desafios.tar.gz

print_status "Deploy concluído com sucesso!"
print_status "URL da aplicação: http://$EXTERNAL_IP"

print_warning "IMPORTANTE: Configure as variáveis de ambiente na VM:"
echo "1. SSH na VM: gcloud compute ssh $VM_NAME --zone=$ZONE"
echo "2. Edite o arquivo: sudo nano /etc/systemd/system/resolve-desafios.service"
echo "3. Configure as variáveis:"
echo "   - SECRET_KEY: Gere uma chave secreta Django"
echo "   - OPENAI_API_KEY: Sua chave da API OpenAI"
echo "4. Reinicie o serviço: sudo systemctl restart resolve-desafios"

print_status "Para verificar logs:"
echo "sudo journalctl -u resolve-desafios -f"
