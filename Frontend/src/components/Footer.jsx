import './footer.css'

// Enlaces decorativos: aún no existen esas páginas, así que no navegan.
function DecorLink({ children }) {
  return (
    <a href="#" onClick={(e) => e.preventDefault()}>
      {children}
    </a>
  )
}

function Footer() {
  return (
    <footer className="site-footer">
      <div className="footer-top">
        <div className="footer-brand">
          <span className="footer-logo">🎰 Casino Virtual</span>
          <p className="footer-tagline">
            El casino donde el único riesgo real es aburrirte. Dinero 100% ficticio,
            emociones 100% imaginarias.
          </p>
        </div>

        <div className="footer-columns">
          <div className="footer-col">
            <h3>Juegos</h3>
            <ul>
              <li><DecorLink>Blackjack</DecorLink></li>
              <li><DecorLink>Cara o Cruz</DecorLink></li>
              <li><DecorLink>Ruleta (próximamente)</DecorLink></li>
              <li><DecorLink>Póker (algún día)</DecorLink></li>
              <li><DecorLink>Tragamonedas (soñar es gratis)</DecorLink></li>
            </ul>
          </div>

          <div className="footer-col">
            <h3>Ayuda</h3>
            <ul>
              <li><DecorLink>Términos y Condiciones</DecorLink></li>
              <li><DecorLink>Política de Privacidad</DecorLink></li>
              <li><DecorLink>Preguntas Frecuentes</DecorLink></li>
              <li><DecorLink>Contacto</DecorLink></li>
              <li><DecorLink>Mapa del sitio</DecorLink></li>
            </ul>
          </div>

          <div className="footer-col">
            <h3>Responsabilidad</h3>
            <ul>
              <li><DecorLink>Política de Juego Responsable</DecorLink></li>
              <li><DecorLink>Autoexclusión (de tu imaginación)</DecorLink></li>
              <li><DecorLink>Límites de depósito (no aplica)</DecorLink></li>
              <li><DecorLink>Línea de ayuda 24/7 (nadie contesta)</DecorLink></li>
            </ul>
          </div>

          <div className="footer-col">
            <h3>Métodos de pago</h3>
            <ul>
              <li><DecorLink>Dinero imaginario</DecorLink></li>
              <li><DecorLink>Favores personales</DecorLink></li>
              <li><DecorLink>Promesas vagas</DecorLink></li>
              <li><DecorLink>Cheques sin fondo (ficticios)</DecorLink></li>
              <li><DecorLink>Puntos de amistad</DecorLink></li>
            </ul>
          </div>
        </div>
      </div>

      <div className="footer-responsible">
        <h3>⚠ Juego responsable</h3>
        <p>
          Este casino es <strong>100% ficticio</strong>. Ningún peso real fue dañado
          en la elaboración de este sitio. Si sientes que estás perdiendo demasiado
          dinero imaginario, respira profundo, tómate un vaso de agua y sigue jugando:
          total, no es real. Los resultados pasados no garantizan resultados futuros,
          principalmente porque son inventados.
        </p>
      </div>

      <div className="footer-badges">
        <span className="footer-badge">🎲 Licencia N° 000-000 (autootorgada)</span>
        <span className="footer-badge">🔞 +18 (de edad mental)</span>
        <span className="footer-badge">🏆 Certificado por el Instituto de Mentiras Piadosas</span>
        <span className="footer-badge">🧾 Miembro honorario de la Asociación de Casinos que No Existen</span>
        <span className="footer-badge">🔒 Encriptado con 0 bits de seguridad</span>
      </div>

      <div className="footer-bottom">
        <p>© 2026 Casino Virtual — Todos los derechos <em>imaginarios</em> reservados.</p>
        <p>Hecho con 🎰, cero auditorías y muchas fichas de cartón.</p>
      </div>
    </footer>
  )
}

export default Footer
