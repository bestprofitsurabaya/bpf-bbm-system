"""Settings Routes"""
from flask import (render_template, request, redirect, url_for, flash)
from modules.config import get_db_connection
from modules.helpers import log_activity_async

def register_settings_routes(app):
    
    @app.route('/admin/settings', methods=['GET', 'POST'])
    def admin_settings():
        if request.method == 'POST':
            try:
                conn = get_db_connection()
                if not conn:
                    flash('DB error!', 'error')
                    return redirect(url_for('admin_settings'))
                cursor = conn.cursor()
                # Vehicles
                for i, vid in enumerate(request.form.getlist('vehicle_id[]')):
                    if vid:
                        active = 1 if str(i) in request.form.getlist('vehicle_active[]') else 0
                        cursor.execute("UPDATE vehicles SET vehicle_type=%s, brand=%s, fuel_capacity=%s, is_active=%s WHERE id=%s",
                            (request.form.getlist('vehicle_name[]')[i], request.form.getlist('vehicle_brand[]')[i],
                             request.form.getlist('vehicle_capacity[]')[i], active, vid))
                for i, nv in enumerate(request.form.getlist('new_vehicle_name[]')):
                    if nv:
                        nb = request.form.getlist('new_vehicle_brand[]')[i] if i<len(request.form.getlist('new_vehicle_brand[]')) else 'Toyota'
                        nc = request.form.getlist('new_vehicle_capacity[]')[i] if i<len(request.form.getlist('new_vehicle_capacity[]')) else 45
                        cursor.execute("INSERT INTO vehicles (vehicle_type, brand, fuel_capacity, is_active) VALUES (%s,%s,%s,1)", (nv, nb, nc))
                # BBM Types
                for i, bid in enumerate(request.form.getlist('bbm_id[]')):
                    if bid:
                        active = 1 if str(i) in request.form.getlist('bbm_active[]') else 0
                        cursor.execute("UPDATE bbm_types SET name=%s, price_per_liter=%s, is_active=%s WHERE id=%s",
                            (request.form.getlist('bbm_name[]')[i], request.form.getlist('bbm_price[]')[i], active, bid))
                for i, nb in enumerate(request.form.getlist('new_bbm_name[]')):
                    if nb and request.form.getlist('new_bbm_price[]')[i]:
                        cursor.execute("INSERT INTO bbm_types (name, price_per_liter, is_active) VALUES (%s,%s,1)",
                            (nb, request.form.getlist('new_bbm_price[]')[i]))
                # Limits
                for i, lid in enumerate(request.form.getlist('limit_id[]')):
                    if lid:
                        is_def = 1 if str(i) in request.form.getlist('limit_default[]') else 0
                        cursor.execute("UPDATE vehicle_bbm_allowed SET good_km_per_liter=%s, warning_km_per_liter=%s, min_km_per_liter=%s, max_km_per_liter=%s, is_default=%s WHERE id=%s",
                            (request.form.getlist('limit_good[]')[i], request.form.getlist('limit_warning[]')[i],
                             request.form.getlist('limit_min[]')[i], request.form.getlist('limit_max[]')[i], is_def, lid))
                # Multifill threshold
                multifill_km = request.form.get('multifill_km_threshold', '40').strip()
                cursor.execute("INSERT INTO system_config (config_key, config_value) VALUES ('multifill_km_threshold',%s) ON DUPLICATE KEY UPDATE config_value=VALUES(config_value)", (multifill_km,))
                conn.commit()
                cursor.close(); conn.close()
                log_activity_async(0, 'settings_save', 'admin', 'Admin', new_data={'multifill_km': multifill_km}, ip=request.remote_addr)
                flash(f'Settings diperbarui!', 'success')
                return redirect(url_for('admin_settings'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'error')
        try:
            conn = get_db_connection()
            if not conn: return "DB error", 500
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM vehicles ORDER BY vehicle_type"); vehicles = cursor.fetchall()
            cursor.execute("SELECT * FROM bbm_types ORDER BY name"); bbm_types = cursor.fetchall()
            cursor.execute("SELECT vba.*, bt.price_per_liter FROM vehicle_bbm_allowed vba JOIN bbm_types bt ON vba.bbm_type=bt.name ORDER BY vba.vehicle_type, vba.bbm_type"); limits = cursor.fetchall()
            cursor.execute("SELECT config_value FROM system_config WHERE config_key='multifill_km_threshold'"); row = cursor.fetchone()
            multifill_threshold = row['config_value'] if row else '40'
            cursor.close(); conn.close()
            return render_template('settings.html', vehicles=vehicles, bbm_types=bbm_types, vehicle_limits=limits, multifill_threshold=multifill_threshold)
        except Exception as e:
            return f"Error: {str(e)}", 500
