import { useState } from 'react'
import { scenarioAPI } from '../services/api'

function ScenarioSimulator({ countryIso, countryName, onUpdate }) {
  const [militaryChange, setMilitaryChange] = useState(0)
  const [populationChange, setPopulationChange] = useState(0)
  const [year, setYear] = useState(2050)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const runScenario = async () => {
    setLoading(true)
    try {
      const response = await scenarioAPI.run({
        iso: countryIso,
        military_change_percent: militaryChange,
        population_change_percent: populationChange,
        year: year,
      })
      setResult(response.data)
      if (onUpdate) onUpdate(response.data)
    } catch (error) {
      console.error('Error running scenario:', error)
      alert('Error running scenario. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (!countryIso) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <p className="text-gray-500">Select a country to run scenarios</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-4">What-If Scenario Simulator</h2>
      <p className="text-gray-600 mb-4">Simulate changes to {countryName}'s military and population</p>

      <div className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Military Budget Change: {militaryChange > 0 ? '+' : ''}{militaryChange}%
          </label>
          <input
            type="range"
            min="-50"
            max="100"
            value={militaryChange}
            onChange={(e) => setMilitaryChange(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>-50%</span>
            <span>0%</span>
            <span>+100%</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Population Growth Change: {populationChange > 0 ? '+' : ''}{populationChange}%
          </label>
          <input
            type="range"
            min="-20"
            max="50"
            value={populationChange}
            onChange={(e) => setPopulationChange(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-gray-500 mt-1">
            <span>-20%</span>
            <span>0%</span>
            <span>+50%</span>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Target Year: {year}
          </label>
          <input
            type="range"
            min="2020"
            max="2050"
            value={year}
            onChange={(e) => setYear(parseInt(e.target.value))}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
          />
        </div>

        <button
          onClick={runScenario}
          disabled={loading}
          className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {loading ? 'Calculating...' : 'Run Scenario'}
        </button>

        {result && (
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold mb-3">Scenario Results</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-600">Original GSI:</p>
                <p className="font-bold text-lg">{result.original_gsi.toFixed(4)}</p>
              </div>
              <div>
                <p className="text-gray-600">New GSI:</p>
                <p className="font-bold text-lg">{result.new_gsi.toFixed(4)}</p>
              </div>
              <div className="col-span-2">
                <p className="text-gray-600">GSI Change:</p>
                <p className={`font-bold text-lg ${result.gsi_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {result.gsi_change >= 0 ? '+' : ''}{result.gsi_change.toFixed(4)}
                </p>
              </div>
            </div>
            <div className="mt-4 pt-4 border-t border-blue-200">
              <p className="text-xs text-gray-600">
                Military: ${result.details.original_military}B → ${result.details.new_military}B
              </p>
              <p className="text-xs text-gray-600">
                Population: {result.details.original_population.toFixed(1)}M → {result.details.new_population.toFixed(1)}M
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ScenarioSimulator
