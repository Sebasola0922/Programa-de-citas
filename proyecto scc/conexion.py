from flask import Flask, redirect, request, render_template, url_for
import mysql.connector


app = Flask(__name__)

# conexión a MySQL validamos la conexión y mostramos un mensaje de éxito o error
try:
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   
        database="descargue"
    )

    if conexion.is_connected():
        print(" Conexión exitosa a MySQL")

except Exception as e:
    print(" Error al conectar:", e)


# creacion del flask para validar el usuario y contraseña, se llama a la función almacenada en MySQL y se muestra un mensaje de éxito o error dependiendo del resultado

@app.route('/')
def inicio():   
    return render_template('principal.html')



# recibimos los datos del formulario de inicio de sesión y los validamos con la función almacenada en MySQL, si el resultado es correcto mostramos un mensaje de éxito, de lo contrario mostramos un mensaje de error

@app.route('/login', methods=['POST'])
def login():
    usuario = request.form['Usuario']
    password = request.form['Contraseña']


    cursor = conexion.cursor(dictionary=True)

    cursor.callproc('validar_usuario', [usuario, password])

    resultado = []
    for res in cursor.stored_results():
        resultado = res.fetchall()

    if resultado:
        print(" Login correcto")
        return redirect(url_for('mostrar_registros'))
    else:
        print(" Datos incorrectos")
        return render_template('principal.html', error="Usuario o contraseña incorrectos")
    
    

# Mostramos los datos en la tabla de la página de inicio, para esto llamamos a la función almacenada en MySQL que nos devuelve los datos de los usuarios registrados y los mostramos en la tabla

@app.route('/inicio')
def mostrar_registros():
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Usuario")
    registros = cursor.fetchall()
    print(" Registros obtenidos:", registros)
    cursor.close()

    return render_template('inicio.html', registros=registros)

    
# procedimientos de eliminado actualizado y creacion


@app.route('/procesar', methods=['POST'])

def procesar():

    accion = request.form['accion']
    cedula = request.form['Cedula']

    cursor = conexion.cursor()


    if accion == 'Actualizar':
        nombre = request.form['Nombre']
        apellido = request.form['Apellido']
        cedula = request.form['Cedula']
        usuario = request.form['Usuario']
        contraseña = request.form['Contraseña']
        cursor.callproc('actualizar_usuario', [cedula,nombre, apellido,usuario, contraseña])
        conexion.commit()
        print(" Usuario actualizado")

    elif accion == "Agregar":
        nombre = request.form['Nombre']
        apellido = request.form['Apellido']
        cedula = request.form['Cedula']
        usuario = request.form['Usuario']
        contraseña = request.form['Contraseña']
        cursor.callproc('agregar', [ nombre, apellido,cedula, usuario, contraseña])

        conexion.commit()
        print(" Usuario agregado")
    

    elif accion == 'Eliminar':
        cedula = request.form['Cedula']

        cursor.callproc('eliminar_usuario', [cedula])
        conexion.commit()
        print("Usuario eliminado")

    cursor.close()

    return redirect(url_for('mostrar_registros'))



if __name__ == '__main__':
    app.run(debug=True)