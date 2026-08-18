import axios from './axios'

export const getTodos = (filter = 'all') =>
  axios.get('/todos', { params: { filter } }).then((res) => res.data)
export const createTodo = (payload) =>
  axios.post('/todos', payload).then((res) => res.data)
export const updateTodo = (id, data) =>
  axios.put(`/todos/${id}`, data).then((res) => res.data)
export const deleteTodo = (id) => axios.delete(`/todos/${id}`)
export const clearCompleted = () => axios.delete('/todos')
export const reorderTodos = (items) =>
  axios.patch('/todos/order', items).then((res) => res.data)