"""Mock a GPIO pin from the Adafruit NeoPixel library."""


class MockGpioPin:
    """Mock a GPIO pin from the Adafruit NeoPixel library."""
    def __init__(self, pin_index):  # type: (int) -> None
        self.pin_index = pin_index
