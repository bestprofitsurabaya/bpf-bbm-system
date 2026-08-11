import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import SettingsView from './SettingsView.vue'

const { apiMock } = vi.hoisted(() => ({ apiMock: vi.fn() }))
vi.mock('../api', () => ({ api: apiMock }))

const DRIVERS = [{ name: 'RIVAN', nopol: 'L 1', vehicle_type: 'AVANZA', bbm_type: 'PERTALITE', is_active: true }]
const VEHICLES = [{ id: 1, vehicle_type: 'AVANZA', brand: 'Toyota', fuel_capacity: 45, is_active: true }]
const BBMS = [{ id: 1, name: 'PERTALITE', price_per_liter: 10000, is_active: true }]

async function mountView() {
  apiMock.mockImplementation((path) => {
    if (path === '/api/drivers') return Promise.resolve(DRIVERS)
    if (path === '/api/vehicles') return Promise.resolve(VEHICLES)
    if (path === '/api/bbm_types') return Promise.resolve(BBMS)
    return Promise.resolve({ status: 'success' })
  })
  const w = mount(SettingsView)
  await flushPromises()
  return w
}

describe('SettingsView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('confirm', vi.fn(() => true))
  })
  afterEach(() => { vi.unstubAllGlobals() })

  it('menampilkan tabel driver, kendaraan, dan tipe BBM', async () => {
    const w = await mountView()
    expect(w.text()).toContain('RIVAN')
    expect(w.text()).toContain('Toyota')
    expect(w.text()).toContain('PERTALITE')
    expect(w.text()).toContain('Aktif')
  })

  it('toggle driver memanggil endpoint activate/deactivate yang tepat', async () => {
    const w = await mountView()
    await w.findAll('button').find((b) => b.text().includes('Nonaktifkan')).trigger('click')
    await flushPromises()
    expect(apiMock).toHaveBeenCalledWith('/api/drivers/RIVAN/deactivate', { method: 'POST' })
  })

  it('modal tambah driver: simpan memanggil /api/drivers/sync dengan nama uppercase', async () => {
    const w = await mountView()
    await w.findAll('button').find((b) => b.text().includes('Tambah Driver')).trigger('click')
    await flushPromises()
    expect(w.text()).toContain('Tambah Driver')
    const inputs = w.findAll('input')
    await inputs[0].setValue('budi')
    await w.findAll('button').find((b) => b.text().includes('Simpan')).trigger('click')
    await flushPromises()
    expect(apiMock).toHaveBeenCalledWith('/api/drivers/sync', {
      method: 'POST',
      body: expect.objectContaining({ driver_name: 'BUDI' }),
    })
  })

  it('hapus driver (dengan konfirmasi) memanggil /api/drivers/<nama>/delete', async () => {
    const w = await mountView()
    await w.findAll('button').find((b) => b.text() === '🗑').trigger('click')
    await flushPromises()
    expect(global.confirm).toHaveBeenCalled()
    expect(apiMock).toHaveBeenCalledWith('/api/drivers/RIVAN/delete', { method: 'POST' })
  })

  it('tipe kendaraan pada modal tidak duplikat (AVANZA hanya sekali)', async () => {
    const w = await mountView()
    await w.findAll('button').find((b) => b.text().includes('Tambah Driver')).trigger('click')
    await flushPromises()
    const opts = w.findAll('select')[0].findAll('option').map((o) => o.text())
    expect(opts.filter((t) => t === 'AVANZA').length).toBe(1)
  })
})
