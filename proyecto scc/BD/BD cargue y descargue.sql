Create database descargue;
Use descargue;
Create table Usuario(
Id INT auto_increment primary key,
Nombre varchar (100) Not null,
Apellido varchar(100) Not null,
Cedula INT not null,
Usuario varchar(100) not null,
Contraseña varchar(255) not null,
Fecha_registro timestamp default current_timestamp
);

insert into Usuario (Nombre,Apellido,Cedula,Usuario,Contraseña)
values ('Sebastian','olave',11111111,'sebas','12234');

select * from Usuario;

DELIMITER //

create procedure validar_usuario (
in p_usuario varchar(100),
in p_contraseña varchar(255)
)
Begin

Select Id, Nombre, Apellido, Usuario
from Usuario
where Usuario=p_usuario
and Contraseña=P_contraseña;

end//

DELIMITER //;

CALL validar_usuario('sebas', '12234');

-- mostrar usuarios read--
Select * from Usuario;

-- procedimeinto de agregar--

delimiter $$
create procedure agregar (
in p_Nombre varchar(100),
in p_Apellido varchar(100),
in p_Cedula int,
in p_Usuario varchar(100),
in p_Contraseña varchar(255)
)

begin
 
 declare existe int;
 
 Select count(*) into existe
 from Usuario
 where Cedula=p_Cedula;
 
 if existe =0 then 
 insert into Usuario(Nombre,Apellido,Cedula,Usuario,Contraseña)
 values(p_Nombre,p_Apellido,p_Cedula,p_Usuario,p_Contraseña);
 
 else
 select 'el usuario ya exite' As mensaje;
 end if;
 end $$
 
 delimiter ;
 
DROP PROCEDURE IF EXISTS agregar;
 
 -- Actualizar usuario --
 
 DELIMITER $$

CREATE PROCEDURE actualizar_usuario (
    IN p_Cedula INT,
    IN p_Nombre VARCHAR(100),
    IN p_Apellido VARCHAR(100),
    IN p_Usuario VARCHAR(100),
    IN p_Contraseña VARCHAR(255)
)
BEGIN

    DECLARE existe INT;

    -- Validar duplicado (otra cédula igual, no la misma)
    SELECT COUNT(*) INTO existe
    FROM Usuario
    WHERE Cedula = p_Cedula;

    IF existe > 0 THEN

        UPDATE Usuario
        SET 
            Nombre = p_Nombre,
            Apellido = p_Apellido,
            Usuario = p_Usuario,
            Contraseña = p_Contraseña
        WHERE Cedula = p_Cedula;

        SELECT 'Actualizado correctamente' AS mensaje;

    ELSE
        SELECT 'La cédula no existe' AS mensaje;

    END IF;

END$$

DELIMITER ;
 
 
 DROP PROCEDURE IF EXISTS actualizar_usuario;
 
 
 -- eliminar --
 
DELIMITER $$

CREATE PROCEDURE eliminar_usuario (
    IN p_Cedula INT
)
BEGIN

    DECLARE existe INT;

    -- Verificar si existe la cédula
    SELECT COUNT(*) INTO existe
    FROM Usuario
    WHERE Cedula = p_Cedula;

    IF existe > 0 THEN

        DELETE FROM Usuario
        WHERE Cedula = p_Cedula;

        SELECT 'Usuario eliminado correctamente' AS mensaje;

    ELSE
        SELECT 'La cédula no existe' AS mensaje;

    END IF;

END$$

DELIMITER ;
 
 