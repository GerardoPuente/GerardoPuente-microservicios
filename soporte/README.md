# Sistema de Soporte Técnico

**Equipo:** Gerardo Puente  
**Dominio:** Dominio 4 — Sistema de Soporte Técnico  
**Fecha:** Abril 2026

---

## ¿Qué problema resuelve?

Sistema para que los clientes reporten problemas técnicos y los equipos los rastreen hasta resolverlos. Permite abrir tickets, asignarlos a técnicos y actualizar su estado en tiempo real.

---

## Estructura de la Base de Datos

| Tabla | Descripción | Relación |
|-------|-------------|----------|
| tickets | Almacena cada reporte de soporte | Tabla principal |
| asignaciones | Registra qué técnico atiende cada ticket | FK → tickets.id |
| historial_estados | Guarda cada cambio de estado | FK → tickets.id |

---

## Rutas de la API

| Método | Ruta | Qué hace |
|--------|------|----------|
| GET | / | Interfaz HTML principal |
| POST | /tickets | Abre un nuevo ticket |
| GET | /tickets | Lista todos los tickets |
| GET | /tickets/abiertos | Tickets abiertos ordenados por prioridad |
| POST | /tickets/asignar | Asigna un ticket a un técnico |
| POST | /tickets/estado | Actualiza el estado de un ticket |

---

## ¿Cuál es la tarea pesada y por qué bloquea el sistema?

Al abrir un ticket, el sistema notifica al área técnica con un `time.sleep(5)` que simula el envío de alertas. En el monolito, este proceso bloquea el servidor completo — mientras se notifica un ticket, ningún otro usuario puede usar el sistema.

---

## Cómo levantar el proyecto

```bash
# 1. Clonar el repositorio
git clone [url]

# 2. Crear las tablas en RDS
mysql -h ENDPOINT_RDS -u admin -p < schema.sql

# 3. Construir la imagen
docker build -t soporte-app .

# 4. Correr el contenedor
docker run -d -p 5000:5000 \
  -e DB_HOST=ENDPOINT_RDS \
  -e DB_USER=admin \
  -e DB_PASSWORD=PASSWORD \
  -e DB_NAME=soporte_db \
  soporte-app

# 5. Abrir en navegador
http://IP_EC2:5000
```

---

## Decisiones técnicas

Las tres tablas se diseñaron para separar responsabilidades: `tickets` guarda el problema, `asignaciones` registra quién lo atiende y `historial_estados` permite auditar cada cambio. El manejo de errores con `try/except/finally` garantiza que las conexiones a BD siempre se cierren, evitando que se agote el pool de conexiones en RDS.
