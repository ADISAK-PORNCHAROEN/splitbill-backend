from decimal import Decimal

import pytest

from app.domain.money import parse_money
from app.domain.splits import allocate
from app.domain.types import DomainError


def test_equal_split_allocates_remainder_in_member_order():
    result = allocate(Decimal("100.00"), {"type": "equal", "members": ["carol", "alice", "bob"]})
    assert result == {
        "carol": Decimal("33.34"),
        "alice": Decimal("33.33"),
        "bob": Decimal("33.33"),
    }
    assert sum(result.values()) == Decimal("100.00")


def test_exact_split_rejects_total_mismatch():
    with pytest.raises(DomainError, match="add up"):
        allocate(Decimal("10.00"), {"type": "exact", "shares": {"alice": "9.99"}})


@pytest.mark.parametrize("value", ["1.001", "0.00", "10000000000.00", 1.0])
def test_invalid_money_is_rejected(value):
    with pytest.raises(DomainError):
        parse_money(value)
