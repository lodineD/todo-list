---

## 📋 完整项目规格说明书（Markdown 格式）

---

# Todo List 全栈应用 - 完整规格说明

## 项目概述

开发一个本地运行的 Todo List 全栈应用。后端使用 FastAPI + SQLModel + SQLite（异步），前端使用 Vue 3 + Axios + Vite。后端遵循低耦合、高内聚的分层架构。

---

## 🐍 后端技术栈

| 组件 | 技术选型 | 版本 |
|------|----------|------|
| Web 框架 | FastAPI | 0.110.0 |
| ASGI 服务器 | Uvicorn | 0.27.0 (with standard extras) |
| ORM | SQLModel | 0.0.14 |
| 异步数据库驱动 | aiosqlite | 0.19.0 |
| 依赖注入 | FastAPI Depends | 内置 |
| 数据库 | SQLite | 3.x |

---

## 🟢 前端技术栈

| 组件 | 技术选型 | 版本 |
|------|----------|------|
| 框架 | Vue 3 (Composition API) | 3.5.41 |
| 构建工具 | Vite | 8.2.1 |
| HTTP 客户端 | Axios | 1.6.0 |
| 插件 | @vitejs/plugin-vue | 6.0.8 |
| 插件 | vite-plugin-vue-devtools（脚手架自带） | 8.2.1 |
| 样式 | 原生 CSS | - |

> 注：前端已完成脚手架（create-vue），本地已安装上述版本，无需重装。Axios 尚未安装，需执行 `npm install axios`。

---

## 📁 文件清单

### 后端文件 (共 20 个)

| 文件路径 | 职责 |
|----------|------|
| `backend/requirements.txt` | Python 依赖列表 |
| `backend/main.py` | FastAPI 应用入口 |
| `backend/app/__init__.py` | 包标识 |
| `backend/app/core/__init__.py` | 包标识 |
| `backend/app/core/config.py` | 配置管理 (Settings) |
| `backend/app/core/database.py` | 数据库引擎和会话管理 |
| `backend/app/core/exceptions.py` | 自定义业务异常 |
| `backend/app/models/__init__.py` | 包标识 |
| `backend/app/models/todo.py` | Todo 数据表模型 |
| `backend/app/schemas/__init__.py` | 包标识 |
| `backend/app/schemas/todo.py` | Pydantic 请求/响应模型 |
| `backend/app/repositories/__init__.py` | 包标识 |
| `backend/app/repositories/todo_repository.py` | 数据库 CRUD 操作 |
| `backend/app/services/__init__.py` | 包标识 |
| `backend/app/services/todo_service.py` | 业务逻辑 |
| `backend/app/api/__init__.py` | 包标识 |
| `backend/app/api/v1/__init__.py` | 包标识 |
| `backend/app/api/v1/endpoints/__init__.py` | 包标识 |
| `backend/app/api/v1/endpoints/todo.py` | API 路由定义 |
| `backend/app/dependencies.py` | 依赖注入函数 |

### 前端文件 (共 9 个核心文件，脚手架已含部分)

| 文件路径 | 职责 | 状态 |
|----------|------|------|
| `frontend/index.html` | HTML 入口 | 现有，需改标题/图标 |
| `frontend/package.json` | npm 依赖和脚本 | 现有，需加 axios |
| `frontend/vite.config.js` | Vite 配置（含代理） | 现有，需补 proxy |
| `frontend/src/main.js` | Vue 应用入口 | 现有 |
| `frontend/src/App.vue` | 根组件 | 现有，需替换为 TodoApp |
| `frontend/src/style.css` | 全局样式 | 新建 |
| `frontend/src/components/TodoApp.vue` | 主业务组件 | 新建 |
| `frontend/src/api/axios.js` | Axios 实例封装 | 新建 |
| `frontend/src/api/todos.js` | API 方法导出 | 新建 |

> 脚手架还自带了 `frontend/jsconfig.json`、`frontend/.vscode/`、`frontend/public/favicon.ico`、`frontend/README.md` 等文件，本项目保留即可。

---

## 文件规格详情

### 后端规格

---

#### `backend/requirements.txt`

```
fastapi==0.110.0
uvicorn[standard]==0.27.0
sqlmodel==0.0.14
aiosqlite==0.19.0
python-multipart==0.0.6
```

---

#### `backend/app/core/config.py`

**职责**：管理应用配置，使用 Pydantic Settings。

**内容要求**：
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./todos.db"
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173"]
    API_V1_PREFIX: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
```

> 使用 pydantic v2 的 `SettingsConfigDict`（而非 v1 的 `class Config`），避免弃用警告。

---

#### `backend/app/core/database.py`

**职责**：创建异步数据库引擎和会话工厂。

**内容要求**：
- 使用 `sqlmodel.ext.asyncio.create_async_engine`
- 配置 `AsyncSessionLocal`
- 提供 `async def get_db() -> AsyncIterator[AsyncSession]` 依赖注入函数
- 导出 `async def init_db()` 用于创建表

---

#### `backend/app/core/exceptions.py`

**职责**：定义自定义业务异常。

**内容要求**：
```python
class TodoNotFoundError(Exception):
    """待办事项不存在"""
    pass

class TodoTitleEmptyError(Exception):
    """待办标题为空"""
    pass
```

---

#### `backend/app/models/todo.py`

**职责**：定义 SQLModel 数据表模型。

**内容要求**：
- 继承 `SQLModel` 和 `Tablename` 混入
- 字段：`id` (int, primary_key), `title` (str, min_length=1, max_length=100), `completed` (bool, default=False), `created_at` (datetime, default=datetime.now(timezone.utc))
- 设置 `table = True`

> 注：`datetime.now(timezone.utc)` 存入 SQLite 时保存为 UTC 时间，返回给前端为带时区的时间戳。如需展示本地时间，可在序列化时转换，或直接使用 `datetime.now(timezone.utc)` 作为统一 UTC 基准（本项目采用后者，保持简单）。

---

#### `backend/app/schemas/todo.py`

**职责**：定义 Pydantic 验证模型。

**内容要求**：
```python
from pydantic import BaseModel, Field
from datetime import datetime

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)

class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    completed: bool | None = None

class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: datetime

    model_config = {"from_attributes": True}
```

---

#### `backend/app/repositories/todo_repository.py`

**职责**：封装所有数据库 CRUD 操作。

**内容要求**：
- 所有方法为 `async`
- 方法列表：
  - `async def get_all(session: AsyncSession) -> List[Todo]`
  - `async def get_by_id(session: AsyncSession, todo_id: int) -> Todo | None`
  - `async def create(session: AsyncSession, todo_data: TodoCreate) -> Todo`
  - `async def update(session: AsyncSession, todo_id: int, todo_data: TodoUpdate) -> Todo | None`
  - `async def delete(session: AsyncSession, todo_id: int) -> bool`
  - `async def delete_completed(session: AsyncSession) -> int` (返回删除数量)
- 不包含业务逻辑判断（如标题是否为空由 Service 层处理）
- 使用 `select` 语句查询，排序按 `created_at.desc()`

---

#### `backend/app/services/todo_service.py`

**职责**：包含业务逻辑，调用 Repository。

**内容要求**：
- 构造器接收 `session` 参数
- 方法列表：
  - `async def get_all_todos(self) -> List[TodoResponse]`
  - `async def create_todo(self, todo_data: TodoCreate) -> TodoResponse`（如标题为空抛出 `TodoTitleEmptyError`）
  - `async def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> TodoResponse`（如不存在抛出 `TodoNotFoundError`）
  - `async def delete_todo(self, todo_id: int) -> None`（如不存在抛出 `TodoNotFoundError`）
  - `async def clear_completed(self) -> int`
- 调用 Repository 完成数据操作，返回 Pydantic 模型

---

#### `backend/app/api/v1/endpoints/todo.py`

**职责**：定义 FastAPI 路由。

**内容要求**：
- 使用 `APIRouter(prefix="/todos", tags=["todos"])`
- 路由列表：
  - `GET /` → 调用 service.get_all_todos()
  - `POST /` → 调用 service.create_todo()
  - `PUT /{todo_id}` → 调用 service.update_todo()
  - `DELETE /{todo_id}` → 调用 service.delete_todo()
  - `DELETE /` → 调用 service.clear_completed()
- 捕获 `TodoNotFoundError` 返回 404，`TodoTitleEmptyError` 返回 400
- 使用 `Depends(get_todo_service)` 注入 Service

---

#### `backend/app/dependencies.py`

**职责**：定义 FastAPI 依赖注入函数。

**内容要求**：
- `async def get_db() -> AsyncSession`（或从 database 导入）
- `def get_todo_service(session: AsyncSession = Depends(get_db)) -> TodoService`
- 可考虑使用 `async with` 管理会话生命周期

---

#### `backend/main.py`

**职责**：创建 FastAPI 应用，注册中间件和路由。

**内容要求**：
```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import todo
from app.core.config import settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todo.router, prefix=settings.API_V1_PREFIX)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

> 使用 lifespan 生命周期而非已弃用的 `@app.on_event("startup")`。

---

#### 所有 `__init__.py` 文件

**要求**：仅用于包标识，可以为空，也可以导出核心类方便导入。

---

### 前端规格

---

#### `frontend/vite.config.js`

**内容要求**：
```javascript
import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

---

#### `frontend/src/api/axios.js`

**职责**：封装 Axios 实例。

**内容要求**：
- 创建 `axios.create({ baseURL: '/api/v1', timeout: 10000 })`
- 配置响应拦截器统一处理错误
- 导出实例

---

#### `frontend/src/api/todos.js`

**职责**：导出所有 API 方法。

**内容要求**：
```javascript
import axios from './axios'

export const getTodos = () => axios.get('/todos').then(res => res.data)
export const createTodo = (title) => axios.post('/todos', { title }).then(res => res.data)
export const updateTodo = (id, data) => axios.put(`/todos/${id}`, data).then(res => res.data)
export const deleteTodo = (id) => axios.delete(`/todos/${id}`)
export const clearCompleted = () => axios.delete('/todos')
```

---

#### `frontend/src/components/TodoApp.vue`

**职责**：所有 UI 和交互逻辑。

**内容要求**：

**模板结构**：
1. 输入框 + 添加按钮（回车触发添加）
2. 待办列表（v-for 遍历）
   - 复选框 `v-model="todo.completed"` 触发更新
   - 文字（completed 时添加 `.completed` 类）
   - 删除按钮 `@click="handleDelete(todo.id)"`
   - 空状态显示 "暂无待办事项 🎉"
3. 底部统计：剩余未完成数量 + 清除已完成按钮

**脚本**：
- 使用 `<script setup>`
- 状态：`todos` (ref 数组), `newTitle` (ref 字符串)
- 计算属性：`remainingCount`
- 方法：`fetchTodos`, `handleAdd`, `handleToggle`, `handleUpdate`, `handleDelete`, `handleClearCompleted`
- 生命周期：`onMounted` 时调用 `fetchTodos`

**样式**（写在 `<style scoped>` 中）：
- 页面居中，最大宽度 600px，垂直居中
- 卡片背景白色，圆角阴影
- 已完成：灰色 + 删除线
- 删除按钮 hover 变红
- 输入框和按钮并排

---

#### `frontend/src/App.vue`

**内容要求**：
```vue
<template>
  <TodoApp />
</template>

<script setup>
import TodoApp from './components/TodoApp.vue'
</script>
```

---

#### `frontend/src/main.js`

**内容要求**：
```javascript
import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

createApp(App).mount('#app')
```

---

#### `frontend/index.html`

**内容要求**：
```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Todo List</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
  </body>
</html>
```

---

#### `frontend/package.json`

**内容要求**：
```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.5.40",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^6.0.8",
    "vite": "^8.1.5",
    "vite-plugin-vue-devtools": "^8.1.5"
  }
}
```

> 版本与现有脚手架安装一致，仅需额外新增 `axios` 依赖（执行 `npm install axios`）。

---

#### `frontend/src/style.css`

**职责**：全局样式重置和基础样式。

**内容要求**：
- 重置 margin/padding
- 设置 `font-family: sans-serif`
- 设置背景色为浅灰色
- 全局居中布局的基础样式

---

## 🚀 启动流程

```bash
# 后端 (首先按本文规格创建 backend/ 目录)
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 前端 (新终端)
cd frontend
npm install          # 已含 axios，无需单独安装
npm run dev
```

> 若使用 conda，可先 `conda create -n todo python=3.x` 并 `conda activate todo`，再执行 `pip install -r requirements.txt`。

---

## ✅ 验收标准

1. 后端启动后访问 `http://localhost:8000/docs` 可见 Swagger 文档
2. 前端访问 `http://localhost:5173` 可见 Todo List 界面
3. 可正常进行增删改查操作
4. 页面刷新后数据持久化（存储在 SQLite 中）

---
