# Script para cambiar .env a base de datos LOCAL
# Ejecutar desde la raíz del proyecto: .\scripts\cambiar_a_local.ps1

$envContent = @"
# ============================================================================
# CONFIGURACIÓN DE BASE DE DATOS LOCAL
# ============================================================================

DB_NAME=Sistemaponti
DB_USER=postgres
DB_PASSWORD=TU_PASSWORD_LOCAL_AQUI
DB_HOST=localhost
DB_PORT=5434

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

# Leer el .env actual para obtener el password local si existe
$currentEnv = Get-Content $envPath -ErrorAction SilentlyContinue
$localPassword = ""
if ($currentEnv) {
    foreach ($line in $currentEnv) {
        if ($line -match "^DB_PASSWORD=(.+)$" -and $line -notmatch "supabase") {
            $localPassword = $matches[1]
            break
        }
    }
}

# Si no hay password guardado, pedirlo
if (-not $localPassword -or $localPassword -eq "TU_PASSWORD_LOCAL_AQUI") {
    Write-Host "⚠️  Necesitas el password de tu base de datos LOCAL" -ForegroundColor Yellow
    Write-Host "   Por favor, ingresa el password:" -ForegroundColor Yellow
    $securePassword = Read-Host -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $localPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

# Reemplazar el password en el contenido
$envContent = $envContent -replace "TU_PASSWORD_LOCAL_AQUI", $localPassword

$envContent | Out-File -FilePath $envPath -Encoding utf8 -NoNewline

Write-Host "✅ Archivo .env configurado para BASE DE DATOS LOCAL" -ForegroundColor Green
Write-Host ""
Write-Host "Configuración:" -ForegroundColor Cyan
Write-Host "  Host: localhost" -ForegroundColor Yellow
Write-Host "  Port: 5434" -ForegroundColor Yellow
Write-Host "  Database: Sistemaponti" -ForegroundColor Yellow
Write-Host ""
Write-Host "💡 Ahora puedes ejecutar:" -ForegroundColor Cyan
Write-Host "   python scripts/exportar_datos_sin_horarios.py" -ForegroundColor White

