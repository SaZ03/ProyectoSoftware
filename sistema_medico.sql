DROP DATABASE IF EXISTS sistema_medico;
CREATE DATABASE sistema_medico;
USE sistema_medico;

-- =======================================================
-- Tabla: Usuario
-- =======================================================
CREATE TABLE Usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL,
    apellido_paterno VARCHAR(50) NOT NULL,
    apellido_materno VARCHAR(50),
    curp CHAR(18) UNIQUE,
    nss CHAR(11) UNIQUE,
    fecha_nacimiento DATE,
    sexo ENUM('M','F','Otro'),
    estado_civil ENUM('Soltero','Casado','Divorciado','Viudo','Otro'),
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

-- =======================================================
-- Tabla: Rol
-- =======================================================
CREATE TABLE Rol (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol ENUM('Médico', 'Farmacéutico', 'Administrativo', 'Paciente') UNIQUE
);

-- =======================================================
-- Tabla: Relación Usuario-Rol
-- =======================================================
CREATE TABLE RolUsuario (
    id_usuario INT,
    id_rol INT,
    PRIMARY KEY (id_usuario, id_rol),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_rol) REFERENCES Rol(id_rol) ON DELETE CASCADE
);

-- =======================================================
-- Tabla: Médico
-- =======================================================
CREATE TABLE Medico (
    id_medico INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT UNIQUE,
    cedula_profesional VARCHAR(20) UNIQUE NOT NULL,
    especialidad VARCHAR(100),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

-- =======================================================
-- Tabla: Medicina
-- =======================================================
CREATE TABLE Medicina (
    id_medicina INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    condicion_restringida VARCHAR(255)
);

-- =======================================================
-- Tabla: NoMezclar (medicinas incompatibles)
-- =======================================================
CREATE TABLE NoMezclar (
    id_medicina1 INT,
    id_medicina2 INT,
    PRIMARY KEY (id_medicina1, id_medicina2),
    FOREIGN KEY (id_medicina1) REFERENCES Medicina(id_medicina) ON DELETE CASCADE,
    FOREIGN KEY (id_medicina2) REFERENCES Medicina(id_medicina) ON DELETE CASCADE
);

-- =======================================================
-- Tablas: Historial Médico (normalizado)
-- =======================================================

CREATE TABLE HistorialMedico (
    id_historial INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT UNIQUE,
    fecha_ingreso_ux DATE,
    fecha_ingreso_piso DATE,
    tipo_interrogatorio VARCHAR(100),
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_paciente) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);

CREATE TABLE AntecedenteFamiliar (
    id_antecedente INT AUTO_INCREMENT PRIMARY KEY,
    id_historial INT,
    relacion ENUM('Padre','Madre','Hermano','Hija','Hijo','Otro'),
    condicion VARCHAR(100),
    descripcion TEXT,
    FOREIGN KEY (id_historial) REFERENCES HistorialMedico(id_historial) ON DELETE CASCADE
);

CREATE TABLE AntecedenteNoPatologico (
    id_no_patologico INT AUTO_INCREMENT PRIMARY KEY,
    id_historial INT,
    ocupacion VARCHAR(100),
    escolaridad VARCHAR(100),
    religion VARCHAR(100),
    FOREIGN KEY (id_historial) REFERENCES HistorialMedico(id_historial) ON DELETE CASCADE
);

CREATE TABLE AntecedentePatologico (
    id_patologico INT AUTO_INCREMENT PRIMARY KEY,
    id_historial INT,
    tabaquismo BOOLEAN DEFAULT FALSE,
    etilismo BOOLEAN DEFAULT FALSE,
    toxicomanias BOOLEAN DEFAULT FALSE,
    tatuajes BOOLEAN DEFAULT FALSE,
    biomasa BOOLEAN DEFAULT FALSE,
    combe BOOLEAN DEFAULT FALSE,
    inmunizaciones TEXT,
    cirugias TEXT,
    fracturas TEXT,
    transfusiones TEXT,
    alergias_antecedentes TEXT,
    enfermedades_cronicas TEXT,
    ultima_hospitalizacion DATE,
    FOREIGN KEY (id_historial) REFERENCES HistorialMedico(id_historial) ON DELETE CASCADE
);

-- =======================================================
-- Tabla: Historial de Actualizaciones
-- =======================================================
CREATE TABLE HistorialActualizacion (
    id_actualizacion INT AUTO_INCREMENT PRIMARY KEY,
    id_historial INT,
    id_medico INT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    descripcion TEXT,
    FOREIGN KEY (id_historial) REFERENCES HistorialMedico(id_historial) ON DELETE CASCADE,
    FOREIGN KEY (id_medico) REFERENCES Medico(id_medico) ON DELETE SET NULL
);

-- =======================================================
-- Tabla: Consulta
-- =======================================================
CREATE TABLE Consulta (
    id_consulta INT AUTO_INCREMENT PRIMARY KEY,
    id_paciente INT,
    id_medico INT,
    fecha DATE NOT NULL,
    motivo TEXT,
    diagnostico TEXT,
    FOREIGN KEY (id_paciente) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_medico) REFERENCES Medico(id_medico) ON DELETE SET NULL
);

-- =======================================================
-- Tabla intermedia: Consulta-Medicina
-- =======================================================
CREATE TABLE receta_medica (
    id_consulta INT,
    id_medicina INT,
    dosis VARCHAR(50),
    frecuencia VARCHAR(50),
    duracion VARCHAR(50),
    PRIMARY KEY (id_consulta, id_medicina),
    FOREIGN KEY (id_consulta) REFERENCES Consulta(id_consulta) ON DELETE CASCADE,
    FOREIGN KEY (id_medicina) REFERENCES Medicina(id_medicina) ON DELETE CASCADE
);

-- =======================================================
-- Tabla: Registro de creación de usuarios
-- =======================================================
CREATE TABLE RegistroUsuario (
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    id_admin INT,
    id_usuario_creado INT,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_admin) REFERENCES Usuario(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (id_usuario_creado) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
);
