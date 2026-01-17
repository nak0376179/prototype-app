import { useEffect } from 'react'
import { useSetAtom } from 'jotai'
import { useNavigate } from '@tanstack/react-router'
import { signOut } from 'aws-amplify/auth'
import { idTokenAtom } from '@/stores/auth'

export default function Logout() {
  const navigate = useNavigate()
  const setIdToken = useSetAtom(idTokenAtom)

  useEffect(() => {
    const doLogout = async () => {
      try {
        await signOut()
      } catch (e) {
        console.warn('サインアウト処理でエラー:', e)
      } finally {
        setIdToken(null) // ローカル状態クリア
        navigate({ to: '/', replace: true }) // ログイン画面へ遷移
      }
    }

    doLogout()
  }, [])

  return <p>ログアウト中です...</p>
}
