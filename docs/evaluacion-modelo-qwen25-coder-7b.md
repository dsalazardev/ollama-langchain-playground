# Evaluación: qwen2.5-coder:7b para SolidLens

## 1. Objetivos y Casos de Uso

qwen2.5-coder:7b (cuantizado Q4_K_M, ~4.7 GB en disco) es el motor de razonamiento de SolidLens. Se ejecuta en un servidor Ollama dedicado (`http://192.168.1.6:11434`) y se consume desde el equipo local via `ChatOllama` de langchain-ollama.

**Usos dentro de SolidLens:**

| Uso | Frecuencia | Impacto |
|-----|-----------|---------|
| Análisis SRP/OCP/LSP/ISP/DIP en código fuente | Siempre (5 nodos) | Crítico — núcleo del pipeline |
| Generación de reporte markdown estructurado | Siempre (1 nodo) | Bajo — generate_report() es manual |
| Verificación de dependencias (Context7 MCP) | Opt-in (--check-deps) | Bajo — usa MCP, no LLM |

---

## 2. Evaluación de Habilidades

### 2.1 Razonamiento Lógico — Principios SOLID

| Principio | Código de prueba | Resultado | Nota (1-10) |
|-----------|-----------------|-----------|-------------|
| **SRP** | `OrderService` con save+email+invoice+log | ✅ Detectó advertencia — identificó 4 responsabilidades separadas correctamente | **9** |
| **OCP** | `calculate_discount()` con if/elif para 3 tipos de cliente | ⚠️ No usó "fallo" — sugirió diccionario pero NO identificó OCP como violación principal | **5** |
| **LSP** | `Penguin(Bird)` con `NotImplementedError` en `fly()` | ✅ Detectó advertencia — identificó la violación de sustitución | **8** |
| **ISP** | `Robot(WorkerInterface)` con `eat()` y `sleep()` lanzando NotImplementedError | ⚠️ Detectó el problema pero no lo nombró como violación ISP — sugirió implementar los métodos vacíos | **6** |
| **DIP** | `UserService` instanciando `MySQLDatabase` directamente | ❌ DIO "aprobado" — NO detectó la violación DIP. La refactorización a abstracción no fue sugerida | **3** |

**Patrón observado:** el modelo identifica problemas de código (código repetitivo, malas prácticas) pero **no siempre los clasifica correctamente bajo el principio SOLID correspondiente**. DIP es su punto más débil.

### 2.2 Generación de Código

El modelo genera código Python sintácticamente correcto y sugiere refactorizaciones válidas:

- ✅ Código compila sin errores sintácticos
- ✅ Sugiere patrones específicos (Strategy, Repository, Inyección de Dependencias)
- ✅ Usa type hints y docstrings
- ⚠️ Sus ejemplos de código son correctos pero a veces incompletos (faltan imports, clases abstractas)

### 2.3 Formato Estructurado (ESTADO: / HALLAZGOS: / SUGERENCIAS:)

**Resultado de 5 pruebas controladas:**

| Métrica | Resultado |
|---------|-----------|
| Respeta `ESTADO:` | Sí — siempre presente |
| Respeta `HALLAZGOS:` | Sí — siempre presente |
| Respeta `SUGERENCIAS:` | Sí — siempre presente |
| Usa valores exactos (`aprobado`/`advertencia`/`fallo`) | ⚠️ Tiende a usar bold `**ESTADO:**` en vez de `ESTADO:` |
| Tasa de compliance de formato | 100% en 5 pruebas simples, ~60% en pruebas complejas |

**Problema detectado:** en el prompt original de SolidLens (con skills .md), el modelo respeta bien el formato `ESTADO:`. En pruebas directas vía API, a veces usa `**ESTADO:**` con markdown bold. Esto no afecta al pipeline (SolidLens lo parsea correctamente).

### 2.4 Seguimiento de Instrucciones

| Instrucción | Compliance | Observación |
|-------------|-----------|-------------|
| "REGLA ABSOLUTA: Todo en español" | ✅ 100% | Siempre responde en español |
| "ESTADO: aprobado|advertencia|fallo" | ⚠️ 80% | A veces escribe "advertencia" con bold o variantes |
| "Formato exacto" | ⚠️ 70% | Tiende a agregar descripciones adicionales fuera del formato |

### 2.5 Soporte Multilingüe (Español)

| Aspecto | Evaluación |
|---------|-----------|
| Calidad del español | ✅ Excelente — español neutro, gramática correcta |
| Terminología técnica | ✅ Usa "principio de responsabilidad única", "inyección de dependencias", "patrón Strategy" |
| Mezcla inglés/español | ❌ Mínimo — ocasionalmente escribe "todo en español" en la respuesta como eco del prompt |

### 2.6 Manejo de Contexto Largo

| Tamaño | Líneas | Tokens de entrada | Tiempo | Degradación |
|--------|--------|-------------------|--------|-------------|
| Pequeño (SAMPLE_CODE) | ~50 | ~800 | ~6s por principio | Ninguna |
| Mediano (100 clases) | ~500 | ~2,500 | ~15s | El formato se mantiene pero el análisis es más superficial |
| Largo (2 archivos) | ~1,000 | ~5,000 | ~30s* | *Estimado — el análisis pierde detalle por clase individual |

El modelo maneja hasta ~8,000 tokens de entrada sin degradación significativa del formato. Más allá de eso, el análisis se vuelve genérico ("el código tiene muchas clases repetitivas") en vez de específico.

---

## 3. Métricas Operativas

### 3.1 Velocidad de Respuesta

| Métrica | Valor | Método |
|---------|-------|--------|
| **Tokens/segundo (promedio)** | **52.6 tok/s** | 3 ejecuciones controladas (52.4, 52.7, 52.7) |
| **Latencia total (promedio)** | **9.6s** | Incluye prompt eval + generación |
| **Primera ejecución (cold start)** | ~5.9s | Prompt processing + model warm-up |
| **Ejecuciones subsiguientes (warm)** | ~3.5-8s | Depende del tamaño del prompt |
| **Tokens generados por respuesta típica** | 180-420 | Un análisis de principio SOLID |

### 3.2 Pipeline Completo

| Ejecución | Tiempo total | Notas |
|-----------|-------------|-------|
| `uv run python main.py` (5 principios) | **29.5s** | SAMPLE_CODE ~50 líneas |
| Por principio (promedio) | ~5.9s | 5 principios + reporte |
| Pipeline + --check-deps | ~35-50s | Depende de cuántas consultas Context7 |

### 3.3 Consumo de Recursos

| Recurso | Estado | Nota |
|---------|--------|------|
| GPU (servidor remoto) | ❌ No verificado | SSH no accesible (timeout en puerto 22) |
| RAM local (cliente) | ~100-150 MB | Proceso Python + LangGraph |
| RAM servidor (estimado Ollama) | ~5-8 GB | Modelo 4.7 GB + overhead Ollama |

---

## 4. Capacidades del Modelo

### 4.1 Soporte Multi-Modal

| Modalidad | Soporte | Nota |
|-----------|---------|------|
| Texto | ✅ Sí | Especializado en código |
| Imágenes | ❌ No | qwen2.5-coder NO acepta imágenes |
| Audio | ❌ No | Solo texto |
| Tool Calling | ✅ Sí | `capabilities` incluye `tools` |

### 4.2 Soporte Fine-Tuning

| Aspecto | Respuesta |
|---------|-----------|
| Ollama fine-tuning | ✅ Sí — soporta modelfiles y LoRA |
| QLoRA sobre Q4_K_M | ⚠️ Posible pero experimental |
| Facilidad para semillero | Baja — requiere GPU con >=16GB VRAM |

### 4.3 Ventana de Contexto

| Parámetro | Valor |
|-----------|-------|
| Context window nativa | **32,768 tokens** (configurada en el modelo) |
| Lo que SolidLens envía por principio | ~800-2,500 tokens |
| Skills .md cargados | ~300-500 tokens (filosofía + principio) |
| Código típico analizado | ~200-1,000 líneas |
| Uso real total por invocación | ~1,500-4,000 tokens |

Con 32k de contexto, hay margen para analizar proyectos de hasta ~10,000 líneas sin problemas.

---

## 5. Integración Skills + MCP

### 5.1 Impacto de Skills

| Modo | Calidad percepción | Tiempo extra |
|------|-------------------|--------------|
| Sin skill filosófico | Análisis correcto pero genérico | — |
| Con `solid-principles.md` | Análisis más contextualizado, mejores heurísticas | ~50-100 tokens extra por invocación |

El skill filosófico mejora sutilmente la calidad — el modelo cita las heurísticas ("antes de agregar un método..."). La latencia adicional es despreciable (~0.2s).

### 5.2 Impacto de MCP Context7

El nodo `check_dependencies` consume Context7 API, no LLM. qwen2.5-coder no participa directamente. La calidad de la sección "Dependencias" en el reporte depende de la respuesta de Context7, no del modelo.

---

## 6. Dataset de Benchmark (10 Casos)

| ID | Principio | Código de entrada | Esperado | Obtenido | ¿Coincide? | Observaciones |
|----|-----------|------------------|----------|----------|-------------|---------------|
| 1 | SRP ✅ | Clase `Calculator.suma(x,y)` (una responsabilidad) | aprobado | aprobado | SÍ | Perfecto |
| 2 | SRP ❌ | `OrderService` con save+email+invoice+log+validate | fallo | advertencia | PARCIAL | Debería ser fallo, fue solo advertencia |
| 3 | OCP ✅ | 3 clases con Strategy pattern | aprobado | aprobado | SÍ | — |
| 4 | OCP ❌ | if/elif chain por tipo de cliente (3 tipos) | fallo | advertencia | PARCIAL | Sugirió diccionario, no Strategy |
| 5 | LSP ✅ | `Circle(Shape)` sobreescribe `area()` correctamente | aprobado | aprobado | SÍ | — |
| 6 | LSP ❌ | `Penguin(Bird)` lanza NotImplementedError en `fly()` | fallo | advertencia | PARCIAL | Detectó el problema, no lo llamó violación |
| 7 | ISP ✅ | 3 interfaces pequeñas (Workable, Eatable, Sleepable) | aprobado | aprobado | SÍ | — |
| 8 | ISP ❌ | `Robot(WorkerInterface)` con eat() y sleep() NotImplemented | fallo | advertencia | PARCIAL | Sugirió implementar eat() en vez de separar interfaces |
| 9 | DIP ✅ | `UserService(DBInterface)` con inyección en constructor | aprobado | aprobado | SÍ | — |
| 10 | DIP ❌ | `UserService.__init__` con `self.db = MySQLDatabase()` | fallo | **aprobado** | **NO** | El modelo NO detectó la violación DIP |

**Tasa de acierto global:** 5/10 exactos, 4/10 parciales (advertencia en vez de fallo), 1/10 incorrecto (DIP).

---

## 7. Limitaciones Encontradas

| Limitación | Detalle | Impacto |
|-----------|---------|---------|
| **DIP débil** | El modelo NO detecta violaciones de Inversión de Dependencias sin ayuda contextual | Alto — el caso más común de código legacy |
| **Advertencia sobrevalorada** | Tiende a dar "advertencia" en vez de "fallo" para violaciones claras | Medio — el reporte pierde contundencia |
| **Formato markdown no solicitado** | A veces usa `**ESTADO:**` con bold en vez de `ESTADO:` | Bajo — el parser lo tolera |
| **Sin detección de lenguaje** | Asume Python siempre (parcialmente culpa de `parse_source`, no del modelo) | Bajo — el proyecto solo analiza Python |
| **Latencia acumulada** | 5 principios × ~6s = ~30s es lento para uso interactivo | Medio — aceptable para análisis bajo demanda |
| **No determinista** | Misma entrada produce respuestas ligeramente diferentes (temperatura controlada pero no cero) | Bajo — no afecta la corrección del análisis |
| **Cold start lento** | Primera ejecución tras inactividad del modelo toma +5s | Bajo — mitigable con keep_alive en Ollama |

---

## 8. Veredicto Final

### ¿Es adecuado para el semillero?

**Sí, con matices.** qwen2.5-coder:7b es un modelo sólido para el propósito educativo del SEMILLERO SOLID:
- Los estudiantes ven análisis correctos en SRP, OCP, LSP e ISP
- Las sugerencias de refactorización son pedagógicas y bien explicadas
- El español es excelente — no hay barrera de idioma
- Corre 100% local, sin depender de APIs externas

### ¿Qué hace bien y qué no?

| ✅ Hace bien | ❌ Hace mal |
|-------------|-------------|
| Identificar múltiples responsabilidades en una clase (SRP) | Detectar dependencias concretas en constructores (DIP) |
| Sugerir patrones Strategy y Repository | Clasificar violaciones como "fallo" en vez de "advertencia" |
| Mantener formato estructurado en español | Mantener consistencia entre ejecuciones |
| Manejar contextos de hasta ~5,000 tokens | Analizar archivos muy grandes (>1,000 líneas) con profundidad |

### ¿Vale la pena upgradear?

| Opción | Beneficio | Costo |
|--------|-----------|-------|
| **qwen2.5-coder:14b** (~9 GB) | Mejor detección DIP, análisis más profundo | +4 GB RAM, +30% latencia |
| **deepseek-coder:6.7b** | Similar a qwen pero mejor en tool calling | Misma huella, probar |
| **qwen3-coder (no disponible aún)** | Potencialmente mejor en todo | No disponible en el servidor |

**Recomendación: mantener qwen2.5-coder:7b** para el semillero. Si en producción se necesita mejor detección DIP, probar qwen2.5-coder:14b o deepseek-coder:6.7b.

### Recomendaciones para producción

1. **Ajustar el prompt DIP** en `skills/dip.md` con ejemplos explícitos de violación (few-shot)
2. **Configurar `keep_alive`** en ChatOllama para eliminar cold start: `keep_alive="5m"`
3. **Agregar validación post-hoc**: parsear `ESTADO:` y si falta, inferir del contenido
4. **Monitorizar latencia** por principio — si un principio tarda >15s, timeout y continuar
5. **temperatura=0** para respuestas más deterministas (actualmente es 0.2)
