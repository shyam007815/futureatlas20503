import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { countriesAPI, timeseriesAPI, insightsAPI } from '../services/api'
import ScenarioSimulator from '../components/ScenarioSimulator'

function CountryDetails() {
  const { iso } = useParams()
  const navigate = useNavigate()
  const [selectedCountry, setSelectedCountry] = useState('')
  const [countries, setCountries] = useState([])
  const [timeseriesData, setTimeseriesData] = useState([])
  const [insights, setInsights] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchCountries()
  }, [])

  useEffect(() => {
    if (iso) {
      setSelectedCountry(iso)
      fetchData(iso)
    }
  }, [iso])

  const fetchCountries = async () => {
    try {
      const response = await countriesAPI.getAll()
      setCountries(response.data)
      if (!iso && response.data.length > 0) {
        setSelectedCountry(response.data[0].iso3)
        fetchData(response.data[0].iso3)
      }
    } catch (error) {
      console.error('Error fetching countries:', error)
    }
  }

  const fetchData = async (countryIso) => {
    setLoading(true)
    try {
      const [timeseriesRes, insightsRes] = await Promise.all([
        timeseriesAPI.get(countryIso),
        insightsAPI.get(countryIso),
      ])
      setTimeseriesData(timeseriesRes.data.data || [])
      setInsights(insightsRes.data)
      if (countryIso !== iso) {
        navigate(`/country/${countryIso}`, { replace: true })
      }
    } catch (error) {
      console.error('Error fetching data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCountryChange = (e) => {
    const newIso = e.target.value
    setSelectedCountry(newIso)
    fetchData(newIso)
  }

  const formatNumber = (num) => {
    if (num >= 1000) return `${(num / 1000).toFixed(1)}T`
    return num.toFixed(1)
  }

  const exportToCSV = () => {
    const headers = ['Year', 'GDP', 'Population', 'Military', 'GSI Score']
    const rows = timeseriesData.map(d => [
      d.year,
      d.gdp,
      d.population,
      d.military,
      d.gsi,
    ])
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `country_data_${selectedCountry}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (loading && !timeseriesData.length) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="animate-pulse space-y-4">
          <div className="h-12 bg-gray-200 rounded w-1/3"></div>
          <div className="h-96 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">Country Details</h1>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Country
          </label>
          <select
            value={selectedCountry}
            onChange={handleCountryChange}
            className="w-full md:w-1/3 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            {countries.map((country) => (
              <option key={country.iso3} value={country.iso3}>
                {country.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Insights Summary */}
      {insights && (
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg shadow-lg p-6 mb-8">
          <h2 className="text-2xl font-bold mb-4">AI-Generated Insights</h2>
          <div className="grid md:grid-cols-2 gap-6 mb-4">
            <div>
              <h3 className="font-semibold mb-2">Current Status (2023)</h3>
              <ul className="space-y-1 text-sm">
                <li>GDP: ${formatNumber(insights.current.gdp)}B</li>
                <li>Population: {formatNumber(insights.current.population)}M</li>
                <li>Military: ${formatNumber(insights.current.military)}B</li>
                <li>GSI: {insights.current.gsi.toFixed(4)}</li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold mb-2">Projected (2050)</h3>
              <ul className="space-y-1 text-sm">
                <li>GDP: ${formatNumber(insights.future.gdp)}B</li>
                <li>Population: {formatNumber(insights.future.population)}M</li>
                <li>Military: ${formatNumber(insights.future.military)}B</li>
                <li>GSI: {insights.future.gsi.toFixed(4)}</li>
                {insights.future.rank && <li>Rank: #{insights.future.rank}</li>}
              </ul>
            </div>
          </div>
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Key Insights</h3>
            <p className="text-sm text-gray-700 leading-relaxed">{insights.summary}</p>
          </div>
        </div>
      )}

      {/* Charts */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">GDP Forecast</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeseriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => formatNumber(value)} />
              <Legend />
              <Line type="monotone" dataKey="gdp" stroke="#3b82f6" strokeWidth={2} name="GDP (B USD)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">Population Forecast</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeseriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => formatNumber(value)} />
              <Legend />
              <Line type="monotone" dataKey="population" stroke="#10b981" strokeWidth={2} name="Population (M)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">Military Expenditure</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeseriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => formatNumber(value)} />
              <Legend />
              <Line type="monotone" dataKey="military" stroke="#ef4444" strokeWidth={2} name="Military (B USD)" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4">Global Superpower Index (GSI)</h2>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={timeseriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="year" />
              <YAxis />
              <Tooltip formatter={(value) => value.toFixed(4)} />
              <Legend />
              <Line type="monotone" dataKey="gsi" stroke="#8b5cf6" strokeWidth={2} name="GSI Score" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Export Button & Scenario Simulator */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="text-lg font-semibold mb-4">Export Data</h3>
          <button
            onClick={exportToCSV}
            className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Export Data to CSV
          </button>
        </div>
      </div>

      {/* Scenario Simulator */}
      <ScenarioSimulator
        countryIso={selectedCountry}
        countryName={countries.find(c => c.iso3 === selectedCountry)?.name || ''}
      />
    </div>
  )
}

export default CountryDetails
