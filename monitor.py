"""
Simple serial monitor that proxies Arduino I/O state to g3py server

To run:

    conda env update -f environment.yml
    conda activate beaver-sim
    python monitor.py -?

"""
import logging
import asyncio
import aiohttp
from aiohttp_sse_client import client as sse_client
from aiohttp.client_exceptions import ClientPayloadError

import json
import argparse


async def watch_panel(panel, hosturl: str=None):
    logging.info('watch_paneL: starting')

    async with aiohttp.ClientSession() as session:
        while True:
            diff = panel.get_state_changes()
            if diff:
                logging.debug("watch_panel: outputs changed", diff)
                if hosturl:
                    #TODO try/except
                    await session.post(f"{hosturl}/inputs", json=diff)
            await asyncio.sleep(0.1)


async def watch_metrics(panel, hosturl: str=None):
    if not hosturl:
        return

    metrics = ','.join(panel.output_names())

    logging.info(f"watch_metrics: starting SSE consumer for {metrics}")

    params = dict(metrics=metrics, latest=0)

    while True:
        async with sse_client.EventSource(f"{hosturl}/stream", params) as events:
            try:
                async for event in events:
                    logging.debug(f"watch_metrics: SSE data {event.data}")
                    result = json.loads(event.data)
                    params['latest'] = result['latest']
                    logging.debug("watch_metrics: got SSE event data {event.data}")
                    if result.get('metrics'):
                        panel.set_state(result['metrics'])
            except (ConnectionError, ClientPayloadError):
                pass
        logging.debug(f"watch_metrics: consumer restarting")


async def main():
    parser = argparse.ArgumentParser(
        prog='monitor',
        description='Sync Arduino I/O panel with g3py metric server',
        add_help=False,
    )
    parser.add_argument('-?', '--help', action='help')
    parser.add_argument('-h', '--hostname', help='metric server root URL')
    parser.add_argument('-m', '--mock', action='store_true', help='mock arduino panel')
    parser.add_argument('-l', '--loglevel', default='INFO', help='set log level (default INFO)',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)

    if args.mock:
        from arduino_mock import ArduinoMock as Arduino
    else:
        from arduino import Arduino

    panel = Arduino()

    # toggle all outputs (lights) on then off
    logging.debug("main: set_test on")
    panel.set_test(True)
    await asyncio.sleep(1)
    logging.debug("main: set_test off")
    panel.set_test(False)

    logging.info("main: start monitors")
    await asyncio.gather(watch_panel(panel, args.hostname), watch_metrics(panel, args.hostname))


asyncio.run(main())
