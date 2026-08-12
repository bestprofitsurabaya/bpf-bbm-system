/**
 * Mesin watermark foto (port dari static/js/driver.js).
 * Bar hitam di bawah foto berisi: nama perusahaan, tanggal & jam, lokasi GPS.
 * Return Blob JPEG yang siap dikirim sebagai file.
 */
export async function applyWatermark(file, gpsText, dateText = null) {
  if (!file || !file.type.startsWith('image/')) return null
  try {
    const now = dateText || new Date().toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' })
    const timeText = now
    const url = URL.createObjectURL(file)
    const img = await new Promise((resolve, reject) => {
      const i = new Image()
      i.onload = () => resolve(i)
      i.onerror = reject
      i.src = url
    })

    const canvas = document.createElement('canvas')
    const ctx = canvas.getContext('2d')
    canvas.width = img.width
    canvas.height = img.height
    ctx.drawImage(img, 0, 0)

    const fontSize = Math.max(16, Math.floor(canvas.width / 35))
    const padding = 20
    const lineH = fontSize * 1.5
    const barH = lineH * 3 + padding * 2

    ctx.fillStyle = 'rgba(0,0,0,0.6)'
    ctx.fillRect(0, canvas.height - barH, canvas.width, barH)

    ctx.fillStyle = '#FFD700'
    ctx.font = `bold ${fontSize}px Inter, Arial`
    ctx.fillText('PT BESTPROFIT FUTURES SBY', padding, canvas.height - barH + lineH)

    ctx.fillStyle = '#FFFFFF'
    ctx.font = `${fontSize * 0.8}px Inter, Arial`
    ctx.fillText(`📅 ${timeText}`, padding, canvas.height - barH + lineH * 2)
    ctx.fillText(`📍 ${gpsText}`, padding, canvas.height - barH + lineH * 3)

    URL.revokeObjectURL(url)
    return await new Promise((resolve) => {
      canvas.toBlob((blob) => resolve(blob), 'image/jpeg', 0.85)
    })
  } catch {
    return null
  }
}

/** Baca file jadi dataURL untuk preview. */
export function fileToDataUrl(file) {
  return new Promise((resolve, reject) => {
    const r = new FileReader()
    r.onload = (e) => resolve(e.target.result)
    r.onerror = reject
    r.readAsDataURL(file)
  })
}
