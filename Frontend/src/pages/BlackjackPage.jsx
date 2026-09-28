import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import BlackjackBoard from '../components/BlackjackBoard'
import './home.css'
import './blackjack.css'

function BlackjackPage() {
  return (
    <div className="home-page">
      <Navbar />
      <main className="bj-main">
        <h1>Blackjack</h1>
        <BlackjackBoard />
      </main>
      <Footer />
    </div>
  )
}

export default BlackjackPage
