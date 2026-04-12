 -- Crear base de datos
CREATE DATABASE sistema_citas;

-- Usar la base de datos
USE sistema_citas;

-- Tabla que almacena las empresas
CREATE TABLE empresa (
    id_empresa INT AUTO_INCREMENT PRIMARY KEY, -- Identificador único

    nombre VARCHAR(100) NOT NULL, -- Nombre de la empresa

    tipo_empresa VARCHAR(50), -- Generadora o transportadora

    direccion VARCHAR(150), -- Dirección física

    telefono VARCHAR(20), -- Número de contacto

    email VARCHAR(100) -- Correo electrónico
);


ALTER TABLE empresa 
ADD estado VARCHAR(20) DEFAULT 'activa';

-- Tabla de usuarios del sistema
CREATE TABLE usuario (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY, -- Identificador del usuario

    nombre VARCHAR(100) NOT NULL, -- Nombre del usuario

    email VARCHAR(100) UNIQUE, -- Correo (no repetido)

    contraseña VARCHAR(255), -- Contraseña (recomendado encriptar)

    rol VARCHAR(50), -- Rol (admin, operador, etc)

    id_empresa INT, -- Empresa a la que pertenece

    -- Llave foránea
    CONSTRAINT fk_usuario_empresa
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa)
);

-- Tabla de vehículos
CREATE TABLE vehiculo (
    id_vehiculo INT AUTO_INCREMENT PRIMARY KEY, -- ID del vehículo

    placa VARCHAR(20) UNIQUE NOT NULL, -- Placa única

    tipo VARCHAR(50), -- Tipo de vehículo

    capacidad FLOAT, -- Capacidad de carga

    id_empresa INT, -- Empresa propietaria

    -- Relación con empresa
    CONSTRAINT fk_vehiculo_empresa
    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa)
);

-- Tabla principal del sistema (citas)
CREATE TABLE cita (
    id_cita INT AUTO_INCREMENT PRIMARY KEY,

    fecha_hora_inicio DATETIME NOT NULL,
    fecha_hora_fin DATETIME NOT NULL,

    estado VARCHAR(50) NOT NULL DEFAULT 'pendiente',
    tipo_cita VARCHAR(50),

    id_empresa INT NOT NULL,
    id_vehiculo INT NULL,

    id_usuario_crea INT NOT NULL,
    id_usuario_toma INT NULL,

    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_asignacion DATETIME NULL,

    FOREIGN KEY (id_empresa) REFERENCES empresa(id_empresa),
    FOREIGN KEY (id_vehiculo) REFERENCES vehiculo(id_vehiculo),
    FOREIGN KEY (id_usuario_crea) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_usuario_toma) REFERENCES usuario(id_usuario)
);



-- Tabla para cambios de citas
CREATE TABLE reasignacion (
    id_reasignacion INT AUTO_INCREMENT PRIMARY KEY, -- ID

    id_cita INT, -- Cita afectada

    fecha_reasignacion DATETIME, -- Fecha del cambio

    motivo VARCHAR(200), -- Motivo del cambio

    nueva_fecha_hora DATETIME, -- Nueva fecha

    id_usuario INT, -- Usuario que hizo el cambio

    -- Relaciones
    CONSTRAINT fk_reasignacion_cita
    FOREIGN KEY (id_cita) REFERENCES cita(id_cita),

    CONSTRAINT fk_reasignacion_usuario
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

DELIMITER $$

CREATE PROCEDURE insertar_empresa (
    IN p_nombre VARCHAR(100),
    IN p_tipo VARCHAR(50),
    IN p_direccion VARCHAR(150),
    IN p_telefono VARCHAR(20),
    IN p_email VARCHAR(100)
)
BEGIN
    INSERT INTO empresa(nombre, tipo_empresa, direccion, telefono, email)
    VALUES (p_nombre, p_tipo, p_direccion, p_telefono, p_email);

    SELECT 'Empresa registrada correctamente' AS mensaje;
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE insertar_usuario (
    IN p_nombre VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_contraseña VARCHAR(255),
    IN p_rol VARCHAR(50),
    IN p_id_empresa INT
)
BEGIN
    DECLARE existe INT;

    -- Validar correo duplicado
    SELECT COUNT(*) INTO existe
    FROM usuario
    WHERE email = p_email;

    IF existe > 0 THEN
        SELECT 'El correo ya está registrado' AS mensaje;
    ELSE
        INSERT INTO usuario(nombre, email, contraseña, rol, id_empresa)
        VALUES (p_nombre, p_email, p_contraseña, p_rol, p_id_empresa);

        SELECT 'Usuario creado correctamente' AS mensaje;
    END IF;

END $$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE crear_cita (
    IN p_inicio DATETIME,
    IN p_fin DATETIME,
    IN p_tipo VARCHAR(50),
    IN p_empresa INT,
    IN p_usuario_crea INT
)
BEGIN
    INSERT INTO cita (
        fecha_hora_inicio,
        fecha_hora_fin,
        estado,
        tipo_cita,
        id_empresa,
        id_usuario_crea,
        id_usuario_toma,
        id_vehiculo
    )
    VALUES (
        p_inicio,
        p_fin,
        'pendiente',
        p_tipo,
        p_empresa,
        p_usuario_crea,
        NULL,
        NULL
    );

    SELECT 'Cita creada correctamente' AS mensaje;
END $$

DELIMITER ;

drop procedure crear_cita;

DELIMITER $$

CREATE PROCEDURE tomar_cita (
    IN p_id_cita INT,
    IN p_usuario INT,
    IN p_vehiculo INT
)
BEGIN
    UPDATE cita
    SET 
        id_usuario_toma = p_usuario,
        id_vehiculo = p_vehiculo,
        estado = 'asignada',
        fecha_asignacion = NOW()
    WHERE id_cita = p_id_cita;

    SELECT 'Cita asignada correctamente' AS mensaje;
END $$

DELIMITER ;

DELIMITER $$

CREATE PROCEDURE reasignar_cita (
    IN p_id_cita INT,
    IN p_motivo VARCHAR(200),
    IN p_nueva_fecha DATETIME,
    IN p_usuario INT
)
BEGIN
    -- Insertar en historial
    INSERT INTO reasignacion(
        id_cita,
        fecha_reasignacion,
        motivo,
        nueva_fecha_hora,
        id_usuario
    )
    VALUES (
        p_id_cita,
        NOW(),
        p_motivo,
        p_nueva_fecha,
        p_usuario
    );

    -- Actualizar la cita
    UPDATE cita
    SET fecha_hora_inicio = p_nueva_fecha
    WHERE id_cita = p_id_cita;

    SELECT 'Cita reasignada correctamente' AS mensaje;
END $$

DELIMITER ;



DELIMITER $$

CREATE PROCEDURE insertar_vehiculo (
    IN p_placa VARCHAR(20),
    IN p_tipo VARCHAR(50),
    IN p_capacidad FLOAT,
    IN p_id_empresa INT
)
BEGIN
    -- 🚨 Validar placa duplicada
    IF EXISTS (SELECT 1 FROM vehiculo WHERE placa = p_placa) THEN
        SELECT 'Error: vehículo ya existe' AS mensaje;
    ELSE
        INSERT INTO vehiculo(placa, tipo, capacidad, id_empresa)
        VALUES (p_placa, p_tipo, p_capacidad, p_id_empresa);

        SELECT 'Vehículo creado correctamente' AS mensaje;
    END IF;
END $$

DELIMITER ;

DROP PROCEDURE IF EXISTS insertar_vehiculo;

-- lOgin usuario
DELIMITER $$

CREATE PROCEDURE login_usuario (
    IN p_email VARCHAR(100),
    IN p_password VARCHAR(255)
)
BEGIN
    SELECT id_usuario, nombre, rol
    FROM usuario
    WHERE email = p_email AND contraseña = p_password;
END $$

DELIMITER ;

-- insertar primer usuario y empresa

INSERT INTO empresa (nombre, tipo_empresa, direccion, telefono, email)
VALUES ('Empresa Demo', 'Generadora', 'Bogotá', '123456', 'empresa@test.com');

INSERT INTO usuario (nombre, email, contraseña, rol, id_empresa)
VALUES ('Admin', 'admin@admin.com', '123', 'admin', 1);





-- procedimeintos de eliminar
DELIMITER $$

CREATE PROCEDURE eliminar_empresa (
    IN p_id INT
)
BEGIN
    -- En vez de eliminar, se desactiva
    UPDATE empresa
    SET estado = 'inactiva'
    WHERE id_empresa = p_id;

    SELECT 'Empresa desactivada correctamente' AS mensaje;
END $$

DELIMITER ;

drop procedure eliminar_empresa;

DELIMITER $$

CREATE PROCEDURE eliminar_usuario (
    IN p_id INT
)
BEGIN
    DELETE FROM usuario
    WHERE id_usuario = p_id;

    SELECT 'Usuario eliminado correctamente' AS mensaje;
END $$

DELIMITER ;

-- procedimeinto de actualizar

DELIMITER $$

CREATE PROCEDURE actualizar_empresa (
    IN p_id INT,
    IN p_nombre VARCHAR(100),
    IN p_tipo VARCHAR(50),
    IN p_direccion VARCHAR(150),
    IN p_telefono VARCHAR(20),
    IN p_email VARCHAR(100)
)
BEGIN
    -- Actualiza los datos de la empresa según su ID
    UPDATE empresa
    SET 
        nombre = p_nombre,
        tipo_empresa = p_tipo,
        direccion = p_direccion,
        telefono = p_telefono,
        email = p_email
    WHERE id_empresa = p_id;

    -- Mensaje de confirmación
    SELECT 'Empresa actualizada correctamente' AS mensaje;
END $$

DELIMITER ;


DELIMITER $$

CREATE PROCEDURE actualizar_usuario (
    IN p_id INT,
    IN p_nombre VARCHAR(100),
    IN p_email VARCHAR(100),
    IN p_password VARCHAR(255),
    IN p_rol VARCHAR(50),
    IN p_id_empresa INT
)
BEGIN
    DECLARE existe INT;

    -- Validar que el correo no esté repetido en otro usuario
    SELECT COUNT(*) INTO existe
    FROM usuario
    WHERE email = p_email AND id_usuario != p_id;

    IF existe > 0 THEN
        SELECT 'El correo ya está en uso' AS mensaje;
    ELSE
        UPDATE usuario
        SET 
            nombre = p_nombre,
            email = p_email,
            contraseña = p_password,
            rol = p_rol,
            id_empresa = p_id_empresa
        WHERE id_usuario = p_id;

        SELECT 'Usuario actualizado correctamente' AS mensaje;
    END IF;

END $$

DELIMITER ;

-- activar empresa
DELIMITER $$

CREATE PROCEDURE activar_empresa (
    IN p_id INT
)
BEGIN
    UPDATE empresa
    SET estado = 'activa'
    WHERE id_empresa = p_id;

    SELECT 'Empresa activada nuevamente' AS mensaje;
END $$

DELIMITER ;



-- visualizar datos 

SELECT * FROM empresa
WHERE estado = 'activa';


SELECT * FROM usuario;

SELECT id_usuario, nombre, email, rol, id_empresa 
FROM usuario;

select * from cita;
select * from vehiculo;