#!/usr/bin/env python
"""Basic usage example and testing of pysma."""
import argparse
import asyncio
import logging
import signal
import sys

import aiohttp

import pysma

# This module will work with Python 3.5+
# Python 3.4+ "@asyncio.coroutine" decorator
# Python 3.5+ uses "async def f()" syntax

_LOGGER = logging.getLogger(__name__)

VAR = {}


def print_table(sensors):
    for sen in sensors:
        if sen.value is None:
            print("{:>25}".format(sen.name))
        else:
            print("{:>25}{:>15} {}".format(sen.name, str(sen.value), sen.unit))


async def main_loop(password, user, ip):  # pylint: disable=invalid-name
    """Main loop."""
    async with aiohttp.ClientSession(
        connector=aiohttp.TCPConnector(ssl=True)
    ) as session:
        VAR["sma"] = pysma.SMA(session, ip, password=password, group=user)
        await VAR["sma"].new_session()
        if VAR["sma"].sma_sid is None:
            _LOGGER.info("No session ID")
            return

        _LOGGER.debug("NEW SID: %s", VAR["sma"].sma_sid)

        VAR["running"] = True
        cnt = 1
        sensors = pysma.Sensors()
        while VAR.get("running"):
            await VAR["sma"].read(sensors)
            print_table(sensors)
            cnt -= 1
            if cnt == 0:
                break
            await asyncio.sleep(2)

        await VAR["sma"].close_session()


def main():
    """Main example."""
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    parser = argparse.ArgumentParser(description="Test the SMA webconnect library.")
    parser.add_argument("ip", type=str, help="IP address of the Webconnect module")
    parser.add_argument("user", help="installer/user")
    parser.add_argument("password", help="Installer password")

    args = parser.parse_args()

    def _shutdown(*_):
        VAR["running"] = False

    signal.signal(signal.SIGINT, _shutdown)

    asyncio.run(
        main_loop(user=args.user, password=args.password, ip=args.ip)
    )


if __name__ == "__main__":
    main()
