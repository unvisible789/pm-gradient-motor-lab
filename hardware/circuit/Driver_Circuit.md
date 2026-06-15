# EML Driver Circuit with Energy Recovery

## Recommended Topology

**Active Clamp Half-Bridge with Energy Recovery**

This topology allows pulsing the EML coils while recovering most of the stored magnetic energy instead of dissipating it as heat.

## Main Components

| Component          | Recommended Part     | Purpose                              |
|--------------------|----------------------|--------------------------------------|
| Main MOSFET (Q1)   | IRLZ44NPBF           | Switches current through EML coil    |
| Clamp MOSFET (Q2)  | IRLZ44NPBF           | Active clamp for energy recovery     |
| Gate Driver        | IR2110PBF            | Drives both MOSFETs with dead time   |
| Current Sensor     | ACS712-20A           | Monitors coil current                |
| Freewheeling Diode | MBR2045CT            | Protects against voltage spikes      |
| Storage Caps       | 1000µF–4700µF 50V | Stores recovered energy              |

## Basic Operation

1. Main MOSFET (Q1) turns ON → Current flows through EML coil.
2. Main MOSFET turns OFF → Energy in coil is directed into clamp capacitor via Q2 path.
3. Stored energy can be reused for next pulse or fed back to supply.

## Text-Based Schematic Overview

```
+24V ----[EML Coil]---- Q1 (Main MOSFET) ---- GND
               |
               +---- Diode ---- Q2 (Clamp) ---- Storage Cap ---- GND
```

## Key Design Notes

- Use proper gate resistors (100–220Ω).
- Add dead time between Q1 and Q2 switching.
- Keep high-current paths short and thick.
- Decouple power supply close to the driver.
