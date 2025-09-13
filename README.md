# 🚀 Resolve Desafios - Manual de Execução

Interface web Django para análise de desafios de programação usando IA.

## 📋 Pré-requisitos

- Python 3.9+
- Chave da API OpenAI
- Git (opcional)

## 🏠 Execução Local

### 1. Criar e Ativar Ambiente Virtual (Recomendado)
```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# No macOS/Linux:
source venv/bin/activate
# No Windows:
# venv\Scripts\activate

# Verificar se está ativo (deve mostrar o caminho do venv)
which python

# Desativar ambiente virtual (quando terminar)
deactivate
```

### 2. Instalar Dependências
```bash
# Com ambiente virtual ativado
pip install -r requirements.txt

# Ou sem ambiente virtual (não recomendado)
pip3 install -r requirements.txt
```

### 3. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp env.example .env

# Editar .env e adicionar sua chave OpenAI
nano .env
```

**Conteúdo do .env:**
```env
OPENAI_API_KEY=sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini
RESOLVE_DB_PATH=./data/resolve_desafios.db
APP_LANGUAGE=pt-BR
```

### 4. Configurar Banco de Dados
```bash
python manage.py migrate
```

### 5. Executar Aplicação
```bash
# Opção 1: Script personalizado (recomendado)
python run_django.py

# Opção 2: Comando Django padrão
python manage.py runserver 0.0.0.0:8000
```

### 6. Acessar Aplicação
- **URL:** http://localhost:8000
- **Health Check:** http://localhost:8000/health/

## 🌐 Deploy em Produção

### Heroku (Recomendado)

#### 1. Preparar para Heroku
```bash
# Verificar se Procfile existe
cat Procfile

# Verificar configurações de produção
cat resolve_desafios_web/settings_heroku.py
```

#### 2. Deploy via Heroku CLI
```bash
# Login no Heroku
heroku login

# Criar app (primeira vez)
heroku create seu-app-nome

# Configurar variáveis de ambiente
heroku config:set OPENAI_API_KEY=sua_chave_aqui
heroku config:set OPENAI_MODEL=gpt-4o-mini

# Deploy
git push heroku main

# Executar migrações
heroku run python manage.py migrate

# Abrir aplicação
heroku open
```

#### 3. Deploy via Script Automático
```bash
# Usar script de deploy
chmod +x deploy-heroku.sh
./deploy-heroku.sh
```

### VPS/Server Linux

#### 1. Configurar Servidor
```bash
# Instalar dependências do sistema
sudo apt update
sudo apt install python3 python3-pip nginx

# Clonar repositório
git clone <seu-repo>
cd resolve-desafios
```

#### 2. Configurar Aplicação
```bash
# Criar e ativar ambiente virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependências Python
pip install -r requirements.txt

# Configurar .env
cp env.example .env
nano .env

# Aplicar migrações
python manage.py migrate
python manage.py collectstatic
```

#### 3. Configurar Nginx
```bash
# Usar configuração incluída
sudo cp nginx.conf /etc/nginx/sites-available/resolve-desafios
sudo ln -s /etc/nginx/sites-available/resolve-desafios /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 4. Executar com Gunicorn
```bash
# Executar em background
gunicorn --bind 0.0.0.0:8000 resolve_desafios_web.wsgi &

# Ou usar systemd service
sudo cp resolve-desafios.service /etc/systemd/system/
sudo systemctl enable resolve-desafios
sudo systemctl start resolve-desafios
```

## 🔧 Comandos Úteis

### Desenvolvimento
```bash
# Ativar ambiente virtual (se não estiver ativo)
source venv/bin/activate

# Verificar configuração
python manage.py check

# Criar superusuário (futuro)
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Coletar arquivos estáticos
python manage.py collectstatic

# Desativar ambiente virtual (quando terminar)
deactivate
```

### Produção
```bash
# Verificar logs
heroku logs --tail

# Executar comando no Heroku
heroku run python manage.py migrate

# Restart aplicação
heroku restart
```

## 📊 Funcionalidades

### Interface Web
- **Página Principal:** Interface completa com abas
- **Análise de Desafios:** Formulário com validação
- **Histórico:** Listagem de análises anteriores
- **Detalhes:** Página dedicada para cada análise

### Endpoints API
- `GET /` - Página principal
- `POST /analyze/` - Analisar desafio
- `GET /analyses/` - Listar análises
- `GET /analysis/<id>/` - Detalhes da análise
- `GET /health/` - Status do serviço

## 🚨 Solução de Problemas

### Erro: "API Key not found"
- Verifique se o arquivo `.env` existe
- Confirme se `OPENAI_API_KEY` está definida
- Reinicie o servidor após alterar `.env`

### Erro: "Database not found"
```bash
# Com ambiente virtual ativado
source venv/bin/activate
python manage.py migrate
```

### Erro: "Static files not found"
```bash
# Com ambiente virtual ativado
source venv/bin/activate
python manage.py collectstatic
```

### Porta 8000 ocupada
```bash
# Usar porta diferente
source venv/bin/activate
python manage.py runserver 0.0.0.0:8080
```

### Dicas sobre Ambiente Virtual
- **Sempre ative o venv** antes de trabalhar no projeto: `source venv/bin/activate`
- **Verifique se está ativo**: O prompt deve mostrar `(venv)` no início
- **Desative quando terminar**: `deactivate`
- **Adicione `venv/` ao .gitignore** (se não estiver já)
- **Reinstale dependências** se trocar de ambiente: `pip install -r requirements.txt`

## 📝 Estrutura do Projeto

```
resolve-desafios/
├── desafios/                 # App Django principal
│   ├── views.py             # Views e endpoints
│   ├── templates/           # Templates HTML
│   └── urls.py              # URLs do app
├── resolve_desafios_web/    # Configurações Django
│   ├── settings.py          # Config local
│   ├── settings_heroku.py   # Config Heroku
│   └── urls.py              # URLs principais
├── src/resolve_desafios/    # Lógica de negócio
│   ├── container.py         # Injeção de dependência
│   ├── llm_adapter.py       # Adapter OpenAI
│   └── schemas.py           # Modelos de dados
├── static/                  # Arquivos estáticos
├── data/                    # Banco de dados SQLite
├── requirements.txt         # Dependências Python
├── Procfile                 # Config Heroku
├── run_django.py           # Script de execução
└── .env                     # Variáveis de ambiente
```

## ✅ Checklist de Deploy

### Local
- [ ] Python 3.9+ instalado
- [ ] Ambiente virtual criado (`python3 -m venv venv`)
- [ ] Ambiente virtual ativado (`source venv/bin/activate`)
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` configurado
- [ ] Migrações aplicadas (`python manage.py migrate`)
- [ ] Servidor rodando (`python run_django.py`)
- [ ] Aplicação acessível em http://localhost:8000

### Produção (Heroku)
- [ ] Conta Heroku criada
- [ ] Heroku CLI instalado
- [ ] App Heroku criado
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy realizado (`git push heroku main`)
- [ ] Migrações executadas (`heroku run python manage.py migrate`)
- [ ] Aplicação acessível via URL do Heroku

### Produção (VPS)
- [ ] Servidor Linux configurado
- [ ] Nginx instalado e configurado
- [ ] Aplicação rodando com Gunicorn
- [ ] Service systemd configurado (opcional)
- [ ] Firewall configurado (porta 80/443)
- [ ] SSL/HTTPS configurado (recomendado)

---

**🎯 Aplicação pronta para uso!** Acesse http://localhost:8000 para começar a analisar desafios de programação.
