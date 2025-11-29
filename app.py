from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_muy_segura_para_el_historial_clinico'

# Configuración de la base de datos
DATABASE = 'historial_clinico.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with app.app_context():
        conn = get_db_connection()
        
        # Crear tabla de usuarios
        conn.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nombre TEXT NOT NULL,
                rol TEXT NOT NULL,
                especialidad TEXT,
                email TEXT,
                telefono TEXT
            )
        ''')
        
        # Crear tabla de pacientes
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pacientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre_completo TEXT NOT NULL,
                sexo TEXT NOT NULL,
                fecha_nacimiento DATE NOT NULL,
                curp TEXT UNIQUE NOT NULL,
                telefono TEXT,
                direccion TEXT,
                creado_por INTEGER,
                FOREIGN KEY (creado_por) REFERENCES usuarios (id)
            )
        ''')
        
        # Crear tabla de historiales clínicos
        conn.execute('''
            CREATE TABLE IF NOT EXISTS historiales_clinicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                paciente_id INTEGER NOT NULL,
                medicacion_actual TEXT,
                antecedentes_personales TEXT,
                antecedentes_familiares TEXT,
                antecedentes_quirurgicos TEXT,
                diagnosticos_actuales TEXT,
                ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actualizado_por INTEGER,
                FOREIGN KEY (paciente_id) REFERENCES pacientes (id),
                FOREIGN KEY (actualizado_por) REFERENCES usuarios (id)
            )
        ''')
        
        # Insertar usuarios por defecto si no existen
        cursor = conn.cursor()
        
        # Verificar si ya existen usuarios
        cursor.execute('SELECT COUNT(*) as count FROM usuarios')
        count = cursor.fetchone()['count']
        
        if count == 0:
            # Insertar doctor
            conn.execute(
                'INSERT INTO usuarios (username, password, nombre, rol, especialidad, email, telefono) VALUES (?, ?, ?, ?, ?, ?, ?)',
                ('doctor', 'doctor123', 'Dr. Juan Pérez', 'doctor', 'Medicina Interna', 'juan.perez@hospital.com', '8111223344')
            )
            
            # Insertar paciente
            conn.execute(
                'INSERT INTO usuarios (username, password, nombre, rol, email, telefono) VALUES (?, ?, ?, ?, ?, ?)',
                ('paciente', 'paciente123', 'Wendy Lizeth Rascón Chávez', 'paciente', 'wendy.rascon@email.com', '812345678')
            )
            
            # Insertar datos del paciente
            conn.execute(
                'INSERT INTO pacientes (nombre_completo, sexo, fecha_nacimiento, curp, telefono, direccion, creado_por) VALUES (?, ?, ?, ?, ?, ?, ?)',
                ('Wendy Lizeth Rascón Chávez', 'Femenino', '2005-07-29', 'RACW050729MMCSHNA2', '812345678', '234 Colonia Flor Bosques de Encinos', 1)
            )
            
            # Insertar historial clínico del paciente
            conn.execute(
                'INSERT INTO historiales_clinicos (paciente_id, medicacion_actual, antecedentes_personales, antecedentes_familiares, antecedentes_quirurgicos, actualizado_por) VALUES (?, ?, ?, ?, ?, ?)',
                (1, 
                 'Losarrán|60 mg|1 vez al día|Oral',
                 'Quirúrgicos:\n- Apendicitis — Apendicectomía en 2018.\n- Sin complicaciones posteriores.\n\nMédicos:\n- Hipertensión arterial (en tratamiento).\n- No presenta alergias conocidas.\n- No consumo de tabaco.\n- Consumo ocasional de alcohol (social).',
                 'Parentesco: Madre\nEnfermedad: Diabetes mellitus tipo 2\nObservaciones: Diagnóstico a los 50 años, en tratamiento.',
                 'Apendicitis — Apendicectomía en 2018. Sin complicaciones posteriores.',
                 1)
            )
        
        conn.commit()
        conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('historial_clinico'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        user = conn.execute(
            'SELECT * FROM usuarios WHERE username = ? AND password = ?',
            (username, password)
        ).fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['nombre'] = user['nombre']
            session['rol'] = user['rol']
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('historial_clinico'))
        else:
            flash('Usuario o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Sesión cerrada exitosamente', 'success')
    return redirect(url_for('login'))

@app.route('/historial-clinico')
def historial_clinico():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    
    if session['rol'] == 'doctor':
        # Doctor puede ver todos los pacientes
        pacientes = conn.execute(
            'SELECT * FROM pacientes'
        ).fetchall()
        
        # Por defecto, mostrar el primer paciente
        paciente_id = request.args.get('paciente_id', 1)
        paciente = conn.execute(
            'SELECT * FROM pacientes WHERE id = ?', (paciente_id,)
        ).fetchone()
    else:
        # Paciente solo puede ver su propio historial
        paciente = conn.execute(
            'SELECT * FROM pacientes WHERE nombre_completo = ?', (session['nombre'],)
        ).fetchone()
        pacientes = [paciente] if paciente else []
        paciente_id = paciente['id'] if paciente else None
    
    if paciente:
        historial = conn.execute(
            'SELECT * FROM historiales_clinicos WHERE paciente_id = ?', (paciente_id,)
        ).fetchone()
        
        # Calcular edad
        fecha_nacimiento = datetime.strptime(paciente['fecha_nacimiento'], '%Y-%m-%d')
        hoy = datetime.now()
        edad = hoy.year - fecha_nacimiento.year - ((hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
        
        # Formatear fecha de nacimiento
        fecha_nacimiento_formateada = fecha_nacimiento.strftime('%d/%m/%Y')
        
        # Parsear medicación
        if historial and historial['medicacion_actual']:
            medicacion_parts = historial['medicacion_actual'].split('|')
            medicacion = {
                'nombre': medicacion_parts[0] if len(medicacion_parts) > 0 else '',
                'dosis': medicacion_parts[1] if len(medicacion_parts) > 1 else '',
                'frecuencia': medicacion_parts[2] if len(medicacion_parts) > 2 else '',
                'via': medicacion_parts[3] if len(medicacion_parts) > 3 else ''
            }
        else:
            medicacion = {'nombre': '', 'dosis': '', 'frecuencia': '', 'via': ''}
    else:
        historial = None
        edad = None
        fecha_nacimiento_formateada = None
        medicacion = {'nombre': '', 'dosis': '', 'frecuencia': '', 'via': ''}
    
    conn.close()
    
    return render_template('historial_clinico.html', 
                         paciente=paciente, 
                         pacientes=pacientes,
                         historial=historial,
                         edad=edad,
                         fecha_nacimiento_formateada=fecha_nacimiento_formateada,
                         medicacion=medicacion)

@app.route('/actualizar-historial', methods=['POST'])
def actualizar_historial():
    if 'user_id' not in session or session['rol'] != 'doctor':
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    data = request.get_json()
    paciente_id = data.get('paciente_id')
    seccion = data.get('seccion')
    datos = data.get('datos')
    
    conn = get_db_connection()
    
    # Verificar si ya existe un historial para este paciente
    historial_existente = conn.execute(
        'SELECT * FROM historiales_clinicos WHERE paciente_id = ?', (paciente_id,)
    ).fetchone()
    
    if historial_existente:
        # Actualizar historial existente
        if seccion == 'datos_generales':
            conn.execute(
                'UPDATE pacientes SET nombre_completo = ?, sexo = ?, fecha_nacimiento = ?, curp = ?, telefono = ?, direccion = ? WHERE id = ?',
                (datos['nombre_completo'], datos['sexo'], datos['fecha_nacimiento'], datos['curp'], datos['telefono'], datos['direccion'], paciente_id)
            )
        elif seccion == 'medicacion':
            medicacion_str = f"{datos['nombre']}|{datos['dosis']}|{datos['frecuencia']}|{datos['via']}"
            conn.execute(
                'UPDATE historiales_clinicos SET medicacion_actual = ?, ultima_actualizacion = CURRENT_TIMESTAMP, actualizado_por = ? WHERE paciente_id = ?',
                (medicacion_str, session['user_id'], paciente_id)
            )
        elif seccion == 'antecedentes_personales':
            conn.execute(
                'UPDATE historiales_clinicos SET antecedentes_personales = ?, ultima_actualizacion = CURRENT_TIMESTAMP, actualizado_por = ? WHERE paciente_id = ?',
                (datos['antecedentes_personales'], session['user_id'], paciente_id)
            )
        elif seccion == 'antecedentes_familiares':
            conn.execute(
                'UPDATE historiales_clinicos SET antecedentes_familiares = ?, ultima_actualizacion = CURRENT_TIMESTAMP, actualizado_por = ? WHERE paciente_id = ?',
                (datos['antecedentes_familiares'], session['user_id'], paciente_id)
            )
        elif seccion == 'antecedentes_quirurgicos':
            conn.execute(
                'UPDATE historiales_clinicos SET antecedentes_quirurgicos = ?, ultima_actualizacion = CURRENT_TIMESTAMP, actualizado_por = ? WHERE paciente_id = ?',
                (datos['antecedentes_quirurgicos'], session['user_id'], paciente_id)
            )
        elif seccion == 'diagnosticos_actuales':
            conn.execute(
                'UPDATE historiales_clinicos SET diagnosticos_actuales = ?, ultima_actualizacion = CURRENT_TIMESTAMP, actualizado_por = ? WHERE paciente_id = ?',
                (datos['diagnosticos_actuales'], session['user_id'], paciente_id)
            )
    else:
        # Crear nuevo historial
        medicacion_str = f"{datos['nombre']}|{datos['dosis']}|{datos['frecuencia']}|{datos['via']}" if seccion == 'medicacion' else ''
        antecedentes_personales = datos['antecedentes_personales'] if seccion == 'antecedentes_personales' else ''
        antecedentes_familiares = datos['antecedentes_familiares'] if seccion == 'antecedentes_familiares' else ''
        antecedentes_quirurgicos = datos['antecedentes_quirurgicos'] if seccion == 'antecedentes_quirurgicos' else ''
        diagnosticos_actuales = datos['diagnosticos_actuales'] if seccion == 'diagnosticos_actuales' else ''
        
        conn.execute(
            'INSERT INTO historiales_clinicos (paciente_id, medicacion_actual, antecedentes_personales, antecedentes_familiares, antecedentes_quirurgicos, diagnosticos_actuales, actualizado_por) VALUES (?, ?, ?, ?, ?, ?, ?)',
            (paciente_id, medicacion_str, antecedentes_personales, antecedentes_familiares, antecedentes_quirurgicos, diagnosticos_actuales, session['user_id'])
        )
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Historial actualizado correctamente'})

@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM usuarios WHERE id = ?', (session['user_id'],)
    ).fetchone()
    conn.close()
    
    return render_template('perfil.html', user=user)

@app.route('/buscar-paciente')
def buscar_paciente():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('buscar_paciente.html')

@app.route('/api/pacientes')
def api_pacientes():
    if 'user_id' not in session:
        return jsonify({'error': 'No autorizado'}), 401
    
    conn = get_db_connection()
    
    # Si es doctor, mostrar todos los pacientes
    if session.get('rol') == 'doctor':
        pacientes = conn.execute('SELECT id, nombre_completo, curp FROM pacientes').fetchall()
    else:
        # Si es paciente, solo mostrar su información
        pacientes = conn.execute(
            'SELECT id, nombre_completo, curp FROM pacientes WHERE id = ?',
            (session.get('user_id'),)
        ).fetchall()
    
    conn.close()
    
    return jsonify({
        'pacientes': [dict(p) for p in pacientes]
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True)