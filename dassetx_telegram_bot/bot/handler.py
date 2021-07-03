from collections import namedtuple, defaultdict
from typing import Dict, List, DefaultDict

from telegram import Bot, TelegramError
from telegram.ext import CommandHandler

from dassetx_telegram_bot.config import CONFIG
from dassetx_telegram_bot.data_provider.dassetx_price_provider import (
    DassetxPriceProvider,
    DassetxPrice,
)

PriceRule = namedtuple(
    "PriceRule", ["crypto", "sign", "price", "subscribers"]
)  # Tuple[str, str, float, Set[int]]


class DassetxPriceAlertHandler:
    HELP = (
        '⚠️ Please provide a crypto code and a price value: \n'
        '<i>/alert &lt;crypto code&gt; operator &lt;price></i>\n'
        'e.g. \n'
        '   /alert btc > 50000\n'
        '   /alert btc &lt; 40000\n'
    )
    PARSE_MODE = "html"

    def __init__(self, dassetxPriceProvider: DassetxPriceProvider, bot: Bot):
        self._price_provider = dassetxPriceProvider
        self._subscribed_rules: DefaultDict[str, List[PriceRule]] = defaultdict(
            list
        )
        self._bot = bot

    def start(self):
        self._price_provider.start()

    def build_telegram_bot_handler(self, command: str):
        return CommandHandler(command, getattr(self, f"{command}_command"))

    def start_command(self, update, context):
        response = 'Hello there! I\'m Dassetx Price Alert Bot UNOFFICIAL.'
        response += "\n"
        response += self.HELP
        self._send(update, context, response)

    def help_command(self, update, context):
        self._send(update, context, self.HELP)

    def alert_command(self, update, context):
        # invalid syntax
        if len(context.args) < 2:
            # invalid arguments
            # print help
            response = self.HELP
            response += "\n"
            self._send(update, context, response)

            return

        crypto = context.args[0].upper()
        sign = context.args[1]
        try:
            expected_price = float(context.args[2])
        except ValueError:
            response = (
                f"Your expected price '{expected_price}' is not a number."
            )
            self._send(update, context, response)
            return

        # make full name <crypto>-USDT
        crypto = self._make_symbol(crypto)

        # handle an invalid crypto name
        current_tick = self._price_provider.get(crypto)
        if not current_tick:
            response = f"Your crypto '{crypto}' doesn't exist."
            self._send(update, context, response)
            return

        self._update_subscribed_rules(
            crypto, sign, expected_price, update.effective_chat.id
        )

        # notify user of new subscription
        response = (
            f"⏳ I will send you a message when the price of {crypto} "
            f"reaches ${expected_price}, \n"
        )
        response += f"the current price of {crypto} is ${current_tick.price}"
        self._send(update, context, response)

    def _update_subscribed_rules(
        self, crypto: str, sign: str, price: float, telegram_user_id: int
    ):
        # crypto not in rules
        if crypto not in self._subscribed_rules:
            self._subscribed_rules[crypto].append(
                PriceRule(
                    crypto=crypto,
                    sign=sign,
                    price=price,
                    subscribers={telegram_user_id},
                )
            )
            return

        # crypto in rules
        for rule in self._subscribed_rules[crypto]:
            # matches an existing rule, add subscription
            if rule.sign == sign and rule.price == price:
                rule.subscribers.add(telegram_user_id)
                return

        # crypto in rules, but no matched existing rules
        self._subscribed_rules[crypto].append(
            PriceRule(
                crypto=crypto,
                sign=sign,
                price=price,
                subscribers={telegram_user_id},
            )
        )

    def on_price_update(self, new_tickers: Dict[str, DassetxPrice]):
        self._monitor_price(new_tickers)

    def _send(self, update, context, text: str):
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode=self.PARSE_MODE,
        )

    def _make_symbol(self, crypto: str, to=CONFIG.DEFAULT_CURRENCY):
        return f"{crypto}-{to}"

    def _monitor_price(self, dassetx_price_dict: Dict[str, DassetxPrice]):
        for crypto, rules in self._subscribed_rules.items():
            if crypto in dassetx_price_dict.keys():
                dassetx_price = dassetx_price_dict[crypto]
                for rule in rules:
                    needs_sending = False
                    if rule.sign == "<":
                        if dassetx_price.lastTradeRate < rule.price:
                            needs_sending = True
                    if rule.sign == ">":
                        if dassetx_price.lastTradeRate > rule.price:
                            needs_sending = True

                    if needs_sending:
                        response = (
                            f'👋 Alert [{crypto} {rule.sign} ${rule.price}]: '
                            f'${dassetx_price.price} now!'
                        )
                        while rule.subscribers:
                            subscriber_id = rule.subscribers.pop()
                            try:
                                self._bot.send_message(
                                    chat_id=subscriber_id, text=response
                                )
                            except TelegramError:
                                rule.subscribers.add(subscriber_id)

                # find indexes of rules that have no subscribers
                rule_index_to_be_removed = []
                for index, rule in enumerate(rules):
                    if not rule.subscribers:
                        rule_index_to_be_removed.append(index)

                # remove rules that have no subscribers
                for i in rule_index_to_be_removed:
                    del self._subscribed_rules[crypto][i]
