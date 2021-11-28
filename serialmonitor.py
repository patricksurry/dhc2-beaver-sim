"""
Simple serial monitor that pings the Arduino to check current input state.
Currenly prints state changes, but soon will send via python-simconnect

To run:

    conda env update -f environment.yml
    conda activate beaver-sim
    python serialmonitor.py

"""
from typing import Dict, Any
import time
import serial
from serial.tools.list_ports import comports

from switchmap import switchmap, ledSetting


# scan attached serial devices for the first one with a USB vendor Id
# to locate the Arduino.  This could fail with multiple USD devices
usbport = next((p.device for p in comports() if p.vid), None)

if not usbport:
    print("Couldn't find usbport, is arduino connected?")
else:
    print(f"Using usb port @ {usbport}")


arduino = serial.Serial(port=usbport, baudrate=115200, timeout=1)

lastdata = b''
oldstate: Dict[str, Any] = {}

oldleds = b''

# turn off all the lights
arduino.write(b'\x0200')

while True:
    # send a "request state" command (the only supported option currently :)
    arduino.write(b'\x01')
    # expect to receive bytes representing input state
    data = arduino.read(switchmap.nbits // 8)
    if data == lastdata:
        continue
    lastdata = data
    # if anything changed, parse input state and look for differences
    # print(f'Data changed, read {len(data)} bytes {data.hex()}')
    state = dict(switchmap.readbytes(data))
    diff = {k: v for (k, v) in state.items() if k not in oldstate or oldstate[k] != v}
    oldstate = state
    if diff:
        print(diff)
        leds = ledSetting(state)
        if leds != oldleds:
            arduino.write(b'\x02' + leds)
    #TODO send change info to FS
    time.sleep(0.1)
