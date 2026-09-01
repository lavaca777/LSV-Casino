import axios from 'axios'

const TOKEN_KEY = 'casino_token'
const USER_ID_KEY = 'casino_user_id'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authService = {
  async register({ email, username, password }) {
    const { data } = await api.post('/auth/register', { email, username, password })
    return data
  },

  async login({ email_or_username, password }) {
    const { data } = await api.post('/auth/login', { email_or_username, password })
    return data
  },

  async logout() {
    await api.post('/auth/logout')
  },

  async getCurrentUser(userId) {
    const { data } = await api.get(`/users/${userId}`)
    return data
  },
}

export const walletService = {
  async getWallet(userId) {
    const { data } = await api.get(`/users/${userId}/wallet`)
    return data
  },

  async requestLoan(userId) {
    const { data } = await api.post(`/users/${userId}/loans/request`)
    return data
  },

  async getLoansHistory(userId) {
    const { data } = await api.get(`/users/${userId}/loans/history`)
    return data
  },

  async requestWithdrawal(userId, amount) {
    const { data } = await api.post(`/users/${userId}/withdrawals/request`, { amount })
    return data
  },

  async getWithdrawals(userId) {
    const { data } = await api.get(`/users/${userId}/withdrawals`)
    return data
  },
}

export const userService = {
  async changePassword(userId, current_password, new_password) {
    const { data } = await api.put(`/users/${userId}/password`, {
      current_password,
      new_password,
    })
    return data
  },

  async updateProfile(userId, payload) {
    const { data } = await api.put(`/users/${userId}`, payload)
    return data
  },
}

export function saveAuth(token, userId) {
  localStorage.setItem(TOKEN_KEY, token)
  localStorage.setItem(USER_ID_KEY, userId)
}

export function clearAuth() {
  localStorage.removeItem(TOKEN_KEY)
  localStorage.removeItem(USER_ID_KEY)
}

export function getStoredToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function getStoredUserId() {
  return localStorage.getItem(USER_ID_KEY)
}
