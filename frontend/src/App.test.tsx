import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import { App } from './App'

describe('application routes', () => {
  it('renders the direct About route inside product navigation', async () => {
    render(<MemoryRouter initialEntries={['/about']}><App /></MemoryRouter>)
    expect(await screen.findByRole('heading', { name: /把城市环境数据/ })).toBeInTheDocument()
    expect(screen.getAllByRole('link', { name: /环境概览/ }).length).toBeGreaterThan(0)
  })

  it('recovers unknown routes through the overview redirect', async () => {
    render(<MemoryRouter initialEntries={['/missing']}><App /></MemoryRouter>)
    expect(await screen.findByRole('heading', { name: '城市环境概览' }, { timeout: 3000 })).toBeInTheDocument()
  })
})
