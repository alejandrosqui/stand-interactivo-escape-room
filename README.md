# Stand interactivo con mini escape room

Proyecto académico de **(2138) Laboratorio de Desarrollo de Software 2026**.

Aplicación web móvil para un stand de eventos que combina desafíos digitales con elementos físicos. La experiencia objetivo dura entre 3 y 7 minutos y permite medir las interacciones de los participantes.

## Objetivo del MVP

Permitir que una persona:

1. descubra la propuesta del stand;
2. ingrese mediante un código QR;
3. complete una misión física-digital con pistas y tiempo límite;
4. reciba un resultado, puntos y una recompensa;
5. genere un registro básico de su participación.

El administrador podrá configurar la experiencia, los desafíos, las respuestas, las pistas, los elementos físicos y la recompensa sin modificar el código.

## Plan de entregas

| Sprint | Objetivo | Resultado |
| --- | --- | --- |
| 1 | Inicio y configuración mínima | Experiencia publicada e ingreso por QR |
| 2 | Ciclo completo del juego | Secuencia con validación, pistas y tiempo límite |
| 3 | Recompensa y trazabilidad | MVP liberable |
| 4 | Mejoras y análisis | Versión 1.1 |

## Documentación

- [User Story Map](docs/USER-STORY-MAP.md)
- [Reglas de trabajo con GitHub](docs/TRAZABILIDAD-GITHUB.md)
- [Plan de pruebas](docs/PLAN-DE-PRUEBAS.md)
- [ADR-001: arquitectura inicial](docs/ADR-001-ARQUITECTURA-INICIAL.md)

## Estado actual

Sprint 1 en desarrollo. El primer corte vertical permite crear una experiencia
desde el panel, activarla y abrirla como participante mediante código o QR.

## Ejecutar localmente

Requisitos: Docker Desktop con Docker Compose.

```bash
docker compose up --build
```

- Aplicación: http://localhost:5173
- Panel: http://localhost:5173/admin
- API: http://localhost:8000
- Documentación interactiva: http://localhost:8000/docs

Para detener los servicios:

```bash
docker compose down
```

Los datos de PostgreSQL se conservan en el volumen `stand_db`.

## Validaciones

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements-dev.txt
$env:DATABASE_URL = "sqlite:///./test_stand.db"
.venv/Scripts/python -m pytest -q tests

cd ../frontend
npm install
npm run build
```

## Trazabilidad

- Cada commit de implementación debe comenzar con el código de la historia: `VIS02: implementa acceso por QR`.
- El checklist **Evidencias** de Trello debe enlazar el commit o Pull Request puntual.
- Al cerrar cada sprint se crea y publica el tag `sprint-N-entrega`.
- La tarjeta de entrega debe adjuntar el tag y un video o capturas de la aplicación funcionando.

## Equipo

- Alejandro Villarroel
