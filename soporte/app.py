"""
Sistema de Soporte Técnico — TechNova Solutions
Dominio 4: Tickets de soporte con asignación y seguimiento
"""

import os
import time
import mysql.connector
from flask import Flask, request, jsonify

app = Flask(__name__)

# ── Conexión a BD desde variables de entorno ──────────────────────────────────
def get_db():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "admin"),
        password=os.environ.get("DB_PASSWORD", "password"),
        database=os.environ.get("DB_NAME", "soporte_db"),
    )

HTML = """
<!DOCTYPE html>
<html>
<head><title>Sistema de Soporte Técnico</title></head>
<body>
<h1>🛠️ Sistema de Soporte Técnico</h1>

<h2>Abrir Ticket</h2>
<form method="POST" action="/tickets">
  Cliente: <input name="cliente"><br><br>
  Título: <input name="titulo"><br><br>
  Descripción: <input name="descripcion"><br><br>
  Prioridad:
  <select name="prioridad">
    <option>alta</option><option>media</option><option>baja</option>
  </select><br><br>
  <input type="submit" value="Abrir Ticket">
</form>

<h2>Asignar Ticket a Técnico</h2>
<form method="POST" action="/tickets/asignar">
  ID Ticket: <input name="ticket_id"><br><br>
  Técnico: <input name="tecnico"><br><br>
  <input type="submit" value="Asignar">
</form>

<h2>Actualizar Estado</h2>
<form method="POST" action="/tickets/estado">
  ID Ticket: <input name="ticket_id"><br><br>
  Estado:
  <select name="estado">
    <option>abierto</option><option>en_progreso</option><option>resuelto</option>
  </select><br><br>
  <input type="submit" value="Actualizar">
</form>

<br><a href="/tickets/abiertos">Ver tickets abiertos por prioridad</a>
</body></html>
"""

@app.route("/")
def index():
    return HTML

@app.route("/tickets", methods=["POST"])
def abrir_ticket():
    data = request.get_json(silent=True) or request.form
    cliente     = data.get("cliente")
    titulo      = data.get("titulo")
    descripcion = data.get("descripcion")
    prioridad   = data.get("prioridad", "media")

    if not cliente or not titulo:
        return jsonify({"error": "cliente y titulo son requeridos"}), 400

    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tickets (cliente, titulo, descripcion, prioridad) VALUES (%s, %s, %s, %s)",
            (cliente, titulo, descripcion, prioridad)
        )
        conn.commit()
        ticket_id = cursor.lastrowid
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    # Tarea pesada: notificar al área técnica
    print(f"[Soporte] Notificando al área técnica sobre ticket #{ticket_id}...")
    time.sleep(5)
    print(f"[Soporte] Área técnica notificada.")

    return jsonify({
        "mensaje":   "Ticket abierto y área técnica notificada.",
        "ticket_id": ticket_id,
        "cliente":   cliente,
        "titulo":    titulo,
        "prioridad": prioridad
    }), 201

@app.route("/tickets", methods=["GET"])
def get_tickets():
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM tickets ORDER BY creado_en DESC")
        tickets = cursor.fetchall()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    for t in tickets:
        t["creado_en"] = str(t["creado_en"])
    return jsonify(tickets), 200

@app.route("/tickets/abiertos", methods=["GET"])
def tickets_abiertos():
    try:
        conn   = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT t.*, a.tecnico
            FROM tickets t
            LEFT JOIN asignaciones a ON t.id = a.ticket_id
            WHERE t.estado = 'abierto'
            ORDER BY FIELD(t.prioridad, 'alta', 'media', 'baja')
        """)
        tickets = cursor.fetchall()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
    for t in tickets:
        t["creado_en"] = str(t["creado_en"])
    return jsonify(tickets), 200

@app.route("/tickets/asignar", methods=["POST"])
def asignar_ticket():
    data      = request.get_json(silent=True) or request.form
    ticket_id = data.get("ticket_id")
    tecnico   = data.get("tecnico")

    if not ticket_id or not tecnico:
        return jsonify({"error": "ticket_id y tecnico son requeridos"}), 400

    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO asignaciones (ticket_id, tecnico) VALUES (%s, %s)",
            (ticket_id, tecnico)
        )
        cursor.execute(
            "UPDATE tickets SET estado = 'en_progreso' WHERE id = %s", (ticket_id,)
        )
        conn.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    return jsonify({"mensaje": "Ticket asignado.", "ticket_id": ticket_id, "tecnico": tecnico}), 200

@app.route("/tickets/estado", methods=["POST"])
def actualizar_estado():
    data      = request.get_json(silent=True) or request.form
    ticket_id = data.get("ticket_id")
    estado    = data.get("estado")

    if not ticket_id or estado not in ["abierto", "en_progreso", "resuelto"]:
        return jsonify({"error": "estado invalido"}), 400

    try:
        conn   = get_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE tickets SET estado = %s WHERE id = %s", (estado, ticket_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Ticket no encontrado"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

    return jsonify({"mensaje": "Estado actualizado.", "ticket_id": ticket_id, "estado": estado}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
