# Ibook 📚

<p align="center">
  <img src="https://img.shields.io/badge/version-1.3.3-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/vue-3.x-green.svg" alt="Vue">
</p>

<p align="center">
  <b>简洁、高效的个人待办任务管理系统</b>
</p>

<p align="center">
  <a href="#-功能特性">功能特性</a> •
  <a href="#-快速开始">快速开始</a> •
  <a href="#-技术栈">技术栈</a> •
  <a href="#-项目结构">项目结构</a> •
  <a href="#-文档">文档</a>
</p>

---

## ✨ 功能特性

### 📝 任务管理
- **任务 CRUD** - 创建、编辑、删除任务，支持富文本描述
- **状态流转** - 支持待办 → 进行中 → 已完成/已取消 的完整状态机
- **优先级标记** - 高/中/低三级优先级，一目了然
- **截止时间** - 支持设置截止日期，过期任务自动标红提醒
- **无限期任务** - 支持不设置截止日期的长期任务

### 🎨 富文本编辑
- **Markdown 编辑器** - 基于 md-editor-v3 的所见即所得编辑体验
- **多媒体支持** - 支持插入图片、视频和附件
- **图片预览** - 点击任务中的图片可放大查看
- **视频播放** - 内置视频播放器，支持在线播放

### 🔍 任务筛选与排序
- **多维度筛选** - 按状态、优先级快速筛选任务
- **关键词搜索** - 支持标题和描述全文搜索
- **拖拽排序** - 自由拖拽调整任务优先级顺序
- **分页展示** - 支持 10/20/50 条每页切换

### 📊 统计面板
- **实时统计** - 任务总数、各状态数量实时展示
- **到期提醒** - 今日到期、已过期任务特别标识
- **快捷筛选** - 点击统计卡片快速筛选对应状态任务

### 🗑️ 回收站
- **软删除机制** - 误删任务可恢复
- **自动清理** - 回收站任务 30 天后自动永久删除
- **彻底删除** - 支持永久删除释放存储空间

### 👤 用户系统
- **多用户支持** - 个人和团队均可使用
- **JWT 认证** - 安全的 Token 认证机制
- **账户安全** - 密码 bcrypt 加密，支持登录失败锁定

### 🔧 管理员功能
- **用户管理** - 查看、禁用/启用、重置密码
- **系统配置** - 灵活配置附件上传限制
- **数据备份** - 一键导出/导入完整数据
- **系统统计** - 全局数据概览

---

## 🚀 快速开始

### 环境要求

| 组件 | 最低版本 | 推荐版本 |
|------|---------|---------|
| Ubuntu | 20.04 LTS | 24.04 LTS |
| Python | 3.8 | 3.12 |
| Node.js | 14 | 20 |

### 方式一：一键安装（推荐）

适用于 Ubuntu 20.04/22.04/24.04：

```bash
# 克隆项目
git clone <your-repo-url> ibook
cd ibook

# 执行安装脚本
chmod +x install.sh
./install.sh
```

安装脚本会自动完成：
- ✅ 检测系统版本
- ✅ 安装 Python3、Node.js 依赖
- ✅ 创建虚拟环境并安装后端依赖
- ✅ 安装前端依赖并构建
- ✅ 交互式设置管理员密码
- ✅ 创建 systemd 服务并启动

访问 `http://localhost:8000`，使用管理员账户 `admin` 登录。

### 方式二：Docker 部署

```bash
cd docker

# 设置管理员密码
export ADMIN_PASSWORD=YourPassword123
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 启动服务
docker compose up -d
```

访问 `http://localhost:8080`

### 方式三：开发模式

**后端：**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**前端：**
```bash
cd frontend
npm install
npm run dev
```

---

## 🛠️ 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Element Plus | 现代化响应式 UI 框架 |
| 构建工具 | Vite | 极速的开发体验 |
| 后端 | FastAPI | 高性能 Python Web 框架 |
| 数据库 | SQLite (WAL 模式) | 零配置、易备份 |
| 认证 | JWT + bcrypt | 安全可靠的认证方案 |
| 编辑器 | md-editor-v3 | 功能强大的 Markdown 编辑器 |

---

## 📁 项目结构

```
ibook/
├── backend/              # FastAPI 后端
│   ├── app/              # 应用代码
│   │   ├── api/          # API 路由
│   │   ├── models/       # 数据模型
│   │   ├── services/     # 业务逻辑
│   │   └── utils/        # 工具函数
│   ├── scripts/          # CLI 工具脚本
│   ├── uploads/          # 附件存储目录
│   └── data/             # SQLite 数据库
├── frontend/             # Vue 3 前端
│   ├── src/
│   │   ├── components/   # 组件
│   │   ├── views/        # 页面
│   │   └── api/          # API 封装
│   └── dist/             # 构建输出
├── docker/               # Docker 配置
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── nginx.conf
├── doc/                  # 项目文档
│   ├── README.md
│   ├── API.md            # API 接口文档
│   ├── DEPLOYMENT.md     # 部署说明
│   └── CHANGELOG.md      # 更新日志
├── install.sh            # 一键安装脚本
└── README.md             # 项目介绍
```

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [doc/API.md](doc/API.md) | 完整的 API 接口文档 |
| [doc/DEPLOYMENT.md](doc/DEPLOYMENT.md) | 详细部署指南 |
| [doc/CHANGELOG.md](doc/CHANGELOG.md) | 版本更新日志 |
| [需求文档.md](需求文档.md) | 产品需求文档 |

---

## 🔒 安全特性

- ✅ 密码使用 bcrypt 加盐哈希存储
- ✅ JWT Token 认证，支持黑名单机制
- ✅ 附件下载接口需认证，防止未授权访问
- ✅ SQL 注入防护
- ✅ XSS 攻击防护
- ✅ 用户数据完全隔离

---

## 🔄 数据备份与恢复

### 命令行方式

```bash
cd backend

# 导出备份
./scripts/export.sh

# 导入备份
./scripts/import.sh backups/ibook_backup_*.tar.gz
```

### Web 界面方式

管理员登录后，进入 **管理后台 → 备份恢复** 进行操作。

---

## 🖥️ 服务管理

```bash
# 启动服务
sudo systemctl start ibook

# 停止服务
sudo systemctl stop ibook

# 重启服务
sudo systemctl restart ibook

# 查看状态
sudo systemctl status ibook

# 查看日志
sudo journalctl -u ibook -f
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

---

## 📄 许可证

本项目采用 [MIT](LICENSE) 许可证开源。

---

<p align="center">
  Made with ❤️ for better productivity
</p>
