import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const countriesAPI = {
  getAll: () => api.get('/countries'),
  getOne: (iso) => api.get(`/countries/${iso}`),
}

export const timeseriesAPI = {
  get: (iso) => api.get(`/timeseries/${iso}`),
}

export const leaderboardAPI = {
  get: (year = 2050) => api.get(`/leaderboard?year=${year}`),
}

export const scenarioAPI = {
  run: (data) => api.post('/scenario', data),
}

export const insightsAPI = {
  get: (iso) => api.get(`/insights/${iso}`),
}

export default api
