from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import database as db
from auth import User
from models import get_patient_history, update_patient_history

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambiar en producción

# Configuración Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Rutas de Autenticación
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.authenticate(email, password)
        if user:
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Credenciales incorrectas', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Rutas Principales
@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/historial/<int:patient_id>')
@login_required
def view_history(patient_id):
    historial = get_patient_history(patient_id)
    return render_template('historial.html', historial=historial, patient_id=patient_id)

@app.route('/historial/editar/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_history(patient_id):
    if request.method == 'POST':
        # Procesar formulario de edición
        data = {
            'antecedentes_quirurgicos': request.form.get('quirurgicos'),
            'antecedentes_medicos': request.form.get('medicos'),
            'alergias': request.form.get('alergias'),
            'habitos': request.form.get('habitos'),
            'medicacion_actual': request.form.get('medicacion'),
            'antecedentes_familiares': request.form.get('familiares')
        }
        update_patient_history(patient_id, data, current_user.id)
        flash('Historial actualizado correctamente', 'success')
        return redirect(url_for('view_history', patient_id=patient_id))
    
    historial = get_patient_history(patient_id)
    return render_template('editar_historial.html', historial=historial, patient_id=patient_id)

if __name__ == '__main__':
    app.run(debug=True)