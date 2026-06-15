# Bill of Materials - Single EML Channel Prototype

This BOM is for building and testing **one EML driver channel** with basic energy recovery.

| Qty | Component                        | Recommended Part          | Notes                              | Est. Price (USD) |
|-----|----------------------------------|---------------------------|------------------------------------|------------------|
| 1   | Microcontroller Board            | STM32F411 Black Pill      | Main controller                    | $6–8            |
| 2   | N-Channel MOSFET (Logic Level)   | IRLZ44NPBF                | Main + Clamp switches              | $1.50 each       |
| 1   | Gate Driver IC                   | IR2110PBF                 | Dual channel gate driver           | $2.50            |
| 1   | Current Sensor                   | ACS712-20A                | Hall-effect current sensing        | $2–3            |
| 2   | Schottky Diode                   | MBR2045CT                 | Freewheeling protection            | $1 each          |
| 2   | Electrolytic Cap 1000µF 50V     | -                         | Energy storage                     | $1 each          |
| 1   | Quadrature Encoder               | 600 PPR Optical           | Rotor position sensing             | $12–18          |
| 1   | NTC Thermistor 10kΩ             | -                         | Temperature sensing                | $0.50            |
| 1   | Prototyping PCB / Perfboard      | -                         | Assembly                           | $3–5            |
| 1   | 24V Power Supply (5A+)           | Mean Well LRS-150-24      | Main power                         | $20–25          |

**Total Estimated Cost**: $55 – $85
