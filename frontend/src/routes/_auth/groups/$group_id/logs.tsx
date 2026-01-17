import { createFileRoute } from '@tanstack/react-router'
import Logs from '@/components/Logs'

export const Route = createFileRoute('/_auth/groups/$group_id/logs')({
  component: () => <Logs />
})
