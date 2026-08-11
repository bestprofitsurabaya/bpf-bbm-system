<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'

const drivers = ref([])
const vehicles = ref([])
const bbms = ref([])
const loading = ref(true)
const err = ref('')
const msg = ref('')
const busy = ref(false)

async function load() {
  loading.value = true; err.value = ''
  try {
    const [d, v, b] = await Promise.all([
      api('/api/drivers').catch(() => []),
      api('/api/vehicles').catch(() => []),
      api('/api/bbm_types').catch(() => []),
    ])
    drivers.value = Array.isArray(d) ? d : []
    vehicles.value = Array.isArray(v) ? v : []
    bbms.value = Array.isArray(b) ? b : []
  } catch (e) { err.value = e.message }
  finally { loading.value = false }
}

async function toggleDriver(name, active) {
  busy.value = true; msg.value = ''
  try {
    await api(`/api/drivers/${encodeURIComponent(name)}/${active ? 'activate' : 'deactivate'}`, { method: 'POST' })
    msg.value = '✅ Status driver diperbarui'; load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { busy.value = false }
}

onMounted(load)
</script>

<template>
  <div>
    <div v-if="msg" class="alert" :class="msg.startsWith('✅') ? 'alert-success' : 'alert-error'">{{ msg }}</div>
    <div v-if="loading" class="empty">⏳ Memuat…</div>
    <div v-else-if="err" class="alert alert-error">{{ err }}</div>
    <template v-else>
      <div class="card card-pad" style="margin-bottom:16px;">
        <h3 style="margin:0;">🚗 Data Master</h3>
        <p class="muted" style="font-size:11px;">Khusus Admin · pengelolaan driver, kendaraan &amp; tipe BBM</p>
      </div>

      <div class="card" style="margin-bottom:16px;">
        <h3 style="padding:14px 18px 0;">👤 Driver</h3>
        <div class="table-wrap">
          <table class="tbl">
            <thead><tr><th>Nama</th><th>Nopol</th><th>Tipe</th><th>BBM</th><th>Status</th><th></th></tr></thead>
            <tbody>
              <tr v-for="d in drivers" :key="d.name">
                <td><b>{{ d.name }}</b></td><td>{{ d.nopol || '—' }}</td><td>{{ d.vehicle_type }}</td>
                <td>{{ d.bbm_type }}</td>
                <td><span class="badge" :class="d.is_active ? 'badge-green' : 'badge-red'">{{ d.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
                <td>
                  <button class="btn btn-sm" :disabled="busy" @click="toggleDriver(d.name, !d.is_active)">
                    {{ d.is_active ? '🔴 Nonaktifkan' : '🟢 Aktifkan' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="stat-grid">
        <div class="card card-pad">
          <h3>🚙 Kendaraan</h3>
          <div class="table-wrap">
            <table class="tbl">
              <thead><tr><th>Tipe</th><th>Merk</th><th>Kapasitas</th><th>Status</th></tr></thead>
              <tbody>
                <tr v-for="v in vehicles" :key="v.id || v.vehicle_type">
                  <td><b>{{ v.vehicle_type }}</b></td><td>{{ v.brand }}</td><td>{{ v.fuel_capacity }}</td>
                  <td><span class="badge" :class="v.is_active ? 'badge-green' : 'badge-red'">{{ v.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="card card-pad">
          <h3>⛽ Tipe BBM</h3>
          <div class="table-wrap">
            <table class="tbl">
              <thead><tr><th>Nama</th><th>Harga/L</th><th>Status</th></tr></thead>
              <tbody>
                <tr v-for="b in bbms" :key="b.id || b.name">
                  <td><b>{{ b.name }}</b></td><td>{{ 'Rp ' + Number(b.price_per_liter || 0).toLocaleString('id-ID') }}</td>
                  <td><span class="badge" :class="b.is_active ? 'badge-green' : 'badge-red'">{{ b.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
