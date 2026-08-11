import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import ChiefDriverDashboard from './ChiefDriverDashboard.vue'

const { apiMock } = vi.hoisted(() => ({ apiMock: vi.fn() }))
vi.mock('../../api', () => ({ api: apiMock }))

const APPS = [
  { id: 1, status: 'scheduled', nasabah_name: 'Nasabah A', alamat: 'Jl. A', sesi: '1', area: 'Surabaya Barat', marketing_member: 'M1' },
  { id: 2, status: 'scheduled', nasabah_name: 'Nasabah B', alamat: 'Jl. B', sesi: '2', area: 'Sidoarjo', marketing_member: 'M2' },
]
const DRIVERS = [{ name: 'RIVAN', is_active: true }, { name: 'BUDI', is_active: true }]

describe('ChiefDriverDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    apiMock.mockImplementation((path) => {
      if (path === '/api/appointments') {
        return Promise.resolve({ data: APPS, stats: { total: 2, scheduled: 2, assigned: 0, completed: 0, cancelled: 0 } })
      }
      if (path === '/api/drivers') return Promise.resolve(DRIVERS)
      if (path.includes('/assign')) return Promise.resolve({ status: 'success', msg: 'ok' })
      return Promise.resolve({})
    })
  })

  it('render satu select driver independen per baris (fix bug select terbagi)', async () => {
    const w = mount(ChiefDriverDashboard)
    await flushPromises()
    const selects = w.findAll('select')
    expect(selects.length).toBe(2)
    // pilih driver di baris pertama -> baris kedua tetap kosong
    await selects[0].setValue('RIVAN')
    const after = w.findAll('select')
    expect(after[0].element.value).toBe('RIVAN')
    expect(after[1].element.value).toBe('')
  })

  it('tombol Tugaskan memakai id appointment baris tersebut', async () => {
    const w = mount(ChiefDriverDashboard)
    await flushPromises()
    await w.findAll('select')[1].setValue('BUDI')
    const buttons = w.findAll('button')
    await buttons[1].trigger('click')
    await flushPromises()
    expect(apiMock).toHaveBeenCalledWith('/api/appointments/2/assign', { method: 'POST', body: { driver_name: 'BUDI' } })
  })
})
