# C01-36‑tf‑canary‑ScenarioManager

Controls the lifecycle and execution of scenarios in the Canary CAN‑Bus Simulator.

---

## 1. Overview of `ScenarioManager`

**Purpose:**  
`ScenarioManager` is responsible for controlling the entire lifecycle of test scenarios: loading, initializing, execution control, logging, and cleanup.

### Responsibilities
- **Load & parse** scenario definitions (XML/JSON/TOML).  
- **Initialize** environment (CAN interfaces, virtual nodes, timers).  
- **Control execution**: start, pause, resume, stop, reset.  
- **Dispatch events** to listeners (UI, logger, metrics).  
- **Log** state changes, errors, performance metrics.  
- **Provide status/query API**.  
- **Ensure deterministic timing** across platforms.

### High‑Level Logic
1. **Load** scenario → validate → build in‑memory model  
2. **Initialize** resources → configure CAN buses  
3. **Start** loop → tick timer → execute steps  
4. **Pause/Resume** → maintain offsets  
5. **Handle Errors** → transition to ERROR + cleanup  
6. **Stop/Reset** → release + optionally reload  

---

## 2. UML Use‑Case Diagram

```mermaid
usecaseDiagram
  actor User
  actor "External Tool" as Tool

  User --> (Load Scenario)
  User --> (Start Scenario)
  User --> (Pause Scenario)
  User --> (Resume Scenario)
  User --> (Stop Scenario)
  User --> (Query Status)

  Tool --> (Subscribe to Events)
  Tool --> (Fetch Logs)

