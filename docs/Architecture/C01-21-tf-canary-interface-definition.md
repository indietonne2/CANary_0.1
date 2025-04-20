## Interface Definitions

### ScenarioManager ↔ CANManager
- `ScenarioManager.trigger_scenario(scenario_id: str)`
  - Calls CANManager to start simulation for a specific scenario.
  - Parameters:
    - `scenario_id`: Unique scenario identifier.
  - Returns: Status message or error.

### CANManager ↔ CarSimulator
- `CANManager.send_message(msg: CANMessage)`
  - Sends CANMessage object to CarSimulator for processing.
  - Parameters:
    - `msg`: Structured CAN message data.
  - Returns: Confirmation of message processing.

