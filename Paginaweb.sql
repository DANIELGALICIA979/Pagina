CREATE DATABASE paginaweb;
USE paginaweb;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL
);

-- Tabla de datos socioeconómicos y solicitud
CREATE TABLE IF NOT EXISTS formularios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    curp VARCHAR(18) UNIQUE NOT NULL,
    edad INT,
    genero ENUM('Masculino', 'Femenino', 'Otro'),
    estado_civil VARCHAR(50),
    nivel_educativo VARCHAR(100),
    ocupacion VARCHAR(100),
    ingresos_mensuales DECIMAL(10,2),
    integrantes_hogar INT,
    tipo_vivienda VARCHAR(100),
    zona ENUM('Rural', 'Urbana'),
    servicios_basicos VARCHAR(200),
    situacion_salud VARCHAR(200),
    dependientes_economicos INT,
    telefono VARCHAR(15),
    direccion VARCHAR(255),
    motivo_solicitud TEXT,
    status ENUM('En revisión', 'Aprobado', 'Denegado') DEFAULT 'En revisión',
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla de documentos oficiales (guardaremos la ruta o nombre del archivo)
CREATE TABLE IF NOT EXISTS documentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    ine_path VARCHAR(255),
    comprobante_domicilio_path VARCHAR(255),
    fecha_subida TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabla de historial de apoyos otorgados
CREATE TABLE historial_apoyos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    fecha_apoyo DATE,
    descripcion TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);



-- SE EJECUTA DESDE AQUI 
DELIMITER $$

CREATE TRIGGER agregar_historial_despues_update
AFTER UPDATE ON formularios
FOR EACH ROW
BEGIN
    -- Solo registrar si el status cambia
    IF NEW.status <> OLD.status THEN
        INSERT INTO historial_apoyos (usuario_id, fecha_apoyo, descripcion)
        VALUES (NEW.usuario_id, CURDATE(), 
            CONCAT('Cambio de estatus a: ', NEW.status)
        );
    END IF;
END $$

DELIMITER ;
-- HASTA AQUI POR SI NO PUEDEN XD