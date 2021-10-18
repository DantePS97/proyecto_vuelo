from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/index/')
@app.route('/home/')
def index():
    return render_template("home.html")


@app.route('/search_results')
def search():
    return render_template("search_results.html")


@app.route('/login', methods=['POST', 'GET'])
@app.route('/login/', methods=['POST', 'GET'])
def login():
    return render_template("login.html")


@app.route('/plantilla')
def plantilla():
    return render_template("plantilla.html")


@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")


@app.route('/dashboard_child')
def dashboard_child():
    return render_template("dashboard_child.html")


@app.route('/dashboard_vuelos')
def dashboard_vuelo():
    return render_template("dashboard_vuelos.html")


@app.route('/dashboard_aviones')
def dashboard_aviones():
    return render_template("dashboard_aviones.html")


@app.route('/dashboard_usuarios')
def dashboard_usuarios():
    return render_template("dashboard_usuarios.html")


@app.route('/dashboard_pilotos')
def dashboard_pilotos():
    return render_template("dashboard_pilotos.html")


@app.route('/usuario_piloto')
def usuario_piloto():
    return render_template("usuario_piloto.html")


@app.route('/perfil_piloto')
def perfil_piloto():
    return render_template("perfil_piloto.html")


@app.route('/mis_reservas')
def mis_reservas():
    return render_template("mis_reservas.html")


@app.route('/dashboard_home')
def dashboard_home():
    return render_template('dashboard_home.html')


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
    return render_template('registrarse.html')


@app.route('/reservar_tiquete', methods=['POST', 'GET'])
def reservar_tiquete():
    return render_template('reservar_tiquete.html')


if __name__ == '__main__':
    app.run(debug=True)
<<<<<<< Updated upstream
=======
    # port=443 , ssl_context=('c_vuelo.pem','k_vuelo.pem'))
>>>>>>> Stashed changes
