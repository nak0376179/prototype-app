import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  TextField,
  Typography
} from '@mui/material'
import { useState } from 'react'
import { useFetchUsersQuery, useCreateUserMutation, useUpdateUserMutation, useDeleteUserMutation } from '@/hooks/api/users' // あなたのhooks定義ファイル

type APIError = string | { msg: string }[] | null

export default function UsersPage() {
  const [error, setError] = useState<APIError>(null)

  const { data: users, isLoading } = useFetchUsersQuery()
  const createUser = useCreateUserMutation()
  const updateUser = useUpdateUserMutation()
  const deleteUser = useDeleteUserMutation()

  const [newUser, setNewUser] = useState({ userid: '', username: '', email: '' })
  const [editingUser, setEditingUser] = useState<{ userid: string; username: string; email: string } | null>(null)

  const handleCreate = async () => {
    setError(null)
    try {
      await createUser.mutateAsync(newUser) // async/awaitに変更
      setNewUser({ userid: '', username: '', email: '' })
    } catch (e: any) {
      const message = e?.response?.data?.detail || 'Failed to create user'
      setError(message)
    }
  }

  const handleUpdate = async () => {
    setError(null)
    if (editingUser) {
      try {
        await updateUser.mutateAsync({
          userid: editingUser.userid,
          data: { username: editingUser.username, email: editingUser.email }
        })
        setEditingUser(null)
      } catch (e: any) {
        const message = e?.response?.data?.detail || 'Failed to update user'
        setError(message)
      }
    }
  }

  const handleDelete = async (userid: string) => {
    setError(null)
    try {
      await deleteUser.mutateAsync(userid)
    } catch (e: any) {
      const message = e?.response?.data?.detail || 'Failed to delete user'
      setError(message)
    }
  }

  if (isLoading) return <Typography>Loading...</Typography>

  return (
    <Box p={4}>
      <Typography variant="h4" mb={2}>
        Users API Demo
      </Typography>

      {/* エラー表示 */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {typeof error === 'string' ? error : Array.isArray(error) ? error.map((err, i) => <div key={i}>{err.msg}</div>) : 'Unknown error'}
        </Alert>
      )}

      {/* 新規作成フォーム */}
      <Stack spacing={2} direction="row" mb={3}>
        <TextField label="ID" value={newUser.userid} onChange={(e) => setNewUser({ ...newUser, userid: e.target.value })} />
        <TextField label="Name" value={newUser.username} onChange={(e) => setNewUser({ ...newUser, username: e.target.value })} />
        <TextField label="Email" value={newUser.email} onChange={(e) => setNewUser({ ...newUser, email: e.target.value })} />
        <Button variant="contained" onClick={handleCreate}>
          Add User
        </Button>
      </Stack>

      {/* ユーザー一覧表示 */}
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Email</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {users?.map((user: any) => (
            <TableRow key={user.userid}>
              <TableCell>{user.userid}</TableCell>
              <TableCell>{user.username}</TableCell>
              <TableCell>{user.email}</TableCell>
              <TableCell>
                <Stack direction="row" spacing={1}>
                  <Button variant="outlined" onClick={() => setEditingUser(user)}>
                    Edit
                  </Button>
                  <Button variant="outlined" color="error" onClick={() => handleDelete(user.userid)}>
                    Delete
                  </Button>
                </Stack>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      {/* 編集ダイアログ */}
      <Dialog open={!!editingUser} onClose={() => setEditingUser(null)} container={document.body}>
        <DialogTitle>Edit User</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Name"
              value={editingUser?.username || ''}
              onChange={(e) => setEditingUser((prev) => (prev ? { ...prev, username: e.target.value } : prev))}
            />
            <TextField
              label="Email"
              value={editingUser?.email || ''}
              onChange={(e) => setEditingUser((prev) => (prev ? { ...prev, useremail: e.target.value } : prev))}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingUser(null)}>Cancel</Button>
          <Button variant="contained" onClick={handleUpdate}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
