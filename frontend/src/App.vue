<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const auth = useAuthStore()

onMounted(() => {
  window.addEventListener('bpf:unauthorized', () => {
    auth.user = null
    localStorage.removeItem('bpf_csrf')
    router.push({ name: 'login' })
  })
})
</script>

<template>
  <router-view />
</template>
