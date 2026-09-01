import { useState } from 'react'

function LoanModal({ amount, onConfirm, onClose }) {
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)

  const handleConfirm = async () => {
    setSubmitting(true)
    setError(null)
    try {
      await onConfirm()
      onClose()
    } catch (err) {
      setError(err?.response?.data?.detail || 'No se pudo procesar el préstamo')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true">
        <h2 className="modal-title">Pedir préstamo</h2>
        <p className="modal-text">
          Vas a recibir <strong>${amount}</strong> en tu saldo. ¿Confirmas?
        </p>

        {error && <p className="modal-error" role="alert">{error}</p>}

        <div className="modal-actions">
          <button type="button" className="modal-btn modal-btn-secondary" onClick={onClose}>
            Cancelar
          </button>
          <button
            type="button"
            className="modal-btn modal-btn-primary"
            onClick={handleConfirm}
            disabled={submitting}
          >
            {submitting ? 'Procesando…' : 'Confirmar'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default LoanModal
