import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import axios from './axios'

const fetchUsers = async () => {
  const response = await axios.get('/users')
  return response.data?.Items
}

const createUser = async (user: { userid: string; username: string; email: string }) => {
  const response = await axios.post('/users', user)
  return response.data
}

const updateUser = async (user: { userid: string; username: string; email: string }) => {
  const response = await axios.put(`/users/${user.userid}`, user)
  return response.data
}

const deleteUser = async (userid: string) => {
  const response = await axios.delete(`/users/${userid}`)
  return response.data
}

// ✅ useQuery
export const useFetchUsersQuery = () => {
  return useQuery({
    queryKey: ['users'],
    queryFn: fetchUsers
  })
}

// ✅ useMutation: create
export const useCreateUserMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })
}

// ✅ useMutation: update
/*
export const useUpdateUserMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })
}
*/

// ユーザー更新ミューテーション（部分更新）
export const useUpdateUserMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: async ({ userid, data }: { userid: string; data: { username?: string; email?: string } }) => {
      const res = await axios.patch(`/users/${userid}`, data)
      return res.data
    },
    onSuccess: () => {
      // ユーザー一覧を再取得
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })
}

// ✅ useMutation: delete
export const useDeleteUserMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteUser,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] })
    }
  })
}
