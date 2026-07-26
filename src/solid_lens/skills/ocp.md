---
name: ocp
description: Evalúa violaciones del Principio Abierto/Cerrado (OCP) en código fuente
---

# OCP — Open/Closed Principle

"Las entidades de software deben estar abiertas para extensión, pero cerradas para modificación." — Bertrand Meyer

## Señales de violación

- Cadenas switch/if-else que requieren modificación para agregar nuevo comportamiento
- Múltiples condiciones anidadas basadas en un tipo o enumeración
- Métodos que crecen con cada nueva funcionalidad en lugar de delegar
- Parches en código existente para soportar nuevos casos

## Cómo evaluar

1. Buscá condicionales que inspeccionen el tipo o estado de un objeto
2. Preguntate: "Si agrego un nuevo tipo, ¿cuántos archivos tengo que modificar?"
2. Si la respuesta es más de uno → posible violación OCP
3. Verificá si el código se puede extender heredando/componiendo sin tocar lo existente

## Formato de respuesta

ESTADO: aprobado|advertencia|fallo
HALLAZGOS: <descripción del problema o confirmación de buena práctica>
SUGERENCIAS: <sugerencia de mejora accionable>

## Reglas

- Respondé ÚNICA y EXCLUSIVAMENTE en español
- Si no hay violaciones, usá ESTADO: aprobado
- Incluí referencias a líneas o patrones específicos del código
- Las sugerencias deben ser accionables
