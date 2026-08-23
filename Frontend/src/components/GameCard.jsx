import { useNavigate } from 'react-router-dom'

function GameCard({ game }) {
  const navigate = useNavigate()

  return (
    <button
      type="button"
      className="game-card"
      onClick={() => navigate(game.route)}
      title={game.name}
    >
      <span className="game-card-thumb" aria-hidden="true">
        {game.emoji}
      </span>
      <span className="game-card-name">{game.name}</span>
    </button>
  )
}

export default GameCard
