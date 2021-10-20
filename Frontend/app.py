from flask import Flask, render_template, redirect, url_for, request, flash, session
import os
from forms import Login, Registro, AgregarAvion, AgregarUsuario, AgregarPilotos, AgregarVuelo
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash
from db import seleccion, accion
from utils import login_valido, pass_valido, email_valido

app = Flask(__name__)

app.secret_key = os.urandom(24)


@app.errorhandler(404)
def e404(e):
    return render_template('404.html'), 404


@app.route('/')
@app.route('/index/')
@app.route('/home/')
def index():
    return render_template("home.html")


@app.route('/search_results')
def search():
    return render_template("search_results.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = Login()
    if request.method == 'GET':
        return render_template("login.html", title='Iniciar sesion', form=form)
    else:
        usuario = escape(form.usuario.data.strip())
        clave = escape(form.clave.data.strip())
        # Preparar la consulta
        sql = f'SELECT id, nombres, correo, password, tipo_usuario FROM usuarios WHERE usuario="{usuario}"'
        # Ejecutar la consulta
        res = seleccion(sql)
        if len(res) == 0:
            flash('ERROR: Usuario o clave invalidas')
            return render_template('login.html', form=form, titulo='Iniciar Sesión')
        else:
            # Recupero el valor de la clave
            cbd = res[0][3]
            if check_password_hash(cbd, clave):
                session.clear()
                session['id'] = res[0][0]
                session['nombre'] = res[0][1]
                session['usuario'] = usuario
                #session['clave'] = clave
                session['email'] = res[0][2]
                session['tipo_usuario'] = res[0][4]

                # c == clientes
                # a == admin
                # p == piloto

                if res[0][4] == 'c':
                    return redirect(url_for('mis_reservas'))
                elif res[0][4] == 'a':
                    return redirect(url_for('dashboard_home'))
                elif res[0][4] == 'p':
                    return redirect(url_for('usuario_piloto'))
                else:
                    return redirect(url_for('home'))
            else:
                flash('ERROR: Usuario o clave invalidas')
                return render_template('login.html', form=form, titulo='Iniciar Sesión')

    return render_template("login.html", title='Iniciar sesion', form=form)


@app.route('/plantilla')
def plantilla():
    return render_template("plantilla.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@app.route('/dashboard_child')
def dashboard_child():
    return render_template("dashboard_child.html", pagina='dashboard')


@app.route('/dashboard_vuelos', methods=['POST', 'GET'])
def dashboard_vuelos():
    sql = f'SELECT id_vuelo, c_destino, c_salida, cant_pasajeros , cupos_disp, modelo ||" "|| matricula AS avion, nombres || " " || apellidos AS piloto, salida FROM vuelos AS v INNER JOIN aviones AS a ON v.avion = id_avion INNER JOIN empleados AS e ON v.piloto = e.id_emp INNER JOIN usuarios AS u ON u.id = e.id_emp'
    res = seleccion(sql)
    if len(res) == 0:
        flash('ERROR: No hay vuelos en la tabla')
    else:
        form = AgregarVuelo()
        sql2 = f'SELECT id_avion, modelo || " " || matricula AS avion FROM aviones'
        aviones = seleccion(sql2)
        print (aviones)
        if len(aviones) == 0:
            flash('ERROR: No hay aviones en la tabla')
        else:
            form.avion.choices = [(a[0], a[1]) for a in aviones]

        sql2 = f'SELECT id, Nombres || " " || Apellidos AS piloto FROM empleados AS em INNER JOIN usuarios AS us ON em.id_emp = us.id'
        pilotos = seleccion(sql2)
        if len(aviones) == 0:
            flash('ERROR: No hay pilotos en la tabla')
        else:
            form.piloto.choices = [(p[0], p[1]) for p in pilotos]

        if request.method == 'POST':
            id = escape(request.form['id'])
            origen = escape(request.form['origen'])
            destino = escape(request.form['destino'])
            cupos = escape(request.form['cupos'])
            avion = request.form.get('avion')
            piloto = request.form.get('piloto')
            fechaSalida = escape(request.form['fechaSalida'])            
            swerror = False
            if id == None or len(id) == 0:
                flash('ERROR: Debe suministrar un id')
                swerror = True
            if origen == None or len(origen) == 0:
                flash('ERROR: Debe suministrar una ciudad origen')
                swerror = True
            if destino == None or len(destino) == 0:
                flash('ERROR: Debe suministrar una ciudad destino')
                swerror = True
            if fechaSalida == None or len(fechaSalida) == 0:
                flash('ERROR: Debe suministrar una fecha de salida')
                swerror = True
            if cupos == None or len(cupos) == 0:
                flash('ERROR: Debe suministrar un número de cupos')
                swerror = True
            if not swerror:
                # Preparar el query -- Paramétrico
                sql2 = "INSERT INTO vuelos(id_vuelo, c_destino, c_salida, avion, piloto, salida, cupos_disp ) VALUES(?, ?, ?, ?, ?, ?, ?)"
                # Ejecutar la consulta
                res2 = accion(sql2, (id, destino, origen, avion, piloto, fechaSalida, cupos))
                # Proceso los resultados
                if res2 == 0:
                    flash('ERROR: No se pudieron almacenar los datos, reintente')
                else:
                    flash('INFO: Los datos fueron almacenados satisfactoriamente')
                    return redirect(url_for('dashboard_vuelos'))
        return render_template("dashboard_vuelos.html", pagina='dashboard', vuelos=res, form=form)


@app.route('/dashboard_aviones', methods=['POST', 'GET'])
def dashboard_aviones():
    sql = f'SELECT id_avion, modelo, matricula, cant_pasajeros FROM aviones'
    res = seleccion(sql)
    if len(res) == 0:
        flash('ERROR: No hay aviones en la tabla')
    else:
        #return render_template("dashboard_aviones.html", pagina='dashboard', aviones=res)
        form = AgregarAvion()
        if request.method == 'POST':
            id = escape(request.form['id'])
            modelo = escape(request.form['modelo'])
            matricula = escape(request.form['matricula'])
            cantidad = escape(request.form['cantidad'])
            swerror = False
            if id == None or len(id) == 0:
                flash('ERROR: Debe suministrar un id')
                swerror = True
            if modelo == None or len(modelo) == 0:
                flash('ERROR: Debe suministrar un modelo')
                swerror = True
            if matricula == None or len(matricula) == 0:
                flash('ERROR: Debe suministrar una matrícula')
                swerror = True
            if cantidad == None or len(cantidad) == 0:
                flash('ERROR: Debe suministrar una cantidad de pasajeros')
                swerror = True
            if not swerror:
                # Preparar el query -- Paramétrico
                sql = "INSERT INTO aviones(id_avion, modelo, matricula, cant_pasajeros) VALUES(?, ?, ?, ?)"
                # Ejecutar la consulta
                res = accion(sql, (id, modelo, matricula, cantidad))
                # Proceso los resultados
                if res == 0:
                    flash('ERROR: No se pudieron almacenar los datos, reintente')
                else:
                    flash('INFO: Los datos fueron almacenados satisfactoriamente')
                    return redirect(url_for('dashboard_aviones'))
        return render_template("dashboard_aviones.html", pagina='dashboard', aviones=res, form=form)


@app.route('/dashboard_usuarios', methods=['POST', 'GET'])
def dashboard_usuarios():
    sql = f'SELECT id, nombres, apellidos, usuario, correo, password, numero, tipo_usuario FROM usuarios'
    res = seleccion(sql)
    if len(res) == 0:
        flash('ERROR: No hay usuarios en la tabla')
    else:
        #return render_template('dashboard_usuarios.html', pagina='dashboard', usuarios=res)
        form = AgregarUsuario()
        if request.method == 'POST':
            id = escape(request.form['id'])
            nombres = escape(request.form['nombres'])
            apellidos = escape(request.form['apellidos'])
            usuario = escape(request.form['usuario'])
            email = escape(request.form['email'])
            clave = escape(request.form['clave'])
            numero = escape(request.form['numero'])
            tipoUsuario = request.form.get('tipoUsuario')
            swerror = False
            if nombres == None or len(nombres) == 0:
                flash('ERROR: Debe suministrar un nombre')
                swerror = True
            if apellidos == None or len(apellidos) == 0:
                flash('ERROR: Debe suministrar un apellido')
                swerror = True
            if usuario == None or len(usuario) == 0 or not login_valido(usuario):
                flash('ERROR: Debe suministrar un usuario válido ')
                swerror = True
            if email == None or len(email) == 0 or not email_valido(email):
                flash('ERROR: Debe suministrar un email válido')
                swerror = True
            if clave == None or len(clave) == 0 or not pass_valido(clave):
                flash('ERROR: Debe suministrar una clave válida')
                swerror = True
            if numero == None or len(numero) == 0:
                flash('ERROR: Debe suministrar un número de teléfono')
                swerror = True
            if not swerror:
                if id == None or len(id) == 0:
                    sql = "INSERT INTO usuarios( Nombres, Apellidos, usuario, correo, numero, password, tipo_usuario) VALUES(?, ?, ?, ?, ?, ?, ?)"
                    pwd = generate_password_hash(clave)
                    res = accion(sql, (nombres, apellidos, usuario, email, numero, pwd, tipoUsuario))
                else:
                    # Preparar el query -- Paramétrico
                    sql = "INSERT INTO usuarios(id, Nombres, Apellidos, usuario, correo, numero, password, tipo_usuario) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
                    pwd = generate_password_hash(clave)
                    # Ejecutar la consulta
                    res = accion(sql, (id, nombres, apellidos, usuario, email,  numero, pwd, tipoUsuario))
                    # Proceso los resultados
                if res == 0:
                    flash('ERROR: No se pudieron almacenar los datos, reintente')
                else:
                    flash('INFO: Los datos fueron almacenados satisfactoriamente')
                    return redirect(url_for('dashboard_usuarios'))
        return render_template('dashboard_usuarios.html', pagina='dashboard', usuarios=res, form = form)


@app.route('/dashboard_pilotos', methods=['POST', 'GET'])
def dashboard_pilotos():
    sql = f"SELECT id, nombres, apellidos, usuario, correo, numero, password, direccion, estado, fecha_ingreso, t_contrato FROM usuarios AS us INNER JOIN empleados AS em ON us.id = em.id_emp AND us.tipo_usuario = 'p'"
    res = seleccion(sql)
    if len(res) == 0:
        flash('ERROR: No hay pilotos en la tabla')
    else:
        #return render_template('dashboard_pilotos.html', pagina='dashboard', pilotos=res)
        form = AgregarPilotos()
        if request.method == 'POST':
            id = escape(request.form['id'])
            nombres = escape(request.form['nombres'])
            apellidos = escape(request.form['apellidos'])
            usuario = escape(request.form['usuario'])
            email = escape(request.form['email'])
            clave = escape(request.form['clave'])
            numero = escape(request.form['numero'])
            direccion = escape(request.form['direccion'])
            fechaIngreso = escape(request.form['fechaIngreso'])
            tiempoC = request.form['tiempoC']
            estado = request.form.get('estado')
            tipoUsuario = 'p'
            swerror = False
            if nombres == None or len(nombres) == 0:
                flash('ERROR: Debe suministrar un nombre')
                swerror = True
            if apellidos == None or len(apellidos) == 0:
                flash('ERROR: Debe suministrar un apellido')
                swerror = True
            if usuario == None or len(usuario) == 0 or not login_valido(usuario):
                flash('ERROR: Debe suministrar un usuario válido ')
                swerror = True
            if email == None or len(email) == 0 or not email_valido(email):
                flash('ERROR: Debe suministrar un email válido')
                swerror = True
            if clave == None or len(clave) == 0 or not pass_valido(clave):
                flash('ERROR: Debe suministrar una clave válida')
                swerror = True
            if numero == None or len(numero) == 0:
                flash('ERROR: Debe suministrar un número de teléfono')
                swerror = True
            if direccion == None or len(direccion) == 0:
                flash('ERROR: Debe suministrar una dirección')
                swerror = True
            if fechaIngreso == None or len(fechaIngreso) == 0:
                flash('ERROR: Debe suministrar la fecha de Ingreso del piloto')
                swerror = True
            if tiempoC == None or len(tiempoC) == 0:
                flash('ERROR: Debe suministrar el tiempo de contratación (meses)')
                swerror = True
            if not swerror:                
                # Preparar el query -- Paramétrico
                sql = "INSERT INTO usuarios(id, Nombres, Apellidos, usuario, correo, numero, password, tipo_usuario) VALUES(?, ?, ?, ?, ?, ?, ?, ?)"
                pwd = generate_password_hash(clave)
                # Ejecutar la consulta
                res = accion(sql, (id, nombres, apellidos, usuario, email,  numero, pwd, tipoUsuario))
                # Proceso los resultados
                sql2 = "INSERT INTO empleados(id_emp, direccion, estado, fecha_ingreso, t_contrato) VALUES(?, ?, ?, ?, ?)"
                res2 = accion(sql2, (id, direccion, estado, fechaIngreso, tiempoC))
                if res == 0 or res2 == 0:
                    flash('ERROR: No se pudieron almacenar los datos, reintente')
                else:
                    flash('INFO: Los datos fueron almacenados satisfactoriamente')
                    return redirect(url_for('dashboard_pilotos'))
        return render_template('dashboard_pilotos.html', pagina='dashboard', pilotos=res, form = form)



@app.route('/usuario_piloto')
def usuario_piloto():
    return render_template("usuario_piloto.html", pagina='piloto')


@app.route('/perfil_piloto')
def perfil_piloto():
    return render_template("perfil_piloto.html", pagina='piloto')


@app.route('/mis_reservas')
def mis_reservas():
    user_id = session['id']
    query_origen_destino = f'SELECT  tiquetes.id, vuelos.c_salida, vuelos.c_destino, vuelos.salida, aviones.modelo, usuarios.nombres, usuarios.apellidos, tiquetes.precio, tiquetes.estado FROM tiquetes INNER JOIN vuelos ON tiquetes.vuelo=vuelos.id_vuelo INNER JOIN aviones on vuelos.avion = aviones.id_avion INNER JOIN usuarios on vuelos.piloto = usuarios.id WHERE tiquetes.usuario = {user_id}'
    tiquetes = seleccion(query_origen_destino)

    if len(tiquetes) == 0:
        flash('ERROR: obteniendo informacion del tiquete')

    return render_template("mis_reservas.html", pagina='mis_reservas', tiquetes=tiquetes)


@app.route('/dashboard_home')
def dashboard_home():
    return render_template('dashboard_home.html', pagina='dashboard')


@app.route('/opiniones')
def opiniones():
    return render_template('opiniones.html')


@app.route('/precio')
def precio():
    return render_template('precio.html')


@app.route('/vuelo')
def vuelo():
    return render_template('vuelo.html')


@app.route('/registrarse', methods=['POST', 'GET'])
def registrarse():
    form = Registro()
    if request.method == 'GET':
        return render_template("registrarse.html", title='Registrarse', form=form)
    else:

        nombre = escape(request.form['nombre'])
        apellido = escape(request.form['apellido'])
        numero = escape(request.form['numero'])
        usuario = escape(request.form['usuario'])
        email = escape(request.form['email'])
        numero = escape(request.form['numero'])
        clave = escape(request.form['clave'])
        verificacion_clave = escape(request.form['verificacion_clave'])
        swerror = False
        if nombre == None or len(nombre) == 0:
            flash('ERROR: Debe suministrar un nombre')
            swerror = True
        if apellido == None or len(apellido) == 0:
            flash('ERROR: Debe suministrar un apellido')
            swerror = True
        if usuario == None or len(usuario) == 0 or not login_valido(usuario):
            flash('ERROR: Debe suministrar un usuario válido ')
            swerror = True
        if email == None or len(email) == 0 or not email_valido(email):
            flash('ERROR: Debe suministrar un email válido')
            swerror = True
        if clave == None or len(clave) == 0 or not pass_valido(clave):
            flash('ERROR: Debe suministrar una clave válida')
            swerror = True
        if verificacion_clave == None or len(verificacion_clave) == 0 or not pass_valido(verificacion_clave):
            flash('ERROR: Debe suministrar una verificación de clave válida')
            swerror = True
        if clave != verificacion_clave:
            flash('ERROR: La clave y la verificación no coinciden')
            swerror = True
        if not swerror:
            # Preparar el query -- Paramétrico
            sql = "INSERT INTO usuarios(nombres, apellidos, usuario, correo, numero, password) VALUES(?, ?, ?, ?, ?, ?)"
            # Ejecutar la consulta
            pwd = generate_password_hash(clave)
            res = accion(sql, (nombre, apellido, usuario, email, numero, pwd))
            # Proceso los resultados
            if res == 0:
                flash('ERROR: No se pudieron almacenar los datos, reintente')
            else:
                flash('INFO: Los datos fueron almacenados satisfactoriamente')
                return redirect(url_for('login'))
    return render_template("registrarse.html", title='Registrarse', form=form)


@app.route('/reservar_tiquete', methods=['POST', 'GET'])
def reservar_tiquete():
    return render_template('reservar_tiquete.html', pagina='usuario')


if __name__ == '__main__':
    app.run(debug=True)
    #app.run(debug=True, port=443, ssl_context=('cp15c.pem', 'cp15k.pem'))
