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
- [Despliegue de producción en Ubuntu 24.04](docs/DESPLIEGUE-PRODUCCION.md)

## Estado actual

Sprint 2 implementa el ciclo completo del juego sobre el corte vertical del Sprint 1.
El administrador configura desafíos y elementos físicos; el participante inicia una
partida, resuelve la secuencia con pistas y tiempo límite y recibe su resultado.

> ESC03 (escaneo con cámara) permanece pendiente. Los códigos QR se ingresan
> manualmente en esta versión y no deben presentarse como escaneo implementado.

## Sprint 2

### Modelo

- `Desafio` pertenece a una experiencia y define orden, tipo (`texto`, `codigo` o
  `qr`), consigna, respuesta, pista, puntos y estado.
- `ElementoFisico` pertenece a una experiencia, tiene un identificador único dentro
  de ella y puede vincularse a un desafío.
- `Partida` guarda solo el estado necesario del recorrido: token público, desafío
  actual, inicio/finalización, estado, puntos y pistas utilizadas. No se almacenan
  datos personales.

La respuesta correcta solo forma parte de los endpoints administrativos. Los
contratos públicos de partida no la incluyen y toda validación ocurre en FastAPI.

### Endpoints

- `GET/POST /api/experiencias/{id}/desafios`
- `PUT /api/experiencias/{id}/desafios/{desafio_id}`
- `PUT /api/experiencias/{id}/desafios/orden`
- `GET/POST /api/experiencias/{id}/elementos`
- `PUT /api/experiencias/{id}/elementos/{elemento_id}`
- `POST /api/publico/experiencias/{codigo}/partidas`
- `GET /api/publico/partidas/{token}`
- `POST /api/publico/partidas/{token}/respuestas`
- `POST /api/publico/partidas/{token}/pista`

### Recorrido E2E

1. Crear una experiencia desde `/admin` y abrir `Configurar secuencia`.
2. Agregar y ordenar desafíos; opcionalmente registrar identificadores físicos y
   vincularlos a desafíos de tipo código o QR.
3. Activar la experiencia y abrir su enlace o QR de entrada.
4. Pulsar `Comenzar misión`, responder o ingresar manualmente identificadores,
   solicitar pistas y completar la secuencia antes del límite.
5. Ver el estado final, puntaje, desafíos resueltos y pistas utilizadas.

### Base de datos local

En desarrollo local, si no se define `DATABASE_URL`, el backend usa siempre
`stand_interactivo.db` en la raíz del repositorio. La ruta se calcula desde el código
y no depende del directorio desde el cual se ejecute uvicorn. El arranque usa
`Base.metadata.create_all` para agregar tablas faltantes, sin borrar ni recrear la
base existente.

Para iniciar el backend local sin configurar variables manualmente:

```powershell
cd backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

PostgreSQL continúa disponible indicando una URL explícita:

```powershell
$env:DATABASE_URL = "postgresql+psycopg://stand:stand@localhost:5432/stand_interactivo"
uvicorn app.main:app --reload
```

Los tests configuran `APP_ENV=test` antes de importar la aplicación y crean una base
SQLite temporal por ejecución. El fixture valida la ruta antes de cada `drop_all` y
rechaza expresamente `stand_interactivo.db`; no es necesario definir `DATABASE_URL`
para ejecutar pytest. No se debe eliminar ninguna base existente para aplicar este
Sprint.

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
