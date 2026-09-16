# ADR-001 - Arquitectura inicial del MVP

- Estado: Aceptada
- Fecha: 2026-09-16

## Contexto

El Sprint 1 necesita demostrar un recorrido móvil y un panel de administración sin incorporar todavía ranking, NFC, sensores ni analítica avanzada.

## Decisión

- React, TypeScript y Vite para la aplicación web adaptable a móviles.
- FastAPI para la API REST.
- PostgreSQL como base de datos de producción.
- SQLite sólo para pruebas automatizadas aisladas.
- Docker Compose para reproducir backend y base de datos.
- La entrada mediante QR contiene una URL con el código público de la experiencia.

## Consecuencias

El equipo puede validar el corte vertical con infraestructura pequeña y reutilizar el mismo backend en los sprints siguientes. El panel no tendrá autenticación durante el primer corte; antes de un despliegue público deberá incorporarse control de acceso.

