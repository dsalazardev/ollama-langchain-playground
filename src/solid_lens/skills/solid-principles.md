---
name: solid-principles
description: Contexto filosófico y heurísticas generales de los principios SOLID para análisis de código
---

# Principios SOLID — Filosofía y Heurísticas

Robert C. Martin consolidó SOLID a principios de los 2000. Los cinco principios responden a: ¿por qué los sistemas OO se vuelven rígidos, frágiles e inmóviles?

## Heurísticas generales

- Antes de agregar un método, preguntate si introduce una NUEVA razón de cambio (SRP)
- Preferí una clase nueva antes que un if más en un switch (OCP)
- Desconfiá de jerarquías con NotImplementedError en subclases (LSP)
- Rompé interfaces gordas cuando un cliente solo usa 3 de 10 métodos (ISP)
- Inyectá dependencias en el constructor; no construyas colaboradores concretos adentro (DIP)

## Cuándo NO aplicar SOLID

- Scripts de una sola ejecución
- Prototipos de investigación
- Funciones puras pequeñas donde la abstracción cuesta más que el beneficio

SOLID es para código que va a vivir y cambiar, no para código que nace para morir.
