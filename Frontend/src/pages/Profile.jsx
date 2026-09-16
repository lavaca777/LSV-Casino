import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import { useAuth } from '../hooks/useAuth'
import { getErrorMessage, userService } from '../services/api'
import './home.css'
import './profile.css'

function formatDate(value) {
  if (!value) return '—'
  return new Intl.DateTimeFormat('es', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

function ProfilePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    setError(null)
    setMessage(null)

    if (newPassword !== confirmPassword) {
      setError('Las contraseñas nuevas no coinciden')
      return
    }

    setSubmitting(true)
    try {
      await userService.changePassword(user.id, currentPassword, newPassword)
      setCurrentPassword('')
      setNewPassword('')
      setConfirmPassword('')
      setMessage('Contraseña actualizada correctamente')
    } catch (err) {
      setError(getErrorMessage(err, 'No se pudo cambiar la contraseña'))
    } finally {
      setSubmitting(false)
    }
  }

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <div className="home-page">
      <Navbar />

      <main className="profile-main">
        <h1>Mi Perfil</h1>

        <section className="profile-card">
          <h2>Datos de cuenta</h2>
          <div className="profile-field">
            <span className="profile-label">Usuario</span>
            <span>{user?.username}</span>
          </div>
          <div className="profile-field">
            <span className="profile-label">Email</span>
            <span>{user?.email}</span>
          </div>
          <div className="profile-field">
            <span className="profile-label">Cuenta creada</span>
            <span>{formatDate(user?.created_at)}</span>
          </div>
        </section>

        <section className="profile-card">
          <h2>Cambiar contraseña</h2>
          <form onSubmit={handlePasswordChange} noValidate>
            <label htmlFor="currentPassword">Contraseña actual</label>
            <input
              id="currentPassword"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              required
            />

            <label htmlFor="newPassword">Nueva contraseña (mínimo 8 caracteres)</label>
            <input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              minLength={8}
              required
            />

            <label htmlFor="confirmPassword">Confirmar nueva contraseña</label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              minLength={8}
              required
            />

            {error && <p className="profile-error" role="alert">{error}</p>}
            {message && <p className="profile-success" role="status">{message}</p>}

            <button type="submit" disabled={submitting}>
              {submitting ? 'Guardando…' : 'Cambiar contraseña'}
            </button>
          </form>
        </section>

        <button type="button" className="profile-logout" onClick={handleLogout}>
          Cerrar sesión
        </button>
      </main>
      <Footer />
    </div>
  )
}

export default ProfilePage
