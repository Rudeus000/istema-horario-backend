# Script para crear/actualizar el archivo .env con las credenciales de Supabase
# Ejecutar desde la raíz del proyecto: .\scripts\crear_env.ps1

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

$envPath = Join-Path $PSScriptRoot ".." ".env"
$envPath = Resolve-Path $envPath -ErrorAction SilentlyContinue

if (-not $envPath) {
    $envPath = Join-Path (Split-Path $PSScriptRoot -Parent) ".env"
}

$envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline

Write-Host "✅ Archivo .env creado/actualizado en: $envPath" -ForegroundColor Green
Write-Host ""
Write-Host "Configuración de Supabase:" -ForegroundColor Cyan
Write-Host "  Host: db.dhnbtnfpqhdtbzopfguw.supabase.co" -ForegroundColor Yellow
Write-Host "  Port: 5432" -ForegroundColor Yellow
Write-Host "  User: postgres" -ForegroundColor Yellow
Write-Host "  Password: `$HunterxHunter`$" -ForegroundColor Yellow
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Cyan
Write-Host "  1. Activar entorno virtual: venv\Scripts\activate" -ForegroundColor White
Write-Host "  2. Probar conexión: python manage.py dbshell" -ForegroundColor White
Write-Host "  3. Ejecutar migraciones: python manage.py migrate" -ForegroundColor White

