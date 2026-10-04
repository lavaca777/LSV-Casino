import { useEffect, useState } from 'react'

import Footer from '../components/Footer'
import GameDetail from '../components/GameDetail'
import GameList from '../components/GameList'
import Navbar from '../components/Navbar'
import { useAuth } from '../hooks/useAuth'
import { useGameHistory } from '../hooks/useGameHistory'
import { gameService } from '../services/api'
import './home.css'
import './gamehistory.css'

function GameHistoryPage() {
  const { user } = useAuth()
  const {
    games,
    total,
    page,
    totalPages,
    gameFilter,
    loading,
    error,
    goToPage,
    changeFilter,
  } = useGameHistory()
  const [catalogo, setCatalogo] = useState([])
  const [selected, setSelected] = useState(null)

  // Catálogo de juegos para poblar el filtro.
  useEffect(() => {
    let cancelled = false
    gameService
      .listGames()
      .then((data) => {
        if (!cancelled) setCatalogo(data)
      })
      .catch(() => {
        if (!cancelled) setCatalogo([])
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="home-page">
      <Navbar />

      <main className="gh-main">
        <h1>Historial de partidas</h1>

        <div className="gh-toolbar">
          <label htmlFor="gh-filter">Filtrar por juego</label>
          <select
            id="gh-filter"
            value={gameFilter}
            onChange={(e) => changeFilter(e.target.value)}
          >
            <option value="">Todos</option>
            {catalogo.map((g) => (
              <option key={g.id} value={g.name}>
                {g.name}
              </option>
            ))}
          </select>
        </div>

        {error && (
          <p className="gh-error" role="alert">
            {error}
          </p>
        )}

        {loading ? (
          <p className="gh-status">Cargando…</p>
        ) : (
          <GameList games={games} onSelect={setSelected} />
        )}

        <div className="gh-pagination">
          <button
            type="button"
            onClick={() => goToPage(page - 1)}
            disabled={page <= 0 || loading}
          >
            ← Anterior
          </button>
          <span className="gh-page-info">
            Página {page + 1} de {totalPages} · {total} partidas
          </span>
          <button
            type="button"
            onClick={() => goToPage(page + 1)}
            disabled={page + 1 >= totalPages || loading}
          >
            Siguiente →
          </button>
        </div>
      </main>

      <Footer />

      {selected && (
        <GameDetail
          userId={user.id}
          sessionId={selected}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  )
}

export default GameHistoryPage
