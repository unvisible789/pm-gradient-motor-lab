# Safety Plan - Prototype Development

## General Principles
- Start small and simple.
- Current-limit everything during early testing.
- Never work alone on high-power tests.
- Have a clear emergency procedure and exit path.

## Minimum Safety Equipment (Required Before Any Powered Testing)

- Emergency stop button (big red mushroom) that cuts main power via contactor or relay.
- Fuses or circuit breakers on all power rails (main supply and branches).
- Current-limited bench DC supply (0-30V, 5A+ with adjustable current limit).
- Safety glasses and closed-toe shoes.
- Fire extinguisher rated for electrical fires (Class C or ABC) within reach.
- Clear workspace with no trip hazards.

## Mechanical Safety
- Full guarding around rotating parts (clear acrylic or polycarbonate shields).
- No loose clothing, hair, or jewelry near rotating shaft.
- Secure test fixture to bench or heavy base plate.
- Use non-magnetic fasteners and tools near strong permanent magnets.

## Electrical Safety
- Low voltage first (start at 5-12V for logic and initial power stage tests).
- Add series resistance or current limit when first powering inductive loads.
- Use properly rated wire and connectors for expected currents.
- Keep high-voltage / high-current sections physically separated from logic sections where possible.
- Discharge capacitors safely before handling (bleeder resistors + verification).

## Thermal Safety
- Monitor coil, MOSFET, and recovery capacitor temperatures continuously during testing.
- Set conservative temperature limits and automatic shutdown if possible.
- Allow adequate cooling time between test runs.
- Have thermal camera or IR thermometer available for spot checks.

## Recommended Test Sequence
1. Bench power supply only + dummy resistive load.
2. Add inductive dummy load + verify recovery behavior.
3. Low-voltage powered test on real EML (single pulse, low energy).
4. Gradually increase energy and monitor temperature rise over time (not just load).
5. Only after passive torque-angle fixture validates FEMM, proceed to synchronized powered rotor tests.

## Documentation
Every test session must record:
- Date, time, ambient temperature
- Power supply settings (voltage + current limit)
- Key waveforms and measurements (scope screenshots or CSV)
- Temperature readings at start, middle, and end
- Any anomalies or unexpected behavior
- Photos of setup
