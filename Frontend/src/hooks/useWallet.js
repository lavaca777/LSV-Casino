import { useCallback, useEffect, useState } from 'react'

import { walletService } from '../services/api'
import { useAuth } from './useAuth'

export function useWallet() {
  const { user } = useAuth()
  const [balance, setBalance] = useState(0)
  const [totalWagered, setTotalWagered] = useState(0)
  const [loading, setLoading] = useState(true)

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

  useEffect(() => {
    refresh()
  }, [refresh])

  return { balance, totalWagered, loading, refresh }
}
