from decimal import Decimal

from app.domain.money import parse_money
from app.domain.types import bad_request


def allocate(amount: Decimal, split: object) -> dict[str, Decimal]:
    if not isinstance(split, dict):
        raise bad_request("Split must be an object")
    if split.get("type") == "equal":
        members = split.get("members")
        if (
            not isinstance(members, list)
            or not members
            or any(not isinstance(member, str) or not member.strip() for member in members)
        ):
            raise bad_request("Equal split requires members")
        if len(set(members)) != len(members):
            raise bad_request("Split members must be unique")
        cents = int(amount * 100)
        each, remainder = divmod(cents, len(members))
        return {name: Decimal(each + (i < remainder)) / 100 for i, name in enumerate(members)}
    if split.get("type") == "exact":
        shares = split.get("shares")
        if (
            not isinstance(shares, dict)
            or not shares
            or any(not isinstance(name, str) or not name.strip() for name in shares)
        ):
            raise bad_request("Exact split requires shares")
        result = {name: parse_money(value) for name, value in shares.items()}
        if sum(result.values(), Decimal(0)) != amount:
            raise bad_request("Exact shares must add up to the expense amount")
        return result
    raise bad_request("Split type must be equal or exact")
