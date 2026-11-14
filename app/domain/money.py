import re
from decimal import Decimal

from app.domain.types import bad_request

MAX_AMOUNT = Decimal("9999999999.99")
MONEY_PATTERN = re.compile(r"^[0-9]+(?:\.[0-9]{1,2})?$")


def parse_money(value: object) -> Decimal:
    if not isinstance(value, str) or not MONEY_PATTERN.fullmatch(value):
        raise bad_request("Amounts must be decimal strings with at most two decimal places")
    amount = Decimal(value)
    if amount <= 0 or amount > MAX_AMOUNT:
        raise bad_request("Amounts must be positive and within the supported range")
    return amount.quantize(Decimal("0.01"))


def format_money(amount: Decimal) -> str:
    return format(amount, ".2f")
