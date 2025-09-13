#!/bin/bash

# Script de inicialização para Google Cloud Platform - Compute Engine
# Este script é executado automaticamente quando a VM é criada

# Atualizar sistema
apt-get update
apt-get upgrade -y

# Instalar dependências básicas
apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    git \
    curl \
    unzip

# Configurar firewall
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Configurar Nginx básico
systemctl enable nginx
systemctl start nginx

# Criar usuário para a aplicação (se não existir)
if ! id "appuser" &>/dev/null; then
    useradd -m -s /bin/bash appuser
fi

# Criar diretório da aplicação
mkdir -p /opt/resolve-desafios
chown appuser:appuser /opt/resolve-desafios

# Configurar logrotate para a aplicação
cat > /etc/logrotate.d/resolve-desafios << EOF
/opt/resolve-desafios/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 appuser appuser
}
EOF

# Configurar backup automático (opcional)
cat > /opt/backup-db.sh << 'EOF'
#!/bin/bash
# Script de backup do banco de dados
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups"
DB_FILE="/opt/resolve-desafios/db.sqlite3"

mkdir -p $BACKUP_DIR

if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/db_backup_$DATE.sqlite3"
    # Manter apenas os últimos 7 backups
    find $BACKUP_DIR -name "db_backup_*.sqlite3" -mtime +7 -delete
fi
EOF

chmod +x /opt/backup-db.sh

# Adicionar backup ao crontab
echo "0 2 * * * /opt/backup-db.sh" | crontab -

# Configurar monitoramento básico
apt-get install -y htop iotop

# Log da inicialização
echo "$(date): Startup script completed successfully" >> /var/log/startup-script.log
