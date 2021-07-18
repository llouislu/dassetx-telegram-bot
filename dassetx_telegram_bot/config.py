import os
from pathlib import Path


class CONFIG:
    DASSETX_ACCOUNT_ID = os.environ.get('DASSETX_ACCOUNT_ID')
    DASSETX_API_SECRET = os.environ.get('DASSETX_API_SECRET')
    TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
    DEFAULT_CURRENCY = os.environ.get("DEFAULT_CURRENCY", "USDT")
    SQLITE_PATH = os.environ.get("SQLITE_PATH")

    @classmethod
    def check(cls):
        assert cls.DASSETX_ACCOUNT_ID, "please configure your dassetx account"
        assert (
            cls.DASSETX_API_SECRET
        ), "please configure your dassetx API secret"
        assert cls.TELEGRAM_TOKEN, "please configure your telegram token"
        assert Path(cls.SQLITE_PATH).is_file(), "sqlite3 file does not exist"
