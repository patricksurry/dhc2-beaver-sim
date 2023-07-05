"""
Simple serial monitor that proxies Arduino I/O state to g3py server

To run:

    conda env update -f environment.yml
    conda activate beaver-sim
    python monitor.py -?

"""
import logging
import asyncio
from typing import Optional

import argparse

from g3py.metrics import MetricsProducer, MetricsConsumer, MetricsModel


async def watch_panel(panel, hub_url: Optional[str] = None, interval: float=0.1):
    logging.info('watch_paneL: starting')

    if hub_url:
        logging.debug("watch_paneL: starting metrics producer")
        producer = MetricsProducer(panel.__class__.__name__, hub_url)
    else:
        producer = None

    while True:
        diff = panel.get_state_changes()
        if diff:
            logging.debug(f"watch_panel: state changed {diff}", )
            if producer:
                await producer.update_async(MetricsModel(metrics=diff))
            else:
                print("Panel changes:", diff)
        await asyncio.sleep(interval)


async def watch_metrics(panel, hub_url: Optional[str]=None):
    if not hub_url:
        return

    metrics = panel.output_names()

    logging.info(f"watch_metrics: starting SSE consumer for {metrics}")

    def handler(mm: MetricsModel):
        logging.debug(f"watch_metrics: updating panel: {mm.dict()}")
        panel.set_state(mm.metrics)

    consumer = MetricsConsumer(panel.__class__.__name__, hub_url)
    await consumer.watch(metrics, handler)


async def main():
    parser = argparse.ArgumentParser(
        prog='monitor',
        description='Sync Arduino I/O panel with g3py metric server',
        add_help=False,
    )
    parser.add_argument('-?', '--help', action='help')
    parser.add_argument('-h', '--hub-url', help='metrics hub root URL')
    parser.add_argument('-m', '--mock', action='store_true', help='mock arduino panel')
    parser.add_argument('-i', '--interval', default=0.1, type=float, help='polling interval')
    parser.add_argument('-l', '--loglevel', default='INFO', help='set log level (default INFO)',
        choices=['debug', 'info', 'warning', 'error', 'critical'])
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel.upper())

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
    await asyncio.gather(
        watch_panel(panel, args.hub_url, args.interval),
        watch_metrics(panel, args.hub_url)
    )


asyncio.run(main())
