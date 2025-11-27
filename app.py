from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import database as db
from auth import User
from models import get_all_patients, get_patient_by_id, search_patients, update_patient, create_patient
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_benavides_2024'

# Configuración Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Inicializar base de datos
print("🔄 Inicializando base de datos...")
db.init_db()

# Helper para formatear nombre
def format_patient_display(patient_db):
    return {
        'id': f"P{patient_db['id_usuario']:010d}",
        'id_usuario': patient_db['id_usuario'],
        'nombre_completo': patient_db['nombre_completo'],
        'sexo': 'Femenino' if patient_db['sexo'] == 'F' else 'Masculino',
        'edad': patient_db['edad'],
        'curp': patient_db['curp'],
        'telefono': patient_db['telefono'],
        'correo': patient_db.get('correo', ''),
        'direccion': patient_db.get('direccion', ''),
        'contacto_emergencia': patient_db.get('contacto_emergencia', '')
    }

# Rutas de Autenticación
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('usuario')
    password = request.form.get('contrasena')
    
    # Para desarrollo, usar credenciales temporales
    if email and password:
        user = User.authenticate(email, password)
        if user:
            login_user(user)
            flash(f'Bienvenido Dr. {user.nombre}', 'success')
            return redirect('/dashboard')
    
    flash('Credenciales incorrectas. Usa: doctor@test.com / 123', 'error')
    return redirect('/')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# Rutas Principales
@app.route('/dashboard')
def dashboard():
    pacientes_db = get_all_patients()
    pacientes = [format_patient_display(p) for p in pacientes_db]
    return render_template('dashboard.html', pacientes=pacientes)

@app.route('/paciente/<patient_id>')
def ver_paciente(patient_id):
    # Extraer ID numérico del formato P0000000001
    id_numero = int(patient_id[1:]) if patient_id.startswith('P') else int(patient_id)
    
    paciente_db = get_patient_by_id(id_numero)
    if paciente_db:
        paciente = format_patient_display({
            'id_usuario': paciente_db['id_usuario'],
            'nombre_completo': f"{paciente_db['nombre_usuario']} {paciente_db['apellido_paterno']} {paciente_db.get('apellido_materno', '')}",
            'sexo': paciente_db['sexo'],
            'edad': paciente_db['edad'],
            'curp': paciente_db['curp'],
            'telefono': paciente_db['telefono'],
            'correo': paciente_db['correo'],
            'direccion': f"{paciente_db['calle']} {paciente_db['numero_exterior']} {paciente_db.get('numero_interior', '')}, {paciente_db['colonia']}",
            'contacto_emergencia': paciente_db['contacto_emergencia']
        })
        return render_template('ver_paciente.html', paciente=paciente)
    else:
        flash('Paciente no encontrado', 'error')
        return redirect('/dashboard')

@app.route('/editar/<patient_id>', methods=['GET', 'POST'])
def editar_paciente(patient_id):
    # Extraer ID numérico
    id_numero = int(patient_id[1:]) if patient_id.startswith('P') else int(patient_id)
    
    if request.method == 'POST':
        # Procesar actualización
        data = {
            'nombre': request.form['nombre'],
            'apellido_paterno': request.form['apellido_paterno'],
            'apellido_materno': request.form.get('apellido_materno', ''),
            'curp': request.form['curp'],
            'fecha_nacimiento': request.form['fecha_nacimiento'],
            'sexo': request.form['sexo'][0],  # Tomar solo M/F
            'calle': request.form['calle'],
            'numero_exterior': request.form['numero_exterior'],
            'colonia': request.form['colonia'],
            'codigo_postal': request.form['codigo_postal'],
            'ciudad': request.form['ciudad'],
            'telefono': request.form['telefono'],
            'correo': request.form['correo'],
            'contacto_emergencia': request.form['contacto_emergencia']
        }
        
        if update_patient(id_numero, data):
            flash('Datos del paciente actualizados correctamente', 'success')
        else:
            flash('Error al actualizar los datos', 'error')
        
        return redirect(f'/paciente/{patient_id}')
    
    # GET - Mostrar formulario
    paciente_db = get_patient_by_id(id_numero)
    if paciente_db:
        paciente = {
            'id': f"P{paciente_db['id_usuario']:010d}",
            'nombre': paciente_db['nombre_usuario'],
            'apellido_paterno': paciente_db['apellido_paterno'],
            'apellido_materno': paciente_db.get('apellido_materno', ''),
            'curp': paciente_db['curp'],
            'fecha_nacimiento': paciente_db['fecha_nacimiento'],
            'sexo': 'Femenino' if paciente_db['sexo'] == 'F' else 'Masculino',
            'calle': paciente_db['calle'] or '',
            'numero_exterior': paciente_db['numero_exterior'] or '',
            'colonia': paciente_db['colonia'] or '',
            'codigo_postal': paciente_db['codigo_postal'] or '',
            'ciudad': paciente_db['ciudad'] or '',
            'telefono': paciente_db['telefono'] or '',
            'correo': paciente_db['correo'] or '',
            'contacto_emergencia': paciente_db['contacto_emergencia'] or ''
        }
        return render_template('editar_paciente.html', paciente=paciente)
    else:
        flash('Paciente no encontrado', 'error')
        return redirect('/dashboard')

@app.route('/buscar')
def buscar_pacientes():
    query = request.args.get('q', '')
    if query:
        resultados_db = search_patients(query)
        resultados = [format_patient_display(p) for p in resultados_db]
    else:
        resultados_db = get_all_patients()
        resultados = [format_patient_display(p) for p in resultados_db]
    
    return jsonify(resultados)

@app.route('/alta-paciente', methods=['GET', 'POST'])
def alta_paciente():
    if request.method == 'POST':
        data = {
            'nombre': request.form['nombre'],
            'apellido_paterno': request.form['apellido_paterno'],
            'apellido_materno': request.form.get('apellido_materno', ''),
            'curp': request.form['curp'],
            'fecha_nacimiento': request.form['fecha_nacimiento'],
            'sexo': request.form['sexo'][0],
            'calle': request.form['calle'],
            'numero_exterior': request.form['numero_exterior'],
            'colonia': request.form['colonia'],
            'codigo_postal': request.form['codigo_postal'],
            'ciudad': request.form['ciudad'],
            'telefono': request.form['telefono'],
            'correo': request.form['correo'],
            'contacto_emergencia': request.form['contacto_emergencia']
        }
        
        patient_id = create_patient(data)
        if patient_id:
            flash(f'Paciente creado exitosamente con ID: P{patient_id:010d}', 'success')
            return redirect('/dashboard')
        else:
            flash('Error al crear el paciente', 'error')
    
    return render_template('alta_paciente.html')

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    app.run(debug=True, host='localhost', port=5000)