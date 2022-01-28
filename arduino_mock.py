from switchmap import inputMap, inputComparators, outputMap, outputValue
from changedict import ChangeDict
from bitstring import BitStream
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
        self.state = ChangeDict(comparators=inputComparators)
        self.output_state = ChangeDict()

    def get(self):
        # send a "request state" command
        # then receive expected number of bytes
        _twiddle()
        state = dict(inputMap.read(_bits))
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
        v = outputValue(self.output_state)
        print('Setting state', v, 'for', self.output_state)
