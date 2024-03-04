# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

import time
import board
import pwmio
import digitalio

led = pwmio.PWMOut(board.D16, frequency=10, duty_cycle=0)

led26 = pwmio.PWMOut(board.D26, frequency=3, duty_cycle=49152)
led5 = pwmio.PWMOut(board.D5, frequency=3, duty_cycle=32768)
led6 = pwmio.PWMOut(board.D6, frequency=3, duty_cycle=16384)

# led16 = digitalio.DigitalInOut(board.D16)
# led16.direction = digitalio.Direction.OUTPUT

while True:
    for i in range(100):
        # PWM LED up and down
        led.duty_cycle = int(i / 100 * 65535)  # Up
        time.sleep(0.01)

    for i in range(100, 0, -1):
        # PWM LED up and down
        led.duty_cycle = int(i / 100 * 65535)  # Up
        time.sleep(0.01)
