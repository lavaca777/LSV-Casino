export function formatDateTime(value) {
  return new Intl.DateTimeFormat('es', {
    dateStyle: 'short',
    timeStyle: 'short',
  }).format(new Date(value))
}

export function resultLabel(result) {
  if (result === 'win') return 'Ganó'
  if (result === 'loss') return 'Perdió'
  if (result === 'draw') return 'Empate'
  return '—'
}
