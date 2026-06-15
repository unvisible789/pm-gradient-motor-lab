# Safety Recommendations

## Minimum Required Protections

- Over-current protection (current sensor + MCU or hardware comparator)
- Over-temperature protection (NTC thermistors on coils and MOSFETs)
- Under-voltage lockout
- Proper dead time in gate driver
- Emergency stop button
- Watchdog timer in firmware

## Testing Best Practices

1. Always start with low current limit on the power supply.
2. Use a fuse (5–10A) on the main power line.
3. Monitor MOSFET and coil temperature during testing.
4. Never leave the system unattended while powered.
5. Have a way to quickly disconnect power.

## General Advice

- Build and test one channel completely before scaling to multiple EMLs.
- Document everything (scope captures, temperatures, current measurements).
- Consider working with someone experienced in power electronics for the first hardware version.
