# Prototype Testing Checklist

## Phase 1: Single Channel Basic Test
- [ ] Power supply current limit set low (2–3A)
- [ ] MOSFETs and diodes installed correctly
- [ ] Gate driver powered and receiving signals
- [ ] Simple pulsing works (manual or timed)
- [ ] Coil clicks/moves when pulsed
- [ ] No excessive heating on MOSFETs
- [ ] Current sensor reading correctly

## Phase 2: Energy Recovery Test
- [ ] Recovery capacitor voltage rises after pulse
- [ ] No shoot-through between main and clamp MOSFETs
- [ ] Dead time configured correctly
- [ ] Energy can be reused for next pulse

## Phase 3: Position-Synchronized Pulsing
- [ ] Encoder / Hall sensors working and calibrated
- [ ] Pulsing only occurs in positive torque zones
- [ ] No pulsing during negative torque regions
- [ ] Smooth operation with low vibration

## Phase 4: Safety & Protection
- [ ] Over-current protection triggers correctly
- [ ] Over-temperature protection works
- [ ] Emergency stop functions
- [ ] Watchdog timer enabled
- [ ] System recovers gracefully from faults

## General Recommendations
- Always have a way to quickly cut power.
- Monitor temperatures during extended tests.
- Log current, voltage, and temperature data when possible.
- Start with short test runs and gradually increase duration.
