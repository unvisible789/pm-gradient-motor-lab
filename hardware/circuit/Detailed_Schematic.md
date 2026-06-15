# Detailed EML Driver Schematic Description

## Component-Level Connections (Single Channel)

### Power Section
- **+24V Main Rail** → Connected to:
  - Positive terminal of EML coil
  - Positive terminal of storage capacitors (C1, C2)
  - Input of gate driver (VCC pin via decoupling)

### Main Switching Path
- **EML Coil Negative Terminal** → Connected to:
  - Drain of Main MOSFET (Q1 - IRLZ44NPBF)
  - Cathode of Freewheeling Diode (D1 - MBR2045CT)

- **Source of Q1** → GND
- **Gate of Q1** → Output of Gate Driver (LO pin via 150Ω resistor)

### Active Clamp / Energy Recovery Path
- **Drain of Clamp MOSFET (Q2)** → Connected to:
  - Anode of Clamp Diode (D2)
  - Positive side of Storage Capacitors

- **Source of Q2** → GND
- **Gate of Q2** → Output of Gate Driver (HO pin via 150Ω resistor)

### Current Sensing
- **ACS712 Current Sensor** placed in series with EML coil (on the low side or high side).
- Output of ACS712 → ADC input of STM32

### Decoupling & Protection
- 0.1µF ceramic capacitor close to IR2110 VCC and GND pins.
- 10µF electrolytic capacitor on main 24V rail near the driver.
- Gate resistors (100–220Ω) on both MOSFET gates.

### Pin Connections (IR2110)
- VDD → 3.3V or 5V logic supply
- VCC → 12V or 15V (bootstrap supply)
- HIN → PWM signal from STM32 (High side)
- LIN → PWM signal from STM32 (Low side)
- HO → Gate of Q2 (via resistor)
- LO → Gate of Q1 (via resistor)
- VS → Connection between Q1 drain and coil

## Important Notes
- Use proper PCB layout for high current paths.
- Keep gate traces short.
- Add bulk capacitance near the power stage.
- Include test points for debugging (coil voltage, gate signals, current sense).
