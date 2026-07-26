---
name: srp
description: Evalúa violaciones del Principio de Responsabilidad Única (SRP) en código fuente
---

# SRP — Single Responsibility Principle

"Una clase debe tener una sola razón para cambiar." — Robert C. Martin

## Señales de violación

- Clases que mezclan persistencia, lógica de negocio y presentación
- Métodos públicos que orquestan múltiples operaciones no relacionadas
- Clases con más de 5-7 métodos públicos que operan en distintos dominios
- Métodos que mezclan cálculo, I/O y logging en el mismo bloque

## Cómo evaluar

1. Identificá cada clase/función en el código
2. Preguntate: "Si cambio X, ¿cuántas cosas se rompen?"
3. Si hay más de una razón de cambio → violación SRP
4. Documentá qué responsabilidades específicas están mezcladas

## Formato de respuesta

ESTADO: aprobado|advertencia|fallo
HALLAZGOS: <descripción del problema o confirmación de buena práctica>
SUGERENCIAS: <sugerencia de mejora accionable>

## Reglas

- Respondé ÚNICA y EXCLUSIVAMENTE en español
- Si no hay violaciones, usá ESTADO: aprobado
- Incluí referencias a líneas o patrones específicos del código
- Las sugerencias deben ser accionables: "Extraé la lógica de X a una nueva clase Y"
