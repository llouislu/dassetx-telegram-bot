import math
from dataclasses import dataclass, field
from typing import List, Dict

import requests

from dassetx_telegram_bot.config import Config
from dassetx_telegram_bot.data_provider.abc_provider import DataProviderABC
from dassetx_telegram_bot.util.ddecorator import singleton


@dataclass
class DassetxPrice:
    lastTradeRate: float = field(default=math.inf)
    bidRate: float = field(default=math.inf)
    askRate: float = field(default=math.inf)
    symbol: str = field(default=None)


@singleton
class DassetxPriceProvider(DataProviderABC):
    def __init__(self):
        self._session = requests.Session()
        self._tickers = {}
        # TODO: make it subscribable i.e. on btc price updates,
        #  run an external callback method to send alert messages

    def __del__(self):
        self._session.close()

    def get(self, key: str) -> DassetxPrice:
        if key in self._tickers:
            return self._tickers.get(key)
        elif f"{key}-NZD" in self._tickers:
            return self._tickers.get(f"{key}-NZD")

    def _get_tickers(self):
        # https://developers.dassetx.com/#428520eb-153b-461d-adb3-f51ca1216232
        r = self._session.get(
            "https://api.dassetx.com/api/markets/tickers",
            headers={
                "x-account-id": Config.DASSETX_ACCOUNT_ID,
                "x-api-key": Config.DASSETX_API_SECRET,
            },
        )
        try:
            self._update_tickers(r.json())
        except Exception as e:
            return

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
