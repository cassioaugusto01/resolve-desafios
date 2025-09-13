# Deploy na Google Cloud Platform - Compute Engine

Este guia explica como fazer o deploy da aplicação Resolve Desafios em uma máquina virtual (Compute Engine) na Google Cloud Platform.

## 📋 Pré-requisitos

1. **Conta Google Cloud Platform** com billing habilitado
2. **Google Cloud SDK** instalado localmente
3. **Projeto GCP** criado
4. **Chave da API OpenAI** válida

## 🚀 Deploy Automático

### 1. Configurar Google Cloud SDK

```bash
# Instalar Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Fazer login
gcloud auth login

# Configurar projeto
gcloud config set project SEU_PROJECT_ID
```

### 2. Executar Deploy

```bash
# Tornar o script executável
chmod +x deploy.sh

# Executar deploy
./deploy.sh SEU_PROJECT_ID NOME_DA_VM [ZONA]

# Exemplo:
./deploy.sh my-project-123 resolve-desafios-vm us-central1-a
```

### 3. Configurar Variáveis de Ambiente

Após o deploy, configure as variáveis de ambiente na VM:

```bash
# SSH na VM
gcloud compute ssh NOME_DA_VM --zone=ZONA

# Editar arquivo de serviço
sudo nano /etc/systemd/system/resolve-desafios.service

# Configurar as variáveis:
# Environment=SECRET_KEY=sua-chave-secreta-django
# Environment=OPENAI_API_KEY=sua-chave-openai

# Reiniciar serviço
sudo systemctl restart resolve-desafios
```

## 🔧 Deploy Manual

Se preferir fazer o deploy manualmente:

### 1. Criar VM

```bash
gcloud compute instances create resolve-desafios-vm \
    --zone=us-central1-a \
    --machine-type=e2-medium \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=20GB \
    --boot-disk-type=pd-standard \
    --tags=http-server,https-server
```

### 2. Configurar VM

```bash
# SSH na VM
gcloud compute ssh resolve-desafios-vm --zone=us-central1-a

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependências
sudo apt install -y python3 python3-pip python3-venv nginx git

# Criar usuário para aplicação
sudo useradd -m -s /bin/bash appuser
```

### 3. Deploy da Aplicação

```bash
# Clonar repositório
git clone https://github.com/seu-usuario/resolve-desafios.git
cd resolve-desafios

# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
export DJANGO_SETTINGS_MODULE=resolve_desafios_web.settings_production
export SECRET_KEY=sua-chave-secreta
export OPENAI_API_KEY=sua-chave-openai

# Executar migrações
python manage.py migrate

# Coletar arquivos estáticos
python manage.py collectstatic --noinput
```

### 4. Configurar Serviços

```bash
# Copiar arquivos de configuração
sudo cp resolve-desafios.service /etc/systemd/system/
sudo cp nginx.conf /etc/nginx/sites-available/resolve-desafios

# Ativar site Nginx
sudo ln -s /etc/nginx/sites-available/resolve-desafios /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default

# Iniciar serviços
sudo systemctl daemon-reload
sudo systemctl enable resolve-desafios
sudo systemctl start resolve-desafios
sudo systemctl restart nginx
```

## 🛠️ Gerenciamento da Aplicação

Use o script de gerenciamento para operações comuns:

```bash
# Tornar executável
chmod +x manage-app.sh

# Comandos disponíveis
./manage-app.sh start      # Iniciar aplicação
./manage-app.sh stop       # Parar aplicação
./manage-app.sh restart    # Reiniciar aplicação
./manage-app.sh status     # Verificar status
./manage-app.sh logs       # Ver logs
./manage-app.sh deploy     # Fazer deploy
./manage-app.sh backup     # Backup do banco
./manage-app.sh migrate    # Executar migrações
```

## 🔍 Verificação e Troubleshooting

### Verificar Status

```bash
# Status dos serviços
sudo systemctl status resolve-desafios
sudo systemctl status nginx

# Logs da aplicação
sudo journalctl -u resolve-desafios -f

# Logs do Nginx
sudo tail -f /var/log/nginx/error.log
```

### Testar Aplicação

```bash
# Testar localmente na VM
curl http://localhost:8000/health/

# Testar externamente
curl http://IP_EXTERNO_DA_VM/health/
```

### Problemas Comuns

1. **Erro 502 Bad Gateway**
   - Verificar se o Gunicorn está rodando
   - Verificar logs: `sudo journalctl -u resolve-desafios`

2. **Arquivos estáticos não carregam**
   - Executar: `python manage.py collectstatic --noinput`
   - Verificar permissões do diretório staticfiles

3. **Erro de banco de dados**
   - Executar migrações: `python manage.py migrate`
   - Verificar permissões do arquivo db.sqlite3

## 🔒 Segurança

### Configurações Recomendadas

1. **Firewall**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **SSL/HTTPS** (opcional)
   - Use Let's Encrypt para certificados gratuitos
   - Configure Nginx para HTTPS

3. **Backup Automático**
   - O script de backup já está configurado
   - Backups são mantidos por 7 dias

## 📊 Monitoramento

### Logs

- **Aplicação**: `/var/log/syslog` (via journalctl)
- **Nginx**: `/var/log/nginx/`
- **Sistema**: `/var/log/`

### Métricas

```bash
# Uso de CPU e memória
htop

# Uso de disco
df -h

# Conexões de rede
sudo netstat -tlnp
```

## 💰 Custos

### Estimativa de Custos (US Central)

- **e2-medium**: ~$24/mês
- **Disco 20GB**: ~$1/mês
- **Tráfego**: $0.12/GB (primeiros 1GB gratuitos)

**Total estimado**: ~$25/mês

### Otimizações de Custo

1. Use **e2-micro** para desenvolvimento (~$6/mês)
2. Configure **preemptible instances** para testes
3. Use **committed use discounts** para produção

## 🔄 Atualizações

Para atualizar a aplicação:

```bash
# SSH na VM
gcloud compute ssh resolve-desafios-vm --zone=us-central1-a

# Ir para diretório da aplicação
cd resolve-desafios

# Atualizar código
git pull origin main

# Fazer deploy
./manage-app.sh deploy
```

## 📞 Suporte

Em caso de problemas:

1. Verifique os logs da aplicação
2. Consulte a documentação do Django
3. Verifique a documentação do Google Cloud Platform
4. Abra uma issue no repositório do projeto
