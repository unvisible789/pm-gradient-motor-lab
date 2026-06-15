# Sensor and Data Acquisition Plan

## Required Measurements (Minimum for Phase 0 + Phase 1)

| Measurement              | Sensor / Method                  | Resolution / Accuracy Target | Notes |
|--------------------------|----------------------------------|------------------------------|-------|
| Rotor Angle (0-45°)      | Quadrature encoder or high-quality printed degree wheel + pointer | 0.5° or better              | Manual first, encoder later |
| Tangential Force / Torque| Load cell (5-50 kg) + HX711 or NAU7802 ADC | 0.1 N or better             | Fixed lever arm; calculate torque = F × r |
| Coil Voltage             | Differential probe or voltage divider + oscilloscope/DAQ | 0.1 V                       | Across EML terminals |
| Coil Current             | Hall current sensor (ACS712 or better) or shunt + amplifier | 10 mA                       | In series with coil |
| Bus Voltage              | Voltage divider + ADC            | 0.1 V                       | Main supply rail |
| Recovery Capacitor Voltage | Voltage divider + ADC          | 0.1 V                       | Critical for energy recovery validation |
| Gate Drive Signal        | Oscilloscope probe               | -                           | Timing verification |
| Temperature (coils, MOSFETs, magnets) | NTC thermistors or thermocouples + ADC | 0.5 °C                    | Multiple points; log over time |

## DAQ / Logging Options (Low Cost First)

1. **ESP32 or Arduino + HX711** (lowest cost)
   - Good for angle + force logging.
   - Limited simultaneous high-speed channels.
2. **USB Oscilloscope / DAQ** (e.g., cheap 4-channel USB scope or Analog Discovery style)
   - Best for simultaneous coil voltage, current, gate, recovery voltage.
   - Export CSV for analysis.
3. **STM32 + multiple ADCs** (higher performance)
   - Good balance; can log everything at reasonable sample rates.

## Data to Capture and Compare to FEMM
- Torque vs angle (0-45° in 1° or 2° steps).
- Integrated work over 45° (area under torque-angle curve).
- Repeatability across 5+ manual sweeps.
- Measurement uncertainty budget (sensor specs + mechanical tolerances + repeatability).

## Energy Recovery Specific
- Recovered energy must be measured as **energy returned to usable storage** (change in capacitor voltage over known capacitance), **not** just voltage spike suppression.
- Log recovery capacitor voltage before and after each pulse or sweep.

## Grounding and Isolation
- Use differential measurement where possible for coil voltage/current.
- Avoid ground loops between scope/DAQ, controller, and power supply.
- Consider isolated USB if using PC-connected DAQ with high-side sensing.
- Clearly label all grounds and reference points in schematics and lab notes.