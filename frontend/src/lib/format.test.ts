import { describe, expect, it } from 'vitest'
import { aqiLevel, value, weatherLabel } from './format'

describe('environment formatting', () => {
  it('maps WMO weather codes to readable conditions', () => {
    expect(weatherLabel(0)).toBe('晴朗')
    expect(weatherLabel(63)).toBe('降雨')
    expect(weatherLabel(95)).toBe('雷暴')
  })

  it('preserves missing observations instead of fabricating zero', () => {
    expect(value(null, 'temperature')).toBe('—')
  })

  it('uses European AQI bands consistently', () => {
    expect(aqiLevel(18).label).toBe('优')
    expect(aqiLevel(55).label).toBe('一般')
    expect(aqiLevel(115).label).toBe('很差')
  })
})
