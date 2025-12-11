# Script para corregir problemas de codificación en .env
# Ejecutar desde la raíz del proyecto: .\scripts\corregir_env.ps1

$projectRoot = Split-Path $PSScriptRoot -Parent
$envPath = Join-Path $projectRoot ".env"

if (-not (Test-Path $envPath)) {
    Write-Host "❌ El archivo .env no existe!" -ForegroundColor Red
    Write-Host "   Ruta esperada: $envPath" -ForegroundColor Yellow
    exit 1
}

Write-Host "📖 Leyendo archivo: $envPath" -ForegroundColor Cyan

# Crear backup
$backupPath = "$envPath.backup"
Copy-Item $envPath $backupPath -Force
Write-Host "💾 Backup creado: $backupPath" -ForegroundColor Green

# Leer el contenido del archivo con diferentes codificaciones
$content = $null
$encodings = @([System.Text.Encoding]::UTF8, [System.Text.Encoding]::Default, [System.Text.Encoding]::ASCII)

foreach ($encoding in $encodings) {
    try {
        $content = Get-Content $envPath -Raw -Encoding UTF8
        Write-Host "✅ Archivo leído correctamente" -ForegroundColor Green
        break
    } catch {
        Write-Host "⚠️  Error con codificación $($encoding.EncodingName): $_" -ForegroundColor Yellow
    }
}

if ($null -eq $content) {
    Write-Host "❌ No se pudo leer el archivo" -ForegroundColor Red
    exit 1
}

# Limpiar líneas problemáticas
$lines = $content -split "`r?`n"
$cleanedLines = @()

foreach ($line in $lines) {
    # Eliminar caracteres de control problemáticos
    $cleanedLine = $line -replace "[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", ""
    $cleanedLines += $cleanedLine
}

# Reconstruir contenido
$cleanedContent = $cleanedLines -join "`n"

# Guardar en UTF-8 sin BOM
try {
    [System.IO.File]::WriteAllText($envPath, $cleanedContent, [System.Text.UTF8Encoding]::new($false))
    Write-Host "✅ Archivo .env guardado correctamente en UTF-8 (sin BOM)" -ForegroundColor Green
    Write-Host ""
    Write-Host "💡 Si el problema persiste:" -ForegroundColor Cyan
    Write-Host "   1. Verifica que la contraseña no tenga caracteres especiales" -ForegroundColor Yellow
    Write-Host "   2. Edita el .env manualmente con un editor que soporte UTF-8" -ForegroundColor Yellow
    Write-Host "   3. Asegúrate de que no haya espacios extraños al inicio/final" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Error al guardar: $_" -ForegroundColor Red
    exit 1
}

