import { fetchAuthSession, signOut } from 'aws-amplify/auth'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { Button, Container, Typography, CircularProgress, Stack } from '@mui/material'
import { useSetAtom } from 'jotai'
import { idTokenAtom } from '@/stores/auth'

export default function ConfirmSession() {
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()
  const setIdToken = useSetAtom(idTokenAtom)

  useEffect(() => {
    const checkSession = async () => {
      const session = await fetchAuthSession().catch(() => null)
      const token = session?.tokens?.idToken?.toString() ?? null

      if (token) {
        setIdToken(token)
      }
      setLoading(false)
    }

    checkSession()
  }, [])

  const handleContinue = () => {
    navigate('/auth/home')
  }

  const handleReLogin = async () => {
    await signOut()
    setIdToken(null)
    navigate('/login')
  }

  if (loading) return <CircularProgress />

  return (
    <Container maxWidth="sm" sx={{ mt: 10 }}>
      <Typography variant="h5" gutterBottom>
        以前のログイン情報が見つかりました
      </Typography>
      <Typography variant="body1" gutterBottom>
        前回のログインセッションを使って続行しますか？
      </Typography>
      <Stack direction="row" spacing={2} mt={4}>
        <Button variant="contained" onClick={handleContinue}>
          続行する
        </Button>
        <Button variant="outlined" color="secondary" onClick={handleReLogin}>
          別のアカウントでログイン
        </Button>
      </Stack>
    </Container>
  )
}
