from typing import Any

from ledmatrix.stubs.mock_gpio_pin import MockGpioPin

SCREEN_WIDTH_PX = 640
SCREEN_HEIGHT_PX = 480


class MockBoard:

    def __init__(self) -> None:
        pass

    def __getattribute__(self, attr_name: str) -> Any:
        try:
            return super().__getattribute__(attr_name)
        except AttributeError:
            if attr_name.startswith('D'):
                pin_index = int(attr_name[1:])
                pin = MockGpioPin(pin_index)
                setattr(self, attr_name, pin)
                return pin
            raise
