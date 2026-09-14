# Plan de pruebas

## Criterio de finalización

Una historia sólo termina cuando todos sus criterios de aceptación fueron comprobados y existe evidencia.

## Niveles

- Pruebas unitarias para reglas de validación, tiempo, puntaje y recompensas.
- Pruebas de integración para aplicación, API y persistencia.
- Pruebas de recorrido desde un teléfono para cada incremento demostrable.
- Regresión dirigida sobre historias terminadas que puedan verse afectadas.
- Prueba integral del MVP antes del tag `sprint-3-entrega`.

## Evidencia mínima

- Resultado automatizado cuando corresponda.
- Captura o video del comportamiento visible.
- Enlace al commit o Pull Request puntual.
- Registro del defecto en **BUGS / MEJORAS** si el resultado no coincide con lo esperado.

## Escenarios críticos del MVP

1. El QR abre la experiencia activa desde un teléfono.
2. Las instrucciones y la duración son visibles antes de iniciar.
3. Una respuesta correcta habilita el desafío siguiente.
4. Una respuesta incorrecta informa el error sin perder la sesión.
5. El participante puede solicitar una pista.
6. El temporizador finaliza la experiencia según la configuración.
7. El resultado, los puntos y la recompensa se calculan al finalizar.
8. La sesión registra inicio, fin, avances, pistas y resultado.

