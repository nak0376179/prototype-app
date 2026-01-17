import { createFileRoute } from '@tanstack/react-router'
import Logout from '@/components/login/Logout'

export const Route = createFileRoute('/logout')({
  component: () => <Logout />
})
