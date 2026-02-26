import { useState, useEffect } from 'react'
import WorldMap from '../components/WorldMap'
import Leaderboard from '../components/Leaderboard'
import { leaderboardAPI } from '../services/api'
import { liveUpdateService } from '../services/liveUpdates'
import LiveDateTime from '../components/LiveDateTime'

function Dashboard() {
  /* Optimized: Debounce removed - direct selection */
  const [year, setYear] = useState(2050)
  const [leaderboardData, setLeaderboardData] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Initial fetch
    fetchLeaderboard()

    // Connect to live updates
    liveUpdateService.connect()
    liveUpdateService.setYear(year)

    // Subscribe to updates
    const unsubscribe = liveUpdateService.subscribe((data) => {
      setLeaderboardData(data)
      setLoading(false) // Ensure loading is off when data arrives
    })

    return () => {
      unsubscribe()
    }
  }, [year])

  const fetchLeaderboard = async () => {
    // Don't set loading logic here if we rely on live updates, or keep it for fallback
    // But usually HTTP is faster than WS connection establishment on first load
    setLoading(true)
    try {
      const response = await leaderboardAPI.get(year)
      // Only set if we haven't received a WS update yet (simple enough to just set, WS will overwrite)
      setLeaderboardData(response.data)
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCountryClick = (iso) => {
    console.log('Country clicked:', iso)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 mb-2">FutureAtlas 2050</h1>
          <p className="text-slate-600">Predicting and visualizing future global superpowers</p>
        </div>
        <LiveDateTime />
      </div>

      {/* Year Selector */}
      <div className="mb-6 bg-white p-4 rounded-lg shadow flex items-center border border-slate-200">
        <label className="text-slate-700 font-medium mr-4">
          Forecast Year:
        </label>
        <select
          value={year}
          onChange={(e) => setYear(parseInt(e.target.value))}
          className="block w-32 border-slate-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 py-2 px-3 border"
        >
          {Array.from({ length: 31 }, (_, i) => 2020 + i).map((y) => (
            <option key={y} value={y}>
              {y}
            </option>
          ))}
        </select>
      </div>

      {/* World Map */}
      <div className="mb-8 relative">
        <WorldMap
          year={year}
          onCountryClick={handleCountryClick}
          leaderboardData={leaderboardData}
        />
      </div>

      {/* Leaderboard */}
      <Leaderboard year={year} initialData={leaderboardData} isLoading={loading} />
    </div>
  )
}

export default Dashboard
