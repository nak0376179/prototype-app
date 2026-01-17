import { createFileRoute } from '@tanstack/react-router'
import Login from '@/components/login/Login'

export const Route = createFileRoute('/_auth/')({
  component: LoginPage
})

function LoginPage() {
  return <Login />
}
