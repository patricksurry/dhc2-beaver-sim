"""
Simple serial monitor that proxies Arduino I/O state to g3py server

To run:

    conda env update -f environment.yml
    conda activate beaver-sim
    python monitor.py --help

"""
import logging
import asyncio
import aiohttp
from aiohttp_sse_client import client as sse_client
from aiohttp.client_exceptions import ClientPayloadError

import json
import argparse


async def watch_panel(hosturl: str=None):
    logging.info('watch_paneL: start monitoring')

    async with aiohttp.ClientSession() as session:
        while True:
            diff = panel.get_state_changes()
            if diff:
                logging.debug("watch_panel: outputs changed", diff)
                if hosturl:
                    #TODO try/except
                    await session.post(f"{hosturl}/inputs", json=diff)
            await asyncio.sleep(0.1)


async def watch_metrics(hosturl: str=None):
    if not hosturl:
        return
    logging.info("watch_metrics: SSE consumer started")
    params = dict(metrics=','.join(panel.output_names()), latest=0)

    while True:
        async with sse_client.EventSource(f"{hosturl}/stream", params) as events:
            try:
                async for event in events:
                    logging.debug(f"watch_metrics: SSE data {event.data}")
                    result = json.loads(event.data)
                    params['latest'] = result['latest']
                    logging.debug('SSE event', event.data)
                    if result.get('metrics'):
                        panel.set_state(result['metrics'])
            except (ConnectionError, ClientPayloadError):
                pass


async def main(hosturl: str=None):
    # test all the lights then leave them off
    logging.info("Initialize: set_test on")
    panel.set_test(True)
    await asyncio.sleep(1)
    logging.info("Initialize: set_test off")
    panel.set_test(False)

    await asyncio.gather(watch_panel(hosturl), watch_metrics(hosturl))


parser = argparse.ArgumentParser(
    prog='monitor',
    description='Sync Arduino I/O panel with g3py metric server',
    add_help=False,
)
parser.add_argument('-?', '--help', action='help')
parser.add_argument('-h', '--hostname', help='metric server root URL')
parser.add_argument('-m', '--mock', action='store_true', help='mock arduino panel')
args = parser.parse_args()

if args.mock:
    from arduino_mock import ArduinoMock as Arduino
else:
    from arduino import Arduino

panel = Arduino()

asyncio.run(main(args.hostname))
