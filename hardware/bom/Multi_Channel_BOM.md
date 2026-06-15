# Multi-Channel BOM (6–8 EML Channels)

This is an estimated BOM for a full motor driver supporting 6–8 EML channels with basic energy recovery and protection.

| Category              | Component                        | Qty (for 8 ch)     | Notes                              |
|-----------------------|----------------------------------|--------------------|------------------------------------|
| Microcontroller       | STM32F411 / STM32H7              | 1                  | Main controller                    |
| Gate Driver           | IR2110 or similar dual driver    | 4–8             | One per 1–2 channels              |
| Power MOSFETs         | IRLZ44N or SiC MOSFET            | 12–16           | 2 per channel (Main + Clamp)       |
| Current Sensors       | ACS712-20A or INA219             | 8                  | One per channel                    |
| Schottky Diodes       | MBR2045CT                        | 16                 | Protection per channel             |
| Storage Capacitors    | 2200µF 50V electrolytic          | 8–12             | Energy recovery storage            |
| Encoder               | 600–1000 PPR quadrature          | 1                  | Rotor position                     |
| Temperature Sensors   | NTC 10kΩ                         | 8–10             | Coil + MOSFET monitoring           |
| Power Supply          | 24V 10A+                         | 1                  | Main power                         |
| Protection            | Fuse, TVS diodes, current limit  | As needed          | System level protection            |

**Estimated Total Cost**: $180 – $350 (depending on component quality and sourcing).
