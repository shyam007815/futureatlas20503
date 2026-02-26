import { useState, useEffect } from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts'
import { countriesAPI, timeseriesAPI } from '../services/api'

function Compare() {
  const [countries, setCountries] = useState([])
  const [selectedCountries, setSelectedCountries] = useState([])
  const [comparisonData, setComparisonData] = useState({})
  const [loading, setLoading] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchCountries()
  }, [])

  useEffect(() => {
    if (selectedCountries.length > 0) {
      fetchComparisonData()
    }
  }, [selectedCountries])

  const fetchCountries = async () => {
    try {
      const response = await countriesAPI.getAll()
      setCountries(response.data)
    } catch (error) {
      console.error('Error fetching countries:', error)
    }
  }

  const fetchComparisonData = async () => {
    setLoading(true)
    try {
      const dataPromises = selectedCountries.map(iso => timeseriesAPI.get(iso))
      const responses = await Promise.all(dataPromises)

      const combinedData = {}
      selectedCountries.forEach((iso, index) => {
        combinedData[iso] = responses[index].data.data || []
      })
      setComparisonData(combinedData)
    } catch (error) {
      console.error('Error fetching comparison data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCountryToggle = (iso) => {
    setSelectedCountries(prev => {
      if (prev.includes(iso)) {
        return prev.filter(c => c !== iso)
      } else {
        return [...prev, iso]
      }
    })
  }

  const getCountryName = (iso) => {
    const country = countries.find(c => c.iso3 === iso)
    return country ? country.name : iso
  }

  const formatNumber = (num, type = 'financial') => {
    if (type === 'population') {
      if (num >= 1000) return `${(num / 1000).toFixed(1)}B`
      return `${num.toFixed(1)}M`
    }
    if (num >= 1000) return `${(num / 1000).toFixed(1)}T`
    return num.toFixed(1)
  }

  // Get data for bar charts (showing selected years: 2020, 2030, 2040, 2050)
  const getBarChartData = (metric) => {
    if (selectedCountries.length === 0) return []

    const targetYears = [2020, 2030, 2040, 2050]
    const chartData = []

    targetYears.forEach(year => {
      const yearData = { year: year.toString() }
      selectedCountries.forEach(iso => {
        const yearDataPoint = comparisonData[iso]?.find(d => d.year === year)
        const countryName = getCountryName(iso)
        if (yearDataPoint) {
          if (metric === 'gdp') {
            yearData[countryName] = yearDataPoint.gdp
          } else if (metric === 'population') {
            yearData[countryName] = yearDataPoint.population
          } else if (metric === 'military') {
            yearData[countryName] = yearDataPoint.military
          } else if (metric === 'gsi') {
            yearData[countryName] = yearDataPoint.gsi
          }
        } else {
          yearData[countryName] = 0
        }
      })
      chartData.push(yearData)
    })

    return chartData
  }

  const get2050Comparison = () => {
    const comparison = []
    selectedCountries.forEach(iso => {
      const year2050 = comparisonData[iso]?.find(d => d.year === 2050)
      if (year2050) {
        const country = countries.find(c => c.iso3 === iso)
        comparison.push({
          iso,
          name: country?.name || iso,
          gdp: year2050.gdp,
          population: year2050.population,
          military: year2050.military,
          gsi: year2050.gsi,
        })
      }
    })
    return comparison.sort((a, b) => b.gsi - a.gsi)
  }

  const filteredCountries = countries.filter(c =>
    c.name.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const comparison2050 = get2050Comparison()

  const colors = ['#3b82f6', '#10b981', '#ef4444', '#8b5cf6', '#f59e0b', '#ec4899', '#06b6d4', '#a855f7']

  const CustomTooltip = ({ active, payload, label, formatter }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white p-4 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-semibold mb-2">{`Year: ${label}`}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }} className="text-sm">
              {`${entry.name}: ${formatter ? formatter(entry.value) : (entry.value?.toFixed(2) || 'N/A')}`}
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-2">Compare Countries</h1>
        <p className="text-slate-600">Select multiple countries to compare their trajectories</p>
      </div>

      {/* Country Selection */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8 border border-slate-200">
        <h2 className="text-xl font-bold mb-4 text-slate-800">Select Countries (All {countries.length} Available)</h2>

        <div className="mb-4">
          <input
            type="text"
            placeholder="Search countries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-2 max-h-96 overflow-y-auto">
          {filteredCountries.map((country) => {
            const isSelected = selectedCountries.includes(country.iso3)
            return (
              <button
                key={country.iso3}
                onClick={() => handleCountryToggle(country.iso3)}
                className={`px-3 py-2 text-sm rounded-lg border transition-colors ${isSelected
                  ? 'bg-blue-600 text-white border-blue-600'
                  : 'bg-white text-slate-700 border-slate-300 hover:border-blue-500'
                  }`}
              >
                {country.name}
              </button>
            )
          })}
        </div>

        {selectedCountries.length > 0 && (
          <div className="mt-4">
            <p className="text-sm font-medium mb-2 text-slate-700">Selected ({selectedCountries.length}):</p>
            <div className="flex flex-wrap gap-2">
              {selectedCountries.map(iso => (
                <span
                  key={iso}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
                >
                  {getCountryName(iso)}
                  <button
                    onClick={() => handleCountryToggle(iso)}
                    className="ml-2 text-blue-600 hover:text-blue-800"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      {loading && (
        <div className="text-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      )}

      {selectedCountries.length > 0 && !loading && (
        <>
          {/* Comparison Charts - Professional Bar Charts */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-lg p-6 border border-slate-100">
              <h2 className="text-xl font-bold mb-4 text-slate-800">GDP Comparison (B USD)</h2>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart
                  data={getBarChartData('gdp')}
                  margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    dataKey="year"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => formatNumber(value)}
                  />
                  <Tooltip content={<CustomTooltip formatter={(v) => formatNumber(v)} />} />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="square"
                  />
                  {selectedCountries.map((iso, index) => (
                    <Bar
                      key={iso}
                      dataKey={getCountryName(iso)}
                      name={getCountryName(iso)}
                      fill={colors[index % colors.length]}
                      radius={[4, 4, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 border border-slate-100">
              <h2 className="text-xl font-bold mb-4 text-slate-800">Population Comparison (M)</h2>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart
                  data={getBarChartData('population')}
                  margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    dataKey="year"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => formatNumber(value)}
                  />
                  <Tooltip content={<CustomTooltip formatter={(v) => formatNumber(v)} />} />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="square"
                  />
                  {selectedCountries.map((iso, index) => (
                    <Bar
                      key={iso}
                      dataKey={getCountryName(iso)}
                      name={getCountryName(iso)}
                      fill={colors[index % colors.length]}
                      radius={[4, 4, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 border border-slate-100">
              <h2 className="text-xl font-bold mb-4 text-slate-800">Military Expenditure (B USD)</h2>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart
                  data={getBarChartData('military')}
                  margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    dataKey="year"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => formatNumber(value)}
                  />
                  <Tooltip content={<CustomTooltip formatter={(v) => formatNumber(v)} />} />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="square"
                  />
                  {selectedCountries.map((iso, index) => (
                    <Bar
                      key={iso}
                      dataKey={getCountryName(iso)}
                      name={getCountryName(iso)}
                      fill={colors[index % colors.length]}
                      radius={[4, 4, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-6 border border-slate-100">
              <h2 className="text-xl font-bold mb-4 text-slate-800">Global Superpower Index (GSI)</h2>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart
                  data={getBarChartData('gsi')}
                  margin={{ top: 20, right: 30, left: 20, bottom: 60 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    dataKey="year"
                    angle={-45}
                    textAnchor="end"
                    height={80}
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis
                    stroke="#64748b"
                    tick={{ fontSize: 12 }}
                    domain={[0, 1]}
                    tickFormatter={(value) => value.toFixed(2)}
                  />
                  <Tooltip
                    content={<CustomTooltip formatter={(v) => v ? v.toFixed(4) : 'N/A'} />}
                  />
                  <Legend
                    wrapperStyle={{ paddingTop: '20px' }}
                    iconType="square"
                  />
                  {selectedCountries.map((iso, index) => (
                    <Bar
                      key={iso}
                      dataKey={getCountryName(iso)}
                      name={getCountryName(iso)}
                      fill={colors[index % colors.length]}
                      radius={[4, 4, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Comparison Table (2050) */}
          <div className="bg-white rounded-lg shadow-lg p-6 border border-slate-200">
            <h2 className="text-2xl font-bold mb-4 text-slate-900">2050 Projection Comparison</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-100">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Country</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">GDP (B USD)</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Population (M)</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Military (B USD)</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">GSI Score</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                  {comparison2050.map((country) => (
                    <tr key={country.iso}>
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
        </>
      )}

      {selectedCountries.length === 0 && !loading && (
        <div className="bg-slate-50 rounded-lg p-8 text-center border border-slate-200">
          <p className="text-slate-500">Select countries from above to start comparing</p>
        </div>
      )}
    </div>
  )
}

export default Compare
