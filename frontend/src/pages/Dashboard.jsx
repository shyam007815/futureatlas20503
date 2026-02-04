import { useState, useEffect } from 'react'
import WorldMap from '../components/WorldMap'
import Leaderboard from '../components/Leaderboard'
import { leaderboardAPI } from '../services/api'
import { liveUpdateService } from '../services/liveUpdates'

function Dashboard() {
  /* Optimized: Debounce slider inputs to prevent API flooding */
  const [year, setYear] = useState(2050)
  const [sliderValue, setSliderValue] = useState(2050)
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

  const handleSliderChange = (e) => {
    setSliderValue(parseInt(e.target.value))
  }

  const handleSliderCommit = () => {
    setYear(sliderValue)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">FutureAtlas 2050</h1>
        <p className="text-gray-600">Predicting and visualizing future global superpowers</p>
      </div>

      {/* Year Selector */}
      <div className="mb-6 bg-white p-4 rounded-lg shadow">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select Year: {sliderValue}
        </label>
        <input
          type="range"
          min="2020"
          max="2050"
          value={sliderValue}
          onChange={handleSliderChange}
          onMouseUp={handleSliderCommit}
          onTouchEnd={handleSliderCommit}
          className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
        />
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>2020</span>
          <span>2035</span>
          <span>2050</span>
        </div>
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
