"""
Simple serial monitor that pings the Arduino to check current input state.
Currenly prints state changes, but soon will send via python-simconnect

To run:

    conda env update -f environment.yml
    conda activate beaver-sim
    python serialmonitor.py

"""
import sys
import time
import requests
from arduino import Arduino
from arduino_mock import ArduinoMock

assert len(sys.argv) <= 2

host = sys.argv[1] if len(sys.argv) == 2 else None

latest = 0

# panel = Arduino()
panel = ArduinoMock()

# test all the lights then leave them off
panel.setTest(True)
time.sleep(0.5)
panel.setTest(False)

query_params = dict(metrics=','.join(panel.outputs()), latest=0)

while True:
    state = panel.get()
    diff = state.changedsince(latest)
    latest = state.latest()
    if diff:
        print('sending', diff)
        if host:
            requests.post(host + '/inputs', json=diff)

    print('requesting outputs', query_params)
    if host:
        result = requests.get(
            host + '/metrics.json', params=query_params
        ).json()
        query_params['latest'] = result['latest']
        if result['metrics']:
            print('got outputs', result)
            panel.set(result['metrics'])

    time.sleep(0.25)
