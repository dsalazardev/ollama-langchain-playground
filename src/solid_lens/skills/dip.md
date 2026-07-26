---
name: dip
description: Evalúa violaciones del Principio de Inversión de Dependencias (DIP) en código fuente
---

# DIP — Dependency Inversion Principle

"Los módulos de alto nivel no deben depender de módulos de bajo nivel. Ambos deben depender de abstracciones." — Robert C. Martin

## Señales de violación

- Instanciación directa de clases concretas dentro de clases de alto nivel
- Dependencias de módulos externos específicos sin interfaz intermedia
- Código de negocio acoplado a infraestructura (base de datos, API, sistema de archivos)
- Falta de inyección de dependencias en constructores
- Dificultad para hacer pruebas unitarias (no se puede mockear)

## Cómo evaluar

1. Identificá qué objetos crea directamente cada clase (con `new` o constructores)
2. Preguntate: "Si cambio la implementación concreta, ¿cuánto código debo modificar?"
3. Si la respuesta es más de un archivo → posible violación DIP
4. Verificá si las dependencias se inyectan desde afuera o se construyen adentro

## Formato de respuesta

ESTADO: aprobado|advertencia|fallo
HALLAZGOS: <descripción del problema o confirmación de buena práctica>
SUGERENCIAS: <sugerencia de mejora accionable>

## Reglas

- Respondé ÚNICA y EXCLUSIVAMENTE en español
- Si no hay violaciones, usá ESTADO: aprobado
- Incluí referencias a líneas o patrones específicos del código
- Las sugerencias deben ser accionables
