import serial
from serial.tools.list_ports import comports

from switchmap import inputMap, inputComparators, outputMap, outputValue
from changedict import ChangeDict

_in_bytes = (inputMap.nbits + 7) // 8
_out_bytes = (len(outputMap) + 7) // 8

print(f"Arduino: reading {_in_bytes} bytes, writing {_out_bytes}")


class Arduino(serial.Serial):
    def __init__(self):
        # scan attached serial devices for the first one with a USB vendor Id
        # to locate the Arduino.  This could fail with multiple USD devices
        self._in_state = ChangeDict(comparators=inputComparators)
        self._out_state = ChangeDict()
        usbport = next((p.device for p in comports() if p.vid), None)
        assert usbport, "Couldn't find usbport, is Arduino connected?"
        print(f"Arduino on usb port @ {usbport}")
        super().__init__(port=usbport, baudrate=115200, timeout=1)
        print(f"Initializing, expecting timeout...")
        self.read(_in_bytes)
        print(f"Ready.")

    def get_state(self):
        # send a "request state" command
        # then receive expected number of bytes
        self.write(b'\x01')
        state = dict(inputMap.from_bytes(self.read(_in_bytes)))
        self._in_state.update(state)
        return self._in_state

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
        print(f"Writing output state 0x{v:02x}")
        self.write(b'\x02' + v.to_bytes(_out_bytes, byteorder='little'))
