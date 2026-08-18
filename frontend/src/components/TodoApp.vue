<script setup>
import { ref, computed, onMounted } from 'vue'
import { getTodos, createTodo, updateTodo, deleteTodo, clearCompleted } from '../api/todos'

const todos = ref([])
const newTitle = ref('')
const error = ref('')

const remainingCount = computed(
  () => todos.value.filter((todo) => !todo.completed).length
)

async function fetchTodos() {
  try {
    todos.value = await getTodos()
  } catch (e) {
    error.value = e.message
  }
}

async function handleAdd() {
  const title = newTitle.value.trim()
  if (!title) return
  try {
    const todo = await createTodo(title)
    todos.value.unshift(todo)
    newTitle.value = ''
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

    <div class="input-row">
      <input
        v-model="newTitle"
        class="todo-input"
        type="text"
        placeholder="添加一个新的待办事项..."
        maxlength="100"
        @keyup.enter="handleAdd"
      />
      <button class="add-btn" @click="handleAdd">添加</button>
    </div>

    <p v-if="error" class="error">⚠️ {{ error }}</p>

    <ul v-if="todos.length" class="todo-list">
      <li v-for="todo in todos" :key="todo.id" class="todo-item">
        <label class="todo-label">
          <input
            type="checkbox"
            class="todo-check"
            :checked="todo.completed"
            @change="handleToggle(todo)"
          />
          <span class="todo-text" :class="{ completed: todo.completed }">
            {{ todo.title }}
          </span>
        </label>
        <button class="delete-btn" @click="handleDelete(todo.id)">✕</button>
      </li>
    </ul>

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
  max-width: 600px;
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

.input-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.todo-input {
  flex: 1;
  padding: 0.6rem 0.8rem;
  font-size: 1rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}

.todo-input:focus {
  border-color: #42b983;
}

.add-btn {
  padding: 0.6rem 1.25rem;
  font-size: 1rem;
  color: #fff;
  background: #42b983;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
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
  justify-content: space-between;
  padding: 0.6rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.todo-label {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  cursor: pointer;
  flex: 1;
}

.todo-check {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: #42b983;
}

.todo-text {
  color: #333;
  word-break: break-word;
}

.todo-text.completed {
  color: #999;
  text-decoration: line-through;
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