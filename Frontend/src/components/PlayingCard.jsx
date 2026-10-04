const SUIT_SYMBOL = {
  corazon: '♥',
  diamante: '♦',
  trebol: '♣',
  espada: '♠',
}

const RED_SUITS = new Set(['corazon', 'diamante'])

function PlayingCard({ carta, delay = 0 }) {
  const symbol = SUIT_SYMBOL[carta.palo] ?? '?'
  const isRed = RED_SUITS.has(carta.palo)

  return (
    <div
      className={`card ${isRed ? 'card-red' : 'card-black'}`}
      style={{ animationDelay: `${delay}ms` }}
    >
      <span className="card-corner card-corner-tl">
        {carta.rango}
        <br />
        {symbol}
      </span>
      <span className="card-pip" aria-hidden="true">
        {symbol}
      </span>
      <span className="card-corner card-corner-br">
        {carta.rango}
        <br />
        {symbol}
      </span>
    </div>
  )
}

export function CardBack({ delay = 0 }) {
  return <div className="card card-back" style={{ animationDelay: `${delay}ms` }} />
}

export default PlayingCard