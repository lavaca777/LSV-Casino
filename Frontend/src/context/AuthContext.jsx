import { useCallback, useEffect, useState } from 'react'

import {
  authService,
  clearAuth,
  getStoredToken,
  getStoredUserId,
  saveAuth,
} from '../services/api'
import { AuthContext } from './authContextValue'

export function AuthProvider({ children }) {
  const [hasStoredSession] = useState(() => Boolean(getStoredToken() && getStoredUserId()))
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(hasStoredSession)

  useEffect(() => {
    if (!hasStoredSession) return

    const userId = getStoredUserId()
    authService
      .getCurrentUser(userId)
      .then(setUser)
      .catch(() => {
        clearAuth()
        setUser(null)
      })
      .finally(() => setLoading(false))
  }, [hasStoredSession])

  const login = useCallback(async (email_or_username, password) => {
    const data = await authService.login({ email_or_username, password })
    saveAuth(data.access_token, data.user_id)
    const currentUser = await authService.getCurrentUser(data.user_id)
    setUser(currentUser)
    setLoading(false)
    return currentUser
  }, [])

  const register = useCallback(async ({ email, username, password }) => {
    const data = await authService.register({ email, username, password })
    saveAuth(data.access_token, data.user_id)
    const currentUser = await authService.getCurrentUser(data.user_id)
    setUser(currentUser)
    setLoading(false)
    return currentUser
  }, [])

  const logout = useCallback(async () => {
    try {
      await authService.logout()
    } catch {
      // el token se invalida igual en el cliente
    } finally {
      clearAuth()
      setUser(null)
      setLoading(false)
    }
  }, [])

  const value = { user, loading, login, register, logout }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
