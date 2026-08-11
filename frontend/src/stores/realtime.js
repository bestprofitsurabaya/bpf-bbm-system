import { defineStore } from 'pinia'
import { io } from 'socket.io-client'

/**
 * Realtime store (ISO/IEC 27001 A.8 — only the events each role needs):
 * - ga/finance/admin : broadcast new_claim / new_trip_report (ops board)
 * - marketing        : join appointments_board -> appointment_update
 * - chief_driver     : join appointments_board -> appointment_update
 */
let socket = null
let toastSeq = 0

export const useRealtimeStore = defineStore('realtime', {
  state: () => ({
    connected: false,
    toasts: [], // { id, text, icon }
    items: [],  // bell history (max 30)
    unread: 0,
  }),
  actions: {
    connect(role) {
      if (socket) return
      try {
        socket = io({ reconnection: true, reconnectionAttempts: Infinity, reconnectionDelay: 1000, timeout: 10000 })
        socket.on('connect', () => {
          this.connected = true
          this.joinRooms(role)
        })
        socket.on('disconnect', () => { this.connected = false })
        socket.on('connect_error', () => { this.connected = false })

        // Broadcast klaim/trip hanya relevan untuk role operasional
        if (['ga', 'finance', 'admin'].includes(role)) {
          socket.on('new_claim', (d) => this.push(`🚛 ${d?.driver_name || 'Driver'} mengajukan klaim BBM`, 'new_claim', d))
          socket.on('new_trip_report', (d) => this.push(`🗺️ ${d?.driver_name || 'Driver'} submit laporan perjalanan`, 'new_trip_report', d))
        }

        // Appointment board (marketing / chief driver)
        if (['marketing', 'chief_driver', 'ga', 'admin'].includes(role)) {
          socket.on('appointment_update', (d) => {
            const label = d?.status
              ? `📅 Appointment ${d.display_id || ''} → ${String(d.status).replace(/_/g, ' ')}`
              : '📅 Ada pembaruan appointment'
            this.push(label, 'appointment_update', d)
          })
        }
      } catch { this.connected = false }
    },
    joinRooms(role) {
      if (!socket) return
      try {
        if (role === 'marketing' || role === 'chief_driver') {
          socket.emit('join_room', { room: 'appointments_board' })
        }
      } catch { /* noop */ }
    },
    push(text, type, data) {
      const id = ++toastSeq
      this.toasts.push({ id, text, type, data })
      this.items.unshift({ id, text, type, data, at: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) })
      if (this.items.length > 30) this.items.pop()
      this.unread++
      setTimeout(() => { this.dismissToast(id) }, 6000)
    },
    dismissToast(id) {
      this.toasts = this.toasts.filter((t) => t.id !== id)
    },
    markAllRead() { this.unread = 0 },
    disconnect() {
      if (socket) { socket.disconnect(); socket = null }
      this.connected = false
    },
  },
})
