import { useEffect, useState } from 'react'

import GameCard from './GameCard'
import { gameService } from '../services/api'

// Mapeo de cada juego a su presentación en el frontend.
const GAME_UI = {
  blackjack: { title: 'Blackjack', emoji: '🂡', route: '/blackjack' },
  coinflip: { title: 'Cara o Cruz', emoji: '🪙', route: '/coinflip' },
}

function GameGrid() {
  const [games, setGames] = useState([])

  useEffect(() => {
    let cancelled = false
    gameService
      .listGames()
      .then((data) => {
        if (!cancelled) setGames(data)
      })
      .catch(() => {
        if (!cancelled) setGames([])
      })
    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div className="game-grid">
      {games.map((game) => {
        const ui = GAME_UI[game.name] || {}
        return (
          <GameCard
            key={game.id}
            game={{
              id: game.id,
              name: ui.title || game.name,
              emoji: ui.emoji || '🎲',
              route: ui.route || '/home',
            }}
          />
        )
      })}
    </div>
  )
}

export default GameGrid
