import logging

from telegram.ext import Updater

from dassetx_telegram_bot.bot.handler import (
    DassetxPriceAlertHandler,
)
from dassetx_telegram_bot.config import CONFIG
from dassetx_telegram_bot.data_provider.dassetx_price_provider import (
    DassetxPriceProvider,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def main():
    updater = Updater(token=CONFIG.TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    dassetxPriceProvider = DassetxPriceProvider(job_queue=updater.job_queue)

    price_handler = DassetxPriceAlertHandler(
        dassetxPriceProvider=dassetxPriceProvider, bot=updater.bot
    )

    dassetxPriceProvider.subscribe(price_handler.on_price_update)

    dispatcher.add_handler(
        price_handler.build_telegram_bot_handler('start')
    )  # Accessed via /start
    dispatcher.add_handler(
        price_handler.build_telegram_bot_handler('alert')
    )  # Accessed via /alert

    price_handler.start()  # let the provider start polling prices

    updater.start_polling()  # Start the bot
    updater.idle()


if __name__ == '__main__':
    CONFIG.check()
    main()
