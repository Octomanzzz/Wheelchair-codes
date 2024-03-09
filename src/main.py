import time
import os
import board
import pwmio
import digitalio

from icm20948 import Icm20948

# initializing io
motio_l_speed = pwmio.PWMOut(board.D16, frequency=10000, duty_cycle=0)
motio_r_speed = pwmio.PWMOut(board.D5, frequency=10000, duty_cycle=0)

motio_l_dir = digitalio.DigitalInOut(board.D26)
motio_l_dir.direction = digitalio.Direction.OUTPUT

motio_r_dir = digitalio.DigitalInOut(board.D6)
motio_r_dir.direction = digitalio.Direction.OUTPUT

motio_l_dir.value = motio_r_dir.value = True

icm = Icm20948()

start_time = time.perf_counter()
warmup_time = 3
gyro_moved = 0.02

# Find averages
init_xs = []
init_ys = []
init_zs = []

while time.perf_counter() - start_time < warmup_time:
    accel = icm.get_accel()
    gyro = icm.get_gyro()

    # stopping from moving before it's done being ready
    gyro_mag = gyro[0] ** 2 + gyro[1] ** 2 + gyro[2] ** 2
    if gyro_mag > gyro_moved:
        start_time = time.perf_counter()
        init_xs = []
        init_ys = []
        init_zs = []
        print("Stop moving! Sit still!")

    print(accel[0])
    init_xs.append(accel[0])
    init_ys.append(accel[1])
    init_zs.append(accel[2])

# cauculates the avg
accel_avg_x = sum(init_xs) / len(init_xs)
accel_avg_y = sum(init_ys) / len(init_ys)
accel_avg_z = sum(init_zs) / len(init_zs)
print(len(init_xs))
print(accel_avg_x)
print(accel_avg_y)
print(accel_avg_z)

# otherstuff
last_action = ""
action_count = 0
speed = 0
enabled = False
steer = 0
while True:
    accel = icm.get_accel()

    # computes the avg and subtracts it from the reading to get close to zero
    # beacuse you wont put the hat on the same way evrey single time
    accel_x = accel[0] - accel_avg_x
    accel_y = accel[1] - accel_avg_y
    accel_z = accel[2] - accel_avg_z

    print(f"accel X{accel_x:6.2f}  Y{accel_y:6.2f}  Z{accel_z:6.2f}  ", end="")

    # if you tilted passed a certain threshold, only then will it detect that you tilted
    action = ""
    if abs(accel_x) > abs(accel_y):
        if accel_x > 4.5:
            action = "front"
        elif accel_x < -4.5:
            action = "back"

    # There has to be three of the same readings in a row to make it actually make that action
    # I put this in  because of the sudden jolting of the chair made your head move in direactions you didn't want it to
    if action == last_action:
        action_count += 1
        if action_count == 3:

            if action == "front":
                if speed < 3:
                    speed += 1

            elif action == "back":
                if speed > 0:
                    speed = 0
                elif speed > -1:
                    speed -= 1

        # This is the part that turns the whole chair on/off when you tilt back from speed 1, 2, or 3 and hold for 75 readings
        elif action_count == 75 and action == "back" and speed == 0:
            enabled = not enabled
            print(action, end="")

            motio_l_speed.duty_cycle = motio_r_speed.duty_cycle = 400

            motio_l_speed.frequency = motio_r_speed.frequency = 500
            time.sleep(0.05)
            motio_l_speed.frequency = motio_r_speed.frequency = 650
            time.sleep(0.05)
            motio_l_speed.frequency = motio_r_speed.frequency = 800
            time.sleep(0.05)
            motio_l_speed.frequency = motio_r_speed.frequency = 950
            time.sleep(0.05)
            motio_l_speed.frequency = motio_r_speed.frequency = 1500
            time.sleep(0.2)

            motio_l_speed.duty_cycle = motio_r_speed.duty_cycle = 0
            motio_l_speed.frequency = motio_r_speed.frequency = 10000

    else:
        # starts the counting of readings from the new action until the next one
        # makes the new action the new last action
        last_action = action
        action_count = 0

    if enabled:
        # If you only tilt a tiny bit then it doesn't count it, otherwise, the steering is a ratio to accel_y which is tilt
        steer = 0 if accel_y < 2 and accel_y > -2 else accel_y * 0.455

        # It's adding and subtracting to make the steering work
        # If the right motor turns faster than the left one, you'll turn left, and vice versa
        motor_l = (speed + steer) * 33
        motor_r = (speed - steer) * 33

        # Stops the readding numbers from going past 100% speed
        motor_l = min(motor_l, 100)
        motor_l = max(motor_l, -100)
        motor_r = min(motor_r, 100)
        motor_r = max(motor_r, -100)

    else:
        motor_l = motor_r = 0

    print(
        f"  {action_count} {action} {speed} {steer=:6.2f} {motor_l:6.2f} {motor_r:6.2f} {enabled}"
    )

    # Duty_cycle is how long the motor is on, EX: 65535: full, 32768: exactly half, 0: none
    motio_l_speed.duty_cycle = int(abs(motor_l) / 100 * 65535)
    motio_r_speed.duty_cycle = int(abs(motor_r) / 100 * 65535)

    # forward is positive numbers and backward is negative
    motio_l_dir.value = motor_l > 0
    motio_r_dir.value = motor_r > 0
