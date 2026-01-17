import type { Preview } from '@storybook/react'

import { CssBaseline, ThemeProvider } from '@mui/material'
import { withThemeFromJSXProvider } from '@storybook/addon-themes'

/* TODO: update import for your custom Material UI themes */
import lightTheme from '../src/themes'

/* Robotoフォント（英語） */
import '@fontsource/roboto/300.css'
import '@fontsource/roboto/400.css'
import '@fontsource/roboto/500.css'
import '@fontsource/roboto/700.css'

/* Noto Sans JP（日本語） */
import '@fontsource/noto-sans-jp/300.css'
import '@fontsource/noto-sans-jp/400.css'
import '@fontsource/noto-sans-jp/500.css'
import '@fontsource/noto-sans-jp/700.css'

import '@fontsource/material-icons'

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i
      }
    }
  },

  decorators: [
    withThemeFromJSXProvider({
      GlobalStyles: CssBaseline,
      Provider: ThemeProvider,
      themes: {
        // Provide your custom themes here
        light: lightTheme,
        dark: lightTheme
      },
      defaultTheme: 'light'
    })
  ]
}

export default preview
