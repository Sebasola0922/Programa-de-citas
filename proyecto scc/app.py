# ==============================
# 📦 IMPORTACIONES
# ==============================
from flask import Flask, render_template, request, redirect, session, jsonify
import mysql.connector

# ==============================
# 🚀 CONFIGURACIÓN INICIAL
# ==============================
app = Flask(__name__)
app.secret_key = "clave_secreta"  # 🔐 Necesaria para manejar sesiones


# ==============================
# 🔌 CONEXIÓN A LA BASE DE DATOS
# ==============================
def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="sistema_citas"
        )
    except Exception as e:
        print("❌ Error conexión:", e)
        return None


# ==============================
# 🏠 RUTA PRINCIPAL (LOGIN)
# ==============================
@app.route('/')
def inicio():
    return render_template('login.html')

@app.route('/conductor')
def conductor():
    return render_template('conductor.html')


# ==============================
# 🔐 LOGIN
# ==============================
@app.route('/login', methods=['POST'])
def login():
    conexion = None
    try:
        email = request.form['Usuario']
        password = request.form['Contraseña']

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        # 🔥 Traer también tipo de empresa
        cursor.execute("""
            SELECT u.*, e.tipo_empresa
            FROM usuario u
            JOIN empresa e ON u.id_empresa = e.id_empresa
            WHERE u.email = %s AND u.contraseña = %s
        """, (email, password))

        usuario = cursor.fetchone()

        if usuario:
            session['usuario'] = usuario

            # 👑 ADMIN
            if usuario['rol'] == 'admin':
                return redirect('/admin')

            # 🏭 EMPRESA GENERADORA
            elif usuario['tipo_empresa'] == 'Generadora':
                return redirect('/panel_generador')

            # 🚚 EMPRESA TRANSPORTADORA
            elif usuario['tipo_empresa'] == 'Transportadora':
                return redirect('/panel_transportador')

        else:
            return render_template('login.html', error="Credenciales incorrectas")

    except Exception as e:
        return str(e)

    finally:
        if conexion:
            conexion.close()

# ==============================
# 🔐 LOGOUT
# ==============================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


# ==============================
# 👑 PANEL ADMIN (PROTEGIDO)
# ==============================
@app.route('/admin')
def admin():
    # 🔒 Verificar sesión
    if 'usuario' not in session:
        return redirect('/')

    # 🔒 Verificar rol
    if session['usuario']['rol'] != 'admin':
        return "Acceso denegado", 403

    return render_template('admin.html')


# ==============================
# 👤 PANEL citas (PROTEGIDO)
# ==============================
@app.route('/panel_generador')
def panel_generador():
    if 'usuario' not in session:
        return redirect('/')

    if session['usuario']['tipo_empresa'] != 'Generadora':
        return "Acceso denegado", 403

    return render_template('citas.html')  

# ==============================
# 👤 PANEL citas (PROTEGIDO)
# ==============================
@app.route('/panel_transportador')
def panel_transportador():
    if 'usuario' not in session:
        return redirect('/')

    if session['usuario']['tipo_empresa'] != 'Transportadora':
        return "Acceso denegado", 403

    return render_template('operador.html')

# ==============================
# 🏢 LISTAR EMPRESAS
# ==============================
@app.route('/empresas', methods=['GET'])
def listar_empresas():
    conexion = None
    try:
        conexion = get_connection()
        if conexion is None:
            return jsonify({"error": "Error conexión"}), 500

        cursor = conexion.cursor(dictionary=True)

        # 🔥 Solo empresas activas
        cursor.execute("SELECT * FROM empresa WHERE estado = 'activa'")
        data = cursor.fetchall()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 👤 LISTAR USUARIOS
# ==============================
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conexion = None
    try:
        conexion = get_connection()
        if conexion is None:
            return jsonify({"error": "Error conexión"}), 500

        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_usuario, nombre, email, rol, id_empresa 
            FROM usuario
        """)

        data = cursor.fetchall()
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 🏢 CREAR EMPRESA
# ==============================
@app.route('/empresa', methods=['POST'])
def crear_empresa():
    conexion = None
    try:
        data = request.json

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.callproc('insertar_empresa', (
            data['nombre'],
            data['tipo'],
            data['direccion'],
            data['telefono'],
            data['email']
        ))

        conexion.commit()
        return jsonify({"mensaje": "Empresa creada correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 🏢 ACTUALIZAR EMPRESA
# ==============================
@app.route('/empresa/actualizar', methods=['POST'])
def actualizar_empresa():
    conexion = None
    try:
        data = request.json

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.callproc('actualizar_empresa', (
            data['id'],
            data['nombre'],
            data['tipo'],
            data['direccion'],
            data['telefono'],
            data['email']
        ))

        conexion.commit()
        return jsonify({"mensaje": "Empresa actualizada"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 🏢 DESACTIVAR EMPRESA
# ==============================
@app.route('/empresa/<int:id>', methods=['DELETE'])
def eliminar_empresa(id):
    conexion = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        # 🔥 Usa procedimiento (eliminación lógica)
        cursor.callproc('eliminar_empresa', (id,))

        conexion.commit()
        return jsonify({"mensaje": "Empresa desactivada"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 👤 CREAR USUARIO
# ==============================
@app.route('/usuario', methods=['POST'])
def crear_usuario():
    conexion = None
    try:
        data = request.json

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.callproc('insertar_usuario', (
            data['nombre'],
            data['email'],
            data['password'],
            data['rol'],
            data['id_empresa']
        ))

        conexion.commit()
        return jsonify({"mensaje": "Usuario creado"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 👤 ACTUALIZAR USUARIO
# ==============================
@app.route('/usuario/actualizar', methods=['POST'])
def actualizar_usuario():
    conexion = None
    try:
        data = request.json

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.callproc('actualizar_usuario', (
            data['id'],
            data['nombre'],
            data['email'],
            data['password'],
            data['rol'],
            data['id_empresa']
        ))

        conexion.commit()
        return jsonify({"mensaje": "Usuario actualizado"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 👤 DESACTIVAR USUARIO
# ==============================
@app.route('/usuario/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    conexion = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.callproc('eliminar_usuario', (id,))

        conexion.commit()
        return jsonify({"mensaje": "Usuario desactivado"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# ▶️ CREAR CITA
# ==============================
@app.route('/cita', methods=['POST'])
def crear_cita():
    conexion = None
    try:
        data = request.json

        id_empresa = session['usuario']['id_empresa']
        id_usuario = session['usuario']['id_usuario']

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.callproc('crear_cita', (
            data['inicio'],
            data['fin'],
            data['tipo'],
            id_empresa,
            id_usuario
        ))

        conexion.commit()
        return jsonify({"mensaje": "Cita creada"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()

# ==============================
# ▶️ VER CITAS PENDIENTES
# ==============================
@app.route('/citas_pendientes', methods=['GET'])
def citas_pendientes():
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute("""
        SELECT c.id_cita, c.fecha_hora_inicio, c.tipo_cita, e.nombre AS empresa
        FROM cita c
        JOIN empresa e ON c.id_empresa = e.id_empresa
        WHERE c.estado = 'pendiente'
    """)

    data = cursor.fetchall()
    conexion.close()

    return jsonify(data)
# ==============================
# ▶️ Obtener citas 
# ==============================
@app.route('/mis_citas_data')
def mis_citas_data():
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    id_usuario = session['usuario']['id_usuario']

    cursor.execute("""
        SELECT id_cita, fecha_hora_inicio, fecha_hora_fin, tipo_cita, estado
        FROM cita
        WHERE id_usuario_crea = %s
    """, (id_usuario,))

    data = cursor.fetchall()
    conexion.close()

    return jsonify(data)

# ==============================
# ▶️ Actualizar cita
# ==============================

@app.route('/cita/actualizar', methods=['POST'])
def actualizar_cita():
    data = request.json

    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("""
        UPDATE cita 
        SET tipo_cita = %s,
            fecha_hora_inicio = %s,
            fecha_hora_fin = %s
        WHERE id_cita = %s AND estado = 'pendiente'
    """, (data['tipo'], data['inicio'], data['fin'], data['id']))

    conexion.commit()
    conexion.close()

    return jsonify({"mensaje": "Actualizada"})

# ==============================
# ▶️ Eliminar cita
# ==============================
@app.route('/cita/<int:id>', methods=['DELETE'])
def eliminar_cita(id):
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("""
        DELETE FROM cita 
        WHERE id_cita = %s AND estado = 'pendiente'
    """, (id,))

    conexion.commit()
    conexion.close()

    return jsonify({"mensaje": "Eliminada"})

# ==============================
# ▶️ TOMAR CITA
# ==============================
@app.route('/tomar_cita', methods=['POST'])
def tomar_cita():
    conexion = None
    try:
        data = request.json

        id_usuario = session['usuario']['id_usuario']

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.callproc('tomar_cita', (
            data['id_cita'],
            id_usuario,
            data['vehiculo']
        ))

        conexion.commit()
        return jsonify({"mensaje": "Cita tomada"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()

# ==============================
# ▶️ CITA COMPLETA
# ==============================
@app.route('/mis_citas_data1')
def mis_citas_data1():
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    id_usuario = session['usuario']['id_usuario']

    cursor.execute("""
        SELECT 
            c.id_cita,
            c.fecha_hora_inicio,
            c.fecha_hora_fin,
            c.tipo_cita,
            c.estado,
            c.id_empresa,       
            v.placa,
            v.tipo AS tipo_vehiculo
        FROM cita c
        LEFT JOIN vehiculo v ON c.id_vehiculo = v.id_vehiculo
        WHERE c.id_usuario_toma = %s
    """, (id_usuario,))

    data = cursor.fetchall()
    conexion.close()

    return jsonify(data)


# ==============================
# ▶🚚 MODIFICAR VEHICULO DE LA CITA 
# ==============================
@app.route('/cita/actualizar_vehiculo', methods=['POST'])
def actualizar_vehiculo_cita():
    conexion = None
    try:
        data = request.json

        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            UPDATE cita
            SET id_vehiculo = %s,
                fecha_asignacion = NOW()
            WHERE id_cita = %s
        """, (
            data['vehiculo'],
            data['id_cita']
        ))

        conexion.commit()

        return jsonify({"mensaje": "Vehículo actualizado en la cita"})

    except Exception as e:
        return jsonify({"error": str(e)})

    finally:
        if conexion:
            conexion.close()




# ==============================
# 🚚 CREAR VEHÍCULO
# ==============================
@app.route('/vehiculo', methods=['POST'])
def crear_vehiculo():
    conexion = None
    try:
        data = request.json

        # 🔐 Obtener empresa del usuario logueado
        id_empresa = session['usuario']['id_empresa']

        conexion = get_connection()
        if conexion is None:
            return jsonify({"error": "Error de conexión"}), 500

        cursor = conexion.cursor()

        # 🔥 Llamar procedimiento almacenado
        cursor.callproc('insertar_vehiculo', (
            data['placa'],
            data['tipo'],
            data['capacidad'],
            id_empresa
        ))

        conexion.commit()

        return jsonify({"mensaje": "Vehículo creado correctamente"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 🚚 LISTAR VEHÍCULOS POR EMPRESA
# ==============================
@app.route('/vehiculos', methods=['GET'])
def listar_vehiculos():
    conexion = None
    try:
        # 🔐 Empresa del usuario logueado
        id_empresa = session['usuario']['id_empresa']

        conexion = get_connection()
        if conexion is None:
            return jsonify({"error": "Error conexión"}), 500

        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT id_vehiculo, placa, tipo, capacidad
            FROM vehiculo
            WHERE id_empresa = %s
        """, (id_empresa,))

        data = cursor.fetchall()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 🚚 ELIMINAR VEHÍCULO
# ==============================
@app.route('/vehiculo/<int:id>', methods=['DELETE'])
def eliminar_vehiculo(id):
    conexion = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        # 🔥 validar si tiene citas
        cursor.execute("""
            SELECT COUNT(*) AS total
            FROM cita
            WHERE id_vehiculo = %s
        """, (id,))

        result = cursor.fetchone()

        if result['total'] > 0:
            return jsonify({
                "error": "🚫 Este vehículo tiene citas asignadas y no se puede borrar"
            }), 400

        # 🗑 eliminar
        cursor.execute("""
            DELETE FROM vehiculo
            WHERE id_vehiculo = %s
        """, (id,))

        conexion.commit()

        return jsonify({"mensaje": "Vehículo eliminado"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()


# ==============================
# 🚚 Conductor valida citas asignadas
# ==============================

@app.route('/citas_por_placa', methods=['POST'])
def citas_por_placa():
    conexion = None
    try:
        data = request.json
        placa = data['placa']

        conexion = get_connection()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                c.id_cita,
                c.fecha_hora_inicio,
                c.fecha_hora_fin,
                c.estado,
                c.tipo_cita,
                e.nombre AS empresa,
                v.placa,
                v.tipo AS tipo_vehiculo,
                v.capacidad
            FROM cita c
            JOIN vehiculo v ON c.id_vehiculo = v.id_vehiculo
            JOIN empresa e ON c.id_empresa = e.id_empresa
            WHERE v.placa = %s
            ORDER BY c.fecha_hora_inicio DESC
        """, (placa,))

        data = cursor.fetchall()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if conexion:
            conexion.close()



# ==============================
# ▶️ INICIAR SERVIDOR
# ==============================
if __name__ == '__main__':
    print("🚀 Servidor corriendo...")
    app.run(host="0.0.0.0", port=5000, debug=False)