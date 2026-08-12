<script setup>
import { computed, onMounted, ref } from 'vue'
import { api } from '../../api'
import StatCard from '../../components/StatCard.vue'
import Modal from '../../components/Modal.vue'

const today = new Date().toISOString().slice(0, 10)
const date = ref(today)
const list = ref([])
const stats = ref(null)
const drivers = ref([])
const sug = ref({}) // saran driver per sesi { '1': 'RIVAN', '2': 'BUDI' }
const members = ref([]) // semua marketing anggota (untuk filter board)
const member = ref('') // filter anggota aktif
const memberSummary = ref([])
const sesiFilter = ref('all')
const loading = ref(true)
const err = ref('')
const selDriver = ref({}) // select assign per baris "Belum Ditugaskan"
const selGanti = ref({}) // select ganti driver per baris "Tugas Per Driver"
const busy = ref(false)
const msg = ref('')

// Modal hasil kunjungan (✅ Selesai / 🎯 ubah hasil)
const visitAppt = ref(null)
const visitForm = ref({ result: '', note: '' })
const savingVisit = ref(false)

const VISIT_LABELS = { ditemui: '😊 Ditemui', prospek: '🤝 Prospek', gagal: '❌ Gagal' }

async function load() {
  loading.value = true; err.value = ''
  const params = { date: date.value }
  if (member.value) params.member = member.value
  try {
    const d = await api('/api/appointments', { params })
    list.value = d.data || d.list || []
    stats.value = d.stats || null
  } catch (e) { err.value = e.message }
  try { drivers.value = await api('/api/drivers') } catch { drivers.value = [] }
  try { sug.value = await api('/api/appointments/suggestions', { params: { date: date.value } }) } catch { sug.value = {} }
  try {
    const m = await api('/api/marketing/members')
    members.value = m.members || []
  } catch { members.value = [] }
  try {
    const ms = await api('/api/appointments/member-summary', { params: { date: date.value } })
    memberSummary.value = ms.members || []
  } catch { memberSummary.value = [] }
  // Isi default select assign dengan saran load-balancing per sesi (bila belum dipilih)
  for (const a of list.value) {
    if (a.status === 'scheduled' && !selDriver.value[a.id]) {
      selDriver.value[a.id] = sug.value[a.sesi] || ''
    }
  }
  loading.value = false
}

const scheduledRows = computed(() =>
  list.value.filter((a) => a.status === 'scheduled' && (sesiFilter.value === 'all' || a.sesi === sesiFilter.value)))

const byDriver = computed(() => {
  // Board menampilkan tugas berjalan (assigned) + kunjungan selesai (completed)
  // agar badge hasil kunjungan & tombol 🎯 Hasil tetap bisa diakses.
  const m = {}
  for (const a of list.value) {
    if ((a.status === 'assigned' || a.status === 'completed') && a.driver_name) {
      (m[a.driver_name] = m[a.driver_name] || []).push(a)
    }
  }
  return Object.entries(m)
})

function suggestFor(a) { return sug.value[a.sesi] || '' }

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

async function doGanti(a) {
  const driver = selGanti.value[a.id]
  if (!driver) return
  if (!confirm(`Ganti driver ${a.driver_name || '-'} → ${driver} untuk ${a.display_id}?`)) return
  busy.value = true; msg.value = ''
  try {
    const r = await api(`/api/appointments/${a.id}/assign`, { method: 'POST', body: { driver_name: driver } })
    msg.value = '✅ ' + (r.message || r.msg || 'Driver diganti')
    selGanti.value[a.id] = ''
    load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { busy.value = false }
}

async function doUnassign(a) {
  if (!confirm(`Batalkan penugasan ${a.display_id} dari ${a.driver_name}?`)) return
  busy.value = true; msg.value = ''
  try {
    const r = await api(`/api/appointments/${a.id}/unassign`, { method: 'POST' })
    msg.value = '✅ ' + (r.msg || 'Penugasan dibatalkan')
    load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { busy.value = false }
}

async function doCancel(a) {
  const reason = prompt(`Alasan membatalkan ${a.display_id} (${a.nasabah_name}):`, '')
  if (reason === null) return
  busy.value = true; msg.value = ''
  try {
    const r = await api(`/api/appointments/${a.id}/cancel`, { method: 'POST', body: { reason } })
    msg.value = '✅ ' + (r.msg || 'Appointment dibatalkan')
    load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { busy.value = false }
}

async function doArea(a) {
  const area = prompt(`Area untuk ${a.nasabah_name} (${a.display_id}):`, a.area || '')
  if (area === null || !area.trim()) return
  busy.value = true; msg.value = ''
  try {
    const r = await api(`/api/appointments/${a.id}`, { method: 'PATCH', body: { area: area.trim() } })
    msg.value = '✅ ' + (r.msg || 'Area diperbarui')
    load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { busy.value = false }
}

function openVisit(a, edit = false) {
  visitAppt.value = a
  visitForm.value = { result: edit ? (a.visit_result || '') : '', note: edit ? (a.visit_note || '') : '' }
}

async function saveVisit() {
  const a = visitAppt.value
  if (!a) return
  savingVisit.value = true; msg.value = ''
  try {
    if (a.status === 'assigned') {
      // Chief Driver menandai selesai + mencatat hasil kunjungan (wajib pilih hasil)
      if (!visitForm.value.result) {
        msg.value = '⚠️ Pilih hasil kunjungan terlebih dahulu.'
        return
      }
      const r = await api(`/api/appointments/${a.id}/complete`, {
        method: 'POST', body: { result: visitForm.value.result, note: visitForm.value.note },
      })
      msg.value = '✅ ' + (r.msg || 'Appointment selesai')
    } else {
      // Edit hasil kunjungan kapan saja (PATCH visit_result/visit_note)
      const body = { visit_result: visitForm.value.result || '', visit_note: visitForm.value.note }
      const r = await api(`/api/appointments/${a.id}`, { method: 'PATCH', body })
      msg.value = '✅ ' + (r.msg || 'Hasil kunjungan disimpan')
    }
    visitAppt.value = null
    load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { savingVisit.value = false }
}

function applyMemberFilter(name) {
  member.value = member.value === name ? '' : name
  load()
}

function visitBadge(a) { return a.visit_result ? (VISIT_LABELS[a.visit_result] || a.visit_result) : '' }

const STATUS = { scheduled: 'badge-amber', assigned: 'badge-blue', completed: 'badge-green', cancelled: 'badge-gray' }

onMounted(load)
</script>

<template>
  <div>
    <div class="card card-pad" style="margin-bottom:16px;">
      <div class="row" style="flex-wrap:wrap;gap:10px;">
        <div class="field" style="margin:0;"><label>Tanggal Board</label>
          <input class="input" type="date" v-model="date" @change="load" />
        </div>
        <div class="field" style="margin:0;"><label>Filter Marketing Anggota</label>
          <select class="select" v-model="member" @change="load" style="min-width:180px;">
            <option value="">Semua anggota</option>
            <option v-for="m in members" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <span v-if="msg" class="alert" :class="msg.startsWith('✅') ? 'alert-success' : 'alert-error'" style="margin:0;">{{ msg }}</span>
        <div class="spacer"></div>
        <a class="btn" :href="`/api/appointments/export?date=${date}${member ? '&member=' + encodeURIComponent(member) : ''}`" target="_blank">📥 Unduh Rekap Excel</a>
      </div>
    </div>

    <div v-if="loading" class="empty skeleton">⏳ Memuat…</div>
    <div v-else-if="err" class="alert alert-error">{{ err }}</div>
    <template v-else>
      <div class="stat-grid" style="margin-bottom:16px;">
        <StatCard icon="📋" label="Total" :value="stats?.total ?? list.length" color="#2563eb" />
        <StatCard icon="⏳" label="Belum Ditugaskan" :value="stats?.scheduled ?? 0" color="#d97706" />
        <StatCard icon="🚗" label="Ditugaskan" :value="stats?.assigned ?? 0" color="#0891b2" />
        <StatCard icon="✅" label="Selesai" :value="stats?.completed ?? 0" color="#059669" />
        <StatCard icon="✕" label="Batal" :value="stats?.cancelled ?? 0" color="#dc2626" />
      </div>

      <!-- Ringkasan per Marketing Anggota -->
      <div v-if="memberSummary.length" class="card card-pad" style="margin-bottom:16px;">
        <h3>📊 Ringkasan per Marketing Anggota</h3>
        <div class="table-wrap">
          <table class="tbl">
            <thead><tr><th>Anggota</th><th>Total</th><th>⏳</th><th>🚗</th><th>✅</th><th>✕</th><th>😊 Ditemui</th><th>🤝 Prospek</th><th>❌ Gagal</th><th>🌅 Sesi 1</th><th>🌆 Sesi 2</th></tr></thead>
            <tbody>
              <tr v-for="m in memberSummary" :key="m.marketing_member"
                  :class="member === m.marketing_member ? 'row-active' : ''"
                  style="cursor:pointer;" :title="member === m.marketing_member ? 'Klik untuk lepas filter' : 'Klik untuk filter board ke anggota ini'"
                  @click="applyMemberFilter(m.marketing_member)">
                <td><b>{{ m.marketing_member }}</b></td>
                <td>{{ m.total }}</td>
                <td>{{ m.scheduled }}</td>
                <td>{{ m.assigned }}</td>
                <td>{{ m.completed }}</td>
                <td>{{ m.cancelled }}</td>
                <td>{{ m.ditemui }}</td>
                <td>{{ m.prospek }}</td>
                <td>{{ m.gagal }}</td>
                <td>{{ m.sesi1 }}</td>
                <td>{{ m.sesi2 }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="card card-pad" style="margin-bottom:16px;">
        <div class="row" style="flex-wrap:wrap;gap:8px;margin-bottom:10px;">
          <h3 style="margin:0;">📋 Belum Ditugaskan</h3>
          <button class="btn btn-sm" :class="sesiFilter === 'all' ? 'btn-primary' : ''" @click="sesiFilter = 'all'">Semua</button>
          <button class="btn btn-sm" :class="sesiFilter === '1' ? 'btn-primary' : ''" @click="sesiFilter = '1'">🌅 Sesi 1</button>
          <button class="btn btn-sm" :class="sesiFilter === '2' ? 'btn-primary' : ''" @click="sesiFilter = '2'">🌆 Sesi 2</button>
        </div>
        <div class="table-wrap">
          <table class="tbl">
            <thead><tr><th>Nasabah</th><th>Sesi</th><th>Area</th><th>Marketing</th><th>Tugaskan ke</th><th></th></tr></thead>
            <tbody>
              <tr v-for="a in scheduledRows" :key="a.id">
                <td><b>{{ a.nasabah_name }}</b><div class="muted" style="font-size:11px;">{{ a.alamat }}</div></td>
                <td>{{ a.sesi === '2' ? '🌆 14.30' : '🌅 08.30' }}</td>
                <td>
                  {{ a.area }}
                  <button class="btn-icon" style="margin-left:4px;" title="Ubah area manual (override deteksi otomatis)" @click="doArea(a)">🌍</button>
                </td>
                <td>{{ a.marketing_member }}</td>
                <td>
                  <select class="select assign-select" v-model="selDriver[a.id]" style="min-width:150px;">
                    <option value="">Pilih driver…</option>
                    <option v-for="dr in drivers.filter((x) => x.is_active)" :key="dr.name" :value="dr.name">{{ dr.name }}</option>
                  </select>
                  <div v-if="suggestFor(a)" class="muted" style="font-size:11px;">💡 Saran: {{ suggestFor(a) }}</div>
                </td>
                <td>
                  <button class="btn btn-primary btn-sm" :disabled="busy || !selDriver[a.id]" @click="doAssign(a)">Tugaskan</button>
                  <button class="btn btn-sm btn-danger" :disabled="busy" style="margin-left:6px;" title="Batalkan appointment" @click="doCancel(a)">✕</button>
                </td>
              </tr>
              <tr v-if="!scheduledRows.length"><td colspan="6" class="empty">Semua sudah ditugaskan. 🎉</td></tr>
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
              <thead><tr><th>Nasabah</th><th>Alamat</th><th>Sesi</th><th>Status</th><th>Hasil</th><th>Aksi</th></tr></thead>
              <tbody>
                <tr v-for="a in apps" :key="a.id">
                  <td><b>{{ a.nasabah_name }}</b><div class="muted" style="font-size:11px;">{{ a.display_id }} · {{ a.marketing_member }}</div></td>
                  <td class="muted">{{ a.alamat }}</td>
                  <td>{{ a.sesi === '2' ? '🌆 14.30' : '🌅 08.30' }}</td>
                  <td><span class="badge" :class="STATUS[a.status] || 'badge-gray'">{{ a.status }}</span></td>
                  <td><span v-if="visitBadge(a)" class="badge badge-green">{{ visitBadge(a) }}</span><span v-else class="muted">—</span></td>
                  <td style="white-space:nowrap;">
                    <template v-if="a.status === 'assigned'">
                      <select class="select ganti-select" v-model="selGanti[a.id]" style="min-width:110px;margin-right:4px;">
                        <option value="">Ganti ke…</option>
                        <option v-for="dr in drivers.filter((x) => x.is_active)" :key="dr.name" :value="dr.name">{{ dr.name }}</option>
                      </select>
                      <button class="btn btn-sm" :disabled="busy || !selGanti[a.id]" title="Ganti driver" @click="doGanti(a)">🔄</button>
                      <button class="btn btn-sm" :disabled="busy" style="margin-left:4px;" title="Batalkan tugas" @click="doUnassign(a)">↩️</button>
                      <button class="btn btn-sm btn-primary" :disabled="busy" style="margin-left:4px;" title="Tandai selesai + catat hasil kunjungan" @click="openVisit(a)">✅</button>
                      <button class="btn btn-sm btn-danger" :disabled="busy" style="margin-left:4px;" title="Batalkan appointment" @click="doCancel(a)">✕</button>
                    </template>
                    <button v-else class="btn btn-sm" :disabled="busy" title="Ubah hasil kunjungan" @click="openVisit(a, true)">🎯 Hasil</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-if="!byDriver.length" class="empty">Belum ada penugasan.</div>
      </div>
    </template>

    <!-- Modal Hasil Kunjungan -->
    <Modal v-if="visitAppt" :title="visitAppt.status === 'assigned' ? '✅ Selesaikan ' + visitAppt.display_id : '🎯 Hasil Kunjungan — ' + visitAppt.display_id" @close="visitAppt = null">
      <p class="muted" style="font-size:12px;margin-bottom:10px;">
        {{ visitAppt.nasabah_name }} · {{ visitAppt.alamat }} · {{ visitAppt.sesi === '2' ? '🌆 Sesi 2' : '🌅 Sesi 1' }}
        <span v-if="visitAppt.driver_name"> · 🚗 {{ visitAppt.driver_name }}</span>
      </p>
      <div class="field"><label>Hasil kunjungan <span v-if="visitAppt.status === 'assigned'" class="req">*</span></label>
        <select class="select" v-model="visitForm.result">
          <option value="">— Pilih hasil —</option>
          <option value="ditemui">😊 Ditemui</option>
          <option value="prospek">🤝 Prospek</option>
          <option value="gagal">❌ Gagal</option>
        </select>
      </div>
      <div class="field" style="margin-top:8px;"><label>Alasan / catatan (opsional)</label>
        <textarea class="textarea" v-model="visitForm.note" rows="2" placeholder="Catatan hasil kunjungan…"></textarea>
      </div>
      <div class="row" style="justify-content:flex-end;gap:6px;margin-top:10px;">
        <span v-if="msg" class="alert" :class="msg.startsWith('✅') ? 'alert-success' : 'alert-error'" style="margin:0;">{{ msg }}</span>
        <div class="spacer"></div>
        <button class="btn" @click="visitAppt = null">Batal</button>
        <button class="btn btn-primary" :disabled="savingVisit" @click="saveVisit">{{ visitAppt.status === 'assigned' ? '✅ Selesai' : '💾 Simpan Hasil' }}</button>
      </div>
    </Modal>
  </div>
</template>
