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

# funcion para redirigir al usuario a la página de inicio después de iniciar sesión correctamente

@app.route('/inicio')
def inicio_usuario():
    return render_template('inicio.html')



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
        return redirect(url_for('inicio_usuario'))
    else:
        print(" Datos incorrectos")
        return render_template('principal.html', error="Usuario o contraseña incorrectos")

if __name__ == '__main__':
    app.run(debug=True)