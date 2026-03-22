#!/bin/bash
# Ibook 一键安装脚本
# 适用于 Ubuntu 20.04 / 22.04 / 24.04
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}==============================${NC}"
echo -e "${GREEN}  Ibook 待办任务管理系统安装  ${NC}"
echo -e "${GREEN}==============================${NC}"
echo ""

# Check Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    UBUNTU_VERSION="$VERSION_ID"
    echo -e "检测到系统: ${GREEN}$PRETTY_NAME${NC}"
else
    echo -e "${RED}无法检测系统版本${NC}"
    exit 1
fi

case "$UBUNTU_VERSION" in
    20.04|22.04|24.04)
        echo -e "Ubuntu ${GREEN}$UBUNTU_VERSION${NC} - 支持"
        ;;
    *)
        echo -e "${YELLOW}警告: Ubuntu $UBUNTU_VERSION 未经测试，可能存在兼容性问题${NC}"
        read -p "是否继续？(y/N) " confirm
        [ "$confirm" != "y" ] && [ "$confirm" != "Y" ] && exit 0
        ;;
esac

INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo ""
echo "安装目录: $INSTALL_DIR"
echo ""

# Install system dependencies
echo -e "${GREEN}[1/6] 安装系统依赖...${NC}"
sudo apt-get update -qq
sudo apt-get install -y -qq python3 python3-pip python3-venv curl > /dev/null

# Install Node.js (if not present or too old)
if ! command -v node &> /dev/null || [ "$(node -v | sed 's/v//' | cut -d. -f1)" -lt 14 ]; then
    echo -e "${GREEN}[2/6] 安装 Node.js...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - > /dev/null 2>&1
    sudo apt-get install -y -qq nodejs > /dev/null
else
    echo -e "${GREEN}[2/6] Node.js 已安装: $(node -v)${NC}"
fi

# Setup Python venv and install backend deps
echo -e "${GREEN}[3/6] 安装后端依赖...${NC}"
cd "$INSTALL_DIR/backend"
python3 -m venv venv
source venv/bin/activate
pip install -q -r requirements.txt

# Install frontend deps and build
echo -e "${GREEN}[4/6] 构建前端...${NC}"
cd "$INSTALL_DIR/frontend"
npm install --silent 2>/dev/null
npx vite build 2>/dev/null

# Configure
echo -e "${GREEN}[5/6] 配置应用...${NC}"
cd "$INSTALL_DIR/backend"

if [ ! -f .env ]; then
    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
    cp .env.example .env
    sed -i "s/change-this-to-a-random-secret-key/$SECRET_KEY/" .env
fi

# Set admin password
echo ""
echo -e "${YELLOW}设置管理员密码（用户名: admin）${NC}"
while true; do
    read -sp "请输入管理员密码（8-32位，包含字母和数字）: " ADMIN_PWD
    echo ""
    if [[ ${#ADMIN_PWD} -lt 8 || ${#ADMIN_PWD} -gt 32 ]]; then
        echo -e "${RED}密码长度需要8-32位${NC}"
        continue
    fi
    if ! [[ "$ADMIN_PWD" =~ [a-zA-Z] ]] || ! [[ "$ADMIN_PWD" =~ [0-9] ]]; then
        echo -e "${RED}密码需要同时包含字母和数字${NC}"
        continue
    fi
    read -sp "确认密码: " ADMIN_PWD2
    echo ""
    if [ "$ADMIN_PWD" != "$ADMIN_PWD2" ]; then
        echo -e "${RED}两次输入的密码不一致${NC}"
        continue
    fi
    break
done

# Initialize database
source venv/bin/activate
python3 -c "
import sys; sys.path.insert(0, '.')
from app.database import Base, engine, SessionLocal
from app.models import *
from app.services.auth_service import init_admin
from app.models.system_config import init_system_config
Base.metadata.create_all(bind=engine)
db = SessionLocal()
init_admin(db, '$ADMIN_PWD')
init_system_config(db)
db.close()
print('数据库初始化完成')
"

# Create systemd service
echo -e "${GREEN}[6/6] 配置系统服务...${NC}"
SERVICE_FILE="/etc/systemd/system/ibook.service"
sudo tee "$SERVICE_FILE" > /dev/null << EOF
[Unit]
Description=Ibook Todo Task Management System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR/backend
ExecStart=$INSTALL_DIR/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
Environment=PATH=$INSTALL_DIR/backend/venv/bin:/usr/local/bin:/usr/bin:/bin

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable ibook
sudo systemctl start ibook

echo ""
echo -e "${GREEN}==============================${NC}"
echo -e "${GREEN}  安装完成！${NC}"
echo -e "${GREEN}==============================${NC}"
echo ""
echo -e "访问地址: ${GREEN}http://$(hostname -I | awk '{print $1}'):8000${NC}"
echo -e "管理员账户: ${GREEN}admin${NC}"
echo ""
echo "管理命令:"
echo "  sudo systemctl start ibook    # 启动"
echo "  sudo systemctl stop ibook     # 停止"
echo "  sudo systemctl restart ibook  # 重启"
echo "  sudo systemctl status ibook   # 状态"
