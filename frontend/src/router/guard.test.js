import { describe, it, expect } from 'vitest'

// Logika guard diekstrak dari router untuk unit-test murni (ISO 9001: proses teruji).
export function guardResult({ toMeta, isAuth, role, toName }) {
  if (toMeta?.public) {
    if (toName === 'login' && isAuth) return 'home'
    return true
  }
  if (!isAuth) return 'login'
  const roles = toMeta?.roles
  if (roles && !roles.includes(role)) return 'forbidden'
  return true
}

describe('Route guard per role', () => {
  it('user belum login diarahkan ke /login', () => {
    const r = guardResult({ toMeta: { roles: ['admin'] }, isAuth: false, role: null, toName: 'users' })
    expect(r).toBe('login')
  })

  it('marketing tidak bisa membuka halaman Users (khusus admin)', () => {
    const r = guardResult({ toMeta: { roles: ['admin'] }, isAuth: true, role: 'marketing', toName: 'users' })
    expect(r).toBe('forbidden')
  })

  it('ga bisa membuka dashboard admin/ga/finance', () => {
    const r = guardResult({ toMeta: { roles: ['admin', 'ga', 'finance'] }, isAuth: true, role: 'ga', toName: 'dashboard' })
    expect(r).toBe(true)
  })

  it('marketing hanya bisa membuka halaman marketing', () => {
    expect(guardResult({ toMeta: { roles: ['marketing'] }, isAuth: true, role: 'marketing', toName: 'marketing' })).toBe(true)
    expect(guardResult({ toMeta: { roles: ['admin'] }, isAuth: true, role: 'marketing', toName: 'users' })).toBe('forbidden')
  })

  it('halaman publik selalu terbuka', () => {
    expect(guardResult({ toMeta: { public: true }, isAuth: false, role: null, toName: 'login' })).toBe(true)
    expect(guardResult({ toMeta: { public: true }, isAuth: false, role: null, toName: 'forbidden' })).toBe(true)
  })

  it('role yang sudah login dibuka halaman login diarahkan ke home role-nya', () => {
    expect(guardResult({ toMeta: { public: true }, isAuth: true, role: 'chief_driver', toName: 'login' })).toBe('home')
  })

  it('driver hanya bisa membuka /app/driver (PWA) — tidak bisa masuk back-office', () => {
    expect(guardResult({ toMeta: { roles: ['driver'] }, isAuth: true, role: 'driver', toName: 'driver' })).toBe(true)
    expect(guardResult({ toMeta: { roles: ['admin', 'ga', 'finance'] }, isAuth: true, role: 'driver', toName: 'dashboard' })).toBe('forbidden')
    expect(guardResult({ toMeta: { roles: ['driver'] }, isAuth: true, role: 'ga', toName: 'driver' })).toBe('forbidden')
  })
})
