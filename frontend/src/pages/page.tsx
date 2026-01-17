import { useEffect } from 'react'
import { useNavigate } from 'react-router'
import { fetchAuthSession } from 'aws-amplify/auth'

export default function RootRedirector() {
  const navigate = useNavigate()

  useEffect(() => {
    const check = async () => {
      const session = await fetchAuthSession().catch(() => null)
      if (session?.tokens?.idToken) {
        navigate('/confirm-session')
      } else {
        navigate('/login')
      }
    }

    check()
  }, [])

  return null
}
