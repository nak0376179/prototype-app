import { createFileRoute, redirect, Outlet } from '@tanstack/react-router'
import { fetchAuthSession } from 'aws-amplify/auth'
import Layout from '@/layouts/Layout' // レイアウトをインポート

export const Route = createFileRoute('/_auth')({
  beforeLoad: async ({ location }) => {
    let isAuthenticated = false

    try {
      const session = await fetchAuthSession()
      console.log('User is logged in:', session)
      isAuthenticated = true
    } catch (e) {
      console.warn('Auth check failed, redirecting to login...')
      throw redirect({
        to: '/login',
        search: { redirect: location.href }
      })
    }

    // ここに到達した = ログイン済み
    console.log('User location.pathname:', location.pathname)
    // try-catch の外なら redirect を投げても catch されない
    if (isAuthenticated && location.pathname === '/') {
      throw redirect({ to: '/users' })
    }
  },
  // component を修正
  component: () => (
    <Layout>
      <Outlet /> {/* ここに子ルート（/usersなど）が表示される */}
    </Layout>
  )
})
