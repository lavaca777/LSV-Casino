import { useState } from 'react'

import { useWallet } from '../hooks/useWallet'
import { getErrorMessage, gameService } from '../services/api'

const MIN_BET = 5

function CardLabel({ carta }) {
  return (
    <span className="bj-card">
      {carta.rango}
      {carta.palo.charAt(0).toUpperCase()}
    </span>
  )
}

function Hand({ title, cartas }) {
  return (
    <div className="bj-hand">
      <h3>{title}</h3>
      <div className="bj-cards">
        {cartas.map((c, i) => (
          <CardLabel key={i} carta={c} />
        ))}
      </div>
    </div>
  )
}

function BlackjackBoard() {
  const { balance, refresh } = useWallet()
  const [bet, setBet] = useState(String(MIN_BET))
  const [ronda, setRonda] = useState(null) // respuesta cruda del backend (start/hit/stand)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const enJuego = ronda?.turn === 'player'
  const terminada = ronda?.turn === 'done'

  const handleStart = async (e) => {
    e.preventDefault()
    setError(null)

    const amount = Number(bet)
    if (!bet || !Number.isFinite(amount) || amount <= 0) {
      setError('Ingresa un monto válido para apostar')
      return
    }

    setSubmitting(true)
    try {
      const data = await gameService.startBlackjack(amount)
      setRonda(data)
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'No se pudo iniciar la ronda'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleHit = async () => {
    if (!ronda?.session_id) return
    setError(null)
    setSubmitting(true)
    try {
      const data = await gameService.hitBlackjack(ronda.session_id)
      setRonda((prev) => ({
        ...prev,
        ...data,
        session_id: data.session_id ?? prev.session_id,
      }))
      if (data.turn === 'done') await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'No se pudo pedir carta'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleStand = async () => {
    if (!ronda?.session_id) return
    setError(null)
    setSubmitting(true)
    try {
      const data = await gameService.standBlackjack(ronda.session_id)
      setRonda((prev) => ({
        ...prev,
        ...data,
        session_id: data.session_id ?? prev.session_id,
      }))
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'No se pudo plantar'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleNuevaRonda = () => {
    setRonda(null)
    setError(null)
  }

  return (
    <div className="bj-board">
      <p className="bj-balance">Saldo: ${Number(balance).toFixed(2)}</p>

      {(!ronda || terminada) && (
        <form onSubmit={handleStart} className="bj-bet-form">
          <label htmlFor="bet">Apuesta (mínimo ${MIN_BET})</label>
          <input
            id="bet"
            type="number"
            min={MIN_BET}
            step="1"
            value={bet}
            onChange={(e) => setBet(e.target.value)}
            required
          />
          <button type="submit" disabled={submitting}>
            {submitting ? 'Repartiendo…' : 'Jugar'}
          </button>
        </form>
      )}

      {error && (
        <p className="bj-error" role="alert">
          {error}
        </p>
      )}

      {ronda && (
        <div className="bj-table">
          <Hand title="Tu mano" cartas={ronda.mano_jugador} />

          {ronda.manos_bots?.map((mano, i) => (
            <Hand key={i} title={`Bot ${i + 1}`} cartas={mano} />
          ))}

          {enJuego && (
            <div className="bj-actions">
              <button type="button" onClick={handleHit} disabled={submitting}>
                Pedir carta
              </button>
              <button type="button" onClick={handleStand} disabled={submitting}>
                Plantarse
              </button>
            </div>
          )}

          {terminada && (
            <div className={`bj-result bj-result-${ronda.resultado}`} role="status">
              <p>
                Resultado: <strong>{ronda.resultado}</strong>
              </p>
              {ronda.payout != null && <p>Payout: ${Number(ronda.payout).toFixed(2)}</p>}
              {ronda.nuevo_balance != null && (
                <p>Nuevo saldo: ${Number(ronda.nuevo_balance).toFixed(2)}</p>
              )}
              <button type="button" onClick={handleNuevaRonda}>
                Jugar de nuevo
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default BlackjackBoard
