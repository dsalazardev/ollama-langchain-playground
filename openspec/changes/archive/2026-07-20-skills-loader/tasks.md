## 1. Loader + Skill filosófico (sin romper nada)

- [x] 1.1 Crear `src/solid_lens/skills.py` con `list_skills()` y `load_skill()` con `@lru_cache`
- [x] 1.2 Crear `src/solid_lens/skills/` directorio
- [x] 1.3 Crear `src/solid_lens/skills/solid-principles.md` con frontmatter YAML y contenido filosófico
- [x] 1.4 Verificar que el loader funciona sin modificar nodes.py

## 2. Migrar prompts a .md + modificar nodes.py con fallback

- [x] 2.1 Crear `src/solid_lens/skills/srp.md` con frontmatter YAML y contenido completo
- [x] 2.2 Crear `src/solid_lens/skills/ocp.md`
- [x] 2.3 Crear `src/solid_lens/skills/lsp.md`
- [x] 2.4 Crear `src/solid_lens/skills/isp.md`
- [x] 2.5 Crear `src/solid_lens/skills/dip.md`
- [x] 2.6 Modificar `_analyze_principle()` en nodes.py: usar `load_skill(principle)` con fallback
- [x] 2.7 Smoke test: ejecutar pipeline y verificar reporte

## 3. Agregar skill filosófico como contexto base

- [x] 3.1 Modificar `_analyze_principle()`: agregar `load_skill("solid-principles")` como `SystemMessage` adicional
- [x] 3.2 Verificar que si `solid-principles.md` no existe, el análisis continúa sin error
- [x] 3.3 Smoke test: verificar que el análisis incluye contexto filosófico

## 4. Eliminar deuda: prompt "report" muerto

- [x] 4.1 Verificar que `SYSTEM_PROMPTS["report"]` nunca es invocado
- [x] 4.2 Eliminar `SYSTEM_PROMPTS["report"]` de `prompts.py`
- [x] 4.3 Smoke test: confirmar que `generate_report()` sigue produciendo reportes idénticos

## 5. Estabilizar y limpiar

- [x] 5.1 Verificar que los 5 .md existen y tienen contenido válido
- [x] 5.2 Verificar que `prompts.py` ya no es necesario
- [x] 5.3 Eliminar `src/solid_lens/prompts.py`
- [x] 5.4 Smoke test completo: pipeline corre sin `prompts.py`, reporte correcto
- [x] 5.5 Actualizar `README.md` con la nueva estructura de skills/
