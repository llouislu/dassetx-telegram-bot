import logging
import math
from dataclasses import dataclass, field
from typing import Callable

import requests
from requests import ReadTimeout
from rx.subject import Subject
from telegram.ext import JobQueue

from dassetx_telegram_bot.config import CONFIG
from dassetx_telegram_bot.data_provider.abc_provider import DataProviderABC
from dassetx_telegram_bot.util.ddecorator import singleton

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclass
class DassetxPrice:
    lastTradeRate: float = field(default=math.inf)
    bidRate: float = field(default=math.inf)
    askRate: float = field(default=math.inf)
    symbol: str = field(default=None)

    @property
    def price(self):
        if self.lastTradeRate > 10:
            return round(self.lastTradeRate, 3)
        return self.lastTradeRate


@singleton
class DassetxPriceProvider(DataProviderABC):
    def __init__(self, job_queue: JobQueue):
        self._job_queue = job_queue
        self._session = requests.Session()
        self._tickers = {}
        self.is_running = False
        self._tickers_observerable = Subject()
        self._subscriptions = []

    def __del__(self):
        self._tickers_observerable.dispose()
        self._job_queue.stop()
        self._session.close()

    def start(self):
        if not self.is_running:
            self._job_queue.run_repeating(
                self._poll_tickers, interval=3.0, first=0.0
            )

    def subscribe(self, callback: Callable):
        self._tickers_observerable.subscribe(callback)

    def get(self, key: str) -> DassetxPrice:
        if key in self._tickers:
            return self._tickers.get(key)
        else:
            return None

    def _poll_tickers(self, context):
        if not self.is_running:
            self.is_running = True
        # https://developers.dassetx.com/#428520eb-153b-461d-adb3-f51ca1216232
        try:
            r = self._session.get(
                "https://api.dassetx.com/api/markets/tickers",
                headers={
                    "x-account-id": CONFIG.DASSETX_ACCOUNT_ID,
                    "x-api-key": CONFIG.DASSETX_API_SECRET,
                },
                timeout=2.0,
            )
            new_tickers = r.json()
        except ReadTimeout as e:
            logger.warning("dassetx price polling timeout!")
        else:
            # [
            #     {
            #         "lastTradeRate": "0.00000753",
            #         "bidRate": "0.00000753",
            #         "askRate": "0.00000756",
            #         "symbol": "ADA-BTC"
            #     },
            #     {
            #         "lastTradeRate": "0.00023858",
            #         "bidRate": "0.00023851",
            #         "askRate": "0.00023914",
            #         "symbol": "ADA-ETH"
            #     }
            # ]
            self._tickers = {
                t["symbol"]: DassetxPrice(
                    lastTradeRate=float(t["lastTradeRate"]),
                    bidRate=float(t["bidRate"]),
                    askRate=float(t["askRate"]),
                    symbol=t["symbol"],
                )
                for t in new_tickers
            }
            self._tickers_observerable.on_next(self._tickers)
