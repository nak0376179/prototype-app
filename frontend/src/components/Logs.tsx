import {
  Box, Button, CircularProgress, FormControl, InputLabel, MenuItem, Select, Stack,
  Table, TableBody, TableCell, TableHead, TableRow, TextField, Typography
} from '@mui/material'
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import { Autocomplete } from '@mui/material'
import { useState } from 'react'
import { format } from 'date-fns'
import { ja } from 'date-fns/locale'
import { useFetchLogsQuery, type LogItem } from '@/hooks/api/logs'
import { useFetchGroupUsersQuery } from '@/hooks/api/groups'

export default function LogsPage({ groupid = 'group1' }: { groupid?: string }) {
  const [begin, setBegin] = useState<Date | null>(null)
  const [end, setEnd] = useState<Date | null>(null)
  const [filterMode, setFilterMode] = useState<'none' | 'userid' | 'type'>('none')
  const [userid, setUserid] = useState('')
  const [type, setType] = useState('')
  const [filters, setFilters] = useState<{ begin?: string; end?: string; userid?: string; type?: string }>({})
  const [pages, setPages] = useState<{ page: number; startkey: any | null }[]>([{ page: 1, startkey: undefined }])
  const currentPage = pages[pages.length - 1]

  const { data, isLoading, isFetching } = useFetchLogsQuery(
    {
      groupid,
      begin: filters.begin,
      end: filters.end,
      userid: filters.userid,
      type: filters.type,
      limit: 3,
      startkey: currentPage.startkey
    },
    true
  )

  const { data: users } = useFetchGroupUsersQuery(groupid)
  const typeOptions = ['INFO', 'WARN', 'ERROR']

  const handleApplyFilters = () => {
    setFilters({
      begin: begin?.toISOString(),
      end: end?.toISOString(),
      userid: filterMode === 'userid' ? userid || undefined : undefined,
      type: filterMode === 'type' ? type || undefined : undefined
    })
    setPages([{ page: 1, startkey: undefined }])
  }

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ja}>
      <Box p={4}>
        <Typography variant="h4" mb={2}>Logs for Group: {groupid}</Typography>

        <Stack direction="row" spacing={2} mb={2} flexWrap="wrap">
          <DatePicker
            label="開始日"
            value={begin}
            onChange={(newValue) => setBegin(newValue)}
            slotProps={{ textField: { size: 'small', sx: { minWidth: 160 } } }}
          />
          <DatePicker
            label="終了日"
            value={end}
            onChange={(newValue) => setEnd(newValue)}
            slotProps={{ textField: { size: 'small', sx: { minWidth: 160 } } }}
          />
          <FormControl sx={{ minWidth: 160 }} size="small">
            <InputLabel id="filter-mode-label">フィルタ条件</InputLabel>
            <Select
              labelId="filter-mode-label"
              value={filterMode}
              label="フィルタ条件"
              onChange={(e) => setFilterMode(e.target.value as any)}
            >
              <MenuItem value="none">なし</MenuItem>
              <MenuItem value="userid">ユーザーID</MenuItem>
              <MenuItem value="type">タイプ</MenuItem>
            </Select>
          </FormControl>

          {filterMode === 'userid' && (
            <Autocomplete
              size="small"
              sx={{ minWidth: 240 }}
              options={users ?? []}
              getOptionLabel={(u) => `${u.username} (${u.userid})`}
              renderInput={(params) => <TextField {...params} label="ユーザーID" />}
              value={users?.find((u) => u.userid === userid) ?? null}
              onChange={(_, newValue) => setUserid(newValue?.userid ?? '')}
            />
          )}

          {filterMode === 'type' && (
            <FormControl sx={{ minWidth: 160 }} size="small">
              <InputLabel id="type-label">タイプ</InputLabel>
              <Select
                labelId="type-label"
                value={type}
                label="タイプ"
                onChange={(e) => setType(e.target.value)}
              >
                {typeOptions.map((t) => (
                  <MenuItem key={t} value={t}>{t}</MenuItem>
                ))}
              </Select>
            </FormControl>
          )}

          <Button variant="contained" onClick={handleApplyFilters}>フィルター</Button>
        </Stack>

        {isLoading && <CircularProgress />}
        {!isLoading && data?.Items?.length === 0 && <Typography>ログが見つかりません。</Typography>}

        <Table>
          <TableHead>
            <TableRow>
              <TableCell>日時</TableCell>
              <TableCell>ユーザー</TableCell>
              <TableCell>タイプ</TableCell>
              <TableCell>メッセージ</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data?.Items?.map((log: LogItem) => (
              <TableRow key={log.groupid + log.created_at}>
                <TableCell>{format(new Date(log.created_at), 'yyyy年MM月dd日 (E) HH:mm:ss', { locale: ja })}</TableCell>
                <TableCell>{log.username ?? '-'} ({log.userid ?? '-'})</TableCell>
                <TableCell>{log.type ?? '-'}</TableCell>
                <TableCell>{log.message ?? '-'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>

        <Stack direction="row" spacing={2} mt={2} alignItems="center">
          <Button onClick={() => pages.length > 1 && setPages(p => p.slice(0, -1))} disabled={pages.length <= 1 || isFetching}>
            前へ
          </Button>
          <Typography>ページ: {currentPage.page}</Typography>
          <Button onClick={() => data?.LastEvaluatedKey && setPages(p => [...p, { page: currentPage.page + 1, startkey: data.LastEvaluatedKey }])}
            disabled={!data?.LastEvaluatedKey || isFetching}>
            次へ
          </Button>
        </Stack>
      </Box>
    </LocalizationProvider>
  )
}
