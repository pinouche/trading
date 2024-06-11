"""main module that implements the trading app and connects to IBKR API."""

import threading
import time

from dotenv import dotenv_values
from loguru import logger

from trading.api.ibapi_class import IBapi
from trading.utils import config_load

env_vars = dotenv_values(".env")
config_vars = config_load("./config.yaml")


def main() -> IBapi:
    """connect to IBapi TWS client"""
    def run_loop() -> None:
        appl.run()

    appl = IBapi()
    appl.connect(env_vars.get("IP_ADDRESS"),
                 int(env_vars.get("PORT")),
                 int(env_vars.get("CLIENT_ID")))

    api_thread = threading.Thread(target=run_loop, daemon=True)
    api_thread.start()

    # Check if the API is connected via orderid
    while True:
        if isinstance(appl.nextorderId, int):
            logger.info('We are connected')
            break
        else:
            print('Waiting for connection... (retrying)')
            time.sleep(1)

    return appl


if __name__ == '__main__':
    app = main()
