# Script para cambiar .env a Supabase
# Ejecutar desde la raíz del proyecto: .\scripts\cambiar_a_supabase.ps1

$envContent = @"
# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS SUPABASE
# ============================================================================

DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=`$HunterxHunter`$
DB_HOST=db.dhnbtnfpqhdtbzopfguw.supabase.co
DB_PORT=5432

# ============================================================================
# CONFIGURACIÓN DE DJANGO
# ============================================================================
SECRET_KEY=django-insecure-dev-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# ============================================================================
# CONFIGURACIÓN DE REDIS (Local)
# ============================================================================
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

# ============================================================================
# CONFIGURACIÓN DE CORS
# ============================================================================
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173,http://localhost:8080
"@

# Obtener el directorio raíz del proyecto
$projectRoot = Split-Path $PSScriptRoot -Parent
$envPath = Join-Path $projectRoot ".env"

$envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline

Write-Host "✅ Archivo .env configurado para SUPABASE" -ForegroundColor Green
Write-Host ""
Write-Host "Configuración:" -ForegroundColor Cyan
Write-Host "  Host: db.dhnbtnfpqhdtbzopfguw.supabase.co" -ForegroundColor Yellow
Write-Host "  Port: 5432" -ForegroundColor Yellow
Write-Host "  Database: postgres" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Ahora puedes ejecutar:" -ForegroundColor Cyan
Write-Host "   python scripts/importar_datos_supabase.py --file backup_sin_horarios_XXXXXX.json" -ForegroundColor White

