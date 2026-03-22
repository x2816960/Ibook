# Ibook 部署说明

## 环境要求

| 组件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Ubuntu | 20.04 LTS | 24.04 LTS |
| Python | 3.8 | 3.12 |
| Node.js | 14 | 20 |
| npm | 6 | 10 |

## 方式一：一键安装脚本

```bash
# 下载项目后执行
chmod +x install.sh
./install.sh
```

脚本自动完成：
1. 检测 Ubuntu 版本
2. 安装 Python3、Node.js 系统依赖
3. 创建 Python 虚拟环境，安装后端依赖
4. 安装前端依赖并构建
5. 交互式设置管理员密码
6. 创建 systemd 服务并启动

### 服务管理

```bash
sudo systemctl start ibook      # 启动
sudo systemctl stop ibook       # 停止
sudo systemctl restart ibook    # 重启
sudo systemctl status ibook     # 查看状态
sudo journalctl -u ibook -f     # 查看日志
```

## 方式二：Docker 部署

```bash
cd docker

# 设置管理员密码和密钥
export ADMIN_PASSWORD=YourPassword123
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 启动
docker compose up -d

# 查看日志
docker compose logs -f
```

默认端口: `8080`，可在 `docker-compose.yml` 中修改。

数据持久化通过 Docker volumes:
- `ibook_data`: SQLite 数据库
- `ibook_uploads`: 附件文件
- `ibook_backups`: 备份文件

## 配置说明

### 环境变量 / .env 文件

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SECRET_KEY` | (需设置) | JWT 签名密钥 |
| `DATABASE_URL` | `sqlite:///./data/ibook.db` | 数据库路径 |
| `UPLOAD_DIR` | `./uploads` | 附件存储目录 |
| `BACKUP_DIR` | `./backups` | 备份输出目录 |
| `ALLOWED_ORIGINS` | `http://localhost:5173` | CORS 允许的域名 |
| `ADMIN_PASSWORD` | (无) | Docker 部署时设置管理员密码 |

## 生产环境建议

### Nginx 反向代理

```bash
sudo cp docker/nginx.conf /etc/nginx/sites-available/ibook
sudo ln -s /etc/nginx/sites-available/ibook /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### HTTPS 配置

使用 Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## 数据备份

### 命令行备份

```bash
cd backend
./scripts/export.sh                          # 导出
./scripts/import.sh backups/ibook_backup_*.tar.gz  # 导入
```

### Web 界面备份

管理员登录后，进入 管理后台 → 备份恢复。

## 常见问题

**Q: 端口 8000 被占用？**
修改 systemd 服务文件中 `--port 8000` 为其他端口。

**Q: 附件上传失败？**
检查 `uploads/` 目录权限，确保应用用户有写入权限。如使用 nginx，检查 `client_max_body_size` 配置。

**Q: 忘记管理员密码？**
```bash
cd backend && source venv/bin/activate
python3 -c "
from app.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password
db = SessionLocal()
admin = db.query(User).filter(User.username=='admin').first()
admin.password_hash = hash_password('NewPassword123')
db.commit()
print('密码已重置')
"
```
