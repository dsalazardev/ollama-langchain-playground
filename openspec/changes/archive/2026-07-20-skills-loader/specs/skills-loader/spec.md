## ADDED Requirements

### Requirement: Carga de skill existente
The system SHALL load the content of a `.md` file from the `skills/` directory when queried by its name (without extension). The content MUST be returned as a UTF-8 string.

#### Scenario: Carga exitosa de skill
- **WHEN** the system calls `load_skill("srp")` and `skills/srp.md` exists with valid UTF-8 content
- **THEN** the system returns the full text content of `skills/srp.md` as a string

### Requirement: Skill no encontrada → fallback
When a `.md` file does not exist for a requested skill name, the system MUST fall back to the corresponding entry in `SYSTEM_PROMPTS` dict from `prompts.py`.

#### Scenario: Fallback a prompts.py
- **WHEN** the system calls `load_skill("ocp")` and `skills/ocp.md` does not exist
- **THEN** the system catches `FileNotFoundError` and uses `SYSTEM_PROMPTS["ocp"]` as the prompt content instead

### Requirement: Carpeta skills/ vacía o inexistente
The system SHALL handle the case where the `skills/` directory is missing or empty without crashing.

#### Scenario: Directorio skills/ no existe
- **WHEN** the `skills/` directory is missing
- **THEN** `list_skills()` returns an empty list, and `load_skill()` raises `FileNotFoundError` which is caught by the fallback

#### Scenario: Directorio skills/ vacío
- **WHEN** the `skills/` directory exists but contains no `.md` files
- **THEN** `list_skills()` returns an empty list

### Requirement: Cache de skills
The system SHALL cache loaded skill content in memory to avoid repeated disk reads within the same process lifetime.

#### Scenario: Cache hit on repeated calls
- **WHEN** `load_skill("srp")` is called twice
- **THEN** the first call reads the file from disk, the second call returns the cached content without disk access

### Requirement: Skill filosófico como contexto base
The system SHALL load `solid-principles.md` (if it exists) and inject it as an additional `SystemMessage` before the principle-specific prompt in `_analyze_principle()`.

#### Scenario: Skill filosófico disponible
- **WHEN** `solid-principles.md` exists and `_analyze_principle()` is called
- **THEN** the messages list includes `SystemMessage(content=philosophy)` followed by `SystemMessage(content=skill_prompt)` and the `HumanMessage`

#### Scenario: Skill filosófico ausente
- **WHEN** `solid-principles.md` does not exist
- **THEN** the system silently skips the philosophy message and proceeds with only the principle-specific prompt

### Requirement: Eliminación de prompt "report" muerto
The system SHALL remove `SYSTEM_PROMPTS["report"]` as it is never invoked by any node in the graph.

#### Scenario: Prompt report eliminado
- **WHEN** `generate_report()` is called after removing the "report" prompt
- **THEN** the node still produces a valid markdown report from `state["results"]` without relying on any LLM prompt

### Requirement: Sistema funcional sin prompts.py
After full migration, the system SHALL operate correctly without `prompts.py`. All 5 principle prompts MUST be loadable from `.md` files.

#### Scenario: prompts.py eliminado
- **WHEN** `prompts.py` is deleted and all 5 `.md` files exist
- **THEN** the pipeline runs identically: same report format, same analysis quality, no import errors

## MODIFIED Requirements

### Requirement: SRP evaluation

#### Scenario: Class with multiple responsibilities detected
- **WHEN** the source code contains a class handling persistence, business logic, and presentation
- **THEN** the system flags it as an SRP violation with justification and suggestion to split

### Requirement: OCP evaluation

#### Scenario: Switch-based logic detected
- **WHEN** the source contains a large switch/if-else chain that requires modification to add new behavior
- **THEN** the system flags it as an OCP violation and suggests polymorphism or strategy pattern

### Requirement: LSP evaluation

#### Scenario: Subtype that throws unexpected exceptions
- **WHEN** a subclass overrides a method and throws exceptions not thrown by the parent
- **THEN** the system flags it as an LSP violation

### Requirement: ISP evaluation

#### Scenario: Fat interface detected
- **WHEN** an interface defines methods that are irrelevant to some of its implementors
- **THEN** the system flags it as an ISP violation and suggests splitting the interface

### Requirement: DIP evaluation

#### Scenario: Concrete dependency detected
- **WHEN** a high-level module directly instantiates a concrete low-level class instead of depending on an abstraction
- **THEN** the system flags it as a DIP violation and suggests dependency injection

## REMOVED Requirements

### Requirement: Report generation via LLM
**Reason**: The "report" system prompt was dead code. `generate_report()` assembles the markdown report manually from state data, never invoking the LLM for report generation.
**Migration**: No migration needed. The manual report generator produces identical output. The `SYSTEM_PROMPTS["report"]` entry is removed.
