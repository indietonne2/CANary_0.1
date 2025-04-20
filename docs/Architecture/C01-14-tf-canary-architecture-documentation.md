# Architecture Documentation v0.1.2

## Table of Contents

1. [Introduction](#introduction)
2. [System Overview](#system-overview)
3. [Module Descriptions](#module-descriptions)
   - [PlatformDetector](#platformdetector)
   - [VenvSetup](#venvsetup)
   - [PixiEnvironment](#pixienvironment)
   - [LoggingSystem](#loggingsystem)
   - [CLI](#cli)
   - [ConfigurationManager](#configurationmanager)
   - [SQLiteDB](#sqlitedb)
   - [ScenarioLoader](#scenarioloader)
   - [ScenarioValidator](#scenariovalidator)
   - [ScenarioManager](#scenariomanager)
   - [CarSimulator](#carsimulator)
   - [CANInterfaceFactory](#caninterfacefactory)
   - [VirtualCANInterface](#virtualcaninterface)
   - [HardwareCANInterface](#hardwarecaninterface)
   - [CANManager](#canmanager)
   - [CANVisualizer](#canvisualizer)
   - [MainWindow](#mainwindow)
4. [Diagrams](#diagrams)
   - [Context Diagram](#context-diagram)
   - [Component Diagram](#component-diagram)
   - [Sequence Diagram: Initialization](#sequence-diagram-initialization)
   - [Sequence Diagram: CAN Message Flow](#sequence-diagram-can-message-flow)
   - [Architecture Diagram](#architecture-diagram)

---

## Introduction

This updated document provides a refined architecture overview for the TF-Canary project, detailing modules, their responsibilities, and interactions, emphasizing logging, testing, and mode-specific configurations. It includes updated PlantUML diagrams reflecting the current design.

## System Overview

TF-Canary is a CAN-bus simulation platform designed with GUI and CLI support. The system integrates scenario management, virtual/hardware CAN interfaces, real-time visualization, and comprehensive testing and logging capabilities. It supports three operational modes: Workshop (Kiosk), Default, and User.

## Module Descriptions

### PlatformDetector

Detects OS and hardware at startup, setting appropriate configurations.

### VenvSetup

Creates a Python virtual environment to manage consistent dependencies.

### PixiEnvironment

Manages package dependencies, tailored to different hardware platforms.

### LoggingSystem

Provides centralized logging, error tracking, and persistent log handling.

### CLI

Offers command-line interaction for module testing and operation validation.

### ConfigurationManager

Manages application configurations from environment variables and files.

### SQLiteDB

Provides persistent storage with CRUD capabilities for scenarios and configurations.

### ScenarioLoader

Loads predefined scenarios from the SQLite database.

### ScenarioValidator

Validates scenarios for data consistency and correctness.

### ScenarioManager

Controls the lifecycle and management of scenarios.

### CarSimulator

Simulates vehicle dynamics and ECU behaviors in response to CAN messages.

### CANInterfaceFactory

Selects appropriate CAN interfaces based on detected hardware or virtual environment.

### VirtualCANInterface

Simulates CAN-bus interactions for testing purposes.

### HardwareCANInterface

Interfaces with physical CAN-bus hardware, including Raspberry Pi CAN shields and USB adapters.

### CANManager

Coordinates the data flow between scenarios, CAN interfaces, and car simulation.

### CANVisualizer

Visualizes real-time CAN-bus data streams within the GUI.

### MainWindow

Integrates GUI components, real-time data visualization, and user interactions.

## Diagrams

### [c01-15] Context Diagram v0.1.1

```plantuml
@startuml C01-20_ContextDiagram
actor User
node "TF-Canary Application" {
  component MainWindow
  component CANManager
  component ScenarioManager
  component CarSimulator
  component CLI
  component LoggingSystem
}
database "SQLiteDB"
actor CANHardware
actor VirtualCAN

User --> MainWindow : interact
User --> CLI : execute commands
MainWindow --> ScenarioManager : select scenario
ScenarioManager --> SQLiteDB : load scenario
ScenarioManager --> CANManager : trigger CAN data
CANManager --> CarSimulator : inputs
CarSimulator --> CANManager : outputs
CANManager --> CANHardware : hardware interface
CANManager --> VirtualCAN : virtual interface
CANManager --> LoggingSystem : log activities
CANManager --> MainWindow : update GUI
@enduml
```

### [c01-16] Component Diagram v0.1.1

```plantuml
@startuml C01-21_ComponentDiagram
package "Core Setup" {
  component PlatformDetector
  component VenvSetup
  component PixiEnvironment
  component LoggingSystem
  component CLI
}
package "Persistence" {
  component ConfigurationManager
  component SQLiteDB
  component ScenarioLoader
  component ScenarioValidator
}
package "Simulation & Visualization" {
  component ScenarioManager
  component CarSimulator
  component CANManager
  component CANVisualizer
}
package "Interfaces" {
  component CANInterfaceFactory
  component VirtualCANInterface
  component HardwareCANInterface
}
package "GUI Layer" {
  component MainWindow
}

PlatformDetector --> ConfigurationManager
ConfigurationManager --> SQLiteDB
ScenarioLoader --> SQLiteDB
ScenarioValidator --> ScenarioLoader
ScenarioManager --> ScenarioValidator
MainWindow --> ScenarioManager
MainWindow --> CANVisualizer
CLI --> all
LoggingSystem --> all
CANInterfaceFactory --> VirtualCANInterface
CANInterfaceFactory --> HardwareCANInterface
CANManager --> CANInterfaceFactory
CANManager --> ScenarioManager
CANManager --> CarSimulator
@enduml
```

### [c01-17] Sequence Diagram: Initialization v0.1.1

```plantuml
@startuml C01-22_InitSequence
participant PD as PlatformDetector
participant VS as VenvSetup
participant PX as PixiEnvironment
participant LS as LoggingSystem
participant CM as ConfigurationManager
participant DB as SQLiteDB
participant SL as ScenarioLoader
participant SV as ScenarioValidator
participant SM as ScenarioManager
participant MW as MainWindow

PD -> VS : setup venv
VS -> PX : configure Pixi
PX -> LS : initialize logging
LS -> CM : load config
CM -> DB : init database
DB -> SL : load scenarios
SL -> SV : validate scenarios
SV -> SM : setup scenarios
SM -> MW : initialize GUI
@enduml
```

### [c01-20] Sequence Diagram: CAN Message Flow v0.1.1

```plantuml
@startuml C01-20_CANFlow
participant SM as ScenarioManager
participant CMgr as CANManager
participant VCI as VirtualCANInterface
participant HCI as HardwareCANInterface
participant CS as CarSimulator
participant CV as CANVisualizer
participant LS as LoggingSystem

SM -> CMgr : start scenario
CMgr -> CS : simulate inputs
CS --> CMgr : generate output
CMgr -> VCI : virtual send
CMgr -> HCI : hardware send
CMgr -> CV : update visualization
CMgr -> LS : log CAN activity
@enduml
```

### [c01-19] Architecture Diagram v0.1.2

```plantuml
@startuml
skinparam backgroundColor #fdf6e3
skinparam nodeStyle rectangle

Title "[c01-19] TF-Canary Architecture Diagram v0.1.2 (Including Modes, Logging, and Testing)"

package "Environment & Core Setup" {
  node "1. PlatformDetector" as PD
  node "2. VenvSetup" as VS
  node "3. PixiEnvironment" as PE
  node "4. LoggingSystem" as LS
  node "5. CLI" as CLI
}

package "Configuration & Data Persistence" {
  node "6. ConfigurationManager" as CM
  node "7. SQLiteDB" as DB
  node "8. ScenarioLoader" as SL
  node "9. ScenarioValidator" as SV
}

package "Scenario & Simulation Logic" {
  node "10. ScenarioManager" as SM
  node "11. CarSimulator" as CS
}

package "Testing Infrastructure" {
  node "12. TestRunner & Pytest" as TR
  node "13. Unit & Integration Tests" as UIT
}

package "CAN Interface & Hardware Abstraction" {
  node "14. CANInterfaceFactory" as CIF
  node "15. VirtualCANInterface" as VCI
  node "16. HardwareCANInterface" as HCI
  node "17. SelfTest" as ST
}

package "CAN Data Management & Visualization" {
  node "18. CANManager" as CANM
  node "19. CANMessageInterpreter" as CMI
  node "20. CANVisualizer" as CV
}

package "GUI Layer & ECU Visualization" {
  node "21. MainWindow" as MW
  node "22. CANVisualizerWidget" as CVW
  node "23. ECUOverlayManager" as EOM
}

package "Connectivity & Advanced Functions" {
  node "24. BluetoothManager" as BM
  node "25. SimulatorNetwork" as SN
}

package "Metrics, Users & Security" {
  node "26. MetricsAggregator" as MA
  node "27. UserManager" as UM
  node "28. AccessControl" as AC
}

package "Error Handling, Documentation & Final Testing" {
  node "29. ErrorManager" as EM
  node "30. DocumentationGenerator" as DG
  node "31. SystemTests" as SYST
}

package "Deployment & Packaging" {
  node "32. PixiConfig & PackageArtifacts" as PA
}

package "Operational Modes" {
  node "Workshop Mode (Kiosk)" as WM
  node "Default Mode" as DM
  node "User Mode" as USM
}

PD --> VS
VS --> PE
PE --> LS
LS --> CLI
CLI --> CM
CM --> DB
DB --> SL
SL --> SV
SV --> SM
SM --> CS
CS --> CANM
CANM --> CIF
CIF --> VCI
CIF --> HCI
HCI --> ST
CANM --> CMI
CMI --> CV
CV --> CVW
CVW --> MW
MW --> EOM
EOM --> BM
BM --> SN
SN --> MA
MA --> UM
UM --> AC
AC --> EM
EM --> DG
DG --> SYST
SYST --> PA

WM --> MW
DM --> MW
USM --> MW

@enduml
```


