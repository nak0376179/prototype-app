import { fetchAuthSession } from 'aws-amplify/auth'
import axios from 'axios'

const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 5000
})

axiosInstance.interceptors.request.use(async (config) => {
  try {
    const session = await fetchAuthSession()
    const token = session.tokens?.idToken?.toString()
    if (token) {
      config.headers.Authorization = 'Bearer ' + token
    }
  } catch (err) {
    console.warn('No ID token found or failed to fetch session', err)
  }
  return config
})

export default axiosInstance
