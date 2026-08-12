/**
 * Utilitas GPS driver (port dari static/js/driver.js).
 * Prioritas alamat: nilai tersimpan → reverse geocode (Nominatim) → koordinat mentah.
 */
export const NOMINATIM = 'https://nominatim.openstreetmap.org'

async function reverseGeocode(lat, lon) {
  const r = await fetch(
    `${NOMINATIM}/reverse?lat=${lat}&lon=${lon}&format=json&zoom=18&addressdetails=1&accept-language=id`,
    { headers: { 'User-Agent': 'BPF-BBM/1.0' } }
  )
  const d = await r.json()
  if (d?.address) {
    const a = d.address
    const parts = []
    if (a.road) parts.push(a.road)
    if (a.suburb || a.village) parts.push(a.suburb || a.village)
    if (a.city || a.town) parts.push(a.city || a.town)
    if (a.state) parts.push(a.state)
    return parts.join(', ') || d.display_name || ''
  }
  return d?.display_name || ''
}

/** Alamat dari koordinat GPS (atau string koordinat bila gagal). */
export async function addressFromCoords(lat, lon) {
  try {
    const addr = await reverseGeocode(lat, lon)
    return addr || `${lat.toFixed(5)}, ${lon.toFixed(5)}`
  } catch {
    return `${lat.toFixed(5)}, ${lon.toFixed(5)}`
  }
}

/** SPBU terdekat (2 teratas) dari koordinat. Return string deskriptif atau ''. */
export async function nearbySpbu(lat, lon) {
  try {
    const r = await fetch(
      `${NOMINATIM}/search?q=SPBU&format=json&limit=3&lat=${lat}&lon=${lon}&bounded=1&addressdetails=1&accept-language=id`,
      { headers: { 'User-Agent': 'BPF-BBM/1.0' } }
    )
    const data = await r.json()
    if (Array.isArray(data) && data.length) {
      return data.slice(0, 2).map((d) => {
        const dist = d.dist ? `${Math.round(d.dist)}m` : ''
        const name = (d.display_name || '').split(',')[0].trim()
        return name + (dist ? ` (${dist})` : '')
      }).join(' | ')
    }
  } catch { /* abaikan */ }
  return ''
}

/** Ambil posisi GPS sekali (promise). */
export function getPosition(timeout = 15000) {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('GPS Tidak Didukung'))
      return
    }
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true, timeout, maximumAge: 300000,
    })
  })
}

/** Ambil posisi + alamat + SPBU terdekat sekaligus. */
export async function locateWithAddress() {
  const pos = await getPosition()
  const { latitude: lat, longitude: lon } = pos.coords
  let addr = ''
  try { addr = await addressFromCoords(lat, lon) } catch { /* fallback */ }
  let spbu = ''
  try { spbu = await nearbySpbu(lat, lon) } catch { /* fallback */ }
  return { lat, lon, addr: addr || `${lat.toFixed(5)}, ${lon.toFixed(5)}`, spbu }
}
