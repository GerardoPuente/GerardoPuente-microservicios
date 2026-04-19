-- Sistema de Soporte Técnico
-- Equipo: Gerardo Puente

CREATE DATABASE IF NOT EXISTS soporte_db;
USE soporte_db;

-- Tabla 1: Tickets de soporte
CREATE TABLE IF NOT EXISTS tickets (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    cliente     VARCHAR(100) NOT NULL,
    titulo      VARCHAR(255) NOT NULL,
    descripcion TEXT,
    prioridad   ENUM('alta', 'media', 'baja') DEFAULT 'media',
    estado      ENUM('abierto', 'en_progreso', 'resuelto') DEFAULT 'abierto',
    creado_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla 2: Asignaciones de tickets a técnicos
CREATE TABLE IF NOT EXISTS asignaciones (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id   INT NOT NULL,
    tecnico     VARCHAR(100) NOT NULL,
    asignado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);

-- Tabla 3: Historial de cambios de estado
CREATE TABLE IF NOT EXISTS historial_estados (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id   INT NOT NULL,
    estado      VARCHAR(50) NOT NULL,
    cambiado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ticket_id) REFERENCES tickets(id)
);
