# Architecture Documentation v0.1.3

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Interface Definitions (C01-21-tf-canary-interface-definition)](#interface-definitions)
4. [Module Descriptions](#module-descriptions)
   - 4.1 [PlatformDetector](#platformdetector)
   - 4.2 [VenvSetup](#venvsetup)
   - 4.3 [PixiEnvironment](#pixienvironment)
   - 4.4 [LoggingSystem](#loggingsystem)
   - 4.5 [CLI](#cli)
   - 4.6 [ConfigurationManager](#configurationmanager)
   - 4.7 [SQLiteDB](#sqlitedb)
   - 4.8 [ScenarioLoader](#scenarioloader)
   - 4.9 [ScenarioValidator](#scenariovalidator)
   - 4.10 [ScenarioManager](#scenariomanager)
   - 4.11 [CarSimulator](#carsimulator)
   - 4.12 [CANInterfaceFactory](#caninterfacefactory)
   - 4.13 [VirtualCANInterface](#virtualcaninterface)
   - 4.14 [HardwareCANInterface](#hardwarecaninterface)
   - 4.15 [CANManager](#canmanager)
   - 4.16 [CANVisualizer](#canvisualizer)
   - 4.17 [MainWindow](#mainwindow)
5. [Data Model Documentation (C01-22-tf-canary-data-model-documentation)](#data-model-documentation)
6. [Cross-Cutting Concerns (C01-23-tf-canary-cross-cutting-concerns)](#cross-cutting-concerns)
7. [Component State Diagrams (C01-26-scenarioManagerStates)](#component-state-diagrams)
8. [Additional Documentation](#additional-documentation)
9. [Diagrams](#diagrams)

---

## 1. Introduction

This updated architecture documentation provides a comprehensive overview of the TF-Canary project, detailing system architecture, module interactions, data models, cross-cutting concerns, and state diagrams. It emphasizes detailed interface definitions, logging, testing, and operational modes.

## 2. System Overview

TF-Canary is a robust CAN-bus simulation platform supporting GUI and CLI. It integrates scenario management, virtual/hardware CAN interfaces, real-time visualization, comprehensive testing, and centralized logging, with three operational modes: Workshop (Kiosk), Default, and User.

```plantuml
@include "docs/diagrams/architecture/system_overview.puml"
```

## 3. Interface Definitions (C01-21-tf-canary-interface-definition)

```markdown
@include "docs/descriptions/C01-21-tf-canary-interface-definition.md"
```

## 4. Module Descriptions

### 4.1 PlatformDetector
Detects operating system and hardware to configure the environment accordingly.

### 4.2 VenvSetup
Creates a Python virtual environment ensuring dependency consistency.

### 4.3 PixiEnvironment
Manages cross-platform dependencies for the application.

### 4.4 LoggingSystem
Centralized logging framework providing structured and persistent logs.

### 4.5 CLI
Facilitates command-line operations and modular testing.

### 4.6 ConfigurationManager
Loads and manages configurations via environment variables and files.

### 4.7 SQLiteDB
Persistent storage solution offering CRUD operations for scenarios and settings.

### 4.8 ScenarioLoader
Fetches and prepares scenarios from the SQLite database.

### 4.9 ScenarioValidator
Ensures scenario data integrity and correctness before execution.

### 4.10 ScenarioManager
Controls the lifecycle and execution of scenarios.

### 4.11 CarSimulator
Simulates vehicle dynamics and responses to CAN messages.

### 4.12 CANInterfaceFactory
Selects and initializes appropriate CAN interfaces (virtual or hardware).

### 4.13 VirtualCANInterface
Provides simulated CAN-bus interactions for testing purposes.

### 4.14 HardwareCANInterface
Interfaces with physical CAN-bus hardware devices.

### 4.15 CANManager
Manages CAN data flows between interfaces, simulation, and visualization.

### 4.16 CANVisualizer
Displays real-time CAN-bus data in graphical form.

### 4.17 MainWindow
Central GUI container integrating all visual and interactive components.

## 5. Data Model Documentation (C01-22-tf-canary-data-model-documentation)

```markdown
@include "docs/descriptions/C01-22-tf-canary-data-model-documentation.md"
```

## 6. Cross-Cutting Concerns (C01-23-tf-canary-cross-cutting-concerns)

```markdown
@include "docs/descriptions/C01-23-tf-canary-Cross-Cutting-Concerns.md"
```

## 7. Component State Diagrams (C01-26-scenarioManagerStates)

```plantuml
@include "docs/diagrams/architecture/c01-26-ScenarioManagerStates.puml"
```

## 8. Additional Documentation

### Makefile (C01-24-tf-canary-makefile)
```makefile
@include "docs/descriptions/C01-24-tf-canary-makefile.mk"
```

### Pixi.toml (C01-25-tf-canary-pixi.toml)
```toml
@include "docs/descriptions/C01-25-tf-canary-pixi.toml"
```

## 9. Diagrams

### Dependency Development Chart (c01-13)
```plantuml
@include "docs/diagrams/architecture/c01-13_Dependency_Development_Chart.puml"
```

### Context Diagram (c01-15)
```plantuml
@include "docs/diagrams/architecture/c01-15 context diagram.puml"
```

### Component Diagram (c01-16)
```plantuml
@include "docs/diagrams/architecture/c01-16 component diagram.puml"
```

### Sequence Diagram: Initialization (c01-17)
```plantuml
@include "docs/diagrams/architecture/c01-17 sequenz initialisation.puml"
```

### Deployment Diagram (c01-18)
```plantuml
@include "docs/diagrams/architecture/c01-18 deployment diagram.puml"
```

### Architecture Diagram (c01-19)
```plantuml
@include "docs/diagrams/architecture/c01-19_architecture_diagram_puml"
```

### Sequence Diagram: CAN Message Flow (c01-20)
```plantuml
@include "docs/diagrams/architecture/c01-20_CAN_Message_Flow.puml"
```


