import { Cloud, CloudFog, CloudLightning, CloudRain, CloudSnow, CloudSun, Sun } from 'lucide-react'

export function WeatherIcon({ code, size = 48 }: { code: number | null; size?: number }) {
  const props = { size, strokeWidth: 1.35, 'aria-hidden': true }
  if (code == null) return <CloudSun {...props}/>
  if (code === 0) return <Sun {...props}/>
  if (code <= 3) return <CloudSun {...props}/>
  if (code <= 48) return <CloudFog {...props}/>
  if (code <= 67 || (code >= 80 && code <= 82)) return <CloudRain {...props}/>
  if (code <= 77 || (code >= 85 && code <= 86)) return <CloudSnow {...props}/>
  if (code >= 95) return <CloudLightning {...props}/>
  return <Cloud {...props}/>
}
