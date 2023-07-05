from serial import Serial  # type: ignore
from serial.tools.list_ports import comports  # type: ignore
import logging

from g3py.decl import MetricDict

from arduino_base import ArduinoBase
from switchmap import inputMap, outputMap


_in_bytes = (inputMap.nbits + 7) // 8
_out_bytes = (len(outputMap) + 7) // 8

logging.debug(f"Arduino: mapped with {_in_bytes} bytes input, {_out_bytes} bytes output")


class Arduino(ArduinoBase, Serial):
    def __init__(self):
        ArduinoBase.__init__(self)

        # scan attached serial devices for the first one with a USB vendor Id
        # to locate the Arduino.  This could fail with multiple USB devices
        usb_port = next((p.device for p in comports() if p.vid), None)
        assert usb_port, "Couldn't find usb port, is Arduino connected?"
        logging.info(f"Arduino: found on usb port @ {usb_port}")
        Serial.__init__(port=usb_port, baudrate=115200, timeout=1)
        logging.debug("Arduino: Initializing, expecting timeout...")
        self.read(_in_bytes)
        logging.info("Arduino: Ready.")

    def _poll(self) -> MetricDict:
        # send a "request state" command
        # then receive expected number of bytes
        logging.debug("Arduino: reading current state")
        self.write(b'\x01')
        return dict(inputMap.from_bytes(self.read(_in_bytes)))

    def set_state(self, state: MetricDict) -> None:
        v = self._maybe_output(state)
        if v is None:
            return
        logging.debug(f"Arduino: writing output state 0x{v:02x}")
        self.write(b'\x02' + v.to_bytes(_out_bytes, byteorder='little'))
