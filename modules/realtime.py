"""Central SocketIO bus + per-driver rooms for real-time driver notifications."""
from flask import request

socketio = None

# Track which room each session is currently in, so a driver switching name
# doesn't keep receiving old rooms' notifications.
_sid_room = {}


def init_socketio(sio):
    """Attach the app-level SocketIO instance and register room handlers."""
    global socketio
    socketio = sio
    if sio is None:
        return
    try:
        @sio.on('join_driver')
        def _join_driver(data):
            try:
                name = str((data or {}).get('name', '')).strip().upper()
                if not name:
                    return
                sid = request.sid
                room = 'driver_' + name
                prev = _sid_room.get(sid)
                # Catatan: room management ada di python-socketio Server (sio.server),
                # bukan di wrapper flask-socketio (sio.enter_room TIDAK ADA).
                if prev and prev != room:
                    sio.server.leave_room(sid, prev)
                sio.server.enter_room(sid, room)
                _sid_room[sid] = room
                print(f"[realtime] join_driver room={room} sid={sid}")
            except Exception as e:
                print(f"[realtime] join_driver error: {e}")

        @sio.on('join_room')
        def _join_room(data):
            """Generic room join (mis. marketing_<username> untuk halaman marketing)."""
            try:
                room = str((data or {}).get('room', '')).strip()
                if not room:
                    return
                sid = request.sid
                prev = _sid_room.get(sid)
                if prev and prev != room:
                    sio.server.leave_room(sid, prev)
                sio.server.enter_room(sid, room)
                _sid_room[sid] = room
            except Exception as e:
                print(f"[realtime] join_room error: {e}")

        @sio.on('disconnect')
        def _on_disconnect():
            _sid_room.pop(request.sid, None)
    except Exception as e:
        print(f"[realtime] init error: {e}")


def emit_event(event, data, room=None):
    """Best-effort socket emit; never raises."""
    if socketio is None:
        print(f"[realtime] emit skipped (socketio not initialized): {event}")
        return
    try:
        if room:
            socketio.emit(event, data, to=room)
        else:
            socketio.emit(event, data)
    except Exception as e:
        print(f"[realtime] emit error ({event}): {e}")


def emit_driver(driver_name, data):
    """Emit an event to all devices of a specific driver."""
    if not driver_name:
        return
    emit_event('driver_notification', data, room='driver_' + str(driver_name).strip().upper())
