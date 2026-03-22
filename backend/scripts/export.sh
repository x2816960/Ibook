#!/bin/bash
# Ibook 数据导出脚本
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${1:-$BACKEND_DIR/backups}"

cd "$BACKEND_DIR"

# Activate venv if exists
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

python3 -c "
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.services.backup_service import export_backup

db = SessionLocal()
try:
    filename = export_backup(db)
    print(f'备份已创建: backups/{filename}')
finally:
    db.close()
"
