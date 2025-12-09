# Guía de Despliegue - DOCX Editor

## 📋 Índice

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Instalación Local](#instalación-local)
3. [Deployment con Docker](#deployment-con-docker)
4. [Deployment en Producción](#deployment-en-producción)
5. [Configuración Avanzada](#configuración-avanzada)
6. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
7. [Troubleshooting](#troubleshooting)

---

## Requisitos del Sistema

### Mínimos

- **CPU**: 1 core
- **RAM**: 512MB
- **Disco**: 1GB espacio libre
- **Sistema Operativo**: Linux, Windows 10+, macOS 10.14+
- **Python**: 3.9+

### Recomendados (Producción)

- **CPU**: 2+ cores
- **RAM**: 2GB+
- **Disco**: 10GB+ (para logs y backups)
- **Sistema Operativo**: Ubuntu 20.04+ LTS
- **Python**: 3.11+

---

## Instalación Local

### 1. Preparación del Entorno

```bash
# Clonar repositorio
git clone https://github.com/yourusername/docx-editor.git
cd docx-editor

# Crear entorno virtual
python3.11 -m venv venv

# Activar entorno
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2. Instalar Dependencias

```bash
# Upgrade pip
pip install --upgrade pip

# Instalar paquete en modo desarrollo
pip install -e .

# O instalar dependencias directamente
pip install -r requirements.txt

# Verificar instalación
docx-editor --version
python -c "import docx; print(docx.__version__)"
```

### 3. Configuración Inicial

```bash
# Crear directorios necesarios
mkdir -p temp backups logs

# Copiar configuración de ejemplo
cp config/settings.yaml.example config/settings.yaml

# Editar configuración
nano config/settings.yaml
```

### 4. Prueba de Instalación

```bash
# Ejecutar tests
pytest tests/ -v

# Verificar CLI
docx-editor --help

# Verificar API (en otra terminal)
uvicorn src.api.rest_server:app --reload
# Visitar: http://localhost:8000/docs
```

---

## Deployment con Docker

### 1. Build de Imagen

```bash
# Build básico
docker build -t docx-editor:latest -f docker/Dockerfile .

# Build con tag específico
docker build -t docx-editor:1.0.0 -f docker/Dockerfile .

# Build multi-stage (optimizado)
docker build \
  --target production \
  -t docx-editor:prod \
  -f docker/Dockerfile .
```

### 2. Ejecutar Container

```bash
# Ejecución básica
docker run -d \
  --name docx-editor \
  -p 8000:8000 \
  docx-editor:latest

# Con volúmenes persistentes
docker run -d \
  --name docx-editor \
  -p 8000:8000 \
  -v $(pwd)/temp:/app/temp \
  -v $(pwd)/backups:/app/backups \
  -v $(pwd)/logs:/app/logs \
  -e LOG_LEVEL=INFO \
  -e WORKER_POOL_SIZE=4 \
  docx-editor:latest

# Health check
curl http://localhost:8000/health
```

### 3. Docker Compose (Recomendado)

```bash
# Crear archivo docker-compose.yml (ver ejemplo en repositorio)

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down

# Rebuild
docker-compose up -d --build
```

**docker-compose.yml completo:**

```yaml
version: "3.8"

services:
  docx-editor:
    build:
      context: .
      dockerfile: docker/Dockerfile
    image: docx-editor:latest
    container_name: docx-editor-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - MAX_FILE_SIZE=20971520
      - WORKER_POOL_SIZE=4
      - PYTHONUNBUFFERED=1
    volumes:
      - ./temp:/app/temp
      - ./backups:/app/backups
      - ./logs:/app/logs
    networks:
      - docx-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    deploy:
      resources:
        limits:
          cpus: "2"
          memory: 1G
        reservations:
          cpus: "0.5"
          memory: 512M

  nginx:
    image: nginx:alpine
    container_name: docx-editor-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - docx-editor
    networks:
      - docx-network

networks:
  docx-network:
    driver: bridge

volumes:
  temp:
  backups:
  logs:
```

---

## Deployment en Producción

### 1. Nginx Reverse Proxy

**nginx.conf:**

```nginx
upstream docx_editor {
    server docx-editor:8000;
}

server {
    listen 80;
    server_name api.ejemplo.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.ejemplo.com;

    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 25M;

    location / {
        proxy_pass http://docx_editor;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    location /health {
        proxy_pass http://docx_editor/health;
        access_log off;
    }
}
```

### 2. Systemd Service (Linux)

**docx-editor.service:**

```ini
[Unit]
Description=DOCX Editor API
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/docx-editor
Environment="PATH=/opt/docx-editor/venv/bin"
ExecStart=/opt/docx-editor/venv/bin/gunicorn \
  src.api.rest_server:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile /var/log/docx-editor/access.log \
  --error-logfile /var/log/docx-editor/error.log \
  --log-level info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Instalación del servicio:**

```bash
# Copiar archivo
sudo cp docx-editor.service /etc/systemd/system/

# Recargar systemd
sudo systemctl daemon-reload

# Habilitar servicio
sudo systemctl enable docx-editor

# Iniciar servicio
sudo systemctl start docx-editor

# Verificar estado
sudo systemctl status docx-editor

# Ver logs
sudo journalctl -u docx-editor -f
```

### 3. Gunicorn con Supervisor

**supervisor.conf:**

```ini
[program:docx-editor]
command=/opt/docx-editor/venv/bin/gunicorn src.api.rest_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
directory=/opt/docx-editor
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/docx-editor/supervisor.log
environment=PYTHONPATH="/opt/docx-editor"
```

---

## Configuración Avanzada

### Variables de Entorno

```bash
# .env para producción
LOG_LEVEL=INFO
MAX_FILE_SIZE=20971520
WORKER_POOL_SIZE=4
BACKUP_RETENTION_DAYS=30
ENABLE_METRICS=true
API_KEY_REQUIRED=true
CORS_ORIGINS=https://app.ejemplo.com,https://admin.ejemplo.com
```

### Optimización de Performance

**1. Gunicorn Workers:**

```bash
# Fórmula: (2 x CPU cores) + 1
# Para servidor de 4 cores:
gunicorn src.api.rest_server:app -w 9 -k uvicorn.workers.UvicornWorker
```

**2. Limpieza Automática:**

```bash
# Cron job para limpiar archivos temporales (crontab -e)
0 2 * * * find /opt/docx-editor/temp -type f -mtime +1 -delete
0 3 * * 0 find /opt/docx-editor/backups -type f -mtime +30 -delete
```

**3. Límites de Sistema:**

```bash
# /etc/security/limits.conf
www-data soft nofile 65536
www-data hard nofile 65536
```

### Seguridad

**1. Firewall (UFW):**

```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

**2. Rate Limiting (Nginx):**

```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location / {
    limit_req zone=api_limit burst=20 nodelay;
    # ... resto de configuración
}
```

---

## Monitoreo y Mantenimiento

### 1. Health Checks

```bash
# Script de monitoreo
#!/bin/bash
# check_health.sh

response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)

if [ $response -ne 200 ]; then
    echo "API no responde correctamente: $response"
    # Enviar alerta
    systemctl restart docx-editor
fi
```

### 2. Logs

```bash
# Ver logs en tiempo real
tail -f logs/docx_editor_$(date +%Y%m%d).log

# Buscar errores
grep -i error logs/*.log

# Análisis de performance
grep "completada en" logs/*.log | awk '{print $NF}'
```

### 3. Backups

```bash
# Backup de configuración y datos
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/docx-editor"

tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" config/
tar -czf "$BACKUP_DIR/backups_$DATE.tar.gz" backups/

# Mantener solo últimos 30 días
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

### 4. Métricas

```python
# Endpoint de métricas (agregar a API)
@app.get("/metrics")
async def get_metrics():
    return {
        "uptime": get_uptime(),
        "documents_processed_today": get_doc_count(),
        "average_processing_time": get_avg_time(),
        "memory_usage_mb": get_memory_usage(),
        "disk_usage_percent": get_disk_usage()
    }
```

---

## Troubleshooting

### Problema: Container se reinicia constantemente

```bash
# Ver logs
docker logs docx-editor

# Verificar recursos
docker stats docx-editor

# Health check manual
docker exec docx-editor curl http://localhost:8000/health
```

### Problema: "Memory limit exceeded"

```yaml
# Aumentar límite en docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
```

### Problema: Archivos temporales acumulándose

```bash
# Limpiar manualmente
find ./temp -type f -mtime +1 -delete

# Configurar limpieza automática en API
# agregar cleanup task en rest_server.py
```

### Problema: Performance degradado

```bash
# Aumentar workers
export WORKER_POOL_SIZE=8

# Verificar CPU/memoria
top
htop

# Profiling
python -m cProfile -o profile.stats script.py
```

---

## Checklist de Deployment

- [ ] Python 3.9+ instalado
- [ ] Dependencias instaladas
- [ ] Configuración revisada (settings.yaml)
- [ ] Directorios creados (temp, backups, logs)
- [ ] Tests pasando
- [ ] Variables de entorno configuradas
- [ ] Firewall configurado
- [ ] SSL/TLS configurado (producción)
- [ ] Nginx configurado (si aplica)
- [ ] Systemd service configurado (Linux)
- [ ] Logs funcionando
- [ ] Health checks funcionando
- [ ] Backups configurados
- [ ] Monitoreo configurado
- [ ] Documentación actualizada

---

## Recursos Adicionales

- [Documentación API](http://localhost:8000/docs)
- [Guía de Desarrollo](CONTRIBUTING.md)
- [Roadmap](ROADMAP.md)
- [Changelog](CHANGELOG.md)

**Soporte:** support@ejemplo.com
