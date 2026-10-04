import { useEffect, useState } from 'react'

import { historyService } from '../services/api'
import { formatDateTime, resultLabel } from '../utils/format'

const SUIT_SYMBOL = {
  corazon: '♥',
  diamante: '♦',
  trebol: '♣',
  espada: '♠',
}
const RED_SUITS = new Set(['corazon', 'diamante'])

// Cada elemento de una mano puede ser una carta ({palo,rango}) o un dato
// de otro juego ({eleccion} / {moneda}). Se renderiza según corresponda.
function HandItem({ item }) {
  if (item.rango != null && item.palo != null) {
    const symbol = SUIT_SYMBOL[item.palo] ?? '?'
    const red = RED_SUITS.has(item.palo)
    return (
      <span className={`gh-card ${red ? 'gh-card-red' : 'gh-card-black'}`}>
        {item.rango}
        {symbol}
      </span>
    )
  }
  if (item.eleccion != null) return <span className="gh-chip">Elección: {item.eleccion}</span>
  if (item.moneda != null) return <span className="gh-chip">Salió: {item.moneda}</span>
  return null
}

function Hand({ title, cartas }) {
  if (!cartas || cartas.length === 0) return null
  return (
    <div className="gh-hand">
      <h4>{title}</h4>
      <div className="gh-cards">
        {cartas.map((c, i) => (
          <HandItem key={i} item={c} />
        ))}
      </div>
    </div>
  )
}

function GameDetail({ userId, sessionId, onClose }) {
  const [detail, setDetail] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    let cancelled = false
    historyService
      .detail(userId, sessionId)
      .then((data) => {
        if (!cancelled) {
          setDetail(data)
          setLoading(false)
        }
      })
      .catch(() => {
        if (!cancelled) {
          setError('No se pudo cargar el detalle')
          setLoading(false)
        }
      })
    return () => {
      cancelled = true
    }
  }, [userId, sessionId])

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div
        className="modal gh-detail"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-modal="true"
      >
        <div className="gh-detail-header">
          <h2 className="modal-title">Detalle de partida</h2>
          <button
            type="button"
            className="gh-detail-close"
            onClick={onClose}
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>

        {loading && <p className="gh-status">Cargando…</p>}
        {error && <p className="modal-error">{error}</p>}

        {detail && (
          <>
            <div className="gh-detail-grid">
              <span>Juego</span>
              <span>{detail.game_name}</span>
              <span>Fecha</span>
              <span>{formatDateTime(detail.date)}</span>
              <span>Apuesta</span>
              <span>${Number(detail.bet).toFixed(2)}</span>
              <span>Resultado</span>
              <span>{resultLabel(detail.result)}</span>
              <span>Payout</span>
              <span>${Number(detail.payout).toFixed(2)}</span>
              <span>Balance después</span>
              <span>${Number(detail.balance_after).toFixed(2)}</span>
              {detail.duration_seconds != null && (
                <>
                  <span>Duración</span>
                  <span>{detail.duration_seconds.toFixed(1)}s</span>
                </>
              )}
            </div>

            <Hand title="Tu mano" cartas={detail.player_hand} />
            {detail.bot_hands?.map((mano, i) => (
              <Hand key={i} title={`Bot ${i + 1}`} cartas={mano} />
            ))}
          </>
        )}
      </div>
    </div>
  )
}

export default GameDetail
