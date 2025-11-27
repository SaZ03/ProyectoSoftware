from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'clave_secreta_benavides_2024'

# Datos de prueba para pacientes
pacientes = [
    {
        'id': 'P2609202501',
        'nombre': 'Wendy Lizeth Rascón Chávez',
        'sexo': 'Femenino',
        'edad': 20,
        'curp': 'RACW050729MMCSHNA2',
        'telefono': '8112345678',
        'direccion': '234 Colonia Flor Bosques de Encinos',
        'correo': 'wendy@gmail.com',
        'contacto_emergencia': '8112345679'
    },
    {
        'id': 'P2609202502', 
        'nombre': 'José Ramírez',
        'sexo': 'Masculino',
        'edad': 22,
        'curp': 'RAJJ021215HMCMSA8',
        'telefono': '8187654321',
        'direccion': '123 Colonia Centro',
        'correo': 'jose@email.com',
        'contacto_emergencia': '8187654322'
    },
    {
        'id': 'P2609202503',
        'nombre': 'Ethan Zavala',
        'sexo': 'Masculino', 
        'edad': 27,
        'curp': 'ZAHE930101HMCVSA1',
        'telefono': '8133445566',
        'direccion': '456 Colonia Reforma',
        'correo': 'ethan@email.com',
        'contacto_emergencia': '8133445567'
    }
]

# Rutas principales
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    # Por ahora, cualquier usuario puede entrar
    return redirect('/dashboard')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', pacientes=pacientes)

@app.route('/paciente/<patient_id>')
def ver_paciente(patient_id):
    paciente = next((p for p in pacientes if p['id'] == patient_id), None)
    if paciente:
        return render_template('ver_paciente.html', paciente=paciente)
    else:
        flash('Paciente no encontrado', 'error')
        return redirect('/dashboard')

@app.route('/editar/<patient_id>', methods=['GET', 'POST'])
def editar_paciente(patient_id):
    paciente = next((p for p in pacientes if p['id'] == patient_id), None)
    
    if not paciente:
        flash('Paciente no encontrado', 'error')
        return redirect('/dashboard')
    
    if request.method == 'POST':
        # Actualizar datos del paciente
        paciente['nombre'] = request.form['nombre']
        paciente['direccion'] = request.form['direccion']
        paciente['telefono'] = request.form['telefono']
        paciente['correo'] = request.form['correo']
        paciente['sexo'] = request.form['sexo']
        paciente['curp'] = request.form['curp']
        paciente['contacto_emergencia'] = request.form['contacto_emergencia']
        
        flash('Datos del paciente actualizados correctamente', 'success')
        return redirect(f'/paciente/{patient_id}')
    
    return render_template('editar_paciente.html', paciente=paciente)

@app.route('/buscar')
def buscar_pacientes():
    query = request.args.get('q', '').lower()
    if query:
        resultados = [p for p in pacientes if query in p['nombre'].lower() or query in p['id'].lower()]
    else:
        resultados = pacientes
    
    return jsonify(resultados)

if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)