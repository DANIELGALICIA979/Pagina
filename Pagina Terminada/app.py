from flask import Flask, render_template, request, redirect, url_for, session, flash
import re
import mysql.connector
import bcrypt
import os
from werkzeug.utils import secure_filename
from functools import wraps


app = Flask(__name__)
app.secret_key = "clave_secreta"  # Necesaria para sesiones

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


db = mysql.connector.connect(
    host="localhost",
    user="root",         # ← cambia si tu usuario no es root
    password="xd",  # ← pon aquí tu contraseña de MySQL
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

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session or not session.get("es_admin"):
            flash("Acceso denegado. Se requiere cuenta de administrador.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function 

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
            session["es_admin"] = usuario.get("es_admin", False)
            
            if session["es_admin"]:
                flash("¡Bienvenido administrador!")
                return redirect(url_for("admin_panel"))
            else:
                flash("¡Inicio de sesión exitoso!")
                return redirect(url_for("estado"))
        else:
            flash("Correo o constraseña incorrectos")
    return render_template("login.html")


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
            return render_template("registro.html")

        es_valida, mensaje = validar_contrasena(contrasena)
        if not es_valida:
            flash(mensaje)
            return render_template("registro.html")

        hash_contra = bcrypt.hashpw(contrasena.encode('utf-8'), bcrypt.gensalt())
        cursor.execute("INSERT INTO usuarios (nombre, correo, contrasena) VALUES (%s, %s, %s)", 
                       (nombre, correo, hash_contra.decode('utf-8')))
        db.commit()

        flash("Registro exitoso. Ahora inicia sesión.")
        return redirect(url_for("login"))
    return render_template("registro.html")

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

#Ruta panel de administracion
@app.route("/admin")
@admin_required
def admin_panel():
    cursor.execute("""
                   SELECT f.*, u.nombre, u.correo
                   FROM formularios f
                   JOIN usuarios u ON f.usuario_id = u.id
                   WHERE f.status = 'En revisión'
                   ORDER BY f.fecha_solicitud DESC
                   """)
    solicitudes = cursor.fetchall()
    return render_template("admin_panel.html", solicitudes=solicitudes)

#Ruta para detalles de una solicitud
@app.route("/admin/solicitud/<int:solicitud_id>")
@admin_required
def ver_solicitud(solicitud_id):
    cursor.execute("""
                   SELECT f.*, u.nombre, u.correo, d.ine_path, d.comprobante_domicilio_path
                   FROM formularios f
                   JOIN usuarios u ON f.usuario_id = u.id
                   LEFT JOIN documentos d ON f.usuario_id = d.usuario_id
                   WHERE f.id = %s
                   """, (solicitud_id,))
    solicitud = cursor.fetchone()
    if not solicitud:
        flash("Solicitud no encontrada.")
        return redirect(url_for("admin_panel"))
    return render_template("detalle_solicitud.html", solicitud=solicitud) 

#Ruta para aprobar/rechazar solicitud
@app.route("/admin/decision", methods=["POST"])
@admin_required
def tomar_decision():
    solicitud_id = request.form.get("solicitud_id")
    decision = request.form.get("decision")
    comentarios = request.form.get("comentarios", "")
    
    nuevo_status = "Aprobado" if decision == "aprobar" else "Denegado"
    
    # Actualizar estado en la base de datos
    cursor.execute("""
                     UPDATE formularios
                     SET status = %s, comentarios_admin = %s
                     WHERE id = %s
                   """, (nuevo_status, comentarios, solicitud_id))
    db.commit()
    
    flash(f"Solicitud {nuevo_status.lower()} correctamente.")
    return redirect(url_for("admin_panel"))

#Ruta historial de decisiones
@app.route("/admin/historial")
@admin_required
def historial():
    cursor.execute("""
                   SELECT f.*, u.nombre, u.correo
                   FROM formularios f
                   JOIN usuarios u ON f.usuario_id = u.id
                   WHERE f.status != 'En revisión'
                   ORDER BY f.fecha_solicitud DESC
                   """)
    historial = cursor.fetchall()
    return render_template("historial_admin.html", historial=historial)


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
