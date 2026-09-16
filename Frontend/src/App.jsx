import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'

import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { WalletProvider } from './context/WalletContext'
import ComingSoon from './pages/ComingSoon'
import CoinflipPage from './pages/Coinflip'
import HomePage from './pages/Home'
import LoginPage from './pages/Login'
import ProfilePage from './pages/Profile'
import RegisterPage from './pages/Register'
import WalletPage from './pages/Wallet'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <WalletProvider>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <HomePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfilePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/history"
              element={
                <ProtectedRoute>
                  <ComingSoon title="Historial" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/stats"
              element={
                <ProtectedRoute>
                  <ComingSoon title="Estadísticas" />
                </ProtectedRoute>
              }
            />
            <Route
              path="/wallet"
              element={
                <ProtectedRoute>
                  <WalletPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/coinflip"
              element={
                <ProtectedRoute>
                  <CoinflipPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/blackjack"
              element={
                <ProtectedRoute>
                  <ComingSoon title="Blackjack" />
                </ProtectedRoute>
              }
            />

            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="*" element={<Navigate to="/home" replace />} />
          </Routes>
        </WalletProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
