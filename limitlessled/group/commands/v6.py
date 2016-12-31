""" Command sets for wifi bridge version 6. """


import math
from colorsys import rgb_to_hsv

from limitlessled.group.rgbw import RGBW, RGBWW, BRIDGE_LED
from limitlessled.group.white import WHITE
from limitlessled.group.commands import CommandSet, Command


class CommandSetV6(CommandSet):
    """ Base command set for wifi bridge v6. """

    SUPPORTED_VERSIONS = [6]
    PASSWORD_BYTE1 = 0x00
    PASSWORD_BYTE2 = 0x00
    MAX_COLOR = 0xFF
    MAX_BRIGHTNESS = 0x64
    MAX_TEMPERATURE = 0x64

    def __init__(self, bridge, group_number, remote_style,
                 brightness_steps=None, color_steps=None,
                 temperature_steps=None):
        """
        Initialize the command set.
        :param bridge: The bridge the leds are connected to.
        :param group_number: The group number.
        :param remote_style: The remote style of the device to control.
        :param brightness_steps: The number of brightness steps.
        :param color_steps: The number of color steps.
        :param temperature_steps: The number of temperature steps.
        """
        brightness_steps = brightness_steps or self.MAX_BRIGHTNESS + 1
        color_steps = color_steps or self.MAX_COLOR + 1
        temperature_steps = temperature_steps or self.MAX_TEMPERATURE + 1
        super().__init__(bridge, group_number, brightness_steps,
                         color_steps=color_steps,
                         temperature_steps=temperature_steps)
        self._remote_style = remote_style

    def convert_brightness(self, brightness):
        """
        Convert the brightness from decimal percent (0.0-1.0)
        to byte representation for use in commands.
        :param brightness: The brightness from in decimal percent (0.0-1.0).
        :return: The brightness in byte representation.
        """
        return math.ceil(brightness * self.MAX_BRIGHTNESS)

    def convert_temperature(self, temperature):
        """
        Convert the temperature from decimal percent (0.0-1.0)
        to byte representation for use in commands.
        :param temperature: The temperature from in decimal percent (0.0-1.0).
        :return: The temperature in byte representation.
        """
        return math.ceil(temperature * self.MAX_TEMPERATURE)

    def convert_color(self, color):
        """
        Converts the color from RGB to byte representation for use in commands.
        :param color: The RGB color tuple.
        :return: The color in byte representation (best-effort basis).
        """
        hue = rgb_to_hsv(*color)[0]
        return math.floor(hue * self.MAX_COLOR)

    def _build_command(self, cmd_1, cmd_2):
        """
        Constructs the complete command.
        :param cmd_1: Light command 1.
        :param cmd_2: Light command 2.
        :return: The complete command.
        """
        wb1 = self._bridge.wb1
        wb2 = self._bridge.wb2
        sn = self._bridge.sn

        preamble = [0x80, 0x00, 0x00, 0x00, 0x11, wb1, wb2, 0x00, sn, 0x00]
        cmd = [0x31, self.PASSWORD_BYTE1, self.PASSWORD_BYTE2,
               self._remote_style, cmd_1, cmd_2, cmd_2, cmd_2, cmd_2]
        zone_selector = [self._group_number, 0x00]
        checksum = sum(cmd + zone_selector) & 0xFF

        return Command(preamble + cmd + zone_selector + [checksum],
                       self._group_number)


class CommandSetBridgeLightV6(CommandSetV6):
    """ Command set for bridge light of wifi bridge v6. """

    SUPPORTED_LED_TYPES = [BRIDGE_LED]
    REMOTE_STYLE = 0x00

    def __init__(self, bridge, group_number):
        """
        Initializes the command set.
        :param bridge: The bridge the leds are connected to.
        :param group_number: The group number.
        """
        super().__init__(bridge, group_number, self.REMOTE_STYLE)

    def on(self):
        """
        Build command for turning the led on.
        :return: The command.
        """
        return self._build_command(0x03, 0x03)

    def off(self):
        """
        Build command for turning the led off.
        :return: The command.
        """
        return self._build_command(0x03, 0x04)

    def white(self):
        """
        Build command for turning the led into white mode.
        :return: The command.
        """
        return self._build_command(0x03, 0x05)

    def color(self, color):
        """
        Build command for setting the color of the led.
        :param color: RGB color tuple.
        :return: The command.
        """
        return self._build_command(0x01, self.convert_color(color))

    def brightness(self, brightness):
        """
        Build command for setting the brightness of the led.
        :param brightness: Value to set (0.0-1.0).
        :return: The command.
        """
        return self._build_command(0x02, self.convert_brightness(brightness))


class CommandSetWhiteV6(CommandSetV6):
    """ Command set for white led light connected to wifi bridge v6. """

    SUPPORTED_LED_TYPES = [WHITE]
    REMOTE_STYLE = 0x08

    def __init__(self, bridge, group_number):
        """
        Initializes the command set.
        :param bridge: The bridge the leds are connected to.
        :param group_number: The group number.
        """
        super().__init__(bridge, group_number, self.REMOTE_STYLE)

    def on(self):
        """
        Build command for turning the led on.
        :return: The command.
        """
        return self._build_command(0x04, 0x01)

    def off(self):
        """
        Build command for turning the led off.
        :return: The command.
        """
        return self._build_command(0x04, 0x02)

    def night_light(self):
        """
        Build command for turning the led into night light mode.
        :return: The command.
        """
        return self._build_command(0x04, 0x05)

    def brightness(self, brightness):
        """
        Build command for setting the brightness of the led.
        :param brightness: Value to set (0.0-1.0).
        :return: The command.
        """
        return self._build_command(0x03, self.convert_brightness(brightness))

    def temperature(self, temperature):
        """
        Build command for setting the temperature of the led.
        :param temperature: Value to set (0.0-1.0).
        :return: The command.
        """
        return self._build_command(0x05, temperature)


class CommandSetRgbwV6(CommandSetV6):
    """ Command set for RGBW led light connected to wifi bridge v6. """

    SUPPORTED_LED_TYPES = [RGBW]
    REMOTE_STYLE = 0x08

    def __init__(self, bridge, group_number):
        """
        Initializes the command set.
        :param bridge: The bridge the leds are connected to.
        :param group_number: The group number.
        """
        super().__init__(bridge, group_number, self.REMOTE_STYLE)

    def on(self):
        """
        Build command for turning the led on.
        :return: The command.
        """
        return self._build_command(0x04, 0x01)

    def off(self):
        """
        Build command for turning the led off.
        :return: The command.
        """
        return self._build_command(0x04, 0x02)

    def night_light(self):
        """
        Build command for turning the led into night light mode.
        :return: The command.
        """
        return self._build_command(0x04, 0x05)

    def white(self):
        """
        Build command for turning the led into white mode.
        :return: The command.
        """
        return self._build_command(0x05, 0x64)

    def color(self, color):
        """
        Build command for setting the color of the led.
        :param color: RGB color tuple.
        :return: The command.
        """
        return self._build_command(0x01, self.convert_color(color))

    def brightness(self, brightness):
        """
        Build command for setting the brightness of the led.
        :param brightness: Value to set (0.0-1.0).
        :return: The command.
        """
        return self._build_command(0x03, self.convert_brightness(brightness))


class CommandSetRgbwwV6(CommandSetV6):
    """ Command set for RGBWW led light connected to wifi bridge v6. """

    SUPPORTED_LED_TYPES = [RGBWW]
    REMOTE_STYLE = 0x07

    def __init__(self, bridge, group_number):
        """
        Initializes the command set.
        :param bridge: The bridge the leds are connected to.
        :param group_number: The group number.
        """
        super().__init__(bridge, group_number, self.REMOTE_STYLE)

    def on(self):
        """
        Build command for turning the led on.
        :return: The command.
        """
        return self._build_command(0x03, 0x01)

    def off(self):
        """
        Build command for turning the led off.
        :return: The command.
        """
        return self._build_command(0x03, 0x02)

    def night_light(self):
        """
        Build command for turning the led into night light mode.
        :return: The command.
        """
        return self._build_command(0x03, 0x06)

    def white(self):
        """
        Build command for turning the led into white mode.
        :return: The command.
        """
        return self._build_command(0x03, 0x05)

    def color(self, color):
        """
        Build command for setting the color of the led.
        :param color: RGB color tuple.
        :return: The command.
        """
        return self._build_command(0x01, self.convert_color(color))

    def brightness(self, brightness):
        """
        Build command for setting the brightness of the led.
        :param brightness: Value to set (0.0-1.0).
        :return: The command.
        """
        return self._build_command(0x02, self.convert_brightness(brightness))