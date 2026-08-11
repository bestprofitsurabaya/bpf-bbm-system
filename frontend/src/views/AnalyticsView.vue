<script setup>
import { onMounted, onBeforeUnmount, ref } from 'vue'
import { Chart, registerables } from 'chart.js'
import { api } from '../api'

Chart.register(...registerables)

const today = new Date().toISOString().slice(0, 10)
const start = ref(new Date(Date.now() - 30 * 864e5).toISOString().slice(0, 10))
const end = ref(today)
const rows = ref([])
const summary = ref(null)
const loading = ref(true)
const err = ref('')
const canvas = ref(null)
let chart = null

const fmt = (n) => 'Rp ' + Number(n || 0).toLocaleString('id-ID')

async function load() {
  loading.value = true; err.value = ''
  try {
    const d = await api('/api/analytics/data', { params: { start_date: start.value, end_date: end.value } })
    rows.value = d.data || d || []
    summary.value = d.summary || null
    drawChart(rows.value)
  } catch (e) { err.value = e.message }
  finally { loading.value = false }
}

function drawChart(data) {
  if (!canvas.value) return
  const byDay = {}
  for (const r of data || []) {
    const day = String(r.created_at || '').slice(0, 10) || 'tanpa-tanggal'
    byDay[day] = (byDay[day] || 0) + Number(r.nominal || 0)
  }
  const labels = Object.keys(byDay).sort()
  const values = labels.map((k) => byDay[k])
  if (chart) chart.destroy()
  const dark = document.documentElement.classList.contains('dark')
  chart = new Chart(canvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Nominal (Rp)',
        data: values,
        borderColor: '#2563eb',
        backgroundColor: 'rgba(37,99,235,.12)',
        fill: true,
        tension: .35,
        pointRadius: 3,
      }],
    },
    options: {
      responsive: true,
      plugins: { legend: { labels: { color: dark ? '#94a3b8' : '#475569' } } },
      scales: {
        x: { ticks: { color: dark ? '#94a3b8' : '#94a3b8', maxTicksLimit: 10 } },
        y: { ticks: { color: dark ? '#94a3b8' : '#94a3b8', callback: (v) => (v >= 1e6 ? (v / 1e6).toFixed(1) + 'jt' : v) } },
      },
    },
  })
}

onMounted(load)
onBeforeUnmount(() => { if (chart) chart.destroy() })
</script>

<template>
  <div>
    <div class="card card-pad" style="margin-bottom:16px;">
      <div class="row">
        <div class="field" style="margin:0;"><label>Dari</label><input class="input" type="date" v-model="start" /></div>
        <div class="field" style="margin:0;"><label>Sampai</label><input class="input" type="date" v-model="end" /></div>
        <button class="btn btn-primary" @click="load" style="margin-top:18px;">📈 Tampilkan</button>
      </div>
    </div>

    <div v-if="loading" class="empty">⏳ Memuat…</div>
    <div v-else-if="err" class="alert alert-error">{{ err }}</div>
    <template v-else>
      <div class="card card-pad" style="margin-bottom:16px;">
        <h3>📈 Tren Nominal</h3>
        <div style="height:260px;"><canvas ref="canvas"></canvas></div>
      </div>
      <div class="card">
        <div class="table-wrap">
          <table class="tbl">
            <thead><tr><th>ID</th><th>Driver</th><th>Nopol</th><th>BBM</th><th>Nominal</th><th>Tanggal</th></tr></thead>
            <tbody>
              <tr v-for="t in rows" :key="t.id">
                <td><b>{{ t.display_id }}</b></td><td>{{ t.driver_name }}</td><td>{{ t.nopol }}</td>
                <td>{{ t.bbm_type }}</td><td>{{ fmt(t.nominal) }}</td><td class="muted">{{ t.created_at }}</td>
              </tr>
              <tr v-if="!rows.length"><td colspan="6" class="empty">Tidak ada data pada rentang tanggal ini.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </div>
</template>
