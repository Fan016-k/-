# 网易云音乐用户标签服务

## 项目简介

网易云音乐用户标签服务是一个RESTful API，用于管理用户的兴趣标签。该服务支持添加、查询和删除用户标签，以便更好地理解用户偏好，为个性化推荐提供数据支持。

## 功能特点

- 为用户添加一个或多个标签
- 获取用户的所有标签
- 删除用户的特定标签
- 查找拥有特定标签的所有用户
- 支持无标签用户创建和管理
- 数据持久化存储

## 技术栈

- **后端**: Python + FastAPI
- **数据存储**: JSON文件 (可扩展至数据库)
- **文档**: OpenAPI (Swagger UI)
- **前端界面**: HTML + JavaScript

## API文档

### 基础信息

- **基础URL**: `http://localhost:8000`
- **内容类型**: 所有请求和响应均使用JSON格式
- **字符编码**: UTF-8

### 统一响应格式

所有API响应遵循以下统一格式：

```json
{
  "status": "成功|错误",
  "message": "描述信息",
  "data": { /* 响应数据对象，可选 */ }
}
```

### API端点

#### 1. 健康检查

**请求**

```
GET /ping
```

**响应**

成功响应 (200 OK)

```json
{
  "status": "成功",
  "message": "用户标签服务正在运行"
}
```

#### 2. 获取用户标签

**请求**

```
GET /users/{user_id}/tags
```

**路径参数**

| 参数     | 类型   | 必填 | 描述       |
| -------- | ------ | ---- | ---------- |
| user_id  | string | 是   | 用户唯一ID |

**响应**

成功响应 - 用户有标签 (200 OK)

```json
{
  "status": "成功",
  "message": "成功获取标签",
  "data": {
    "user_id": "user123",
    "tags": [
      "摇滚爱好者",
      "音乐发烧友"
    ]
  }
}
```

成功响应 - 用户无标签 (200 OK)

```json
{
  "status": "成功",
  "message": "用户没有标签",
  "data": {
    "user_id": "user4",
    "tags": []
  }
}
```

#### 3. 添加用户标签

**请求**

```
POST /users/{user_id}/tags
```

**路径参数**

| 参数     | 类型   | 必填 | 描述       |
| -------- | ------ | ---- | ---------- |
| user_id  | string | 是   | 用户唯一ID |

**请求头**

```
Content-Type: application/json
```

**请求体**

```json
{
  "tags": ["摇滚乐迷", "交响乐爱好者", "ACG爱好者"]
}
```

**响应**

成功响应 (201 Created)

```json
{
  "status": "成功",
  "message": "标签添加成功",
  "data": {
    "user_id": "user3",
    "tags": ["摇滚乐迷", "交响乐爱好者", "ACG爱好者"]
  }
}
```

#### 4. 创建用户（无标签）

**请求**

```
POST /users/{user_id}
```

**路径参数**

| 参数     | 类型   | 必填 | 描述       |
| -------- | ------ | ---- | ---------- |
| user_id  | string | 是   | 用户唯一ID |

**响应**

成功响应 (201 Created)

```json
{
  "status": "成功",
  "message": "用户创建成功",
  "data": {
    "user_id": "user1",
    "tags": []
  }
}
```

#### 5. 删除用户标签

**请求**

```
DELETE /users/{user_id}/tags/{tag}
```

**路径参数**

| 参数     | 类型   | 必填 | 描述                 |
| -------- | ------ | ---- | -------------------- |
| user_id  | string | 是   | 用户唯一ID           |
| tag      | string | 是   | 要删除的标签（URL编码） |

**响应**

成功响应 (200 OK)

```json
{
  "status": "成功",
  "message": "成功删除标签 '交响乐爱好者'",
  "data": {
    "user_id": "user123",
    "removed_tag": "交响乐爱好者"
  }
}
```

错误响应 (404 Not Found)

```json
{
  "detail": "用户 'user123' 没有标签 '古典乐'"
}
```

#### 6. 查找拥有特定标签的用户

**请求**

```
GET /tags/{tag}/users
```

**路径参数**

| 参数 | 类型   | 必填 | 描述                 |
| ---- | ------ | ---- | -------------------- |
| tag  | string | 是   | 要查找的标签（URL编码） |

**响应**

成功响应 (200 OK)

```json
{
  "status": "成功",
  "message": "成功获取拥有标签 '摇滚乐迷' 的用户",
  "data": {
    "tag": "摇滚乐迷",
    "users": ["user3", "user4"]
  }
}
```

#### 7. 获取所有标签

**请求**

```
GET /tags
```

**响应**

成功响应 (200 OK)

```json
{
  "status": "成功",
  "message": "成功获取所有标签",
  "data": {
    "tags": ["摇滚乐迷", "夜猫子", "ACG爱好者", "古典乐迷", "电子乐迷"]
  }
}
```

#### 8. 获取所有用户

**请求**

```
GET /users
```

**响应**

成功响应 (200 OK)

```json
{
  "status": "成功",
  "message": "成功获取所有用户",
  "data": {
    "users": ["user1", "user2", "user123"]
  }
}
```

### 状态码说明

| 状态码 | 说明                                           |
| ------ | ---------------------------------------------- |
| 200    | 成功 - 请求成功处理                           |
| 201    | 已创建 - 资源创建成功                         |
| 400    | 错误请求 - 请求参数有误或缺失                 |
| 404    | 未找到 - 请求的资源不存在                     |
| 500    | 服务器内部错误 - 服务器处理请求时发生意外错误 |

## 本地开发环境搭建

请参考 [本地开发环境搭建与服务运行手册](./本地开发环境搭建与服务运行手册.md) 获取详细说明。

## 使用示例

### 使用curl示例

```bash
# 健康检查
curl http://localhost:8000/ping

# 创建用户（无标签）
curl -X POST http://localhost:8000/users/test_user

# 添加用户标签
curl -X POST http://localhost:8000/users/user4/tags -H "Content-Type: application/json" -d "{\"tags\": [\"摇滚乐迷\"]}"

# 获取用户标签
curl http://localhost:8000/users/test_user/tags

# 删除用户标签
curl -X DELETE http://localhost:8000/users/test_user/tags/交响乐爱好者

# 查找拥有特定标签的用户
curl http://localhost:8000/tags/摇滚乐迷/users
# 显示所有标签
curl http://localhost:8000/tags
# 显示所有用户
curl http://localhost:8000/users
```

### 使用HTML界面

项目包含一个HTML界面 (`tag-manager.html`)，提供用户友好的图形界面来管理用户标签。

