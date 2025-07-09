# 🚀 Deploy em Produção - Sistema de Fila Digital

## 📋 Preparação para Produção

### 1️⃣ Configurações de Segurança

Edite `src/config.py`:

```python
class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    
    # IMPORTANTE: Altere esta chave!
    SECRET_KEY = '14022005Jvn@'
    
    # Configurações de segurança
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

### 2️⃣ Servidor WSGI (Recomendado)

```bash
# Instale Gunicorn
pip install gunicorn

# Execute em produção
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

### 3️⃣ Nginx (Proxy Reverso)

Configuração `/etc/nginx/sites-available/fila-barbearia`:

```nginx
server {
    listen 80;
    server_name seu-dominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /caminho/para/sistema-fila-barbearia/src/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 🐳 Docker (Opcional)

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.main:app"]
```

### docker-compose.yml
```yaml
version: '3.8'

services:
  fila-barbearia:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./src/database:/app/src/database
      - ./backups:/app/backups
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

## 🔒 Segurança Adicional

### 1️⃣ Firewall
```bash
# Ubuntu/Debian
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw enable
```

### 2️⃣ SSL/HTTPS (Let's Encrypt)
```bash
# Instale Certbot
sudo apt install certbot python3-certbot-nginx

# Obtenha certificado
sudo certbot --nginx -d seu-dominio.com
```

### 3️⃣ Backup Automático
```bash
# Adicione ao crontab
crontab -e

# Backup diário às 2h da manhã
0 2 * * * /caminho/para/backup_script.sh
```

## 📊 Monitoramento

### 1️⃣ Logs
```bash
# Logs do Gunicorn
gunicorn --access-logfile access.log --error-logfile error.log

# Rotação de logs
sudo apt install logrotate
```

### 2️⃣ Systemd Service

Arquivo `/etc/systemd/system/fila-barbearia.service`:

```ini
[Unit]
Description=Sistema de Fila Digital para Barbearia
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/caminho/para/sistema-fila-barbearia
Environment=PATH=/caminho/para/sistema-fila-barbearia/venv/bin
ExecStart=/caminho/para/sistema-fila-barbearia/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 src.main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Ative o serviço
sudo systemctl enable fila-barbearia
sudo systemctl start fila-barbearia
sudo systemctl status fila-barbearia
```

## 🔧 Otimizações

### 1️⃣ Performance
- Use Redis para cache (opcional)
- Configure compressão gzip no Nginx
- Otimize imagens e assets estáticos

### 2️⃣ Banco de Dados
- Para alta demanda, considere PostgreSQL
- Configure backup automático
- Monitore tamanho e performance

### 3️⃣ CDN (Opcional)
- Use CloudFlare para assets estáticos
- Configure cache adequadamente

## 📱 Acesso Mobile

### PWA (Progressive Web App)
O sistema já está preparado para funcionar como PWA:
- Responsivo em todos os dispositivos
- Funciona offline (cache básico)
- Pode ser "instalado" no celular

## 🚨 Checklist de Deploy

- [ ] Configurações de produção aplicadas
- [ ] Chave secreta alterada
- [ ] Gunicorn configurado
- [ ] Nginx configurado (se aplicável)
- [ ] SSL/HTTPS configurado
- [ ] Firewall configurado
- [ ] Backup automático configurado
- [ ] Monitoramento ativo
- [ ] Logs configurados
- [ ] Testes realizados
- [ ] Documentação atualizada

## 🆘 Troubleshooting Produção

### Erro 502 Bad Gateway
```bash
# Verifique se o Gunicorn está rodando
sudo systemctl status fila-barbearia

# Verifique logs
sudo journalctl -u fila-barbearia -f
```

### Performance Lenta
```bash
# Monitore recursos
htop
iotop

# Verifique logs de acesso
tail -f access.log
```

### Banco de Dados Corrompido
```bash
# Restaure do backup
cp backups/app_YYYYMMDD_HHMMSS.db src/database/app.db
sudo systemctl restart fila-barbearia
```

---

**⚠️ IMPORTANTE:** Sempre teste em ambiente de desenvolvimento antes de aplicar em produção!

**🔒 SEGURANÇA:** Mantenha backups regulares e monitore logs de segurança.

