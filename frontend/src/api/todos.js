import axios from './axios'

export const getTodos = () => axios.get('/todos').then((res) => res.data)
export const createTodo = (title) =>
  axios.post('/todos', { title }).then((res) => res.data)
export const updateTodo = (id, data) =>
  axios.put(`/todos/${id}`, data).then((res) => res.data)
export const deleteTodo = (id) => axios.delete(`/todos/${id}`)
export const clearCompleted = () => axios.delete('/todos')