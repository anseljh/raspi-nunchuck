"""
A Nunchuck class

Tested with the Wiichuck adaptor: 
    https://todbot.com/blog/2008/02/18/wiichuck-wii-nunchuck-adapter-available/
    https://www.sparkfun.com/products/retired/9281

Good documentation of I2C commands for Nunchuck:
    https://create.arduino.cc/projecthub/infusion/using-a-wii-nunchuk-with-arduino-597254

Successful I2C communication in Python:
    https://magpi.raspberrypi.org/articles/wii-nunchucks-raspberry-pi

I2C pins and setup:
    https://pinout.xyz/pinout/i2c
"""

from sys import platform
from threading import Thread
from time import sleep, time
from typing import Callable

# If we're on a Pi, import the smbus module for I2C.
# The smbus module is provided by the python3-smbus apt package.
I2C_CAPABLE = False
if platform == "linux":  # TODO: Detect Pi, not just any Linux.
    import smbus  # pylint: disable=import-error

    I2C_CAPABLE = True
    print("Guessed we're on a Pi, so imported smbus.")
else:
    print("Not on Pi, so not importing smbus.")


# TICK = 1.000  # 1 Hz
TICK = 0.500  # 2 Hz
# TICK = 0.050  # 20 Hz

DEBUG = True
# DEBUG = False

# I2C constants
DEVICE_BUS = 1
NUNCHUCK_ADDR = 0x52


class NunchuckState:
    def __init__(self, stick, accel, button_c, button_z):
        self.stick = stick
        self.accel = accel
        self.button_c = button_c
        self.button_z = button_z

    def __repr__(self):
        return f"<stick {self.stick} accel {self.accel} B {self.button_c} C {self.button_z}>"


class Nunchuck:
    class NunchuckThread(Thread):
        def __init__(self, instance):
            self.instance = instance
            Thread.__init__(self)

        def run(self):
            if DEBUG:
                print("Hello from NunchuckThread.run()")
            while True:
                if DEBUG:
                    print("NunchuckThread.run(): Top of while loop")
                if I2C_CAPABLE:
                    if DEBUG:
                        print("NunchuckThread.run(): Reading nunchuck...")
                    self.instance.read()
                if DEBUG:
                    print("NunchuckThread.run(): Tick!")
                sleep(TICK)

    def __init__(
        self,
        button_c_callback: Callable = None,
        button_z_callback: Callable = None,
        callback: Callable = None,
    ):
        if DEBUG:
            print("Hello from Nunchuck.__init__()")
        self.thread = Nunchuck.NunchuckThread(self)
        self.stick = None  # (None, None)
        self.accel = None  # (None, None, None)
        self.button_c = None
        self.button_c_changed = None
        self.button_z = None
        self.button_z_changed = None
        self.button_c_callback = button_c_callback
        self.button_z_callback = button_z_callback
        self.callback = callback

        if I2C_CAPABLE:
            # Init I2C bus
            print("Initializing I2C bus...")
            self.bus = smbus.SMBus(DEVICE_BUS)

            # Init Nunchuck
            # https://magpi.raspberrypi.org/articles/wii-nunchucks-raspberry-pi
            print("Initializing nunchuck...")
            self.bus.write_byte_data(NUNCHUCK_ADDR, 0x40, 0x00)
            sleep(0.01)

            self.get_ident()

        else:
            self.bus = None

    def get_ident(self):
        # https://create.arduino.cc/projecthub/infusion/using-a-wii-nunchuk-with-arduino-597254
        # 3. Read the device ident from extension register:
        # START, 0xFA, STOPREAD 6 byte

        if I2C_CAPABLE:
            print("Getting ident from nunchuck...")
            sleep(0.004)
            self.bus.write_byte(NUNCHUCK_ADDR, 0xFA)
            sleep(0.002)  # delay for Nunchuck to respond
            data = [
                ((self.bus.read_byte(NUNCHUCK_ADDR) ^ 0x17) + 0x17) for i in range(0, 6)
            ]
            ident = [hex(b) for b in data]
            self.ident = ident
            print("Ident: ", ident)
            return ident
        else:
            print("Can't get ident (not on Pi)")
            return None

    def read(self):
        """
        Read values from the nunchuck
        """
        # https://magpi.raspberrypi.org/articles/wii-nunchucks-raspberry-pi
        # the I2C drivers or something throws up an occasional error - this is the sticking plaster
        sleep(0.004)
        try:
            self.bus.write_byte(NUNCHUCK_ADDR, 0)
        except:
            print("bus restart")
            sleep(0.1)
            self.bus.write_byte(NUNCHUCK_ADDR, 0)
        sleep(0.002)  # delay for Nunchuck to respond
        data = [
            ((self.bus.read_byte(NUNCHUCK_ADDR) ^ 0x17) + 0x17) for i in range(0, 6)
        ]

        # Parse
        stick = (data[0], data[1])
        accel = (data[2], data[3], data[4])
        button_c = not ((data[5] & 0x02) >> 1)  # Flip so True means button is pressed
        button_z = not (data[5] & 0x01)

        self.set(stick, accel, button_c, button_z)

    def start(self):
        self.thread.start()

    def set(self, stick, accel, button_c, button_z):
        """
        Set nunchuck sensor values and trigger any callbacks
        """

        # First, check for change in button states
        if self.button_c != button_c:
            self.button_c_changed = True
        else:
            self.button_c_changed = False

        if self.button_z != button_z:
            self.button_z_changed = True
        else:
            self.button_z_changed = False

        self.stick = stick
        self.accel = accel
        self.button_c = button_c
        self.button_z = button_z

        self.state = NunchuckState(stick, accel, button_c, button_z)

        if DEBUG:
            print(self)

        if self.button_c_changed and self.button_c_callback:
            self.button_c_callback(self.state)
        if self.button_z_changed and self.button_z_callback:
            self.button_z_callback(self.state)
        if self.callback:
            self.callback(self.state)

    def fake_button_c(self, pressed=True):
        print(f"Fake button C {Nunchuck.button_state(pressed)}")
        self.set(self.stick, self.accel, pressed, self.button_z)

    def fake_button_z(self, pressed=True):
        print(f"Fake button Z {Nunchuck.button_state(pressed)}")
        self.set(self.stick, self.accel, self.button_c, pressed)

    def __repr__(self):
        return f"<Nunchuck {hex(NUNCHUCK_ADDR)} {self.state}>"

    @staticmethod
    def button_state(pressed: bool) -> str:
        return "pressed" if pressed else "released"
