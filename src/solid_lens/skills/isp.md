---
name: isp
description: Evalúa violaciones del Principio de Segregación de Interfaces (ISP) en código fuente
---

# ISP — Interface Segregation Principle

"Ningún cliente debería ser forzado a depender de métodos que no usa." — Robert C. Martin

## Señales de violación

- Interfaces con muchos métodos donde la mayoría de implementaciones dejan varios sin implementar
- Clases que lanzan `NotImplementedError` o `pass` en métodos heredados
- Interfaces "gordas" que mezclan operaciones no relacionadas
- Clientes que reciben una interfaz completa pero solo usan una fracción

## Cómo evaluar

1. Identificá interfaces o clases base abstractas
2. Preguntate: "¿Cada implementación usa TODOS los métodos definidos?"
3. Si alguna implementación deja métodos vacíos o lanza excepciones → violación ISP
4. Verificá si dividir la interfaz en varias más pequeñas tendría sentido

## Formato de respuesta

ESTADO: aprobado|advertencia|fallo
HALLAZGOS: <descripción del problema o confirmación de buena práctica>
SUGERENCIAS: <sugerencia de mejora accionable>

## Reglas

- Respondé ÚNICA y EXCLUSIVAMENTE en español
- Si no hay violaciones, usá ESTADO: aprobado
- Incluí referencias a líneas o patrones específicos del código
- Las sugerencias deben ser accionables
