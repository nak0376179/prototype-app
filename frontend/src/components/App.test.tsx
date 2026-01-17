import '@testing-library/jest-dom'
import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import Home from './Home'

test('home', () => {
  render(<Home />)
  const linkElement = screen.getByText(/Home/i)
  expect(linkElement).toBeInTheDocument()
})
