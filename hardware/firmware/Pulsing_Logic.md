# Control Logic & Pulsing Strategy

## Core Principles

- Only pulse EMLs when they produce **net positive torque**.
- Avoid pulsing during **negative torque** regions.
- Allow brief **neutral torque** during EML energizing and when gradient is escaping the field.
- Use rotor position feedback for precise timing.

## Basic Pulsing Logic

```c
if (rotor_position is in Positive_Torque_Zone) {
    Pulse corresponding EML(s);
} else {
    Keep EML off;
}
```

## Recommended Implementation

1. Use a quadrature encoder or Hall sensors for rotor position.
2. Create a position lookup table or real-time calculation for "safe pulsing windows".
3. Pulse duration: 1–5 ms (adjustable).
4. Add load sensing so pulsing only occurs when extra torque is needed.
5. Implement safety checks before every pulse.
