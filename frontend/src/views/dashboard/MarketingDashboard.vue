<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../../api'
import StatCard from '../../components/StatCard.vue'

const today = new Date().toISOString().slice(0, 10)
const list = ref([])
const stats = ref(null)
const loading = ref(true)
const err = ref('')

const form = ref({ appointment_date: today, sesi: '1', nasabah_name: '', nasabah_phone: '', alamat: '', marketing_member: '', notes: '' })
const saving = ref(false)
const msg = ref('')

async function load() {
  try {
    const d = await api('/api/appointments', { params: { date: today } })
    list.value = d.data || d.list || []
    stats.value = d.stats || null
  } catch (e) { err.value = e.message }
  finally { loading.value = false }
}

async function submit() {
  msg.value = ''
  if (!form.value.nasabah_name || !form.value.alamat || !form.value.marketing_member) {
    msg.value = '⚠️ Nama nasabah, alamat, dan nama marketing wajib diisi.'; return
  }
  saving.value = true
  try {
    const d = await api('/api/appointments', { method: 'POST', body: [form.value] })
    msg.value = '✅ ' + (d.message || d.msg || 'Appointment tersimpan')
    form.value = { appointment_date: today, sesi: '1', nasabah_name: '', nasabah_phone: '', alamat: '', marketing_member: '', notes: '' }
    load()
  } catch (e) { msg.value = '❌ ' + e.message }
  finally { saving.value = false }
}

const STATUS = { scheduled: ['⏳ Menunggu Driver', 'badge-amber'], assigned: ['🚗 Ditugaskan', 'badge-blue'], completed: ['✅ Selesai', 'badge-green'], cancelled: ['✕ Batal', 'badge-gray'] }

onMounted(load)
</script>

<template>
  <div>
    <div class="card card-pad" style="margin-bottom:16px;">
      <h3>📣 Input Appointment Baru</h3>
      <form @submit.prevent="submit">
        <div class="form-grid">
          <div class="field"><label>Tanggal <span class="req">*</span></label><input class="input" type="date" v-model="form.appointment_date" required /></div>
          <div class="field"><label>Sesi <span class="req">*</span></label>
            <select class="select" v-model="form.sesi">
              <option value="1">🌅 Sesi 1 (08.30)</option>
              <option value="2">🌆 Sesi 2 (14.30)</option>
            </select>
          </div>
          <div class="field"><label>Nama Calon Nasabah <span class="req">*</span></label><input class="input" v-model="form.nasabah_name" placeholder="Nama nasabah" required /></div>
          <div class="field"><label>Nama Marketing (prospek) <span class="req">*</span></label><input class="input" v-model="form.marketing_member" placeholder="Anggota tim yang memprospek" required /></div>
          <div class="field"><label>No. HP</label><input class="input" v-model="form.nasabah_phone" placeholder="08xx…" /></div>
          <div class="field"><label>Alamat lengkap <span class="req">*</span></label><input class="input" v-model="form.alamat" placeholder="Alamat calon nasabah" required /></div>
          <div class="field" style="grid-column:1/-1;"><label>Catatan</label><textarea class="textarea" v-model="form.notes" rows="2"></textarea></div>
        </div>
        <div class="row">
          <button class="btn btn-primary" :disabled="saving">{{ saving ? '⏳ Menyimpan…' : '📤 Simpan Appointment' }}</button>
          <span v-if="msg" :class="msg.startsWith('✅') ? 'alert-success' : msg.startsWith('❌') ? 'alert-error' : 'alert-info'" class="alert" style="margin:0;padding:8px 12px;">{{ msg }}</span>
        </div>
      </form>
    </div>

    <div v-if="loading" class="empty">⏳ Memuat…</div>
    <div v-else-if="err" class="alert alert-error">{{ err }}</div>
    <template v-else>
      <div class="stat-grid" style="margin-bottom:16px;">
        <StatCard icon="📅" label="Total Hari Ini" :value="stats?.total ?? list.length" color="#2563eb" />
        <StatCard icon="🌅" label="Sesi 1" :value="stats?.sesi1 ?? 0" color="#d97706" />
        <StatCard icon="🌆" label="Sesi 2" :value="stats?.sesi2 ?? 0" color="#7c3aed" />
        <StatCard icon="✅" label="Selesai" :value="stats?.completed ?? 0" color="#059669" />
      </div>

      <div class="card">
        <div class="table-wrap">
          <table class="tbl">
            <thead><tr><th>Nasabah</th><th>Marketing</th><th>HP</th><th>Sesi</th><th>Area</th><th>Status</th></tr></thead>
            <tbody>
              <tr v-for="a in list" :key="a.id">
                <td><b>{{ a.nasabah_name }}</b><div class="muted" style="font-size:11px;">{{ a.display_id }}</div></td>
                <td>{{ a.marketing_member }}</td>
                <td>{{ a.nasabah_phone || '—' }}</td>
                <td>{{ a.sesi === '2' ? '🌆 14.30' : '🌅 08.30' }}</td>
                <td>{{ a.area }}</td>
                <td><span class="badge" :class="(STATUS[a.status] || STATUS.scheduled)[1]">{{ (STATUS[a.status] || STATUS.scheduled)[0] }}</span></td>
              </tr>
              <tr v-if="!list.length"><td colspan="6" class="empty">Belum ada appointment hari ini.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
