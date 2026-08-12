<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../api'
import Modal from '../components/Modal.vue'

const drivers = ref([])
const vehicles = ref([])
const bbms = ref([])
const loading = ref(true)
const err = ref('')
const msg = ref('')
const busy = ref(false)

const showDriverForm = ref(false)
const driverForm = ref({ driver_name: '', nopol: '', vehicle_type: 'AVANZA', bbm_type: 'PERTALITE' })
const showVehicleForm = ref(false)
const vehicleForm = ref({ nopol: '', vehicle_type: 'AVANZA', brand: 'Toyota', bbm_default: 'PERTALITE' })

const vehicleTypes = computed(() => ['AVANZA', ...[...new Set(vehicles.value.map((v) => (v.vehicle_type || '').trim()).filter(Boolean))].sort()].filter((v, i, a) => a.indexOf(v) === i).slice(0, 12))
const bbmNames = computed(() => bbms.value.map((b) => b.name).filter(Boolean))

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

async function addDriver() {
  busy.value = true; msg.value = ''
  try {
    const body = { ...driverForm.value }
    body.driver_name = body.driver_name.trim().toUpperCase()
    body.nopol = body.nopol.trim().toUpperCase()
    if (!body.driver_name) { msg.value = '❌ Nama driver wajib diisi'; return }
    await api('/api/drivers/sync', { method: 'POST', body })
    msg.value = '✅ Driver tersimpan'
    showDriverForm.value = false
    driverForm.value = { driver_name: '', nopol: '', vehicle_type: 'AVANZA', bbm_type: 'PERTALITE' }
    load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { busy.value = false }
}

async function deleteDriver(name) {
  if (!confirm(`HAPUS permanen driver "${name}"?`)) return
  busy.value = true; msg.value = ''
  try {
    await api(`/api/drivers/${encodeURIComponent(name)}/delete`, { method: 'POST' })
    msg.value = '✅ Driver dihapus'; load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { busy.value = false }
}

/** Reset PIN massal seluruh akun driver ke 123456 (onboarding cepat). */
async function resetDriverPinMassal() {
  if (!confirm('Reset PIN SEMUA akun driver menjadi 123456?')) return
  busy.value = true; msg.value = ''
  try {
    const r = await api('/api/drivers/pin-reset', { method: 'POST', body: { new_pin: '123456' } })
    msg.value = '✅ ' + (r.msg || 'PIN semua driver direset ke 123456')
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { busy.value = false }
}

async function addVehicle() {
  busy.value = true; msg.value = ''
  try {
    const body = { ...vehicleForm.value }
    body.nopol = body.nopol.trim().toUpperCase()
    if (!body.nopol) { msg.value = '❌ No. Polisi wajib diisi'; return }
    await api('/api/vehicles/add', { method: 'POST', body })
    msg.value = '✅ Kendaraan tersimpan'
    showVehicleForm.value = false
    vehicleForm.value = { nopol: '', vehicle_type: 'AVANZA', brand: 'Toyota', bbm_default: 'PERTALITE' }
    load()
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
      <div class="card card-pad" style="margin-bottom:16px;display:flex;align-items:center;">
        <div class="grow">
          <h3 style="margin:0;">🚗 Data Master</h3>
          <p class="muted" style="font-size:11px;">Khusus Admin · pengelolaan driver, kendaraan &amp; tipe BBM</p>
        </div>
        <button class="btn btn-primary btn-sm" @click="showDriverForm = true">➕ Tambah Driver</button>
        <button class="btn btn-sm" style="margin-left:8px;" @click="showVehicleForm = true">🚙 Tambah Kendaraan</button>
        <button class="btn btn-sm" style="margin-left:8px;" :disabled="busy" @click="resetDriverPinMassal" title="Set PIN semua akun driver ke 123456">🔑 PIN Driver = 123456</button>
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
                  <button class="btn btn-sm btn-danger" :disabled="busy" style="margin-left:6px;" @click="deleteDriver(d.name)" title="Hapus permanen">🗑</button>
                </td>
              </tr>
              <tr v-if="!drivers.length"><td colspan="6" class="empty">Belum ada driver.</td></tr>
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

    <Modal v-if="showDriverForm" title="➕ Tambah Driver" @close="showDriverForm = false">
      <div class="form-grid">
        <div class="field"><label>Nama Driver *</label><input class="input" v-model="driverForm.driver_name" placeholder="mis. RIVAN" /></div>
        <div class="field"><label>No. Polisi</label><input class="input" v-model="driverForm.nopol" placeholder="mis. L 1234 AB" /></div>
        <div class="field"><label>Tipe Kendaraan</label>
          <select class="select" v-model="driverForm.vehicle_type"><option v-for="t in vehicleTypes" :key="t" :value="t">{{ t }}</option></select>
        </div>
        <div class="field"><label>Tipe BBM</label>
          <select class="select" v-model="driverForm.bbm_type"><option v-for="b in bbmNames" :key="b" :value="b">{{ b }}</option></select>
        </div>
      </div>
      <div class="row" style="justify-content:flex-end;margin-top:12px;">
        <button class="btn" @click="showDriverForm = false">Batal</button>
        <button class="btn btn-primary" :disabled="busy" @click="addDriver">💾 Simpan</button>
      </div>
    </Modal>

    <Modal v-if="showVehicleForm" title="🚙 Tambah Kendaraan" @close="showVehicleForm = false">
      <div class="form-grid">
        <div class="field"><label>No. Polisi *</label><input class="input" v-model="vehicleForm.nopol" placeholder="mis. L 1234 AB" /></div>
        <div class="field"><label>Tipe Kendaraan</label>
          <select class="select" v-model="vehicleForm.vehicle_type"><option v-for="t in vehicleTypes" :key="t" :value="t">{{ t }}</option></select>
        </div>
        <div class="field"><label>Merk</label><input class="input" v-model="vehicleForm.brand" /></div>
        <div class="field"><label>BBM Default</label>
          <select class="select" v-model="vehicleForm.bbm_default"><option v-for="b in bbmNames" :key="b" :value="b">{{ b }}</option></select>
        </div>
      </div>
      <div class="row" style="justify-content:flex-end;margin-top:12px;">
        <button class="btn" @click="showVehicleForm = false">Batal</button>
        <button class="btn btn-primary" :disabled="busy" @click="addVehicle">💾 Simpan</button>
      </div>
    </Modal>
  </div>
</template>
