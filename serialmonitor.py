"""

PIP_EXTRA_INDEX_URL= PIP_INDEX_URL= conda env update -f environment.yml
conda activate beaver-sim

ls -l /dev/cu.usb*
crw-rw-rw-  1 root  wheel   18,   3 24 Apr 10:26 /dev/cu.usbmodem141101

"""
import time
import json
import serial
from serial.tools.list_ports import comports

from switchmap import switchmap

assert switchmap.nbits % 8 == 0, f"{switchmap.nbits} bit switch map not byte aligned"

usbport = next((p.device for p in comports() if p.vid), None)

if not usbport:
    print("Couldn't find usbport, is arduino connected?")
else:
    print(f"Using usb port @ {usbport}")


arduino = serial.Serial(port=usbport, baudrate=115200, timeout=1)

lastdata = b''
oldstate = {}

while True:
    arduino.write(b'\x01')
    data = arduino.read(switchmap.nbits // 8)
    if data == lastdata:
        continue
    lastdata = data
    print(f'Data changed, read {len(data)} bytes {data.hex()}')
    state = dict(switchmap.readbytes(data))
    diff = {k: v for (k, v) in state.items() if k not in oldstate or oldstate[k] != v}
    oldstate = state
    print(json.dumps(diff, indent=4))
    time.sleep(0.1)

