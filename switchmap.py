from typing import List, Tuple, Any
from bitstring import ConstBitStream, BitArray


class InputBits:
    def __init__(self, name: str=None, fmt: str=None):
        self.name = name
        self.fmt = fmt
        if fmt and ':' in fmt:
            self.nbits = int(fmt.split(':')[-1])
        elif fmt == 'bool':
            self.nbits = 1
        else:
            self.nbits = None

    def read(self, bits: ConstBitStream) -> List[Tuple[str, Any]]:
        return [(self.name, bits.read(self.fmt))]


class InputBool(InputBits):
    """Represent a single bit boolean input"""
    def __init__(self, name: str):
        super().__init__(name, 'bool')


class InputNPosition(InputBits):
    """
    Represent an N-position switch with one bit for each position
    Value will be the position of the first bit that's set (MSB=N, LSB=1),
    or 0 if no bit is set.  If multiple bits are set, favor_msb determines
    whether we pick the highest or lowest.
    """

    def __init__(self, name: str, n: int, favor_msb = True):
        self.n = n
        self.favor_msb = favor_msb
        super().__init__(name, f'bits:{n}')

    def read(self, bits: ConstBitStream) -> List[Tuple[str, Any]]:
        bs = bits.read(self.fmt)
        # Find the index of the first (or last) set bit,
        # returned as a 0-indexed tuple, where 0 indicates MSB
        # and N-1 indicates MSB, so we return N-v
        v = bs.find('0b1') if self.favor_msb else bs.rfind('0b1')
        return [(self.name, self.n - v[0] if v else 0)]


class InputUnused(InputBits):
    """Represent a range of unused bits"""
    def __init__(self, bits):
        super().__init__(None, f'pad:{bits}')

    def read(self, bits: ConstBitStream) -> List[Tuple[str, Any]]:
        bits.read(self.fmt)
        return []


class InputList(InputBits):
    """Represent a list of inputs, from MSB towards LSB"""
    def __init__(self, inputs: List[InputBits]):
        super().__init__()
        self.inputs = inputs
        self.nbits = sum(d.nbits for d in inputs)

    def read(self, bits: ConstBitStream) -> List[Tuple[str, Any]]:
        """note bits should be MSB first throughout"""
        return sum((d.read(bits) for d in self.inputs), [])


class InputEncoderWithButton(InputList):
    """
    Represent a rotary encoder plus a button, encoded in one byte
    where msb is button status, 7 lsb are a signed rotation
    """
    def __init__(self, name):
        super().__init__([
            InputBool(f"{name}-BTN"),
            InputBits(f"{name}-ROT", 'int:7'),
        ])


switchmap = InputList(list(reversed([
    # listed here from LSB first, so include the reverse
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
    InputBits('MAGNETO', 'uint:2'),
    InputNPosition('KEY', 6),
    InputUnused(10),
    InputEncoderWithButton('A'),
    InputEncoderWithButton('B'),
    InputEncoderWithButton('C'),
    InputEncoderWithButton('D'),
    InputEncoderWithButton('E'),
])))

print(switchmap.nbits)

"""
read 9 bytes fb01ff00 0000000000
XX.X XXXX XXXX XXXX X... .... .... .... 0 0 0 0 0
read 9 bytes fb7f01000000000000
XX.XXXXXXXXXXXX.X............... 0 0 0 0 0
read 9 bytes fb3f01000000000000
XX.XXXXXXXXXXX..X............... 0 0 0 0 0
"""

def bitsfrombytes(xs: bytes) -> ConstBitStream:
    # reverse bytes so we read() from msb to lsb
    return ConstBitStream(bytes(reversed(xs)))


import json

bits = bitsfrombytes(bytes.fromhex('fbbf0173007f830000'))
s = bits.bin
s = ' '.join([s[i:i+8] for i in range(0, len(s), 8)])
assert len(bits) == switchmap.nbits, "Mismatch length from mapping"
print(len(bits), s)
print('XX.X XXXX XXXX XX.X X............... 0 0 0 0 0')
print(json.dumps(dict(switchmap.read(bits)), indent=4))
