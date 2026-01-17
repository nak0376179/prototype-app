import { createFileRoute } from '@tanstack/react-router'
import Settings from '@/components/Settings'

export const Route = createFileRoute('/_auth/groups/$group_id/settings')({
  component: () => <Settings />
})
