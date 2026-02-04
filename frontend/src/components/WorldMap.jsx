import { MapContainer, TileLayer, GeoJSON, useMap, LayersControl } from 'react-leaflet'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import L from 'leaflet'

// Fix for default marker icons
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
})

function MapUpdater({ gsiData, year }) {
  const map = useMap()

  useEffect(() => {
    // You can update map view here if needed
  }, [gsiData, year])

  return null
}

function WorldMap({ year, onCountryClick, leaderboardData }) {
  const [geojson, setGeojson] = useState(null)
  const [gsiData, setGsiData] = useState({})
  const navigate = useNavigate()

  useEffect(() => {
    // Load simplified world GeoJSON
    axios.get('https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/world.geojson')
      .then(response => {
        if (response.data && response.data.type === 'FeatureCollection') {
          setGeojson(response.data)
        } else {
          setGeojson({
            type: 'FeatureCollection',
            features: []
          })
        }
      })
      .catch((error) => {
        console.warn('Failed to load GeoJSON, using empty map:', error)
        // Fallback: create a simple GeoJSON structure
        setGeojson({
          type: 'FeatureCollection',
          features: []
        })
      })
  }, [])

  useEffect(() => {
    // Fetch GSI data for all countries at the selected year
    if (leaderboardData && leaderboardData.length > 0) {
      const gsiMap = {}
      leaderboardData.forEach(country => {
        gsiMap[country.iso] = country.gsi
      })
      setGsiData(gsiMap)
    }
  }, [leaderboardData, year])

  const getColor = (gsi) => {
    if (!gsi) return '#e5e7eb'
    if (gsi >= 0.8) return '#1e40af'
    if (gsi >= 0.6) return '#3b82f6'
    if (gsi >= 0.4) return '#60a5fa'
    if (gsi >= 0.2) return '#93c5fd'
    return '#dbeafe'
  }

  const onEachFeature = (feature, layer) => {
    const iso = feature.properties.ISO_A3?.toLowerCase() || feature.properties.ISO3?.toLowerCase()
    const gsi = gsiData[iso] || 0
    const countryData = leaderboardData?.find(c => c.iso === iso)
    const rank = countryData?.rank || null

    layer.bindPopup(`
      <div class="p-2">
        <h3 class="font-bold">${feature.properties.NAME || feature.properties.ADMIN || 'Unknown'}</h3>
        <p>GSI Score: ${gsi.toFixed(4)}</p>
        ${rank ? `<p>Rank: #${rank}</p>` : ''}
      </div>
    `)

    layer.on({
      mouseover: (e) => {
        const layer = e.target
        layer.setStyle({
          weight: 2,
          color: '#3b82f6',
          opacity: 1,
          fillColor: '#3b82f6',
          fillOpacity: 0.1,
        })
      },
      mouseout: (e) => {
        const layer = e.target
        layer.setStyle({
          weight: 1,
          opacity: 0,
          fillOpacity: 0,
        })
      },
      click: () => {
        if (iso) {
          navigate(`/country/${iso}`)
          if (onCountryClick) onCountryClick(iso)
        }
      },
    })
  }

  const style = (feature) => {
    const iso = feature.properties.ISO_A3?.toLowerCase() || feature.properties.ISO3?.toLowerCase()
    const gsi = gsiData[iso] || 0
    return {
      fillColor: 'transparent',
      weight: 1,
      opacity: 0,
      color: 'white',
      dashArray: '3',
      fillOpacity: 0,
    }
  }

  return (
    <div className="w-full h-[600px] rounded-lg overflow-hidden shadow-lg border border-gray-200">
      <MapContainer
        center={[20, 0]}
        zoom={2}
        style={{ height: '100%', width: '100%' }}
        className="z-0"
      >
        <LayersControl position="topright">
          <LayersControl.BaseLayer checked name="Google Maps">
            <TileLayer
              attribution='&copy; Google'
              url="https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}"
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="Satellite Hybrid">
            <TileLayer
              attribution='&copy; Google'
              url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
            />
          </LayersControl.BaseLayer>
          <LayersControl.BaseLayer name="OpenStreetMap">
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
          </LayersControl.BaseLayer>
        </LayersControl>
        {geojson && (
          <GeoJSON
            data={geojson}
            style={style}
            onEachFeature={onEachFeature}
          />
        )}
        <MapUpdater gsiData={gsiData} year={year} />
      </MapContainer>
      {/* Legend removed as map is no longer color-coded */}
    </div>
  )
}

export default WorldMap
