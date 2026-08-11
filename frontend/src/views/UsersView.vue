<script setup>
import { onMounted, ref } from 'vue'
import { api } from '../api'
import Modal from '../components/Modal.vue'

const users = ref([])
const loading = ref(true)
const err = ref('')
const showForm = ref(false)
const form = ref({ username: '', full_name: '', role: 'ga', pin: '123456', team_name: '', is_active: true })
const reset = ref(null)
const busy = ref(false)

const ROLES = [
  ['admin', '🛡️ Admin'], ['ga', '🧾 GA Officer'], ['finance', '💰 Finance'],
  ['marketing', '📣 Marketing'], ['chief_driver', '🚛 Chief Driver'],
]
const roleLabel = (r) => (ROLES.find((x) => x[0] === r) || [r, r])[1]

async function load() {
  loading.value = true; err.value = ''
  try { users.value = await api('/api/users') || [] }
  catch (e) { err.value = e.message }
  finally { loading.value = false }
}

function openForm(u) {
  form.value = u ? { username: u.username, full_name: u.full_name, role: u.role, pin: '', team_name: u.team_name || '', is_active: !!u.is_active } : { username: '', full_name: '', role: 'ga', pin: '123456', team_name: '', is_active: true }
  showForm.value = true
}

async function save() {
  busy.value = true
  try {
    const body = { ...form.value }
    if (!body.pin) delete body.pin
    await api('/api/users/sync', { method: 'POST', body })
    showForm.value = false; load()
  } catch (e) { alert('❌ ' + e.message) }
  finally { busy.value = false }
}

async function resetPin() {
  busy.value = true
  try {
    await api('/api/users/reset-pin', { method: 'POST', body: { username: reset.value.username, pin: reset.value.pin } })
    reset.value = null; load()
  } catch (e) { alert('❌ ' + e.message) }
  finally { busy.value = false }
}

async function toggleUser(u) {
  const action = u.is_active ? 'nonaktifkan' : 'aktifkan'
  if (!confirm(`Yakin ${action} user ${u.username}?`)) return
  busy.value = true
  try {
    await api('/api/users/sync', { method: 'POST', body: { username: u.username, full_name: u.full_name, role: u.role, is_active: !u.is_active, team_name: u.team_name || '' } })
    load()
  } catch (e) { alert('❌ ' + e.message) }
  finally { busy.value = false }
}

async function deleteUser(u) {
  if (!confirm(`HAPUS user ${u.username}?`)) return
  busy.value = true
  try {
    await api('/api/users/sync', { method: 'POST', body: { username: u.username, full_name: u.full_name, role: u.role, is_active: false, team_name: u.team_name || '' } })
    load()
  } catch (e) { alert('❌ ' + e.message) }
  finally { busy.value = false }
}

onMounted(load)
</script>

<template>
  <div>
    <div class="card card-pad" style="margin-bottom:16px;display:flex;align-items:center;">
      <div class="grow"><h3 style="margin:0;">👥 Manajemen User</h3><p class="muted" style="font-size:11px;">Khusus Admin — pengelolaan akun &amp; hak akses per peran (ISO/IEC 27001 · A.8.2)</p></div>
      <button class="btn btn-primary" @click="openForm(null)">➕ Tambah User</button>
    </div>

    <div v-if="loading" class="empty">⏳ Memuat…</div>
    <div v-else-if="err" class="alert alert-error">{{ err }}</div>
    <div class="card" v-else>
      <div class="table-wrap">
        <table class="tbl">
          <thead><tr><th>Username</th><th>Nama</th><th>Role</th><th>Tim</th><th>Status</th><th>Terakhir Login</th><th></th></tr></thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td><b>{{ u.username }}</b></td>
              <td>{{ u.full_name }}</td>
              <td><span class="badge badge-purple">{{ roleLabel(u.role) }}</span></td>
              <td>{{ u.team_name || '—' }}</td>
              <td><span class="badge" :class="u.is_active ? 'badge-green' : 'badge-red'">{{ u.is_active ? 'Aktif' : 'Nonaktif' }}</span></td>
              <td class="muted">{{ u.last_login || '—' }}</td>
              <td>
                <button class="btn btn-sm" :disabled="busy" @click="openForm(u)" title="Edit">✏️</button>
                <button class="btn btn-sm" :disabled="busy" @click="toggleUser(u)" :title="u.is_active ? 'Nonaktifkan' : 'Aktifkan'">{{ u.is_active ? '🚫' : '🟢' }}</button>
                <button class="btn btn-sm btn-danger" :disabled="busy" @click="deleteUser(u)" title="Hapus">🗑</button>
                <button class="btn btn-sm" :disabled="busy" @click="reset = { username: u.username, pin: '' }" title="Reset PIN">🔑</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <Modal v-if="showForm" :title="form.username ? '✏️ Edit User' : '➕ Tambah User'" @close="showForm = false">
      <div class="form-grid">
        <div class="field"><label>Username *</label><input class="input" v-model="form.username" required /></div>
        <div class="field"><label>Nama Lengkap *</label><input class="input" v-model="form.full_name" required /></div>
        <div class="field"><label>Role *</label>
          <select class="select" v-model="form.role"><option v-for="r in ROLES" :key="r[0]" :value="r[0]">{{ r[1] }}</option></select>
        </div>
        <div class="field"><label>PIN {{ form.username && !form.pin ? '(kosong = tidak diubah)' : '' }}</label><input class="input" v-model="form.pin" maxlength="6" inputmode="numeric" /></div>
        <div class="field"><label>Tim Marketing (role marketing)</label><input class="input" v-model="form.team_name" placeholder="mis. Tim Yusie" /></div>
        <div class="field"><label>Status</label>
          <select class="select" v-model="form.is_active"><option :value="true">Aktif</option><option :value="false">Nonaktif</option></select>
        </div>
      </div>
      <div class="row" style="justify-content:flex-end;margin-top:12px;">
        <button class="btn" @click="showForm = false">Batal</button>
        <button class="btn btn-primary" :disabled="busy" @click="save">💾 Simpan</button>
      </div>
    </Modal>

    <Modal v-if="reset" title="🔑 Reset PIN" @close="reset = null">
      <p class="muted" style="font-size:12px;margin-bottom:10px;">User: <b style="color:var(--text);">{{ reset.username }}</b></p>
      <div class="field"><label>PIN baru (6 digit)</label><input class="input" v-model="reset.pin" maxlength="6" inputmode="numeric" /></div>
      <div class="row" style="justify-content:flex-end;margin-top:12px;">
        <button class="btn" @click="reset = null">Batal</button>
        <button class="btn btn-primary" :disabled="busy || reset.pin.length !== 6" @click="resetPin">🔑 Reset</button>
      </div>
    </Modal>
  </div>
</template>
