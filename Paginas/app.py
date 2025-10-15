from flask import Flask, render_template_string, request, redirect, url_for, session, flash
import re

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Necesaria para sesiones

# Simulación de base de datos 
usuarios = {}

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

plantilla_principal = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <title>Página principal</title>
    <style>
        body { font-family: Arial, sans-serif; background: #f2e7df; color: white; text-align: center; }
        .container { background: #c96148; padding: 30px; border-radius: 15px; width: 400px; margin: auto; margin-top: 100px; }
        button { background: #802d20; color: white; border: none; padding: 10px; width: 100%; margin-top: 10px; border-radius: 8px; cursor: pointer; }
        button:hover { background: #dca791; }
        .success { background: #51cf66; color: white; padding: 10px; border-radius: 5px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Bienvenido, {{ nombre }} </h1>
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="success">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="post" action="{{ url_for('logout') }}">
            <button type="submit">Cerrar sesión</button>
        </form>
    </div>
</body>
</html>
"""

# RUTAS
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        if correo in usuarios and usuarios[correo]["contrasena"] == contrasena:
            session["usuario"] = usuarios[correo]["nombre"]
            session["correo"] = correo
            flash("¡Inicio de sesión exitoso!")
            return redirect(url_for("principal"))
        else:
            flash("Correo o contraseña incorrectos.")
    return render_template_string(plantilla_login)

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        correo = request.form["correo"]
        contrasena = request.form["contrasena"]

        # Validar que el correo no exista
        if correo in usuarios:
            flash("Ese correo ya está registrado.")
            return render_template_string(plantilla_registro)
        
        # Validar contraseña
        es_valida, mensaje = validar_contrasena(contrasena)
        if not es_valida:
            flash(mensaje)
            return render_template_string(plantilla_registro)
        
        # Guardar usuario
        usuarios[correo] = {
            "nombre": nombre, 
            "contrasena": contrasena
        }
        flash("Registro exitoso. Ahora inicia sesión.")
        return redirect(url_for("login"))
    
    return render_template_string(plantilla_registro)

@app.route("/principal")
def principal():
    if "usuario" in session:
        return render_template_string(plantilla_principal, nombre=session["usuario"])
    return redirect(url_for("login"))

@app.route("/logout", methods=["POST"])
def logout():
    session.pop("usuario", None)
    session.pop("correo", None)
    flash("Has cerrado sesión correctamente.")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)