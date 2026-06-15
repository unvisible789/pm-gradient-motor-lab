# STM32 Pulsing Code Template

## Recommended Project Setup
- Use **STM32CubeIDE** with STM32F411 (Black Pill) or similar.
- Enable:
  - TIM1 or TIM8 for PWM generation (with dead time)
  - TIM for encoder input
  - ADC for current sensing
  - UART for debugging

## High-Level Code Structure

```c
// main.c

#include "main.h"

#define NUM_EML 8
#define PULSE_DURATION_MS 3

volatile uint16_t rotor_position = 0;

void PulseEML(uint8_t index) {
    if (!IsSafeToPulse(index)) return;

    // Turn on corresponding MOSFET
    HAL_GPIO_WritePin(EML_Pins[index].GPIOx, EML_Pins[index].Pin, GPIO_PIN_SET);
    HAL_Delay(PULSE_DURATION_MS);
    HAL_GPIO_WritePin(EML_Pins[index].GPIOx, EML_Pins[index].Pin, GPIO_PIN_RESET);
}

void HAL_TIM_IC_CaptureCallback(TIM_HandleTypeDef *htim) {
    if (htim->Instance == TIM3) {  // Encoder timer
        rotor_position = __HAL_TIM_GET_COUNTER(htim);
    }
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_TIM_Init();     // PWM + Encoder
    MX_ADC_Init();

    while (1) {
        uint16_t pos = rotor_position;

        for (int i = 0; i < NUM_EML; i++) {
            if (ShouldPulse(i, pos)) {
                PulseEML(i);
            }
        }

        CheckSafety();
        HAL_Delay(1);
    }
}
```

## Key Functions to Implement

- `IsSafeToPulse(uint8_t eml_index)`
- `ShouldPulse(uint8_t eml_index, uint16_t position)`
- `CheckSafety()`
- Position to torque zone mapping

## Safety Checks (Recommended)
- Coil current limit
- MOSFET temperature
- Supply voltage
- Emergency stop input
