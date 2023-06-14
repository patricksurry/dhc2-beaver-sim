import serial   # type: ignore
from serial.tools.list_ports import comports  # type: ignore
import logging

from switchmap import inputMap, inputComparators, outputMap, outputValue
from changedict import ChangeDict

_in_bytes = (inputMap.nbits + 7) // 8
_out_bytes = (len(outputMap) + 7) // 8

logging.debug(f"Arduino: mapped with {_in_bytes} bytes input, {_out_bytes} bytes output")

class Arduino(serial.Serial):
    def __init__(self):
        # scan attached serial devices for the first one with a USB vendor Id
        # to locate the Arduino.  This could fail with multiple USB devices
        self._in_state = ChangeDict(comparators=inputComparators)
        self._out_state = ChangeDict()
        usbport = next((p.device for p in comports() if p.vid), None)
        assert usbport, "Couldn't find usbport, is Arduino connected?"
        logging.info(f"Arduino: found on usb port @ {usbport}")
        super().__init__(port=usbport, baudrate=115200, timeout=1)
        logging.debug("Arduino: Initializing, expecting timeout...")
        self.read(_in_bytes)
        logging.info("Arduino: Ready.")

    def get_state(self):
        # send a "request state" command
        # then receive expected number of bytes
        logging.debug("Arduino: reading current state")
        self.write(b'\x01')
        state = dict(inputMap.from_bytes(self.read(_in_bytes)))
        self._in_state.update(state)
        return self._in_state

    def get_state_changes(self):
        t = self._in_state.latest()
        self.get_state()
        return self._in_state.changedsince(t)

    def output_names(self):
        return [k for k in outputMap if k]

    def set_test(self, on: bool):
        self.set_state({k: on for k in self.output_names()})

    def set_state(self, state):
        state = {k: v for (k, v) in state.items() if k in self.output_names()}
        if not state:
            return
        latest = self._out_state.latest()
        self._out_state.update(state)
        if self._out_state.latest() == latest:
            return

        v = outputValue(self._out_state)
        logging.debug(f"Arduino: writing output state 0x{v:02x}")
        self.write(b'\x02' + v.to_bytes(_out_bytes, byteorder='little'))
