import { fetchAuthSession } from 'aws-amplify/auth'
import { useEffect, useState } from 'react'
import { Navigate, Outlet } from 'react-router'
import Layout from '@/layouts/Layout'

export function RequireAuthLayout() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const session = await fetchAuthSession()
        const token = session?.tokens?.idToken?.toString()
        console.log('session:', session)

        if (token) {
          setAuthenticated(true)
        } else {
          setAuthenticated(false)
        }
      } catch (e) {
        console.error('Session fetch failed:', e)
        setAuthenticated(false)
      }
    }

    checkAuth()
  }, [])

  if (authenticated === null) return <p>Loading protected layout...</p>
  if (!authenticated) return <Navigate to="/login" replace />

  return (
    <Layout>
      <Outlet />
    </Layout>
  )
}
