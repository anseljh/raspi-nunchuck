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

import smbus
import time

DEVICE_BUS = 1
NUNCHUCK_ADDR = 0x52

class Nunchuck:

    def __init__(self):
        print("Begun Nunchuck __init__()")
        self.bus = smbus.SMBus(DEVICE_BUS)
        self.stick = None
        self.accel = None
        self.button_c = None
        self.button_z = None
        self.button_c_changed = False
        self.button_z_changed = False

        # https://magpi.raspberrypi.org/articles/wii-nunchucks-raspberry-pi
        self.bus.write_byte_data(NUNCHUCK_ADDR, 0x40, 0x00)
        time.sleep(0.01)

        print("End Nunchuck __init__()")


    def get_ident(self):
        # https://create.arduino.cc/projecthub/infusion/using-a-wii-nunchuk-with-arduino-597254
        # 3. Read the device ident from extension register:
        # START, 0xFA, STOPREAD 6 byte

        time.sleep(0.004)
        self.bus.write_byte(NUNCHUCK_ADDR, 0xfa)
        time.sleep(0.002) #delay for Nunchuck to respond
        data = [((self.bus.read_byte(NUNCHUCK_ADDR) ^ 0x17) +0x17) for i in range(0,6)]
        ident = [hex(b) for b in data]
        self.ident = ident
        print("Ident: ", ident)
        return ident


    def read(self):
        """
        https://magpi.raspberrypi.org/articles/wii-nunchucks-raspberry-pi
        """
        # the I2C drivers or something throws up an occasional error - this is the sticking plaster
        time.sleep(0.004)
        try:
            self.bus.write_byte(NUNCHUCK_ADDR, 0)
        except:
            print("bus restart")
            time.sleep(0.1)
            self.bus.write_byte(NUNCHUCK_ADDR, 0)
        time.sleep(0.002) #delay for Nunchuck to respond   
        data = [((self.bus.read_byte(NUNCHUCK_ADDR) ^ 0x17) +0x17) for i in range(0,6)]

        # Parse
        stick = (data[0], data[1])
        accel = (data[2], data[3], data[4])
        button_c = not ((data[5] & 0x02) >> 1)
        button_z = not (data[5] & 0x01)

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


    def print_(self):
        d = {
            "stick": self.stick,
            "accel": self.accel,
            "c": self.button_c,
            "z": self.button_z
        }
        print(d)


if __name__ == "__main__":
    nc = Nunchuck()
    print(nc)
    nc.get_ident()
    while True:
        values = nc.read()
        # print(values)
        nc.print_()
        if nc.button_c and nc.button_c_changed:
            print("**PEW**")
        if nc.button_z and nc.button_z_changed:
            print("--ZOT--")
        time.sleep(.25)
