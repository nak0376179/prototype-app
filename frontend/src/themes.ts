// src/theme.js
import { red } from '@mui/material/colors'
import { createTheme } from '@mui/material/styles'

// A custom theme for this app
const theme = createTheme({
  cssVariables: true,
  palette: {
    primary: { main: '#556cd6' },
    secondary: { main: '#19857b' },
    error: { main: red.A400 }
  },
  typography: { fontFamily: ['Roboto', 'Noto Sans JP', 'sans-serif'].join(',') }
})

export default theme
