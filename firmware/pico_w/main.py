"""HawaBot Pico W firmware — MicroPython servo controller.

Flash this onto the Raspberry Pi Pico W.  It listens for simple text
commands on USB serial (115200 baud) and drives hobby servos via PWM.

Wiring (default — matches PicoDriver.DEFAULT_PIN_MAP):
  GP0 → waist_yaw servo signal
  GP1 → left_shoulder_pitch servo signal
  GP2 → right_shoulder_pitch servo signal
  GP3 → head_pan servo signal
  GP4 → head_tilt servo signal
  VSYS (pin 39) → optional voltage divider to GP26 (ADC0) for battery monitoring

Protocol (newline-terminated, 115200 baud):
  S <pin> <pulse_us>   →  OK          Set servo PWM pulse width
  V                     →  V <float>   Read VSYS voltage (or V NONE)
  P                     →  PONG        Ping / health check

Upload:
  1. Install MicroPython on Pico W (hold BOOTSEL, drag .uf2)
  2. Copy this file as main.py to the Pico W filesystem
     (e.g. via Thonny, mpremote, or rshell)
  3. Power-cycle — the Pico will start listening immediately.
"""

import sys
import time
from machine import ADC, PWM, Pin

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SERVO_PINS = [0, 1, 2, 3, 4]  # GPIO numbers that may drive servos
PWM_FREQ = 50                  # Standard servo PWM frequency (50 Hz)

# Voltage divider on GP26 (ADC0) to monitor VSYS.
# With a 100k/100k divider: V_actual = ADC_voltage * 2
# Set to None to disable voltage monitoring.
VSYS_ADC_PIN = 26
VSYS_DIVIDER_RATIO = 2.0

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

# Pre-create PWM objects for each allowed pin.
# Servos only start receiving pulses once the first S command is sent.
servos: dict[int, PWM] = {}
for pin_num in SERVO_PINS:
    pwm = PWM(Pin(pin_num))
    pwm.freq(PWM_FREQ)
    pwm.duty_ns(0)  # Off until commanded
    servos[pin_num] = pwm

# Optional voltage ADC.
vsys_adc: ADC | None = None
if VSYS_ADC_PIN is not None:
    vsys_adc = ADC(Pin(VSYS_ADC_PIN))


def set_servo_us(pin: int, pulse_us: int) -> bool:
    """Set a servo's pulse width in microseconds."""
    pwm = servos.get(pin)
    if pwm is None:
        return False
    # Clamp to safe servo range.
    pulse_us = max(500, min(2500, pulse_us))
    pwm.duty_ns(pulse_us * 1000)
    return True


def read_voltage() -> float | None:
    """Read supply voltage via ADC, or None if not wired."""
    if vsys_adc is None:
        return None
    # MicroPython ADC returns 0-65535 for 0-3.3V.
    raw = vsys_adc.read_u16()
    adc_voltage = (raw / 65535) * 3.3
    return round(adc_voltage * VSYS_DIVIDER_RATIO, 2)


# ---------------------------------------------------------------------------
# Main loop — read commands from USB serial, respond
# ---------------------------------------------------------------------------

def main() -> None:
    # Signal that firmware is ready.
    print("HAWABOT PICO READY")

    while True:
        try:
            line = sys.stdin.readline()
        except Exception:
            time.sleep_ms(10)
            continue

        if not line:
            time.sleep_ms(10)
            continue

        line = line.strip()
        if not line:
            continue

        parts = line.split()
        cmd = parts[0]

        if cmd == "P":
            print("PONG")

        elif cmd == "S" and len(parts) == 3:
            try:
                pin = int(parts[1])
                pulse_us = int(parts[2])
            except ValueError:
                print("ERR BAD_ARGS")
                continue
            if set_servo_us(pin, pulse_us):
                print("OK")
            else:
                print("ERR BAD_PIN")

        elif cmd == "V":
            v = read_voltage()
            if v is not None:
                print(f"V {v}")
            else:
                print("V NONE")

        else:
            print("ERR UNKNOWN_CMD")


main()
