function StatsCard({ label, value, accent }) {
  const className = accent ? `stats-card stats-card-${accent}` : 'stats-card'
  return (
    <div className={className}>
      <span className="stats-card-value">{value}</span>
      <span className="stats-card-label">{label}</span>
    </div>
  )
}

export default StatsCard
