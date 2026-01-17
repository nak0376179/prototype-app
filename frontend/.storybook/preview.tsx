import type { Preview } from '@storybook/react-vite'
import { createRootRoute, createRouter, RouterProvider } from '@tanstack/react-router'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'

// TanStack Router の最小限のモック
const rootRoute = createRootRoute()
const router = createRouter({ routeTree: rootRoute })

// Create a default theme
const theme = createTheme()

const preview: Preview = {
  decorators: [
    (Story) => (
      <ThemeProvider theme={theme}>
        <CssBaseline />
        {/* children ではなく、defaultComponent プロパティを使用する */}
        <RouterProvider router={router} defaultComponent={() => <Story />} />
      </ThemeProvider>
    )
  ],
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i
      }
    },

    a11y: {
      // 'todo' - show a11y violations in the test UI only
      // 'error' - fail CI on a11y violations
      // 'off' - skip a11y checks entirely
      test: 'todo'
    }
  }
}

export default preview
