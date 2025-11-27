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
    return db.execute_query(query, fetch=True) or []

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
        u.seguro_medico,
        CAST((julianday('now') - julianday(u.fecha_nacimiento)) / 365.25 AS INTEGER) as edad
    FROM Usuario u
    WHERE u.id_usuario = ?
    """
    return db.execute_query(query, (patient_id,), fetch_one=True)

def search_patients(search_term):
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
    return db.execute_query(query, (search_pattern, search_pattern, search_pattern, search_pattern), fetch=True) or []

def update_patient(patient_id, data):
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
        data['nombre'],
        data['apellido_paterno'],
        data['apellido_materno'],
        data['curp'],
        data['fecha_nacimiento'],
        data['sexo'],
        data['calle'],
        data['numero_exterior'],
        data['colonia'],
        data['codigo_postal'],
        data['ciudad'],
        data['telefono'],
        data['correo'],
        data['contacto_emergencia'],
        patient_id
    )
    
    return db.execute_query(query, params)

def create_patient(data):
    query = """
    INSERT INTO Usuario (
        nombre_usuario, apellido_paterno, apellido_materno, curp, fecha_nacimiento,
        sexo, calle, numero_exterior, colonia, codigo_postal, ciudad, telefono,
        correo, contacto_emergencia, contrasena_hash
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    # Contraseña temporal
    temp_password = "temp123"
    
    params = (
        data['nombre'],
        data['apellido_paterno'], 
        data['apellido_materno'],
        data['curp'],
        data['fecha_nacimiento'],
        data['sexo'],
        data['calle'],
        data['numero_exterior'],
        data['colonia'],
        data['codigo_postal'],
        data['ciudad'],
        data['telefono'],
        data['correo'],
        data['contacto_emergencia'],
        temp_password
    )
    
    user_id = db.execute_query(query, params)
    
    # Asignar rol de paciente
    if user_id:
        role_query = "INSERT INTO RolUsuario (id_usuario, id_rol) VALUES (?, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Paciente'))"
        db.execute_query(role_query, (user_id,))
    
    return user_id