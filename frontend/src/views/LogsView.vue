<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'

const logs = ref([])
const loading = ref(true)
const err = ref('')

onMounted(async () => {
  try { logs.value = await api('/api/audit-logs') || [] }
  catch (e) { err.value = e.message }
  finally { loading.value = false }
})
</script>

<template>
  <div>
    <div class="card card-pad" style="margin-bottom:16px;">
      <h3 style="margin:0;">📝 Audit Log</h3>
      <p class="muted" style="font-size:11px;">Jejak digital seluruh aktivitas (ISO/IEC 27001 · A.8.15 logging &amp; monitoring) · Khusus Admin</p>
    </div>

    <div v-if="loading" class="empty">⏳ Memuat…</div>
    <div v-else-if="err" class="alert alert-error">{{ err }}</div>
    <div class="card" v-else>
      <div class="table-wrap">
        <table class="tbl">
          <thead><tr><th>Waktu</th><th>User</th><th>Tipe</th><th>Aksi</th><th>Ref</th><th>IP</th></tr></thead>
          <tbody>
            <tr v-for="l in logs" :key="l.id">
              <td class="muted">{{ l.created_at }}</td>
              <td><b>{{ l.user_name }}</b></td>
              <td><span class="badge badge-gray">{{ l.user_type }}</span></td>
              <td>{{ l.action }}</td>
              <td>{{ l.transaction_id || '—' }}</td>
              <td class="muted">{{ l.ip_address || '—' }}</td>
            </tr>
            <tr v-if="!logs.length"><td colspan="6" class="empty">Belum ada aktivitas tercatat.</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
