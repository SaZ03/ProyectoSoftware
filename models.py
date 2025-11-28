import database as db
from datetime import datetime

def get_all_patients():
    query = """
    SELECT 
        u.id_usuario,
        u.nombre_usuario || ' ' || u.apellido_paterno || ' ' || COALESCE(u.apellido_materno, '') as nombre_completo,
        u.curp,
        u.telefono,
        u.correo,
        u.sexo,
        CAST((julianday('now') - julianday(u.fecha_nacimiento)) / 365.25 AS INTEGER) as edad,
        u.calle || ' ' || u.numero_exterior || ' ' || COALESCE(u.numero_interior, '') || ', ' || u.colonia as direccion,
        u.contacto_emergencia
    FROM Usuario u
    JOIN RolUsuario ru ON u.id_usuario = ru.id_usuario
    JOIN Rol r ON ru.id_rol = r.id_rol
    WHERE r.nombre_rol = 'Paciente'
    """
    result = db.execute_query(query, fetch=True)
    return result if result else []

def get_patient_by_id(patient_id):
    query = """
    SELECT 
        u.id_usuario,
        u.nombre_usuario,
        u.apellido_paterno,
        u.apellido_materno,
        u.curp,
        u.nss,
        u.fecha_nacimiento,
        u.sexo,
        u.estado_civil,
        u.calle,
        u.numero_exterior,
        u.numero_interior,
        u.colonia,
        u.codigo_postal,
        u.ciudad,
        u.estado,
        u.pais,
        u.telefono,
        u.correo,
        u.contacto_emergencia,
        u.tipo_sangre,
        u.altura,
        u.peso,
        u.seguro_medico
    FROM Usuario u
    WHERE u.id_usuario = ?
    """
    result = db.execute_query(query, (patient_id,), fetch_one=True)
    if result:
        # Calcular edad si hay fecha de nacimiento
        if result['fecha_nacimiento']:
            birth_date = datetime.strptime(result['fecha_nacimiento'], '%Y-%m-%d')
            today = datetime.now()
            result['edad'] = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        else:
            result['edad'] = None
    return result

def search_patients(search_term):
    if not search_term:
        return get_all_patients()
    
    query = """
    SELECT 
        u.id_usuario,
        u.nombre_usuario || ' ' || u.apellido_paterno || ' ' || COALESCE(u.apellido_materno, '') as nombre_completo,
        u.curp,
        u.telefono,
        u.sexo,
        CAST((julianday('now') - julianday(u.fecha_nacimiento)) / 365.25 AS INTEGER) as edad
    FROM Usuario u
    JOIN RolUsuario ru ON u.id_usuario = ru.id_usuario
    JOIN Rol r ON ru.id_rol = r.id_rol
    WHERE r.nombre_rol = 'Paciente'
    AND (u.nombre_usuario LIKE ? OR u.apellido_paterno LIKE ? OR u.curp LIKE ? OR u.telefono LIKE ?)
    """
    search_pattern = f"%{search_term}%"
    result = db.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern), fetch=True)
    return result if result else []

def update_patient(patient_id, data):
    try:
        query = """
        UPDATE Usuario 
        SET 
            nombre_usuario = ?,
            apellido_paterno = ?,
            apellido_materno = ?,
            curp = ?,
            fecha_nacimiento = ?,
            sexo = ?,
            calle = ?,
            numero_exterior = ?,
            colonia = ?,
            codigo_postal = ?,
            ciudad = ?,
            telefono = ?,
            correo = ?,
            contacto_emergencia = ?
        WHERE id_usuario = ?
        """
        
        params = (
            data.get('nombre', ''),
            data.get('apellido_paterno', ''),
            data.get('apellido_materno', ''),
            data.get('curp', ''),
            data.get('fecha_nacimiento', ''),
            data.get('sexo', ''),
            data.get('calle', ''),
            data.get('numero_exterior', ''),
            data.get('colonia', ''),
            data.get('codigo_postal', ''),
            data.get('ciudad', ''),
            data.get('telefono', ''),
            data.get('correo', ''),
            data.get('contacto_emergencia', ''),
            patient_id
        )
        
        result = db.execute_query(query, params)
        return result is not None
    except Exception as e:
        print(f"❌ Error en update_patient: {e}")
        return False

def create_patient(data):
    try:
        query = """
        INSERT INTO Usuario (
            nombre_usuario, apellido_paterno, apellido_materno, curp, fecha_nacimiento,
            sexo, calle, numero_exterior, colonia, codigo_postal, ciudad, telefono,
            correo, contacto_emergencia, contrasena_hash
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        temp_password = "123"  # Contraseña simple para desarrollo
        
        params = (
            data.get('nombre', ''),
            data.get('apellido_paterno', ''),
            data.get('apellido_materno', ''),
            data.get('curp', ''),
            data.get('fecha_nacimiento', ''),
            data.get('sexo', ''),
            data.get('calle', ''),
            data.get('numero_exterior', ''),
            data.get('colonia', ''),
            data.get('codigo_postal', ''),
            data.get('ciudad', ''),
            data.get('telefono', ''),
            data.get('correo', ''),
            data.get('contacto_emergencia', ''),
            temp_password
        )
        
        user_id = db.execute_query(query, params)
        
        # Asignar rol de paciente
        if user_id:
            role_query = "INSERT INTO RolUsuario (id_usuario, id_rol) VALUES (?, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Paciente'))"
            db.execute_query(role_query, (user_id,))
            return user_id
        return None
    except Exception as e:
        print(f"❌ Error en create_patient: {e}")
        return None