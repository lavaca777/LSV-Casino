import GameGrid from '../components/GameGrid'
import Navbar from '../components/Navbar'
import './home.css'

function HomePage() {
  return (
    <div className="home-page">
      <Navbar />
      <main className="home-main">
        <h1>Bienvenido al Casino Virtual</h1>
        <p>Elige un juego para empezar</p>
        <GameGrid />
      </main>
    </div>
  )
}

export default HomePage
