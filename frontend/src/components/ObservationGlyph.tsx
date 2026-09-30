export function ObservationGlyph({ humidity, aqi, wind, precipitation }: { humidity: number | null; aqi: number | null; wind: number | null; precipitation: number | null }) {
  const humid = Math.min(90, Math.max(22, humidity ?? 45))
  const air = Math.min(100, Math.max(12, aqi ?? 20))
  const breeze = Math.min(34, Math.max(4, wind ?? 8))
  const rain = Math.min(30, Math.max(0, (precipitation ?? 0) * 6))
  return <svg className="observation-glyph" viewBox="0 0 240 240" role="img" aria-label="根据湿度、空气质量、风速和降水生成的观测图形">
    <circle cx="120" cy="120" r="92" className="glyph-track"/>
    <circle cx="120" cy="120" r={humid} className="glyph-humidity"/>
    <circle cx="120" cy="120" r={air * .55} className="glyph-air"/>
    <path d={`M${120-breeze} 120 H${120+breeze} M120 ${120-breeze} V${120+breeze}`} className="glyph-wind"/>
    {rain > 0 && <path d={`M92 178 Q120 ${178+rain} 148 178`} className="glyph-rain"/>}
    <circle cx="120" cy="120" r="4" className="glyph-core"/>
  </svg>
}
