# Ibook - 待办任务管理系统

基于 Web 的多用户待办任务管理系统，支持任务创建、编辑、状态管理、Markdown 详情编辑、附件管理、拖拽排序等功能。

## 主要功能

- 用户注册/登录，JWT 认证
- 任务 CRUD，状态流转（待办/进行中/已完成/已取消）
- Markdown 详细信息编辑，支持插入图片、视频、附件
- 任务筛选、搜索、拖拽排序、分页
- 任务统计面板（各状态数量、今日到期、已过期）
- 回收站（软删除、恢复、30天自动清理）
- 管理员：用户管理、系统配置、数据备份恢复
- 一键部署脚本 + Docker 支持

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + Vite |
| 后端 | Python FastAPI |
| 数据库 | SQLite (WAL 模式) |
| 认证 | JWT + bcrypt |
| 编辑器 | md-editor-v3 |

## 快速开始

### 一键安装 (Ubuntu 20.04/22.04/24.04)

```bash
chmod +x install.sh
./install.sh
```

安装脚本会自动安装依赖、构建前端、配置系统服务。

### Docker 部署

```bash
cd docker
ADMIN_PASSWORD=YourPassword123 docker compose up -d
```

访问 `http://localhost:8080`

### 开发模式

```bash
# 后端
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd frontend
npm install
npm run dev
```

## 项目结构

```
ibook/
├── backend/          # FastAPI 后端
│   ├── app/          # 应用代码
│   ├── scripts/      # CLI 工具脚本
│   ├── uploads/      # 附件存储
│   └── data/         # SQLite 数据库
├── frontend/         # Vue 3 前端
├── docker/           # Docker 配置
├── doc/              # 项目文档
└── install.sh        # 一键安装脚本
```

## 许可证

MIT License
