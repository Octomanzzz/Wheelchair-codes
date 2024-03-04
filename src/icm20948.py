import board
import adafruit_icm20x

class Icm20948:
    def __init__(self) -> None:
        self.i2c = board.I2C()  # uses board.SCL and board.SDA
        # i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller

        self.init()

    def init(self):
        try:
            self.icm = adafruit_icm20x.ICM20948(self.i2c)
        except Exception as ex:
            print(f"Error connecting ICM20948 {ex=}")

    def get_accel(self)->tuple[float,float,float]:
        try:
            return self.icm.acceleration
        except OSError as ex:
            print(f"Error getting accel {ex=}")

        self.init()

    def get_gyro(self)->tuple[float,float,float]:
        try:
            return self.icm.gyro
        except OSError as ex:
            print(f"Error getting gyro {ex=}")

        self.init()



