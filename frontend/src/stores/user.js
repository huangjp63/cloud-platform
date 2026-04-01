import { defineStore } from 'pinia'
import { login, logout, getUserInfo } from '@/api/user'
import { getToken, setToken, removeToken } from '@/utils/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: getToken() || '',
    userInfo: null
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    isAdmin: (state) => state.userInfo?.role === 'admin'
  },
  
  actions: {
    async login(loginForm) {
      const res = await login(loginForm)
      this.token = res.data.token
      setToken(res.data.token)
      return res
    },
    
    async logout() {
      await logout()
      this.token = ''
      this.userInfo = null
      removeToken()
    },
    
    async getUserInfo() {
      const res = await getUserInfo()
      this.userInfo = res.data
      return res
    }
  }
})
