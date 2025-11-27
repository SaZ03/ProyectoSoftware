-- Tabla: Usuario
CREATE TABLE IF NOT EXISTS Usuario (
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
CREATE TABLE IF NOT EXISTS Rol (
    id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_rol TEXT CHECK(nombre_rol IN ('Médico', 'Farmacéutico', 'Administrativo', 'Paciente')) UNIQUE
);

-- Tabla: Relación Usuario-Rol
CREATE TABLE IF NOT EXISTS RolUsuario (
    id_usuario INTEGER,
    id_rol INTEGER,
    PRIMARY KEY (id_usuario, id_rol),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol) ON DELETE CASCADE
);

-- Insertar roles básicos
INSERT OR IGNORE INTO Rol (nombre_rol) VALUES 
('Médico'),
('Farmacéutico'),
('Administrativo'),
('Paciente');

-- Insertar usuario médico de prueba
INSERT OR IGNORE INTO Usuario (nombre_usuario, apellido_paterno, apellido_materno, correo, contrasena_hash) 
VALUES ('Doctor', 'Prueba', 'Sistema', 'doctor@test.com', '123');

-- Asignar rol de médico
INSERT OR IGNORE INTO RolUsuario (id_usuario, id_rol) 
VALUES (1, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Médico'));

-- Insertar pacientes de prueba
INSERT OR IGNORE INTO Usuario (nombre_usuario, apellido_paterno, apellido_materno, curp, fecha_nacimiento, sexo, telefono, correo, contacto_emergencia, contrasena_hash) VALUES 
('Wendy Lizeth', 'Rascón', 'Chávez', 'RACW050729MMCSHNA2', '2005-07-29', 'F', '8112345678', 'wendy@gmail.com', '8112345679', '123'),
('José', 'Ramírez', 'Gómez', 'RAJJ021215HMCMSA8', '2002-12-15', 'M', '8187654321', 'jose@email.com', '8187654322', '123'),
('Ethan', 'Zavala', 'López', 'ZAHE930101HMCVSA1', '1997-01-01', 'M', '8133445566', 'ethan@email.com', '8133445567', '123');

-- Asignar rol de paciente
INSERT OR IGNORE INTO RolUsuario (id_usuario, id_rol) 
VALUES 
(2, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Paciente')),
(3, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Paciente')),
(4, (SELECT id_rol FROM Rol WHERE nombre_rol = 'Paciente'));