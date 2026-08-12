<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore, ROLE_META } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const brandIcon = '/static/icon-192.png'
const username = ref('')
const pin = ref('')
const showPin = ref(false)
const capsOn = ref(false)
const error = ref('')
const loading = ref(false)

function checkCaps(e) {
  capsOn.value = e.getModifierState && e.getModifierState('CapsLock')
}

async function submit() {
  error.value = ''
  if (!username.value.trim() || !pin.value) { error.value = 'Username dan PIN wajib diisi.'; return }
  loading.value = true
  try {
    const d = await auth.login(username.value.trim(), pin.value)
    const target = route.query.next && route.query.next.startsWith('/app/')
      ? route.query.next
      : (ROLE_META[d.user.role]?.home || '/dashboard')
    router.push(target)
  } catch (e) {
    error.value = e.message || 'Login gagal'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <img :src="brandIcon" alt="BPF" />
        <h1>BPF Fleet &amp; BBM System</h1>
        <p>PT Bestprofit Futures · Surabaya</p>
      </div>

      <div v-if="error" class="alert alert-error">{{ error }}</div>

      <form @submit.prevent="submit">
        <div class="field">
          <label>Username</label>
          <input class="input" v-model="username" placeholder="cth: admin" autocomplete="username" required autofocus />
        </div>
        <div class="field">
          <label for="login-pin">PIN 6-digit</label>
          <div class="pin-wrap">
            <input id="login-pin" class="input" v-model="pin" :type="showPin ? 'text' : 'password'" maxlength="6" inputmode="numeric"
                   placeholder="••••••" autocomplete="current-password" @keyup="checkCaps" required />
            <button type="button" class="btn-icon pin-eye" :title="showPin ? 'Sembunyikan PIN' : 'Lihat PIN'"
                    :aria-label="showPin ? 'Sembunyikan PIN' : 'Lihat PIN'" @click="showPin = !showPin">
              {{ showPin ? '🙈' : '👁' }}
            </button>
          </div>
          <div v-if="capsOn" class="caps-hint" role="note">⚠️ Caps Lock sedang aktif — pastikan PIN tidak terkunci huruf besar.</div>
        </div>
        <button class="btn btn-primary" style="width:100%;justify-content:center;padding:11px;" :disabled="loading">
          {{ loading ? '⏳ Memverifikasi…' : '🔐 Masuk' }}
        </button>
      </form>

      <div class="login-foot">
        <p>Hak akses Anda mengikuti peran (role) yang diberikan Admin — hanya menu yang menjadi wewenang Anda yang tampil (ISO/IEC 27001 · least privilege).</p>
        <div class="row" style="justify-content:center;margin-top:10px;">
          <span v-for="(m, r) in ROLE_META" :key="r" class="badge badge-gray">{{ m.icon }} {{ m.label }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px;
  background:
    radial-gradient(at 0% 0%, rgba(37, 99, 235, .08) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(5, 150, 105, .08) 0px, transparent 50%), var(--bg);
}
.login-card {
  width: 100%; max-width: 400px; background: var(--surface); border: 1px solid var(--border);
  border-radius: 16px; padding: 30px 28px; box-shadow: var(--shadow-lg); animation: popIn .2s ease;
}
.login-brand { text-align: center; margin-bottom: 20px; }
.login-brand img { width: 54px; height: 54px; border-radius: 13px; box-shadow: 0 4px 14px rgba(37, 99, 235, .25); }
.login-brand h1 { font-size: 17px; font-weight: 800; margin-top: 10px; }
.login-brand p { font-size: 11px; color: var(--text-3); margin-top: 2px; }
.login-foot { margin-top: 18px; font-size: 11px; color: var(--text-3); text-align: center; line-height: 1.5; }
.pin-wrap { position: relative; display: flex; }
.pin-wrap .input { width: 100%; letter-spacing: 6px; font-size: 18px; padding-right: 44px; }
.pin-eye {
  position: absolute; right: 4px; top: 50%; transform: translateY(-50%);
  width: 34px; height: 34px; border-radius: 8px;
}
.caps-hint { font-size: 11px; color: var(--warning); font-weight: 600; }
</style>
