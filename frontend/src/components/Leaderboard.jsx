import { useState, useEffect } from 'react'
import { leaderboardAPI } from '../services/api'
import { useNavigate } from 'react-router-dom'

function Leaderboard({ year, initialData, isLoading }) {
  const [data, setData] = useState([])
  const [internalLoading, setInternalLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    if (initialData) {
      setData(initialData)
      if (isLoading !== undefined) {
        setInternalLoading(isLoading)
      }
    } else {
      fetchLeaderboard()
    }
  }, [year, initialData, isLoading])

  const fetchLeaderboard = async () => {
    setInternalLoading(true)
    try {
      const response = await leaderboardAPI.get(year)
      setData(response.data)
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
    } finally {
      setInternalLoading(false)
    }
  }

  const formatNumber = (num, type = 'financial') => {
    if (type === 'population') {
      // Input is in Millions
      if (num >= 1000) return `${(num / 1000).toFixed(1)}B`
      return `${num.toFixed(1)}M`
    }
    // Financial: Input is in Billions
    if (num >= 1000) return `${(num / 1000).toFixed(1)}T`
    return `${num.toFixed(1)}`
  }

  if (internalLoading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-12 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">Top 20 Global Superpowers ({year})</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-slate-200">
          <thead className="bg-slate-100">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Rank</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Country</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">GDP (B USD)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Population (M)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Military (B USD)</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">GSI Score</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-slate-200">
            {data.map((country) => (
              <tr
                key={country.iso}
                className="hover:bg-slate-50 cursor-pointer transition-colors"
                onClick={() => navigate(`/country/${country.iso}`)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${country.rank <= 3 ? 'bg-yellow-100 text-yellow-800' : 'bg-slate-100 text-slate-800'
                    }`}>
                    #{country.rank}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-slate-900">
                  {country.name}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                  {formatNumber(country.gdp, 'financial')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                  {formatNumber(country.population, 'population')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                  {formatNumber(country.military, 'financial')}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className="text-sm font-medium text-slate-900">{country.gsi.toFixed(4)}</span>
                    <div className="ml-2 w-24 bg-slate-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${country.gsi * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Leaderboard
