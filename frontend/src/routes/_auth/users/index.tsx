import { createFileRoute } from '@tanstack/react-router'
import Users from '@/components/Users'

export const Route = createFileRoute('/_auth/users/')({
  component: () => <Users />
})
