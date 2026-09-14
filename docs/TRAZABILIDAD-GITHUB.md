# Trazabilidad entre Trello y GitHub

## Commit por historia

Cada commit de implementación incluye el código de la historia:

```text
VIS02: implementa acceso a la experiencia mediante QR
ESC04: valida las respuestas ingresadas
ADM01: agrega creación de experiencias
```

No se usa el enlace general del repositorio como evidencia. En Trello se adjunta el enlace al commit o Pull Request puntual.

## Cierre de sprint

Sólo cuando el sprint esté cerrado y probado:

```bash
git tag sprint-N-entrega
git push origin sprint-N-entrega
```

La tarjeta de entrega debe adjuntar:

1. enlace al tag o release, obligatorio;
2. video o capturas de la aplicación funcionando, obligatorio;
3. build o despliegue, opcional.

## Flujo mínimo

1. Mover la HU a **EN DESARROLLO**.
2. Implementar con commits identificados.
3. Mover a **EN PRUEBAS**.
4. Ejecutar los criterios de aceptación y regresión relacionada.
5. Adjuntar evidencias.
6. Pasar a **TERMINADO** sólo con criterios al 100 %.

