import { useQuery } from '@tanstack/react-query'
import axios from './axios'

export type UserSummary = {
  userid: string
  username: string
}

export const fetchGroupUsers = async (groupid: string): Promise<UserSummary[]> => {
  const response = await axios.get(`/groups/${groupid}/users`)
  return response.data.Items
}

export const useFetchGroupUsersQuery = (groupid: string) =>
  useQuery({
    queryKey: ['group', groupid, 'users'],
    queryFn: () => fetchGroupUsers(groupid),
    enabled: !!groupid
  })
