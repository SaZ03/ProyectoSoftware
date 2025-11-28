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

# Inicializar base de datos AL INICIO
print("🔄 Inicializando base de datos...")
db.init_db()

# Helper para formatear nombre
def format_patient_display(patient_db):
    if not patient_db:
        return None
        
    # Calcular edad si no viene
    if 'edad' not in patient_db or not patient_db['edad']:
        if patient_db.get('fecha_nacimiento'):
            birth_date = datetime.strptime(patient_db['fecha_nacimiento'], '%Y-%m-%d')
            today = datetime.now()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        else:
            age = 0
    else:
        age = patient_db['edad']
    
    return {
        'id': f"P{patient_db['id_usuario']:010d}",
        'id_usuario': patient_db['id_usuario'],
        'nombre_completo': patient_db.get('nombre_completo', f"{patient_db.get('nombre_usuario', '')} {patient_db.get('apellido_paterno', '')} {patient_db.get('apellido_materno', '')}"),
        'sexo': 'Femenino' if patient_db.get('sexo') == 'F' else 'Masculino',
        'edad': age,
        'curp': patient_db.get('curp', ''),
        'telefono': patient_db.get('telefono', ''),
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
    
    print(f"🔐 Intentando login: {email}")
    
    if email and password:
        user = User.authenticate(email, password)
        if user:
            login_user(user)
            flash(f'Bienvenido Dr. {user.nombre}', 'success')
            return redirect('/dashboard')
        else:
            print(f"❌ Falló autenticación para: {email}")
    
    flash('Credenciales incorrectas. Usa: doctor@benavides.com / doctor123', 'error')
    return redirect('/')

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# Rutas Principales
@app.route('/dashboard')
def dashboard():
    try:
        pacientes_db = get_all_patients()
        print(f"📊 Pacientes encontrados: {len(pacientes_db)}")
        pacientes = [format_patient_display(p) for p in pacientes_db if p]
        return render_template('dashboard.html', pacientes=pacientes)
    except Exception as e:
        print(f"❌ Error en dashboard: {e}")
        flash('Error cargando pacientes', 'error')
        return render_template('dashboard.html', pacientes=[])

@app.route('/paciente/<patient_id>')
def ver_paciente(patient_id):
    try:
        # Extraer ID numérico del formato P0000000001
        id_numero = int(patient_id[1:]) if patient_id.startswith('P') else int(patient_id)
        print(f"👤 Buscando paciente ID: {id_numero}")
        
        paciente_db = get_patient_by_id(id_numero)
        if paciente_db:
            paciente = format_patient_display(paciente_db)
            return render_template('ver_paciente.html', paciente=paciente)
        else:
            flash('Paciente no encontrado', 'error')
            return redirect('/dashboard')
    except Exception as e:
        print(f"❌ Error viendo paciente: {e}")
        flash('Error cargando paciente', 'error')
        return redirect('/dashboard')

@app.route('/editar/<patient_id>', methods=['GET', 'POST'])
def editar_paciente(patient_id):
    try:
        # Extraer ID numérico
        id_numero = int(patient_id[1:]) if patient_id.startswith('P') else int(patient_id)
        
        if request.method == 'POST':
            print("📝 Procesando edición de paciente...")
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
                print("✅ Paciente actualizado exitosamente")
            else:
                flash('Error al actualizar los datos', 'error')
                print("❌ Error actualizando paciente")
            
            return redirect(f'/paciente/{patient_id}')
        
        # GET - Mostrar formulario
        paciente_db = get_patient_by_id(id_numero)
        if paciente_db:
            # Formatear fecha para el input type="date"
            fecha_nacimiento = paciente_db.get('fecha_nacimiento')
            if fecha_nacimiento:
                if isinstance(fecha_nacimiento, str):
                    fecha_formateada = fecha_nacimiento
                else:
                    fecha_formateada = fecha_nacimiento.strftime('%Y-%m-%d')
            else:
                fecha_formateada = ''
                
            paciente = {
                'id': f"P{paciente_db['id_usuario']:010d}",
                'nombre': paciente_db['nombre_usuario'],
                'apellido_paterno': paciente_db['apellido_paterno'],
                'apellido_materno': paciente_db.get('apellido_materno', ''),
                'curp': paciente_db['curp'],
                'fecha_nacimiento': fecha_formateada,
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
    except Exception as e:
        print(f"❌ Error en editar_paciente: {e}")
        flash('Error procesando la solicitud', 'error')
        return redirect('/dashboard')

@app.route('/alta-paciente', methods=['GET', 'POST'])
def alta_paciente():
    try:
        if request.method == 'POST':
            print("🆕 Procesando alta de paciente...")
            data = {
                'nombre': request.form['nombre'],
                'apellido_paterno': request.form['apellido_paterno'],
                'apellido_materno': request.form.get('apellido_materno', ''),
                'curp': request.form['curp'],
                'fecha_nacimiento': request.form['fecha_nacimiento'],
                'sexo': request.form['sexo'],
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
                print(f"✅ Paciente creado con ID: {patient_id}")
                return redirect('/dashboard')
            else:
                flash('Error al crear el paciente', 'error')
                print("❌ Error creando paciente")
        
        return render_template('alta_paciente.html')
    except Exception as e:
        print(f"❌ Error en alta_paciente: {e}")
        flash('Error procesando la solicitud', 'error')
        return redirect('/dashboard')

@app.route('/buscar')
def buscar_pacientes():
    query = request.args.get('q', '')
    resultados_db = search_patients(query)
    resultados = [format_patient_display(p) for p in resultados_db if p]
    return jsonify(resultados)

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask...")
    app.run(debug=True, host='localhost', port=5000)