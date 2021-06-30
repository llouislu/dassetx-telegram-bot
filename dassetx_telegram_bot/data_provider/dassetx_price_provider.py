import logging
import math
from dataclasses import dataclass, field
from typing import List, Dict

import requests
from telegram.ext import JobQueue

from dassetx_telegram_bot.config import Config
from dassetx_telegram_bot.data_provider.abc_provider import DataProviderABC
from dassetx_telegram_bot.util.ddecorator import singleton

logger = logging.getLogger(__name__)


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

    def __del__(self):
        self._job_queue.stop()
        self._session.close()

    def start(self):
        if not self.is_running:
            self._job_queue.run_repeating(
                self._get_tickers, interval=1.5, first=0.0
            )

    def get(self, key: str) -> DassetxPrice:
        if key in self._tickers:
            return self._tickers.get(key)
        elif f"{key}-NZD" in self._tickers:
            return self._tickers.get(f"{key}-NZD")
        else:
            return None

    def _get_tickers(self, context):
        if not self.is_running:
            self.is_running = True
        # https://developers.dassetx.com/#428520eb-153b-461d-adb3-f51ca1216232
        r = self._session.get(
            "https://api.dassetx.com/api/markets/tickers",
            headers={
                "x-account-id": Config.DASSETX_ACCOUNT_ID,
                "x-api-key": Config.DASSETX_API_SECRET,
            },
            timeout=3,
        )
        try:
            logger.error(r.json())
            self._update_tickers(r.json())
        except Exception as e:
            logger.exception(e)
            pass

    def _update_tickers(self, tickers: List[Dict[str, str]]):
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
            for t in tickers
        }
