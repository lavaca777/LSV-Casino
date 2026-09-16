import { useCallback, useEffect, useState } from 'react'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { useAuth } from '../hooks/useAuth'
import { useWallet } from '../hooks/useWallet'
import { getErrorMessage, walletService } from '../services/api'
import './home.css'
import './wallet.css'

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('es', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function WalletPage() {
  const { user } = useAuth()
  const { balance, totalWagered, refresh } = useWallet()
  const [loans, setLoans] = useState([])
  const [withdrawals, setWithdrawals] = useState([])
  const [withdrawalAmount, setWithdrawalAmount] = useState('')
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const reloadHistory = useCallback(async () => {
    if (!user) return
    const [loanData, withdrawalData] = await Promise.all([
      walletService.getLoansHistory(user.id),
      walletService.getWithdrawals(user.id),
    ])
    setLoans(loanData)
    setWithdrawals(withdrawalData)
  }, [user])

  useEffect(() => {
    if (!user) return
    let cancelled = false
    Promise.all([
      walletService.getLoansHistory(user.id),
      walletService.getWithdrawals(user.id),
    ])
      .then(([loanData, withdrawalData]) => {
        if (cancelled) return
        setLoans(loanData)
        setWithdrawals(withdrawalData)
      })
      .catch(() => {
        if (!cancelled) {
          setLoans([])
          setWithdrawals([])
        }
      })
    return () => {
      cancelled = true
    }
  }, [user])
  const handleWithdrawal = async (e) => {
    e.preventDefault()
    setError(null)
    setMessage(null)

    const amount = Number(withdrawalAmount)
    if (!withdrawalAmount || !Number.isFinite(amount) || amount <= 0) {
      setError('Ingresa un monto válido para retirar')
      return
    }

    setSubmitting(true)
    try {
      await walletService.requestWithdrawal(user.id, amount)
      setWithdrawalAmount('')
      setMessage('Retiro aprobado')
      await Promise.all([refresh(), reloadHistory()])
    } catch (err) {
      setError(getErrorMessage(err, 'No se pudo solicitar el retiro'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="home-page">
      <Navbar />

      <main className="wallet-main">
        <h1>Billetera</h1>

        <section className="wallet-balance-card">
          <div className="wallet-balance-amount">${Number(balance).toFixed(2)}</div>
          <div className="wallet-balance-label">Saldo disponible</div>
          <div className="wallet-total-wagered">
            Total apostado histórico: ${Number(totalWagered).toFixed(2)}
          </div>
        </section>

        <section className="wallet-card">
          <h2>Solicitar retiro</h2>
          <form onSubmit={handleWithdrawal} noValidate>
            <input
              type="number"
              min="1"
              step="0.01"
              value={withdrawalAmount}
              onChange={(e) => setWithdrawalAmount(e.target.value)}
              placeholder="Monto a retirar (ficticio)"
              required
            />
            {error && <p className="wallet-error" role="alert">{error}</p>}
            {message && <p className="wallet-success" role="status">{message}</p>}
            <button type="submit" disabled={submitting}>
              {submitting ? 'Solicitando…' : 'Solicitar retiro'}
            </button>
          </form>
        </section>

        <section className="wallet-card">
          <h2>Historial de préstamos</h2>
          {loans.length === 0 ? (
            <p className="wallet-empty">Aún no has pedido préstamos.</p>
          ) : (
            <table className="wallet-table">
              <thead>
                <tr>
                  <th>Monto</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {loans.map((loan) => (
                  <tr key={loan.id}>
                    <td>${Number(loan.amount).toFixed(2)}</td>
                    <td>{formatDate(loan.requested_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <section className="wallet-card">
          <h2>Historial de retiros</h2>
          {withdrawals.length === 0 ? (
            <p className="wallet-empty">Aún no has solicitado retiros.</p>
          ) : (
            <table className="wallet-table">
              <thead>
                <tr>
                  <th>Monto</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                </tr>
              </thead>
              <tbody>
                {withdrawals.map((wd) => (
                  <tr key={wd.id}>
                    <td>${Number(wd.amount).toFixed(2)}</td>
                    <td>{wd.status}</td>
                    <td>{formatDate(wd.requested_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>
      </main>
      <Footer />
    </div>
  )
}

export default WalletPage
