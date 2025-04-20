# MainWindow Class (c01-45_MainWindow)

## Overview
The `MainWindow` class is the central GUI container for the TFITPICAN Canary CAN‑Bus Simulator application. It subclasses `QMainWindow` and orchestrates all visual and interactive components—data streams, images with overlays, line‑graphs, selection fields, text fields, informational text, status indicators, and tab panels—into a cohesive user interface. Widgets are managed via factory methods for flexibility and future swapping.

## Use Case Diagram
```mermaid
usecaseDiagram
    actor User
    rectangle MainWindow {
      User -- (Launch Scenario)
      User -- (Select Widget)
      User -- (View Data Stream)
      User -- (Display Images)
      User -- (Monitor Status)
    }
```

## Class Diagram
```mermaid
classDiagram
    class MainWindow {
        -Logger logger
        -Configuration config
        -ScenarioManager scenarioManager
        -CANDataProcessor dataProcessor
        -Dictionary~String,QWidget~ widgets
        +__init__(config_path: str)
        +init_logging(): void
        +init_ui(): void
        +start_simulation(scenario_id: str): void
        +stop_simulation(): void
        +add_widget(widget: QWidget, position: WidgetPosition, name: str): void
        +update_status(msg: str, level: LogLevel): void
        +closeEvent(event: QCloseEvent): void
        -setup_menus(): void
        -layout_widgets(): void
        -create_car_display(): CarDisplayWidget
        -create_scenario_panel(): ScenarioPanelWidget
        -create_tab_panel(): TabPanelWidget
        -create_logger_view(): LoggerViewWidget
        -create_graph_view(): GraphViewWidget
        -connect_signals(): void
        -cleanup(): void
    }

    class WidgetPosition {
        <<enumeration>>
        TOP
        LEFT
        RIGHT
        BOTTOM
        CENTER
        TAB
    }

    class CarDisplayWidget {
        +highlight_area(area_id: str, color: QColor): void
        +clear_highlights(): void
        +update_overlay(data: Dict): void
    }

    class ScenarioPanelWidget {
        +set_scenarios(scenarios: List~Scenario~): void
        +get_selected_scenario(): str
    }

    class TabPanelWidget {
        +add_tab(widget: QWidget, name: str): void
        +set_current_tab(name: str): void
        +get_current_tab(): str
    }

    class LoggerViewWidget {
        +add_log_entry(timestamp: str, channel: str, flags: str, dlc: str, data: str): void
        +clear(): void
        +highlight_row(row_index: int, color: QColor): void
    }

    class GraphViewWidget {
        +add_data_point(series_id: str, x: float, y: float): void
        +clear_series(series_id: str): void
        +set_range(x_min: float, x_max: float, y_min: float, y_max: float): void
    }

    MainWindow *-- CarDisplayWidget
    MainWindow *-- ScenarioPanelWidget
    MainWindow *-- TabPanelWidget
    MainWindow *-- LoggerViewWidget
    MainWindow *-- GraphViewWidget
    MainWindow o-- WidgetPosition
```

## Component Layout
```mermaid
flowchart TB
    MW[MainWindow] --> MenuBar
    MW --> TopContainer
    MW --> BottomContainer
    MW --> StatusBar

    MenuBar --> FileMenu
    MenuBar --> SimulationMenu
    MenuBar --> ViewMenu
    MenuBar --> HelpMenu

    TopContainer --> ScenarioPanel
    TopContainer --> CarDisplay
    TopContainer --> RightSidebar

    RightSidebar --> LogButton
    RightSidebar --> SettingsButton

    BottomContainer --> TabPanel

    TabPanel --> LoggerTab
    TabPanel --> BluetoothTab
    TabPanel --> TranslationTab
    TabPanel --> ModeTab
    TabPanel --> UserTab

    StatusBar --> StatusLabel
    StatusBar --> VersionLabel
    
    style TopContainer fill:#bbf,stroke:#333
    style BottomContainer fill:#bbf,stroke:#333
    style TabPanel fill:#ddf,stroke:#333
```

## Initialization Sequence
```mermaid
sequenceDiagram
    participant Main as main.py
    participant MW as MainWindow
    participant Config as Configuration
    participant Logger as Logger
    participant ScenarioMgr as ScenarioManager

    Main->>MW: __init__(config_path)
    activate MW

    MW->>Config: __init__(config_path)
    activate Config
    Config-->>MW: config object
    deactivate Config

    MW->>MW: init_logging()
    MW->>Logger: setup_logger()
    Logger-->>MW: logger object

    MW->>MW: init_ui()
    MW->>MW: setup_menus()
    MW->>MW: create_scenario_panel()
    MW->>MW: create_car_display()
    MW->>MW: create_tab_panel()
    MW->>MW: layout_widgets()
    MW->>MW: connect_signals()

    MW->>MW: load_scenarios()
    activate ScenarioMgr
    MW->>ScenarioMgr: __init__(scenarios_path)
    ScenarioMgr-->>MW: loaded scenarios
    deactivate ScenarioMgr

    Main->>MW: show()
    deactivate MW
```

## Event Flow Diagram
```mermaid
stateDiagram-v2
    [*] --> Initialized: __init__()
    Initialized --> Ready: show()
    
    Ready --> LaunchingScenario: launch_scenario()
    LaunchingScenario --> SimulationRunning: start_simulation()
    SimulationRunning --> SimulationStopped: stop_simulation()
    SimulationStopped --> Ready: reset()
    
    SimulationRunning --> Recording: start_recording()
    Recording --> SimulationRunning: stop_recording()
    
    Ready --> ExportingData: export_data()
    ExportingData --> Ready: export_complete
    
    Ready --> [*]: closeEvent()
```

## Error Handling Strategy
```mermaid
flowchart TD
    Error[Error Occurs] --> Type{Error Type}
    
    Type -->|Configuration| ConfigError[Log Error and Load Defaults]
    Type -->|Scenario Loading| ScenarioError[Log Error and Show Dialog]
    Type -->|UI Creation| UIError[Log Error and Fallback to Basic UI]
    Type -->|Runtime| RuntimeError[Log Error and Continue]
    Type -->|Critical| CriticalError[Log Error and Exit]
    
    ConfigError --> Recovery
    ScenarioError --> Recovery
    UIError --> Recovery
    RuntimeError --> Recovery
    
    Recovery[Continue Operation]
    CriticalError --> Shutdown[Clean Shutdown]
```

## Responsibility Breakdown
```mermaid
pie
    title "MainWindow Responsibilities"
    "UI Initialization" : 25
    "Widget Management" : 20
    "Event Handling" : 15
    "Simulation Control" : 15
    "Logging" : 10
    "Configuration" : 10
    "Cleanup" : 5
```

## Data Flow
```mermaid
graph LR
    CAN[CAN Data Source] --> DP[Data Processor]
    DP --> MW[MainWindow]
    MW --> LV[Logger View]
    MW --> CD[Car Display]
    MW --> GV[Graph View]
    
    classDef source fill:#bbf,stroke:#333
    classDef processor fill:#ddf,stroke:#333
    classDef ui fill:#fbb,stroke:#333
    
    class CAN source
    class DP processor
    class MW,LV,CD,GV ui
```

## Menu Structure
```mermaid
mindmap
    root((Menus))
        File
            New Project
            Open Project
            Save
            Save As
            Exit
        Simulation
            Start Simulation
            Stop Simulation
            Record Data
            Stop Recording
        View
            Show Scenario Panel
            Show Graph View
        Help
            About
```

## Key Methods

### Constructor
```mermaid
graph LR
    A[__init__] --> B[Initialize attributes]
    B --> C[Load configuration]
    C --> D[Initialize logging]
    D --> E[Initialize UI]
    E --> F[Connect signals/slots]
```

### UI Initialization
```mermaid
graph TD
    A[init_ui] --> B[Create window & apply stylesheet]
    B --> C[Create main layout]
    C --> D[Create top container]
    D --> D1[Scenario panel]
    D --> D2[Car display]
    D --> D3[Right sidebar]
    C --> E[Create bottom container]
    E --> E1[Tab panel & add tabs]
    E1 --> E1a[Logger, Bluetooth, Translation, Mode, User]
    C --> F[Create status bar]
    F --> G[Setup menus]
```

### Signal Binding
```
tabPanel.currentChanged.connect(self.handle_tab_changed)
scenarioPanel.launchClicked.connect(self.launch_scenario)
dataProcessor.messageReceived.connect(self.on_can_message)
loggerView.clearRequested.connect(self.logger.clear)
```

### Scenario Launching
```mermaid
graph TD
    A[launch_scenario] --> B[Get selected scenario ID]
    B -->|No| C[Log warning]
    B -->|Yes| D[Fetch scenario object]
    D -->|Missing| E[Log error & alert]
    D -->|Found| F[Create DataProcessor]
    F --> G[Register listeners]
    G --> H[Start simulation]
    H --> I[Update status bar]
```

### Simulation Control
```mermaid
graph TD
    A[start_simulation] --> B{Data processor available?}
    B -->|No| C[Log warning]
    B -->|Yes| D[DP.start()]
    D --> E[Update status]
    
    F[stop_simulation] --> G{Data processor available?}
    G -->|No| H[Log warning]
    G -->|Yes| I[DP.stop()]
    I --> J[Update status]
```

## Widget Management

- **CarDisplayWidget** – Car visualization with area highlighting
- **ScenarioPanelWidget** – Scenario selection and launch controls
- **TabPanelWidget** – Tabbed interface for different views
- **LoggerViewWidget** – CAN message table with flags, DLC, data
- **GraphViewWidget** – Real‑time plots of selected signal series

```mermaid
graph TD
    MW[MainWindow] --> CD[CarDisplayWidget]
    MW --> SP[ScenarioPanelWidget]
    MW --> TP[TabPanelWidget]
    MW --> LV[LoggerViewWidget]
    MW --> GV[GraphViewWidget]
    
    SP -->|launchClicked| MW
    MW -->|on_can_message| LV
    MW -->|on_can_message| CD
    MW -->|on_can_message| GV
```

## Usage Example: Scenario Launch Sequence
```mermaid
sequenceDiagram
    participant User
    participant SP as ScenarioPanel
    participant MW as MainWindow
    participant SM as ScenarioManager
    participant DP as DataProcessor
    participant LV as LoggerView

    User->>SP: Select scenario + click Launch
    SP->>MW: launch_scenario(id)
    MW->>SM: get_scenario(id)
    SM-->>MW: scenario object
    MW->>DP: new DataProcessor(scenario)
    DP->>DP: register on_can_message
    MW->>DP: start_processing()
    DP->>LV: on_can_message(msg)
    DP->>CD: on_can_message(msg)
    DP->>GV: on_can_message(msg)
```

## Testing & CI

- **Unit Tests**: pytest-qt for widget init, signal/slot behavior
- **Integration Tests**: Offscreen Qt rendering in CI to verify layouts
- **Mocking**: Stub CAN sources for predictable message sequences
- **Coverage**: Target ≥ 80% on orchestration logic

## Implementation Details

### Coding Guidelines
- **Language**: Python 3.8+ with PyQt5/PySide2 (or equivalent)
- **Architecture**: MVC‑style separation; controllers handle logic, widgets handle presentation
- **Modularity**: WidgetFactory pattern for easy swapping
- **Dependency Injection**: Pass Configuration, Logger, and data sources into MainWindow

### Logging
- **Init**: init_logging() sets up console + rotating file handlers
- **Levels**: DEBUG (dev), INFO (runtime), WARNING/ERROR (issues)
- **Status Bar**: update_status() pushes to both status widget and logger

### Startup Sequence
1. Parse CLI args (config path, verbose flags)
2. Instantiate Logger
3. MainWindow = MainWindow(config_path)
4. MainWindow.start_simulation() if auto‑start
5. Enter Qt event loop

### Cross‑Platform Notes
- **macOS**: app.setAttribute(Qt.AA_UseHighDpiPixmaps) for Retina
- **Windows/Linux**: Bundle Qt plugins via pyinstaller or similar
- **Shortcuts & Styles**: Verify consistency on each OS
