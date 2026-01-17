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
import { useFetchItemsQuery, useCreateItemMutation, useUpdateItemMutation, useDeleteItemMutation } from '@/hooks/api/items'

type APIError = string | { msg: string }[] | null

export default function ItemsPage() {
  const [error, setError] = useState<APIError>(null)

  const { data, isLoading, refetch } = useFetchItemsQuery()
  const items = data?.items ?? []

  const createItem = useCreateItemMutation()
  const updateItem = useUpdateItemMutation()
  const deleteItem = useDeleteItemMutation()

  const [newItem, setNewItem] = useState({ id: '', name: '', price: '', category: '' })
  const [editingItem, setEditingItem] = useState<{ id: string; name: string; price: string; category: string } | null>(null)

  const handleCreate = async () => {
    setError(null)
    try {
      await createItem.mutateAsync({ ...newItem, price: parseFloat(newItem.price) })
      setNewItem({ id: '', name: '', price: '', category: '' })
      refetch()
    } catch (e: any) {
      const message = e?.response?.data?.detail || 'Failed to create item'
      setError(message)
    }
  }

  const handleUpdate = async () => {
    setError(null)
    if (editingItem) {
      try {
        await updateItem.mutateAsync({
          id: editingItem.id,
          data: {
            name: editingItem.name,
            price: parseFloat(editingItem.price),
            category: editingItem.category
          }
        })
        setEditingItem(null)
        refetch()
      } catch (e: any) {
        const message = e?.response?.data?.detail || 'Failed to update item'
        setError(message)
      }
    }
  }

  const handleDelete = async (id: string) => {
    setError(null)
    try {
      await deleteItem.mutateAsync(id)
      refetch()
    } catch (e: any) {
      const message = e?.response?.data?.detail || 'Failed to delete item'
      setError(message)
    }
  }

  if (isLoading) return <Typography>Loading...</Typography>

  return (
    <Box p={4}>
      <Typography variant="h4" mb={2}>
        Items API Demo
      </Typography>

      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {typeof error === 'string' ? error : Array.isArray(error) ? error.map((err, i) => <div key={i}>{err.msg}</div>) : 'Unknown error'}
        </Alert>
      )}

      {/* 新規作成フォーム */}
      <Stack spacing={2} direction="row" mb={3}>
        <TextField label="ID" value={newItem.id} onChange={(e) => setNewItem({ ...newItem, id: e.target.value })} />
        <TextField label="Name" value={newItem.name} onChange={(e) => setNewItem({ ...newItem, name: e.target.value })} />
        <TextField label="Price" type="number" value={newItem.price} onChange={(e) => setNewItem({ ...newItem, price: e.target.value })} />
        <TextField label="Category" value={newItem.category} onChange={(e) => setNewItem({ ...newItem, category: e.target.value })} />
        <Button variant="contained" onClick={handleCreate}>
          Add Item
        </Button>
      </Stack>

      {/* 一覧表示 */}
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Name</TableCell>
            <TableCell>Price</TableCell>
            <TableCell>Category</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {items.map((item: any) => (
            <TableRow key={item.id}>
              <TableCell>{item.id}</TableCell>
              <TableCell>{item.name}</TableCell>
              <TableCell>{item.price}</TableCell>
              <TableCell>{item.category}</TableCell>
              <TableCell>
                <Stack direction="row" spacing={1}>
                  <Button variant="outlined" onClick={() => setEditingItem({ ...item, price: String(item.price) })}>
                    Edit
                  </Button>
                  <Button variant="outlined" color="error" onClick={() => handleDelete(item.id)}>
                    Delete
                  </Button>
                </Stack>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>

      {/* 編集ダイアログ */}
      <Dialog open={!!editingItem} onClose={() => setEditingItem(null)} container={document.body}>
        <DialogTitle>Edit Item</DialogTitle>
        <DialogContent>
          <Stack spacing={2} mt={1}>
            <TextField
              label="Name"
              value={editingItem?.name || ''}
              onChange={(e) => setEditingItem((prev) => (prev ? { ...prev, name: e.target.value } : prev))}
            />
            <TextField
              label="Price"
              type="number"
              value={editingItem?.price || ''}
              onChange={(e) => setEditingItem((prev) => (prev ? { ...prev, price: e.target.value } : prev))}
            />
            <TextField
              label="Category"
              value={editingItem?.category || ''}
              onChange={(e) => setEditingItem((prev) => (prev ? { ...prev, category: e.target.value } : prev))}
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditingItem(null)}>Cancel</Button>
          <Button variant="contained" onClick={handleUpdate}>
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
