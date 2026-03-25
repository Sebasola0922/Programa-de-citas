create database gestion_logistica;
use  gestion_logistica;

CREATE TABLE empresa (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    tipo_empresa ENUM('generadora', 'transportadora') NOT NULL,
    direccion VARCHAR(150),
    telefono VARCHAR(20),
    email VARCHAR(100)
) ENGINE=InnoDB;


-- TABLA USUARIO

CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    rol ENUM('admin', 'operador', 'transportador') NOT NULL,
    id_empresa INT,
    CONSTRAINT fk_usuario_empresa
        FOREIGN KEY (id_empresa)
        REFERENCES empresa(id_empresa)
        ON DELETE SET NULL
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- TABLA VEHICULO

CREATE TABLE vehiculo (
    id_vehiculo INT AUTO_INCREMENT PRIMARY KEY,
    placa VARCHAR(10) NOT NULL UNIQUE,
    tipo VARCHAR(50),
    capacidad FLOAT,
    id_empresa INT NOT NULL,
    CONSTRAINT fk_vehiculo_empresa
        FOREIGN KEY (id_empresa)
        REFERENCES empresa(id_empresa)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- TABLA CITA

CREATE TABLE cita (
    id_cita INT AUTO_INCREMENT PRIMARY KEY,
    fecha_hora_inicio DATETIME NOT NULL,
    fecha_hora_fin DATETIME NOT NULL,
    estado ENUM('programada', 'en_proceso', 'finalizada', 'cancelada') 
        DEFAULT 'programada',
    tipo ENUM('cargue', 'descargue') NOT NULL,
    id_empresa_generadora INT NOT NULL,
    id_vehiculo INT NOT NULL,
    id_usuario_creador INT NOT NULL,

    CONSTRAINT fk_cita_empresa
        FOREIGN KEY (id_empresa_generadora)
        REFERENCES empresa(id_empresa)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_cita_vehiculo
        FOREIGN KEY (id_vehiculo)
        REFERENCES vehiculo(id_vehiculo)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_cita_usuario
        FOREIGN KEY (id_usuario_creador)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;


-- TABLA REASIGNACION

CREATE TABLE reasignacion (
    id_reasignacion INT AUTO_INCREMENT PRIMARY KEY,
    id_cita INT NOT NULL,
    fecha_reasignacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo VARCHAR(255),
    nueva_fecha_hora DATETIME NOT NULL,
    id_usuario INT NOT NULL,

    CONSTRAINT fk_reasignacion_cita
        FOREIGN KEY (id_cita)
        REFERENCES cita(id_cita)
        ON DELETE CASCADE
        ON UPDATE CASCADE,

    CONSTRAINT fk_reasignacion_usuario
        FOREIGN KEY (id_usuario)
        REFERENCES usuario(id_usuario)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB;

