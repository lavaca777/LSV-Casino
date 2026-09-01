import { useCallback, useEffect, useState } from 'react'

import { useAuth } from '../hooks/useAuth'
import { walletService } from '../services/api'
import { WalletContext } from './walletContextValue'

export function WalletProvider({ children }) {
  const { user } = useAuth()
  const [balance, setBalance] = useState(0)
  const [totalWagered, setTotalWagered] = useState(0)
  const [loading, setLoading] = useState(false)

  const refresh = useCallback(async () => {
    if (!user) return
    try {
      const wallet = await walletService.getWallet(user.id)
      setBalance(wallet.balance)
      setTotalWagered(wallet.total_wagered)
    } finally {
      setLoading(false)
    }
  }, [user])

  const requestLoan = useCallback(async () => {
    if (!user) return
    const data = await walletService.requestLoan(user.id)
    setBalance(data.new_balance)
    return data
  }, [user])

  useEffect(() => {
    refresh()
  }, [refresh])

  const value = { balance, totalWagered, loading, refresh, requestLoan }

  return <WalletContext.Provider value={value}>{children}</WalletContext.Provider>
}
