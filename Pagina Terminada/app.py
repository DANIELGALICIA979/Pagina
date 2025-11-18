from flask import Flask, render_template, render_template_string, request, redirect, url_for, session, flash
import re
import mysql.connector
import bcrypt
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "clave_secreta"  # Necesaria para sesiones

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = mysql.connector.connect(
    host="localhost",
    user="root",         # ← cambia si tu usuario no es root
    password="202233759",  # ← pon aquí tu contraseña de MySQL
    database="paginaweb"
)
cursor = db.cursor(dictionary=True)

def validar_contrasena(contrasena):
    """
    Valida que la contraseña cumpla con los requisitos:
    - Longitud entre 8 y 15 caracteres
    - Al menos una mayúscula
    - Al menos una minúscula
    - Al menos un número
    """
    if len(contrasena) < 8 or len(contrasena) > 15:
        return False, "La contraseña debe tener entre 8 y 15 caracteres"
    
    if not re.search(r'[A-Z]', contrasena):
        return False, "La contraseña debe contener al menos una mayúscula"
    
    if not re.search(r'[a-z]', contrasena):
        return False, "La contraseña debe contener al menos una minúscula"
    
    if not re.search(r'[0-9]', contrasena):
        return False, "La contraseña debe contener al menos un número"
    
    return True, "Contraseña válida"

plantilla_login = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Login</title>
    <style>
        body { font-family: Arial, sans-serif; background: #802d20; color: white; text-align: center; }
        .container { background: #d7a773; padding: 30px; border-radius: 15px; width: 300px; margin: auto; margin-top: 100px; }
        input { padding: 10px; width: 90%; margin: 5px 0; border: none; border-radius: 8px; }
        button { background: #c96148; color: white; border: none; padding: 10px; width: 100%; margin-top: 10px; border-radius: 8px; cursor: pointer; }
        button:hover { background: #dca791; }
        a { color: #c96148; text-decoration: none; }
        .alert { background: #ff6b6b; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .success { background: #51cf66; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .password-requirements { text-align: left; background: #f8f9fa; color: #333; padding: 10px; border-radius: 5px; margin: 10px 0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Iniciar sesión</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="post">
            <input type="email" name="correo" placeholder="Correo" required><br>
            <input type="password" name="contrasena" placeholder="Contraseña" required><br>
            <button type="submit">Ingresar</button>
        </form>
        <p>¿No tienes cuenta? <a href="{{ url_for('registro') }}">Regístrate aquí</a></p>
    </div>
</body>
</html>
"""

plantilla_registro = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Registro</title>
    <style>
        body { font-family: Arial, sans-serif; background: #c96148; color: white; text-align: center; }
        .container { background: #802d20; padding: 30px; border-radius: 15px; width: 300px; margin: auto; margin-top: 100px; }
        input { padding: 10px; width: 90%; margin: 5px 0; border: none; border-radius: 8px; }
        button { background: #d7a773; color: white; border: none; padding: 10px; width: 100%; margin-top: 10px; border-radius: 8px; cursor: pointer; }
        button:hover { background: #dca791; }
        a { color: #d7a773; text-decoration: none; }
        .alert { background: #ff6b6b; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .success { background: #51cf66; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
        .password-requirements { text-align: left; background: #f8f9fa; color: #333; padding: 10px; border-radius: 5px; margin: 10px 0; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Crear cuenta</h2>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="password-requirements">
            <strong>Requisitos de contraseña:</strong>
            <ul>
                <li>Entre 8 y 15 caracteres</li>
                <li>Al menos una mayúscula</li>
                <li>Al menos una minúscula</li>
                <li>Al menos un número</li>
            </ul>
        </div>
        
        <form method="post">
            <input type="text" name="nombre" placeholder="Nombre Completo" required><br>
            <input type="email" name="correo" placeholder="Correo" required><br>
            <input type="password" name="contrasena" placeholder="Contraseña" required><br>
            <button type="submit">Registrar</button>
        </form>
        <p>¿Ya tienes cuenta? <a href="{{ url_for('login') }}">Inicia sesión</a></p>
    </div>
</body>
</html>
"""


# RUTAS
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    #session.pop('_flashes', None)
    if request.method == "POST":
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        cursor.execute("SELECT * FROM usuarios WHERE correo =%s", (correo,))
        usuario = cursor.fetchone()

        if usuario and bcrypt.checkpw(contrasena.encode('utf-8'), usuario["contrasena"].encode('utf-8')):
            session["usuario"] = usuario["nombre"]
            session["correo"] = usuario["correo"]
            session["id_usuario"] = usuario["id"]
            flash("¡Inicio de sesión exitoso!")
            return redirect(url_for("estado"))
        else:
            flash("Correo o constraseña incorrectos")
    return render_template_string(plantilla_login)


@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        # Validar que el correo no exista
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        existente = cursor.fetchone()
        if existente:
            flash("Ese correo ya está registrado.")
            return render_template_string(plantilla_registro)

        es_valida, mensaje = validar_contrasena(contrasena)
        if not es_valida:
            flash(mensaje)
            return render_template_string(plantilla_registro)

        hash_contra = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO usuarios (nombre, correo, contrasena) VALUES (%s, %s, %s)", 
                       (nombre, correo, hash_contra.decode('utf-8')))
        db.commit()

        flash("Registro exitoso. Ahora inicia sesión.")
        return redirect(url_for("login"))
    return render_template_string(plantilla_registro)

@app.route("/principal")
def principal():
    if "usuario" in session:
        return render_template("index.html", nombre=session["usuario"])
    return redirect(url_for("login"))

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for("login"))


##################################################################

# === Formulario de evaluación ===
@app.route("/evaluacion", methods=["GET", "POST"])
def evaluacion():
    error_curp = None  # ← mensaje de error para CURP duplicado

    if request.method == "POST":

        #  Validar sesión
        usuario_id = session.get("id_usuario")
        if not usuario_id:
            return redirect(url_for("login"))

        # Datos del formulario
        datos = {
            "curp": request.form.get("curp"),
            "edad": request.form.get("edad"),
            "genero": request.form.get("genero"),
            "estado_civil": request.form.get("estado_civil"),
            "educacion": request.form.get("educacion"),
            "ocupacion": request.form.get("ocupacion"),
            "empleo": request.form.get("empleo"),
            "ingresos": request.form.get("ingresos"),
            "integrantes": request.form.get("integrantes"),
            "dependientes": request.form.get("dependientes"),
            "vivienda": request.form.get("vivienda"),
            "zona": request.form.get("zona"),
            "servicios": request.form.get("servicios"),
            "discapacidad": request.form.get("discapacidad"),
            "telefono": request.form.get("telefono"),
            "direccion": request.form.get("direccion"),
            "motivo": request.form.get("motivo"),
        }

        # Archivos subidos
        ine_file = request.files.get("ine")
        comprobante_file = request.files.get("comprobante")

        ine_path = None
        comprobante_path = None

        if ine_file and ine_file.filename != "":
            ine_filename = secure_filename(ine_file.filename)
            ine_path = os.path.join(app.config['UPLOAD_FOLDER'], ine_filename)

        if comprobante_file and comprobante_file.filename != "":
            comp_filename = secure_filename(comprobante_file.filename)
            comprobante_path = os.path.join(app.config['UPLOAD_FOLDER'], comp_filename)

        # Intentar guardar la evaluación
        try:
            query = """
                INSERT INTO formularios (
                    usuario_id, curp, edad, genero, estado_civil, nivel_educativo, ocupacion,
                    ingresos_mensuales, integrantes_hogar, tipo_vivienda, zona, servicios_basicos,
                    situacion_salud, dependientes_economicos, telefono, direccion, motivo_solicitud, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'En revisión')
            """

            cursor.execute(query, (
                usuario_id, datos["curp"], datos["edad"], datos["genero"], datos["estado_civil"],
                datos["educacion"], datos["ocupacion"], datos["ingresos"], datos["integrantes"],
                datos["vivienda"], datos["zona"], datos["servicios"], datos["discapacidad"],
                datos["dependientes"], datos["telefono"], datos["direccion"], datos["motivo"]
            ))
            db.commit()

        except mysql.connector.IntegrityError as err:
            # Codigo: entrada duplicada
            if err.errno == 1062:
                error_curp = "Este CURP ya está registrado."
                return render_template("evaluacion.html", error_curp=error_curp, datos=datos)
            else:
                raise

        # Guardar archivos si el insert fue exitoso
        if ine_path:
            ine_file.save(ine_path)
        if comprobante_path:
            comprobante_file.save(comprobante_path)

        # Guardar rutas de documentos
        cursor.execute("""
            INSERT INTO documentos (usuario_id, ine_path, comprobante_domicilio_path)
            VALUES (%s, %s, %s)
        """, (usuario_id, ine_path, comprobante_path))
        db.commit()

        return redirect(url_for("resultado"))

    return render_template("evaluacion.html", error_curp=error_curp)

# === Página de resultado ===
@app.route("/resultado")
def resultado():
    return render_template("resultado.html")

@app.route("/estado")
def estado():
    usuario_id = session.get("id_usuario")
    if not usuario_id:
        return redirect(url_for("login"))

    # Ver si el usuario ya envió el formulario
    cursor.execute("SELECT status FROM formularios WHERE usuario_id = %s", (usuario_id,))
    resultado = cursor.fetchone()

    # Si NO tiene formulario → mandarlo a evaluacion
    if not resultado:
        return redirect(url_for("evaluacion"))

    status = resultado["status"]

    # Redirigir según status
    if status == "En revisión":
        return render_template("estado_revision.html")

    elif status == "Aprobado":
        return render_template("estado_aprobado.html")

    elif status == "Denegado":
        return render_template("estado_denegado.html")

    else:
        return "Error: Estado desconocido."


##################################################################

if __name__ == "__main__":
    app.run(debug=True)
