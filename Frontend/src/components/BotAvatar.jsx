const FACES = {
  emoji: {
    idle: ':)',
    thinking: '...',
    win: ':D',
    lose: '>:(',
    tie: ':|',
  },
  kaomoji: {
    idle: '(・_・)',
    thinking: '(・_・?)',
    win: 'ヽ(^o^)ノ',
    lose: '(╥﹏╥)',
    tie: '(..;)',
  },
}

function BotAvatar({ name, style, mood }) {
  const face = FACES[style]?.[mood] ?? FACES[style]?.idle

  return (
    <div className="bot">
      <div className="bot-head">
        <div className="bot-antenna" />
        <div
          className={`bot-screen bot-screen-${style} ${
            mood === 'thinking' ? 'bot-screen-blink' : ''
          }`}
        >
          {face}
        </div>
      </div>
      <span className="bot-name">{name}</span>
    </div>
  )
}

export default BotAvatar