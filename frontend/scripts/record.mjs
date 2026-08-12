// ============================================================
// REKAM VIDEO WALKTHROUGH PER PERAN — screenshot berkala (andal)
// Ambil serangkaian screenshot saat berinteraksi, lalu gabung
// dengan efek zoom (Ken Burns) via scripts/make_videos.sh
//
// Jalankan:  node scripts/record.mjs [role1 role2 ...]
// ============================================================
import puppeteer from 'puppeteer-core'
import { mkdirSync } from 'fs'

const BASE = process.env.BASE || 'http://localhost:5001'
const CHROME = process.env.CHROME_PATH || '/home/it-ef/.local/opt/chrome/chrome-linux64/chrome'
const OUT = '/tmp/record'
mkdirSync(OUT, { recursive: true })

const ROLES = {
  admin:    { user: 'admin',           home: '/app/dashboard',    steps: [['', 2200], ['/app/analytics', 2200], ['/app/users', 2000]] },
  ob:       { user: 'ob1',             home: '/app/water',        steps: [['', 2500], ['', 1500]] },
  finance:  { user: 'finance_officer', home: '/app/finance',      steps: [['', 2500], ['/app/water', 2500]] },
  ga:       { user: 'ga_officer',      home: '/app/ga',           steps: [['', 2500], ['', 1500]] },
  marketing:{ user: 'Yusie',           home: '/app/marketing',    steps: [['', 2500], ['', 1500]] },
  chief:    { user: 'driver',          home: '/app/chief-driver', steps: [['', 2500], ['', 1500]] },
  driver:   { user: 'RIVAN',           home: '/app/driver',       steps: [['', 2500], ['', 1500], ['', 1500]] },
}
const only = process.argv.slice(2)

const browser = await puppeteer.launch({
  executablePath: CHROME, headless: 'new',
  args: ['--no-sandbox', '--disable-gpu'],
  defaultViewport: { width: 1440, height: 900 },
})

async function loginPage(user, pin, home) {
  const ctx = await browser.createBrowserContext()
  const p = await ctx.newPage()
  let sess = null
  const onResp = (r) => {
    if (r.url().includes('/api/auth/login') && r.status() === 200) {
      const m = (r.headers()['set-cookie'] || '').match(/session=([^;]+)/)
      if (m) sess = m[1]
    }
  }
  p.on('response', onResp)
  await p.goto(BASE + '/app/login', { waitUntil: 'domcontentloaded' })
  for (let i = 0; i < 3; i++) {
    try { await p.waitForSelector('#login-pin', { timeout: 12000 }); break }
    catch (e) { if (i === 2) throw e; await p.goto(BASE + '/app/login', { waitUntil: 'domcontentloaded' }) }
  }
  await p.type('input[autocomplete="username"]', user)
  await p.type('#login-pin', pin)
  await p.click('form button.btn-primary')
  const t0 = Date.now()
  while (!sess && Date.now() - t0 < 15000) await new Promise((r) => setTimeout(r, 200))
  p.off('response', onResp)
  if (!sess) throw new Error('login gagal ' + user)
  const cdp = await p.createCDPSession()
  await cdp.send('Network.setCookie', { name: 'session', value: sess, url: BASE, path: '/', httpOnly: true, secure: false, sameSite: 'Lax' })
  await p.goto(BASE + home, { waitUntil: 'domcontentloaded' })
  await new Promise((r) => setTimeout(r, 2500))
  return { p, ctx }
}

async function record(role) {
  const cfg = ROLES[role]
  const dir = `${OUT}/${role}`
  mkdirSync(dir, { recursive: true })
  console.log('🎬 merekam', role, '...')
  const { p, ctx } = await loginPage(cfg.user, '123456', cfg.home)
  let n = 0
  for (const [path, wait] of cfg.steps) {
    if (path) { await p.goto(BASE + path, { waitUntil: 'domcontentloaded' }); await new Promise((r) => setTimeout(r, 800)) }
    await p.screenshot({ path: `${dir}/s${String(++n).padStart(2, '0')}.png` })
    await new Promise((r) => setTimeout(r, wait))
    await p.screenshot({ path: `${dir}/s${String(++n).padStart(2, '0')}.png` })
  }
  console.log(`  ${role}: ${n} screenshot`)
  await ctx.close().catch(() => {})
}

for (const role of Object.keys(ROLES)) {
  if (only.length && !only.includes(role)) continue
  try { await record(role) } catch (e) { console.log('❌', role, String(e).slice(0, 100)) }
}

await browser.close()
console.log('Selesai — screenshot di', OUT)
