import sqlite3
import os
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('sistema_medico.db', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query, params=None, fetch=False, fetch_one=False):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch:
            result = [dict(row) for row in cursor.fetchall()]
        elif fetch_one:
            row = cursor.fetchone()
            result = dict(row) if row else None
        else:
            conn.commit()
            result = cursor.lastrowid
        
        conn.close()
        return result
    except Exception as e:
        print(f"❌ Error en query: {e}")
        print(f"Query: {query}")
        print(f"Params: {params}")
        conn.close()
        return None

def init_db():
    """Inicializar la base de datos con las tablas y datos de prueba"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Script SQL completo
    sql_script = """
    -- Eliminar tablas si existen
    DROP TABLE IF EXISTS receta_medica;
    DROP TABLE IF EXISTS Consulta;
    DROP TABLE IF EXISTS HistorialActualizacion;
    DROP TABLE IF EXISTS AntecedentePatologico;
    DROP TABLE IF EXISTS AntecedenteNoPatologico;
    DROP TABLE IF EXISTS AntecedenteFamiliar;
    DROP TABLE IF EXISTS HistorialMedico;
    DROP TABLE IF EXISTS NoMezclar;
    DROP TABLE IF EXISTS Medicina;
    DROP TABLE IF EXISTS Medico;
    DROP TABLE IF EXISTS RolUsuario;
    DROP TABLE IF EXISTS Rol;
    DROP TABLE IF EXISTS RegistroUsuario;
    DROP TABLE IF EXISTS Usuario;

    -- Tabla: Usuario
    CREATE TABLE Usuario (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_usuario VARCHAR(50) NOT NULL,
        apellido_paterno VARCHAR(50) NOT NULL,
        apellido_materno VARCHAR(50),
        curp CHAR(18) UNIQUE,
        nss CHAR(11) UNIQUE,
        fecha_nacimiento DATE,
        sexo TEXT CHECK(sexo IN ('M', 'F', 'Otro')),
        estado_civil TEXT CHECK(estado_civil IN ('Soltero', 'Casado', 'Divorciado', 'Viudo', 'Otro')),
        calle VARCHAR(100),
        numero_exterior VARCHAR(10),
        numero_interior VARCHAR(10),
        colonia VARCHAR(100),
        codigo_postal CHAR(5),
        ciudad VARCHAR(100),
        estado VARCHAR(100),
        pais VARCHAR(100),
        telefono VARCHAR(20),
        correo VARCHAR(100) UNIQUE,
        contacto_emergencia VARCHAR(100),
        tipo_sangre VARCHAR(5),
        altura DECIMAL(4,2),
        peso DECIMAL(5,2),
        seguro_medico VARCHAR(100),
        contrasena_hash VARCHAR(255) NOT NULL
    );

    -- Tabla: Rol
    CREATE TABLE Rol (
        id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_rol TEXT CHECK(nombre_rol IN ('Médico', 'Farmacéutico', 'Administrativo', 'Paciente')) UNIQUE
    );

    -- Tabla: Relación Usuario-Rol
    CREATE TABLE RolUsuario (
        id_usuario INTEGER,
        id_rol INTEGER,
        PRIMARY KEY (id_usuario, id_rol),
        FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
        FOREIGN KEY (id_rol) REFERENCES Rol(id_rol) ON DELETE CASCADE
    );

    -- Insertar roles básicos
    INSERT INTO Rol (nombre_rol) VALUES 
    ('Médico'),
    ('Farmacéutico'),
    ('Administrativo'),
    ('Paciente');

    -- =======================================================
    -- USUARIOS DE PRUEBA
    -- =======================================================

    -- Doctor Principal
    INSERT INTO Usuario (nombre_usuario, apellido_paterno, apellido_materno, correo, contrasena_hash, telefono) 
    VALUES ('Carlos', 'Mendoza', 'López', 'doctor@benavides.com', 'doctor123', '8181001001');

    -- Administrador
    INSERT INTO Usuario (nombre_usuario, apellido_paterno, apellido_materno, correo, contrasena_hash, telefono) 
    VALUES ('Ana', 'García', 'Rodríguez', 'admin@benavides.com', 'admin123', '8182002002');

    -- Paciente de Prueba
    INSERT INTO Usuario (nombre_usuario, apellido_paterno, apellido_materno, curp, fecha_nacimiento, sexo, telefono, correo, contacto_emergencia, contrasena_hash, calle, numero_exterior, colonia, codigo_postal, ciudad) 
    VALUES ('María', 'González', 'Pérez', 'GOPM880101MTSNRA01', '1988-01-01', 'F', '8183003003', 'paciente@benavides.com', '8184004004', 'paciente123', 'Av. Revolución', '123', 'Centro', '64000', 'Monterrey');

    -- Asignar roles
    INSERT INTO RolUsuario (id_usuario, id_rol) VALUES 
    (1, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Médico')),
    (2, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Administrativo')),
    (3, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Paciente'));

    -- Más pacientes de prueba
    INSERT INTO Usuario (nombre_usuario, apellido_paterno, apellido_materno, curp, fecha_nacimiento, sexo, telefono, correo, contacto_emergencia, contrasena_hash, calle, numero_exterior, colonia, codigo_postal, ciudad) VALUES 
    ('Wendy Lizeth', 'Rascón', 'Chávez', 'RACW050729MMCSHNA2', '2005-07-29', 'F', '8112345678', 'wendy@gmail.com', '8112345679', '123', 'Av. Ignacio Morones', '65238', 'Flor Bosques', '64780', 'Monterrey'),
    ('José', 'Ramírez', 'Gómez', 'RAJJ021215HMCMSA8', '2002-12-15', 'M', '8187654321', 'jose@email.com', '8187654322', '123', 'Calle Central', '456', 'Colonia Norte', '64750', 'Monterrey'),
    ('Ethan', 'Zavala', 'López', 'ZAHE930101HMCVSA1', '1997-01-01', 'M', '8133445566', 'ethan@email.com', '8133445567', '123', 'Blvd. Constitución', '789', 'Reforma', '64720', 'Monterrey');

    INSERT INTO RolUsuario (id_usuario, id_rol) VALUES 
    (4, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Paciente')),
    (5, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Paciente')),
    (6, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Paciente'));
    """
    
    # Ejecutar script
    try:
        cursor.executescript(sql_script)
        conn.commit()
        print("✅ Base de datos inicializada correctamente")
        print("👨‍⚕️ Usuarios creados:")
        print("   Doctor: doctor@benavides.com / doctor123")
        print("   Admin: admin@benavides.com / admin123") 
        print("   Paciente: paciente@benavides.com / paciente123")
        print("   Paciente Wendy: wendy@gmail.com / 123")
        print("   Paciente José: jose@email.com / 123")
        print("   Paciente Ethan: ethan@email.com / 123")
    except Exception as e:
        print(f"❌ Error inicializando BD: {e}")
    finally:
        conn.close()