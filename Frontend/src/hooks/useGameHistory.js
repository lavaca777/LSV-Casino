import { useEffect, useState } from 'react'

import { historyService } from '../services/api'
import { useAuth } from './useAuth'

export const PAGE_SIZE = 20

export function useGameHistory() {
  const { user } = useAuth()
  const [games, setGames] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [gameFilter, setGameFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!user) return

    let cancelled = false
    historyService
      .list(user.id, {
        limit: PAGE_SIZE,
        offset: page * PAGE_SIZE,
        game: gameFilter || undefined,
      })
      .then((data) => {
        if (cancelled) return
        setGames(data.games)
        setTotal(data.total)
        setLoading(false)
      })
      .catch(() => {
        if (cancelled) return
        setGames([])
        setTotal(0)
        setError('No se pudo cargar el historial')
        setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [user, page, gameFilter])

  // Los handlers marcan el estado de carga (no el effect, para evitar renders
  // en cascada).
  const goToPage = (nuevaPagina) => {
    setLoading(true)
    setError(null)
    setPage(nuevaPagina)
  }

  const changeFilter = (juego) => {
    setLoading(true)
    setError(null)
    setGameFilter(juego)
    setPage(0)
  }

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  return {
    games,
    total,
    page,
    totalPages,
    gameFilter,
    loading,
    error,
    goToPage,
    changeFilter,
  }
}
