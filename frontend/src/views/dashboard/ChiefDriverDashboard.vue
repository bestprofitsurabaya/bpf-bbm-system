<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api'
import StatCard from '../../components/StatCard.vue'

const today = new Date().toISOString().slice(0, 10)
const date = ref(today)
const list = ref([])
const stats = ref(null)
const drivers = ref([])
const loading = ref(true)
const err = ref('')
const selDriver = ref({})
const busy = ref(false)
const msg = ref('')

async function load() {
  loading.value = true; err.value = ''
  try {
    const d = await api('/api/appointments', { params: { date: date.value } })
    list.value = d.data || d.list || []
    stats.value = d.stats || null
  } catch (e) { err.value = e.message }
  try { drivers.value = await api('/api/drivers') } catch { drivers.value = [] }
  loading.value = false
}

const byDriver = computed(() => {
  const m = {}
  for (const a of list.value) {
    if (a.status === 'assigned' && a.driver_name) {
      (m[a.driver_name] = m[a.driver_name] || []).push(a)
    }
  }
  return Object.entries(m)
})

async function doAssign(a) {
  const driver = selDriver.value[a.id]
  if (!driver) return
  busy.value = true; msg.value = ''
  try {
    const r = await api(`/api/appointments/${a.id}/assign`, { method: 'POST', body: { driver_name: driver } })
    msg.value = '✅ ' + (r.message || r.msg || 'Ditugaskan')
    selDriver.value[a.id] = ''
    load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { busy.value = false }
}

const STATUS = { scheduled: 'badge-amber', assigned: 'badge-blue', completed: 'badge-green', cancelled: 'badge-gray' }

onMounted(load)
</script>

<template>
  <div>
    <div class="card card-pad" style="margin-bottom:16px;">
      <div class="row">
        <div class="field" style="margin:0;"><label>Tanggal Board</label>
          <input class="input" type="date" v-model="date" @change="load" />
        </div>
        <span v-if="msg" class="alert" :class="msg.startsWith('✅') ? 'alert-success' : 'alert-error'" style="margin:0;">{{ msg }}</span>
        <div class="spacer"></div>
        <a class="btn" :href="`/api/appointments/export?date=${date}`" target="_blank">📥 Unduh Rekap Excel</a>
      </div>
    </div>

    <div v-if="loading" class="empty">⏳ Memuat…</div>
    <div v-else-if="err" class="alert alert-error">{{ err }}</div>
    <template v-else>
      <div class="stat-grid" style="margin-bottom:16px;">
        <StatCard icon="📋" label="Total" :value="stats?.total ?? list.length" color="#2563eb" />
        <StatCard icon="⏳" label="Belum Ditugaskan" :value="stats?.scheduled ?? 0" color="#d97706" />
        <StatCard icon="🚗" label="Ditugaskan" :value="stats?.assigned ?? 0" color="#0891b2" />
        <StatCard icon="✅" label="Selesai" :value="stats?.completed ?? 0" color="#059669" />
        <StatCard icon="✕" label="Batal" :value="stats?.cancelled ?? 0" color="#dc2626" />
      </div>

      <div class="card card-pad" style="margin-bottom:16px;">
        <h3>📋 Belum Ditugaskan</h3>
        <div class="table-wrap">
          <table class="tbl">
            <thead><tr><th>Nasabah</th><th>Sesi</th><th>Area</th><th>Marketing</th><th>Tugaskan ke</th><th></th></tr></thead>
            <tbody>
              <tr v-for="a in list.filter((x) => x.status === 'scheduled')" :key="a.id">
                <td><b>{{ a.nasabah_name }}</b><div class="muted" style="font-size:11px;">{{ a.alamat }}</div></td>
                <td>{{ a.sesi === '2' ? '🌆 14.30' : '🌅 08.30' }}</td>
                <td>{{ a.area }}</td>
                <td>{{ a.marketing_member }}</td>
                <td>
                  <select class="select" v-model="selDriver[a.id]" style="min-width:150px;">
                    <option value="">Pilih driver…</option>
                    <option v-for="dr in drivers.filter((x) => x.is_active)" :key="dr.name" :value="dr.name">{{ dr.name }}</option>
                  </select>
                </td>
                <td><button class="btn btn-primary btn-sm" :disabled="busy || !selDriver[a.id]" @click="doAssign(a)">Tugaskan</button></td>
              </tr>
              <tr v-if="!list.filter((x) => x.status === 'scheduled').length"><td colspan="6" class="empty">Semua sudah ditugaskan. 🎉</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card card-pad">
        <h3>🚛 Tugas Per Driver</h3>
        <div v-for="[driver, apps] in byDriver" :key="driver" style="margin-bottom:14px;">
          <div class="role-chip" style="background:#7c3aed;margin-bottom:6px;">{{ driver }} · {{ apps.length }} kunjungan</div>
          <div class="table-wrap">
            <table class="tbl">
              <thead><tr><th>Nasabah</th><th>Alamat</th><th>Sesi</th><th>Status</th></tr></thead>
              <tbody>
                <tr v-for="a in apps" :key="a.id">
                  <td><b>{{ a.nasabah_name }}</b></td>
                  <td class="muted">{{ a.alamat }}</td>
                  <td>{{ a.sesi === '2' ? '🌆 14.30' : '🌅 08.30' }}</td>
                  <td><span class="badge" :class="STATUS[a.status] || 'badge-gray'">{{ a.status }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-if="!byDriver.length" class="empty">Belum ada penugasan.</div>
      </div>
    </template>
  </div>
</template>
