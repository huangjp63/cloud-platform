import { defineStore } from 'pinia'
import { useUserStore } from './user'

export const usePermissionStore = defineStore('permission', {
  getters: {
    isAdmin: () => {
      const userStore = useUserStore()
      return userStore.isAdmin
    },
    
    canAccessAdmin: () => {
      const userStore = useUserStore()
      return userStore.isAdmin
    }
  },
  
  actions: {
    checkPermission(role) {
      const userStore = useUserStore()
      if (role === 'admin') {
        return userStore.isAdmin
      }
      return true
    }
  }
})
