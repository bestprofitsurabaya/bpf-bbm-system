import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import UsersView from './UsersView.vue'

const { apiMock } = vi.hoisted(() => ({ apiMock: vi.fn() }))
vi.mock('../api', () => ({ api: apiMock }))

const USERS = [
  { id: 1, username: 'ga1', full_name: 'GA Satu', role: 'ga', team_name: '', is_active: true, last_login: null },
  { id: 2, username: 'fin1', full_name: 'FIN Satu', role: 'finance', team_name: '', is_active: false, last_login: '2026-08-10' },
]

async function mountView() {
  apiMock.mockImplementation((path) => {
    if (path === '/api/users') return Promise.resolve(USERS)
    return Promise.resolve({ status: 'success', msg: 'saved' })
  })
  const w = mount(UsersView)
  await flushPromises()
  return w
}

describe('UsersView', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.stubGlobal('confirm', vi.fn(() => true))
  })
  afterEach(() => { vi.unstubAllGlobals() })

  it('menampilkan daftar user dengan role & status', async () => {
    const w = await mountView()
    expect(w.text()).toContain('ga1')
    expect(w.text()).toContain('GA Officer')
    expect(w.text()).toContain('fin1')
    expect(w.text()).toContain('Nonaktif')
  })

  it('toggle aktif TIDAK mengirim field pin (PIN user dipertahankan)', async () => {
    const w = await mountView()
    await w.findAll('button').find((b) => b.text() === '🚫').trigger('click')
    await flushPromises()
    expect(global.confirm).toHaveBeenCalled()
    const call = apiMock.mock.calls.find((c) => c[0] === '/api/users/sync')
    expect(call).toBeTruthy()
    const body = call[1].body
    expect(body.is_active).toBe(false)
    expect('pin' in body).toBe(false)
  })

  it('hapus user TIDAK mengirim field pin dan menonaktifkan user', async () => {
    const w = await mountView()
    await w.findAll('button').find((b) => b.text() === '🗑').trigger('click')
    await flushPromises()
    const call = apiMock.mock.calls.find((c) => c[0] === '/api/users/sync')
    expect(call[1].body.is_active).toBe(false)
    expect('pin' in call[1].body).toBe(false)
  })

  it('tambah user: simpan mengirim pin saat diisi', async () => {
    const w = await mountView()
    await w.findAll('button').find((b) => b.text().includes('Tambah User')).trigger('click')
    await flushPromises()
    const inputs = w.findAll('input')
    await inputs[0].setValue('new_user')
    await inputs[1].setValue('User Baru')
    await w.findAll('button').find((b) => b.text().includes('Simpan')).trigger('click')
    await flushPromises()
    const call = apiMock.mock.calls.find((c) => c[0] === '/api/users/sync')
    expect(call[1].body.username).toBe('new_user')
    expect(call[1].body.pin).toBe('123456')
  })
})
