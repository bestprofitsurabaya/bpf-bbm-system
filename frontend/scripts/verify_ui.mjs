// Verifikasi UI/UX via Chrome DevTools Protocol (puppeteer-core).
// Konek ke Chrome yang berjalan di Docker: docker run ... -p 9222:9222 zenika/alpine-chrome
import puppeteer from 'puppeteer-core'

const BASE = process.env.BASE || 'http://web:5000'
const CDP = 'http://localhost:9222'
const SHOT_DIR = '/tmp/ui_shots'
import { mkdirSync } from 'fs'
mkdirSync(SHOT_DIR, { recursive: true })

const browser = await puppeteer.connect({ browserURL: CDP, defaultViewport: { width: 1440, height: 900 } })
const page = await browser.newPage()

const errors = []
let sessionCookie = null
page.on('console', (m) => { if (m.type() === 'error') errors.push(m.text().slice(0, 160)) })
page.on('pageerror', (e) => errors.push('PAGEERROR: ' + String(e).slice(0, 160)))
page.on('response', (r) => {
  if (r.url().includes('/api/auth/login') && r.status() === 200) {
    const sc = r.headers()['set-cookie'] || ''
    const m = sc.match(/session=([^;]+)/)
    if (m) sessionCookie = m[1]
  }
})

const ok = (name, cond, extra = '') => console.log((cond ? '✅' : '❌') + ' ' + name + (cond ? '' : ' GAGAL') + (extra ? ' — ' + extra : ''))
const $ = (sel) => page.$(sel)
const text = async (sel) => page.$eval(sel, (el) => el.textContent.trim()).catch(() => '')

// ---------- 1. Halaman login ----------
await page.goto(BASE + '/app/login', { waitUntil: 'domcontentloaded' })
await page.waitForSelector('.login-card', { timeout: 15000 })
ok('Login page dimuat', await $('.login-card'))
await page.screenshot({ path: SHOT_DIR + '/01-login.png' })

// Toggle lihat PIN
await page.click('.pin-eye')
const pinType = await page.$eval('#login-pin', (el) => el.type)
ok('Toggle lihat PIN mengubah type ke text', pinType === 'text', pinType)

// ---------- 2. Login sebagai admin ----------
await page.waitForSelector('input[autocomplete="username"]', { timeout: 15000 })
await page.type('input[autocomplete="username"]', 'admin')
await page.type('#login-pin', '123456')
await page.click('form button.btn-primary')
const t0 = Date.now()
while (!sessionCookie && Date.now() - t0 < 12000) await new Promise((r) => setTimeout(r, 200))
// Akses verifikasi via HTTP — set cookie sesi manual via CDP (produksi pakai HTTPS + Secure cookie)
const cdp = await page.createCDPSession()
await cdp.send('Network.setCookie', {
  name: 'session', value: sessionCookie, url: 'http://web:5000',
  path: '/', httpOnly: true, secure: false, sameSite: 'Lax',
})
await page.goto(BASE + '/app/dashboard', { waitUntil: 'domcontentloaded' })
await page.waitForSelector('.side-nav a', { timeout: 15000 })
await new Promise((r) => setTimeout(r, 2000))
ok('Login admin → /app/dashboard', (await page.url()).includes('/app/dashboard'), await page.url())
await page.screenshot({ path: SHOT_DIR + '/02-dashboard.png' })

// Menu sidebar tampil
ok('Menu sidebar tampil', await $('.side-nav a'))

// ---------- 3. Mode gelap ----------
await page.click('.topbar .btn-icon[title="Mode gelap"]')
await new Promise((r) => setTimeout(r, 400))
const darkOn = await page.evaluate(() => document.documentElement.classList.contains('dark'))
ok('Mode gelap aktif (html.dark)', darkOn)
await page.screenshot({ path: SHOT_DIR + '/03-dark.png' })

// ---------- 4. Mode kontras tinggi ----------
await page.click('.topbar .btn-icon[title="Mode kontras tinggi"]')
await new Promise((r) => setTimeout(r, 400))
const hcOn = await page.evaluate(() => document.documentElement.classList.contains('hc'))
ok('Mode kontras tinggi aktif (html.hc)', hcOn)
const borderW = await page.evaluate(() => getComputedStyle(document.querySelector('.card')).borderTopWidth)
ok('Border kartu menebal di HC (≥2px)', parseFloat(borderW) >= 2, borderW)
await page.screenshot({ path: SHOT_DIR + '/04-high-contrast.png' })

// Balikkan ke mode normal (light) utk cek selanjutnya
await page.click('.topbar .btn-icon[title="Mode kontras normal"]')
await page.click('.topbar .btn-icon[title="Mode terang"]')
await new Promise((r) => setTimeout(r, 300))

// ---------- 5. Fokus keyboard terlihat (WCAG 2.4.7) ----------
await page.keyboard.press('Tab')
await new Promise((r) => setTimeout(r, 200))
const focusInfo = await page.evaluate(() => {
  const el = document.activeElement
  if (!el) return null
  const cs = getComputedStyle(el)
  return { tag: el.tagName, outline: cs.outlineStyle + ' ' + cs.outlineWidth, cls: el.className }
})
ok('Fokus keyboard: elemen aktif punya outline', focusInfo && focusInfo.outline.includes('solid'), JSON.stringify(focusInfo))

// ---------- 6. Bell notifikasi: buka + tutup dengan Esc ----------
await page.click('.topbar .bell-wrap .btn-icon')
await new Promise((r) => setTimeout(r, 300))
ok('Bell panel terbuka', await $('.bell-panel'))
const expanded = await page.$eval('.topbar .bell-wrap .btn-icon', (el) => el.getAttribute('aria-expanded'))
ok('Bell punya aria-expanded=true', expanded === 'true', expanded)
await page.keyboard.press('Escape')
await new Promise((r) => setTimeout(r, 300))
ok('Bell tertutup dengan Esc', !(await $('.bell-panel')))

// ---------- 7. Halaman Finance (rekap air minum) ----------
await page.evaluate(() => { localStorage.removeItem('bpf_hc'); localStorage.removeItem('bpf_dark') })
await page.goto(BASE + '/app/finance', { waitUntil: 'domcontentloaded' })
await page.waitForSelector('.page', { timeout: 15000 }).catch(() => {})
await new Promise((r) => setTimeout(r, 2000))
const finText = await text('.page')
ok('Dashboard Finance tampil', finText.includes('Dashboard Finance'))
await page.screenshot({ path: SHOT_DIR + '/05-finance.png' })

// ---------- 8. Halaman Air Minum (OB) ----------
await page.goto(BASE + '/app/water', { waitUntil: 'domcontentloaded' })
await page.waitForSelector('.card', { timeout: 15000 }).catch(() => {})
await new Promise((r) => setTimeout(r, 2000))
ok('Halaman Air Minum tampil (admin)', await $('.card'))
await page.screenshot({ path: SHOT_DIR + '/06-water.png' })

console.log('\n=== ERROR CONSOLE ===')
console.log(errors.length ? errors.join('\n') : '(tidak ada error console)')

await browser.disconnect()
process.exit(errors.length ? 1 : 0)
