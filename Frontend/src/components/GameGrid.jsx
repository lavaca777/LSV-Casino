import GameCard from './GameCard'

const GAMES = [
  { id: 'blackjack', name: 'Blackjack', emoji: '🂡', route: '/blackjack' },
]

function GameGrid() {
  return (
    <div className="game-grid">
      {GAMES.map((game) => (
        <GameCard key={game.id} game={game} />
      ))}
    </div>
  )
}

export default GameGrid
