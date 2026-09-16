import Footer from '../components/Footer'
import Navbar from '../components/Navbar'
import './home.css'

function ComingSoon({ title }) {
  return (
    <div className="home-page">
      <Navbar />
      <main className="home-main">
        <h1>{title}</h1>
        <p>Esta sección estará disponible próximamente.</p>
      </main>
      <Footer />
    </div>
  )
}

export default ComingSoon
