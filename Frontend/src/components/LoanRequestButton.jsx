import { useState } from 'react'

import { useWallet } from '../hooks/useWallet'
import LoanModal from './LoanModal'

const LOAN_AMOUNT = 20

function LoanRequestButton() {
  const { requestLoan } = useWallet()
  const [open, setOpen] = useState(false)

  return (
    <>
      <button
        type="button"
        className="navbar-loan-btn"
        onClick={() => setOpen(true)}
      >
        Pedir préstamo
      </button>

      {open && (
        <LoanModal
          amount={LOAN_AMOUNT}
          onConfirm={requestLoan}
          onClose={() => setOpen(false)}
        />
      )}
    </>
  )
}

export default LoanRequestButton
