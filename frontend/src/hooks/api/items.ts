import { useMutation, useQuery, useQueryClient, keepPreviousData } from '@tanstack/react-query'
import axios from './axios'

// 取得: クエリパラメータ対応（例: category, sort_by, limit, lastKey）
export const fetchItems = async (params?: { category?: string; sort_by?: string; limit?: number; lastKey?: string }) => {
  const response = await axios.get('/items', { params })
  return response.data // items: Item[], last_evaluated_key: any
}

// 作成
const createItem = async (item: { id: string; name: string; price: number; category: string }) => {
  const response = await axios.post('/items', item)
  return response.data
}

// 更新（部分更新対応）
const updateItem = async ({ id, data }: { id: string; data: { name?: string; price?: number; category?: string } }) => {
  const response = await axios.patch(`/items/${id}`, data)
  return response.data
}

// 削除
const deleteItem = async (id: string) => {
  const response = await axios.delete(`/items/${id}`)
  return response.data
}

// ✅ useQuery: 一覧取得
export const useFetchItemsQuery = (params?: { category?: string; sort_by?: string; limit?: number; lastKey?: string }) => {
  return useQuery({
    queryKey: ['items', params],
    queryFn: () => fetchItems(params),
    placeholderData: keepPreviousData
  })
}

// ✅ useMutation: 作成
export const useCreateItemMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    }
  })
}

// ✅ useMutation: 部分更新
export const useUpdateItemMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: updateItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    }
  })
}

// ✅ useMutation: 削除
export const useDeleteItemMutation = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: deleteItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] })
    }
  })
}
