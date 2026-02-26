import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import CountryDetails from './pages/CountryDetails'
import Compare from './pages/Compare'
import './App.css'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-slate-900 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <Link to="/" className="flex items-center px-2 py-2 text-xl font-bold text-white">
                  🌍 FutureAtlas 2050
                </Link>
                <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                  <Link
                    to="/"
                    className="border-transparent text-slate-300 hover:border-slate-500 hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
                  >
                    Dashboard
                  </Link>
                  <Link
                    to="/country"
                    className="border-transparent text-slate-300 hover:border-slate-500 hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
                  >
                    Country Details
                  </Link>
                  <Link
                    to="/compare"
                    className="border-transparent text-slate-300 hover:border-slate-500 hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors"
                  >
                    Compare
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/country" element={<CountryDetails />} />
          <Route path="/country/:iso" element={<CountryDetails />} />
          <Route path="/compare" element={<Compare />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App
