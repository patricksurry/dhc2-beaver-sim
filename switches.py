"""

conda create -n beaver-sim python=3.7
conda activate beaver-sim

PIP_EXTRA_INDEX_URL= PIP_INDEX_URL= pip install pyserial


ls -l /dev/cu.usb*
crw-rw-rw-  1 root  wheel   18,   3 24 Apr 10:26 /dev/cu.usbmodem141101

"""
import serial
import time
arduino = serial.Serial(port='/dev/cu.usbmodem141101', baudrate=115200, timeout=1)

lastdata = b''

while True:
    arduino.write(b'\x01')
    data = arduino.read(4+5)
    if data == lastdata:
        continue
    lastdata = data
    print(f'read {len(data)} bytes {data.hex()}')
    v = int.from_bytes(data[:4], byteorder='little')
    s = ''.join('X' if (1<<i) & v else '.' for i in range(32))
    knobs = data[4:]
    for knob in knobs:
        v = knob & 0x7f
        if v & 0x40: v -= 0x80
        button = knob & 0x80
        s += f" {v}{'*' if button else ''}"
    print(s)
    time.sleep(0.1)

