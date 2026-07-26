---
name: lsp
description: Evalúa violaciones del Principio de Sustitución de Liskov (LSP) en código fuente
---

# LSP — Liskov Substitution Principle

"Los objetos de un programa deberían ser reemplazables por instancias de sus subtipos sin alterar el correcto funcionamiento del programa." — Barbara Liskov

## Señales de violación

- Subclases que lanzan excepciones no declaradas en la clase base
- Métodos sobrescritos que ignoran parámetros o devuelven tipos diferentes
- Clases que heredan pero dejan métodos con `pass` o `NotImplementedError`
- Condicionales que verifican el tipo concreto antes de llamar a un método
- Precondiciones más fuertes o postcondiciones más débiles en la subclase

## Cómo evaluar

1. Identificá jerarquías de herencia en el código
2. Preguntate: "¿Puedo usar cualquier subclase donde espero la clase base sin saber cuál es?"
3. Si el código tiene `isinstance` para decidir el comportamiento → posible violación LSP
4. Verificá que las subclases no rompan las expectativas del contrato de la clase base

## Formato de respuesta

ESTADO: aprobado|advertencia|fallo
HALLAZGOS: <descripción del problema o confirmación de buena práctica>
SUGERENCIAS: <sugerencia de mejora accionable>

## Reglas

- Respondé ÚNICA y EXCLUSIVAMENTE en español
- Si no hay violaciones, usá ESTADO: aprobado
- Incluí referencias a líneas o patrones específicos del código
- Las sugerencias deben ser accionables
