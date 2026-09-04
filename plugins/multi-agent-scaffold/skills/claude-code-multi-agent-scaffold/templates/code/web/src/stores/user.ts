import { defineStore } from 'pinia'
import { ref } from 'vue'

/**
 * 用户状态
 */
export const useUserStore = defineStore('user', () => {
  const token = ref('')
  const username = ref('')

  function setToken(value: string) {
    token.value = value
  }

  function setUsername(value: string) {
    username.value = value
  }

  return { token, username, setToken, setUsername }
})
