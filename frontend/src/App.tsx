import { BrowserRouter, Route, Routes } from 'react-router'
import { RequireAuthLayout } from '@/layouts/RequireAuthLayout'

import Root from '@/pages/page'

import Users from '@/pages/users'

import Home from '@/pages/groups/[group_id]/home'
import Logs from '@/pages/groups/[group_id]/logs'
import Settings from '@/pages/groups/[group_id]/settings'

import Login from '@/pages/login'
import Logout from '@/pages/logout'
import ConfirmSession from '@/pages/confirm-session'

import Demo from '@/pages/demo'
import DemoConfirmSession from '@/pages/demo/confirm-session'

function NotFound() {
  return <p>Not Found</p>
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 認証不要ルート */}
        <Route index element={<Root />} />
        <Route path="/confirm-session" element={<ConfirmSession />} />
        <Route path="/login" element={<Login />} />
        <Route path="/logout" element={<Logout />} />
        <Route path="/demo/confirm-session" element={<DemoConfirmSession />} />
        <Route path="/demo" element={<Demo />} />
        {/* 認証が必要なルート */}
        <Route path="auth" element={<RequireAuthLayout />}>
          <Route path="users" element={<Users />} />
          <Route path="logs" element={<Logs />} />
          <Route path="settings" element={<Settings />} />
          <Route path="home" element={<Home />} />
        </Route>
        {/* 認証不要ルート */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </BrowserRouter>
  )
}
