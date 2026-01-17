import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Box, Button, Checkbox, FormControlLabel, TextField, Typography, CircularProgress } from '@mui/material'
import { signUp } from 'aws-amplify/auth'
import { useState } from 'react'
import { Amplify } from 'aws-amplify'

export const Route = createFileRoute('/_auth/demo/')({
  component: DemoSignupPage
})

function DemoSignupPage() {
  Amplify.configure({
    Auth: {
      Cognito: {
        userPoolId: import.meta.env.VITE_DEMO_USER_POOL_ID,
        userPoolClientId: import.meta.env.VITE_DEMO_USER_POOL_WEB_CLIENT_ID
      }
    }
  })

  // React Routerのhistoryを使って遷移
  const navigate = useNavigate()

  const [form, setForm] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    phone: '',
    company: '',
    position: '',
    purpose: '',
    agree: false
  })
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleCheckbox = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.checked })
  }

  const handleSubmit = async () => {
    // 必須項目のバリデーション
    if (!form.email || !form.password || !form.firstName || !form.lastName || !form.agree) {
      setErrorMessage('全ての必須項目を入力してください')
      return
    }
    setErrorMessage('') // エラーメッセージのリセット

    setIsLoading(true)

    try {
      // サインアップ処理
      await signUp({
        username: form.email,
        password: form.password,
        options: {
          userAttributes: {
            email: form.email,
            given_name: form.firstName,
            family_name: form.lastName,
            phone_number: form.phone,
            'custom:company': form.company,
            'custom:position': form.position,
            'custom:purpose': form.purpose
          }
        }
      })

      // サインアップ成功後、確認メール送信後にページ遷移
      alert('確認メールを送信しました')

      // 遷移先ページ（`confirm-session.tsx`）に遷移
      navigate({ to: '/demo/confirm-session' }) // '/demo/confirm-session' への遷移
    } catch (error: any) {
      console.error(error)
      setErrorMessage(error.message || '登録に失敗しました')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 4 }}>
      <Typography variant="h4" gutterBottom>
        デモ登録
      </Typography>

      {/* エラーメッセージ */}
      {errorMessage && (
        <Typography color="error" sx={{ marginBottom: 2 }}>
          {errorMessage}
        </Typography>
      )}

      {/* フォーム項目 */}
      <TextField label="メールアドレス" name="email" fullWidth margin="normal" onChange={handleChange} value={form.email} />
      <TextField label="パスワード" name="password" type="password" fullWidth margin="normal" onChange={handleChange} value={form.password} />
      <TextField label="姓" name="lastName" fullWidth margin="normal" onChange={handleChange} value={form.lastName} />
      <TextField label="名" name="firstName" fullWidth margin="normal" onChange={handleChange} value={form.firstName} />
      <TextField label="電話番号" name="phone" fullWidth margin="normal" onChange={handleChange} value={form.phone} />
      <TextField label="会社名" name="company" fullWidth margin="normal" onChange={handleChange} value={form.company} />
      <TextField label="役職名" name="position" fullWidth margin="normal" onChange={handleChange} value={form.position} />
      <TextField label="目的" name="purpose" fullWidth margin="normal" onChange={handleChange} value={form.purpose} />

      {/* チェックボックス（利用規約同意） */}
      <FormControlLabel control={<Checkbox name="agree" checked={form.agree} onChange={handleCheckbox} />} label="利用規約に同意する" />

      {/* 登録ボタン */}
      <Button variant="contained" onClick={handleSubmit} disabled={isLoading} fullWidth sx={{ mt: 2 }}>
        {isLoading ? <CircularProgress size={24} color="inherit" /> : '登録'}
      </Button>
    </Box>
  )
}
