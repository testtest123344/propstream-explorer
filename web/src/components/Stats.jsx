import { useState, useEffect } from 'react'

function Stats() {
  const [stats, setStats] = useState(null)

  useEffect(() => {
    fetchStats()
    const interval = setInterval(fetchStats, 10000) // Refresh every 10s
    return () => clearInterval(interval)
  }, [])

  const fetchStats = async () => {
    try {
      const response = await fetch('/api/stats')
      const data = await response.json()
      setStats(data)
    } catch (err) {
      // Silently fail
    }
  }

  if (!stats) return null

  const dailyPercent = (stats.daily_requests / stats.daily_limit) * 100

  return (
    <div className="flex items-center gap-4 text-sm">
      <div className="flex items-center gap-2">
        <span className="text-gray-400">Today:</span>
        <span className={dailyPercent > 80 ? 'text-red-400' : 'text-green-400'}>
          {stats.daily_requests}/{stats.daily_limit}
        </span>
      </div>
      <div className="w-20 h-2 bg-gray-700 rounded-full overflow-hidden">
        <div 
          className={`h-full ${dailyPercent > 80 ? 'bg-red-500' : 'bg-green-500'}`}
          style={{ width: `${Math.min(dailyPercent, 100)}%` }}
        />
      </div>
    </div>
  )
}

export default Stats
