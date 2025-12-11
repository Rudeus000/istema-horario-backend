# Script temporal para corregir .env
import sys
from pathlib import Path

env_path = Path('.env')

# Leer con latin-1 (acepta cualquier byte)
with open(env_path, 'rb') as f:
    raw = f.read()

# Decodificar a string ignorando errores
text = raw.decode('latin-1')

# Limpiar y guardar en UTF-8
cleaned = text.encode('utf-8', errors='replace').decode('utf-8')

# Backup
with open('.env.backup', 'wb') as f:
    f.write(raw)

# Guardar en UTF-8 sin BOM
with open(env_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(cleaned)

print("✅ Corregido")
sys.exit(0)

