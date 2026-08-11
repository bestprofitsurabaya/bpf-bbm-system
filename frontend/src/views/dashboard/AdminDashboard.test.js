import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import AdminDashboard from './AdminDashboard.vue'
import { useAuthStore } from '../../stores/auth'

const { apiMock } = vi.hoisted(() => ({ apiMock: vi.fn() }))
vi.mock('../../api', () => ({ api: apiMock }))

const STATS = { pending: 3, verified_ga: 2, os_finance: 1, archived: 5, today_tx: 2, today_nominal: 100000 }

const TX = (id, status) => ({
  id, display_id: `BPF-${id}`, driver_name: `DRV${id}`, nopol: 'L 1 AB', bbm_type: 'PERTALITE',
  nominal: 150000, liter: 15, odo_km: 1000, ml_anomaly_flag: false, created_at: '2026-08-11 10:00:00', status,
})

function mockApi() {
  apiMock.mockImplementation((path, opts = {}) => {
    if (path === '/api/stats') return Promise.resolve(STATS)
    if (path === '/api/queue') {
      const tab = opts.params?.tab || 'ga'
      if (tab === 'ga') return Promise.resolve([TX(1, 'pending'), TX(2, 'pending')])
      if (tab === 'finance') return Promise.resolve([TX(3, 'verified_ga')])
      return Promise.resolve([TX(4, 'os_finance')])
    }
    return Promise.resolve({ status: 'success', msg: 'ok' })
  })
}

async function mountWith(role) {
  const pinia = createPinia()
  setActivePinia(pinia)
  const auth = useAuthStore()
  auth.user = { role, full_name: 'User ' + role, user_name: role }
  mockApi()
  const w = mount(AdminDashboard, {
    global: {
      plugins: [pinia],
      stubs: { 'router-link': { template: '<a><slot /></a>' } },
    },
  })
  await flushPromises()
  await flushPromises()
  return w
}

describe('AdminDashboard', () => {
  beforeEach(() => { vi.clearAllMocks(); vi.stubGlobal('confirm', vi.fn(() => true)); vi.stubGlobal('prompt', vi.fn(() => 'alasan uji')) })
  afterEach(() => { vi.unstubAllGlobals() })

  it('role ga melihat kartu statistik GA + antrean GA dengan tombol Approve/Tolak', async () => {
    const w = await mountWith('ga')
    expect(w.text()).toContain('Antrean GA (pending)')
    expect(w.text()).toContain('Terarsip')
    expect(w.text()).toContain('Antrean Kerja')
    expect(w.text()).toContain('BPF-1')
    expect(w.text()).toContain('✅ Approve')
    expect(w.text()).toContain('❌ Tolak')
  })

  it('role finance melihat kartu finance + tab Finance & Konfirmasi Driver (bukan GA)', async () => {
    const w = await mountWith('finance')
    expect(w.text()).toContain('Menunggu Finance (os_finance)')
    expect(w.text()).not.toContain('Antrean GA (pending)')
    expect(w.text()).toContain('💰 Finance')
    expect(w.text()).toContain('🤝 Konfirmasi Driver')
  })

  it('klik Approve memanggil /api/queue/approve-ga/<id>', async () => {
    const w = await mountWith('ga')
    const btn = w.findAll('button').find((b) => b.text().includes('Approve'))
    expect(btn).toBeTruthy()
    await btn.trigger('click')
    await flushPromises()
    expect(apiMock).toHaveBeenCalledWith('/api/queue/approve-ga/1', { method: 'POST' })
  })

  it('klik Tolak meminta alasan lalu memanggil /api/queue/reject/<id>', async () => {
    const w = await mountWith('ga')
    const btn = w.findAll('button').find((b) => b.text().includes('Tolak'))
    await btn.trigger('click')
    await flushPromises()
    expect(global.prompt).toHaveBeenCalled()
    expect(apiMock).toHaveBeenCalledWith('/api/queue/reject/1', { method: 'POST', body: { reason: 'alasan uji' } })
  })

  it('role finance: tab Finance menampilkan tombol Cairkan yang memanggil /api/queue/payout', async () => {
    const w = await mountWith('finance')
    const tabBtn = w.findAll('button').find((b) => b.text().includes('💰 Finance'))
    await tabBtn.trigger('click')
    await flushPromises()
    await flushPromises()
    expect(w.text()).toContain('BPF-3')
    const btn = w.findAll('button').find((b) => b.text().includes('Cairkan'))
    expect(btn).toBeTruthy()
    await btn.trigger('click')
    await flushPromises()
    expect(apiMock).toHaveBeenCalledWith('/api/queue/payout/3', { method: 'POST' })
  })

  it('role finance: tab Konfirmasi Driver menampilkan tombol Arsipkan yang memanggil /api/queue/archive', async () => {
    const w = await mountWith('finance')
    const tabBtn = w.findAll('button').find((b) => b.text().includes('Konfirmasi Driver'))
    await tabBtn.trigger('click')
    await flushPromises()
    await flushPromises()
    expect(w.text()).toContain('BPF-4')
    const btn = w.findAll('button').find((b) => b.text().includes('Arsipkan'))
    expect(btn).toBeTruthy()
    await btn.trigger('click')
    await flushPromises()
    expect(apiMock).toHaveBeenCalledWith('/api/queue/archive/4', { method: 'POST' })
  })

  it('transaksi ber-flag anomali ML tidak bisa di-approve cepat (wajib verifikasi klasik)', async () => {
    // Baris anomali: tanpa tombol Approve/Tolak + pesan wajib klasik
    const pinia = createPinia()
    setActivePinia(pinia)
    const auth = useAuthStore()
    auth.user = { role: 'ga', full_name: 'GA', user_name: 'ga' }
    apiMock.mockImplementation((path) => {
      if (path === '/api/stats') return Promise.resolve(STATS)
      if (path === '/api/queue') return Promise.resolve([{ ...TX(9, 'pending'), ml_anomaly_flag: true }])
      return Promise.resolve({ status: 'success', msg: 'ok' })
    })
    const w = mount(AdminDashboard, {
      global: { plugins: [pinia], stubs: { 'router-link': { template: '<a><slot /></a>' } } },
    })
    await flushPromises()
    await flushPromises()
    expect(w.text()).toContain('Wajib verifikasi klasik')
    expect(w.findAll('button').some((b) => b.text().includes('Approve'))).toBe(false)
  })
})
