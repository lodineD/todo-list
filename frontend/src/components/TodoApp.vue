<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  getTodos,
  createTodo,
  updateTodo,
  deleteTodo,
  clearCompleted,
} from '../api/todos'

// 明天日期（添加表单默认截止日期）
function tomorrow() {
  const d = new Date()
  d.setDate(d.getDate() + 1)
  return d.toISOString().slice(0, 10)
}

const todos = ref([])
const error = ref('')

// 添加表单状态
const newTitle = ref('')
const newDueDate = ref(tomorrow())
const newPriority = ref('medium')
const newCategory = ref('')

// 当前筛选
const currentFilter = ref('all')
const FILTERS = [
  { key: 'all', label: '全部' },
  { key: 'today', label: '今天' },
  { key: 'overdue', label: '逾期' },
  { key: 'completed', label: '已完成' },
]

const todayStr = computed(() => new Date().toISOString().slice(0, 10))

// 统计（基于当前筛选结果计算）
const totalCount = computed(() => todos.value.length)
const completedCount = computed(() => todos.value.filter((t) => t.completed).length)
const overdueCount = computed(
  () => todos.value.filter((t) => !t.completed && t.due_date && t.due_date < todayStr.value).length
)
const todayCount = computed(
  () => todos.value.filter((t) => t.due_date === todayStr.value).length
)
const remainingCount = computed(() => todos.value.filter((t) => !t.completed).length)

// 优先级色标
const PRIORITY_CLASS = {
  urgent: 'p-urgent',
  high: 'p-high',
  medium: 'p-medium',
  low: 'p-low',
}

function isOverdue(todo) {
  return !todo.completed && todo.due_date && todo.due_date < todayStr.value
}

async function fetchTodos() {
  try {
    todos.value = await getTodos(currentFilter.value)
  } catch (e) {
    error.value = e.message
  }
}

function switchFilter(key) {
  currentFilter.value = key
  fetchTodos()
}

async function handleAdd() {
  const title = newTitle.value.trim()
  if (!title) return
  try {
    const payload = { title, priority: newPriority.value }
    if (newDueDate.value) payload.due_date = newDueDate.value
    if (newCategory.value.trim()) payload.category = newCategory.value.trim()
    await createTodo(payload)
    newTitle.value = ''
    newCategory.value = ''
    newDueDate.value = tomorrow()
    newPriority.value = 'medium'
    await fetchTodos()
  } catch (e) {
    error.value = e.message
  }
}

async function handleToggle(todo) {
  try {
    const updated = await updateTodo(todo.id, { completed: !todo.completed })
    const idx = todos.value.findIndex((t) => t.id === todo.id)
    if (idx !== -1) todos.value[idx] = updated
  } catch (e) {
    error.value = e.message
  }
}

async function handleDelete(id) {
  try {
    await deleteTodo(id)
    todos.value = todos.value.filter((t) => t.id !== id)
  } catch (e) {
    error.value = e.message
  }
}

async function handleClearCompleted() {
  try {
    await clearCompleted()
    todos.value = todos.value.filter((t) => !t.completed)
  } catch (e) {
    error.value = e.message
  }
}

onMounted(fetchTodos)
</script>

<template>
  <main class="todo-app">
    <h1 class="title">📝 待办事项</h1>

    <!-- 统计栏 -->
    <div class="stats-bar">
      <div class="stat">
        <span class="stat-num">{{ totalCount }}</span>
        <span class="stat-label">总任务</span>
      </div>
      <div class="stat">
        <span class="stat-num">{{ todayCount }}</span>
        <span class="stat-label">今天</span>
      </div>
      <div class="stat stat-overdue">
        <span class="stat-num">{{ overdueCount }}</span>
        <span class="stat-label">逾期</span>
      </div>
      <div class="stat stat-done">
        <span class="stat-num">{{ completedCount }}</span>
        <span class="stat-label">已完成</span>
      </div>
    </div>

    <!-- 筛选按钮 -->
    <div class="filter-row">
      <button
        v-for="f in FILTERS"
        :key="f.key"
        class="filter-btn"
        :class="{ active: currentFilter === f.key }"
        @click="switchFilter(f.key)"
      >
        {{ f.label }}
      </button>
    </div>

    <!-- 添加表单 -->
    <div class="add-form">
      <input
        v-model="newTitle"
        class="todo-input"
        type="text"
        placeholder="添加一个新的待办事项..."
        maxlength="100"
        @keyup.enter="handleAdd"
      />
      <div class="add-fields">
        <label class="field">
          <span class="field-label">截止</span>
          <input v-model="newDueDate" class="field-input" type="date" />
        </label>
        <label class="field">
          <span class="field-label">优先级</span>
          <select v-model="newPriority" class="field-input">
            <option value="low">低</option>
            <option value="medium">中</option>
            <option value="high">高</option>
            <option value="urgent">紧急</option>
          </select>
        </label>
        <label class="field">
          <span class="field-label">分类</span>
          <input v-model="newCategory" class="field-input" type="text" placeholder="可选" maxlength="50" />
        </label>
        <button class="add-btn" @click="handleAdd">添加</button>
      </div>
    </div>

    <p v-if="error" class="error">⚠️ {{ error }}</p>

    <!-- 任务列表 -->
    <div v-if="todos.length" class="todo-list">
      <div v-for="todo in todos" :key="todo.id" class="todo-item" :class="{ 'is-overdue': isOverdue(todo) }">
        <span class="prio-dot" :class="PRIORITY_CLASS[todo.priority]" :title="'优先级：' + todo.priority"></span>
        <label class="todo-label">
          <input
            type="checkbox"
            class="todo-check"
            :checked="todo.completed"
            @change="handleToggle(todo)"
          />
          <div class="todo-body">
            <span class="todo-text" :class="{ completed: todo.completed }">
              {{ todo.title }}
            </span>
            <div class="todo-meta">
              <span v-if="todo.category" class="badge badge-category">{{ todo.category }}</span>
              <span v-if="todo.due_date" class="badge badge-date" :class="{ 'badge-warn': isOverdue(todo) }">
                {{ isOverdue(todo) ? '⚠️ ' : '📅 ' }}{{ todo.due_date }}
              </span>
            </div>
            <p v-if="todo.description" class="todo-desc">{{ todo.description }}</p>
          </div>
        </label>
        <button class="delete-btn" @click="handleDelete(todo.id)">✕</button>
      </div>
    </div>

    <p v-else class="empty">暂无待办事项 🎉</p>

    <footer v-if="todos.length" class="footer">
      <span>剩余 {{ remainingCount }} 项未完成</span>
      <button class="clear-btn" @click="handleClearCompleted">清除已完成</button>
    </footer>
  </main>
</template>

<style scoped>
.todo-app {
  width: 100%;
  max-width: 640px;
  margin: 0 auto;
  padding: 2rem;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
}

.title {
  margin: 0 0 1.5rem;
  font-size: 1.75rem;
  text-align: center;
  color: #333;
}

/* 统计栏 */
.stats-bar {
  display: flex;
  justify-content: space-around;
  padding: 0.75rem 0;
  margin-bottom: 1rem;
  background: #f7f7f7;
  border-radius: 10px;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-num {
  font-size: 1.4rem;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 0.78rem;
  color: #888;
}

.stat-overdue .stat-num {
  color: #d9534f;
}

.stat-done .stat-num {
  color: #42b983;
}

/* 筛选 */
.filter-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.filter-btn {
  flex: 1;
  padding: 0.45rem 0;
  font-size: 0.9rem;
  color: #666;
  background: #f0f0f0;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.filter-btn:hover {
  background: #e0e0e0;
}

.filter-btn.active {
  background: #42b983;
  color: #fff;
}

/* 添加表单 */
.add-form {
  margin-bottom: 1rem;
}

.todo-input {
  width: 100%;
  padding: 0.6rem 0.8rem;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  margin-bottom: 0.5rem;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.todo-input:focus {
  border-color: #42b983;
}

.add-fields {
  display: flex;
  gap: 0.5rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.field-label {
  font-size: 0.72rem;
  color: #999;
}

.field-input {
  padding: 0.4rem 0.5rem;
  font-size: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
}

.field-input:focus {
  border-color: #42b983;
}

.add-btn {
  padding: 0.5rem 1.25rem;
  font-size: 0.95rem;
  color: #fff;
  background: #42b983;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
  height: 36px;
}

.add-btn:hover {
  background: #36a06c;
}

.error {
  color: #d9534f;
  font-size: 0.9rem;
  margin: 0 0 1rem;
}

.todo-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.4rem;
  border-bottom: 1px solid #f0f0f0;
}

.todo-item.is-overdue {
  background: #fef5f4;
}

/* 优先级色标 */
.prio-dot {
  flex-shrink: 0;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.p-urgent {
  background: #c0392b;
}

.p-high {
  background: #e74c3c;
}

.p-medium {
  background: #f39c12;
}

.p-low {
  background: #bdc3c7;
}

.todo-label {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  cursor: pointer;
  flex: 1;
}

.todo-check {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  cursor: pointer;
  accent-color: #42b983;
  flex-shrink: 0;
}

.todo-body {
  flex: 1;
  min-width: 0;
}

.todo-text {
  color: #333;
  word-break: break-word;
}

.todo-text.completed {
  color: #999;
  text-decoration: line-through;
}

.todo-meta {
  display: flex;
  gap: 0.4rem;
  margin-top: 0.25rem;
  flex-wrap: wrap;
}

.badge {
  font-size: 0.72rem;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  background: #eee;
  color: #555;
}

.badge-category {
  background: #e8f4fd;
  color: #2980b9;
}

.badge-date {
  background: #f0f0f0;
  color: #777;
}

.badge-warn {
  background: #fde8e6;
  color: #d9534f;
}

.todo-desc {
  margin: 0.25rem 0 0;
  font-size: 0.8rem;
  color: #999;
  word-break: break-word;
}

.delete-btn {
  background: none;
  border: none;
  font-size: 1rem;
  color: #999;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;
  flex-shrink: 0;
}

.delete-btn:hover {
  color: #d9534f;
  background: #fdeceb;
}

.empty {
  text-align: center;
  color: #999;
  padding: 2rem 0;
  margin: 0;
}

.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 1rem;
  font-size: 0.9rem;
  color: #666;
}

.clear-btn {
  background: none;
  border: none;
  color: #d9534f;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  transition: background 0.2s;
}

.clear-btn:hover {
  background: #fdeceb;
}
</style>