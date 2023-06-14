from switchmap import inputMap, inputComparators, outputMap, outputValue
from changedict import ChangeDict
from bitstring import BitStream  # type: ignore
from random import random


_bits = BitStream([False] * inputMap.nbits)


def _twiddle():
    _bits.pos = 0
    vs = _bits.readlist(f'{_bits.len}*bool')
    vs = [v if random() < 0.95 else not v for v in vs]
    _bits.overwrite(BitStream(vs), 0)
    _bits.pos = 0


class ArduinoMock():
    def __init__(self):
        # scan attached serial devices for the first one with a USB vendor Id
        # to locate the Arduino.  This could fail with multiple USD devices
        self._in_state = ChangeDict(comparators=inputComparators)
        self._out_state = ChangeDict()

    def get_state(self):
        # send a "request state" command
        # then receive expected number of bytes
        _twiddle()
        state = dict(inputMap.read(_bits))
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
        print(f"Setting state 0x{v:02x} for {self._out_state}")
