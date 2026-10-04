import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import StatsCard from '../components/StatsCard'
import { useStats } from '../hooks/useStats'
import './home.css'
import './stats.css'

function money(value) {
  return `$${Number(value).toFixed(2)}`
}

function StatsPage() {
  const { stats, loading, error } = useStats()

  return (
    <div className="home-page">
      <Navbar />

      <main className="stats-main">
        <h1>Estadísticas</h1>

        {loading && <p className="stats-status">Cargando…</p>}
        {error && (
          <p className="stats-error" role="alert">
            {error}
          </p>
        )}

        {stats && (
          <>
            <section className="stats-section">
              <h2>Partidas</h2>
              <div className="stats-grid">
                <StatsCard label="Jugadas" value={stats.total_games} />
                <StatsCard
                  label="Tasa de victoria"
                  value={`${stats.win_rate}%`}
                  accent="accent"
                />
                <StatsCard
                  label="Racha actual"
                  value={stats.current_streak}
                  accent="win"
                />
                <StatsCard
                  label="Racha más larga"
                  value={stats.longest_streak}
                />
              </div>
            </section>

            <section className="stats-section">
              <h2>Dinero</h2>
              <div className="stats-grid">
                <StatsCard
                  label="Mayor ganancia"
                  value={money(stats.biggest_win)}
                  accent="win"
                />
                <StatsCard
                  label="Total apostado"
                  value={money(stats.total_wagered)}
                />
                <StatsCard
                  label="Profit / Loss"
                  value={`${stats.net_profit >= 0 ? '+' : ''}${money(stats.net_profit)}`}
                  accent={stats.net_profit >= 0 ? 'win' : 'loss'}
                />
                <StatsCard
                  label="W / L / E"
                  value={`${stats.total_games_won} / ${stats.total_games_lost} / ${stats.total_games_drawn}`}
                />
              </div>
            </section>
          </>
        )}
      </main>

      <Footer />
    </div>
  )
}

export default StatsPage
