from bitstring import BitStream  # type: ignore
from random import random
import logging

from g3py.decl import MetricDict

from arduino_base import ArduinoBase
from switchmap import inputMap


class ArduinoMock(ArduinoBase):
    def __init__(self, rate: float=0.05):
        super().__init__()
        self.rate = rate
        self._bits = BitStream([False] * inputMap.nbits)

    def _twiddle(self) -> None:
        self._bits.pos = 0
        vs = self._bits.readlist(f'{self._bits.len}*bool')
        vs = [not v if random() < self.rate else v for v in vs]
        self._bits.overwrite(BitStream(vs), 0)
        self._bits.pos = 0

    def _poll(self) -> MetricDict:
        self. _twiddle()
        state = dict(inputMap.read(self._bits))
        self._in_state.update(state)
        return self._in_state

    def set_state(self, state: MetricDict) -> None:
        v = self._maybe_output(state)
        if v is None:
            return
        logging.debug(f"ArduinoMock: New output state 0x{v:02x} for {self._out_state}")
