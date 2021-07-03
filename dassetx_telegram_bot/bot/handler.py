from telegram.ext import CommandHandler

from dassetx_telegram_bot.data_provider.dassetx_price_provider import (
    DassetxPriceProvider,
    DassetxPrice,
)


class DassetxPriceAlertHandler:
    HELP = (
        '⚠️ Please provide a crypto code and a price value: \n'
        '<i>/alert &lt;crypto code&gt; operator &lt;price></i>\n'
        'e.g. \n'
        '   /alert btc > 50000\n'
        '   /alert btc &lt; 40000\n'
    )
    PARSE_MODE = "html"

    def __init__(self, dassetxPriceProvider: DassetxPriceProvider):
        self._price_provider = dassetxPriceProvider

    def start(self):
        self._price_provider.start()

    def build_handler(self, command: str):
        return CommandHandler(command, getattr(self, f"{command}_command"))

    def start_command(self, update, context):
        response = 'Hello there! I\'m Dassetx Price Alert Bot UNOFFICIAL.'
        response += "\n"
        response += self.HELP
        self._send(update, context, response)

    def help_command(self, update, context):
        self._send(update, context, self.HELP)

    def alert_command(self, update, context):
        if len(context.args) < 2:
            # invalid arguments
            # print help
            response = self.HELP
            response += "\n"
            self._send(update, context, response)

            return

        crypto = context.args[0].upper()
        sign = context.args[1]
        expected_price = context.args[2]

        # context.job_queue.run_repeating(
        #     self._monitor_price,
        #     interval=15,
        #     first=15,
        #     context=[crypto, sign, price, update.message.chat_id],
        # )

        current_tick = self._price_provider.get(crypto)
        if not current_tick:
            response = f"Your crypto '{crypto}' doesn't exist."
            self._send(update, context, response)
            return

        response = (
            f"⏳ I will send you a message when the price of {crypto} "
            f"reaches ${expected_price}, \n"
        )
        response += f"the current price of {crypto} is ${current_tick.price}"
        self._send(update, context, response)

    def _send(self, update, context, text: str):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode=self.PARSE_MODE,
        )

    def _make_symbol(self, crypto: str, to=CONFIG.DEFAULT_CURRENCY):
        return f"{crypto}-{to}"

    def _monitor_price(self, context):
        crypto = context.job.context[0]
        sign = context.job.context[1]
        expected_price = context.job.context[2]
        chat_id = context.job.context[3]

        current_tick: DassetxPrice = self._price_provider.get(crypto)
        current_price = current_tick.lastTradeRate

        needs_sending = False
        if sign == "<":
            if current_price < expected_price:
                needs_sending = True
        if sign == ">":
            if current_price > expected_price:
                needs_sending = True

        if needs_sending:
            response = f'👋 {crypto} has surpassed ${expected_price} and has just reached <b>${current_price}</b>!'

            context.job.schedule_removal()

            context.bot.send_message(chat_id=chat_id, text=response)
