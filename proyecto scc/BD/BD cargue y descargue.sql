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

DELIMITER //

CALL validar_usuario('sebas', '12234');

