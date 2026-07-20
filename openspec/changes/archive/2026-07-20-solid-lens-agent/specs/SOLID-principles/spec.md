## ADDED Requirements

### Requirement: Source code input
The system SHALL accept source code as a text string passed at invocation time. The system MUST detect the programming language from the code context or from an explicit language parameter.

#### Scenario: Accept valid source code
- **WHEN** the user provides a non-empty source code string
- **THEN** the system stores it in state for analysis

#### Scenario: Empty code input
- **WHEN** the user provides an empty source code string
- **THEN** the system SHALL return an error message and halt execution

### Requirement: Configuration injection
The system SHALL read Ollama base URL from the `OLLAMA_BASE_URL` environment variable. The system MUST accept `model` and `temperature` parameters at invocation to configure the LLM dynamically.

#### Scenario: Default configuration
- **WHEN** the user runs the pipeline without explicit model/temperature
- **THEN** the system uses `qwen3-coder:latest` as default model and `0.2` as default temperature

#### Scenario: Custom configuration
- **WHEN** the user provides `model="deepseek-coder:6.7b"` and `temperature=0.5`
- **THEN** the system instantiates ChatOllama with those exact parameters

### Requirement: SRP evaluation
The system SHALL analyze the source code for violations of the Single Responsibility Principle. Each class, module, or function MUST be evaluated for having more than one reason to change.

#### Scenario: Class with multiple responsibilities detected
- **WHEN** the source code contains a class handling persistence, business logic, and presentation
- **THEN** the system flags it as an SRP violation with justification and suggestion to split

#### Scenario: Clean single-responsibility class
- **WHEN** the source code contains a class with a single, well-defined responsibility
- **THEN** the system reports no SRP violations for that class

### Requirement: OCP evaluation
The system SHALL analyze the source code for violations of the Open/Closed Principle. Code MUST be evaluated for whether it is open for extension but closed for modification.

#### Scenario: Switch-based logic detected
- **WHEN** the source contains a large switch/if-else chain that requires modification to add new behavior
- **THEN** the system flags it as an OCP violation and suggests polymorphism or strategy pattern

### Requirement: LSP evaluation
The system SHALL analyze the source code for violations of the Liskov Substitution Principle. Inheritance hierarchies MUST be evaluated for whether subtypes are substitutable for their base types.

#### Scenario: Subtype that throws unexpected exceptions
- **WHEN** a subclass overrides a method and throws exceptions not thrown by the parent
- **THEN** the system flags it as an LSP violation

### Requirement: ISP evaluation
The system SHALL analyze the source code for violations of the Interface Segregation Principle. Interfaces MUST be evaluated for whether they force clients to depend on methods they don't use.

#### Scenario: Fat interface detected
- **WHEN** an interface defines methods that are irrelevant to some of its implementors
- **THEN** the system flags it as an ISP violation and suggests splitting the interface

### Requirement: DIP evaluation
The system SHALL analyze the source code for violations of the Dependency Inversion Principle. Dependencies MUST be evaluated for whether high-level modules depend on abstractions rather than concrete implementations.

#### Scenario: Concrete dependency detected
- **WHEN** a high-level module directly instantiates a concrete low-level class instead of depending on an abstraction
- **THEN** the system flags it as a DIP violation and suggests dependency injection

### Requirement: Report generation
The system SHALL produce a structured report containing: per-principle findings with severity (pass/warning/fail), justifications referencing specific code patterns, and actionable improvement suggestions.

#### Scenario: Complete report with mixed results
- **WHEN** all 5 principles have been evaluated (some pass, some fail)
- **THEN** the system outputs a markdown report with a summary table and per-principle detail sections

#### Scenario: Graceful error in one node
- **WHEN** one principle evaluation fails due to model error
- **THEN** the system SHALL record the error in state, continue with remaining principles, and note the failure in the report
