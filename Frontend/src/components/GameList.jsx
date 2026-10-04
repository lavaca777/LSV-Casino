import { formatDateTime, resultLabel } from '../utils/format'

function GameList({ games, onSelect }) {
  if (games.length === 0) {
    return <p className="gh-empty">Todavía no has jugado ninguna partida.</p>
  }

  return (
    <div className="gh-table-wrap">
      <table className="gh-table">
        <thead>
          <tr>
            <th>Fecha</th>
            <th>Juego</th>
            <th>Apuesta</th>
            <th>Resultado</th>
            <th>Payout</th>
            <th>Balance</th>
          </tr>
        </thead>
        <tbody>
          {games.map((g) => (
            <tr key={g.id} className="gh-row" onClick={() => onSelect(g.id)}>
              <td>{formatDateTime(g.date)}</td>
              <td>{g.game_name}</td>
              <td>${Number(g.bet).toFixed(2)}</td>
              <td className={`gh-result gh-result-${g.result ?? 'none'}`}>
                {resultLabel(g.result)}
              </td>
              <td>${Number(g.payout).toFixed(2)}</td>
              <td>${Number(g.balance_after).toFixed(2)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default GameList
