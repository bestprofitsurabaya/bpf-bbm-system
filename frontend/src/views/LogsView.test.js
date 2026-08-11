import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import LogsView from './LogsView.vue'

const { apiMock } = vi.hoisted(() => ({ apiMock: vi.fn() }))
vi.mock('../api', () => ({ api: apiMock }))

const now = new Date()
const LOGS = [
  { id: 1, action: 'approve_ga', user_type: 'ga', user_name: 'GA1', created_at: now.toISOString(), transaction_id: 1, ip_address: '1.1.1.1' },
  { id: 2, action: 'payout', user_type: 'finance', user_name: 'FIN1', created_at: new Date(now.getTime() - 864e5).toISOString(), transaction_id: 2, ip_address: '2.2.2.2' },
  { id: 3, action: 'approve_ga', user_type: 'ga', user_name: 'GA2', created_at: now.toISOString(), transaction_id: 3, ip_address: '3.3.3.3' },
]

describe('LogsView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.mockResolvedValue(LOGS)
  })

  it('merender seluruh log + badge hari ini & total', async () => {
    const w = mount(LogsView)
    await flushPromises()
    expect(w.text()).toContain('GA1')
    expect(w.text()).toContain('FIN1')
    expect(w.text()).toContain('Approve Ga') // label aksi dibersihkan
    expect(w.text()).toContain('Hari ini: 2')
    expect(w.text()).toContain('Total: 3 / 3')
  })

  it('filter aksi menyaring baris dan memperbarui badge total', async () => {
    const w = mount(LogsView)
    await flushPromises()
    const select = w.find('select')
    await select.setValue('approve_ga')
    expect(w.findAll('tbody tr').length).toBe(2)
    expect(w.text()).toContain('Total: 2 / 3')
  })

  it('filter peran menyaring baris', async () => {
    const w = mount(LogsView)
    await flushPromises()
    const selects = w.findAll('select')
    await selects[1].setValue('finance')
    expect(w.findAll('tbody tr').length).toBe(1)
    expect(w.text()).toContain('FIN1')
  })

  it('menampilkan pesan kosong saat tidak ada log', async () => {
    apiMock.mockResolvedValue([])
    const w = mount(LogsView)
    await flushPromises()
    expect(w.text()).toContain('Tidak ada data dengan filter ini.')
  })
})
