from flask import Flask, render_template, request, redirect, send_from_directory, session
from flaskext.mysql import MySQL
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "develoteca"
mysql=MySQL()

app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='sitio'
mysql.init_app(app)

@app.route('/')
def inicio():
    return render_template('sitio/index.html')

# mostrar la imagen
@app.route('/img/<imagen>')
def imagens(imagen):
    print(imagen)
    return send_from_directory(os.path.join('templates/sitio/img/'),imagen)

@app.route("/css/<archivocss>")
def css_link(archivocss):
    return send_from_directory(os.path.join('templates/sitio/css'),archivocss)


@app.route('/libros')
def libros():

    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros = cursor.fetchall()
    conexion.commit()
    print(libros)

    return render_template('sitio/libros.html', libros = libros)

@app.route('/nosotros')
def nosotros():
    return render_template('sitio/nosotros.html')

@app.route('/admin/')
def admin_index():
    if not 'login' in session:
        return redirect("/admin/login")
    
    return render_template ('admin/index.html')

@app.route('/admin/login')
def admin_login():
    return render_template('admin/login.html')

@app.route('/admin/login', methods=['POST'])
def admin_login_post():

    #Login

    usuario = request.form['txtUsuario']
    password = request.form['txtPassword']
    print(usuario)
    print(password)

    #verificacion de usuario

    if usuario=="admin" and password == "123":
        session["login"] = True
        session["usuario"] = "Administrador"
        return redirect("/admin")

    return render_template("admin/login.html", mensaje = "Acceso denegado")

@app.route('/admin/cerrar')
def admin_lofin_cerrar():
    session.clear()
    return redirect('/admin/login')

@app.route('/admin/libros')
def admin_libros():

    if not 'login' in session:
        return redirect("/admin/login")

    # consulta de informacion
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM `libros`")
    libros = cursor.fetchall()
    conexion.commit()
    print(libros)

    return render_template('admin/libros.html', libros = libros)

@app.route('/admin/libros/guardar', methods=['POST'])
def admin_libros_guardar():

    if not 'login' in session:
        return redirect("/admin/login")

    # insertar datos en la base de datos
    nombre = request.form['txtNombre']
    url = request.form['txtURL']
    imagen = request.files['txtImagen']

    #guardar la imagen
    tiempo = datetime.now()
    hora_actual = tiempo.strftime('%Y%H%M%S')

    if imagen.filename != "":
        nuevo_nombre = hora_actual + "_" + imagen.filename
        imagen.save("templates/sitio/img/" + nuevo_nombre) 

    sql = "INSERT INTO `libros` (`id`, `nombre`, `imagen`, `url`) VALUES (NULL, %s , %s, %s); "
    datos = (nombre, nuevo_nombre, url)

    #conexion a la base de datos
    conexion = mysql.connect()
    cursor= conexion.cursor()
    cursor.execute(sql, datos)
    conexion.commit()

    print(nombre)
    print(url)
    print(imagen)
    return redirect('/admin/libros')

@app.route('/admin/libros/borrar', methods=['POST'])
def admin_libros_borrar():

    if not 'login' in session:
        return redirect("/admin/login")

    id = request.form['txtID']


    conexion = mysql.connect()
    cursor= conexion.cursor()
    cursor.execute("SELECT imagen FROM `libros` WHERE id = %s", (id))
    libro = cursor.fetchall()
    conexion.commit()

    #Borrar de la base de datos
    sql = "DELETE FROM libros WHERE `libros`.`id` = %s" #instrucion del sql
    datos = (id) # los datos de sql(%s)

    #conexion a la base de datos
    conexion = mysql.connect()
    cursor = conexion.cursor()
    cursor.execute(sql, datos) # datos que enviamos
    conexion.commit() # ejecutamos la instrucion

    if os.path.exists("templates/sitio/img/" + str(libro[0][0])):
        os.unlink("templates/sitio/img/"+ str(libro[0][0]))

    return redirect('/admin/libros')


if __name__ == '__main__':
    app.run(debug=True)