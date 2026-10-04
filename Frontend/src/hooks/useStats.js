import { useEffect, useState } from 'react'

import { statsService } from '../services/api'
import { useAuth } from './useAuth'

export function useStats() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!user) return

    let cancelled = false
    statsService
      .get(user.id)
      .then((data) => {
        if (!cancelled) {
          setStats(data)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('No se pudieron cargar las estadísticas')
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [user])

  return { stats, loading, error }
}
