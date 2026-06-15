# Step-by-Step Build Guide - First Prototype

## Phase 0: Warnings

- Start small (single EML channel).
- Use a current-limited power supply (2–3A max initially).
- Expect to damage a few components while learning.

## Phase 1: Basic Driver Circuit

1. Assemble the driver on a breadboard or perfboard.
2. Use IRLZ44N MOSFET + flyback diode for initial testing.
3. Write simple STM32 code to generate PWM pulses (e.g., 5ms on, 500ms off).
4. Test with one EML coil and observe behavior.

## Phase 2: Add Energy Recovery

1. Implement active clamp or simple capacitor recovery.
2. Verify that energy is being captured when the main switch turns off.

## Phase 3: Add Rotor Position Sensing

1. Mount encoder or Hall sensors.
2. Read rotor position in firmware.
3. Only pulse EMLs during positive torque zones.

## Phase 4: Scale Up

1. Duplicate driver channels for all EMLs.
2. Add temperature sensing and basic protection.
3. Test full motor with synchronized pulsing.

## Recommended Tools

- STM32CubeIDE
- Logic analyzer or oscilloscope
- Current-limited power supply
