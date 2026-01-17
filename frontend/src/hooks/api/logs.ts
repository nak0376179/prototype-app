import { useQuery } from '@tanstack/react-query'
import axios from './axios'

export type LogItem = {
  groupid: string
  created_at: string
  userid: string
  username: string
  type: string
  message: string
}

type FetchLogsParams = {
  groupid: string
  begin?: string // ISO文字列
  end?: string   // ISO文字列
  limit?: number
  startkey?: string
  userid?: string
  type?: string
}

const fetchLogs = async ({
  groupid,
  begin,
  end,
  limit = 50,
  startkey,
  userid,
  type
}: FetchLogsParams) => {
  const params = new URLSearchParams()
  if (begin) params.append('begin', begin)
  if (end) params.append('end', end)
  if (limit) params.append('limit', String(limit))
  if (startkey) params.append('startkey', JSON.stringify(startkey))
  if (userid) params.append('userid', userid)
  if (type) params.append('type', type)

  const response = await axios.get(`/groups/${groupid}/logs?${params.toString()}`)
  return response.data
}

export const useFetchLogsQuery = (
  params: FetchLogsParams,
  enabled = true
) => {
  return useQuery({
    queryKey: ['logs', params],
    queryFn: () => fetchLogs(params),
    enabled: enabled && !!params.groupid
  })
}
