<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'

const logs = ref([])
const loading = ref(true)
const err = ref('')
const fAction = ref('all')
const fRole = ref('all')

const actions = computed(() => ['all', ...[...new Set(logs.value.map((l) => l.action).filter(Boolean))].sort()])
const roles = computed(() => ['all', ...[...new Set(logs.value.map((l) => l.user_type).filter(Boolean))].sort()])
const filtered = computed(() =>
  logs.value.filter((l) =>
    (fAction.value === 'all' || l.action === fAction.value) &&
    (fRole.value === 'all' || l.user_type === fRole.value)))
const todayCount = computed(() =>
  logs.value.filter((l) => new Date(l.created_at).toDateString() === new Date().toDateString()).length)

const actionLabel = (a) => (a || '—').replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())

onMounted(async () => {
  try { logs.value = await api('/api/audit-logs') || [] }
  catch (e) { err.value = e.message }
  finally { loading.value = false }
})
</script>

<template>
  <div>
    <div class="card card-pad" style="margin-bottom:16px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
      <div class="grow">
        <h3 style="margin:0;">📝 Audit Log</h3>
        <p class="muted" style="font-size:11px;">Jejak digital seluruh aktivitas (ISO/IEC 27001 · A.8.15 logging &amp; monitoring) · Khusus Admin</p>
      </div>
      <span class="badge badge-blue">📅 Hari ini: {{ todayCount }}</span>
      <span class="badge badge-gray">Total: {{ filtered.length }} / {{ logs.length }}</span>
    </div>

    <div v-if="loading" class="empty">⏳ Memuat…</div>
    <div v-else-if="err" class="alert alert-error">{{ err }}</div>
    <template v-else>
      <div class="card card-pad" style="margin-bottom:16px;">
        <div class="row">
          <div class="field" style="margin:0;flex:1;">
            <label>Filter Aksi</label>
            <select class="select" v-model="fAction">
              <option v-for="a in actions" :key="a" :value="a">{{ a === 'all' ? 'Semua Aksi' : actionLabel(a) }}</option>
            </select>
          </div>
          <div class="field" style="margin:0;flex:1;">
            <label>Filter Peran</label>
            <select class="select" v-model="fRole">
              <option v-for="r in roles" :key="r" :value="r">{{ r === 'all' ? 'Semua Peran' : r.toUpperCase() }}</option>
            </select>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="tbl">
            <thead><tr><th>Waktu</th><th>User</th><th>Tipe</th><th>Aksi</th><th>Ref</th><th>IP</th></tr></thead>
            <tbody>
              <tr v-for="l in filtered" :key="l.id">
                <td class="muted">{{ l.created_at }}</td>
                <td><b>{{ l.user_name }}</b></td>
                <td><span class="badge badge-gray">{{ l.user_type }}</span></td>
                <td>{{ actionLabel(l.action) }}</td>
                <td>{{ l.transaction_id || '—' }}</td>
                <td class="muted">{{ l.ip_address || '—' }}</td>
              </tr>
              <tr v-if="!filtered.length"><td colspan="6" class="empty">Tidak ada data dengan filter ini.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
