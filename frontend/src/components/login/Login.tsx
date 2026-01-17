import { useState } from 'react'
import { useNavigate } from 'react-router'
import { useSetAtom } from 'jotai'
import { fetchAuthSession, signIn } from 'aws-amplify/auth'
import { idTokenAtom } from '@/stores/auth'
import { Box, Button, Container, TextField, Typography, Alert } from '@mui/material'
import { useForm } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import * as yup from 'yup'

const schema = yup.object({
  username: yup.string().required('ユーザー名を入力してください'),
  password: yup.string().required('パスワードを入力してください')
})

type FormData = yup.InferType<typeof schema>

function Login() {
  const {
    register,
    handleSubmit,
    formState: { errors }
  } = useForm<FormData>({
    resolver: yupResolver(schema)
  })

  const setIdToken = useSetAtom(idTokenAtom)
  const navigate = useNavigate()
  const [authError, setAuthError] = useState<string | null>(null)

  const onSubmit = async (data: FormData) => {
    try {
      setAuthError(null)
      await signIn({ username: data.username, password: data.password })
      const session = await fetchAuthSession().catch(() => null)
      const token = session?.tokens?.idToken?.toString() ?? null
      if (token) {
        setIdToken(token)
        navigate('/auth/users')
      }
    } catch (err) {
      console.error('ログイン失敗:', err)
      setAuthError('ログインに失敗しました。ユーザー名またはパスワードを確認してください。')
    }
  }

  return (
    <Container maxWidth="sm">
      <Box display="flex" flexDirection="column" gap={2} mt={8}>
        <Typography variant="h5" align="center">
          ログイン
        </Typography>

        {authError && <Alert severity="error">{authError}</Alert>}

        <TextField label="ユーザー名" variant="outlined" fullWidth {...register('username')} error={!!errors.username} helperText={errors.username?.message} />

        <TextField
          label="パスワード"
          variant="outlined"
          type="password"
          fullWidth
          {...register('password')}
          error={!!errors.password}
          helperText={errors.password?.message}
        />

        <Button variant="contained" color="primary" onClick={handleSubmit(onSubmit)}>
          ログイン
        </Button>
      </Box>
    </Container>
  )
}

export default Login
