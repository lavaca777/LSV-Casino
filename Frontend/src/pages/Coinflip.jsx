import { useState } from 'react'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { useWallet } from '../hooks/useWallet'
import { getErrorMessage, gameService } from '../services/api'
import './home.css'
import './coinflip.css'

const MIN_BET = 5

function CoinflipPage() {
  const { balance, refresh } = useWallet()
  const [eleccion, setEleccion] = useState('cara')
  const [bet, setBet] = useState(String(MIN_BET))
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const handlePlay = async (e) => {
    e.preventDefault()
    setError(null)
    setResult(null)

    const amount = Number(bet)
    if (!bet || !Number.isFinite(amount) || amount <= 0) {
      setError('Ingresa un monto válido para apostar')
      return
    }

    setSubmitting(true)
    try {
      const data = await gameService.playCoinflip(amount, eleccion)
      setResult(data)
      await refresh()
    } catch (err) {
      setError(getErrorMessage(err, 'No se pudo jugar. Revisa tu apuesta.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="home-page">
      <Navbar />

      <main className="coinflip-main">
        <h1>Cara o Cruz</h1>
        <p className="coinflip-balance">Saldo: ${Number(balance).toFixed(2)}</p>

        <form className="coinflip-card" onSubmit={handlePlay}>
          <label>Elige</label>
          <div className="coinflip-choices">
            <button
              type="button"
              className={`coinflip-choice ${eleccion === 'cara' ? 'active' : ''}`}
              onClick={() => setEleccion('cara')}
            >
              🪙 Cara
            </button>
            <button
              type="button"
              className={`coinflip-choice ${eleccion === 'cruz' ? 'active' : ''}`}
              onClick={() => setEleccion('cruz')}
            >
              🪙 Cruz
            </button>
          </div>

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

          {error && <p className="coinflip-error" role="alert">{error}</p>}

          <button type="submit" className="coinflip-play" disabled={submitting}>
            {submitting ? 'Lanzando…' : 'Jugar'}
          </button>
        </form>

        {result && (
          <div className={`coinflip-result ${result.resultado}`} role="status">
            <p className="coinflip-coin">Salió: <strong>{result.moneda}</strong></p>
            <p className="coinflip-outcome">
              {result.resultado === 'win' ? '¡Ganaste!' : 'Perdiste'}
            </p>
            <p>Payout: ${Number(result.payout).toFixed(2)}</p>
            <p>Nuevo saldo: ${Number(result.nuevo_balance).toFixed(2)}</p>
          </div>
        )}
      </main>
      <Footer />
    </div>
  )
}

export default CoinflipPage
