import L from 'leaflet'
import { MapContainer, Marker, Popup, TileLayer } from 'react-leaflet'
import { useNavigate } from 'react-router-dom'
import type { CitySnapshot } from '../api/types'
import { value } from '../lib/format'

const icon = L.divIcon({ className: 'city-map-marker', html: '<span></span>', iconSize: [24,24], iconAnchor: [12,12] })

export function CityMap({ cities }: { cities: CitySnapshot[] }) {
  const navigate = useNavigate()
  return <MapContainer className="city-map" center={[31.5, 127]} zoom={4} scrollWheelZoom={false} attributionControl>
    <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    {cities.map(({ city, observation }) => <Marker key={city.id} position={[city.latitude, city.longitude]} icon={icon} eventHandlers={{ click: () => navigate(`/cities/${city.id}`) }}><Popup><strong>{city.name}</strong><br/>{value(observation.temperature, 'temperature')} · AQI {observation.air_quality_index?.toFixed(0) ?? '—'}</Popup></Marker>)}
  </MapContainer>
}
