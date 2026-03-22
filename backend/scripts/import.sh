#!/bin/bash
# Ibook 数据导入脚本
set -e

if [ -z "$1" ]; then
    echo "用法: ./import.sh <备份文件路径>"
    echo "示例: ./import.sh ../backups/ibook_backup_20260321_120000.tar.gz"
    exit 1
fi

BACKUP_FILE="$1"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "错误: 备份文件不存在: $BACKUP_FILE"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(dirname "$SCRIPT_DIR")"

echo "警告: 导入将覆盖当前所有数据！"
read -p "确认导入？(y/N) " confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "已取消"
    exit 0
fi

cd "$BACKEND_DIR"

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
fi

BACKUP_ABSOLUTE="$(cd "$(dirname "$BACKUP_FILE")" && pwd)/$(basename "$BACKUP_FILE")"

python3 -c "
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.services.backup_service import import_backup
from pathlib import Path

backup_path = Path('$BACKUP_ABSOLUTE')
content = backup_path.read_bytes()
db = SessionLocal()
try:
    result = import_backup(db, content, backup_path.name)
    print(result['message'])
finally:
    db.close()
"

echo "请重启 Ibook 服务以加载恢复的数据"
