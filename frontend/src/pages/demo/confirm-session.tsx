import { Box, Button, TextField, Typography } from '@mui/material'
import { useState } from 'react'
import { confirmSignUp } from 'aws-amplify/auth'
import { useNavigate } from 'react-router'

export default function ConfirmSessionPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [code, setCode] = useState('')
  const [errorMessage, setErrorMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value)
  }

  const handleCodeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCode(e.target.value)
  }

  const handleSubmit = async () => {
    if (!email || !code) {
      setErrorMessage('メールアドレスと確認コードを入力してください')
      return
    }
    setErrorMessage('')

    setIsLoading(true)

    try {
      await confirmSignUp({ username: email, confirmationCode: code })
      alert('確認コードが正しく入力されました')
      navigate('/demo/login') // ログインページなどに遷移
    } catch (error) {
      console.error(error)
      setErrorMessage('確認コードが間違っています')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Box sx={{ maxWidth: 600, mx: 'auto', p: 4 }}>
      <Typography variant="h4" gutterBottom>
        メールアドレス確認
      </Typography>

      {/* エラーメッセージ */}
      {errorMessage && (
        <Typography color="error" sx={{ marginBottom: 2 }}>
          {errorMessage}
        </Typography>
      )}

      {/* 確認コード入力フォーム */}
      <TextField label="メールアドレス" name="email" fullWidth margin="normal" onChange={handleEmailChange} value={email} />
      <TextField label="確認コード" name="code" fullWidth margin="normal" onChange={handleCodeChange} value={code} />

      {/* 確認ボタン */}
      <Button variant="contained" onClick={handleSubmit} disabled={isLoading} fullWidth sx={{ mt: 2 }}>
        {isLoading ? '確認中...' : '確認'}
      </Button>
    </Box>
  )
}
