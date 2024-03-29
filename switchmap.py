"""
Defines the switch map which configures how we map the raw data
received from the Arduino to the actual physical inputs that
we want to send to FS
"""
from typing import cast, List, Tuple
from bitstring import ConstBitStream, Bits # type: ignore

from g3py.decl import Metric, MetricValue, MetricDict


InputValue = Tuple[Metric, MetricValue]


class InputBits:
    """
    Base class for consuming some bits from a stream to produce
    a list of one or more named valued.
    Every subclass specifies the number of bits it consumes via `nbits`
    """
    def __init__(self, name: Metric, fmt: str):
        """By default provide a name and a bitstring format string"""
        self.name = name
        self.fmt = fmt
        if fmt and ':' in fmt:
            self.nbits = int(fmt.split(':')[-1])
        elif fmt == 'bool':
            self.nbits = 1
        else:
            raise NotImplementedError(f"Didn't specify nbits, got name={name}, fmt={fmt}")

    def read(self, bits: ConstBitStream) -> List[InputValue]:
        """Consume bits from the stream to return a list of one named value"""
        return [(self.name, bits.read(self.fmt))]


class InputBool(InputBits):
    """Represent a single bit boolean input, needing just a name"""
    def __init__(self, name: str):
        super().__init__(name, 'bool')


class InputNPosition(InputBits):
    """
    Represent an N-position switch with one bit for each position
    Value will be the position of the first bit that's set (MSB=N, LSB=1),
    or 0 if no bit is set.  If multiple bits are set, favor_msb determines
    whether we pick the highest or lowest.
    """
    def __init__(self, name: str, n: int, favor_msb=True):
        self.n = n
        self.favor_msb = favor_msb
        super().__init__(name, f'bits:{n}')

    def read(self, bits: ConstBitStream) -> List[InputValue]:
        bs = cast(Bits, bits.read(self.fmt))
        # Find the index of the first (or last) set bit,
        # returned as a 0-indexed tuple, where 0 indicates MSB
        # and N-1 indicates MSB, so we return N-v
        v = bs.find('0b1') if self.favor_msb else bs.rfind('0b1')
        return [(self.name, self.n - v[0] if v else 0)]


class InputUnused(InputBits):
    """Consume a range of unused bits, returning no values"""
    def __init__(self, bits):
        super().__init__(None, f'pad:{bits}')

    def read(self, bits: ConstBitStream) -> List[InputValue]:
        bits.read(self.fmt)
        return []


class InputList(InputBits):
    """
    Represent a sequence of InputBits definitions, from MSB towards LSB.
    This is used to specify the overall configuration, to consume all the
    input data via from_bytes(), and for nested compound inputs
    like the InputEncoderWithButton
    """
    def __init__(self, inputs: List[InputBits]):
        self.inputs = inputs
        nbits = sum(d.nbits for d in inputs)
        super().__init__('list', fmt=f':{nbits}')

    def read(self, bits: ConstBitStream) -> List[InputValue]:
        """note bits should be MSB first throughout"""
        return sum((d.read(bits) for d in self.inputs), [])

    def from_bytes(self, xs: bytes, debug=False) -> List[InputValue]:
        # reverse bytes so we read() from msb to lsb
        bits = ConstBitStream(bytes(reversed(xs)))
        assert len(bits) == self.nbits, f"Mismatched length from_bytes {len(bits)} != {self.nbits}"
        if debug:
            s = bits.bin
            s = ' '.join([s[i:i+8] for i in range(0, len(s), 8)])
            print(f'Reading bytes {xs.hex()} with {len(bits)} bits: {s}')
        return self.read(bits)


class InputEncoderWithButton(InputList):
    """
    Represent a rotary encoder plus a button as a compound input.
    The value is encoded in one byte
    where msb is button status, and 7 lsb are a signed change in rotation.
    """
    def __init__(self, name):
        super().__init__([
            InputBool(f"{name}-BTN"),
            InputBits(f"{name}-ROT", 'int:7'),
        ])


inputMap = InputList(list(reversed([
    # listed here from LSB onward, so reversed() gives desired MSB -> LSB order
    # main switch panel below the flight instruments
    InputBool('MASTER0'),
    InputBool('MASTER1'),
    InputBool('STARTER'),
    InputBool('SW1-1'),
    InputBool('SW1-2'),
    InputBool('SW1-3'),
    InputBool('SW2-1'),
    InputBool('SW2-2'),
    InputBool('SW2-3'),
    InputBool('SW2-4'),
    InputBool('SW2-5'),
    InputBool('SW3-1'),
    InputBool('SW3-2'),
    InputBool('SW3-3'),
    InputBits('FUELSELECTOR', 'uint:2'),
    InputNPosition('KEY', 6),
    InputBool('PRIMER'),
    InputUnused(9),
    # rotary encoders on main flight instrument display
    InputEncoderWithButton('VOR'),  # VHF omnidirectional range - bottom right
    InputEncoderWithButton('ADF'),  # auto direction finder - top right
    InputEncoderWithButton('ALT'),  # altimeter - top 2nd from right
    InputEncoderWithButton('ATT'),   # attitude indicator - top 2nd from left
    InputEncoderWithButton('HDG'),   # heading indicator - bottom 2nd from left
    InputBits('WOBBLE', 'uint:10'),  # potentiometer for wobble pump handle
    InputBits('MIXTURE', 'uint:10'),  # potentiometer for carburetor mixture
    InputUnused(14 * 10),
])))


def lo_fidelity(delta=8):
    return lambda a, b: abs(a-b) < delta


inputComparators = {
    'WOBBLE': lo_fidelity(),
    'MIXTURE': lo_fidelity(),
}


# 8-bit 12V LED controller via SPIO
outputMap = [
    'RED_WARNING',
    'ORANGE_WARNING',
    None,
    None,
    'FRONT_CABIN_LIGHTS',
    'REAR_CABIN_LIGHTS',
    None,
    None
]


def outputValue(state: MetricDict) -> int:
    return sum(
        1 << i for i, k in enumerate(outputMap) if k is not None and state.get(k)
    )


if __name__ == '__main__':
    """Simple test that we can read state from bytes similar to Arduino output"""
    import json

    print(f'Switch map has {inputMap.nbits} bits')
    xs = bytes.fromhex('fbbf0173007f8300003ff3f0' + '00'*17)
    state = dict(inputMap.from_bytes(xs, debug=True))
    print(json.dumps(state, indent=4))

    print('LED setting:', ConstBitStream(int=outputValue(state), length=8).bin)
