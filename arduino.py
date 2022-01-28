import serial
from serial.tools.list_ports import comports

from switchmap import inputMap, inputComparators, outputMap, outputValue
from changedict import ChangeDict


class Arduino(serial.Serial):
    def __init__(self):
        # scan attached serial devices for the first one with a USB vendor Id
        # to locate the Arduino.  This could fail with multiple USD devices
        self.in_bytes = (inputMap.nbits + 7) // 8
        self.out_bytes = (len(outputMap) + 7) // 8
        self.out_mask = (1 << (self.out_bytes * 8)) - 1
        self.state = ChangeDict(comparators=inputComparators)
        self.output_state = ChangeDict()
        usbport = next((p.device for p in comports() if p.vid), None)
        assert usbport, "Couldn't find usbport, is arduino connected?"
        print(f"Using usb port @ {usbport}")
        super().init(port=usbport, baudrate=115200, timeout=1)

    def get(self):
        # send a "request state" command
        # then receive expected number of bytes
        self.write(b'\x01')
        state = dict(inputMap.from_bytes(self.read(self.in_bytes)))
        self.state.update(state)
        return self.state

    def outputs(self):
        return [k for k in outputMap if k]

    def setTest(self, on: bool):
        self.set({k: on for k in self.outputs()})

    def set(self, state):
        latest = self.output_state.latest()
        self.output_state.update(state)
        if self.output_state.latest() == latest:
            return

        v = (outputValue(self.output_state) & self.out_mask)
        self.write(b'\x02')
        self.write(v.to_bytes(self.out_bytes, byteorder='little'))
