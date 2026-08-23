import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'
import { useWallet } from '../hooks/useWallet'

const LOAN_THRESHOLD = 20

function Navbar() {
  const { user, logout } = useAuth()
  const { balance, refresh } = useWallet()
  const [menuOpen, setMenuOpen] = useState(false)
  const dropdownRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    refresh()
  }, [refresh])

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setMenuOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = async () => {
    setMenuOpen(false)
    await logout()
    navigate('/login')
  }

  return (
    <header className="navbar">
      <Link to="/home" className="navbar-logo">Casino Virtual</Link>

      <div className="navbar-right">
        <div className="navbar-balance">${Number(balance).toFixed(2)}</div>

        {balance < LOAN_THRESHOLD && (
          <button type="button" className="navbar-loan-btn" title="Pedir préstamo ($20)">
            Pedir préstamo
          </button>
        )}

        <div className="navbar-user" ref={dropdownRef}>
          <button
            type="button"
            className="navbar-user-btn"
            onClick={() => setMenuOpen((open) => !open)}
          >
            {user?.username} ▾
          </button>

          {menuOpen && (
            <div className="navbar-menu">
              <Link to="/profile" onClick={() => setMenuOpen(false)}>Perfil</Link>
              <Link to="/history" onClick={() => setMenuOpen(false)}>Historial</Link>
              <Link to="/stats" onClick={() => setMenuOpen(false)}>Estadísticas</Link>
              <Link to="/wallet" onClick={() => setMenuOpen(false)}>Billetera</Link>
              <button type="button" onClick={handleLogout}>Salir</button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

export default Navbar
