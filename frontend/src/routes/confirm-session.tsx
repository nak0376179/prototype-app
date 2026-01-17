import { createFileRoute } from '@tanstack/react-router'
import ComfirmSession from '@/components/login/ConfirmSession'

export const Route = createFileRoute('/confirm-session')({
  component: () => <ComfirmSession />
})
