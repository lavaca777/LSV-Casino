import { useEffect, useState } from 'react'

import { useWallet } from '../hooks/useWallet'
import { getErrorMessage, gameService } from '../services/api'
import BotAvatar from './BotAvatar'
import PlayingCard, { CardBack } from './PlayingCard'

const MIN_BET = 5

const BOTS = [
  { id: 'bot-1', name: 'UNIT // 01', style: 'emoji' },
  { id: 'bot-2', name: 'UNIT // 02', style: 'kaomoji' },
]
const REVEAL_STEP_MS = 700
const REVEAL_START_MS = 500
const RESULT_DELAY_MS = 500

function handValue(cartas) {
  let total = 0
  let ases = 0
  for (const c of cartas) {
    if (['J', 'Q', 'K'].includes(c.rango)) total += 10
    else if (c.rango === 'A') {
      ases += 1
      total += 11
    } else total += Number(c.rango)
  }
  while (total > 21 && ases > 0) {
    total -= 10
    ases -= 1
  }
  return total
}

function botMood(botHand, jugadorTotal, jugadorPasado) {
  const botTotal = handValue(botHand)
  if (botTotal > 21) return 'lose' 
  if (jugadorPasado) return 'win'
  if (botTotal > jugadorTotal) return 'win'
  if (botTotal < jugadorTotal) return 'lose'
  return 'tie'
}

function resultLabel(resultado) {
  if (resultado === 'win') return 'Ganaste'
  if (resultado === 'draw') return 'Empate'
  return 'Perdiste'
}

function BlackjackBoard() {
  const { balance, refresh } = useWallet()
  const [bet, setBet] = useState(String(MIN_BET))
  const [ronda, setRonda] = useState(null)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)
  const [revealedBots, setRevealedBots] = useState(0)
  const [showResult, setShowResult] = useState(false)

  const enJuego = ronda?.turn === 'player'
  const terminada = ronda?.turn === 'done'

  useEffect(() => {
    if (!terminada || !ronda?.manos_bots) {
      setRevealedBots(0)
      setShowResult(false)
      return undefined
    }

    setRevealedBots(0)
    setShowResult(false)
    const timers = []
    ronda.manos_bots.forEach((_, i) => {
      timers.push(
        setTimeout(
          () => setRevealedBots((n) => Math.max(n, i + 1)),
          REVEAL_START_MS + i * REVEAL_STEP_MS
        )
      )
    })
    timers.push(
      setTimeout(
        () => setShowResult(true),
        REVEAL_START_MS + ronda.manos_bots.length * REVEAL_STEP_MS + RESULT_DELAY_MS
      )
    )
    return () => timers.forEach(clearTimeout)
  }, [terminada, ronda?.resultado])

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

  const jugadorTotal = ronda ? handValue(ronda.mano_jugador) : 0
  const jugadorPasado = jugadorTotal > 21

  return (
    <div className="bj-page">
      <p className="bj-balance">Saldo: ${Number(balance).toFixed(2)}</p>

      <div className="bj-table">
        <div className="bj-shoe" aria-hidden="true" />

        <div className="bj-seats">
          {BOTS.map((bot, i) => {
            const hand = ronda?.manos_bots?.[i]
            const revealed = terminada && revealedBots > i

            return (
              <div className="bj-seat" key={bot.id}>
                <BotAvatar
                  name={bot.name}
                  style={bot.style}
                  mood={
                    !terminada
                      ? 'idle'
                      : !revealed
                        ? 'thinking'
                        : botMood(hand ?? [], jugadorTotal, jugadorPasado)
                  }
                />
                <div className="bj-hand bj-hand-bot">
                  {revealed && hand
                    ? hand.map((c, idx) => (
                        <PlayingCard key={idx} carta={c} delay={idx * 150} />
                      ))
                    : ronda && (
                        <>
                          <CardBack />
                          <CardBack delay={80} />
                        </>
                      )}
                </div>
              </div>
            )
          })}
        </div>

        <h1 className="bj-title">Blackjack</h1>

        {!ronda && (
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
          <div className="bj-player-seat">
            <div className="bj-hand">
              {ronda.mano_jugador.map((c, idx) => (
                <PlayingCard key={idx} carta={c} delay={idx * 120} />
              ))}
            </div>
            <span className="bj-hand-total">{jugadorTotal}</span>

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

            {terminada && !showResult && (
              <p className="bj-waiting">Revelando mesa…</p>
            )}

            {terminada && showResult && (
              <div className={`bj-result bj-result-${ronda.resultado}`} role="status">
                <p className="bj-result-line">{resultLabel(ronda.resultado)}</p>
                {ronda.payout != null && (
                  <p>Payout: ${Number(ronda.payout).toFixed(2)}</p>
                )}
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
    </div>
  )
}

export default BlackjackBoard