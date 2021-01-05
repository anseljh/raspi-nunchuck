# raspi-nunchuck

A Python 3 class for using a Wii nunchuck controller with a Raspberry Pi

Pressing the Z button while holding the stick at the upper right position:

## What's this?

**Who *wouldn't* want to remotely control a robot with a [Wii Nunchuk™ controller](https://store.nintendo.com/nunchuk-wii-u-wii-wii-mini.html)?**

There are lots of examples out there of working with these nunchucks with Arduino microcontrollers, but what are we, animals? Dear reader, you and I are more civilized than that. We program our robots in Python!

## How does it work?

### Prepare your Pi

Before anything else, you need to activate the I<sup>2</sup>C bus on your Raspberry Pi. Run the `raspi-config` tool:

```shell
sudo raspi-config
```

Select `Interface Options`, and then `I2C`.

Next, install the `smbus` module for Python, on which this code depends:

```shell
sudo apt install python3-smbus
```

### Using the code

In your Python code, create an instance of the `Nunchuck` class. Pass it three callback functions: one each for changes in the state of the C and Z buttons, and another to be called continuously.

When you're ready, call the `start()` method. This launches a thread that polls your nunchuck and calls your callbacks.

```python
nunchuck = Nunchuck(cb_c, cb_z, cb)
nunchuck.start()
```

Callback functions accept an instance of `NunchuckState`, which simply holds the following properties:

* `stick`: 2-tuple of integers for position of the joystick
* `accel`: 3-tuple of integers for position of the accelerometer
* `button_c`: Boolean for whether the C button is pressed
* `button_z`: Boolean for whether the Z button is pressed

Here's what a simple Z-button callback could look like:

```python
def cb_z(state: NunchuckState):
    if state.button_z:
        print("** ZOT **")
```

Once you do that, you can get output like this:

```
NunchuckThread.run(): Reading nunchuck...
<Nunchuck 0x52 <stick (193, 193) accel (118, 124, 174) B False C True>>
** ZOT **
RIGHT
FORWARD
```

## Can I install this with `pip`?

Not yet. Maybe later.

## What hardware and software does this work on?

This was developed and tested on a [Raspberry Pi Zero W](https://www.raspberrypi.org/pi-zero-w/) running [Rasperry Pi OS Lite](https://www.raspberrypi.org/software/operating-systems/#raspberry-pi-os-32-bit) (Debian Buster). It *should* work on any Raspberry Pi model as long as you activate the I<sup>2</sup>C bus.

If you test this on other hardware and it works, please submit an issue or PR to let me know, and I'll update this documentation.

## Can I use this with Legacy Python, also known as Python 2?

No. You should really use modern Python 3.

This code was developed and tested on Python 3.7, which ships with the current version of Raspberry Pi OS.

## Is this code stable?

No. Maybe later. Maybe not! Your mileage may vary.

## How's this code licensed?

Thank you for asking! This code is under the MIT License.

## Who wrote this?

This code is by Ansel Halliburton, who is a lawyer and software developer. You can find him on [GitHub](https://github.com/anseljh) or [Twitter](https://twitter.com/anseljh).
