# Ibook API 接口文档

## 基础信息

- Base URL: `/api`
- 认证方式: Bearer Token (JWT)
- 请求格式: JSON (`Content-Type: application/json`)
- 附件上传: `multipart/form-data`

## 认证接口

### POST /api/auth/register - 用户注册

```json
// Request
{
  "username": "testuser",
  "password": "Test1234",
  "confirm_password": "Test1234",
  "email": "test@example.com",
  "nickname": "测试用户"
}

// Response 200
{ "message": "注册成功" }
```

### POST /api/auth/login - 用户登录

```json
// Request
{
  "username": "testuser",
  "password": "Test1234",
  "remember_me": false
}

// Response 200
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "must_change_password": false
}
```

### POST /api/auth/logout - 退出登录

需要 Bearer Token。将当前 Token 加入黑名单。

### PUT /api/auth/password - 修改密码

```json
// Request
{ "old_password": "Test1234", "new_password": "NewPass123" }
// Response 200
{ "message": "密码修改成功" }
```

### GET /api/auth/profile - 获取当前用户信息

### PUT /api/auth/profile - 更新个人信息

```json
{ "nickname": "新昵称" }
```

## 任务接口

### GET /api/tasks - 获取任务列表

查询参数: `status`, `priority`, `keyword`, `page` (默认1), `page_size` (默认20, 最大50)

```json
// Response 200
{
  "items": [...],
  "total": 50,
  "page": 1,
  "page_size": 20
}
```

### POST /api/tasks - 新增任务

```json
{
  "title": "任务标题",
  "description": "描述",
  "detail_content": "# Markdown 详情",
  "priority": "高",
  "due_date": "2026-04-01T00:00:00",
  "is_indefinite": false
}
```

### GET /api/tasks/{id} - 获取单个任务

### PUT /api/tasks/{id} - 编辑任务

### DELETE /api/tasks/{id} - 删除任务（软删除）

### PATCH /api/tasks/{id}/status - 切换状态

```json
{ "status": "进行中" }
```

允许的状态流转:
- 待办 → 进行中、已取消
- 进行中 → 已完成、待办
- 已完成 → 进行中
- 已取消 → 待办

### GET /api/tasks/sort - 获取排序信息

### PUT /api/tasks/sort - 保存拖拽排序

```json
{ "task_ids": [3, 1, 5, 2] }
```

### GET /api/tasks/stats - 获取任务统计

### GET /api/tasks/trash - 回收站列表

### POST /api/tasks/{id}/restore - 恢复任务

### DELETE /api/tasks/{id}/permanent - 永久删除

## 附件接口

### POST /api/tasks/{task_id}/attachments - 上传附件

`multipart/form-data`，字段名 `file`

需要 Bearer Token 认证。

### GET /api/tasks/{task_id}/attachments - 获取附件列表

需要 Bearer Token 认证。

### GET /api/attachments/{id}/download - 下载附件

**需要认证**：支持以下两种方式
1. Authorization header: `Authorization: Bearer <token>`
2. Query 参数: `token=<token>`

查询参数: `preview=true` 内联显示（用于图片预览、视频播放）

### DELETE /api/attachments/{id} - 删除附件

需要 Bearer Token 认证。

## 管理员接口

所有管理员接口需要管理员权限。

### GET /api/admin/users - 用户列表

### PATCH /api/admin/users/{id} - 禁用/启用/解锁用户

```json
{ "is_active": false }  // 或 { "unlock": true }
```

### POST /api/admin/users/{id}/reset-password - 重置密码

### GET /api/admin/stats - 系统统计

### GET /api/admin/config - 获取系统配置

### PUT /api/admin/config - 更新系统配置

## 备份恢复接口

### POST /api/admin/backup/export - 导出备份

### GET /api/admin/backup/download/{filename} - 下载备份

### POST /api/admin/backup/import - 导入备份

### GET /api/admin/backup/list - 备份列表

### DELETE /api/admin/backup/delete/{filename} - 删除指定备份

### DELETE /api/admin/backup/delete-all - 删除所有备份

## 错误码

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 请求参数错误 |
| 401 | 未认证或 Token 失效 |
| 403 | 权限不足 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
